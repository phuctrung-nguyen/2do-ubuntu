import unittest
from daily_todo.positioning import resolve_position, valid_position, saved_size


class PositionTests(unittest.TestCase):
    def test_monitor_coordinates_do_not_shift_when_dock_changes(self):
        saved = dict(monitor=0, x=620, y=40, coordinate_space='monitor')
        geometries = [(0, 0, 1920, 1200)]
        for left in (0, 66):
            self.assertEqual(resolve_position(saved, [(left, 32, 1920-left, 1168)],
                                              0, (1300, 780), None, geometries), (620, 40))

    def test_monitor_identity_survives_reordering(self):
        saved = dict(monitor=1, monitor_name='HDMI-1', x=150, y=80)
        areas = [(0, 32, 1920, 1048), (1920, 32, 1920, 1048)]
        self.assertEqual(resolve_position(saved, areas, 1, (1300, 650),
                                          ['HDMI-1', 'DP-1']), (150, 112))

    def test_legacy_position_does_not_match_missing_monitor_name(self):
        saved = dict(monitor=1, x=100, y=60)
        areas = [(0, 32, 1920, 1048), (1920, 32, 1920, 1048)]
        self.assertEqual(resolve_position(saved, areas, 0, (1300, 650),
                                          [None, None]), (2020, 92))

    def test_saved_size_accepts_dimensions_and_old_position_files(self):
        self.assertEqual(saved_size(dict(width=900, height=600)), (900, 600))
        for value in (None, dict(monitor=0, x=10, y=10),
                      dict(width=True, height=650), dict(width=100, height=650),
                      dict(width=1300, height=99999)):
            self.assertEqual(saved_size(value), (1300, 650))

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
