---
title: ComboCode
aliases:
  - Combo Code
  - ShiduLab ComboCode
type: progetto
status: concept
created: 2026-09-12
tags:
  - ShiduLab
  - software
  - Windows
  - shortcut
  - comandi
  - Obsidian
---

# ComboCode

## Concept

**ComboCode** è un motore di accesso alle funzioni, non una semplice lista di shortcut.

L'utente cerca **cosa vuole ottenere** e ComboCode restituisce tutte le route disponibili:

1. combinazione di tasti;
2. stringa per **ESEGUI**;
3. comando **CMD/DOS**.

Il modello può essere esteso internamente anche a:
- PowerShell;
- URI `ms-settings:`;
- CPL;
- MSC;
- shell namespace;
- URL;
- percorsi file/cartelle;
- comandi applicativi;
- macro e script.

> Stesso obiettivo, più route.

---

## Esempio 1 — Esegui

Ricerca:

`Esegui`

Risultato:

**HOTKEY**

`WIN + R`

Azioni:
- Copia
- Preferito
- Mostra sequenza

---

## Esempio 2 — Connessioni di rete

Ricerca:

`Connessioni di rete`

Risultati possibili:

**RUN**

`ncpa.cpl`

**CMD**

`control netconnections`

Azioni:
- Apri / Esegui
- Copia
- Preferito

Sinonimi di ricerca:
- schede di rete
- network adapters
- ethernet
- wifi
- ncpa

---

## Idea UX centrale

La ricerca deve funzionare per **intenzione**, non solo per testo esatto.

Esempio:

`schede di rete`

`connessioni`

`network adapters`

`ncpa`

devono poter convergere sullo stesso nodo.

ComboCode quindi diventa una **mappa operativa di accesso**.

---

## Interfaccia

Home essenziale:

`Cosa vuoi aprire o fare?`

Sotto:
- risultati istantanei;
- recenti;
- preferiti;
- categorie.

Ogni risultato mostra:
- nome;
- tipo;
- comando / shortcut;
- compatibilità;
- privilegi richiesti;
- pulsanti `APRI`, `COPIA`, `★`.

---

## Tastiera-first

ComboCode deve essere interamente usabile senza mouse.

Flusso ideale:

`hotkey globale` → ricerca → frecce → `ENTER`

Azioni rapide:
- `ENTER` = apri/esegui;
- `CTRL+C` = copia;
- `ESC` = chiudi;
- frecce = navigazione;
- hotkey globale configurabile per richiamare ComboCode sopra qualunque finestra.

Concetto vicino a una **Command Palette di Windows universale**.

---

## Liste / pacchetti

Nodi previsti:

- [[ComboCode Windows]]
- [[ComboCode Word]]
- [[ComboCode Excel]]
- [[ComboCode Obsidian]]
- [[ComboCode ChatGPT]]
- [[ComboCode Browser]]
- [[ComboCode VS Code]]
- [[ComboCode Git]]
- [[ComboCode Networking]]
- [[ComboCode Sysadmin]]

Possibili pacchetti:
- Windows Pack
- Office Pack
- Obsidian Pack
- ChatGPT Pack
- Sysadmin Pack
- Networking Pack
- Developer Pack

---


## Pagina TUTTI

ComboCode deve avere una pagina dedicata che raccolga **tutte le voci disponibili**, non solo i risultati di ricerca.

La pagina `TUTTI` deve permettere di vedere l'intero archivio in modo ordinato e filtrabile.

Possibile struttura:

- TUTTI
- HOTKEY
- RUN
- CMD
- PowerShell
- CPL
- MSC
- URI Windows
- Applicazioni

Ogni riga mostra almeno:
- Obiettivo
- Tipo
- Comando / combinazione
- Categoria
- Stato
- Versione / compatibilità

Funzioni:
- ordinamento per colonna;
- filtro per categoria;
- ricerca interna;
- apertura/esecuzione;
- copia;
- preferiti;
- esportazione Markdown;
- conteggio totale delle voci.

