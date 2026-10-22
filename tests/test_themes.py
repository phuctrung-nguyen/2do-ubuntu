import tempfile
import unittest
from pathlib import Path

from daily_todo.themes import THEMES, load_theme, save_theme, theme_css


class ThemeTests(unittest.TestCase):
    def test_preferences_round_trip_and_invalid_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'theme.json'
            self.assertEqual(load_theme(path), 'cyan')
            for theme in THEMES:
                save_theme(path, theme)
                self.assertEqual(load_theme(path), theme)
            for invalid in ('null', '[]', '{"theme": []}', '{"theme": "unknown"}', 'broken'):
                path.write_text(invalid)
                self.assertEqual(load_theme(path), 'cyan')

    def test_palettes_preserve_destructive_colors(self):
        css = 'background: #0c1319; color: #66d4df; border-color: #ffb1b5;'
        self.assertEqual(theme_css(css, 'cyan'), css)
        palettes = {theme_css(css, theme) for theme in THEMES}
        self.assertEqual(len(palettes), len(THEMES))
        for palette in palettes:
            self.assertIn('#ffb1b5', palette)
