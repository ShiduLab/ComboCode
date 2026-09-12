from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class V8UISourceTests(unittest.TestCase):
    def test_mie_tab_and_form_exist(self):
        text = (ROOT/'combocode/ui.py').read_text(encoding='utf-8')
        self.assertIn("self.notebook.add(self.mine_tab, text='MIE')", text)
        self.assertIn('def add_user_shortcut', text)
        self.assertIn('def _shortcut_form', text)
        self.assertIn('KEY+MOUSE', text)
        self.assertIn('POWERSHELL', text)

    def test_user_data_outside_program(self):
        text = (ROOT/'combocode/storage.py').read_text(encoding='utf-8')
        self.assertIn("self.shortcuts_path = self.base / 'user_shortcuts.json'", text)

if __name__ == '__main__':
    unittest.main()
