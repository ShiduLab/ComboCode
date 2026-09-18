from __future__ import annotations

import os
import shutil
import subprocess
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


def launch_opera_internal(url: str, executable: str | None = None) -> None:
    value = str(url or '').strip()
    if not value.lower().startswith(('opera://', 'chrome://', 'chrome-untrusted://')):
        raise ValueError(f'Route interna browser non valida: {value}')

    opera = executable or find_opera_executable()
    if not opera:
        raise FileNotFoundError(
            'Opera non trovato. ComboCode ha la route interna, ma non riesce a localizzare opera.exe.'
        )

    subprocess.Popen([opera, value])
