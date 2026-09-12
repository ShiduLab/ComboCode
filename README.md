# ComboCode — ShiduLab

> L'utente non deve ricordare **come** si raggiunge qualcosa.  
> Deve sapere soltanto **cosa vuole ottenere**.

**ComboCode** è un motore locale di accesso rapido a funzioni, pannelli, shortcut e comandi Windows.

La ricerca parte dall'intenzione: scrivi `Connessioni di rete`, `schede di rete`, `ncpa`, `ethernet` o `wifi` e ComboCode converge sullo stesso obiettivo mostrando le route disponibili.

## v1 — cosa c'è già

- 92 obiettivi / 106 route iniziali.
- Ricerca istantanea per nome, alias, descrizione, categoria e stringa di comando.
- Route `HOTKEY`, `RUN` e `CMD`, con predisposizione per URI, PowerShell e altri tipi.
- Apertura/esecuzione diretta delle route compatibili su Windows.
- Copia immediata della stringa.
- Preferiti persistenti in SQLite locale.
- Ricerca e navigazione pensate prima di tutto per la tastiera.
- Filtro per categoria.
- Esportazione del nodo selezionato come nota Markdown pronta per Obsidian.
- Link alla fonte associata alla route.
- Classificazione `SAFE`, `ELEVATED`, `DESTRUCTIVE`.
- Database a pacchetti JSON, espandibile senza riscrivere il motore.

## Due prove immediate

Cerca:

`Esegui`

Risposta principale:

`HOTKEY — WIN + R`

Cerca:

`Connessioni di rete`

Tra le route:

`RUN — ncpa.cpl`

`CMD — control netconnections`

`RUN — ms-settings:network-advancedsettings`

## Tastiera

| Tasto | Azione |
|---|---|
| `Ctrl+K` / `Ctrl+L` | focus sulla ricerca |
| `↓` | dai risultati della ricerca alla lista |
| `Invio` | apri/esegui la route selezionata |
| `Ctrl+C` | copia la route |
| `Ctrl+F` | preferito |
| `Ctrl+M` | esporta il nodo come Markdown Obsidian |
| `F1` | aiuto |
| `Esc` | chiudi |

## Database

Il primo pack è:

`combocode/data/packs/windows_core.json`

Ogni obiettivo può avere più route. Esempio concettuale:

```text
Connessioni di rete
├── RUN  ncpa.cpl
├── CMD  control netconnections
└── RUN  ms-settings:network-advancedsettings
```

È questo il principio strutturale di ComboCode: **stesso obiettivo, più route**.

## Sicurezza

ComboCode distingue il tipo di route prima dell'esecuzione.

- `SAFE`: apertura di pannelli, strumenti o comandi informativi.
- `ELEVATED`: può richiedere privilegi amministrativi; ComboCode chiede conferma.
- `DESTRUCTIVE`: previsto dal modello dati ma non viene eseguito automaticamente.

Le HOTKEY sono mostrate e copiabili, non simulate dal programma.

## Obsidian

Il pulsante **ESPORTA .MD** produce una nota con frontmatter, route e primi WikiLink, per inserirla direttamente nel futuro `[[OlogrammIo]]`.

## Avvio da sorgente

Richiede Python 3.10+ su Windows; Tkinter e SQLite sono già nella distribuzione standard di Python.

```bash
python main.py
```

## EXE con GitHub Actions

Il repository include `.github/workflows/windows.yml`.

Dopo il push su `main`, Actions:

1. esegue i test;
2. installa PyInstaller;
3. genera `ComboCode v1.exe` senza console;
4. pubblica l'artifact `ComboCode-Windows-v1`.

## Fonti iniziali del pack Windows

Il primo dataset usa come riferimenti principali la documentazione Microsoft su:

- shortcut Windows;
- schema URI `ms-settings:`;
- Windows command-line reference.

Il database è volutamente versionato: una route potrà essere segnata come verificata, legacy, deprecata o dipendente dalla versione.

## Prossimo giro di smussatura

La v1 serve a mettere le mani sul concept. I candidati naturali per v2 sono:

- editor interno per aggiungere/modificare nodi e alias;
- import/export di pack ComboCode;
- pacchetti Word, Excel, Obsidian, VS Code, Git e ChatGPT;
- hotkey globale richiamabile sopra qualunque programma;
- ranking `più rapido / più universale / legacy / admin`;
- verifica automatica della disponibilità di comandi e applicazioni;
- modalità portable completa;
- tema e identità grafica ShiduLab.

---

**ShiduLab non programma, indica.**
