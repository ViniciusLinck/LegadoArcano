"""Licensed animated spell sheets and frame timing."""

import pygame

from src.assets import resource_path


EFFECT_DURATIONS = {'cast': 0.3, 'impact': 0.3, 'explosion': 0.6,
                    'dash': 0.3, 'death': 0.4, 'hazard': 0.3}

SHEETS = {'orb': ('energia.png', 16, 16, 4),
          'lightning': ('raio.png', 20, 28, 8),
          'burst': ('gelo.png', 32, 32, 10),
          'ring': ('circulo.png', 32, 32, 6),
          'impact': ('impacto.png', 30, 35, 9),
          'smoke': ('fumaca.png', 30, 14, 8)}


def frame_index(elapsed, duration, count, loop=False):
    if duration <= 0 or count <= 1:
        return 0
    elapsed = max(0.0, elapsed)
    if loop:
        elapsed %= duration
    return min(count - 1, int(elapsed / duration * count))


class EffectLibrary:
    def __init__(self):
        self.sheets = {}
        for name, (filename, width, height, count) in SHEETS.items():
            try:
                image = pygame.image.load(str(resource_path('assets', 'effects', filename))).convert_alpha()
                if image.get_width() >= width * count and image.get_height() >= height:
                    self.sheets[name] = image
            except (FileNotFoundError, OSError, pygame.error):
                pass

    def frame(self, name, elapsed, duration, loop=False):
        sheet = self.sheets.get(name)
        if sheet is None:
            return None
        _, width, height, count = SHEETS[name]
        index = frame_index(elapsed, duration, count, loop)
        return sheet.subsurface((index * width, 0, width, height))
