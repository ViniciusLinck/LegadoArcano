"""Player movement in logical screen coordinates."""

import pygame

from src import settings
from src.collision import move_with_collisions
from src.settings import PLAYER_SIZE, PLAYER_SPEED


class Player:
    def __init__(self, position: tuple[float, float]):
        self.position = pygame.Vector2(position)
        self.rect = pygame.Rect(0, 0, *PLAYER_SIZE)
        self.rect.center = self.position
        self.hp = settings.MAX_HP
        self.max_hp = settings.MAX_HP
        self.invulnerability = 0.0
        self.dash_time = 0.0
        self.dash_direction = pygame.Vector2(1, 0)
        self.facing = pygame.Vector2(1, 0)
        self.moving = False
        self.cooldowns = {'basic': 0.0, 'spear': 0.0, 'explosion': 0.0, 'dash': 0.0}
        self.damage_multiplier = 1.0
        self.cooldown_multiplier = 1.0

    def take_damage(self, amount: float) -> bool:
        if self.invulnerability > 0 or self.dash_time > 0 or self.hp <= 0:
            return False
        self.hp = max(0, self.hp - amount)
        self.invulnerability = settings.HIT_INVULNERABILITY
        return True

    def use_ability(self, name: str) -> bool:
        if self.hp <= 0 or self.cooldowns[name] > 0:
            return False
        durations = {'basic': settings.BASIC_COOLDOWN, 'spear': settings.SPEAR_COOLDOWN,
                     'explosion': settings.EXPLOSION_COOLDOWN, 'dash': settings.DASH_COOLDOWN}
        multiplier = self.cooldown_multiplier if name in ('spear', 'explosion') else 1.0
        self.cooldowns[name] = durations[name] * multiplier
        return True

    def dash(self, direction: tuple[float, float]) -> bool:
        if not self.use_ability('dash'):
            return False
        vector = pygame.Vector2(direction)
        self.dash_direction = vector.normalize() if vector.length_squared() else self.facing.copy()
        self.dash_time = settings.DASH_DURATION
        return True

    def update(self, direction: tuple[float, float], dt: float, bounds: pygame.Rect, obstacles=()) -> None:
        dt = max(0.0, dt)
        for key in self.cooldowns:
            self.cooldowns[key] = max(0.0, self.cooldowns[key] - dt)
        self.invulnerability = max(0.0, self.invulnerability - dt)
        movement = pygame.Vector2(direction)
        self.moving = bool(movement.length_squared())
        if movement.length_squared() > 0:
            movement = movement.normalize()
            self.facing = movement.copy()
        dash_step = min(dt, self.dash_time)
        self.dash_time = max(0.0, self.dash_time - dt)
        delta = self.dash_direction * settings.DASH_SPEED * dash_step + movement * PLAYER_SPEED * (dt - dash_step)
        self.position = move_with_collisions(self.position, self.rect.size, delta, bounds, obstacles)
        self.rect.center = self.position
