from pathlib import Path
import json
import tempfile
import unittest

from combocode.storage import UserStore
from combocode.engine import KnowledgeBase


class V8UserShortcutTests(unittest.TestCase):
    def test_user_shortcut_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            store = UserStore(Path(td))
            goal = {
                'name': 'Mia prova', 'category': 'MIE', 'context': 'Opera',
                'routes': [{'kind': 'HOTKEY', 'value': 'CTRL + ALT + S', 'safety': 'SAFE'}],
            }
            saved = store.upsert_user_goal(goal)
            loaded = store.load_user_goals()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]['id'], saved['id'])
            self.assertEqual(loaded[0]['origin'], 'user')
            self.assertEqual(loaded[0]['category'], 'MIE')

    def test_kb_indexes_context(self):
        goal = {
            'id': 'user.test', 'name': 'Apri pannello', 'category': 'MIE',
            'context': 'Programma segretissimo', 'origin': 'user',
            'routes': [{'kind': 'HOTKEY', 'value': 'CTRL + 1'}],
        }
        kb = KnowledgeBase([goal])
        hits = kb.search('segretissimo')
        self.assertEqual(hits[0].goal['id'], 'user.test')

    def test_import_export(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            store = UserStore(base/'a')
            store.upsert_user_goal({'name':'Uno','routes':[{'kind':'CMD','value':'dir'}]})
            exported = base/'backup.json'
            store.export_user_shortcuts(exported)
            other = UserStore(base/'b')
            count = other.import_user_shortcuts(exported)
            self.assertEqual(count, 1)
            self.assertEqual(other.load_user_goals()[0]['name'], 'Uno')

if __name__ == '__main__':
    unittest.main()
