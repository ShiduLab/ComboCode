from __future__ import annotations

from pathlib import Path


def goal_to_markdown(goal: dict) -> str:
    aliases = goal.get('aliases', [])
    lines = [
        '---',
        'type: ComboCode',
        f'category: "{goal.get("category", "")}"',
        f'platform: "{goal.get("platform", "Windows")}"',
        'aliases:',
    ]
    for alias in aliases:
        lines.append(f'  - "{alias}"')
    lines += [
        '---',
        '',
        f'# {goal.get("name", "ComboCode")}',
        '',
        goal.get('description', ''),
        '',
        '## Route',
        '',
    ]
    for route in goal.get('routes', []):
        lines += [
            f'### {route.get("kind", "ROUTE")}',
            '',
            f'`{route.get("value", "")}`',
            '',
        ]
        note = route.get('note')
        if note:
            lines += [note, '']
    lines += [
        '## Collegamenti',
        '',
        '[[ComboCode]]',
        f'[[ComboCode {goal.get("category", "Windows")}]]',
        '[[ShiduLab]]',
        '',
    ]
    return '\n'.join(lines)


def export_goal(goal: dict, target: Path) -> None:
    target.write_text(goal_to_markdown(goal), encoding='utf-8')
