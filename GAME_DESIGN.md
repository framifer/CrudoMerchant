# Crudo Merchant — Documento di Design & Meccaniche

> Documento di handoff. Racchiude visione, regole, meccaniche e struttura tecnica del gioco,
> pensato per essere letto da un altro sviluppatore o da un'altra AI che debba metterci mano.
> Titolo del gioco: **Crudo Merchant** (schermata iniziale: "CRUDO / MERCHANT", senza teschio).
> Ultimo aggiornamento: sessione del 2026-09-19.

---

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

- **Un unico file**: `index.html` (~8000 righe). Tutto inline: HTML + CSS + JS + dati.
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
  — `marketNudge(port,gid,dir)`.
- **`marketTick(dt)`**: ogni ~3s produce/consuma, applica auto-correzione verso l'equilibrio + rumore,
  aggiorna i prezzi, e gestisce gli eventi.

### 4.3 Eventi economici (casuali)
- In `marketTick`, se non c'è evento attivo, **3% di probabilità** per tick di generarne uno:
  porto+merce a caso, tipo `shortage` (prezzo ×1.5) o `boom` (×0.6), durata ~60s. Banner d'avviso.
- Imprevedibili, non pilotabili dal giocatore. Frequenza/durata tarabili (`0.03` e `tLeft:60`).

### 4.4 Investimenti nei porti (progressione infinita)
- `market.invest[port][good]` = livello. Menu Mercante → "Investi nel porto" → `openInvest(port)`.
- `investCost` cresce del 60% per livello (`INVEST_COST0=150 × 1.6^lvl`).
- Ogni livello aggiunge `INVEST_STEP=2` unità di produzione a quel bene → surplus stabile → reddito
  crescente e senza tetto. È il motore dei "progressi infiniti".

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

### 4.9 Costo di trasporto per distanza + vantaggio geografico (NUOVO)
- **Matrice distanze** `ROUTE_DIST` tra i 4 hub, coerente con `AREA_GRID`; `routeDist(a,b)`.
- **Tempo di viaggio** scala con la distanza: `routeLegSecs = ROUTE_BASE_SECS(12) × dist / shipSpeed`.
- **Costo di trasporto monetario**: `routeShipCost = SHIP_FEE_PER_DIST(0.9) × dist × qty`, salvato nella
  rotta e **dedotto dal ricavo** in `resolveRoute` (ricavo netto = lordo − trasporto). Mostrato nelle
  opzioni quantità e nel banner finale (`rt_shipcost`).
- **Rischio d'assalto scala con la distanza**: in `routeTick` la soglia usa `sec - dist*3` (rotte lunghe
  più difficili da proteggere).
- **Contratti scalati sulla distanza** (`makeOffer`): premio +`dist*2`, giorni concessi ~`dist*0.8+2..`.
- **Vantaggio geografico**: gli scambi al banco locale (`openTrade`) non pagano trasporto; le rotte a
  lunga distanza sì → i porti vicini restano competitivi. Rotte lunghe = più tempo/spese/rischio.

### 4.8 Contratti a lungo termine (NUOVO)
- Stato `contract` (uno attivo per volta). Menu Mercante → "Contratti" → `openContracts(port)`.
- Offerta (`makeOffer`): consegna **N casse** (4–9) di una merce a un **porto destinazione** entro
  **D giorni** (3–5), a **prezzo fisso premium** (+40%..+80% sul mercato). Protegge dalle fluttuazioni.
- Accetti → l'offerta diventa contratto attivo con `dueDay = dayCount + D`.
- Consegna: al porto destinazione, con la merce in stiva → `deliverContract()` paga `price×qty` + fama.
- **Scadenza**: `contractTick()` nel loop fallisce il contratto se `dayCount > dueDay`.
- Persistito nel save (`contract`).

---

## 5. Altri sistemi

- **Cantiere navale** (`openShipyard`): 4 tipi di nave (rowboat/sloop/brig/galleon), upgrade
  scafo/cannoni/prua. La stiva (`cargoCap`) dipende dalla nave.