La pagina TUTTI serve anche come **indice generale dell'archivio**, utile per esplorare ciò che l'utente non sa ancora di poter cercare.

In pratica ComboCode deve avere due modalità complementari:

**Ricerca intenzionale**  
> So cosa voglio ottenere.

**Esplorazione archivio**  
> Voglio vedere tutto ciò che ComboCode conosce.


## Struttura di una voce

Esempio:

```yaml
name: Connessioni di rete
aliases:
  - schede di rete
  - network adapters
  - ncpa
  - ethernet
  - wifi
types:
  - run
  - cmd
commands:
  - ncpa.cpl
  - control netconnections
platform: Windows
versions:
  - 10
  - 11
verified: true
```

Campi utili:
- nome;
- alias;
- tipo;
- comando;
- piattaforma;
- applicazione;
- versione;
- privilegi;
- stato;
- data ultimo test;
- fonte;
- note.

Stati:
- verificato;
- legacy;
- deprecato;
- non verificato;
- dipende dalla versione.

---

## Sicurezza

Il pulsante `ESEGUI` non deve lanciare indiscriminatamente qualunque stringa.

Classificazione:

- `SAFE` — apre pannelli, cartelle, impostazioni;
- `ELEVATED` — richiede amministratore;
- `DESTRUCTIVE` — modifica o cancella dati/configurazioni;
- `EXTERNAL` — apre URL o applicazioni esterne.

I comandi distruttivi non devono partire con un solo `ENTER`.

---

## Nota tecnica sui link eseguibili

Da una normale pagina web non è corretto promettere l'esecuzione arbitraria di comandi locali: i browser lo impediscono per sicurezza.

In una **app desktop Windows**, invece, ComboCode può avere pulsanti `APRI/ESEGUI` che invocano in modo controllato il comando previsto.

Quindi il concept guadagna molto se nasce come **app desktop**, eventualmente portable.

---

## Database

### Prototipo
JSON.

### Versione stabile
SQLite locale.

Tabelle indicative:
- commands;
- aliases;
- applications;
- categories;
- versions;
- tags;
- favorites;
- history.

Vantaggi:
- nessun server;
- veloce;
- portabile;
- esportabile;
- facile backup.

---

## Funzioni da aggiungere

- ricerca fuzzy;
- sinonimi italiano/inglese;
- preferiti;
- cronologia;
- alias personali;
- note personali;
- copia istantanea;
- import/export JSON, CSV, Markdown;
- verifica se un'app o comando è disponibile;
- modalità portable;
- fonte e data ultimo test;
- versione Windows/applicazione;
- ordinamento per route più rapida / più universale.

---

## MVP

Prima versione:

- Windows desktop;
- archivio locale;
- ricerca istantanea;
- tipi HOTKEY / RUN / CMD;
- copia comando;
- esecuzione controllata;
- categorie;
- preferiti;
- navigazione completa da tastiera;
- import/export JSON;
- primo database Windows.

---

## Evoluzione

ComboCode può diventare un archivio condiviso e versionato.

Ogni voce potrebbe avere:
- fonte;
- autore;
- data;
- sistema testato;
- esito;
- compatibilità.

In seguito:
- pacchetti aggiornabili;
- contributi community;
- validazione automatica;
- sincronizzazione opzionale;
- esportazione note Obsidian.

---

## ComboCode + Obsidian

Ogni comando può diventare un nodo Markdown.

Esempio:

```md
---
type: ComboCode
platform: Windows
category: networking
verified: true
---

# Connessioni di rete

## RUN
`ncpa.cpl`

## CMD
`control netconnections`

## Link
[[Windows Networking]]
[[Pannello di controllo]]
[[Shortcut Windows]]
```

---

## Relazione con MindLink / OlogrammIo

ComboCode applica concretamente un principio di [[MindLink]]:

**un nodo può essere raggiunto da route differenti.**

Esempio:

`[[Connessioni di rete]]`
→ HOTKEY
→ RUN
→ CMD
→ URI
→ Pannello di controllo
→ Networking

