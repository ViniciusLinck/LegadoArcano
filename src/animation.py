"""Time-based sprite frame selection for the four-directional mage."""

import pygame


def mage_frame(direction, moving, elapsed):
    return character_frame(direction, moving, elapsed)


def character_frame(direction, moving, elapsed, attacking=False):
    """Ninja Adventure sheets: direction in columns, animation in rows."""
    x, y = direction
    if abs(x) > abs(y):
        column = 3 if x > 0 else 2
    else:
        column = 1 if y < 0 else 0
    row = 4 if attacking else (int(max(0, elapsed) * 8) % 4 if moving else 0)
    return pygame.Rect(column * 16, row * 16, 16, 16)


def creature_frame(kind, direction, elapsed, attacking=False):
    if kind == 'goblin':
        frame = int(max(0, elapsed) * 7) % 8
        return pygame.Rect((frame % 3) * 54, (frame // 3) * 54, 54, 54)
    if kind == 'golem':
        return pygame.Rect((int(max(0, elapsed) * 8) % 8) * 32, 0, 32, 32)
    return character_frame(direction, True, elapsed, attacking and kind != 'dragon')
