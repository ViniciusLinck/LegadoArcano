import unittest

import pygame

from src.combat import Projectile
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

    def test_dead_boss_clears_hostile_attacks_before_damage(self):
        self.world.load_room(3)
        self.world.hazards.append([self.player.position.copy(), 0.01])
        self.world.projectiles.append(Projectile(self.player.position, (1, 0), 30, 0, friendly=False))
        self.world.enemies[0].take_damage(1000)
        self.world.update(0.02)
        self.assertEqual(self.player.hp, 100)
        self.assertFalse(self.world.hazards)
        self.assertFalse(self.world.projectiles)

    def test_explosion_damages_only_nearby_enemies_and_has_cooldown(self):
        self.world.load_room(1)
        near, far = self.world.enemies[:2]
        near.position = self.player.position + pygame.Vector2(25, 0)
        far.position = self.player.position + pygame.Vector2(-180, 0)
        self.assertTrue(self.world.explode())
        self.assertEqual(near.hp, 12)
        self.assertEqual(far.hp, 30)
        self.assertFalse(self.world.explode())

    def test_projectile_reaches_enemy_and_applies_damage(self):
        self.world.load_room(1)
        target = self.world.enemies[0]
        target.position = self.player.position + pygame.Vector2(30, 0)
        self.world.fire(target.position, 'basic')
        self.world.update(0.06)
        self.assertEqual(target.hp, 20)

    def test_simulated_run_can_clear_all_combat_rooms(self):
        for room in range(1, 4):
            self.world.load_room(room)
            for _ in range(3600):
                alive = [enemy for enemy in self.world.enemies if enemy.alive]
                if not alive or self.player.hp <= 0:
                    break
                target = min(alive, key=lambda enemy: enemy.position.distance_to(self.player.position))
                delta = self.player.position - target.position
                move = delta.normalize() if 0 < delta.length() < 105 else pygame.Vector2()
                self.player.update(move, 1 / 60, self.world.bounds)
                self.world.fire(target.position, 'basic')
                self.world.fire(target.position, 'spear')
                if delta.length() < 65:
                    self.world.explode()
                self.world.update(1 / 60)
            self.assertTrue(self.world.complete, f'Sala {room} não foi concluída')
            self.assertGreater(self.player.hp, 0)
            if room < 3:
                self.world.apply_upgrade('vital')


if __name__ == '__main__':
    unittest.main()
