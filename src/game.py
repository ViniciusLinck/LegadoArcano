"""Window, input, game states and rendering for Arcane Trials."""

from enum import Enum, auto
import math

import pygame

from src import settings
from src.assets import Sounds, resource_path
from src.animation import character_frame, creature_frame
from src.maps import MapRenderer
from src.effects import EFFECT_DURATIONS, EffectLibrary
from src.player import Player
from src.ui import Menu
from src.world import World


class GameState(Enum):
    MENU = auto()
    CONTROLS = auto()
    PLAYING = auto()
    PAUSED = auto()
    UPGRADE = auto()
    LEVEL_UP = auto()
    TRANSITION = auto()
    VICTORY = auto()
    DEFEAT = auto()


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(settings.WINDOW_SIZE)
        pygame.display.set_caption('Arcane Trials — As Provações Arcanas')
        self.canvas = pygame.Surface(settings.LOGICAL_SIZE)
        self.clock = pygame.time.Clock()
        self.menu = Menu()
        self.sounds = Sounds()
        self.effect_library = EffectLibrary()
        self.state = GameState.MENU
        self.running = True
        self.bounds = pygame.Rect(settings.ARENA_RECT)
        self.map_renderer = MapRenderer(self.bounds)
        self.player = Player(self.bounds.center)
        self.world = World(self.player, self.bounds)
        self.mage_sheet = self._load_mage()
        self.enemy_sheets = self._load_enemy_sheets()
        self.dragon_parts = self._load_dragon_parts()
        self.pause_selected = 0
        self.boss_defeat_time = 0.0
        self.animation_time = 0.0
        self.sequence_time = 0.0
        self.next_room = 1
        self.room_loaded = False
        self.upgrade_label = ''
        self.cast_time = 0.0

    def _load_mage(self):
        try:
            image = pygame.image.load(str(resource_path('assets', 'sprites', 'ninja-adventure', 'mago_laranja.png'))).convert_alpha()
            return image if image.get_width() >= 64 and image.get_height() >= 112 else None
        except (FileNotFoundError, pygame.error, OSError):
            return None

    def _load_enemy_sheets(self):
        names = {'goblin': 'goblin.png', 'golem': 'golem.png', 'wizard': 'feiticeiro.png',
                 'ninja': 'ninja.png', 'warrior': 'guerreiro.png', 'dragon': 'dragao.png'}
        result = {}
        for kind, filename in names.items():
            try:
                result[kind] = pygame.image.load(str(resource_path('assets', 'sprites', 'ninja-adventure', filename))).convert_alpha()
            except (FileNotFoundError, pygame.error, OSError):
                pass
        return result

    def _load_dragon_parts(self):
        parts = {}
        for part in ('head', 'wing', 'body1', 'body2', 'bodyend'):
            try:
                parts[part] = pygame.image.load(str(resource_path('assets', 'sprites', 'ninja-adventure',
                                      f'dragao_chefe_{part}.png'))).convert_alpha()
            except (FileNotFoundError, pygame.error, OSError):
                return {}
        return parts

    def _new_run(self):
        self.player = Player(self.bounds.center)
        self.world = World(self.player, self.bounds)
        self.boss_defeat_time = 0.0
        self.animation_time = 0.0
        self.sequence_time = 0.0
        self.cast_time = 0.0
        self.state = GameState.PLAYING

    def _choose_menu(self, index):
        self.sounds.play('confirm')
        if index == 0:
            self._new_run()
        elif index == 1:
            self.state = GameState.CONTROLS
        elif index == 2:
            self.running = False

    def _logical_pos(self, pos):
        return (pos[0] * settings.LOGICAL_SIZE[0] / self.window.get_width(),
                pos[1] * settings.LOGICAL_SIZE[1] / self.window.get_height())

    def _pause_choice(self, choice):
        if choice == 0:
            self.state = GameState.PLAYING
        elif choice == 1:
            self._new_run()
        else:
            self.menu.selected = 0
            self.state = GameState.MENU

    def _advance(self):
        if self.world.complete and self.world.chosen_upgrade and self.world.room_index < self.world.final_level:
            self.next_room = self.world.room_index + 1
            self.room_loaded = False
            self.sequence_time = 0.0
            self.state = GameState.TRANSITION
            self.sounds.play('confirm')

    def _upgrade(self, index):
        self.world.apply_upgrade(('power', 'vital', 'flow')[index])
        self.upgrade_label = ('PODER ARCANO', 'ESSÊNCIA VITAL', 'FLUXO MÍSTICO')[index]
        self.sequence_time = 0.0
        self.state = GameState.LEVEL_UP
        self.sounds.play('confirm')

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu.selected = (self.menu.selected + 1) % len(self.menu.buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.menu.selected = (self.menu.selected - 1) % len(self.menu.buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._choose_menu(self.menu.selected)
            elif self.state == GameState.CONTROLS:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.state = GameState.MENU
                    self.menu.selected = 0
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.pause_selected = 0
                    self.state = GameState.PAUSED
                elif event.key == pygame.K_e:
                    self._advance()
                elif event.key == pygame.K_q and self.world.explode():
                    self.cast_time = 0.22
                    self.sounds.play('impact')
                elif event.key == pygame.K_SPACE:
                    keys = pygame.key.get_pressed()
                    direction = (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                                 int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
                    self.player.dash(direction)
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pause_selected = (self.pause_selected + 1) % 3
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pause_selected = (self.pause_selected - 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._pause_choice(self.pause_selected)
            elif self.state == GameState.UPGRADE:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self._upgrade(event.key - pygame.K_1)
            elif self.state in (GameState.VICTORY, GameState.DEFEAT):
                if event.key in (pygame.K_RETURN, pygame.K_r):
                    self._new_run()
                elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                    self.menu.selected = 0
                    self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = self._logical_pos(event.pos)
            if self.state == GameState.MENU and event.button == 1:
                for index, (_, rect) in enumerate(self.menu.buttons):
                    if rect.collidepoint(pos):
                        self._choose_menu(index)
                        break
            elif self.state == GameState.PLAYING:
                if event.button == 1 and self.world.fire(pos, 'basic'):
                    self.cast_time = 0.16
                    self.sounds.play('cast')
                elif event.button == 3 and self.world.fire(pos, 'spear'):
                    self.cast_time = 0.22
                    self.sounds.play('cast')
            elif self.state == GameState.UPGRADE and event.button == 1:
                for index, rect in enumerate(self.menu.upgrade_rects):
                    if rect.collidepoint(pos):
                        self._upgrade(index)
                        break
            elif self.state == GameState.PAUSED and event.button == 1:
                for index, rect in enumerate(self.menu.pause_rects):
                    if rect.collidepoint(pos):
                        self._pause_choice(index)
                        break
            elif self.state in (GameState.VICTORY, GameState.DEFEAT) and event.button == 1:
                for index, rect in enumerate(self.menu.end_rects):
                    if rect.collidepoint(pos):
                        if index == 0:
                            self._new_run()
                        else:
                            self.menu.selected = 0
                            self.state = GameState.MENU
                        break

    def update(self, dt):
        if self.state == GameState.TRANSITION:
            self.sequence_time += max(0.0, dt)
            if not self.room_loaded and self.sequence_time >= settings.TRANSITION_DURATION / 2:
                self.world.load_room(self.next_room)
                self.room_loaded = True
            if self.sequence_time >= settings.TRANSITION_DURATION:
                self.state = GameState.PLAYING
            return
        if self.state == GameState.LEVEL_UP:
            self.sequence_time += max(0.0, dt)
            if self.sequence_time >= settings.LEVEL_UP_DURATION:
                self.state = GameState.PLAYING
            return
        if self.state != GameState.PLAYING:
            return
        self.animation_time += dt
        self.cast_time = max(0.0, self.cast_time - dt)
        keys = pygame.key.get_pressed()
        direction = (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                     int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
        self.player.update(direction, dt, self.bounds, self.world.obstacles)
        if self.player.dash_time > 0 and len(self.world.effects) < 20:
            self.world.effects.append([self.player.position.copy(), EFFECT_DURATIONS['dash'], 'dash'])
        if pygame.mouse.get_pressed()[0]:
            if self.world.fire(self._logical_pos(pygame.mouse.get_pos()), 'basic'):
                self.cast_time = 0.16
                self.sounds.play('cast')
        self.world.update(dt)
        if self.player.hp <= 0:
            self.state = GameState.DEFEAT
        elif self.world.complete and self.world.room_index > 0 and not self.world.chosen_upgrade:
            self.state = GameState.UPGRADE
        elif self.world.complete and self.world.room_index == self.world.final_level:
            self.boss_defeat_time += dt
            if self.boss_defeat_time >= 1:
                self.state = GameState.VICTORY

    def _draw_arena(self):
        self.canvas.blit(self.map_renderer.get(self.world.room_index), (0, 0))
        for pos, timer in self.world.hazards:
            pygame.draw.circle(self.canvas, (210, 70, 80), pos, 32, 2)
            pygame.draw.circle(self.canvas, (235, 120, 90), pos, max(2, int(32 * (1 - min(timer, 1)))), 1)
        for enemy in self.world.enemies:
            if not enemy.alive:
                continue
            if enemy.windup > 0:
                pygame.draw.circle(self.canvas, (235, 90, 60), enemy.position, 42 if enemy.kind == 'golem' and not enemy.is_boss else 28, 2)
            colors = {'goblin': (92, 180, 95), 'wizard': (227, 141, 65), 'golem': (145, 150, 163),
                      'ninja': (146, 113, 183), 'warrior': (186, 184, 155), 'dragon': (170, 210, 85)}
            sheet = self.enemy_sheets.get(enemy.kind)
            sprite_size = 58 if enemy.is_boss else (40 if enemy.kind in ('golem', 'dragon') else 32)
            if enemy.is_boss and enemy.kind == 'dragon' and self.dragon_parts:
                self._draw_dragon_boss(enemy)
            elif sheet:
                frame = creature_frame(enemy.kind, enemy.facing, enemy.animation_time,
                                       enemy.windup > 0 or enemy.attacking_time > 0)
                sprite = sheet.subsurface(frame)
                if enemy.kind in ('goblin', 'golem') and enemy.facing.x < 0:
                    sprite = pygame.transform.flip(sprite, True, False)
                sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                if enemy.hit_flash > 0:
                    sprite.fill((80, 80, 80, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.canvas.blit(sprite, sprite.get_rect(midbottom=enemy.rect.midbottom))
            else:
                pygame.draw.ellipse(self.canvas, (255, 255, 255) if enemy.hit_flash else colors[enemy.kind], enemy.rect)
            if not enemy.is_boss:
                labels = {'goblin': 'GOBLIN', 'golem': 'GOLEM', 'wizard': 'FEITICEIRO',
                          'ninja': 'NINJA', 'warrior': 'GUERREIRO', 'dragon': 'DRAGÃO'}
                bar_y = enemy.rect.bottom - sprite_size - 4
                self.menu.draw_text(self.canvas, labels[enemy.kind], (enemy.rect.centerx, bar_y - 7), self.menu.tiny_font, (235, 230, 218))
                pygame.draw.rect(self.canvas, (30, 20, 30), (enemy.rect.left, bar_y, enemy.size, 3))
                pygame.draw.rect(self.canvas, (220, 80, 95), (enemy.rect.left, bar_y, int(enemy.size * enemy.hp / enemy.max_hp), 3))
        for shot in self.world.projectiles:
            self._draw_projectile(shot)
        for pos, time, kind in self.world.effects:
            self._draw_effect(pos, time, kind)
        if self.world.room_index == self.world.final_level and self.world.complete:
            center = (320, 160)
            pygame.draw.polygon(self.canvas, settings.ACCENT, [(320, 142), (332, 160), (320, 178), (308, 160)])
            pygame.draw.circle(self.canvas, settings.ACCENT, center, 20 + int(self.boss_defeat_time * 35), 2)
        pygame.draw.ellipse(self.canvas, (21, 28, 40), self.player.rect.move(0, 6))
        pygame.draw.ellipse(self.canvas, (80, 149, 157), self.player.rect.inflate(5, -5), 1)
        if self.mage_sheet and not (self.player.invulnerability > 0 and int(self.player.invulnerability * 12) % 2):
            frame = character_frame(self.player.facing, self.player.moving, self.animation_time, self.cast_time > 0)
            sprite = self.mage_sheet.subsurface(frame)
            sprite = pygame.transform.scale(sprite, (32, 32))
            self.canvas.blit(sprite, sprite.get_rect(midbottom=self.player.rect.midbottom))
        elif not self.mage_sheet:
            pygame.draw.rect(self.canvas, settings.ACCENT, self.player.rect, border_radius=3)
        if self.cast_time > 0:
            radius = 11 + int((0.22 - min(0.22, self.cast_time)) * 38)
            pygame.draw.circle(self.canvas, (121, 222, 225), self.player.rect.center, radius, 1)
        self.menu.draw_hud(self.canvas, self.player, self.world)

    def _blit_effect(self, name, position, elapsed, duration, size, angle=0, tint=None, loop=False):
        sprite = self.effect_library.frame(name, elapsed, duration, loop)
        if sprite is None:
            return False
        sprite = pygame.transform.scale(sprite, size)
        if tint:
            sprite = sprite.copy()
            sprite.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)
        if angle:
            sprite = pygame.transform.rotate(sprite, angle)
        self.canvas.blit(sprite, sprite.get_rect(center=position))
        return True

    def _draw_projectile(self, shot):
        if shot.friendly and shot.max_hits > 1:
            # The bolt follows its actual aim direction while the sprite cycles.
            angle = -math.degrees(math.atan2(shot.direction.y, shot.direction.x))
            color = (255, 213, 115)
            pygame.draw.line(self.canvas, (137, 91, 50), shot.position - shot.direction * 24, shot.position, 5)
            pygame.draw.line(self.canvas, color, shot.position - shot.direction * 24, shot.position, 2)
            drawn = self._blit_effect('lightning', shot.position, shot.age, 0.48,
                                      (36, 26), angle=angle, loop=True)
        else:
            color = (109, 225, 242) if shot.friendly else (240, 115, 149)
            pygame.draw.circle(self.canvas, color, shot.position, shot.radius + 3, 1)
            tint = None if shot.friendly else (255, 95, 150, 255)
            drawn = self._blit_effect('orb', shot.position, shot.age, 0.4,
                                      (22, 22), tint=tint, loop=True)
        if not drawn:
            pygame.draw.circle(self.canvas, color, shot.position, shot.radius)

    def _draw_effect(self, position, remaining, kind):
        duration = EFFECT_DURATIONS.get(kind, 0.3)
        elapsed = max(0.0, duration - remaining)
        if kind == 'explosion':
            # Two layers use the licensed magic ring and blue burst sprites.
            pygame.draw.circle(self.canvas, (89, 195, 210), position, 68, 1)
            self._blit_effect('ring', position, elapsed, duration, (116, 116))
            if not self._blit_effect('burst', position, elapsed, duration, (136, 136)):
                pygame.draw.circle(self.canvas, settings.ACCENT, position, max(2, int(68 * elapsed / duration)), 2)
        elif kind == 'cast':
            self._blit_effect('ring', position, elapsed, duration, (46, 46))
        elif kind in ('impact', 'hazard'):
            tint = (255, 110, 110, 255) if kind == 'hazard' else None
            if not self._blit_effect('impact', position, elapsed, duration, (32, 36), tint=tint):
                pygame.draw.circle(self.canvas, (240, 180, 130), position, 8, 2)
        elif kind in ('dash', 'death'):
            if not self._blit_effect('smoke', position, elapsed, duration, (34, 16)):
                pygame.draw.circle(self.canvas, settings.ACCENT, position, 6, 1)

    def _draw_dragon_boss(self, enemy):
        """Layer the original CC0 dragon pieces and animate the wings."""
        x, y = enemy.position
        wing = pygame.transform.scale(self.dragon_parts['wing'], (48, 48))
        flap = math.sin(enemy.animation_time * 7) * 8
        right = pygame.transform.rotate(wing, flap)
        left = pygame.transform.flip(right, True, False)
        self.canvas.blit(left, left.get_rect(center=(x - 32, y - 10)))
        self.canvas.blit(right, right.get_rect(center=(x + 32, y - 10)))
        for part, size, offset in (('bodyend', (28, 38), (0, 33)), ('body2', (28, 25), (0, 20)),
                                   ('body1', (30, 26), (0, 8)), ('head', (46, 46), (0, -9))):
            sprite = pygame.transform.scale(self.dragon_parts[part], size)
            if enemy.hit_flash > 0:
                sprite.fill((75, 75, 75, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.canvas.blit(sprite, sprite.get_rect(center=(x + offset[0], y + offset[1])))

    def draw(self):
        if self.state == GameState.MENU:
            self.menu.draw(self.canvas)
        elif self.state == GameState.CONTROLS:
            self.menu.draw_controls(self.canvas)
        else:
            self._draw_arena()
            if self.state == GameState.PAUSED:
                self.menu.draw_pause(self.canvas, self.pause_selected)
            elif self.state == GameState.UPGRADE:
                self.menu.draw_upgrades(self.canvas)
            elif self.state == GameState.LEVEL_UP:
                self.menu.draw_level_up(self.canvas, self.upgrade_label, self.sequence_time / settings.LEVEL_UP_DURATION)
            elif self.state == GameState.TRANSITION:
                self.menu.draw_transition(self.canvas, self.world.ROOM_NAMES[self.next_room], self.sequence_time / settings.TRANSITION_DURATION)
            elif self.state in (GameState.VICTORY, GameState.DEFEAT):
                self.menu.draw_end(self.canvas, self.state == GameState.VICTORY)
        pygame.transform.scale(self.canvas, self.window.get_size(), self.window)
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(settings.FPS) / 1000.0, settings.MAX_FRAME_TIME)
                for event in pygame.event.get():
                    self.handle_event(event)
                if self.running:
                    self.update(dt)
                    self.draw()
        finally:
            pygame.quit()
