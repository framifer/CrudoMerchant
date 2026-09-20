# Crudo Merchant — Documento di Design, Meccaniche & Storia delle Modifiche

> Documento unico di handoff. Racchiude **visione, regole, meccaniche, struttura tecnica** del gioco
> e il **registro completo delle modifiche** fatte nelle varie sessioni. Pensato per essere letto da un
> altro sviluppatore o da un'altra AI che debba metterci mano.
> Titolo del gioco: **Crudo Merchant** (schermata iniziale: "CRUDO / MERCHANT", senza teschio).
> Il gioco resta **un unico file** `index.html`. Ultimo aggiornamento: 2026-09-20.

---

# PARTE A — DESIGN & MECCANICHE

## 1. Cos'è il gioco

Un **action-adventure piratesco con un forte cuore gestionale-economico** (visione "Opzione B":
avventura con economia viva). Ambientazione: **Caraibi 1650–1730**. Protagonista: **Crudo the Pirate**,
tornato dal mare per vendicarsi del Re che ha bruciato la sua nave e la sua ciurma, e liberare i porti
dal giogo delle tasse.

Il gioco mescola:
- una **spina dorsale narrativa breve** (10 tappe) che funge anche da tutorial dei sistemi;
- un **gestionale economico** in stile Anno 1701 / Port Royale / Mercatorio (ma senza micromanagement):
  mercato dinamico, produzione, stagioni, catene produttive, investimenti, contratti;
- **battaglie navali**, duelli, esplorazione di 9 aree via mare/terra.

**Filosofia di design guida:** aggiungere profondità economica solo dove aumenta il divertimento del
loop `naviga → commercia → combatti → cresci`, MAI dove aggiunge burocrazia. Niente stipendi, niente
degrado edifici, niente micromanagement. "Il commercio è ricco ma scorre da solo."

---

## 2. Struttura tecnica

- **Un unico file**: `index.html` (~8300 righe). Tutto inline: HTML + CSS + JS + dati.
- Motore: **Canvas 2D**, risoluzione interna `W=192, H=168`, tile `TILE=16`. Pixel art, `imageSmoothingEnabled=false`.
- Tutto il codice è dentro una **IIFE** `(function(){ "use strict"; ... })();`.
- **Game loop**: `loop(now)` → `update(dt)` + `draw()` via `requestAnimationFrame`. `dt` clampato a 0.1.
- **i18n**: oggetto `STR` con `it` ed `en`; funzione `t(key)`. Anche `VARIANTS`/`vpick` per righe variabili.
  Le chiavi mancanti ritornano la chiave stessa (utile per debug).
- **Dati storia inline**: `window.STORY_DATA` (premise, quests, dialogues) e `window.STORY_POS`
  (posizioni NPC e pickup). Iniettati a runtime dal "CENTRAL STORY LOADER" (`loadStory`).
- **Salvataggio**: automatico e continuo su `localStorage` (chiave `crudoRPG.save.v2`), via `saveGame()`.
  `loadGame()` ripristina; `resetProgress()` per nuova partita.
- **Input**: tastiera (WASD/frecce, Z/K=A, X/L=B, Enter=START, Shift=SELECT) + bottoni touch on-screen.
  `consumePress(k)` per input edge-triggered. **SELECT è disabilitato** (niente veicoli di terra usabili).
- **Hook di test** (solo per i test headless): `window.__CRUDO_TEST__` espone stato e funzioni per
  pilotare il gioco. È **inerte** nel gioco normale, non influisce sul gameplay.

