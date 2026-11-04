"""Player movement in logical screen coordinates."""

import pygame

from src.settings import PLAYER_SIZE, PLAYER_SPEED


class Player:
    def __init__(self, position: tuple[float, float]):
        self.position = pygame.Vector2(position)
        self.rect = pygame.Rect(0, 0, *PLAYER_SIZE)
        self.rect.center = self.position

    def update(self, direction: tuple[float, float], dt: float, bounds: pygame.Rect) -> None:
        movement = pygame.Vector2(direction)
        if movement.length_squared() > 0:
            movement = movement.normalize()
        self.position += movement * PLAYER_SPEED * max(0.0, dt)
        half_width, half_height = self.rect.width / 2, self.rect.height / 2
        self.position.x = max(bounds.left + half_width, min(bounds.right - half_width, self.position.x))
        self.position.y = max(bounds.top + half_height, min(bounds.bottom - half_height, self.position.y))
        self.rect.center = self.position
