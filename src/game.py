"""Window, input, game states and rendering for Arcane Trials."""

from enum import Enum, auto

import pygame

from src import settings
from src.assets import Sounds, resource_path
from src.player import Player
from src.ui import Menu
from src.world import World


class GameState(Enum):
    MENU = auto()
    CONTROLS = auto()
    PLAYING = auto()
    PAUSED = auto()
    UPGRADE = auto()
    VICTORY = auto()
    DEFEAT = auto()


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(settings.WINDOW_SIZE)
        pygame.display.set_caption('Arcane Trials — As Provações Arcanas')
        self.canvas = pygame.Surface(settings.LOGICAL_SIZE)
        self.clock = pygame.time.Clock()
        self.menu = Menu()
        self.sounds = Sounds()
        self.state = GameState.MENU
        self.running = True
        self.bounds = pygame.Rect(settings.ARENA_RECT)
        self.player = Player(self.bounds.center)
        self.world = World(self.player, self.bounds)
        self.tiles = self._load_tiles()
        self.pause_selected = 0
        self.boss_defeat_time = 0.0

    def _load_tiles(self):
        try:
            return pygame.image.load(str(resource_path('assets', 'sprites', 'tiny_dungeon.png'))).convert_alpha()
        except (FileNotFoundError, pygame.error, OSError):
            return None

    def _new_run(self):
        self.player = Player(self.bounds.center)
        self.world = World(self.player, self.bounds)
        self.boss_defeat_time = 0.0
        self.state = GameState.PLAYING

    def _choose_menu(self, index):
        self.sounds.play('confirm')
        if index == 0:
            self._new_run()
        elif index == 1:
            self.state = GameState.CONTROLS
        elif index == 2:
            self.running = False

    def _logical_pos(self, pos):
        return (pos[0] * settings.LOGICAL_SIZE[0] / self.window.get_width(),
                pos[1] * settings.LOGICAL_SIZE[1] / self.window.get_height())

    def _pause_choice(self, choice):
        if choice == 0:
            self.state = GameState.PLAYING
        elif choice == 1:
            self._new_run()
        else:
            self.menu.selected = 0
            self.state = GameState.MENU

    def _advance(self):
        if self.world.complete and self.world.chosen_upgrade and self.world.room_index < 3:
            self.world.load_room(self.world.room_index + 1)
            self.sounds.play('confirm')

    def _upgrade(self, index):
        self.world.apply_upgrade(('power', 'vital', 'flow')[index])
        self.state = GameState.PLAYING
        self.sounds.play('confirm')

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
            elif self.state == GameState.CONTROLS:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.state = GameState.MENU
                    self.menu.selected = 0
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.pause_selected = 0
                    self.state = GameState.PAUSED
                elif event.key == pygame.K_e:
                    self._advance()
                elif event.key == pygame.K_q and self.world.explode():
                    self.sounds.play('impact')
                elif event.key == pygame.K_SPACE:
                    keys = pygame.key.get_pressed()
                    direction = (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                                 int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
                    self.player.dash(direction)
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pause_selected = (self.pause_selected + 1) % 3
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pause_selected = (self.pause_selected - 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._pause_choice(self.pause_selected)
            elif self.state == GameState.UPGRADE:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self._upgrade(event.key - pygame.K_1)
            elif self.state in (GameState.VICTORY, GameState.DEFEAT):
                if event.key in (pygame.K_RETURN, pygame.K_r):
                    self._new_run()
                elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                    self.menu.selected = 0
                    self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = self._logical_pos(event.pos)
            if self.state == GameState.MENU and event.button == 1:
                for index, (_, rect) in enumerate(self.menu.buttons):
                    if rect.collidepoint(pos):
                        self._choose_menu(index)
                        break
            elif self.state == GameState.PLAYING:
                if event.button == 1 and self.world.fire(pos, 'basic'):
                    self.sounds.play('cast')
                elif event.button == 3 and self.world.fire(pos, 'spear'):
                    self.sounds.play('cast')
            elif self.state == GameState.UPGRADE and event.button == 1:
                for index, rect in enumerate(self.menu.upgrade_rects):
                    if rect.collidepoint(pos):
                        self._upgrade(index)
                        break
            elif self.state == GameState.PAUSED and event.button == 1:
                for index, rect in enumerate(self.menu.pause_rects):
                    if rect.collidepoint(pos):
                        self._pause_choice(index)
                        break
            elif self.state in (GameState.VICTORY, GameState.DEFEAT) and event.button == 1:
                for index, rect in enumerate(self.menu.end_rects):
                    if rect.collidepoint(pos):
                        if index == 0:
                            self._new_run()
                        else:
                            self.menu.selected = 0
                            self.state = GameState.MENU
                        break

    def update(self, dt):
        if self.state != GameState.PLAYING:
            return
        keys = pygame.key.get_pressed()
        direction = (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                     int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
        self.player.update(direction, dt, self.bounds)
        if self.player.dash_time > 0 and len(self.world.effects) < 20:
            self.world.effects.append([self.player.position.copy(), 0.16, 'dash'])
        if pygame.mouse.get_pressed()[0]:
            if self.world.fire(self._logical_pos(pygame.mouse.get_pos()), 'basic'):
                self.sounds.play('cast')
        self.world.update(dt)
        if self.player.hp <= 0:
            self.state = GameState.DEFEAT
        elif self.world.complete and self.world.room_index in (1, 2) and not self.world.chosen_upgrade:
            self.state = GameState.UPGRADE
        elif self.world.complete and self.world.room_index == 3:
            self.boss_defeat_time += dt
            if self.boss_defeat_time >= 1:
                self.state = GameState.VICTORY

    def _draw_arena(self):
        self.canvas.fill(settings.BACKGROUND)
        pygame.draw.rect(self.canvas, (39, 40, 53), self.bounds)
        if self.tiles:
            floor = self.tiles.subsurface((64, 48, 16, 16))
            self.canvas.set_clip(self.bounds)
            for y in range(self.bounds.top, self.bounds.bottom, 16):
                for x in range(self.bounds.left, self.bounds.right, 16):
                    self.canvas.blit(floor, (x, y))
            self.canvas.set_clip(None)
        pygame.draw.rect(self.canvas, (122, 101, 148), self.bounds, 3)
        for pos, timer in self.world.hazards:
            pygame.draw.circle(self.canvas, (210, 70, 80), pos, 32, 2)
            pygame.draw.circle(self.canvas, (235, 120, 90), pos, max(2, int(32 * (1 - min(timer, 1)))), 1)
        for enemy in self.world.enemies:
            if not enemy.alive:
                continue
            if enemy.windup > 0:
                pygame.draw.circle(self.canvas, (235, 90, 60), enemy.position, 42 if enemy.kind == 'sentinel' else 28, 2)
            colors = {'shadow': (139, 80, 166), 'cultist': (227, 141, 65), 'sentinel': (145, 150, 163), 'boss': (211, 71, 116)}
            if self.tiles and enemy.hit_flash <= 0:
                coords = {'shadow': (0, 144), 'cultist': (64, 144), 'sentinel': (0, 160), 'boss': (16, 160)}
                sprite = self.tiles.subsurface((*coords[enemy.kind], 16, 16))
                self.canvas.blit(pygame.transform.scale(sprite, enemy.rect.size), enemy.rect)
            else:
                pygame.draw.ellipse(self.canvas, (255, 255, 255) if enemy.hit_flash else colors[enemy.kind], enemy.rect)
            if enemy.kind != 'boss':
                pygame.draw.rect(self.canvas, (30, 20, 30), (enemy.rect.left, enemy.rect.top - 5, enemy.size, 3))
                pygame.draw.rect(self.canvas, (220, 80, 95), (enemy.rect.left, enemy.rect.top - 5, int(enemy.size * enemy.hp / enemy.max_hp), 3))
        for shot in self.world.projectiles:
            color = (255, 222, 120) if shot.friendly and shot.max_hits > 1 else ((102, 235, 250) if shot.friendly else (247, 101, 140))
            if shot.friendly and shot.max_hits > 1:
                pygame.draw.line(self.canvas, color, shot.position, shot.position - shot.direction * 14, 3)
            pygame.draw.circle(self.canvas, color, shot.position, shot.radius)
            pygame.draw.circle(self.canvas, (245, 245, 250), shot.position, max(2, shot.radius // 2))
        for pos, time, kind in self.world.effects:
            radius = int((0.35 - time) * 160) if kind == 'explosion' else (5 if kind == 'dash' else 9)
            pygame.draw.circle(self.canvas, (110, 235, 240) if kind != 'hazard' else (250, 100, 90), pos, max(2, radius), 2)
        if self.tiles and not (self.player.invulnerability > 0 and int(self.player.invulnerability * 12) % 2):
            sprite = self.tiles.subsurface((0, 112, 16, 16))
            sprite = pygame.transform.scale(sprite, self.player.rect.size)
            if self.player.facing.x < 0:
                sprite = pygame.transform.flip(sprite, True, False)
            bob = int(self.player.moving and (pygame.time.get_ticks() // 130) % 2)
            self.canvas.blit(sprite, self.player.rect.move(0, -bob))
        elif not self.tiles:
            pygame.draw.rect(self.canvas, settings.ACCENT, self.player.rect, border_radius=3)
        self.menu.draw_hud(self.canvas, self.player, self.world)

    def draw(self):
        if self.state == GameState.MENU:
            self.menu.draw(self.canvas)
        elif self.state == GameState.CONTROLS:
            self.menu.draw_controls(self.canvas)
        else:
            self._draw_arena()
            if self.state == GameState.PAUSED:
                self.menu.draw_pause(self.canvas, self.pause_selected)
            elif self.state == GameState.UPGRADE:
                self.menu.draw_upgrades(self.canvas)
            elif self.state in (GameState.VICTORY, GameState.DEFEAT):
                self.menu.draw_end(self.canvas, self.state == GameState.VICTORY)
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
