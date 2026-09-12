from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[1]
class V6Shortcuts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'combocode/data/packs/windows_shortcuts_complete.json').read_text(encoding='utf-8'))
        cls.rows=[(g['category'], r['value'], g['name']) for g in cls.data['goals'] for r in g['routes']]
    def test_catalog_is_large(self):
        self.assertGreaterEqual(len(self.rows), 180)
    def test_key_windows_routes(self):
        values={v for _,v,_ in self.rows}
        for expected in ['WIN + R','WIN + CTRL + D','CTRL + SHIFT + N','ALT + D','WIN + CTRL + SHIFT + B','SHIFT + F10']:
            self.assertIn(expected, values)
    def test_categories(self):
        cats={c for c,_,_ in self.rows}
        self.assertGreaterEqual(len(cats), 10)
if __name__=='__main__': unittest.main()
