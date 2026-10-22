import unittest
from daily_todo.positioning import resolve_position, valid_position


class PositionTests(unittest.TestCase):
    def test_default_respects_dock_and_panel(self):
        self.assertEqual(resolve_position(None, [(66, 32, 1854, 1048)], 0, (980, 650)), (928, 44))

    def test_restore_relative_to_monitor_workarea(self):
        saved = dict(monitor=0, x=74, y=138)
        self.assertEqual(resolve_position(saved, [(66, 32, 1854, 1048)], 0, (980, 650)), (140, 170))

    def test_removed_monitor_falls_back_and_clamps(self):
        saved = dict(monitor=3, x=9999, y=-200)
        self.assertEqual(resolve_position(saved, [(0, 32, 1024, 720)], 0, (980, 650)), (44, 32))

    def test_corrupt_position_is_ignored(self):
        for value in (None, [], {}, dict(monitor=True, x=1, y=2), dict(monitor=0, x=float('nan'), y=2)):
            self.assertFalse(valid_position(value))


if __name__ == '__main__':
    unittest.main()
