import unittest
from collections import deque
import hashlib
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame

from src.maps import MAPS, MapRenderer, map_for_level
from src.player import Player
from src.combat import Projectile
from src.enemy import Enemy


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def setUp(self):
        self.bounds = pygame.Rect(48, 42, 544, 270)

    def test_each_level_has_its_own_layout(self):
        self.assertEqual(len(MAPS), 11)  # tutorial + 10 níveis
        layouts = [tuple(map_for_level(i).obstacles) for i in range(1, 11)]
        self.assertEqual(len(set(layouts)), 10)

    def test_each_level_renders_a_different_scene(self):
        renderer = MapRenderer(self.bounds)
        digests = [hashlib.sha256(pygame.image.tostring(renderer.get(i), 'RGB')).digest()
                   for i in range(1, 11)]
        self.assertEqual(len(set(digests)), 10)

    def test_obstacles_stay_inside_arena_and_clear_spawn_points(self):
        spawns = [(155, 95), (485, 95), (320, 165), (195, 205), (320, 276), (320, 110)]
        for level in range(11):
            for item in map_for_level(level).solids:
                rect = pygame.Rect(item)
                self.assertTrue(self.bounds.contains(rect), (level, item))
                for point in spawns:
                    area = pygame.Rect(point[0] - 24, point[1] - 24, 48, 48)
                    self.assertFalse(rect.colliderect(area), (level, item, point))

    def test_player_cannot_walk_or_dash_through_solid_pillar(self):
        pillar = pygame.Rect(180, 100, 24, 48)
        player = Player((150, 120))
        player.update((1, 0), 0.3, self.bounds, (pillar,))
        self.assertLessEqual(player.rect.right, pillar.left)
        player.dash((1, 0))
        player.update((1, 0), 0.18, self.bounds, (pillar,))
        self.assertLessEqual(player.rect.right, pillar.left)

    def test_projectile_cannot_tunnel_through_pillar(self):
        pillar = pygame.Rect(180, 100, 24, 48)
        projectile = Projectile((150, 120), (1, 0), 10, 500)
        projectile.update(0.2, self.bounds, (pillar,))
        self.assertFalse(projectile.alive)

    def test_enemy_can_move_around_a_pillar(self):
        pillar = pygame.Rect(180, 100, 24, 48)
        enemy = Enemy('goblin', (150, 120))
        player = Player((250, 120))
        for _ in range(180):
            enemy.update(1 / 60, player, self.bounds, (pillar,))
            self.assertFalse(enemy.rect.colliderect(pillar))
        self.assertGreater(enemy.rect.left, pillar.right)

    def test_every_map_keeps_spawn_points_connected(self):
        targets = [(155, 95), (485, 95), (320, 165), (195, 205), (320, 110)]
        for level in range(11):
            obstacles = [pygame.Rect(item).inflate(16, 20) for item in map_for_level(level).solids]
            def free(point):
                x, y = point
                return (56 <= x <= 584 and 52 <= y <= 300 and
                        not any(rect.collidepoint(point) for rect in obstacles))
            start = (320, 276)
            queue = deque([start])
            visited = {start}
            while queue:
                x, y = queue.popleft()
                for step in ((8, 0), (-8, 0), (0, 8), (0, -8)):
                    nxt = (x + step[0], y + step[1])
                    if nxt not in visited and free(nxt):
                        visited.add(nxt)
                        queue.append(nxt)
            for target in targets:
                self.assertTrue(any(abs(x - target[0]) <= 8 and abs(y - target[1]) <= 8
                                    for x, y in visited), (level, target))
