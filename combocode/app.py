from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return base / relative


def main() -> None:
    from .engine import KnowledgeBase
    from .storage import UserStore
    from .ui import ComboCodeUI

    kb = KnowledgeBase.from_pack_dir(resource_path('combocode/data/packs'))
    store = UserStore()
    app = ComboCodeUI(kb, store)
    app.run()


if __name__ == '__main__':
    main()
