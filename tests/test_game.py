import os
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from src.game import Game, GameState


class GameStateTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def key(self, key):
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))

    def test_start_and_return_to_menu(self):
        self.assertEqual(self.game.state, GameState.MENU)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.state, GameState.MENU)

    def test_controls_screen_and_back(self):
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.state, GameState.CONTROLS)
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.state, GameState.MENU)

    def test_mouse_coordinates_are_scaled_to_logical_size(self):
        rect = self.game.menu.buttons[0][1]
        pos = (rect.centerx * 2, rect.centery * 2)
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_quit_works_in_every_state(self):
        for state in GameState:
            with self.subTest(state=state):
                self.game.running = True
                self.game.state = state
                self.game.handle_event(pygame.event.Event(pygame.QUIT))
                self.assertFalse(self.game.running)

    def test_menu_exit_action(self):
        self.key(pygame.K_UP)
        self.key(pygame.K_RETURN)
        self.assertFalse(self.game.running)

    def test_render_all_states(self):
        for state in GameState:
            with self.subTest(state=state):
                self.game.state = state
                self.game.draw()

    def test_arena_renders_when_optional_art_is_missing(self):
        self.game.tiles = None
        self.game.state = GameState.PLAYING
        self.game.draw()

    def test_run_exits_on_window_close(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game.run()
        self.assertFalse(self.game.running)
