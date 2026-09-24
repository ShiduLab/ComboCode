# ComboCode — ShiduLab

> L'utente non deve ricordare **come** si raggiunge qualcosa.  
> Deve sapere soltanto **cosa vuole ottenere**.

**Salto attuale: J8.0.2**

**Download Windows:** [ComboCode v8.0.2](https://github.com/ShiduLab/ComboCode/releases/tag/v8.0.2) 
<img width="1920" height="1082" alt="ComboCode v8 2 J" src="https://github.com/user-attachments/assets/cfc4465d-e931-45d3-93fb-b0b39374a7e6" />



ComboCode è un motore locale, keyboard-first, per trovare e usare shortcut, comandi, pannelli e route di accesso a Windows e alle applicazioni.

L'idea centrale è semplice:

**un obiettivo → più route**

Per esempio, cercando `Connessioni di rete`, ComboCode può proporre più strade per arrivare allo stesso punto: RUN, CMD, URI o altre route disponibili.

### J8.0.2

Correzioni pubbliche:
- corretto il form **MIE**: i campi di inserimento ricevono correttamente focus al primo rendering, senza dover minimizzare e massimizzare la finestra;
- aggiunta la route **Impostazioni screen saver**: `control desk.cpl,,@screensaver`.

## Stato archivio J8

Archivio standard incluso:

- **861 obiettivi**
- **941 route**
- **667 HOTKEY**
- **149 RUN**
- **125 CMD**

A questo archivio si aggiungono le shortcut personali create dall'utente nella pagina **MIE**.

## Interfaccia

ComboCode ha tre aree principali:

### CERCA

Per quando sai **cosa vuoi ottenere**.

La ricerca indicizza:
- obiettivo;
- alias;
- descrizione;
- categoria;
- keyword;
- comando/stringa;
- note;
- contesto.

La `×` a destra del campo ricerca azzera immediatamente la query.

Il menu Categoria usa un menu popup dedicato, non il vecchio `ttk.Combobox`.

### TUTTI

È l'atlante completo dell'archivio.

Permette di:
- vedere tutte le route;
- filtrare per testo;
- filtrare per tipo;
- filtrare per categoria;
- ordinare cliccando sulle intestazioni;
- invertire crescente/decrescente con un secondo click.

### MIE

Archivio personale dell'utente.

Permette di:
- aggiungere shortcut;
- modificare;
- eliminare;
- cercare;
- duplicare una route standard e personalizzarla;
- importare/esportare JSON.

Le personalizzazioni vengono salvate fuori dall'EXE in:

`%APPDATA%\ShiduLab\ComboCode\user_shortcuts.json`

Quindi non vengono perse aggiornando ComboCode.

## Aggiungi shortcut

Campi disponibili:

- **A cosa serve**
- **Tipo**
- **Tasti / stringa / gesto**
- **Contesto**
- **Alias**
- **Sicurezza**
- **Note**

Tipi previsti:

- `HOTKEY`
- `MOUSE`
- `KEY+MOUSE`
- `RUN`
- `CMD`
- `POWERSHELL`
- `URI`
- `APP`
- `ALTRO`

Questo permette di registrare anche shortcut personali di Windows o di qualunque programma, oltre a gesture tipo `CTRL + rotellina`.

## Windows

Il catalogo Windows comprende shortcut contestuali per:

- modifica testo;
- desktop e comandi generali;
- combinazioni col tasto WIN;
- Prompt dei comandi;
- finestre di dialogo;
- Esplora file;
- desktop virtuali;
- barra delle applicazioni;
- Impostazioni;
- Accessibilità;
- Lente d'ingrandimento.

Sono inoltre presenti route RUN, CMD, CPL, MSC, URI e materiale storico ESEGUI/DOS.

Le voci legacy restano distinguibili dalle route moderne.

## Browser

Sono presenti pack separati per:

- Browser comuni;
- Opera;
- Google Chrome;
- Microsoft Edge;
- Mozilla Firefox.

Le stesse combinazioni possono comparire in più browser quando il contesto cambia.

Il contesto applicativo è parte del dato: ComboCode non considera una shortcut soltanto come una sequenza di tasti.

## Esecuzione

`APRI / ESEGUI` prova a lanciare la route selezionata.

- `SAFE`: esecuzione diretta;
- `ELEVATED`: conferma, poi richiesta privilegi quando necessaria;
- `DESTRUCTIVE`: conferma esplicita prima dell'esecuzione.

Le HOTKEY supportate possono essere inviate direttamente da ComboCode su Windows.

Le gesture `MOUSE` e `KEY+MOUSE` vengono archiviate e mostrate come istruzioni operative.

## Grafica

- tema chiaro/scuro adattato al sistema;
- scaling/DPI Windows;
- icona ComboCode nell'EXE, taskbar e finestra;
- **Botolo + ShiduLab in basso a destra**;
- testo ShiduLab adattato ai colori del tema.

## Shortcut interne ComboCode

| Tasto | Azione |
|---|---|
| `Ctrl+K` / `Ctrl+L` | focus ricerca |
| `Ctrl+1` | CERCA |
| `Ctrl+2` | TUTTI |
| `Ctrl+3` | MIE |
| `Ctrl+Shift+A` | Aggiungi shortcut |
| `↓` | passa alla lista |
| `Invio` | Apri / Esegui |
| `Ctrl+C` | copia route |
| `Ctrl+F` | preferito |
| `Ctrl+M` | esporta Markdown |
| `F1` | aiuto |
| `Esc` | chiudi |

## Obsidian

ComboCode può esportare una voce come nota Markdown con frontmatter e WikiLink, pronta per essere integrata in un vault Obsidian.

La documentazione del progetto è in `docs/`.

## Fonti e provenienza

Le fonti moderne sono elencate in:

`docs/SOURCES.md`

L'archivio storico fornito durante lo sviluppo è documentato in:

`docs/USER_ARCHIVE_SOURCES.md`

Tra le fonti storiche:
- `comandi Esegui_dos.docx`
- `Comandi Esegui_Dos2.docx`
- `Comandi Esegui_Dos3.docx`

## Avvio da sorgente

Richiede Python 3.10+ su Windows.

```bash
python main.py
```

## Build EXE con GitHub Actions

Dopo il push su `main`, GitHub Actions:

1. esegue i test;
2. installa PyInstaller;
3. genera **`ComboCode J8.0.1.exe`**;
4. pubblica l'artifact **`ComboCode-Windows-J8.0.1`**.

## Cronologia


### v8.0.1 — Fix build Windows

- chiusura esplicita della connessione SQLite;
- test delle shortcut personali compatibili con il file locking di Windows;
- chiusura del database alla terminazione della GUI;
- GitHub Actions aggiornate a `actions/checkout@v5` e `actions/setup-python@v6` per Node 24.


### v8 — Personalizzazione

- nuova pagina **MIE**;
- `+ AGGIUNGI SHORTCUT`;
- tipi MOUSE e KEY+MOUSE;
- contesto personalizzabile;
- modifica/elimina;
- import/export JSON;
- duplicazione di route standard;
- persistenza separata dagli aggiornamenti.

### v7 — Browser

- Browser comuni;
- Opera;
- Chrome;
- Edge;
- Firefox;
- centinaia di route di navigazione e controllo browser.

### v6 — Shortcut Windows

- ampliamento massiccio delle scorciatoie da tastiera Windows;
- catalogazione per contesto;
- accessibilità e navigazione incluse.

### v5 — Menu a tendina

- eliminato `ttk.Combobox`;
- introdotti `Menubutton + Menu` per i filtri.

### v4 — Smussature operative

- Botolo + ShiduLab spostati a destra;
- `×` nella ricerca;
- ordinamento CERCA/TUTTI;
- esecuzione route legacy sbloccata con conferme di sicurezza.

### v3 — GUI e archivio

- GUI adattiva chiaro/scuro;
- DPI/scaling;
- pagina TUTTI reale;
- ordinamento colonne;
- import archivio storico.

### v2 — Primo ampliamento

- ricerca semantica più ampia;
- famiglia Tastiera;
- archivio CMD ampliato;
- pagina TUTTI.

### v1 — Primo prototipo operativo

- ricerca per intenzione;
- HOTKEY / RUN / CMD;
- preferiti;
- copia;
- export Markdown;
- database a pack JSON.

---

**ShiduLab non programma, indica.**
