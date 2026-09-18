import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from combocode.engine import KnowledgeBase
from combocode.executor import execute_route
from combocode.browser_internal import canonical_opera_url, launch_opera_internal, launch_browser_internal
from combocode.safety import confirmation_for_route


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'combocode' / 'data' / 'packs' / 'browser_internal_urls.json'


class BrowserInternalPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PACK.read_text(encoding='utf-8'))
        cls.goals = cls.data['goals']
        cls.by_value = {
            route['value']: (goal, route)
            for goal in cls.goals
            for route in goal.get('routes', [])
        }

    def test_pack_contains_all_pdf_urls_plus_keyboard_shortcuts(self):
        self.assertEqual(len(self.goals), 128)
        self.assertEqual(len({g['id'] for g in self.goals}), 128)
        self.assertIn('opera://settings/keyboardShortcuts', self.by_value)
        goal, route = self.by_value['opera://settings/keyboardShortcuts']
        self.assertIn('shortcuts', [a.lower() for a in goal['aliases']])
        self.assertEqual(route['handler'], 'opera_internal')
        self.assertTrue(route['executable'])

    def test_browser_urls_category_populates_left_list(self):
        self.assertEqual({g['category'] for g in self.goals}, {"Browser url's"})
        kb = KnowledgeBase(self.goals)
        self.assertIn("Browser url's", kb.categories())
        hits = kb.search('', category="Browser url's", limit=None)
        self.assertEqual(len(hits), 128)

    def test_browser_url_descriptions_explain_the_destination(self):
        generic = [
            g['name']
            for g in self.goals
            if g.get('description', '').startswith('Apre la pagina interna ')
        ]
        self.assertEqual(generic, [])
        self.assertIn(
            'interazione',
            self.by_value['opera://site-engagement'][0]['description'].lower(),
        )
        self.assertIn(
            'graf',
            self.by_value['opera://gpu'][0]['description'].lower(),
        )

    def test_shortcuts_search_finds_keyboard_shortcuts_page(self):
        kb = KnowledgeBase(self.goals)
        hits = kb.search('shortcuts')
        self.assertTrue(any(
            h.goal['routes'][0]['value'] == 'opera://settings/keyboardShortcuts'
            for h in hits
        ))

    def test_keyboard_shortcuts_page_is_visible_from_opera_domain(self):
        kb = KnowledgeBase.from_pack_dir(ROOT / 'combocode' / 'data' / 'packs')
        hits = kb.search('shortcut', category='Browser · Opera', limit=None)
        self.assertTrue(any(
            route.get('value') == 'opera://settings/keyboardShortcuts'
            for hit in hits
            for route in hit.goal.get('routes', [])
        ))

    def test_all_routes_remain_executable(self):
        routes = [r for g in self.goals for r in g['routes']]
        self.assertEqual(len(routes), 128)
        self.assertTrue(all(r.get('executable') is True for r in routes))

    def test_dangerous_debug_commands_are_destructive_with_warning(self):
        for value in (
            'opera://crash',
            'opera://hang',
            'opera://memory-exhaust',
            'opera://gpucrash',
        ):
            with self.subTest(value=value):
                _goal, route = self.by_value[value]
                self.assertEqual(route['safety'], 'DESTRUCTIVE')
                self.assertTrue(route.get('warning'))

    def test_quit_and_restart_are_caution(self):
        for value in ('opera://quit', 'opera://restart'):
            with self.subTest(value=value):
                _goal, route = self.by_value[value]
                self.assertEqual(route['safety'], 'CAUTION')
                self.assertTrue(route.get('warning'))

    def test_normal_pages_stay_safe(self):
        for value in (
            'opera://settings',
            'opera://downloads',
            'opera://history',
            'opera://extensions',
            'opera://gpu',
            'opera://version',
        ):
            with self.subTest(value=value):
                _goal, route = self.by_value[value]
                self.assertEqual(route['safety'], 'SAFE')


