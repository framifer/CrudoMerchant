# Crudo Merchant — PWA

Pacchetto pronto per [PWA Builder](https://www.pwabuilder.com/).

## Contenuto della cartella

```
crudo-merchant-pwa/
├── index.html              # il gioco (con link al manifest + registrazione service worker)
├── manifest.webmanifest    # metadati PWA (nome, icone, colori, display)
├── sw.js                   # service worker (offline / installabilita')
├── icons/
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── icon-192-maskable.png
│   └── icon-512-maskable.png
└── gen_icons.py            # script usato per rigenerare le icone (opzionale)
```

## Come pubblicare con PWA Builder

PWA Builder ha bisogno di un URL **pubblico in HTTPS**: non legge cartelle locali.
Devi quindi prima mettere online questi file, poi passare l'URL a PWA Builder.

1. **Pubblica i file** su un hosting statico con HTTPS, ad esempio:
   - GitHub Pages, Netlify, Cloudflare Pages, Amazon S3 + CloudFront, ecc.
   - Carica l'intera cartella mantenendo la struttura (index.html nella radice).

2. **Verifica** aprendo l'URL: il gioco deve caricarsi e il service worker
   registrarsi (DevTools → Application → Service Workers).

3. **Vai su https://www.pwabuilder.com/** e incolla l'URL pubblico.
   - PWA Builder analizza manifest, service worker e icone.
   - Da lì puoi generare i pacchetti per **Android (TWA)**, **iOS**, **Windows**.

## Test in locale (facoltativo)

Un service worker non funziona aprendo il file con `file://`. Serve un server HTTP:

```bash
cd crudo-merchant-pwa
python3 -m http.server 8000
# poi apri http://localhost:8000
```

## Note

- Le icone sono generate a tema (ancora dorata su sfondo scuro). Se vuoi
  sostituirle con un logo tuo, rimpiazza i PNG in `icons/` mantenendo
  nomi e dimensioni, oppure modifica `gen_icons.py` e rilancialo.
- `theme_color` e `background_color` seguono i colori gia' usati nel gioco.
- `orientation` e' impostato su `any` perche' il gioco supporta sia il
  layout Game Boy (verticale) sia il fullscreen orizzontale su telefono.
