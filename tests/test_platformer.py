import os
import unittest
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from src.platformer import PlatformGame

class PlatformDemoTest(unittest.TestCase):
    def test_jump_lands_on_first_platform_in_every_level(self):
        game = PlatformGame()
        game.state = 'play'
        for level in range(4):
            game.level = level
            game.load_level()
            game.enemies.clear()
            platform = game.platforms[1]
            game.x = float(platform.left + 15)
            game.update(.02)
            game.jump()
            for _ in range(70):
                game.update(.016)
            self.assertEqual(game.rect().bottom, platform.top, f'level {level+1}')
            self.assertTrue(game.grounded)

    def test_landing_prefers_first_platform_crossed(self):
        game = PlatformGame()
        game.state = 'play'
        game.enemies.clear()
        game.platforms = [pygame.Rect(0, 470, 500, 70), pygame.Rect(0, 450, 500, 10)]
        game.x, game.y, game.vy = 100., 370., 850.
        game.update(.1)
        self.assertEqual(game.rect().bottom, 450)
        self.assertTrue(game.grounded)

    def test_mouse_hover_and_click_select_class(self):
        game = PlatformGame()
        game.choose()
        point = game.class_cards()[2].center
        game.event(pygame.event.Event(pygame.MOUSEMOTION, pos=point, rel=(0, 0), buttons=(0, 0, 0)))
        self.assertEqual(game.selection, 2)
        game.draw()
        game.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=point, button=1))
        self.assertEqual((game.state, game.class_index), ('play', 2))

    def test_buffered_jump_fires_after_landing(self):
        game = PlatformGame()
        game.state = 'play'
        game.enemies.clear()
        game.x, game.y, game.vy = 80., 410., 200.
        game.grounded = False
        game.jump()
        game.update(.05)
        self.assertLess(game.vy, 0)
        self.assertFalse(game.grounded)

    def test_wasd_jump_and_drop_through_platform(self):
        game = PlatformGame()
        game.state = 'play'
        platform = game.platforms[1]
        game.x = float(platform.left + 10)
        game.y = float(platform.top - game.rect().height)
        game.grounded = True
        game.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        self.assertLess(game.vy, 0)
        game.y = float(platform.top - game.rect().height)
        game.vy = 0
        game.grounded = True
        game.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
        game.update(.05)
        self.assertGreater(game.rect().bottom, platform.top)
        self.assertFalse(game.grounded)
        for _ in range(60):
            game.update(.02)
        self.assertEqual(game.rect().bottom, 470)
        game.drop()
        self.assertTrue(game.grounded)

    def test_menu_options_and_restart_clear_combat_state(self):
        game = PlatformGame()
        game.selection = 1
        game.choose()
        self.assertEqual(game.state, 'options')
        game.choose()
        self.assertFalse(game.sound)
        game.selection = 1
        game.choose()
        game.choose()
        game.choose()
        game.projectiles.append({'x': 1, 'y': 1, 'vx': 0, 'enemy': False, 'life': 1})
        game.dash_cooldown = .9
        game.reset()
        self.assertEqual(game.projectiles, [])
        self.assertEqual(game.dash_cooldown, 0)

    def test_each_class_can_damage_boss(self):
        for chosen in range(3):
            with self.subTest(chosen=chosen):
                game = PlatformGame()
                game.class_index = chosen
                game.level = 4
                game.load_level()
                game.state = 'play'
                boss = game.enemies[0]
                game.x = boss['x'] - (40 if chosen == 1 else 100)
                game.y = boss['y'] + 40
                original = boss['hp']
                game.attack()
                for _ in range(20):
                    game.update(.02)
                self.assertLess(boss['hp'], original)

    def test_death_animation_and_paused_state(self):
        game = PlatformGame()
        game.state = 'play'
        game.hp = 1
        game.hurt_player(5)
        self.assertEqual(game.state, 'dying')
        game.update(.4)
        game.draw()
        self.assertEqual(game.state, 'dying')
        game.update(.6)
        self.assertEqual(game.state, 'defeat')
        game.state = 'pause'
        old_position = game.x
        game.update(.5)
        self.assertEqual(game.x, old_position)

    def test_special_cooldown_and_piercing_arrow(self):
        game = PlatformGame()
        game.state = 'play'
        game.class_index = 2
        game.special()
        self.assertGreater(game.special_cooldown, 0)
        self.assertTrue(game.projectiles[0]['pierce'])
        game.special()
        self.assertEqual(len(game.projectiles), 1)
        game.state = 'pause'
        before = game.special_cooldown
        game.update(.5)
        self.assertEqual(game.special_cooldown, before)

    def test_trap_damage_and_restart_from_defeat(self):
        game = PlatformGame()
        game.level = 1
        game.load_level()
        game.state = 'play'
        game.x = game.hazards[0].x
        game.y = 422
        original = game.hp
        game.update(.01)
        self.assertLess(game.hp, original)
        game.state = 'defeat'
        game.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        self.assertEqual((game.state, game.level, game.hp), ('play', 0, game.max_hp))

    def test_enemy_types_have_distinct_behavior_and_telegraph(self):
        game = PlatformGame()
        game.state = 'play'
        self.assertEqual({e['kind'] for e in game.enemies}, {'goblin', 'ninja', 'golem'})
        speeds = []
        for kind in ('goblin', 'ninja', 'golem'):
            enemy = game.enemy(200, kind=kind)
            game.x = 100
            game.update_enemy(enemy, .1)
            speeds.append(200 - enemy['x'])
        self.assertGreater(speeds[1], speeds[0])
        self.assertGreater(speeds[0], speeds[2])
        golem = game.enemy(120, kind='golem')
        game.update_enemy(golem, .01)
        self.assertEqual(golem['mode'], 'windup')
        self.assertGreater(golem['mode_time'], .5)

    def test_boss_ground_attack_and_death_delay(self):
        game = PlatformGame()
        game.level = 4
        game.load_level()
        game.state = 'play'
        boss = game.enemies[0]
        boss['attack_count'] = 1
        boss['timer'] = 0
        game.update(.01)
        self.assertEqual(len(game.shockwaves), 2)
        boss['hp'] = 0
        game.update(.1)
        self.assertFalse(game.boss_defeated)
        game.draw()
        game.update(1.2)
        self.assertTrue(game.boss_defeated)

    def test_classes_levels_and_two_stage_boss(self):
        game = PlatformGame()
        game.choose()
        self.assertEqual(game.state, 'classes')
        game.selection = 2
        game.choose()
        self.assertEqual((game.state, game.class_index), ('play', 2))
        game.update(.05)
        self.assertTrue(game.grounded)
        game.jump()
        self.assertLess(game.vy, 0)
        game.attack()
        self.assertEqual(len(game.projectiles), 1)
        for level in range(4):
            game.enemies.clear()
            game.x = game.width - 50
            game.update(.01)
            self.assertEqual(game.level, level + 1)
        boss = game.enemies[0]
        boss['hp'] = boss['maxhp'] / 2
        boss['timer'] = 0
        game.update(.01)
        self.assertEqual(sum(p['enemy'] for p in game.projectiles), 3)
        boss['hp'] = 0
        game.update(.01)
        self.assertFalse(game.boss_defeated)
        game.update(1.2)
        self.assertTrue(game.boss_defeated)
        self.assertEqual(game.state, 'play')
        game.x = game.width - 50
        game.update(.01)
        self.assertEqual(game.state, 'victory')
        game.draw()

if __name__ == '__main__':
    unittest.main()
