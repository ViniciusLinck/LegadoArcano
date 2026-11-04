import unittest

import pygame

from src.player import Player
from src.world import World


class WorldTests(unittest.TestCase):
    def setUp(self):
        self.player = Player((320, 180))
        self.world = World(self.player, pygame.Rect(48, 42, 544, 270))

    def test_room_layout_and_completion(self):
        self.world.load_room(1)
        self.assertEqual(len(self.world.enemies), 3)
        self.assertFalse(self.world.complete)
        for enemy in self.world.enemies:
            enemy.take_damage(1000)
        self.world.update(0.01)
        self.assertTrue(self.world.complete)

    def test_dead_enemy_cannot_attack(self):
        self.world.load_room(1)
        enemy = self.world.enemies[0]
        enemy.position = self.player.position.copy()
        enemy.take_damage(1000)
        self.assertEqual(enemy.update(1, self.player, self.world.bounds), [])
        self.assertEqual(self.player.hp, 100)

    def test_upgrade_changes_stats_and_clamps_healing(self):
        self.player.hp = 85
        self.world.apply_upgrade('vital')
        self.assertEqual(self.player.hp, 100)
        self.world.apply_upgrade('power')
        self.assertAlmostEqual(self.player.damage_multiplier, 1.2)
        self.world.apply_upgrade('flow')
        self.assertAlmostEqual(self.player.cooldown_multiplier, 0.8)

    def test_boss_changes_phase_at_half_health(self):
        self.world.load_room(3)
        boss = self.world.enemies[0]
        boss.take_damage(150)
        self.assertEqual(boss.phase, 2)
        boss.take_damage(150)
        self.world.update(0.01)
        self.assertTrue(self.world.complete)

    def test_room_transition_clears_projectiles(self):
        self.world.fire((500, 180), 'basic')
        self.assertTrue(self.world.projectiles)
        self.world.load_room(1)
        self.assertFalse(self.world.projectiles)


if __name__ == '__main__':
    unittest.main()
