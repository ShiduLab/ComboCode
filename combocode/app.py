from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return base / relative


def _prepare_windows_process() -> None:
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ShiduLab.ComboCode.v7')
    except Exception:
        pass
    try:
        import ctypes
        # Per-monitor DPI awareness v2 when available.
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass


def main() -> None:
    from .engine import KnowledgeBase
    from .storage import UserStore
    from .ui import ComboCodeUI

    _prepare_windows_process()
    kb = KnowledgeBase.from_pack_dir(resource_path('combocode/data/packs'))
    store = UserStore()
    app = ComboCodeUI(
        kb,
        store,
        icon_png=resource_path('assets/combocode-icon.png'),
        icon_ico=resource_path('assets/combocode-icon.ico'),
        brand_png=resource_path('assets/shidulab-botolo-mark.png'),
    )
    app.run()


if __name__ == '__main__':
    main()
