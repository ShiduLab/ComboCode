from __future__ import annotations

import json
import os
import sqlite3
import uuid
from pathlib import Path


class UserStore:
    def __init__(self, base: Path | None = None):
        self.base = Path(base) if base is not None else Path(os.getenv('APPDATA') or Path.home()) / 'ShiduLab' / 'ComboCode'
        self.base.mkdir(parents=True, exist_ok=True)
        self.path = self.base / 'combocode.db'
        self.shortcuts_path = self.base / 'user_shortcuts.json'
        self.conn = sqlite3.connect(self.path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS favorites (goal_id TEXT PRIMARY KEY)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS history (goal_id TEXT, used_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
        self.conn.commit()
        if not self.shortcuts_path.exists():
            self._write_shortcuts([])

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

    def load_user_goals(self) -> list[dict]:
        try:
            data = json.loads(self.shortcuts_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return []
        goals = data.get('goals', []) if isinstance(data, dict) else []
        return [g for g in goals if isinstance(g, dict) and g.get('id') and g.get('name')]

    def _write_shortcuts(self, goals: list[dict]) -> None:
        payload = {
            'format': 'ComboCode user shortcuts',
            'version': 1,
            'goals': goals,
        }
        tmp = self.shortcuts_path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        tmp.replace(self.shortcuts_path)

    def save_user_goals(self, goals: list[dict]) -> None:
        self._write_shortcuts(goals)

    def upsert_user_goal(self, goal: dict) -> dict:
        goal = dict(goal)
        goal.setdefault('id', f'user.{uuid.uuid4().hex}')
        goal['origin'] = 'user'
        goal['category'] = 'MIE'
        goals = self.load_user_goals()
        replaced = False
        for idx, existing in enumerate(goals):
            if existing.get('id') == goal['id']:
                goals[idx] = goal
                replaced = True
                break
        if not replaced:
            goals.append(goal)
        self._write_shortcuts(goals)
        return goal

    def delete_user_goal(self, goal_id: str) -> bool:
        goals = self.load_user_goals()
        new_goals = [g for g in goals if g.get('id') != goal_id]
        if len(new_goals) == len(goals):
            return False
        self._write_shortcuts(new_goals)
        self.conn.execute('DELETE FROM favorites WHERE goal_id=?', (goal_id,))
        self.conn.commit()
        return True

    def export_user_shortcuts(self, target: Path) -> None:
        target.write_text(self.shortcuts_path.read_text(encoding='utf-8'), encoding='utf-8')

    def import_user_shortcuts(self, source: Path, merge: bool = True) -> int:
        data = json.loads(source.read_text(encoding='utf-8'))
        incoming = data.get('goals', []) if isinstance(data, dict) else []
        incoming = [g for g in incoming if isinstance(g, dict) and g.get('name') and g.get('routes')]
        for g in incoming:
            g.setdefault('id', f'user.{uuid.uuid4().hex}')
            g['origin'] = 'user'
            g['category'] = 'MIE'
        if merge:
            current = {g.get('id'): g for g in self.load_user_goals()}
            for g in incoming:
                current[g['id']] = g
            self._write_shortcuts(list(current.values()))
        else:
            self._write_shortcuts(incoming)
        return len(incoming)