Non è quindi soltanto un archivio di stringhe.

È una **mappa delle vie d'accesso operative**.

---

## Formula sintetica

> L'utente non deve ricordare **come** si raggiunge qualcosa.
> Deve sapere soltanto **cosa vuole ottenere**.

---

## Nodi collegabili

- [[ShiduLab]]
- [[MindLink]]
- [[OlogrammIo]]
- [[Windows]]
- [[CMD]]
- [[PowerShell]]
- [[Shortcut]]
- [[Command Palette]]
- [[Knowledge Base]]
- [[Obsidian]]
- [[Sysadmin]]
- [[Networking]]
- [[KUNTA]]
- [[MyJong]]


## Regola grafica ShiduLab

**Botolo + ShiduLab devono essere sempre presenti in basso a destra nell'interfaccia di ComboCode.**

Regola permanente del progetto:
- discreti;
- trasparenti;
- senza card, riquadri o fondi aggiuntivi;
- sempre leggibili;
- non devono interferire con i controlli;
- posizione canonica: **basso a destra**.

## Smussature emerse dal test v2

- `TUTTI` deve mostrare realmente **tutto l'archivio**, non un sottoinsieme iniziale di 25 route;
- le intestazioni delle colonne (`Obiettivo`, `Tipo`, `Comando/combinazione`, `Categoria`, `Stato`) devono essere cliccabili e ordinare realmente la tabella;
- l'ordinamento deve poter essere crescente/decrescente;
- l'icona ComboCode deve apparire anche nell'angolo alto sinistro della finestra, oltre che nella taskbar;
- i documenti storici di comandi ESEGUI/CMD forniti dall'utente sono una fonte da incorporare, verificando e marcando le voci obsolete/legacy;
- la pagina `TUTTI` deve essere anche un vero atlante esplorabile dell'archivio.


## Stato implementazione v3 — 2026-09-12

La v3 incorpora le smussature emerse dall'uso reale della v2:

- GUI adattiva al tema di sistema Windows;
- passaggio automatico chiaro/scuro anche a programma aperto;
- DPI/scaling per-monitor;
- icona ComboCode rinforzata anche nella barra del titolo;
- [[Botolo]] + [[ShiduLab]] canonici in basso a sinistra;
- `TUTTI` diventa davvero l'intero archivio, con filtri separati dalla pagina CERCA;
- ordinamento crescente/decrescente cliccando tutte le intestazioni;
- colonna `Verifica` distinta dalla sicurezza;
- archivio storico dell'utente importato come fonte senza modernizzazioni silenziose;
- le route legacy/non verificate sono conservate ma non eseguite automaticamente.

### Numeri v3

- 290 obiettivi
- 308 route
- 149 RUN
- 125 CMD
- 34 HOTKEY

### Nuovi nodi naturali

- [[ComboCode Archivio ESEGUI]]
- [[ComboCode Archivio DOS]]
- [[ComboCode GUI adattiva]]
- [[ComboCode Fonti]]
- [[Windows Legacy]]
- [[Windows 2000 XP]]
- [[Botolo]]
- [[ShiduLab]]


## Stato implementazione v4

Smussature nate dal test reale della v3:

- Botolo + ShiduLab spostati in **basso a destra** per non interferire con le informazioni di stato;
- `ShiduLab` non è più testo raster nero nell'immagine: viene disegnato dalla GUI e segue il tema chiaro/scuro;
- pulsante `×` alla fine della ricerca per azzerare immediatamente la query;
- filtro Categoria della pagina CERCA reso esplicitamente reattivo;
- intestazioni `Obiettivo` e `Categoria` della pagina CERCA ordinabili crescente/decrescente;
- intestazioni della pagina TUTTI restano ordinabili;
- APRI/ESEGUI disponibile per ogni route;
- ELEVATED e DESTRUCTIVE chiedono conferma ma non vengono bloccati;
- fallback di esecuzione per le route storiche importate;
- invio diretto delle HOTKEY su Windows.

