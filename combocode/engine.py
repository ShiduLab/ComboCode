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


@dataclass(frozen=True)
class RouteRow:
    goal: dict
    route_index: int
    route: dict


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
        keywords = [normalize(x) for x in goal.get('keywords', [])]
        description = normalize(goal.get('description', ''))
        category = normalize(goal.get('category', ''))
        route_values = [normalize(r.get('value', '')) for r in goal.get('routes', [])]
        route_kinds = [normalize(r.get('kind', '')) for r in goal.get('routes', [])]
        route_notes = [normalize(r.get('note', '')) for r in goal.get('routes', [])]
        blob = ' '.join([
            name,
            *aliases,
            *keywords,
            description,
            category,
            *route_values,
            *route_kinds,
            *route_notes,
        ])
        return {
            'name': name,
            'aliases': aliases,
            'keywords': keywords,
            'blob': blob,
        }

    def categories(self) -> list[str]:
        return sorted({g.get('category', 'Altro') for g in self.goals}, key=str.lower)

    def route_kinds(self) -> list[str]:
        return sorted(
            {r.get('kind', 'ROUTE') for g in self.goals for r in g.get('routes', [])},
            key=str.lower,
        )

    def stats(self) -> dict[str, int]:
        stats: dict[str, int] = {
            'goals': len(self.goals),
            'routes': 0,
        }
        for goal in self.goals:
            for route in goal.get('routes', []):
                stats['routes'] += 1
                kind = route.get('kind', 'ROUTE')
                stats[kind] = stats.get(kind, 0) + 1
        return stats

    def search(
        self,
        query: str,
        category: str | None = None,
        limit: int | None = 80,
    ) -> list[SearchHit]:
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
        return hits if limit is None else hits[:limit]

    def route_rows(
        self,
        query: str = '',
        category: str | None = None,
        kind: str | None = None,
        sort_by: str = 'goal',
        descending: bool = False,
    ) -> list[RouteRow]:
        hits = self.search(query, category, limit=None)
        rows: list[RouteRow] = []
        for hit in hits:
            goal = hit.goal
            for idx, route in enumerate(goal.get('routes', [])):
                if kind and kind != 'TUTTI' and route.get('kind') != kind:
                    continue
                rows.append(RouteRow(goal=goal, route_index=idx, route=route))

        def value(row: RouteRow):
            mapping = {
                'goal': row.goal.get('name', ''),
                'kind': row.route.get('kind', ''),
                'value': row.route.get('value', ''),
                'cat': row.goal.get('category', ''),
                'safety': row.route.get('safety', 'SAFE'),
                'verified': row.route.get('verified', ''),
            }
            primary = normalize(str(mapping.get(sort_by, mapping['goal'])))
            return (
                primary,
                normalize(row.goal.get('name', '')),
                normalize(row.route.get('kind', '')),
                normalize(row.route.get('value', '')),
            )

        rows.sort(key=value, reverse=descending)
        return rows

    @staticmethod
    def _score(q: str, q_tokens: list[str], idx: dict) -> float:
        name = idx['name']
        aliases = idx['aliases']
        keywords = idx['keywords']
        blob = idx['blob']
        score = 0.0

        if q == name:
            score += 120
        if q in aliases:
            score += 112
        if q in keywords:
            score += 104
        if name.startswith(q):
            score += 80
        if any(a.startswith(q) for a in aliases):
            score += 72
        if any(k.startswith(q) for k in keywords):
            score += 68
        if q in name:
            score += 62
        if any(q in a for a in aliases):
            score += 54
        if any(q in k for k in keywords):
            score += 50
        if q in blob:
            score += 40

        for token in q_tokens:
            if token == name:
                score += 25
            elif token in name:
                score += 16
            elif any(token in a for a in aliases):
                score += 13
            elif any(token in k for k in keywords):
                score += 11
            elif token in blob:
                score += 8
            else:
                return 0.0

        ratio = SequenceMatcher(None, q, name).ratio()
        if ratio >= 0.55:
            score += ratio * 25
        else:
            best_related = max(
                [*(SequenceMatcher(None, q, a).ratio() for a in aliases),
                 *(SequenceMatcher(None, q, k).ratio() for k in keywords)],
                default=0.0,
            )
            if best_related >= 0.62:
                score += best_related * 20
        return score
