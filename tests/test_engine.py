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


if __name__ == '__main__':
    unittest.main()
