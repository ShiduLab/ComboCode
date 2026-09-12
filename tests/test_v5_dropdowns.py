from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class V5DropdownTests(unittest.TestCase):
    def test_no_ttk_combobox_in_ui(self):
        text = (ROOT / 'combocode/ui.py').read_text(encoding='utf-8')
        self.assertNotIn('ttk.Combobox', text)

    def test_menubutton_dropdowns_present(self):
        text = (ROOT / 'combocode/ui.py').read_text(encoding='utf-8')
        self.assertIn('ttk.Menubutton', text)
        self.assertIn('def _make_dropdown', text)
        self.assertIn('def _select_dropdown', text)

if __name__ == '__main__':
    unittest.main()
