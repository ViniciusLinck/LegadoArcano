import os
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from src.effects import EffectLibrary, frame_index
from src.player import Player
from src.world import World


class EffectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_frame_timing_clamps_and_loops(self):
        self.assertEqual(frame_index(0, 0.6, 10), 0)
        self.assertEqual(frame_index(0.3, 0.6, 10), 5)
        self.assertEqual(frame_index(5, 0.6, 10), 9)
        self.assertEqual(frame_index(0.6, 0.6, 10, loop=True), 0)

    def test_spritesheets_load_and_have_distinct_frames(self):
        library = EffectLibrary()
        self.assertTrue({'orb', 'lightning', 'burst', 'ring', 'impact', 'smoke'} <= set(library.sheets))
        first = library.frame('orb', 0, 0.4, loop=True)
        second = library.frame('orb', 0.12, 0.4, loop=True)
        self.assertNotEqual(pygame.image.tostring(first, 'RGBA'), pygame.image.tostring(second, 'RGBA'))

    def test_cast_and_explosion_trigger_visual_effects(self):
        world = World(Player((320, 180)), pygame.Rect(48, 42, 544, 270))
        world.fire((450, 180), 'basic')
        self.assertIn('cast', [item[2] for item in world.effects])
        world.explode()
        self.assertIn('explosion', [item[2] for item in world.effects])
