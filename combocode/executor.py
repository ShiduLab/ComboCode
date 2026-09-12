from __future__ import annotations

import os
import subprocess
import sys


class ExecutionError(RuntimeError):
    pass


def execute_route(route: dict) -> None:
    if sys.platform != 'win32':
        raise ExecutionError('L’esecuzione diretta è disponibile solo su Windows.')

    if not route.get('executable', False):
        raise ExecutionError('Questa voce è informativa/copiabile e non viene eseguita da ComboCode.')

    safety = route.get('safety', 'SAFE')
    if safety == 'DESTRUCTIVE':
        raise ExecutionError('I comandi distruttivi non vengono eseguiti automaticamente.')

    handler = route.get('handler', 'none')
    value = route.get('value', '')

    try:
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
        else:
            raise ExecutionError('Nessun esecutore associato a questa route.')
    except OSError as exc:
        raise ExecutionError(str(exc)) from exc
