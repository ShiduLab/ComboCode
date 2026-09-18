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
        self.assertGreaterEqual(len(rows), 300)

    def test_archive_cmd_filter(self):
        rows = self.kb.route_rows(kind='CMD')
        self.assertGreater(len(rows), 100)
        self.assertTrue(all(row.route.get('kind') == 'CMD' for row in rows))
        values = {row.route.get('value') for row in rows}
        self.assertIn('dir', values)
        self.assertIn('help', values)
        self.assertIn('ipconfig /all', values)

    def test_legacy_user_archive_imported(self):
        values = {
            row.route.get('value', '').lower()
            for row in self.kb.route_rows(category='ESEGUI (archivio)')
        }
        self.assertIn('ciadv.msc', values)
        self.assertIn('control userpasswords2', values)
        self.assertIn('winver', values)

    def test_sort_by_category(self):
        rows = self.kb.route_rows(sort_by='cat')
        categories = [row.goal.get('category', '').lower() for row in rows]
        self.assertEqual(categories, sorted(categories))
        rows_desc = self.kb.route_rows(sort_by='cat', descending=True)
        categories_desc = [row.goal.get('category', '').lower() for row in rows_desc]
        self.assertEqual(categories_desc, sorted(categories_desc, reverse=True))

    def test_sicurezza_opens_windows_security_app(self):
        hits = self.kb.search('sicurezza', limit=None)
        self.assertTrue(hits)
        self.assertEqual(hits[0].goal['id'], 'sys.windows-security')
        values = {r['value'] for r in hits[0].goal['routes']}
        self.assertIn('windowsdefender:', values)

    def test_sicurezza_search_never_returns_ctrl_alt_del(self):
        hits = self.kb.search('sicurezza', limit=None)
        values = {
            route.get('value')
            for hit in hits
            for route in hit.goal.get('routes', [])
        }
        self.assertNotIn('CTRL + ALT + DEL', values)

    def test_ctrl_alt_del_is_session_management(self):
        hits = self.kb.search('gestione sessione', limit=None)
        self.assertTrue(hits)
        ctrl_alt_del = [
            hit.goal for hit in hits
            if any(r.get('value') == 'CTRL + ALT + DEL' for r in hit.goal.get('routes', []))
        ]
        self.assertEqual(len(ctrl_alt_del), 1)
        self.assertNotIn('sicurezza', ctrl_alt_del[0].get('name', '').lower())
        self.assertNotIn('sicurezza', ctrl_alt_del[0].get('description', '').lower())

    def test_transparent_domains_match_primary_and_additional_domain(self):
        goal = {
            'id': 'test.transparent',
            'name': 'Scorciatoie da tastiera — Opera',
            'category': "Browser url's",
            'domains': ['Browser · Opera'],
            'routes': [{'kind': 'URI', 'value': 'opera://settings/keyboardShortcuts'}],
        }
        kb = KnowledgeBase([goal])

        self.assertEqual(
            [h.goal['id'] for h in kb.search('', category="Browser url's", limit=None)],
            ['test.transparent'],
        )
        self.assertEqual(
            [h.goal['id'] for h in kb.search('', category='Browser · Opera', limit=None)],
            ['test.transparent'],
        )
        self.assertIn("Browser url's", kb.categories())
        self.assertIn('Browser · Opera', kb.categories())

    def test_unique_goal_ids(self):
        ids = [g['id'] for g in self.kb.goals]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == '__main__':
    unittest.main()
