# Crudo Merchant — PWA offline

Cartella completa e pronta per essere installata come **Progressive Web App** (PWA)
installabile e funzionante **completamente offline**.

## Contenuto della cartella

| File            | A cosa serve |
|-----------------|--------------|
| `index.html`    | Il gioco completo (HTML + CSS + JS + dati, tutto inline). |
| `manifest.json` | Metadati PWA: nome, icone, colori, modalità standalone. |
| `sw.js`         | Service worker: mette in cache gli asset → il gioco funziona offline. |
| `icon-192.png`  | Icona 192×192 (schermata home / app list). |
| `icon-512.png`  | Icona 512×512 (splash screen / store). |
| `make_icons.py` | Script che rigenera le icone (solo se vuoi cambiarle). Non serve per giocare. |

> `index.html` già referenzia manifest, icone e registra `sw.js`: non devi modificare nulla.

## Come provarla / installarla

Una PWA richiede di essere **servita via HTTP(S)** (il service worker non parte con `file://`).

### In locale (per test)
```bash
cd crudo-merchant-pwa
python3 -m http.server 3000
```
Poi apri `http://localhost:3000` (o, in DevSpaces, il bottone **Connect** → porta 3000).

- **Chrome/Edge desktop**: comparirà l'icona "Installa" nella barra degli indirizzi.
- **Android (Chrome)**: menu ⋮ → "Aggiungi a schermata Home" / "Installa app".
- **iOS (Safari)**: Condividi → "Aggiungi a Home".

Dopo il primo caricamento online, il service worker mette in cache tutto:
da lì in poi il gioco **si apre anche senza rete**.

### Pubblicarla su un hosting
Carica gli stessi 5 file (index.html, manifest.json, sw.js, icon-192.png, icon-512.png)
nella stessa cartella di un qualsiasi hosting statico **HTTPS** (GitHub Pages, Netlify,
Amazon S3 + CloudFront, ecc.). La PWA è self-contained: nessun backend, nessuna dipendenza esterna.

## Aggiornare il gioco

Il service worker usa una cache versionata. Quando modifichi `index.html` (o altri asset):

1. Sostituisci il file.
2. Apri `sw.js` e **incrementa** `CACHE_VERSION` (es. `crudo-merchant-v1` → `crudo-merchant-v2`).

Al successivo avvio online, il service worker scarica la nuova versione, la mette in cache
e cancella quella vecchia. Senza cambiare la versione, gli utenti continuerebbero a vedere
la copia in cache.

## Note

- Il salvataggio della partita usa `localStorage` (chiave `crudoRPG.save.v2`) e funziona
  offline: i progressi restano sul dispositivo.
- Le icone sono un placeholder pixel-art (nave/vela oro su fondo notte). Per personalizzarle,
  sostituisci i due PNG mantenendo gli stessi nomi e dimensioni (192×192 e 512×512),
  oppure modifica ed esegui `make_icons.py`.
