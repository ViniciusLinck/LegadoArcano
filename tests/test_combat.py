import unittest

import pygame

from src.combat import Projectile
from src.player import Player


class CombatTests(unittest.TestCase):
    def setUp(self):
        self.player = Player((100, 100))
        self.bounds = pygame.Rect(0, 0, 400, 300)

    def test_damage_and_invulnerability(self):
        self.assertTrue(self.player.take_damage(30))
        self.assertEqual(self.player.hp, 70)
        self.assertFalse(self.player.take_damage(30))
        self.player.update((0, 0), 0.7, self.bounds)
        self.player.take_damage(1000)
        self.assertEqual(self.player.hp, 0)

    def test_dash_invulnerability_and_cooldown(self):
        self.assertTrue(self.player.dash((1, 0)))
        self.assertFalse(self.player.take_damage(30))
        self.assertFalse(self.player.dash((1, 0)))
        self.player.update((0, 0), 1.3, self.bounds)
        self.assertTrue(self.player.dash((1, 0)))

    def test_cooldowns_prevent_repeated_attacks(self):
        self.assertTrue(self.player.use_ability('spear'))
        self.assertFalse(self.player.use_ability('spear'))
        self.player.update((0, 0), 3.0, self.bounds)
        self.assertTrue(self.player.use_ability('spear'))

    def test_projectile_hit_limit_and_unique_targets(self):
        shot = Projectile((30, 30), (1, 0), 10, 100, max_hits=2)
        a, b = object(), object()
        self.assertTrue(shot.register_hit(a))
        self.assertFalse(shot.register_hit(a))
        self.assertTrue(shot.alive)
        self.assertTrue(shot.register_hit(b))
        self.assertFalse(shot.alive)


if __name__ == '__main__':
    unittest.main()
