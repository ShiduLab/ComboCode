from pathlib import Path
import json
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class WordPackTests(unittest.TestCase):
    def setUp(self):
        self.pack_paths = sorted((ROOT / 'combocode/data/packs').glob('word_shortcuts_windows_*.json'))

    def test_word_pack_contains_full_windows_reference(self):
        self.assertTrue(self.pack_paths, 'Mancano i pack Word per Windows')
        goals = [g for p in self.pack_paths for g in json.loads(p.read_text(encoding='utf-8'))['goals']]
        routes = [r for g in goals for r in g.get('routes', [])]
        self.assertGreaterEqual(len(goals), 337)
        self.assertGreaterEqual(len(routes), 337)

    def test_word_pack_has_shortcuts_from_distant_sections(self):
        goals = [g for p in self.pack_paths for g in json.loads(p.read_text(encoding='utf-8'))['goals']]
        values = {r['value'] for g in goals for r in g['routes']}
        expected_values = {
            'CTRL + B',
            'CTRL + S',
            'ALT + SHIFT + O',
            'CTRL + ALT + F',
            'CTRL + ALT + P',
            'ALT + F11',
            'CTRL + SHIFT + F12',
        }
        self.assertTrue(expected_values.issubset(values), expected_values - values)

    def test_every_word_route_points_to_microsoft_source(self):
        for path in self.pack_paths:
            data = json.loads(path.read_text(encoding='utf-8'))
            for goal in data['goals']:
                for route in goal['routes']:
                    self.assertEqual(route.get('verified'), 'Microsoft')
                    self.assertEqual(route.get('source'), 'https://support.microsoft.com/it-it/accessibility/word/keyboard-shortcuts-in-word')


class ThemeTests(unittest.TestCase):
    def test_dark_is_safe_fallback_when_system_theme_cannot_be_read(self):
        import combocode.theme as theme
        with patch.object(theme.sys, 'platform', 'linux'):
            self.assertTrue(theme.system_prefers_dark())


if __name__ == '__main__':
    unittest.main()
