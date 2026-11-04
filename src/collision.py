"""Axis-separated movement against the arena and solid map props."""

import math

import pygame


def move_with_collisions(position, size, delta, bounds, obstacles=()):
    position = pygame.Vector2(position)
    delta = pygame.Vector2(delta)
    half_x, half_y = size[0] / 2, size[1] / 2
    steps = max(1, math.ceil(max(abs(delta.x), abs(delta.y)) / 4)) if obstacles else 1
    increment = delta / steps
    for _ in range(steps):
        position.x = max(bounds.left + half_x, min(bounds.right - half_x, position.x + increment.x))
        for item in obstacles:
            rect = pygame.Rect(item)
            if (position.x + half_x > rect.left and position.x - half_x < rect.right and
                    position.y + half_y > rect.top and position.y - half_y < rect.bottom):
                if increment.x > 0:
                    position.x = rect.left - half_x
                elif increment.x < 0:
                    position.x = rect.right + half_x
        position.y = max(bounds.top + half_y, min(bounds.bottom - half_y, position.y + increment.y))
        for item in obstacles:
            rect = pygame.Rect(item)
            if (position.x + half_x > rect.left and position.x - half_x < rect.right and
                    position.y + half_y > rect.top and position.y - half_y < rect.bottom):
                if increment.y > 0:
                    position.y = rect.top - half_y
                elif increment.y < 0:
                    position.y = rect.bottom + half_y
    return position
