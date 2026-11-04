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
        self.upgrade_rects = [pygame.Rect(60 + i * 180, 132, 160, 105) for i in range(3)]
        self.pause_rects = [pygame.Rect(225, 125 + i * 42, 190, 34) for i in range(3)]
        self.end_rects = [pygame.Rect(205, 220, 110, 34), pygame.Rect(325, 220, 110, 34)]

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
            'WASD: mover    |    Mouse: mirar',
            'Botão esquerdo: ataque    |    Direito: Lança de Raio',
            'Q: Explosão Arcana    |    Espaço: esquiva',
            'E: avançar de sala    |    Esc: pausar',
        ]
        for index, line in enumerate(lines):
            self.draw_text(surface, line, (320, 125 + index * 32), self.font, settings.TEXT)
        self.draw_text(surface, 'Esc ou Enter para voltar', (320, 305), self.small_font, settings.ACCENT)

    def _overlay(self, surface):
        shade = pygame.Surface(settings.LOGICAL_SIZE, pygame.SRCALPHA)
        shade.fill((8, 8, 20, 215))
        surface.blit(shade, (0, 0))

    def draw_hud(self, surface, player, world):
        pygame.draw.rect(surface, (65, 29, 43), (12, 10, 120, 12), border_radius=3)
        pygame.draw.rect(surface, (214, 73, 102), (12, 10, round(120 * player.hp / player.max_hp), 12), border_radius=3)
        self.draw_text(surface, f'PV {int(player.hp)}/{player.max_hp}', (72, 29), self.small_font, settings.TEXT)
        self.draw_text(surface, world.ROOM_NAMES[world.room_index].upper(), (320, 19), self.small_font, settings.TEXT)
        parts = []
        for key, label in (('spear', 'RAIO'), ('explosion', 'Q'), ('dash', 'ESPAÇO')):
            remaining = player.cooldowns[key]
            parts.append(f'{label}: {remaining:.1f}s' if remaining > 0 else f'{label}: PRONTO')
        self.draw_text(surface, '   |   '.join(parts), (320, 337), self.small_font, settings.TEXT)
        if world.room_index < 3 and world.complete and world.chosen_upgrade:
            self.draw_text(surface, 'E — AVANÇAR', (320, 300), self.small_font, settings.ACCENT)
        if world.room_index == 0:
            self.draw_text(surface, 'WASD: mover  |  Mouse: atacar  |  Q: explosão  |  Espaço: esquiva',
                           (320, 319), self.small_font, settings.TEXT)
        if world.room_index == 3 and world.enemies and world.enemies[0].alive:
            boss = world.enemies[0]
            pygame.draw.rect(surface, (55, 23, 37), (200, 43, 240, 7))
            pygame.draw.rect(surface, (220, 74, 110), (200, 43, round(240 * boss.hp / boss.max_hp), 7))
            self.draw_text(surface, 'GUARDIÃO DO NÚCLEO', (320, 60), self.small_font, settings.TEXT)

    def draw_pause(self, surface, selected):
        self._overlay(surface)
        self.draw_text(surface, 'PAUSADO', (320, 70), self.title_font, settings.TEXT)
        for index, (label, rect) in enumerate(zip(('Continuar', 'Reiniciar', 'Menu principal'), self.pause_rects)):
            pygame.draw.rect(surface, settings.PANEL, rect, border_radius=4)
            pygame.draw.rect(surface, settings.ACCENT if index == selected else (73, 71, 92), rect, 1, border_radius=4)
            self.draw_text(surface, label, rect.center, self.font, settings.TEXT)

    def draw_upgrades(self, surface):
        self._overlay(surface)
        self.draw_text(surface, 'ESCOLHA UMA MELHORIA', (320, 68), self.title_font, settings.TEXT)
        options = [('1  PODER ARCANO', '+20% dano mágico'), ('2  ESSÊNCIA VITAL', 'Recupera 30 PV'),
                   ('3  FLUXO MÍSTICO', '-20% recarga especial')]
        for rect, (title, description) in zip(self.upgrade_rects, options):
            pygame.draw.rect(surface, settings.PANEL, rect, border_radius=4)
            pygame.draw.rect(surface, settings.ACCENT, rect, 1, border_radius=4)
            self.draw_text(surface, title, (rect.centerx, rect.y + 33), self.small_font, settings.ACCENT)
            self.draw_text(surface, description, (rect.centerx, rect.y + 65), self.small_font, settings.TEXT)
        self.draw_text(surface, 'Clique ou pressione 1, 2 ou 3', (320, 287), self.small_font, settings.MUTED)

    def draw_end(self, surface, victory):
        self._overlay(surface)
        self.draw_text(surface, 'VITÓRIA' if victory else 'DERROTA', (320, 85), self.title_font, settings.ACCENT if victory else (225, 90, 110))
        text = 'O cristal corrompido foi purificado!' if victory else 'O santuário venceu esta tentativa.'
        self.draw_text(surface, text, (320, 145), self.font, settings.TEXT)
        for rect, label in zip(self.end_rects, ('Reiniciar', 'Menu')):
            pygame.draw.rect(surface, settings.PANEL, rect, border_radius=4)
            pygame.draw.rect(surface, settings.ACCENT, rect, 1, border_radius=4)
            self.draw_text(surface, label, rect.center, self.font, settings.TEXT)
        self.draw_text(surface, 'Enter: reiniciar  |  Esc: menu', (320, 285), self.small_font, settings.MUTED)
