from pathlib import Path
import unittest

from combocode.engine import KnowledgeBase


PACKS = Path(__file__).resolve().parents[1] / 'combocode' / 'data' / 'packs'


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeBase.from_pack_dir(PACKS)

    def test_esegui(self):
        hits = self.kb.search('Esegui')
        self.assertTrue(hits)
        self.assertEqual(hits[0].goal['id'], 'windows.run')
        self.assertIn('WIN + R', [r['value'] for r in hits[0].goal['routes']])

    def test_network_connections(self):
        hits = self.kb.search('Connessioni di rete')
        self.assertTrue(hits)
        self.assertEqual(hits[0].goal['id'], 'net.connections')
        values = {r['value'] for r in hits[0].goal['routes']}
        self.assertIn('ncpa.cpl', values)
        self.assertIn('control netconnections', values)

    def test_alias(self):
        hits = self.kb.search('schede di rete')
        self.assertTrue(hits)
        self.assertEqual(hits[0].goal['id'], 'net.connections')

    def test_command_search(self):
        hits = self.kb.search('ipconfig /all')
        self.assertTrue(hits)
        self.assertEqual(hits[0].goal['id'], 'net.ipconfig')

    def test_keyboard_query_returns_family(self):
        hits = self.kb.search('tastiera', limit=None)
        names = {h.goal['name'] for h in hits}
        self.assertIn('Tastiera su schermo', names)
        self.assertIn('Impostazioni digitazione', names)
        self.assertIn('Accessibilità tastiera', names)
        self.assertIn('Proprietà tastiera classiche', names)
        self.assertGreaterEqual(len(hits), 5)

    def test_osk_routes(self):
        goal = self.kb.by_id['keyboard.onscreen']
        values = {r['value'] for r in goal['routes']}
        self.assertIn('WIN + CTRL + O', values)
        self.assertIn('osk.exe', values)

    def test_archive_contains_every_route(self):
        expected = sum(len(g.get('routes', [])) for g in self.kb.goals)
        rows = self.kb.route_rows()
        self.assertEqual(len(rows), expected)

    def test_archive_cmd_filter(self):
        rows = self.kb.route_rows(kind='CMD')
        self.assertGreater(len(rows), 50)
        self.assertTrue(all(row.route.get('kind') == 'CMD' for row in rows))
        values = {row.route.get('value') for row in rows}
        self.assertIn('dir', values)
        self.assertIn('help', values)
        self.assertIn('ipconfig /all', values)

    def test_unique_goal_ids(self):
        ids = [g['id'] for g in self.kb.goals]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == '__main__':
    unittest.main()
