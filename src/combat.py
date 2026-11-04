"""Reusable projectile mechanics."""

import pygame


class Projectile:
    def __init__(self, position, direction, damage, speed, max_hits=1, friendly=True, lifetime=1.7):
        self.position = pygame.Vector2(position)
        vector = pygame.Vector2(direction)
        self.direction = vector.normalize() if vector.length_squared() else pygame.Vector2(1, 0)
        self.damage = damage
        self.speed = speed
        self.max_hits = max_hits
        self.friendly = friendly
        self.lifetime = lifetime
        self.age = 0.0
        self.alive = True
        self.hit_targets = set()
        self.radius = 5 if friendly else 6
        self.blocked = False

    @property
    def rect(self):
        return pygame.Rect(round(self.position.x - self.radius), round(self.position.y - self.radius),
                           self.radius * 2, self.radius * 2)

    def register_hit(self, target):
        if not self.alive or target in self.hit_targets:
            return False
        self.hit_targets.add(target)
        if len(self.hit_targets) >= self.max_hits:
            self.alive = False
        return True

    def update(self, dt, bounds, obstacles=()):
        previous = self.position.copy()
        self.position += self.direction * self.speed * dt
        self.age += dt
        self.lifetime -= dt
        intersections = [pygame.Rect(item).inflate(self.radius * 2, self.radius * 2).clipline(previous, self.position)
                         for item in obstacles]
        intersections = [segment for segment in intersections if segment]
        if intersections:
            closest = min((pygame.Vector2(segment[0]) for segment in intersections),
                          key=lambda point: point.distance_squared_to(previous))
            self.position = closest
            self.blocked = True
        if self.lifetime <= 0 or self.blocked or not bounds.collidepoint(self.position):
            self.alive = False
