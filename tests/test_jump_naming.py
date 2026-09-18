from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class JumpNamingTests(unittest.TestCase):
    def test_current_jump_uses_j_prefix(self):
        jump = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        self.assertTrue(jump.startswith('J'), jump)

    def test_windows_build_uses_jump_name(self):
        spec = (ROOT / 'ComboCode.spec').read_text(encoding='utf-8')
        workflow = (ROOT / '.github/workflows/windows.yml').read_text(encoding='utf-8')
        app = (ROOT / 'combocode/app.py').read_text(encoding='utf-8')
        self.assertIn("name='ComboCode J8.0.1'", spec)
        self.assertIn('ComboCode-Windows-J8.0.1', workflow)
        self.assertIn('dist/ComboCode J8.0.1.exe', workflow)
        self.assertIn('ShiduLab.ComboCode.J8.0.1', app)


if __name__ == '__main__':
    unittest.main()
