from __future__ import annotations

import os
import sqlite3
from pathlib import Path


class UserStore:
    def __init__(self):
        base = Path(os.getenv('APPDATA') or Path.home()) / 'ShiduLab' / 'ComboCode'
        base.mkdir(parents=True, exist_ok=True)
        self.path = base / 'combocode.db'
        self.conn = sqlite3.connect(self.path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS favorites (goal_id TEXT PRIMARY KEY)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS history (goal_id TEXT, used_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
        self.conn.commit()

    def is_favorite(self, goal_id: str) -> bool:
        row = self.conn.execute('SELECT 1 FROM favorites WHERE goal_id=?', (goal_id,)).fetchone()
        return bool(row)

    def toggle_favorite(self, goal_id: str) -> bool:
        if self.is_favorite(goal_id):
            self.conn.execute('DELETE FROM favorites WHERE goal_id=?', (goal_id,))
            state = False
        else:
            self.conn.execute('INSERT OR IGNORE INTO favorites(goal_id) VALUES (?)', (goal_id,))
            state = True
        self.conn.commit()
        return state

    def add_history(self, goal_id: str) -> None:
        self.conn.execute('INSERT INTO history(goal_id) VALUES (?)', (goal_id,))
        self.conn.execute('DELETE FROM history WHERE rowid NOT IN (SELECT rowid FROM history ORDER BY used_at DESC LIMIT 300)')
        self.conn.commit()
