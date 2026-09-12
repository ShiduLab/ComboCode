# ComboCode Pack Schema — v1

Ogni file in `combocode/data/packs/*.json` contiene:

```json
{
  "name": "Nome pack",
  "version": "1.0.0",
  "updated": "2026-09-12",
  "goals": []
}
```

Ogni `goal` rappresenta **cosa vuole ottenere l'utente**:

```json
{
  "id": "net.connections",
  "name": "Connessioni di rete",
  "category": "Networking",
  "description": "Apre le connessioni di rete",
  "aliases": ["schede di rete", "ncpa"],
  "platform": "Windows 10/11",
  "routes": []
}
```

Ogni `route` rappresenta **come arrivarci**:

```json
{
  "kind": "RUN",
  "value": "ncpa.cpl",
  "handler": "control",
  "executable": true,
  "safety": "SAFE",
  "verified": "Windows built-in",
  "source": "https://...",
  "note": "Apre il pannello classico"
}
```

## Handler v1

- `none` — mostra/copia soltanto.
- `uri` — apre un URI Windows.
- `control` — invoca `control.exe <value>`.
- `exe` — avvia un eseguibile.
- `cmd_keep` — apre CMD e lascia la finestra aperta.
- `cmd_run` — esegue tramite CMD.
- `start` — apre percorso/variabile tramite associazione Windows.
- `explorer` — apre una route tramite Explorer.

## Safety

- `SAFE`
- `ELEVATED`
- `DESTRUCTIVE`
- `EXTERNAL`

La v1 non esegue automaticamente route `DESTRUCTIVE`.
