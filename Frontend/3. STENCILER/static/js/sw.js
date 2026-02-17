const CACHE_NAME = 'sullivan-cache-v2';
const STATIC_ASSETS = [
    '/',
    '/stenciler',
    '/static/js/sullivan_engine.js',
    '/static/js/semantic_bridge.js',
    '/static/js/viewer.js',
    '/static/js/stenciler_app.js',
    '/static/css/viewer.css',
    '/static/css/stenciler.css'
];

// Installation : Mise en cache des assets statiques
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('🧬 SW: Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
});

// Activation : Nettoyage des anciens caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        })
    );
});

// Stratégie de Fetch
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Stratégie Stale-While-Revalidate pour l'API Genome
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            caches.open(CACHE_NAME).then(cache => {
                return cache.match(event.request).then(cachedResponse => {
                    const fetchPromise = fetch(event.request).then(networkResponse => {
                        // On ne peut mettre en cache que les requêtes GET réussies
                        if (event.request.method === 'GET' && networkResponse.ok) {
                            cache.put(event.request, networkResponse.clone());
                        }
                        return networkResponse;
                    }).catch(() => {
                        // Offline : retourner le cache si disponible
                        return cachedResponse || new Response(JSON.stringify({ error: "Offline mode active" }), {
                            headers: { 'Content-Type': 'application/json' }
                        });
                    });
                    return cachedResponse || fetchPromise;
                });
            })
        );
    }
    // Stratégie Cache-First pour les assets statiques
    else {
        event.respondWith(
            caches.match(event.request).then(response => {
                return response || fetch(event.request);
            })
        );
    }
});
