"""Enemies and the final guardian."""

import math

import pygame

from src.combat import Projectile


class Enemy:
    STATS = {'shadow': (30, 72, 10), 'cultist': (25, 48, 9), 'sentinel': (75, 32, 18),
             'boss': (300, 38, 15)}

    def __init__(self, kind, position):
        self.kind = kind
        self.max_hp, self.speed, self.damage = self.STATS[kind]
        self.hp = self.max_hp
        self.position = pygame.Vector2(position)
        self.size = 36 if kind == 'boss' else (24 if kind == 'sentinel' else 18)
        self.cooldown = 0.7
        self.windup = 0.0
        self.hit_flash = 0.0
        self.pattern = 0

    @property
    def alive(self):
        return self.hp > 0

    @property
    def phase(self):
        return 2 if self.kind == 'boss' and self.hp <= self.max_hp / 2 else 1

    @property
    def rect(self):
        return pygame.Rect(round(self.position.x - self.size / 2), round(self.position.y - self.size / 2),
                           self.size, self.size)

    def take_damage(self, damage):
        if self.alive:
            self.hp = max(0, self.hp - damage)
            self.hit_flash = 0.12

    def update(self, dt, player, bounds):
        if not self.alive:
            return []
        self.cooldown = max(0, self.cooldown - dt)
        self.hit_flash = max(0, self.hit_flash - dt)
        delta = player.position - self.position
        distance = delta.length()
        direction = delta.normalize() if distance else pygame.Vector2(1, 0)
        output = []
        if self.windup > 0:
            self.windup -= dt
            if self.windup <= 0:
                if self.kind == 'boss':
                    count = 12 if self.phase == 2 else 8
                    offset = self.pattern * 0.18
                    for i in range(count):
                        angle = offset + i * math.tau / count
                        output.append(Projectile(self.position, (math.cos(angle), math.sin(angle)),
                                                 self.damage, 155 if self.phase == 2 else 125,
                                                 friendly=False, lifetime=3))
                    self.pattern += 1
                    self.cooldown = 1.0 if self.phase == 2 else 1.6
                elif self.kind == 'sentinel':
                    if distance < 42:
                        player.take_damage(self.damage)
                    self.cooldown = 1.8
            return output
        if self.kind == 'boss':
            if distance > 110:
                self.position += direction * self.speed * dt
            if self.cooldown == 0:
                self.windup = 0.7 if self.phase == 1 else 0.45
        elif self.kind == 'cultist':
            if distance > 150:
                self.position += direction * self.speed * dt
            elif distance < 85:
                self.position -= direction * self.speed * dt
            if self.cooldown == 0:
                output.append(Projectile(self.position, direction, self.damage, 155, friendly=False, lifetime=3))
                self.cooldown = 1.7
        else:
            if distance > (32 if self.kind == 'sentinel' else 18):
                self.position += direction * self.speed * dt
            if distance < (38 if self.kind == 'sentinel' else 22) and self.cooldown == 0:
                if self.kind == 'sentinel':
                    self.windup = 0.7
                else:
                    player.take_damage(self.damage)
                    self.cooldown = 1.0
        half = self.size / 2
        self.position.x = max(bounds.left + half, min(bounds.right - half, self.position.x))
        self.position.y = max(bounds.top + half, min(bounds.bottom - half, self.position.y))
        return output
