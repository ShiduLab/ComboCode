# ComboCode Web / PWA

Versione browser di ComboCode, pensata anche per PC aziendali o postazioni dove non è possibile installare software o usare supporti USB.

L'interfaccia riprende ComboCode desktop: CERCA, TUTTI e MIE. Il catalogo standard viene costruito dagli stessi pack JSON della versione desktop.

## Esecuzione

I browser non possono eseguire liberamente comandi locali Windows.

Per questo il pulsante **APRI / ESEGUI** resta sempre presente:

- quando una route è realmente apribile dal browser, il pulsante è attivo;
- quando non lo è, resta disabilitato e compare l'avviso **"Per usare questo comando scarica ComboCode"**;
- **COPIA** resta disponibile e ComboCode spiega come usare la route sul PC in base al tipo: RUN, CMD, PowerShell, URI, HOTKEY o gesto.

Esempio RUN:

> Clicca COPIA, premi Win + R, incolla il comando e premi Invio.

## MIE

Le shortcut personali della versione Web vengono salvate nel `localStorage` del browser. Possono essere importate ed esportate in JSON.

## PWA

La Web App include manifest e service worker per il caricamento rapido e la consultazione della shell già visitata. L'installazione PWA è opzionale: ComboCode Web funziona normalmente anche aprendolo come semplice sito.
