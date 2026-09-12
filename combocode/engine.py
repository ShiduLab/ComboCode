from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r'[^a-z0-9+#.:/_-]+', ' ', text)
    return ' '.join(text.split())


@dataclass(frozen=True)
class SearchHit:
    score: float
    goal: dict


class KnowledgeBase:
    def __init__(self, goals: Iterable[dict]):
        self.goals = list(goals)
        self.by_id = {g['id']: g for g in self.goals}
        self._index = {g['id']: self._build_index(g) for g in self.goals}

    @classmethod
    def from_pack_dir(cls, pack_dir: Path) -> 'KnowledgeBase':
        goals = []
        for path in sorted(pack_dir.glob('*.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            goals.extend(data.get('goals', []))
        return cls(goals)

    @staticmethod
    def _build_index(goal: dict) -> dict:
        name = normalize(goal.get('name', ''))
        aliases = [normalize(x) for x in goal.get('aliases', [])]
        description = normalize(goal.get('description', ''))
        category = normalize(goal.get('category', ''))
        route_values = [normalize(r.get('value', '')) for r in goal.get('routes', [])]
        route_kinds = [normalize(r.get('kind', '')) for r in goal.get('routes', [])]
        blob = ' '.join([name, *aliases, description, category, *route_values, *route_kinds])
        return {
            'name': name,
            'aliases': aliases,
            'blob': blob,
        }

    def categories(self) -> list[str]:
        return sorted({g.get('category', 'Altro') for g in self.goals}, key=str.lower)

    def search(self, query: str, category: str | None = None, limit: int = 80) -> list[SearchHit]:
        q = normalize(query)
        q_tokens = q.split()
        hits: list[SearchHit] = []
        for goal in self.goals:
            if category and category != 'Tutte' and goal.get('category') != category:
                continue
            idx = self._index[goal['id']]
            if not q:
                score = 1.0
            else:
                score = self._score(q, q_tokens, idx)
                if score <= 0:
                    continue
            hits.append(SearchHit(score=score, goal=goal))
        hits.sort(key=lambda h: (-h.score, h.goal.get('name', '').lower()))
        return hits[:limit]

    @staticmethod
    def _score(q: str, q_tokens: list[str], idx: dict) -> float:
        name = idx['name']
        aliases = idx['aliases']
        blob = idx['blob']
        score = 0.0

        if q == name:
            score += 120
        if q in aliases:
            score += 112
        if name.startswith(q):
            score += 80
        if any(a.startswith(q) for a in aliases):
            score += 72
        if q in name:
            score += 62
        if any(q in a for a in aliases):
            score += 54
        if q in blob:
            score += 40

        for token in q_tokens:
            if token == name:
                score += 25
            elif token in name:
                score += 16
            elif any(token in a for a in aliases):
                score += 13
            elif token in blob:
                score += 8
            else:
                return 0.0

        ratio = SequenceMatcher(None, q, name).ratio()
        if ratio >= 0.55:
            score += ratio * 25
        else:
            best_alias = max((SequenceMatcher(None, q, a).ratio() for a in aliases), default=0.0)
            if best_alias >= 0.62:
                score += best_alias * 20
        return score