- **Ciurma** (`crew`), **fama/rango pirata** (`fame`, `pirateRank`), **taglie** (`bounty`).
- **Battaglie navali** (`startNaval`): bordate, speronamento/arrembaggio, obiettivi (sink/board/…).
- **Duelli a terra** (`startFight`): action Zelda-like (A colpisci, B schiva).
- **Boss verbale** (`startConfront`): scegli la prova giusta per abbattere la resistenza.
- **Pedinamento** (`startTail`), **perlustrazione** (`startScour`), **deduzione** (`startDeduction`).
- **Side-quest** (SQ slot engine): missioni gialle a rotazione, una per volta.
- **Ciclo giorno/notte**: `clock`, `DAY_LEN=180s` per giorno, `dayCount`. `nightFactor()` per il tinting.
- **Sbarco universale**: in barca, premendo A vicino a qualsiasi spiaggia/molo/isola si sbarca
  (logica message-driven in `interact`, hint `drawBoatLandHint`).

---

## 6. Menu (voci attive)
`MENU_KEYS = [map, journal(REGISTRO), notebook(merchant stats), crew, lang, rules, exit]`.
La voce STAGIONE e MOTORINO NON sono nel menu (sistemi rispettivamente automatico / disattivato).
Menu Mercante (parlando con un Mercante in un hub): Contratta al banco / Organizza rotta /
Investi nel porto / **Contratti** / Esci.

### 6.1 Registro del Capitano (ex "DIARIO") — `drawJournal`
Il vecchio diario è stato evoluto in **Registro del Capitano**, a 2 schede (sinistra/destra per cambiare):
- **MISSIONI**: lista UNICA (storia + secondarie insieme), **senza distinzione rosso/giallo**. Attive
  prima, poi completate ([>]=attiva, [x]=completata). A = dettaglio, su/giù = scorri.
  (`journalAllMissions()` unisce active red+yellow e done red+yellow.)
- **ECONOMIA** (sola lettura, `economyLines()`): stagione corrente, contratto attivo, rotta in corso,
  investimenti per porto/merce (livelli >0), oro e fama. È la "UI economica" che rende leggibile il motore.
- Marcatori "!" nel mondo: **tutti GIALLI** (`drawQuestMark`, `body="#ffd020"`), incluse le missioni
  di storia — nessun marcatore rosso.
- Le vecchie funzioni `journalActive/DoneRed/Yellow` restano come sorgenti dati per `journalAllMissions`.

---

## 7. Convenzioni e cose da NON rompere

- **Non cambiare le CHIAVI i18n** (es. `scooter_*`, `menu_*`) anche se il testo visibile è cambiato:
  sono ID usati dal codice. Cambia solo i VALORI (le stringhe tra virgolette).
- **`scooter`/`player.scooter`** sono identificatori di una meccanica DISATTIVATA (SELECT off). Le
  stringhe visibili sono state ritematizzate ("cavallo/sella") ma la logica è inerte: non riattivarla
  senza una decisione di design.
- Le mappe area devono avere **righe di uguale lunghezza**.
- Ogni modifica alla storia richiede di riallineare **pickup positions** e **SNODI**.
- Fai **backup** di `index.html` prima di modifiche grosse (nel repo ci sono molti `index.backup-*.html`).
- **Verifica sempre**: sintassi JS dei 3 blocchi `<script>`; completabilità storia (10/10); no-crash
  sulle 9 aree; i sistemi economici. (In questa sessione si sono usati harness headless in Node che
  stubbano DOM/Canvas/Audio, iniettano un export di stato interno e pilotano il game loop.)

---

## 8. Backlog / idee non ancora implementate

- **UI economica leggibile**: mostrare stock/tendenza prezzi, stagione corrente e catene nel menu
  Mercante (l'economia è ricca ma poco "visibile" al giocatore).
- **Order book leggero**: NPC che piazzano ordini visibili (raffinatezza, opzionale).
- Bilanciamento fine: frequenza eventi, reattività prezzi per merce, difficoltà tappe/naval.

## 9. Scelte di design esplicite (visione "A")
- SÌ: catene, contratti, trasporto/distanza, stagioni, eventi, investimenti.
- NO: stipendi manodopera, degrado/manutenzione edifici, order book pieno multiplayer. Questi
  renderebbero il gioco un "foglio di calcolo" e snaturerebbero l'avventura.
