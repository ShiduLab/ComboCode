from __future__ import annotations


def confirmation_for_route(route: dict) -> tuple[str, str] | None:
    safety = str(route.get('safety', 'SAFE')).upper()
    if safety == 'SAFE':
        return None

    value = str(route.get('value', '')).strip()
    warning = str(route.get('warning', '')).strip()

    if safety == 'ELEVATED':
        title = 'ComboCode — Conferma privilegi'
        detail = warning or 'Questa route può richiedere privilegi amministrativi.'
    elif safety == 'CAUTION':
        title = 'ComboCode — ATTENZIONE'
        detail = warning or (
            'Questa route apre una funzione avanzata. '
            'Verifica di sapere cosa comporta prima di eseguirla.'
        )
    elif safety == 'DESTRUCTIVE':
        title = 'ComboCode — PERICOLO'
        detail = warning or 'Questa route può causare perdita di dati, crash o instabilità.'
    else:
        title = 'ComboCode — Conferma'
        detail = warning or f'Livello di sicurezza non riconosciuto: {safety}.'

    return title, f'{detail}\n\nRoute:\n{value}\n\nVuoi eseguire davvero?'
