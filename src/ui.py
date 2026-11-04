"""Pixel-art panels, HUD and short progression animations."""

import math

import pygame

from src import settings
from src.assets import resource_path


INK = (17, 20, 36)
PANEL = (35, 37, 57)
PANEL_LIGHT = (51, 51, 72)
EDGE = (112, 104, 131)
GOLD = (224, 182, 112)
CYAN = (121, 222, 225)
WHITE = (240, 233, 220)
MUTED = (167, 166, 183)


class Menu:
    def __init__(self):
        self.selected = 0
        self.buttons = [('Jogar', pygame.Rect(225, 156, 190, 34)),
                        ('Controles', pygame.Rect(225, 199, 190, 34)),
                        ('Sair', pygame.Rect(225, 242, 190, 34))]
        path = resource_path('assets', 'fonts', 'PixelifySans.ttf')
        try:
            self.title_font = pygame.font.Font(str(path), 38)
            self.heading_font = pygame.font.Font(str(path), 25)
            self.font = pygame.font.Font(str(path), 20)
            self.small_font = pygame.font.Font(str(path), 15)
        except (OSError, pygame.error):
            self.title_font = pygame.font.Font(None, 48)
            self.heading_font = pygame.font.Font(None, 30)
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 19)
        self.upgrade_rects = [pygame.Rect(60 + i * 180, 132, 160, 105) for i in range(3)]
        self.pause_rects = [pygame.Rect(225, 125 + i * 42, 190, 34) for i in range(3)]
        self.end_rects = [pygame.Rect(205, 220, 110, 34), pygame.Rect(325, 220, 110, 34)]

    def draw_text(self, surface, text, center, font, color):
        rendered = font.render(text, False, color)
        shadow = font.render(text, False, (9, 10, 18))
        rect = rendered.get_rect(center=center)
        surface.blit(shadow, rect.move(1, 1))
        surface.blit(rendered, rect)

    def panel(self, surface, rect, active=False):
        rect = pygame.Rect(rect)
        pygame.draw.rect(surface, (9, 10, 20), rect.move(2, 3))
        pygame.draw.rect(surface, PANEL_LIGHT if active else PANEL, rect)
        pygame.draw.rect(surface, GOLD if active else EDGE, rect, 2)
        pygame.draw.rect(surface, (76, 70, 90), rect.inflate(-6, -6), 1)
        for x in (rect.left + 3, rect.right - 4):
            for y in (rect.top + 3, rect.bottom - 4):
                surface.set_at((x, y), GOLD if active else CYAN)

    def _backdrop(self, surface):
        surface.fill(INK)
        ticks = pygame.time.get_ticks() / 1000
        for index in range(48):
            x = (index * 137 + 23) % 640
            y = (index * 83 + int(ticks * (3 + index % 3))) % 360
            color = (48 + index % 3 * 8, 54 + index % 4 * 5, 77 + index % 5 * 5)
            pygame.draw.rect(surface, color, (x, y, 2, 2))
        pygame.draw.circle(surface, (35, 44, 61), (320, 164), 115, 1)
        pygame.draw.circle(surface, (39, 48, 65), (320, 164), 126, 1)

    def _overlay(self, surface, opacity=215):
        shade = pygame.Surface(settings.LOGICAL_SIZE, pygame.SRCALPHA)
        shade.fill((8, 9, 21, max(0, min(255, int(opacity)))))
        surface.blit(shade, (0, 0))

    def draw(self, surface):
        self._backdrop(surface)
        self.panel(surface, (105, 20, 430, 320))
        pygame.draw.line(surface, GOLD, (245, 117), (395, 117), 1)
        self.draw_text(surface, 'ARCANE TRIALS', (320, 63), self.title_font, WHITE)
        self.draw_text(surface, 'AS PROVAÇÕES ARCANAS', (320, 102), self.small_font, CYAN)
        pygame.draw.polygon(surface, GOLD, [(320, 120), (324, 124), (320, 128), (316, 124)])
        for index, (label, rect) in enumerate(self.buttons):
            self.panel(surface, rect, index == self.selected)
            self.draw_text(surface, label.upper(), rect.center, self.font, WHITE)
        self.draw_text(surface, 'SETAS + ENTER  /  MOUSE', (320, 315), self.small_font, MUTED)

    def draw_controls(self, surface):
        self._backdrop(surface)
        self.panel(surface, (70, 26, 500, 308))
        self.draw_text(surface, 'CONTROLES', (320, 65), self.title_font, WHITE)
        lines = ['WASD: mover   |   Mouse: mirar',
                 'Clique esquerdo: ataque   |   Direito: Lança de Raio',
                 'Q: Explosão Arcana   |   Espaço: esquiva',
                 'E: avançar de sala   |   Esc: pausar']
        for index, line in enumerate(lines):
            self.draw_text(surface, line, (320, 125 + index * 32), self.font, WHITE)
        self.draw_text(surface, 'ESC OU ENTER PARA VOLTAR', (320, 305), self.small_font, CYAN)

    def draw_hud(self, surface, player, world):
        self.panel(surface, (8, 7, 134, 34))
        pygame.draw.rect(surface, (68, 29, 43), (14, 12, 122, 10))
        pygame.draw.rect(surface, (213, 78, 96), (14, 12, round(122 * player.hp / player.max_hp), 10))
        self.draw_text(surface, f'PV {int(player.hp)}/{player.max_hp}', (75, 30), self.small_font, WHITE)
        self.draw_text(surface, world.ROOM_NAMES[world.room_index].upper(), (320, 19), self.small_font, WHITE)
        if world.room_index < 3 and world.complete and world.chosen_upgrade:
            self.panel(surface, (493, 8, 139, 28), True)
            self.draw_text(surface, 'E  •  AVANÇAR', (562, 22), self.small_font, WHITE)
        if world.room_index == 0:
            self.draw_text(surface, 'WASD MOVER   •   MOUSE ATACAR   •   Q EXPLOSÃO   •   ESPAÇO ESQUIVA',
                           (320, 318), self.small_font, WHITE)
        for index, (key, label) in enumerate((('spear', 'RAIO'), ('explosion', 'Q'), ('dash', 'ESPAÇO'))):
            rect = pygame.Rect(166 + index * 105, 328, 98, 25)
            self.panel(surface, rect, player.cooldowns[key] <= 0)
            remaining = player.cooldowns[key]
            self.draw_text(surface, f'{label}  {remaining:.1f}s' if remaining > 0 else f'{label}  OK',
                           rect.center, self.small_font, WHITE if remaining <= 0 else MUTED)
        if world.room_index == 3 and world.enemies and world.enemies[0].alive:
            boss = world.enemies[0]
            pygame.draw.rect(surface, INK, (197, 42, 246, 12))
            pygame.draw.rect(surface, (100, 49, 67), (200, 45, 240, 6))
            pygame.draw.rect(surface, (221, 87, 112), (200, 45, round(240 * boss.hp / boss.max_hp), 6))
            self.draw_text(surface, 'GUARDIÃO DO NÚCLEO', (320, 62), self.small_font, WHITE)

    def draw_pause(self, surface, selected):
        self._overlay(surface)
        self.panel(surface, (180, 40, 280, 245))
        self.draw_text(surface, 'PAUSADO', (320, 78), self.title_font, WHITE)
        for index, (label, rect) in enumerate(zip(('CONTINUAR', 'REINICIAR', 'MENU PRINCIPAL'), self.pause_rects)):
            self.panel(surface, rect, index == selected)
            self.draw_text(surface, label, rect.center, self.font, WHITE)

    def draw_upgrades(self, surface):
        self._overlay(surface)
        self.draw_text(surface, 'ESCOLHA SUA MELHORIA', (320, 64), self.heading_font, WHITE)
        self.draw_text(surface, 'UM PODER PARA ESTA JORNADA', (320, 91), self.small_font, CYAN)
        options = [('1  PODER ARCANO', '+20% dano mágico', (207, 129, 238)),
                   ('2  ESSÊNCIA VITAL', 'Recupera 30 PV', (239, 114, 132)),
                   ('3  FLUXO MÍSTICO', '-20% nas especiais', CYAN)]
        for rect, (title, description, color) in zip(self.upgrade_rects, options):
            self.panel(surface, rect)
            pygame.draw.polygon(surface, color, [(rect.centerx, rect.y + 12), (rect.centerx + 9, rect.y + 24),
                                                 (rect.centerx, rect.y + 36), (rect.centerx - 9, rect.y + 24)])
            self.draw_text(surface, title, (rect.centerx, rect.y + 55), self.small_font, WHITE)
            self.draw_text(surface, description, (rect.centerx, rect.y + 78), self.small_font, MUTED)
        self.draw_text(surface, 'CLIQUE OU PRESSIONE 1, 2 OU 3', (320, 286), self.small_font, GOLD)

    def draw_level_up(self, surface, label, progress):
        progress = max(0.0, min(1.0, progress))
        self._overlay(surface, 165)
        radius = 32 + int(38 * progress)
        pygame.draw.circle(surface, CYAN, (320, 171), radius, 2)
        for i in range(8):
            angle = i * math.tau / 8 + progress
            pos = (320 + math.cos(angle) * radius, 171 + math.sin(angle) * radius)
            pygame.draw.circle(surface, GOLD, pos, 2)
        self.panel(surface, (159, 112, 322, 116), True)
        self.draw_text(surface, 'PODER APRIMORADO', (320, 146), self.heading_font, WHITE)
        self.draw_text(surface, label, (320, 179), self.font, CYAN)
        self.draw_text(surface, 'ATIVO NESTA JORNADA', (320, 204), self.small_font, MUTED)
        pygame.draw.rect(surface, INK, (207, 215, 226, 5))
        pygame.draw.rect(surface, CYAN, (209, 216, round(222 * progress), 3))

    def draw_transition(self, surface, room_name, progress):
        progress = max(0.0, min(1.0, progress))
        self._overlay(surface, 175 + 45 * math.sin(progress * math.pi))
        self.panel(surface, (125, 112, 390, 130), True)
        self.draw_text(surface, 'INDO PARA O PRÓXIMO NÍVEL', (320, 146), self.heading_font, WHITE)
        self.draw_text(surface, room_name.upper(), (320, 180), self.font, CYAN)
        pygame.draw.rect(surface, INK, (203, 210, 234, 8))
        pygame.draw.rect(surface, GOLD, (205, 212, round(230 * progress), 4))

    def draw_end(self, surface, victory):
        self._overlay(surface)
        self.panel(surface, (130, 40, 380, 260), True)
        self.draw_text(surface, 'VITÓRIA' if victory else 'DERROTA', (320, 90), self.title_font, CYAN if victory else (232, 111, 122))
        text = 'O cristal corrompido foi purificado!' if victory else 'O santuário venceu esta tentativa.'
        self.draw_text(surface, text, (320, 149), self.font, WHITE)
        for rect, label in zip(self.end_rects, ('REINICIAR', 'MENU')):
            self.panel(surface, rect)
            self.draw_text(surface, label, rect.center, self.font, WHITE)
        self.draw_text(surface, 'ENTER: REINICIAR   |   ESC: MENU', (320, 281), self.small_font, MUTED)
