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


def _navigate_internal_via_address_bar(value: str) -> None:
    user32 = ctypes.windll.user32
    SW_RESTORE = 9
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

    def is_opera_window(hwnd: int) -> bool:
        return bool(hwnd and user32.IsWindowVisible(hwnd) and 'opera' in window_title(hwnd).lower())

    def find_window() -> int | None:
        foreground = user32.GetForegroundWindow()
        if is_opera_window(foreground):
            return int(foreground)

        found: list[int] = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        @callback_type
        def enum_proc(hwnd, _lparam):
            if is_opera_window(hwnd):
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
        raise OSError('Finestra di Opera non trovata.')

    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.12)

    if int(user32.GetForegroundWindow()) != int(hwnd):
        user32.keybd_event(VK_MENU, 0, 0, 0)
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.08)

    if int(user32.GetForegroundWindow()) != int(hwnd):
        raise OSError('Impossibile portare Opera in primo piano.')

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
    _navigate_internal_via_address_bar(value)
