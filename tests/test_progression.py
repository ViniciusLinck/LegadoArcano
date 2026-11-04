import unittest

import pygame

from src.player import Player
from src.world import World


class TenLevelProgressionTests(unittest.TestCase):
    def setUp(self):
        self.player = Player((320, 180))
        self.world = World(self.player, pygame.Rect(48, 42, 544, 270))

    def test_ten_levels_with_bosses_on_five_and_ten(self):
        self.assertEqual(self.world.final_level, 10)
        for level in range(1, 11):
            self.world.load_room(level)
            self.assertEqual(self.world.is_boss_room, level in (5, 10))
            self.assertTrue(self.world.enemies)
            self.assertEqual(self.world.wave_count, 1 if level in (5, 10) else 2)

    def test_common_room_requires_all_waves(self):
        self.world.load_room(1)
        self.assertEqual(self.world.wave_number, 1)
        self.assertEqual(self.world.wave_count, 2)
        for enemy in self.world.enemies:
            enemy.take_damage(9999)
        self.assertFalse(self.world.complete)
        self.world.update(2)
        self.assertEqual(self.world.wave_number, 2)
        self.assertTrue(any(enemy.alive for enemy in self.world.enemies))
        for enemy in self.world.enemies:
            enemy.take_damage(9999)
        self.assertTrue(self.world.complete)

    def test_all_requested_enemy_types_have_separate_sprites(self):
        kinds = set()
        for level in range(1, 11):
            self.world.load_room(level)
            for wave in self.world.waves:
                kinds.update(kind for kind, _ in wave)
        self.assertTrue({'goblin', 'golem', 'wizard', 'ninja', 'warrior', 'dragon'} <= kinds)

    def test_fifth_boss_is_not_final_boss(self):
        self.world.load_room(5)
        self.assertEqual(self.world.enemies[0].kind, 'golem')
        self.assertTrue(self.world.enemies[0].is_boss)
        self.world.load_room(10)
        self.assertEqual(self.world.enemies[0].kind, 'dragon')
        self.assertTrue(self.world.enemies[0].is_boss)
