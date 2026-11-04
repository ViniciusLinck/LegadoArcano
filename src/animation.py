"""Time-based sprite frame selection for the four-directional mage."""

import pygame


def mage_frame(direction, moving, elapsed):
    x, y = direction
    if abs(x) > abs(y):
        column, row = (0 if x > 0 else 4), 1
    else:
        column, row = (4 if y < 0 else 0), 0
    frame = int(max(0, elapsed) * 8) % 4 if moving else 0
    return pygame.Rect((column + frame) * 16, row * 16, 16, 16)
