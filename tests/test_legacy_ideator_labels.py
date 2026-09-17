from pathlib import Path
import json
import unittest

from combocode.engine import KnowledgeBase

ROOT = Path(__file__).resolve().parents[1]


class LegacyIdeatorLabelsTests(unittest.TestCase):
    def test_legacy_archive_uses_ideator_labels_without_touching_mie(self):
        personal = {
            'id': 'user.test',
            'name': 'Mia',
            'origin': 'user',
            'description': 'Creata dall’utente',
            'routes': [],
        }
        kb = KnowledgeBase.from_pack_dir(ROOT / 'combocode/data/packs', extra_goals=[personal])
        legacy = [g for g in kb.goals if str(g.get('id', '')).startswith('archive.user.')]
        self.assertTrue(legacy)
        for goal in legacy:
            text = json.dumps(goal, ensure_ascii=False).lower()
            self.assertNotIn('archivio utente', text)
            self.assertNotIn('dell’utente', text)
            self.assertNotIn('dall’utente', text)
        self.assertEqual(kb.by_id['user.test']['description'], 'Creata dall’utente')


if __name__ == '__main__':
    unittest.main()
