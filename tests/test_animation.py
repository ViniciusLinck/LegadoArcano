import unittest

from src.animation import mage_frame


class MageAnimationTests(unittest.TestCase):
    def test_four_facing_directions_use_distinct_rows_and_columns(self):
        self.assertEqual(mage_frame((0, 1), False, 0).topleft, (0, 0))
        self.assertEqual(mage_frame((0, -1), False, 0).topleft, (64, 0))
        self.assertEqual(mage_frame((1, 0), False, 0).topleft, (0, 16))
        self.assertEqual(mage_frame((-1, 0), False, 0).topleft, (64, 16))

    def test_walk_frames_change_with_time_and_idle_stays_still(self):
        self.assertNotEqual(mage_frame((1, 0), True, 0), mage_frame((1, 0), True, 0.15))
        self.assertEqual(mage_frame((1, 0), False, 0), mage_frame((1, 0), False, 5))
