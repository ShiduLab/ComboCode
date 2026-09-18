from pathlib import Path
import json, unittest

from combocode.engine import KnowledgeBase

ROOT = Path(__file__).resolve().parents[1]

class V7BrowserShortcuts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT/'combocode/data/packs/browser_shortcuts_windows.json').read_text(encoding='utf-8'))
        cls.goals = cls.data['goals']
        cls.rows = [(g['category'], r['value'], g['name']) for g in cls.goals for r in g['routes']]

    def test_pack_is_large(self):
        self.assertGreaterEqual(len(self.goals), 180)
        self.assertGreaterEqual(len(self.rows), 230)

    def test_all_major_browsers_present(self):
        cats = {g['category'] for g in self.goals}
        for expected in ['Browser · Opera', 'Browser · Chrome', 'Browser · Edge', 'Browser · Firefox', 'Browser · Browser comuni']:
            self.assertIn(expected, cats)

    def test_browser_specific_shortcut_settings_are_discoverable(self):
        kb = KnowledgeBase.from_pack_dir(ROOT/'combocode/data/packs')
        expected = {
            'Browser · Chrome': 'chrome://extensions/shortcuts',
            'Browser · Edge': 'edge://extensions/shortcuts',
            'Browser · Firefox': 'about:keyboard',
            'Browser · Opera': 'opera://settings/keyboardShortcuts',
        }
        for category, url in expected.items():
            with self.subTest(category=category):
                hits = kb.search('shortcut', category=category, limit=None)
                values = [
                    route.get('value', '')
                    for hit in hits
                    for route in hit.goal.get('routes', [])
                ]
                self.assertTrue(any(url in value for value in values), (category, url))

    def test_navigation_basics_present(self):
        values = {r[1] for r in self.rows}
        for expected in ['CTRL + T', 'CTRL + SHIFT + T', 'CTRL + L', 'ALT + FRECCIA SINISTRA', 'ALT + FRECCIA DESTRA', 'CTRL + TAB', 'CTRL + SHIFT + TAB']:
            self.assertIn(expected, values)

if __name__ == '__main__':
    unittest.main()
