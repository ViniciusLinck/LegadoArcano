"""Enemies and the final guardian."""

import math

import pygame

from src.combat import Projectile
from src.collision import move_with_collisions


class Enemy:
    STATS = {'goblin': (30, 72, 10), 'wizard': (25, 48, 9), 'golem': (75, 32, 18),
             'ninja': (25, 100, 9), 'warrior': (45, 60, 12), 'dragon': (55, 52, 12)}

    def __init__(self, kind, position, boss=False):
        self.kind = kind
        self.is_boss = boss
        self.max_hp, self.speed, self.damage = self.STATS[kind]
        if boss:
            self.max_hp = 300 if kind == 'golem' else 380
            self.speed = 38 if kind == 'golem' else 48
            self.damage = 15
        self.hp = self.max_hp
        self.position = pygame.Vector2(position)
        self.size = 42 if boss else (26 if kind == 'golem' else 20)
        self.cooldown = 0.7
        self.windup = 0.0
        self.hit_flash = 0.0
        self.pattern = 0
        self.facing = pygame.Vector2(0, 1)
        self.animation_time = 0.0
        self.attacking_time = 0.0
        self.moving = False
        self.detour_time = 0.0
        self.detour_sign = 1 if position[0] < 320 else -1

    @property
    def alive(self):
        return self.hp > 0

    @property
    def phase(self):
        return 2 if self.is_boss and self.hp <= self.max_hp / 2 else 1

    @property
    def rect(self):
        return pygame.Rect(round(self.position.x - self.size / 2), round(self.position.y - self.size / 2),
                           self.size, self.size)

    def take_damage(self, damage):
        if self.alive:
            self.hp = max(0, self.hp - damage)
            self.hit_flash = 0.12

    def update(self, dt, player, bounds, obstacles=()):
        if not self.alive:
            return []
        previous_position = self.position.copy()
        self.moving = False
        self.cooldown = max(0, self.cooldown - dt)
        self.hit_flash = max(0, self.hit_flash - dt)
        self.animation_time += dt
        self.attacking_time = max(0, self.attacking_time - dt)
        self.detour_time = max(0, self.detour_time - dt)
        delta = player.position - self.position
        distance = delta.length()
        direction = delta.normalize() if distance else pygame.Vector2(1, 0)
        self.facing = direction
        output = []
        if self.windup > 0:
            self.windup -= dt
            if self.windup <= 0:
                if self.is_boss:
                    self.attacking_time = 0.3
                    count = 12 if self.phase == 2 else 8
                    offset = self.pattern * 0.18
                    for i in range(count):
                        angle = offset + i * math.tau / count
                        output.append(Projectile(self.position, (math.cos(angle), math.sin(angle)),
                                                 self.damage, 155 if self.phase == 2 else 125,
                                                 friendly=False, lifetime=3))
                    self.pattern += 1
                    self.cooldown = 1.0 if self.phase == 2 else 1.6
                elif self.kind == 'golem':
                    if distance < 42:
                        player.take_damage(self.damage)
                    self.cooldown = 1.8
            return output
        if self.is_boss:
            if distance > 110:
                self.position += direction * self.speed * dt
            if self.cooldown == 0:
                self.windup = 0.7 if self.phase == 1 else 0.45
        elif self.kind in ('wizard', 'dragon'):
            if distance > 150:
                self.position += direction * self.speed * dt
            elif distance < 85:
                self.position -= direction * self.speed * dt
            if self.cooldown == 0:
                self.attacking_time = 0.3
                output.append(Projectile(self.position, direction, self.damage, 155, friendly=False, lifetime=3))
                self.cooldown = 1.7
        else:
            if distance > (32 if self.kind == 'golem' else 18):
                self.position += direction * self.speed * dt
            if distance < (38 if self.kind == 'golem' else 22) and self.cooldown == 0:
                if self.kind == 'golem':
                    self.windup = 0.7
                else:
                    self.attacking_time = 0.3
                    player.take_damage(self.damage)
                    self.cooldown = 0.8 if self.kind == 'ninja' else 1.0
        desired = self.position - previous_position
        if self.detour_time > 0 and desired.length_squared() > 0:
            desired = pygame.Vector2(-direction.y, direction.x) * self.detour_sign * self.speed * dt
        self.position = move_with_collisions(previous_position, (self.size, self.size), desired, bounds, obstacles)
        if desired.length_squared() > 0 and self.position.distance_to(previous_position) < min(0.2, desired.length() * 0.2):
            side = pygame.Vector2(-direction.y, direction.x) * self.detour_sign * self.speed * dt
            alternative = move_with_collisions(previous_position, (self.size, self.size), side, bounds, obstacles)
            if alternative.distance_to(previous_position) < 0.1:
                self.detour_sign *= -1
                alternative = move_with_collisions(previous_position, (self.size, self.size), -side, bounds, obstacles)
            self.position = alternative
            self.detour_time = 0.6
        self.moving = self.position != previous_position
        return output
