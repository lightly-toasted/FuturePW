const CACHE_NAME = 'countdown-cache';
const urlsToCache = [
    '/',
    '/form.js',
    '/form.css',
    '/countdown.css',
    '/countdown.js',
    '/flying.gif',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(urlsToCache);
            })
    );
});