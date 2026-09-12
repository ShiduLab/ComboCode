# ComboCode — ShiduLab

> L'utente non deve ricordare **come** si raggiunge qualcosa.  
> Deve sapere soltanto **cosa vuole ottenere**.

**ComboCode** è un motore locale di accesso rapido a funzioni, pannelli, shortcut e comandi Windows.

La ricerca parte dall'intenzione: scrivi `Connessioni di rete`, `schede di rete`, `ncpa`, `ethernet` o `wifi` e ComboCode converge sullo stesso obiettivo mostrando le route disponibili.


## v4 — smussature dal test reale

- Botolo + **ShiduLab** spostati in basso a destra.
- Scritta ShiduLab renderizzata dalla GUI: segue automaticamente i colori del tema.
- X nella casella di ricerca per azzerare subito la query.
- Filtro categoria in alto collegato direttamente al motore di ricerca.
- Ordinamento cliccabile anche nella pagina **CERCA** (`Obiettivo`, `Categoria`), crescente/decrescente.
- Ordinamento della pagina **TUTTI** mantenuto su tutte le colonne.
- `APRI / ESEGUI` non blocca più le route importate/legacy.
- Route `ELEVATED` e `DESTRUCTIVE`: conferma esplicita, poi esecuzione.
- Le HOTKEY possono essere inviate direttamente da ComboCode su Windows.
- Le route archivistiche non riconosciute usano un fallback CMD: se Windows le supporta vengono eseguite, altrimenti restituiscono l'errore reale del sistema.

## v3 — GUI moderna + archivio vero

La v3 nasce direttamente dalle prime prove d'uso reali.

- GUI ridisegnata con `ttk` moderno: niente look Win95.
- Tema **automatico Sistema**: segue il tema chiaro/scuro di Windows anche se viene cambiato mentre ComboCode è aperto.
- DPI/scaling Windows gestito in modalità per-monitor quando disponibile.
- Icona ComboCode forzata anche nella **barra del titolo**, oltre a EXE e taskbar.
- **Botolo + ShiduLab** canonici, trasparenti, sempre in basso a sinistra.
- La pagina **TUTTI** ha filtri propri e non eredita più la categoria della pagina CERCA: a filtri azzerati mostra realmente l'intero archivio.
- Tutte le intestazioni di TUTTI sono cliccabili: `Obiettivo`, `Tipo`, `Comando`, `Categoria`, `Sicurezza`, `Verifica`.
- Secondo click sulla stessa intestazione inverte crescente/decrescente.
- Archivio ampliato con le liste storiche ESEGUI/DOS fornite dall'utente.
- Le voci storiche non vengono corrette o rese eseguibili di nascosto: sono marcate `LEGACY` o `da verificare`.

### Dimensione archivio v3

- **290 obiettivi**
- **308 route**
- **149 RUN**
- **125 CMD**
- **34 HOTKEY**

## Ricerca e archivio sono due cose diverse

### CERCA

Serve quando sai **cosa vuoi ottenere**.

La ricerca usa:
- nome;
- alias;
- descrizione;
- categoria;
- keyword;
- stringa del comando;
- note della route.

### TUTTI

È l'atlante completo di ciò che ComboCode conosce.

Ha filtri indipendenti per:
- testo;
- tipo;
- categoria.

`AZZERA` riporta immediatamente alla vista completa.

## Esempi

Cerca:

`Esegui`

Risposta:

`HOTKEY — WIN + R`

Cerca:

`Connessioni di rete`

Tra le route:

`RUN — ncpa.cpl`

`CMD — control netconnections`

`RUN — ms-settings:network-advancedsettings`

Cerca:

`tastiera`

Trovi, fra le altre:
- Tastiera su schermo;
- Impostazioni digitazione;
- Accessibilità tastiera;
- Tastiera virtuale/touch;
- Proprietà tastiera classiche;
- Lingua e layout tastiera.

## Archivio storico dell'utente

La v3 incorpora, come **fonte archivistica**, i tre documenti forniti durante lo sviluppo:

- `comandi Esegui_dos.docx`
- `Comandi Esegui_Dos2.docx`
- `Comandi Esegui_Dos3.docx`

La terza lista è stata usata come base più estesa; le precedenti restano parte della provenienza del materiale.

Le voci non già presenti nei pack moderni verificati sono conservate con:
- fonte;
- descrizione originaria;
- stato `LEGACY` oppure `da verificare`;
- esecuzione disabilitata finché non vengono controllate sulla versione corrente di Windows.

Questa distinzione evita di trasformare materiale storico Windows 2000/XP in falsi comandi “attuali”.

## Sicurezza

ComboCode distingue:

- `SAFE`
- `ELEVATED`
- `DESTRUCTIVE`

Le voci archivistiche non verificate sono informative/copiabili e non vengono eseguite automaticamente.

## Tastiera

| Tasto | Azione |
|---|---|
| `Ctrl+K` / `Ctrl+L` | focus sulla ricerca della pagina attiva |
| `Ctrl+1` | CERCA |
| `Ctrl+2` | TUTTI |
| `↓` | passa dalla ricerca alla lista |
| `Invio` | apri/esegui la route selezionata |
| `Ctrl+C` | copia la route |
| `Ctrl+F` | preferito |
| `Ctrl+M` | esporta il nodo come Markdown Obsidian |
| `F1` | aiuto |
| `Esc` | chiudi |

## Obsidian

Il pulsante **ESPORTA .MD** produce una nota con frontmatter, route e WikiLink per `[[OlogrammIo]]`.

Il progetto stesso mantiene documentazione Obsidian-ready in `docs/`.

## Avvio da sorgente

Richiede Python 3.10+ su Windows. Tkinter e SQLite fanno parte della distribuzione standard di Python.

```bash
python main.py
```

## EXE con GitHub Actions

Dopo il push su `main`, Actions:

1. esegue i test;
2. installa PyInstaller;
3. genera `ComboCode v3.exe` senza console;
4. pubblica l'artifact `ComboCode-Windows-v3`.

---

**ShiduLab non programma, indica.**
