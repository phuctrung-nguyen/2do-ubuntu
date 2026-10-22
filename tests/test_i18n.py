import tempfile
import unittest
from datetime import date
from pathlib import Path
from daily_todo.i18n import TEXT, display_date, load_language, save_language, translate


class LanguageTests(unittest.TestCase):
    def test_catalogs_have_matching_keys(self):
        self.assertEqual(TEXT['vi'].keys(), TEXT['en'].keys())

    def test_localized_dates_and_counts(self):
        day = date(2026, 10, 22)
        self.assertEqual(display_date(day, 'vi'), 'Thứ Năm, 22/10/2026')
        self.assertEqual(display_date(day, 'en'), 'Thursday, 22/10/2026')
        self.assertEqual(translate('en', 'tasks', count=1), '1 task')
        self.assertEqual(translate('en', 'tasks', count=2), '2 tasks')

    def test_save_reload_and_invalid_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'settings.json'
            self.assertEqual(load_language(path), 'vi')
            save_language(path, 'en')
            self.assertEqual(load_language(path), 'en')
            for invalid in ('null', '[]', '{"language": []}', '{"language": "fr"}', 'broken'):
                path.write_text(invalid)
                self.assertEqual(load_language(path), 'vi')
