"""Side-scrolling demo for Legado Arcano."""
import math
import random
import pygame
from src.assets import resource_path, Sounds
from src.platform_art import load_art

W, H = 960, 540
FLOOR = 470
CLASSES = ('Mago', 'Cavaleiro', 'Arqueiro')
COLORS = ((115, 207, 255), (255, 195, 106), (160, 226, 123))
NAMES = ('Ruínas Arcanas', 'Caverna Azul', 'Floresta Ancestral', 'Templo das Estátuas', 'Guardião Ancião')

class PlatformGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption('Legado Arcano — Demo')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(str(resource_path('assets', 'fonts', 'PixelifySans.ttf')), 24)
        self.big = pygame.font.Font(str(resource_path('assets', 'fonts', 'PixelifySans.ttf')), 58)
        self.small = pygame.font.Font(str(resource_path('assets', 'fonts', 'PixelifySans.ttf')), 18)
        self.state, self.selection, self.class_index = 'menu', 0, 0
        self.sound = True
        self.sounds = Sounds()
        self.time = 0
        self.action = 'idle'
        self.action_time = 0.
        self.death_time = 0.
        self.running = True
        self.sheets = {}
        for name in ('mago_laranja', 'guerreiro', 'ninja', 'goblin', 'golem'):
            self.sheets[name] = pygame.image.load(str(resource_path('assets', 'sprites', 'ninja-adventure', name + '.png'))).convert_alpha()
        self.art = load_art()
        self.reset()

    def reset(self):
        self.level = 0
        self.max_hp = (90, 130, 100)[self.class_index]
        self.hp = self.max_hp
        self.load_level()

    def load_level(self):
        self.x, self.y, self.vy = 80., float(FLOOR - 48), 0.
        self.grounded, self.facing = False, 1
        self.drop_platform = None
        self.attack_timer = self.dash_timer = self.cooldown = self.hurt = 0.
        self.dash_cooldown = 0.
        self.special_cooldown = 0.
        self.special_time = 0.
        self.boss_defeated = False
        self.boss_death_time = 0.
        self.shockwaves = []
        self.action = 'idle'
        self.action_time = 0.
        self.death_time = 0.
        self.camera = 0.
        self.projectiles, self.particles = [], []
        self.width = 1800 if self.level < 4 else 960
        self.platforms = [pygame.Rect(0, FLOOR, self.width, 70)]
        self.hazards = [pygame.Rect(x, FLOOR-14, 50, 14) for x in (710, 1230)] if 0 < self.level < 4 else []
        if self.level < 4:
            layouts = (
                ((290,380,140),(550,315,120),(850,390,150),(1130,330,140),(1450,380,130)),
                ((240,390,120),(460,330,140),(750,365,120),(1030,300,150),(1410,375,160)),
                ((300,360,170),(610,400,130),(850,325,130),(1150,385,170),(1480,315,140)),
                ((250,390,130),(490,345,130),(750,300,130),(1040,380,140),(1330,330,160)))
            for x, y, w in layouts[self.level]:
                self.platforms.append(pygame.Rect(x, y, w, 20))
            self.enemies = [self.enemy(x, kind=kind) for x, kind in zip((520, 920, 1310, 1580), ('goblin', 'ninja', 'golem', 'goblin'))]
        else:
            self.enemies = [self.enemy(690, True)]
        self.banner = 2.5

    def enemy(self, x, boss=False, kind='goblin'):
        hp = 240 if boss else {'goblin': 35, 'ninja': 30, 'golem': 65}[kind]
        return {'x': float(x), 'y': FLOOR - (100 if boss else 44), 'hp': hp,
                'maxhp': hp, 'boss': boss, 'kind': kind, 'timer': 1.5,
                'flash': 0., 'dir': -1, 'dead_time': 0., 'mode': 'patrol',
                'home': float(x), 'patrol_dir': -1, 'mode_time': 0., 'attack_count': 0}

    def update_enemy(self, e, dt):
        distance = abs(self.x - e['x'])
        kind = e['kind']
        e['mode_time'] = max(0., e['mode_time'] - dt)
        if e['mode'] in ('windup', 'recover'):
            if e['mode_time'] > 0:
                return
            if e['mode'] == 'windup':
                reach = {'goblin': 65, 'ninja': 105, 'golem': 90}[kind]
                if distance < reach and abs(self.y - e['y']) < 65:
                    self.hurt_player({'goblin': 8, 'ninja': 10, 'golem': 18}[kind])
                e['mode'] = 'recover'
                e['mode_time'] = {'goblin': .65, 'ninja': .8, 'golem': 1.3}[kind]
                return
            e['mode'] = 'chase'
        if distance < 55:
            e['mode'] = 'windup'
            e['mode_time'] = {'goblin': .35, 'ninja': .2, 'golem': .75}[kind]
            return
        if distance < 260:
            e['mode'] = 'chase'
            e['dir'] = -1 if self.x < e['x'] else 1
            speed = {'goblin': 70, 'ninja': 135, 'golem': 38}[kind]
            e['x'] = max(0, min(self.width-30, e['x'] + e['dir'] * speed * dt))
        else:
            e['mode'] = 'patrol'
            if abs(e['x'] - e['home']) >= 65:
                e['patrol_dir'] = -1 if e['x'] > e['home'] else 1
            e['dir'] = e['patrol_dir']
            e['x'] += e['dir'] * 25 * dt

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), 30, 48)

    def burst(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append([x, y, random.uniform(-100, 100), random.uniform(-140, 30), random.uniform(.2, .55), color])

    def jump(self):
        if self.grounded:
            self.vy = -510
            self.grounded = False
            self.burst(self.x + 15, self.y + 48, (180, 169, 166), 5)

    def drop(self):
        if not self.grounded:
            return
        feet = self.y + self.rect().height
        for platform in self.platforms[1:]:
            if abs(feet - platform.top) <= 1 and self.rect().right > platform.left and self.rect().left < platform.right:
                self.drop_platform = platform
                self.grounded = False
                self.y += 2
                self.vy = max(self.vy, 40)
                break

    def attack(self):
        if self.cooldown > 0: return
        if self.sound: self.sounds.play("cast")
        self.attack_timer = .25
        self.cooldown = .35 if self.class_index != 1 else .45
        if self.class_index == 1:
            hit = pygame.Rect(self.x + (28 if self.facing > 0 else -65), self.y - 5, 67, 58)
            for e in self.enemies:
                if hit.colliderect(self.enemy_rect(e)): self.damage_enemy(e, 25)
        else:
            self.projectiles.append({'x': self.x + 15, 'y': self.y + 23, 'vx': self.facing * (520 if self.class_index == 2 else 400), 'enemy': False, 'life': 1.3})

    def special(self):
        if self.state != 'play' or self.special_cooldown > 0:
            return
        self.special_cooldown = 4.0
        self.special_time = .4
        self.attack_timer = .3
        if self.sound: self.sounds.play('cast')
        if self.class_index == 2:
            self.projectiles.append({'x': self.x + 15, 'y': self.y + 23,
                                     'vx': self.facing * 650, 'enemy': False,
                                     'life': 1.8, 'damage': 32, 'pierce': True, 'hit': set()})
        else:
            radius = 155 if self.class_index == 0 else 100
            area = pygame.Rect(self.x-radius, self.y-60, radius*2+30, 160)
            for enemy in self.enemies:
                if area.colliderect(self.enemy_rect(enemy)):
                    self.damage_enemy(enemy, 32 if self.class_index == 0 else 42)
            self.burst(self.x+15, self.y+20, COLORS[self.class_index], 24)

    def damage_enemy(self, e, amount):
        if self.sound: self.sounds.play("impact")
        e['hp'] -= amount
        e['flash'] = .16
        self.burst(e['x'] + (40 if e['boss'] else 15), e['y'] + 20, (255, 195, 120))

    def enemy_rect(self, e):
        return pygame.Rect(e['x'], e['y'], 80 if e['boss'] else 30, 100 if e['boss'] else 44)

    def hurt_player(self, amount):
        if self.hurt <= 0 and self.dash_timer <= 0:
            self.hp -= amount
            self.hurt = .9
            self.burst(self.x + 15, self.y + 20, (255, 100, 100))
            if self.hp <= 0:
                self.hp = 0
                self.state = 'dying'
                self.death_time = 0.

    def update(self, dt):
        self.time += dt
        if self.state == 'dying':
            self.death_time += dt
            if self.death_time >= .9: self.state = 'defeat'
            return
        if self.state != 'play': return
        self.banner = max(0, self.banner-dt)
        self.hurt = max(0, self.hurt-dt)
        self.cooldown = max(0, self.cooldown-dt)
        self.special_cooldown = max(0, self.special_cooldown-dt)
        self.special_time = max(0, self.special_time-dt)
        self.dash_cooldown = max(0, self.dash_cooldown-dt)
        self.attack_timer = max(0, self.attack_timer-dt)
        self.dash_timer = max(0, self.dash_timer-dt)
        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        if direction and self.dash_timer <= 0: self.facing = direction
        speed = self.facing * 470 if self.dash_timer else direction * 210
        self.x = max(0, min(self.width-30, self.x + speed * dt))
        previous_bottom = self.y + 48
        self.vy = min(850, self.vy + 1250 * dt)
        self.y += self.vy * dt
        self.grounded = False
        if self.drop_platform is not None and self.y >= self.drop_platform.bottom:
            self.drop_platform = None
        for p in self.platforms:
            if p is self.drop_platform:
                continue
            if self.vy >= 0 and previous_bottom <= p.top and self.y + 48 >= p.top and self.x + 30 > p.left and self.x < p.right:
                self.y, self.vy, self.grounded = float(p.top-48), 0., True
        self.camera = max(0, min(self.width-W, self.x-W*.35))
        if any(self.rect().colliderect(hazard) for hazard in self.hazards):
            self.hurt_player(12)
            if self.state != 'play': return
        for e in self.enemies[:]:
            e['flash'] = max(0, e['flash']-dt)
            if e['hp'] <= 0:
                if e['boss']:
                    e['dead_time'] += dt
                    if e['dead_time'] < 1.2:
                        continue
                    self.boss_defeated = True
                self.burst(e['x']+20, e['y']+20, (255, 170, 90), 25)
                self.enemies.remove(e)
                continue
            if not e['boss']:
                self.update_enemy(e, dt)
                if self.state != 'play': break
                continue
            e['dir'] = -1 if self.x < e['x'] else 1
            distance = abs(self.x - e['x'])
            phase2 = e['boss'] and e['hp'] <= e['maxhp']/2
            if distance < (500 if e['boss'] else 240) and distance > (100 if e['boss'] else 35):
                e['x'] += e['dir'] * (100 if phase2 else 65 if e['boss'] else 70) * dt
            if self.rect().colliderect(self.enemy_rect(e)): self.hurt_player(14 if e['boss'] else 8)
            if self.state != 'play': break
            e['timer'] -= dt
            if e['boss'] and e['timer'] <= 0:
                e['timer'] = .85 if phase2 else 1.5
                if e['attack_count'] % 2:
                    for wave_dir in (-1, 1):
                        self.shockwaves.append({'x': e['x']+40, 'vx': wave_dir * (260 if phase2 else 190), 'life': 3.})
                    self.burst(e['x']+40, FLOOR-5, (213, 169, 115), 18)
                else:
                    for offset in ((-55, 0, 55) if phase2 else (0,)):
                        self.projectiles.append({'x': e['x']+40, 'y': e['y']+45, 'vx': e['dir'] * (280 if phase2 else 220), 'vy': offset, 'enemy': True, 'life': 4})
                e['attack_count'] += 1
        if self.state != 'play': return
        for wave in self.shockwaves[:]:
            wave['x'] += wave['vx'] * dt
            wave['life'] -= dt
            hitbox = pygame.Rect(wave['x']-13, FLOOR-20, 26, 20)
            if hitbox.colliderect(self.rect()):
                self.hurt_player(15)
                wave['life'] = 0
            if wave['life'] <= 0 or not 0 <= wave['x'] <= self.width:
                self.shockwaves.remove(wave)
        for p in self.projectiles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p.get('vy', 0) * dt
            p['life'] -= dt
            box = pygame.Rect(p['x']-7, p['y']-7, 14, 14)
            if p['enemy'] and box.colliderect(self.rect()):
                self.hurt_player(12); p['life'] = 0
            elif not p['enemy']:
                for e in self.enemies:
                    if box.colliderect(self.enemy_rect(e)) and id(e) not in p.get('hit', set()):
                        self.damage_enemy(e, p.get('damage', 18 if self.class_index == 0 else 15))
                        if p.get('pierce'):
                            p['hit'].add(id(e))
                        else:
                            p['life'] = 0
                            break
            if p['life'] <= 0 or p['x'] < 0 or p['x'] > self.width: self.projectiles.remove(p)
        for p in self.particles[:]:
            p[0] += p[2]*dt; p[1] += p[3]*dt; p[3] += 200*dt; p[4] -= dt
            if p[4] <= 0: self.particles.remove(p)
        if self.level < 4 and self.x > self.width-85 and not self.enemies:
            self.level += 1
            self.hp = min(self.max_hp, self.hp + 20)
            self.load_level()
        elif self.level == 4 and self.boss_defeated and self.x > self.width-85:
            self.state = 'victory'

    def text(self, value, x, y, color=(240, 222, 191), font=None, center=True):
        surface = (font or self.font).render(value, True, color)
        self.screen.blit(surface, surface.get_rect(center=(x, y)) if center else (x, y))

    def sprite(self, sheet, column, row, size, x, y, flip=False, source_size=16):
        src = pygame.Rect(column*source_size, row*source_size, source_size, source_size)
        image = pygame.transform.scale(sheet.subsurface(src), size)
        if flip: image = pygame.transform.flip(image, True, False)
        self.screen.blit(image, (int(x), int(y)))

    def draw_art(self, image, size, x, y, flip=False):
        image = pygame.transform.scale(image, size)
        if flip: image = pygame.transform.flip(image, True, False)
        self.screen.blit(image, (int(x), int(y)))

    def background(self):
        palettes = ((20,25,49), (12,32,54), (20,43,38), (38,29,50), (35,22,41))
        self.screen.blit(self.art['scenes'][self.level], (0, 0))
        shade = pygame.Surface((W,H), pygame.SRCALPHA)
        shade.fill((8, 10, 24, 115))
        self.screen.blit(shade,(0,0))
        for i in range(24):
            x = (i*113 - self.camera*.5) % (W+30)
            y = 80 + (i*79)%300 + math.sin(self.time*2+i)*4
            pygame.draw.circle(self.screen, (80, 120, 145), (int(x), int(y)), 2)

    def draw(self):
        self.background()
        if self.state in ('menu', 'options', 'classes'):
            if self.state == 'classes':
                self.screen.blit(self.art['selection'], (0, 0))
                shade = pygame.Surface((W,H), pygame.SRCALPHA); shade.fill((8,8,20,155)); self.screen.blit(shade,(0,0))
            self.text('LEGADO ARCANO', W//2, 100, (246,190,125), self.big)
            if self.state == 'menu':
                self.text('UMA AVENTURA DE PLATAFORMA', W//2, 157, font=self.small)
                self.buttons(('Jogar', 'Opções', 'Sair'))
                self.text('A/D: mover | W: pular | S: descer | J: atacar', W//2, 438, font=self.small)
                self.text('K: especial | Shift: esquiva | Esc: pausa | Enter: confirmar', W//2, 464, font=self.small)
                self.text('R: reiniciar | M: menu | Mouse ou setas: navegar', W//2, 490, font=self.small)
            elif self.state == 'options':
                self.buttons(('Som: ' + ('Ligado' if self.sound else 'Desligado'), 'Voltar'))
                self.text('A/D: mover | W: pular | S: descer | J: atacar', W//2, 440, font=self.small)
            else:
                self.text('Escolha sua classe', W//2, 175)
                self.buttons(CLASSES + ('Voltar',))
                descriptions = ('Magia a média distância - explosão arcana', 'Espada corpo a corpo - golpe pesado', 'Flechas rápidas - disparo perfurante', '')
                self.text(descriptions[self.selection], W//2, 480, font=self.small)
            pygame.display.flip(); return
        for p in self.platforms:
            r = p.move(-self.camera, 0)
            pygame.draw.rect(self.screen, (54,48,62), r)
            pygame.draw.rect(self.screen, (131,115,128), (r.x,r.y,r.w,6))
            for x in range(r.x, r.right, 48): pygame.draw.line(self.screen, (77,67,80), (x,r.y+8), (x,r.bottom), 2)
        for hazard in self.hazards:
            x = hazard.x-self.camera
            for offset in range(0, hazard.width, 10):
                pygame.draw.polygon(self.screen, (214, 197, 205), [(x+offset,FLOOR),(x+offset+5,FLOOR-14),(x+offset+10,FLOOR)])
        if self.level < 4 or self.boss_defeated:
            x = self.width-60-self.camera
            pygame.draw.ellipse(self.screen, (111, 77, 180) if not self.enemies else (65,57,78), (x, FLOOR-95, 45, 95), 5)
        for e in self.enemies:
            x = e['x']-self.camera
            if e['boss']:
                phase2 = e['hp'] <= e['maxhp']/2
                if e['timer'] < .45:
                    warning = pygame.Surface((W, 18), pygame.SRCALPHA)
                    warning.fill((255, 75, 75, 80 if int(self.time*12)%2 else 35))
                    warning_y = FLOOR-18 if e['attack_count'] % 2 else int(e['y']+36)
                    self.screen.blit(warning, (0, warning_y))
                if e['hp'] <= 0:
                    progress = min(1., e['dead_time']/1.2)
                    self.draw_art(self.art['mobs'][3][0], (150, max(4, int(135*(1-progress)))), x-35, FLOOR-max(4,int(135*(1-progress))), e['dir']<0)
                    if int(self.time*15)%2:
                        pygame.draw.circle(self.screen, (250,190,120), (int(x+40),int(e['y']+50)), int(12+progress*35), 3)
                else:
                    self.draw_art(self.art['mobs'][3][int(self.time*(11 if phase2 else 7))%3], (150,135), x-35, e['y']-35, e['dir']<0)
                pygame.draw.rect(self.screen, (70,33,47), (250,35,460,15))
                pygame.draw.rect(self.screen, (204,61,83) if phase2 else (141,102,215), (250,35,int(460*max(0,e['hp'])/e['maxhp']),15))
                self.text('GUARDIÃO ANCIÃO  •  ' + ('FASE 2' if phase2 else 'FASE 1'), 480, 20, font=self.small)
            else:
                frame = int(self.time*7)%3
                art_index = {'goblin': 2, 'ninja': 1, 'golem': 3}[e['kind']]
                if e['mode'] == 'windup':
                    pygame.draw.circle(self.screen, (240, 110, 90), (int(x+15), int(e['y']-10)), 8, 2)
                self.draw_art(self.art['mobs'][art_index][frame], (65,65), x-17, e['y']-21, e['dir']<0)
        keys = pygame.key.get_pressed()
        moving = keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
        action = ('death' if self.state in ('dying','defeat') else 'hit' if self.hurt else 'dash' if self.dash_timer else 'attack' if self.attack_timer else
                  'jump' if not self.grounded and self.vy < 0 else 'fall' if not self.grounded else 'run' if moving else 'idle')
        frames = self.art['actors'][self.class_index][action]
        if action != self.action:
            self.action, self.action_time = action, self.time
        elapsed = self.death_time if action == 'death' else self.time - self.action_time
        index = int(elapsed * (12 if action in ('attack','dash') else 8))
        if action in ('attack', 'death', 'hit'):
            index = min(index, len(frames)-1)
        frame = frames[index % len(frames)]
        if action == 'death' or not self.hurt or int(self.hurt*12)%2:
            self.draw_art(frame, (70,75), self.x-self.camera-20, self.y-27, self.facing<0)
        if self.attack_timer and self.class_index == 1:
            pygame.draw.arc(self.screen, (245,237,219), (self.x-self.camera + (13 if self.facing>0 else -53), self.y-12, 70,70), -1.5, 1.5, 5)
        for wave in self.shockwaves:
            x = int(wave['x']-self.camera)
            pygame.draw.polygon(self.screen, (255, 190, 105), [(x-16,FLOOR),(x,FLOOR-22),(x+16,FLOOR)])
        for p in self.projectiles:
            color = (235,89,118) if p['enemy'] else COLORS[self.class_index]
            pygame.draw.circle(self.screen, color, (int(p['x']-self.camera),int(p['y'])), 8)
            if not p['enemy'] and self.class_index == 0:
                self.draw_art(self.art['effects'][int(self.time*12)%4], (45,45), p['x']-self.camera-22, p['y']-22, p['vx']<0)
            pygame.draw.circle(self.screen, (255,245,218), (int(p['x']-self.camera),int(p['y'])), 3)
        for p in self.particles: pygame.draw.circle(self.screen, p[5], (int(p[0]-self.camera), int(p[1])), max(1,int(p[4]*8)))
        pygame.draw.rect(self.screen, (50,27,39), (20,20,204,20))
        pygame.draw.rect(self.screen, (212,75,90), (22,22,max(0,int(self.hp/self.max_hp*200)),16))
        self.text(f'{self.hp}/{self.max_hp}', 120, 30, font=self.small)
        self.text('Especial: pronto' if self.special_cooldown <= 0 else f'Especial: {self.special_cooldown:.1f}s', 20, 72, font=self.small, center=False)
        self.text(CLASSES[self.class_index] + '  •  ' + NAMES[self.level], 20, 47, font=self.small, center=False)
        if self.level < 4: self.text('Inimigos: ' + str(len(self.enemies)), W-100, 30, font=self.small)
        self.text('A/D mover | W pular | S descer | J atacar | K especial | SHIFT esquivar', W//2, H-18, font=self.small)
        if self.banner: self.text(NAMES[self.level], W//2, 105, (255,215,156), self.big)
        if self.state in ('pause','victory','defeat'):
            overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((8,8,20,200)); self.screen.blit(overlay,(0,0))
            self.text({'pause':'Pausado','victory':'Vitória!','defeat':'Fim de jogo'}[self.state], W//2, 190, font=self.big)
            self.text('Enter: continuar  |  R: reiniciar  |  M: menu' if self.state == 'pause' else 'R: reiniciar  |  Enter: menu', W//2, 280, font=self.small)
        pygame.display.flip()

    def buttons(self, labels):
        for i, label in enumerate(labels):
            rect = pygame.Rect(W//2-150, 210+i*62, 300, 48)
            pygame.draw.rect(self.screen, (66,55,74) if i == self.selection else (27,27,42), rect, border_radius=6)
            pygame.draw.rect(self.screen, (221,157,97) if i == self.selection else (92,79,88), rect, 2, border_radius=6)
            self.text(label, rect.centerx, rect.centery)

    def choose(self):
        if self.state == 'menu':
            if self.selection == 0: self.state = 'classes'; self.selection = 0
            elif self.selection == 1: self.state = 'options'; self.selection = 0
            else: self.running = False
        elif self.state == 'options':
            if self.selection == 0: self.sound = not self.sound
            else: self.state = 'menu'; self.selection = 0
        elif self.state == 'classes':
            if self.selection == 3: self.state = 'menu'; self.selection = 0
            else: self.class_index = self.selection; self.reset(); self.state = 'play'

    def event(self, event):
        if event.type == pygame.QUIT: self.running = False; return
        if self.state in ('menu','options','classes'):
            count = {'menu':3,'options':2,'classes':4}[self.state]
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN,pygame.K_s): self.selection = (self.selection+1)%count
                elif event.key in (pygame.K_UP,pygame.K_w): self.selection = (self.selection-1)%count
                elif event.key in (pygame.K_RETURN,pygame.K_KP_ENTER): self.choose()
                elif event.key == pygame.K_ESCAPE and self.state != 'menu': self.state='menu'; self.selection=0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(count):
                    if pygame.Rect(W//2-150,210+i*62,300,48).collidepoint(event.pos): self.selection=i; self.choose(); break
        elif event.type == pygame.KEYDOWN:
            if self.state == 'play':
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP): self.jump()
                elif event.key in (pygame.K_s, pygame.K_DOWN): self.drop()
                elif event.key in (pygame.K_j, pygame.K_z): self.attack()
                elif event.key == pygame.K_k: self.special()
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    if self.dash_timer <= 0 and not getattr(self,'dash_cooldown',0): self.dash_timer=.16; self.dash_cooldown=1.0
                elif event.key == pygame.K_ESCAPE: self.state='pause'
            elif self.state in ('pause', 'defeat', 'victory'):
                if event.key == pygame.K_r: self.reset(); self.state = 'play'
                elif event.key == pygame.K_m: self.state = 'menu'; self.selection = 0
                elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    if self.state == 'pause': self.state='play'
                    else: self.state='menu'; self.selection=0

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60)/1000, .05)
            for event in pygame.event.get(): self.event(event)
            self.update(dt); self.draw()
        pygame.quit()
