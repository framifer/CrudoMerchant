/* Crudo Merchant - Service Worker
 * Strategia: cache-first con precache di tutti gli asset del gioco.
 * Il gioco e' un unico file (index.html) piu' manifest e icone, quindi una volta
 * messo in cache funziona completamente offline.
 *
 * IMPORTANTE: quando modifichi index.html (o gli altri asset), incrementa CACHE_VERSION
 * cosi' il service worker scarica la nuova versione e ripulisce la vecchia cache.
 */
const CACHE_VERSION = "crudo-merchant-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png"
];

// Install: precache di tutti gli asset.
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(ASSETS))
  );
  // attiva subito il nuovo SW senza aspettare la chiusura delle tab
  self.skipWaiting();
});

// Activate: elimina le cache vecchie (versioni precedenti).
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch: cache-first. Se in cache la usa; altrimenti va in rete e mette in cache.
// Solo richieste GET same-origin (il gioco non ha dipendenze esterne).
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          // metti in cache una copia della risposta valida
          if (res && res.status === 200 && res.type === "basic") {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(req, copy));
          }
          return res;
        })
        .catch(() => {
          // offline e non in cache: per le navigazioni, ripiega su index.html
          if (req.mode === "navigate") return caches.match("./index.html");
        });
    })
  );
});
