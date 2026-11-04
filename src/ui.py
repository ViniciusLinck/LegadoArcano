"""Menu layout and presentation."""

import pygame

from src import settings


class Menu:
    def __init__(self):
        self.selected = 0
        self.buttons = [
            ('Jogar', pygame.Rect(225, 156, 190, 34)),
            ('Controles', pygame.Rect(225, 199, 190, 34)),
            ('Sair', pygame.Rect(225, 242, 190, 34)),
        ]
        self.title_font = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 19)

    def draw_text(self, surface, text, center, font, color):
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=center))

    def draw(self, surface):
        surface.fill(settings.BACKGROUND)
        pygame.draw.rect(surface, (45, 43, 67), (115, 24, 410, 304), 1, border_radius=8)
        self.draw_text(surface, 'ARCANE TRIALS', (320, 72), self.title_font, settings.TEXT)
        self.draw_text(surface, 'AS PROVAÇÕES ARCANAS', (320, 101), self.small_font, settings.ACCENT)
        for index, (label, rect) in enumerate(self.buttons):
            selected = index == self.selected
            pygame.draw.rect(surface, settings.PANEL, rect, border_radius=4)
            pygame.draw.rect(surface, settings.ACCENT if selected else (73, 71, 92), rect, 1, border_radius=4)
            self.draw_text(surface, label, rect.center, self.font, settings.TEXT)
        self.draw_text(surface, 'Setas + Enter ou mouse para escolher', (320, 309), self.small_font, settings.MUTED)

    def draw_controls(self, surface):
        surface.fill(settings.BACKGROUND)
        self.draw_text(surface, 'CONTROLES', (320, 65), self.title_font, settings.TEXT)
        lines = [
            'W A S D  —  movimentar',
            'Esc  —  voltar ao menu',
            'Mouse ou setas + Enter  —  navegar no menu',
            'Combate e esquiva serão adicionados nas próximas fases.',
        ]
        for index, line in enumerate(lines):
            self.draw_text(surface, line, (320, 130 + index * 34), self.font if index < 3 else self.small_font, settings.TEXT)
        self.draw_text(surface, 'Esc ou Enter para voltar', (320, 305), self.small_font, settings.ACCENT)
