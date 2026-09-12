from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V4SourceTests(unittest.TestCase):
    def test_executor_no_legacy_block(self):
        text = (ROOT / 'combocode/executor.py').read_text(encoding='utf-8')
        self.assertNotIn("if not route.get('executable'", text)
        self.assertIn("if kind == 'HOTKEY':", text)
        self.assertIn("subprocess.Popen(['cmd.exe', '/k', value])", text)

    def test_ui_has_clear_search(self):
        text = (ROOT / 'combocode/ui.py').read_text(encoding='utf-8')
        self.assertIn("command=self.clear_search", text)
        self.assertIn("def clear_search(self):", text)

    def test_ui_has_search_sorting(self):
        text = (ROOT / 'combocode/ui.py').read_text(encoding='utf-8')
        self.assertIn("def sort_search_results", text)
        self.assertIn("command=lambda: self.sort_search_results('cat')", text)

    def test_brand_is_right_and_theme_text(self):
        text = (ROOT / 'combocode/ui.py').read_text(encoding='utf-8')
        self.assertIn("brand_frame.grid(row=0, column=1, sticky='se')", text)
        self.assertIn("text='ShiduLab', style='Brand.TLabel'", text)


if __name__ == '__main__':
    unittest.main()
