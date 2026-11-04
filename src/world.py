"""Fixed rooms, combat, upgrades and run progression."""

import pygame

from src import settings
from src.combat import Projectile
from src.enemy import Enemy


class World:
    ROOM_NAMES = ('Câmara Inicial', 'Salão Abandonado', 'Galeria das Sombras', 'Câmara Ritual',
                  'Salão da Forja', 'Guardião de Pedra', 'Corredor Ardente', 'Santuário dos Ecos',
                  'Câmara Escarlate', 'Portões do Núcleo', 'Dragão do Núcleo')
    final_level = 10
    BOSS_LEVELS = (5, 10)
    # Explicit, repeatable encounter plans. Every normal room contains two waves.
    WAVE_KINDS = {
        1: (('goblin', 'goblin', 'goblin'), ('goblin', 'goblin', 'warrior')),
        2: (('warrior', 'goblin', 'ninja'), ('ninja', 'goblin', 'warrior')),
        3: (('wizard', 'goblin', 'goblin'), ('wizard', 'warrior', 'ninja')),
        4: (('golem', 'warrior', 'goblin'), ('golem', 'wizard', 'ninja')),
        5: (('golem',),),
        6: (('dragon', 'goblin', 'ninja'), ('dragon', 'warrior', 'wizard')),
        7: (('golem', 'wizard', 'ninja'), ('dragon', 'goblin', 'warrior', 'ninja')),
        8: (('dragon', 'dragon', 'goblin'), ('golem', 'wizard', 'wizard', 'ninja')),
        9: (('golem', 'dragon', 'warrior'), ('dragon', 'wizard', 'ninja', 'goblin')),
        10: (('dragon',),),
    }
    SPAWN_POINTS = ((155, 95), (485, 95), (320, 165), (195, 205))

    def __init__(self, player, bounds):
        self.player = player
        self.bounds = bounds
        self.room_index = 0
        self.enemies = []
        self.projectiles = []
        self.effects = []
        self.hazards = []
        self.chosen_upgrade = False
        self.load_room(0)

    def load_room(self, index):
        if not 0 <= index <= self.final_level:
            raise ValueError('Nível inexistente')
        self.room_index = index
        self.waves = [tuple((kind, (320, 110) if self.is_boss_room else self.SPAWN_POINTS[i]) for i, kind in enumerate(wave))
                      for wave in self.WAVE_KINDS.get(index, ())]
        self.wave_number = 0
        self.wave_timer = 0.0
        self.enemies = []
        if self.waves:
            self._spawn_wave()
        self.projectiles = []
        self.effects = []
        self.hazards = []
        self.chosen_upgrade = index in (0, self.final_level)
        self.player.position.update(self.bounds.centerx, self.bounds.bottom - 36)
        self.player.rect.center = self.player.position

    @property
    def complete(self):
        return self.wave_number >= len(self.waves) and all(not enemy.alive for enemy in self.enemies)

    @property
    def is_boss_room(self):
        return self.room_index in self.BOSS_LEVELS

    @property
    def wave_count(self):
        return len(self.waves)

    def _spawn_wave(self):
        wave = self.waves[self.wave_number]
        self.enemies = [Enemy(kind, position, boss=self.is_boss_room) for kind, position in wave]
        self.wave_number += 1
        self.wave_timer = 0.0

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
                if not enemy.alive:
                    self.effects.append([enemy.position.copy(), 0.35, 'death'])
                if delta.length_squared() and not enemy.is_boss:
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
        if self.wave_number < len(self.waves) and not any(enemy.alive for enemy in self.enemies):
            self.wave_timer += dt
            if self.wave_timer >= 0.8:
                self._spawn_wave()
        for enemy in self.enemies:
            old_windup = enemy.windup
            self.projectiles.extend(enemy.update(dt, self.player, self.bounds))
            if enemy.is_boss and enemy.alive and old_windup <= 0 < enemy.windup and enemy.pattern % 2:
                self.hazards.append([self.player.position.copy(), enemy.windup + 0.3])
        living = [enemy for enemy in self.enemies if enemy.alive]
        for i, first in enumerate(living):
            for second in living[i + 1:]:
                delta = second.position - first.position
                distance = delta.length()
                minimum = (first.size + second.size) * 0.4
                if distance < minimum:
                    normal = delta / distance if distance else pygame.Vector2(1, 0)
                    correction = normal * min((minimum - distance) / 2, 35 * dt)
                    first.position -= correction
                    second.position += correction
        for enemy in living:
            half = enemy.size / 2
            enemy.position.x = max(self.bounds.left + half, min(self.bounds.right - half, enemy.position.x))
            enemy.position.y = max(self.bounds.top + half, min(self.bounds.bottom - half, enemy.position.y))
        if self.is_boss_room and self.complete:
            self.projectiles = [shot for shot in self.projectiles if shot.friendly]
            self.hazards = []
        remaining = []
        for pos, timer in self.hazards:
            timer -= dt
            if timer <= 0:
                if self.player.position.distance_to(pos) < 32:
                    self.player.take_damage(18)
                self.effects.append([pos, 0.25, 'hazard'])
            else:
                remaining.append([pos, timer])
        self.hazards = remaining
        for shot in self.projectiles:
            shot.update(dt, self.bounds)
            if not shot.alive:
                continue
            if shot.friendly:
                for enemy in self.enemies:
                    if enemy.alive and shot.rect.colliderect(enemy.rect) and shot.register_hit(enemy):
                        enemy.take_damage(shot.damage)
                        self.effects.append([shot.position.copy(), 0.12, 'impact'])
                        if not enemy.alive:
                            self.effects.append([enemy.position.copy(), 0.35, 'death'])
                            if self.is_boss_room and self.complete:
                                self.hazards = []
                                for other in self.projectiles:
                                    if not other.friendly:
                                        other.alive = False
                        if not shot.alive:
                            break
            elif shot.rect.colliderect(self.player.rect):
                if shot.register_hit(self.player):
                    self.player.take_damage(shot.damage)
        self.projectiles = [shot for shot in self.projectiles if shot.alive]
