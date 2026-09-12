from __future__ import annotations

import os
import subprocess
import sys
import time


class ExecutionError(RuntimeError):
    pass


def _send_hotkey(combo: str) -> None:
    if sys.platform != 'win32':
        raise ExecutionError('Le hotkey possono essere inviate direttamente solo su Windows.')

    import ctypes

    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002

    aliases = {
        'CTRL': 0x11,
        'CONTROL': 0x11,
        'SHIFT': 0x10,
        'ALT': 0x12,
        'WIN': 0x5B,
        'WINDOWS': 0x5B,
        'TAB': 0x09,
        'ENTER': 0x0D,
        'INVIO': 0x0D,
        'ESC': 0x1B,
        'ESCAPE': 0x1B,
        'SPACE': 0x20,
        'SPAZIO': 0x20,
        'BACKSPACE': 0x08,
        'INSERT': 0x2D,
        'INS': 0x2D,
        'PRTSCN': 0x2C,
        'PRINT SCREEN': 0x2C,
        'PAUSE': 0x13,
        'NUM LOCK': 0x90,
        'CAPS LOCK': 0x14,
        'DELETE': 0x2E,
        'DEL': 0x2E,
        'HOME': 0x24,
        'END': 0x23,
        'PGUP': 0x21,
        'PGDN': 0x22,
        'FRECCIA SINISTRA': 0x25,
        'LEFT': 0x25,
        'FRECCIA SU': 0x26,
        'UP': 0x26,
        'FRECCIA DESTRA': 0x27,
        'RIGHT': 0x27,
        'FRECCIA GIÙ': 0x28,
        'FRECCIA GIU': 0x28,
        'DOWN': 0x28,
        '.': 0xBE,
        ',': 0xBC,
        ';': 0xBA,
        ':': 0xBA,
        '/': 0xBF,
        '\\': 0xDC,
        '-': 0xBD,
        '+': 0xBB,
        '=': 0xBB,
        '[': 0xDB,
        ']': 0xDD,
        "'": 0xDE,
        '`': 0xC0,
    }

    for n in range(1, 25):
        aliases[f'F{n}'] = 0x6F + n

    parts = [p.strip().upper() for p in combo.split('+') if p.strip()]
    if not parts:
        raise ExecutionError('Hotkey vuota.')

    keys = []
    for part in parts:
        if part in aliases:
            keys.append(aliases[part])
        elif len(part) == 1 and part.isalnum():
            keys.append(ord(part))
        else:
            raise ExecutionError(f'Tasto non riconosciuto nella combinazione: {part}')

    for vk in keys:
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.015)
    for vk in reversed(keys):
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.015)


def _run_elevated_cmd(value: str, keep_open: bool) -> None:
    import ctypes
    verb = 'runas'
    exe = 'cmd.exe'
    switch = '/k' if keep_open else '/c'
    params = f'{switch} {value}'
    result = ctypes.windll.shell32.ShellExecuteW(None, verb, exe, params, None, 1)
    if int(result) <= 32:
        raise ExecutionError(f'Avvio elevato non riuscito (codice {result}).')


def execute_route(route: dict) -> None:
    if sys.platform != 'win32':
        raise ExecutionError('L’esecuzione diretta è disponibile solo su Windows.')

    handler = route.get('handler', 'none')
    value = str(route.get('value', '')).strip()
    kind = str(route.get('kind', '')).upper()
    safety = str(route.get('safety', 'SAFE')).upper()

    if not value:
        raise ExecutionError('Questa route non contiene un comando eseguibile.')

    try:
        if kind == 'HOTKEY':
            _send_hotkey(value)
            return

        if kind in {'MOUSE', 'KEY+MOUSE', 'TASTIERA+MOUSE'} or handler == 'manual':
            raise ExecutionError(f'Gesto manuale: {value}')

        # Route marcate ELEVATED: UAC, poi esecuzione.
        if safety == 'ELEVATED':
            _run_elevated_cmd(value, keep_open=(kind == 'CMD'))
            return

        # Handler espliciti del database.
        if handler == 'uri':
            os.startfile(value)  # type: ignore[attr-defined]
        elif handler == 'control':
            subprocess.Popen(['control.exe', value])
        elif handler == 'control_raw':
            subprocess.Popen(['control.exe', *value.split()])
        elif handler == 'exe':
            subprocess.Popen([value])
        elif handler == 'exe_args':
            subprocess.Popen(route.get('argv', [value]))
        elif handler == 'explorer':
            subprocess.Popen(['explorer.exe', value])
        elif handler == 'cmd_keep':
            subprocess.Popen(['cmd.exe', '/k', value])
        elif handler == 'cmd_run':
            subprocess.Popen(['cmd.exe', '/c', value])
        elif handler == 'start':
            os.startfile(os.path.expandvars(value))  # type: ignore[attr-defined]
        elif handler == 'powershell' or kind == 'POWERSHELL':
            subprocess.Popen(['powershell.exe', '-NoProfile', '-Command', value])
        else:
            # Fallback intenzionale v4:
            # le voci importate/legacy non restano più solo informative.
            if kind == 'CMD':
                subprocess.Popen(['cmd.exe', '/k', value])
            elif value.lower().startswith(('http://', 'https://', 'ms-settings:')):
                os.startfile(value)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(['cmd.exe', '/c', value])
    except OSError as exc:
        raise ExecutionError(str(exc)) from exc
