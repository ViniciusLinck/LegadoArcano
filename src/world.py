"""Fixed rooms, combat, upgrades and run progression."""

import pygame

from src import settings
from src.combat import Projectile
from src.enemy import Enemy


class World:
    ROOM_NAMES = ('Câmara Inicial', 'Salão Abandonado', 'Câmara Ritual', 'Câmara do Núcleo')
    LAYOUTS = ((), (('shadow', (155, 95)), ('shadow', (485, 95)), ('shadow', (320, 245))),
               (('cultist', (145, 95)), ('cultist', (485, 95)), ('shadow', (200, 240)),
                ('shadow', (440, 240)), ('sentinel', (320, 90))), (('boss', (320, 110)),))

    def __init__(self, player, bounds):
        self.player = player
        self.bounds = bounds
        self.room_index = 0
        self.enemies = []
        self.projectiles = []
        self.effects = []
        self.chosen_upgrade = False
        self.load_room(0)

    def load_room(self, index):
        self.room_index = index
        self.enemies = [Enemy(kind, position) for kind, position in self.LAYOUTS[index]]
        self.projectiles = []
        self.effects = []
        self.chosen_upgrade = index in (0, 3)
        self.player.position.update(self.bounds.centerx, self.bounds.bottom - 36)
        self.player.rect.center = self.player.position

    @property
    def complete(self):
        return all(not enemy.alive for enemy in self.enemies)

    def fire(self, target, kind):
        if not self.player.use_ability(kind):
            return False
        direction = pygame.Vector2(target) - self.player.position
        if kind == 'basic':
            self.projectiles.append(Projectile(self.player.position, direction,
                settings.BASIC_DAMAGE * self.player.damage_multiplier, 340))
        elif kind == 'spear':
            self.projectiles.append(Projectile(self.player.position, direction,
                settings.SPEAR_DAMAGE * self.player.damage_multiplier, 470, max_hits=2))
        return True

    def explode(self):
        if not self.player.use_ability('explosion'):
            return False
        self.effects.append([self.player.position.copy(), 0.35, 'explosion'])
        for enemy in self.enemies:
            delta = enemy.position - self.player.position
            if enemy.alive and delta.length() <= 68:
                enemy.take_damage(settings.EXPLOSION_DAMAGE * self.player.damage_multiplier)
                if delta.length_squared() and enemy.kind != 'boss':
                    enemy.position += delta.normalize() * 24
                    enemy.position.x = max(self.bounds.left + enemy.size / 2, min(self.bounds.right - enemy.size / 2, enemy.position.x))
                    enemy.position.y = max(self.bounds.top + enemy.size / 2, min(self.bounds.bottom - enemy.size / 2, enemy.position.y))
        return True

    def apply_upgrade(self, kind):
        if kind == 'power':
            self.player.damage_multiplier *= 1.2
        elif kind == 'vital':
            self.player.hp = min(self.player.max_hp, self.player.hp + 30)
        elif kind == 'flow':
            self.player.cooldown_multiplier *= 0.8
        else:
            raise ValueError('Unknown upgrade')
        self.chosen_upgrade = True

    def update(self, dt):
        self.effects = [[pos, time - dt, kind] for pos, time, kind in self.effects if time - dt > 0]
        for enemy in self.enemies:
            self.projectiles.extend(enemy.update(dt, self.player, self.bounds))
        for shot in self.projectiles:
            shot.update(dt, self.bounds)
            if not shot.alive:
                continue
            if shot.friendly:
                for enemy in self.enemies:
                    if enemy.alive and shot.rect.colliderect(enemy.rect) and shot.register_hit(enemy):
                        enemy.take_damage(shot.damage)
                        self.effects.append([shot.position.copy(), 0.12, 'impact'])
                        if not shot.alive:
                            break
            elif shot.rect.colliderect(self.player.rect):
                if shot.register_hit(self.player):
                    self.player.take_damage(shot.damage)
        self.projectiles = [shot for shot in self.projectiles if shot.alive]
