"""Window, event handling, game states and the frame loop."""

from enum import Enum, auto
from pathlib import Path

import pygame

from src import settings
from src.player import Player
from src.ui import Menu


class GameState(Enum):
    MENU = auto()
    CONTROLS = auto()
    PLAYING = auto()


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(settings.WINDOW_SIZE)
        pygame.display.set_caption('Arcane Trials — As Provações Arcanas')
        self.canvas = pygame.Surface(settings.LOGICAL_SIZE)
        self.clock = pygame.time.Clock()
        self.menu = Menu()
        self.state = GameState.MENU
        self.running = True
        self.bounds = pygame.Rect(settings.ARENA_RECT)
        self.player = Player(self.bounds.center)
        self.tiles = self._load_tiles()

    def _load_tiles(self):
        path = Path(__file__).resolve().parent.parent / 'assets' / 'sprites' / 'tiny_dungeon.png'
        try:
            return pygame.image.load(str(path)).convert_alpha()
        except (FileNotFoundError, pygame.error, OSError):
            return None

    def _choose_menu(self, index):
        if index == 0:
            self.player = Player(self.bounds.center)
            self.state = GameState.PLAYING
        elif index == 1:
            self.state = GameState.CONTROLS
        elif index == 2:
            self.running = False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu.selected = (self.menu.selected + 1) % len(self.menu.buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.menu.selected = (self.menu.selected - 1) % len(self.menu.buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._choose_menu(self.menu.selected)
            elif event.key == pygame.K_ESCAPE or (self.state == GameState.CONTROLS and event.key == pygame.K_RETURN):
                self.state = GameState.MENU
                self.menu.selected = 0
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == GameState.MENU:
            x = event.pos[0] * settings.LOGICAL_SIZE[0] / self.window.get_width()
            y = event.pos[1] * settings.LOGICAL_SIZE[1] / self.window.get_height()
            for index, (_, rect) in enumerate(self.menu.buttons):
                if rect.collidepoint(x, y):
                    self._choose_menu(index)
                    break

    def update(self, dt):
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            direction = (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                         int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
            self.player.update(direction, dt, self.bounds)

    def _draw_arena(self):
        self.canvas.fill(settings.BACKGROUND)
        pygame.draw.rect(self.canvas, (39, 40, 53), self.bounds)
        if self.tiles:
            floor = self.tiles.subsurface((144, 64, 16, 16))
            self.canvas.set_clip(self.bounds)
            for y in range(self.bounds.top, self.bounds.bottom, 16):
                for x in range(self.bounds.left, self.bounds.right, 16):
                    self.canvas.blit(floor, (x, y))
            self.canvas.set_clip(None)
            sprite = self.tiles.subsurface((0, 112, 16, 16))
            self.canvas.blit(pygame.transform.scale(sprite, self.player.rect.size), self.player.rect)
        else:
            pygame.draw.rect(self.canvas, settings.ACCENT, self.player.rect, border_radius=3)
        pygame.draw.rect(self.canvas, (122, 101, 148), self.bounds, 3)
        self.menu.draw_text(self.canvas, 'CÂMARA INICIAL', (320, 20), self.menu.small_font, settings.TEXT)
        self.menu.draw_text(self.canvas, 'WASD: mover   |   Esc: menu', (320, 336), self.menu.small_font, settings.MUTED)

    def draw(self):
        if self.state == GameState.MENU:
            self.menu.draw(self.canvas)
        elif self.state == GameState.CONTROLS:
            self.menu.draw_controls(self.canvas)
        else:
            self._draw_arena()
        pygame.transform.scale(self.canvas, self.window.get_size(), self.window)
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(settings.FPS) / 1000.0, settings.MAX_FRAME_TIME)
                for event in pygame.event.get():
                    self.handle_event(event)
                if self.running:
                    self.update(dt)
                    self.draw()
        finally:
            pygame.quit()
