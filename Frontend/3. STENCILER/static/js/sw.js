// sw.js — DÉSACTIVÉ 2026-02-23
// Ce SW se désinstalle et nettoie tous les caches pour éviter les interférences en dev.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.map(key => caches.delete(key))))
            .then(() => self.registration.unregister())
            .then(() => self.clients.claim())
    );
});
// Pas de listener fetch pour permettre un bypass immédiat au réseau