class BrowserLauncherTests(unittest.TestCase):
    def test_chrome_scheme_is_canonicalized_to_opera(self):
        self.assertEqual(canonical_opera_url('chrome://settings'), 'opera://settings')
        self.assertEqual(canonical_opera_url('opera://settings'), 'opera://settings')
        self.assertEqual(
            canonical_opera_url('chrome-untrusted://print'),
            'chrome-untrusted://print',
        )

    @patch('combocode.browser_internal.subprocess.Popen')
    @patch(
        'combocode.browser_internal._navigate_internal_via_address_bar',
        create=True,
    )
    def test_launch_navigates_internal_url_through_opera_address_bar(
        self, navigate, popen
    ):
        launch_opera_internal(
            'opera://settings',
            executable=r'C:\\Opera\\opera.exe',
        )
        popen.assert_called_once_with([r'C:\\Opera\\opera.exe'])
        navigate.assert_called_once_with('opera://settings')

    @patch('combocode.browser_internal.subprocess.Popen')
    def test_generic_chrome_internal_launcher_targets_chrome(self, popen):
        launch_browser_internal(
            'chrome://extensions/shortcuts',
            'chrome',
            executable=r'C:\\Chrome\\chrome.exe',
        )
        popen.assert_called_once_with([
            r'C:\\Chrome\\chrome.exe',
            'chrome://extensions/shortcuts',
        ])

    @patch('combocode.executor.launch_browser_internal')
    def test_executor_dispatches_generic_browser_internal_handler(self, launch):
        route = {
            'kind': 'URI',
            'value': 'edge://extensions/shortcuts',
            'handler': 'browser_internal',
            'browser': 'edge',
            'safety': 'SAFE',
        }
        with patch.object(sys, 'platform', 'win32'):
            execute_route(route)
        launch.assert_called_once_with('edge://extensions/shortcuts', 'edge')

    @patch('combocode.executor.launch_opera_internal')
    def test_executor_dispatches_opera_internal_handler(self, launch):
        route = {
            'kind': 'URI',
            'value': 'opera://settings',
            'handler': 'opera_internal',
            'safety': 'SAFE',
        }
        with patch.object(sys, 'platform', 'win32'):
            execute_route(route)
        launch.assert_called_once_with('opera://settings')


class SafetyConfirmationTests(unittest.TestCase):
    def test_safe_route_needs_no_confirmation(self):
        self.assertIsNone(
            confirmation_for_route({'safety': 'SAFE', 'value': 'opera://settings'})
        )

    def test_caution_uses_specific_warning(self):
        title, message = confirmation_for_route({
            'safety': 'CAUTION',
            'value': 'opera://restart',
            'warning': 'Riavvia Opera e interrompe la sessione corrente.',
        })
        self.assertIn('ATTENZIONE', title)
        self.assertIn('Riavvia Opera', message)
        self.assertIn('opera://restart', message)

    def test_destructive_uses_specific_warning(self):
        title, message = confirmation_for_route({
            'safety': 'DESTRUCTIVE',
            'value': 'opera://crash',
            'warning': 'Provoca intenzionalmente un crash.',
        })
        self.assertIn('PERICOLO', title)
        self.assertIn('Provoca intenzionalmente un crash', message)

    def test_route_detail_shows_goal_description_before_technical_note(self):
        source = (ROOT / 'combocode' / 'ui.py').read_text(encoding='utf-8')
        self.assertIn("description = self.current_goal.get('description', '')", source)
        self.assertIn("lines = [description, note, f'Verifica: {verified}']", source)

    def test_ui_exposes_caution_and_uses_common_confirmation_helper(self):
        source = (ROOT / 'combocode' / 'ui.py').read_text(encoding='utf-8')
        self.assertIn("['SAFE', 'CAUTION', 'ELEVATED', 'DESTRUCTIVE']", source)
        self.assertIn('confirmation_for_route(self.current_route)', source)


if __name__ == '__main__':
    unittest.main()
