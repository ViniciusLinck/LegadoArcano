import os
import unittest
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from src.game import Game, GameState
from src.assets import Sounds


class GameStateTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def key(self, key):
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))

    def test_start_pause_and_return_to_menu(self):
        self.assertEqual(self.game.state, GameState.MENU)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.state, GameState.PAUSED)
        self.game.pause_selected = 2
        self.key(pygame.K_RETURN)
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

    def test_progression_upgrades_and_victory(self):
        self.key(pygame.K_RETURN)
        self.key(pygame.K_e)
        self.assertEqual(self.game.world.room_index, 1)
        self.key(pygame.K_e)
        self.assertEqual(self.game.world.room_index, 1)
        for enemy in self.game.world.enemies:
            enemy.take_damage(1000)
        self.game.update(0.01)
        self.assertEqual(self.game.state, GameState.UPGRADE)
        self.key(pygame.K_1)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.key(pygame.K_e)
        self.assertEqual(self.game.world.room_index, 2)
        self.game.world.load_room(3)
        self.game.world.enemies[0].take_damage(1000)
        self.game.update(1.1)
        self.assertEqual(self.game.state, GameState.VICTORY)

    def test_defeat_and_restart_reset_run(self):
        self.key(pygame.K_RETURN)
        self.game.player.hp = 0
        self.game.update(0.01)
        self.assertEqual(self.game.state, GameState.DEFEAT)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertEqual(self.game.player.hp, 100)
        self.assertEqual(self.game.world.room_index, 0)

    def test_mouse_attacks_and_cooldowns(self):
        self.key(pygame.K_RETURN)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(800, 300))
        self.game.handle_event(event)
        self.game.handle_event(event)
        self.assertEqual(len(self.game.world.projectiles), 1)
        self.assertEqual(self.game.world.projectiles[0].max_hits, 2)
        self.assertGreater(self.game.player.cooldowns['spear'], 0)

    def test_draw_combat_objects_and_telegraph(self):
        self.key(pygame.K_RETURN)
        self.game.world.load_room(3)
        self.game.world.enemies[0].windup = 0.5
        self.game.world.hazards.append([pygame.Vector2(320, 180), 0.5])
        self.game.world.fire((400, 100), 'spear')
        self.game.draw()

    def test_audio_is_optional_when_mixer_unavailable(self):
        with patch('pygame.mixer.get_init', return_value=None):
            sounds = Sounds()
            self.assertEqual(sounds.clips, {})
            sounds.play('cast')