### Aree del mondo (9)
`AREA_GRID` mappa una griglia 3x3 + open sea:
- `town` = **Porto Franco** (hub principale, base del giocatore)
- `holiday` = **Baia dei Pirati**
- `forestNW` = **Arcipelago dei Nativi**
- `forestNE` = **Campagna del Re**
- `mountain` = **Mar del Nord** (mare aperto + vulcano)
- `industrial` = **Borgo del Re** (l'industria/porto del Re)
- `cape` = **Capo del Faro**
- `island` = **Isola del Tesoro**
- `opensea` = **Mare Aperto** (raggiungibile solo via nave, zona battaglie)

Le mappe sono array di stringhe (una riga = una stringa; ogni carattere = un tile).
**Regola critica**: tutte le righe di una mappa devono avere la STESSA lunghezza, o si rompono
collisioni/rendering. `ISOLATED_AREAS = {opensea, island}` = raggiungibili solo via nave.

---

## 3. La storia — "La Marea di Crudo" (10 tappe)

Arco breve e forte; ogni tappa ha una **meccanica dominante diversa** (anti-ripetitività) e insegna/usa
un pilastro del gioco. Catena lineare `ky01 → ky10` (ognuna sblocca la successiva via `needs`).
Prima della catena c'è una quest `intro` (parla con hawkins → moll) che sblocca `ky01`.

| # | id | Titolo | Area | Meccanica |
|---|-----|--------|------|-----------|
| 1 | ky01 | Ceneri e sale | Porto Franco | intro/dialogo, recupero diario |
| 2 | ky02 | Una nave che navighi | Porto Franco | **Cantiere** (vara una nave) |
| 3 | ky03 | Primo carico | Capo del Faro | **Commercio/Mercante** |
| 4 | ky04 | Il guardiano del faro | Capo | **Pedinamento (tail)** |
| 5 | ky05 | Il patto della Baia | Baia dei Pirati | **Duello (fight)** |
| 6 | ky06 | Ferro dai Reietti | Arcipelago | **Perlustrazione (scour)** |
| 7 | ky07 | Sangue sull'acqua | Mare Aperto | **Battaglia navale (sink)** |
| 8 | ky08 | La fucina dell'inferno | Isola | **Deduzione + arrembaggio (board)** |
| 9 | ky09 | La flotta si raduna | Borgo del Re | **Naval (galleon) + scelta morale** |
| 10 | ky10 | L'ultima bordata | Borgo del Re | **Confront (boss verbale) finale** |

- **Scelta morale** (ky09, `MORAL_SNODI`): sorte di Lady Isabel → A (giustizia) / B (pietà).
  Determina il finale (`showEnding`): variante `just` / `mercy` / `grey`.
- **FINAL_ID = "ky10"**. Al completamento parte `showEnding()`.
- Ogni tappa ha `pickup` (un indizio da raccogliere in un'area, posizione in `STORY_POS.pickups`) e
  NPC `start_npc`/`complete_npc` (posizioni in `STORY_POS.npc`).
- **SNODI** (mappano id-quest → tipo di meccanica speciale):
  - `FIGHT_SNODI = { ky05 }` — duello Zelda-like in tempo reale.
  - `NAVAL_SNODI = { ky07:sloop/sink, ky08:brig/board, ky09:galleon/sink }`.
  - `TAIL_SNODI = { ky04 @cape }` — pedinamento stealth.
  - `SCOUR_SNODI = { ky06 @forestNW }` — perlustrazione (barra hot/cold).
  - `DEDUCTION_SNODI = { ky08 → ky04 }` — collega due indizi.
  - `CONFRONT_SNODI = { ky10 }` — boss verbale: scegli la prova giusta.
  - `MORAL_SNODI = { ky09 }`.

**Nota architetturale importante:** la storia gira dentro un motore chiamato internamente **`CASE`**
(con termini `clue`/`interro`/`case`): sono un **retaggio di naming** del vecchio gioco investigativo, ma
la **logica è viva e indispensabile** — fa girare la storia pirata `ky01..ky10` e i suoi minigiochi.
NON va rimossa né rinominata alla leggera.

**Regola di coerenza dati** (validata da test): ogni pickup deve stare nell'area indicata dalla quest,
su una tile calpestabile (non in `OUT_SOLID`). Ogni NPC referenziato deve esistere in `STORY_POS.npc`.

Per cambiare la storia: modificare `window.STORY_DATA` (quests+dialogues) e `window.STORY_POS`
(posizioni), poi riallineare gli SNODI e `FINAL_ID`. Gli stati dialogo sono `start` / `active` / `done`.

---

## 4. Economia dinamica (IL CUORE del gioco)

Obiettivo: economia viva con **progressi potenzialmente infiniti**. Tutte le funzioni sono nel blocco
"DYNAMIC ECONOMY" di `index.html`.

### 4.1 Merci e porti
- **6 merci** (`TRADE_GOODS`): fish (8), rum (16), timber (12), spice (26), iron (34), pearl (55).
  Il numero è il prezzo `base`.
- **4 hub commerciali** (`TRADE_HUBS`): forestNW, town, industrial, cape.
- Ogni porto (`TRADE_PORTS`) ha:
  - `prof[gid]`: profilo statico (<1 = lo produce/costa poco; >1 = lo domanda/costa caro).
  - `prod[gid]`: unità prodotte per tick.
  - `cons[gid]`: unità consumate per tick.

### 4.2 Stock e prezzi (domanda/offerta reale)
- `market.stock[port][good]` = magazzino (0..`STOCK_CAP=60`, equilibrio `STOCK_MID=30`).
- **Prezzo derivato dallo stock**: magazzino pieno → prezzo basso (~0.6×), vuoto → alto (~1.7×).
  Funzione `stockMult(s)`. Prezzo finale in `goodPrice(port,gid)` =
  `base × prof × dyn(stock) × evento × stagione(domanda)`, arrotondato, min 1.
- **Il giocatore muove il mercato**: comprare drena lo stock (prezzo su), vendere lo riempie (prezzo giù)
  — `marketNudge(port,gid,dir)`. (Verificato in diagnostica: prezzo base 3 → 9 dopo acquisti → 3 dopo vendite.)
- **`marketTick(dt)`**: ogni ~3s produce/consuma, applica auto-correzione verso l'equilibrio + rumore,
  aggiorna i prezzi, e gestisce gli eventi.

### 4.3 Eventi economici (casuali)
- In `marketTick`, se non c'è evento attivo, **3% di probabilità** per tick di generarne uno:
  porto+merce a caso, tipo `shortage` (prezzo ×1.5) o `boom` (×0.6), durata ~60s. Banner d'avviso.
- Imprevedibili, non pilotabili dal giocatore. Frequenza/durata tarabili (`0.03` e `tLeft:60`).

### 4.4 Investimenti nei porti (progressione infinita)
- `market.invest[port][good]` = livello. Menu Mercante → "Investi nel porto" → `openInvest(port)`.
- `investCost` cresce del 60% per livello (`INVEST_COST0=150 × 1.6^lvl`).
- Ogni livello aggiunge `INVEST_STEP=2` unità di produzione a quel bene (produzione effettiva =
  `prod[gid] + invLvl*INVEST_STEP`, calcolata a runtime) → surplus stabile → reddito crescente e senza
  tetto. È il motore dei "progressi infiniti".

### 4.5 Stagioni cicliche (dettate dal tempo)
- Ciclo **primavera → estate → autunno → inverno** (`SEASON_ORDER`), rotazione automatica ogni
  `SEASON_AUTO_SECS=300` secondi di gioco effettivo (nel loop). Banner al cambio. `cycleSeason()`.
- Cambiano **produzione** e **domanda** per merce (`SEASON_ECON`), es.:
  - Inverno: pesca/spezie/perle crollano; rum/legname/ferro molto richiesti.
  - Estate: pesca e perle abbondanti; gran sete di rum.
  - Primavera/autunno: raccolti e scorte.
- Cambiano anche le **palette** del mondo (`SEASON_PAL`), effetto puramente visivo (neve, colori).
- Persistite: `season`, `seasonAutoTimer`.

### 4.6 Catene di produzione (dipendenza reciproca)
- `RECIPES`: un bene LAVORATO richiede un INPUT grezzo, che consuma:
  - **Rum ← Spezie**, **Ferro ← Legname**, **Perle ← Pesce** (ratio 1:1).
  - Materie prime (fish, spice, timber) prodotte direttamente.
- In `marketTick`: le materie prime si producono, poi i lavorati sono **limitati dall'input in stock**
  (se manca, la produzione si ferma e il prezzo del lavorato sale → segnale di rotta commerciale).
- Crea rotte emergenti: nessun porto si basta da solo. Si combina con stagioni (meno pesce d'inverno
  → meno perle a valle) ed eventi.

### 4.7 Rotte commerciali automatiche
- `chooseRouteDest/Good/Qty` → `routeTick`: mandi la nave a comprare/vendere in un altro hub; richiede
  tempo (leg out/back), può subire un **assalto** (dipende da `shipSecurity()`), poi `resolveRoute()`
  paga il ricavo. Una rotta attiva per volta.

### 4.8 Costo di trasporto per distanza + vantaggio geografico
- **Matrice distanze** `ROUTE_DIST` tra i 4 hub, coerente con `AREA_GRID`; `routeDist(a,b)`.
- **Tempo di viaggio** scala con la distanza: `routeLegSecs = ROUTE_BASE_SECS(12) × dist / shipSpeed`.
- **Costo di trasporto monetario**: `routeShipCost = SHIP_FEE_PER_DIST(0.9) × dist × qty`, salvato nella
  rotta e **dedotto dal ricavo** in `resolveRoute` (ricavo netto = lordo − trasporto). Mostrato nelle
  opzioni quantità e nel banner finale (`rt_shipcost`).
- **Rischio d'assalto scala con la distanza**: in `routeTick` la soglia usa `sec - dist*3`.
- **Contratti scalati sulla distanza** (`makeOffer`): premio +`dist*2`, giorni concessi ~`dist*0.8+2..`.
- **Vantaggio geografico**: gli scambi al banco locale (`openTrade`) non pagano trasporto; le rotte a
  lunga distanza sì → i porti vicini restano competitivi. Rotte lunghe = più tempo/spese/rischio.

### 4.9 Contratti a lungo termine
- Stato `contract` (uno attivo per volta). Menu Mercante → "Contratti" → `openContracts(port)`.
- Offerta (`makeOffer`): consegna **N casse** (4–9) di una merce a un **porto destinazione** entro
  **D giorni** (3–5), a **prezzo fisso premium** (+40%..+80% sul mercato). Protegge dalle fluttuazioni.
- Accetti → l'offerta diventa contratto attivo con `dueDay = dayCount + D`.
- Consegna: al porto destinazione, con la merce in stiva → `deliverContract()` paga `price×qty` + fama.
- **Scadenza**: `contractTick()` nel loop fallisce il contratto se `dayCount > dueDay`.
- Persistito nel save (`contract`).

---

## 5. Altri sistemi

- **Cantiere navale** (`openShipyard`): 5 tipi di nave con progressione di costo/stiva —
  rowboat (0, hold 8) → sloop (60, 16) → caravel (180, 28) → frigate (400, 40) → galleon (720, 60).
  Comprare una nave più grande MANTIENE i componenti. Upgrade **scafo** (HP), **cannoni** (danno),
  **prua** (speronamento). La stiva (`cargoCap`) dipende dalla nave.
- **Ciurma** (`crew`), **fama/rango pirata** (`fame`, `pirateRank`), **taglie** (`bounty`).
- **Battaglie navali** (`startNaval`): bordate (A, fianco a fianco), speronamento/arrembaggio,
  obiettivi (sink/board/escort/flee/batteries). In Mare Aperto ci sono navi ostili ambientali, quindi
  una battaglia navale è **sempre disponibile** al giocatore.
- **Duelli a terra** (`startFight`): action Zelda-like (A colpisci, B schiva).
- **Boss verbale** (`startConfront`/`runConfront`): scegli la prova giusta per abbattere la resistenza.
- **Pedinamento** (`startTail`), **perlustrazione** (`startScour`), **deduzione** (`startDeduction`).
- **Taverna / Locanda** (`openTavern`): menu con **Recluta ciurma** (`recruitCrew`) e **Gioca ai dadi**
  (`openDice`). Dadi: punti 10/25/50 dobloni, scommetti ALTO/BASSO/PARI/DISPARI, tiri 3 dadi,
  payout **1.9×** (margine del banco ~5%). Persistente coi dobloni reali.
- **Pesca (rete di sicurezza economica)**: parla con un Pescatore sul molo → sempre qualche pesce (o oro
  se la stiva è piena). Garantisce che non si resti mai bloccati senza soldi.
- **SQ slot engine**: pool vuoto (nessuna side-quest a rotazione al momento; `window.SIDEQUESTS` vuoto).
  Kind rimasti: recon, morale, confront, tail, fight, courier.
- **Ciclo giorno/notte**: `clock`, `DAY_LEN=180s` per giorno, `dayCount`. `nightFactor()` per il tinting.
- **Sbarco universale**: in barca, premendo A vicino a qualsiasi spiaggia/molo/isola si sbarca.

---

## 6. Sistemi di guida al giocatore e Menu

### 6.0 Voci di menu attive
`MENU_KEYS = [map, journal(REGISTRO), notebook(MERCANTILE), crew(CIURMA), lang(LINGUA),
guide(GUIDA), rules(REGOLE DI GIOCO), exit]` — 8 voci, senza sovrapposizioni sullo schermo.
Menu Mercante (parlando con un Mercante in un hub): Contratta al banco / Organizza rotta /
Investi nel porto / Contratti / Esci.

Ci sono **tre sistemi distinti** che accompagnano il giocatore nelle meccaniche:

### 6.1 "Ordini del Capitano" — missioni-guida LINEARI (`tut`)
Il tutorial iniziale, travestito da missioni (a schermo: "ORDINE n/9"). Una NUOVA PARTITA
(`resetProgress`) inizia **in barca accanto al molo di Porto Franco** (tx23,ty33), con **50 dobloni**.
`TUT_STEPS = intro, move, merchant, buy, shipyard, log, tavern, story, sail`.
- **intro** → sbarca (A) — `tutOnLand`
- **move** → cammina (6 passi) — `tutOnMove`
- **merchant** → parla col Mercante [! su `trader_town`] — `tutOnMerchant`
- **buy** → compra una merce al banco — `tutOnBuy`
- **shipyard** → entra nel Cantiere — `tutOnShipyard`
- **log** → apri il Registro (START) — `tutOnLog`
- **tavern** → entra in Taverna — `tutOnTavern`
- **story** → parla con Hawkins [! su `hawkins`] — `tutOnStoryTalk`
- **sail** → salpa in Mare Aperto — `tutOnSail`
Ogni passo avanza quando il giocatore compie l'azione. Il testo dell'ordine corrente appare nel box HUD
in alto a destra via `activeQuestText()`. Marcatori "!" via `tutTargetNpc`. Stato `tut{step,done}`
persistito. NUOVA PARTITA riavvia gli Ordini; CONTINUA (vecchio save) no.

### 6.2 "Imprese del Capitano" — missioni-guida NON LINEARI (`tut2`)
Appena gli Ordini finiscono (`tut.done`), il loop (`tut2Maybe`) avvia una SECONDA serie: **9 Imprese**
che insegnano le meccaniche avanzate. A differenza degli Ordini, sono una **checklist non lineare**: si
completano nell'ordine che il giocatore preferisce mentre gioca la storia.
`TUT2_STEPS = sell, prices, route, invest, contract, recruit, upgrade, bounty, naval`.
- **sell** → vendi al banco — `tut2OnSell`
- **prices** → apri la scheda PREZZI del Registro — `tut2OnPrices`
- **route** → avvia una rotta commerciale — `tut2OnRoute`
- **invest** → investi in un porto — `tut2OnInvest`
- **contract** → accetta un contratto — `tut2OnContract`
- **recruit** → recluta un marinaio — `tut2OnRecruit`
- **upgrade** → potenzia la nave — `tut2OnUpgrade`
- **bounty** → accetta una taglia — `tut2OnBounty`
- **naval** → vinci una battaglia navale — `tut2OnNaval`
L'impresa in sospeso appare nell'HUD (via `activeQuestText`, solo quando NON c'è una missione di storia
attiva, che ha priorità). Introduzione con pannello `showExamine(tut2_start)`, progresso `#/9`, banner di
chiusura. Stato `tut2{started,done,done_map}` persistito; azzerato da NUOVA PARTITA. Stringhe `tut2_*`.

### 6.3 Tutorial contestuali "primo utilizzo" (`teachOnce`) — NON sono missioni
La **prima volta** che il giocatore entra in una meccanica d'azione, appare un pannello che ne spiega i
comandi, poi il gioco prosegue (nessun obiettivo, nessun "!"). Meccaniche coperte (stringhe `learn_*`):
- **trade** (banco: A compra, ← vende, B esci) — in `openTrade`
- **naval** (frecce naviga, A bordata fianco a fianco, sperona per arrembaggio) — in `startNaval`
- **fight** (A colpisci, B schiva) — in `startFight`
- **tail** (segui a distanza, tieni A per furtivo) — in `startTail`
- **scour** (barra caldo/freddo, A sul punto) — in `startScour`
- **confront** (scegli la prova giusta) — in `runConfront`
Dettagli: stato `learned{}` persistito; `teachOnce(key,onDone)` mostra il pannello **una sola volta** poi
va al callback; il pannello (dialog) ha **priorità** sui minigiochi nell'update (li mette in pausa); NON
appare durante gli Ordini iniziali (per non duplicare le guide del tutorial base).

### 6.4 GUIDA (manuale sfogliabile) — `GUIDE_PAGES` / `drawGuide`
Voce di menu **GUIDA** (tra LINGUA e REGOLE). Manuale di **17 pagine** (frecce = cambia pagina, B = esci)
che spiega ogni modalità e meccanica: comandi, missioni, comprare, vendere, rotte, investimenti,
contratti, stagioni e catene, cantiere, battaglia navale, duello, ciurma/taverna, fama/taglie, pesca,
registro/mappa, Imprese. Pagine `{h,lines}` localizzate it/en. Testi calibrati per non sforare il box.

### 6.5 Freccia-guida sopra la testa (`questTargetPoint` / `drawQuestMarksOverlay`)
Una **freccia gialla su disco scuro appare appena sopra la testa di Crudo** e punta sempre verso il
prossimo obiettivo, per non lasciare mai il giocatore senza indicazioni. Coperta da `questTargetPoint()`:
- **Ordini del Capitano** (tut base): punta all'NPC/insegna/mare del passo corrente (gli step "sbarca"
  e "cammina" non hanno luogo, quindi lì non c'è freccia — è corretto).
- **Missioni della storia** (case attive): punta al pickup dell'indizio o all'NPC di consegna.
- **Imprese del Capitano** (serie 2): punta al luogo dell'impresa in sospeso — insegna Mercante
  (sell/prices/route/invest/contract), Taverna (recruit), Cantiere (upgrade), il Banditore (bounty) o
  il mare (naval). Se l'insegna non è nell'area corrente, la freccia guida verso Porto Franco.
La freccia gira anche mentre sei in barca (per l'impresa navale). È disegnata in `drawQuestMarksOverlay`,
sempre sopra night/fog per restare leggibile. Verificata dai test di regressione.

### 6.6 Registro del Capitano (ex "DIARIO") — `drawJournal`
A 3 schede (sinistra/destra per cambiare):
- **MISSIONI**: lista UNICA (storia + secondarie), senza distinzione rosso/giallo. Attive prima, poi
  completate ([>]=attiva, [x]=completata). A = dettaglio, su/giù = scorri.
- **ECONOMIA** (sola lettura, `economyLines()`): stagione, contratto, rotta, investimenti, oro, fama.
- **PREZZI**: tabella porto × merce col prezzo corrente (`goodPrice`) — dove comprare basso / vendere alto.
- Marcatori "!" nel mondo: **tutti GIALLI** (`drawQuestMark`), incluse le missioni di storia.

---

## 7. Convenzioni e cose da NON rompere

- **Non cambiare le CHIAVI i18n** (es. `menu_*`, `tut_*`, `cs_*`) anche se il testo visibile cambia:
  sono ID usati dal codice. Cambia solo i VALORI (le stringhe tra virgolette).
- **Parità i18n**: ogni chiave in `STR.it` deve esistere in `STR.en` e viceversa (verificato dai test).
- Le mappe area devono avere **righe di uguale lunghezza**.
- Il motore `CASE` (storia) e i suoi minigiochi (tail/scour/fight/naval/confront/deduction) NON vanno
  rimossi: fanno girare la storia pirata.
- Ogni modifica alla storia richiede di riallineare **pickup positions** e **SNODI**.
- Fai **backup** di `index.html` prima di modifiche grosse (ci sono molti `index.backup-*.html`).
- **Verifica sempre** dopo ogni modifica: `node test/run.js` e `node test/diagnose.js`.

---

## 8. Backlog / idee non ancora implementate

- **UI economica leggibile**: mostrare stock/tendenza prezzi e catene anche nel menu Mercante.
- **Order book leggero**: NPC che piazzano ordini visibili (opzionale).
- **Micro-missioni guidate dedicate** (opzione discussa): trasformare i tutorial contestuali (§6.3) da
  pop-up a vere missioni di prova (es. "Impara la battaglia navale" con una battaglia guidata).
- Bilanciamento fine: frequenza eventi, reattività prezzi per merce, difficoltà tappe/naval.
- Coerenza estetica: nell'area `mountain` (Mar del Nord) restano decorazioni alpine (sciatori/chalet),
  residuo del vecchio tema montano — da valutare se ritematizzare.

## 9. Scelte di design esplicite
- SÌ: catene, contratti, trasporto/distanza, stagioni, eventi, investimenti.
- NO: stipendi manodopera, degrado/manutenzione edifici, order book pieno multiplayer. Questi
  renderebbero il gioco un "foglio di calcolo" e snaturerebbero l'avventura.

---
---

# PARTE B — REGISTRO DELLE MODIFICHE (CHANGELOG)

## Sessione 2026-09-19 — Diagnostica & QA iniziale
Metodo: harness headless in Node che stubba DOM/Canvas/Audio, carica i 3 blocchi `<script>`, cattura i
listener tastiera e il game loop, e pilota il gioco. Suite: init, completabilità storia (10/10), coerenza
i18n, griglia mappe, economia end-to-end, minigiochi, tutte le viste di menu/Registro, tutte le 9 aree,
fuzzing 50k input. Risultato: 0 crash, 0 errori runtime.

Bug REALI trovati e CORRETTI:
1. **Stallo economico iniziale**: si partiva con 0 oro e la pesca non fruttava nulla. Ora la pesca dà
   1-2 pesci (o un po' d'oro se la stiva è piena) → rete di sicurezza economica.
2. **Hint mare col tema vecchio**: "Isola del Culto" → "Isola del Tesoro"; "Mare Profondo" → "acque aperte".
3. **Placeholder SQ-spazzatura**: `sqLoadPool` generava side-quest fittizie se `window.SIDEQUESTS` era
   vuoto. Ora il pool resta vuoto.

---

## Sessione 2026-09-20 (mattina) — Pulizia, colore mappa e prima serie di guide

### 1. Colore del mare del Borgo del Re (fix minimappa)
Il mare dell'area est (`industrial`) appariva **più scuro** sulla schermata MAPPA. Causa: il tile del
porto del Re (`q`) valeva `#1c3450` in `MINI_COL`, mentre il mare normale (`~`) vale `#3a8ad8`. Nel mondo
reale `q` era già disegnato identico al mare. Fix: `MINI_COL["q"]` → `#3a8ad8`. Minimappa uniforme.

### 2. Rimozione del vecchio gioco "investigativo/cittadina"
Il progetto era nato da un vecchio gioco (ragazzo che torna in una cittadina di mare, con detective e
micro-quest). Rimossi **fisicamente dal codice** tutti i residui:
- **Micro-quest** cat/shell/parcel/kids/oldfriend/photos e i loro **NPC** (nonna, pino, fornaio, nico,
  mamma, boy, girl, teo, capo).
- **Oggetti collezionabili** morti (cat, shell, ball, keyring, photos, bike) e le funzioni di disegno
  (`drawShell/drawBall/drawKeyring/drawPhoto/drawBikeObj`).
- Variabili/funzioni morte: `questState`, `shellQuest`, `canStartMicro`, `MICRO_ORDER`,
  `currentMicroSlot`, `microDone`.
- **Scooter/"cavallo"**: side-quest delivery/chase, `scooterUnlocked`, beat "foot-chase → scooter".
- **Photo-stakeout** orfana (`photoCam`, `startPhotoCam`, `drawPhotoCam`, `PHOTO_SNODI`).
- **~110 chiavi i18n morte** (rimosse da IT ed EN mantenendo la parità).
- Gli **NPC filler** del porto (vito, lena, gina, bruno, marinaio) **ritematizzati** a tema mercante;
  testi HUD/REGOLE "rosso vs giallo" → "tutti gialli"; "Chiedi in giro di chi ti ha convocato" → flusso
  pirata (Hawkins → Moll).
- **NON rimosso** (è la storia pirata): il motore `CASE` e i suoi minigiochi.

Risultato: `index.html` ridotto di ~35 KB / ~400 righe di codice morto.

### 3. Prima serie extra: "Imprese del Capitano" (`tut2`)
Aggiunta la seconda serie di 9 guide non lineari (vedi §6.2), con auto-avvio a fine Ordini e hook su ogni
meccanica avanzata.

---

## Sessione 2026-09-20 (pomeriggio) — GUIDA, tutorial contestuale, diagnostica totale

### 1. Voce di menu "GUIDA"
Nuova voce **GUIDA** (dopo LINGUA, prima di REGOLE) — manuale di 17 pagine (vedi §6.4).

### 2. Tutorial contestuale "primo utilizzo" (`teachOnce`)
Pop-up esplicativi la prima volta che si entra in trade/naval/fight/tail/scour/confront (vedi §6.3).

### 3. Diagnostica TOTALE e correzioni
Diagnostica profonda (`test/diagnose.js`) che pilota il gioco come un giocatore:
- rendering di **tutte le 9 aree** (40 frame l'una);
- **input in ogni contesto** (tutte le direzioni + A/B/START/SELECT per area);
- **tutti gli 8 menu** con navigazione interna;
- **economia end-to-end** (400 tick) + **logica economica reale** (compra alza prezzo, vendi lo abbassa,
  investi alza il livello di investimento — verificato);
- **completabilità storia** ky01→ky10 (10/10);
- **playthrough end-to-end** (nuova partita → fine tutorial → auto-avvio serie 2 → completamento);
- **fuzz di 12.000 input casuali**.

**Risultato finale: 0 crash, 0 problemi logici.**

Problemi trovati e **corretti**:
1. **Overflow UI** di 2 pagine della GUIDA (Rotte, Stagioni) → riscritte più corte.
2. **UX avvio serie 2**: mostrava il banner sbagliato → ora pannello introduttivo `tut2_start`.
3. **Chiave i18n duplicata** `tut_intro` (EN) → rimossa.
4. **Stub audio del test** incompleto → completato l'harness (non è codice di gioco).

Note (non-bug): due chiavi i18n (`area_island`, `yard_nogold`) risultano definite due volte nello stesso
`STR` per lingua; l'ultima vince ed è corretta, quindi innocue. Lasciate intatte per non rischiare righe
i18n dense a fronte di guadagno nullo.

### Valutazione da game designer (giocabilità, logica, UI)
- **Giocabilità/logica**: il loop `naviga → commercia → combatti → cresci` regge; economia viva e
  reattiva; nessuno stato senza uscita (pesca come rete di sicurezza; battaglie navali sempre trovabili
  in Mare Aperto).
- **Bilanciamento**: progressione navi (0/60/180/400/720) e prezzi merci (8–55) coerenti col capitale
  iniziale (50); progressione "infinita" via investimenti.
- **UI/menu**: 8 voci senza sovrapposizioni; GUIDA e REGOLE non sforano; hint dei minigiochi corretti.

---
---

# PARTE C — COME LAVORARE SUL PROGETTO

- Il gioco è tutto in **`index.html`** (HTML + CSS + JS + dati inline).
- Questo documento (design + changelog) è il riferimento unico.
- I **backup** (`index.backup-*.html`) sono istantanee salvate a ogni grande tappa.
- I **test** sono in `test/`, headless in Node, e NON fanno parte del gioco.

## Eseguire i test (consigliato dopo OGNI modifica)
```bash
cd <cartella-del-progetto>
node test/run.js        # 29 test di regressione: boot, storia, i18n, mappe, funzionali, serie2, guida, learn
node test/diagnose.js   # diagnostica profonda: 9 aree, tutti i menu, economia, storia, playthrough, fuzz 12k
```

## Provare il gioco nel browser
```bash
cd <cartella-del-progetto>
python3 -m http.server 3000
```
Poi apri il gioco tramite il proxy DevSpaces (bottone **Connect**, porta 3000).

## Struttura dei test
- `test/harness.js` — stub headless di DOM/Canvas/Audio/localStorage; carica i 3 blocchi `<script>`.
- `test/run.js` — suite di regressione (29 test).
- `test/diagnose.js` — diagnostica profonda (aree, input, economia, storia, playthrough, fuzz 12k).
- `test/dead-i18n.js` / `test/strip-dead-i18n.js` — utility per individuare/rimuovere stringhe morte.

Hook di test nel gioco: `window.__CRUDO_TEST__` (getter di stato + funzioni per pilotare). Inerte nel
gioco normale.
