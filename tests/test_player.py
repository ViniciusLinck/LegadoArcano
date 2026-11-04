import math
import unittest

import pygame

from src.player import Player


class PlayerMovementTests(unittest.TestCase):
    def setUp(self):
        self.bounds = pygame.Rect(0, 0, 1000, 1000)
        self.player = Player((500, 500))

    def test_cardinal_movement_uses_seconds(self):
        self.player.update((1, 0), 0.5, self.bounds)
        self.assertAlmostEqual(self.player.position.x, 610)
        self.assertAlmostEqual(self.player.position.y, 500)

    def test_diagonal_movement_is_normalized(self):
        self.player.update((1, 1), 0.5, self.bounds)
        distance = self.player.position.distance_to((500, 500))
        self.assertAlmostEqual(distance, 110)

    def test_time_steps_produce_same_result(self):
        other = Player((500, 500))
        self.player.update((1, 0), 0.5, self.bounds)
        for _ in range(10):
            other.update((1, 0), 0.05, self.bounds)
        self.assertAlmostEqual(self.player.position.x, other.position.x)

    def test_all_edges_constrain_entire_player(self):
        for direction, edge in (((-1, 0), 'left'), ((1, 0), 'right'),
                                ((0, -1), 'top'), ((0, 1), 'bottom')):
            with self.subTest(edge=edge):
                player = Player((500, 500))
                player.update(direction, 20, self.bounds)
                self.assertEqual(getattr(player.rect, edge), getattr(self.bounds, edge))
                self.assertTrue(self.bounds.contains(player.rect))

    def test_zero_direction_does_not_move(self):
        self.player.update((0, 0), 1, self.bounds)
        self.assertEqual(self.player.position, pygame.Vector2(500, 500))


if __name__ == '__main__':
    unittest.main()
