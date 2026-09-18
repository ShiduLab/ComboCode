from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import time
from pathlib import Path


def canonical_opera_url(url: str) -> str:
    value = str(url or '').strip()
    if value.lower().startswith('chrome://'):
        return 'opera://' + value[len('chrome://'):]
    return value


def find_opera_executable() -> str | None:
    found = shutil.which('opera.exe') or shutil.which('opera')
    if found:
        return found

    candidates: list[Path] = []
    local = os.environ.get('LOCALAPPDATA')
    program_files = os.environ.get('PROGRAMFILES')
    program_files_x86 = os.environ.get('PROGRAMFILES(X86)')

    if local:
        candidates.extend([
            Path(local) / 'Programs' / 'Opera' / 'opera.exe',
            Path(local) / 'Programs' / 'Opera GX' / 'opera.exe',
        ])
    if program_files:
        candidates.extend([
            Path(program_files) / 'Opera' / 'opera.exe',
            Path(program_files) / 'Opera GX' / 'opera.exe',
        ])
    if program_files_x86:
        candidates.extend([
            Path(program_files_x86) / 'Opera' / 'opera.exe',
            Path(program_files_x86) / 'Opera GX' / 'opera.exe',
        ])

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None



def find_browser_executable(browser: str) -> str | None:
    name = str(browser or '').strip().lower()
    if name == 'opera':
        return find_opera_executable()

    aliases = {
        'chrome': ('chrome.exe', 'chrome'),
        'edge': ('msedge.exe', 'msedge'),
        'firefox': ('firefox.exe', 'firefox'),
    }
    if name not in aliases:
        return None

    for executable_name in aliases[name]:
        found = shutil.which(executable_name)
        if found:
            return found

    local = os.environ.get('LOCALAPPDATA')
    program_files = os.environ.get('PROGRAMFILES')
    program_files_x86 = os.environ.get('PROGRAMFILES(X86)')
    candidates: list[Path] = []

    if name == 'chrome':
        for base in (local, program_files, program_files_x86):
            if base:
                candidates.append(Path(base) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe')
    elif name == 'edge':
        for base in (local, program_files, program_files_x86):
            if base:
                candidates.append(Path(base) / 'Microsoft' / 'Edge' / 'Application' / 'msedge.exe')
    elif name == 'firefox':
        for base in (program_files, program_files_x86):
            if base:
                candidates.append(Path(base) / 'Mozilla Firefox' / 'firefox.exe')

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def launch_browser_internal(
    url: str,
    browser: str,
    executable: str | None = None,
) -> None:
    name = str(browser or '').strip().lower()
    value = str(url or '').strip()

    if name == 'opera':
        launch_opera_internal(value, executable=executable)
        return

    prefixes = {
        'chrome': ('chrome://',),
        'edge': ('edge://',),
        'firefox': ('about:',),
    }
    if name not in prefixes:
        raise ValueError(f'Browser interno non supportato: {browser}')
    if not value.lower().startswith(prefixes[name]):
        raise ValueError(f'Route interna non valida per {browser}: {value}')

    browser_exe = executable or find_browser_executable(name)
    if not browser_exe:
        raise FileNotFoundError(
            f'{browser.capitalize()} non trovato. ComboCode conosce la route ma non trova il browser.'
        )

    subprocess.Popen([browser_exe])
    _navigate_internal_via_address_bar(value, name)


def _navigate_internal_via_address_bar(value: str, browser: str = 'opera') -> None:
    user32 = ctypes.windll.user32
    SW_RESTORE = 9
    SW_MAXIMIZE = 3
    KEYEVENTF_KEYUP = 0x0002
    VK_CONTROL = 0x11
    VK_MENU = 0x12
    VK_SHIFT = 0x10
    VK_L = 0x4C
    VK_RETURN = 0x0D

    def window_title(hwnd: int) -> str:
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ''
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value

    browser_name = str(browser or '').strip().lower()
    title_markers = {
        'opera': ('opera',),
        'chrome': ('google chrome',),
        'edge': ('microsoft edge',),
        'firefox': ('mozilla firefox',),
    }
    markers = title_markers.get(browser_name)
    if not markers:
        raise OSError(f'Browser non supportato per la navigazione interna: {browser}')

    def is_browser_window(hwnd: int) -> bool:
        title = window_title(hwnd).lower()
        return bool(
            hwnd
            and user32.IsWindowVisible(hwnd)
            and any(marker in title for marker in markers)
        )

    def find_window() -> int | None:
        foreground = user32.GetForegroundWindow()
        if is_browser_window(foreground):
            return int(foreground)

        found: list[int] = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        @callback_type
        def enum_proc(hwnd, _lparam):
            if is_browser_window(hwnd):
                found.append(int(hwnd))
                return False
            return True

        user32.EnumWindows(enum_proc, 0)
        return found[0] if found else None

    deadline = time.monotonic() + 6.0
    hwnd = None
    while time.monotonic() < deadline:
        hwnd = find_window()
        if hwnd:
            break
        time.sleep(0.05)

    if not hwnd:
        raise OSError(f'Finestra di {browser_name} non trovata.')

    show_cmd = SW_RESTORE if browser_name == 'opera' else SW_MAXIMIZE
    user32.ShowWindow(hwnd, show_cmd)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.12)

    if int(user32.GetForegroundWindow()) != int(hwnd):
        user32.keybd_event(VK_MENU, 0, 0, 0)
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.08)

    if int(user32.GetForegroundWindow()) != int(hwnd):
        raise OSError(f'Impossibile portare {browser_name} in primo piano.')

    def press(vk: int) -> None:
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.01)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    press(VK_L)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)

    for ch in value:
        code = int(user32.VkKeyScanW(ord(ch)))
        if code == -1:
            raise OSError(f'Carattere non digitabile nella route: {ch!r}')
        vk = code & 0xFF
        modifiers = (code >> 8) & 0xFF
        pressed = []
        if modifiers & 1:
            user32.keybd_event(VK_SHIFT, 0, 0, 0)
            pressed.append(VK_SHIFT)
        if modifiers & 2:
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            pressed.append(VK_CONTROL)
        if modifiers & 4:
            user32.keybd_event(VK_MENU, 0, 0, 0)
            pressed.append(VK_MENU)

        press(vk)

        for modifier in reversed(pressed):
            user32.keybd_event(modifier, 0, KEYEVENTF_KEYUP, 0)

    time.sleep(0.05)
    press(VK_RETURN)


def launch_opera_internal(url: str, executable: str | None = None) -> None:
    value = str(url or '').strip()
    if not value.lower().startswith(('opera://', 'chrome://', 'chrome-untrusted://')):
        raise ValueError(f'Route interna browser non valida: {value}')

    opera = executable or find_opera_executable()
    if not opera:
        raise FileNotFoundError(
            'Opera non trovato. ComboCode ha la route interna, ma non riesce a localizzare opera.exe.'
        )

    subprocess.Popen([opera])
    _navigate_internal_via_address_bar(value, 'opera')
