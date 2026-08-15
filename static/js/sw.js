/* Niter Hub service worker — offline-first caching for the PWA shell.
 *
 * Strategy:
 *   - install:  precache the core static assets (theme/topbar/page CSS) plus
 *               the offline routes (/study-corner/, /transport/) and the
 *               app shell pages;
 *   - navigate: network-first with cache fallback, so the notes catalog and
 *               transport schedules stay fresh online but still render
 *               offline (falling back to the cached dashboard);
 *   - static:   cache-first with a background update (stale-while-revalidate),
 *               so deploys never serve a permanently stale stylesheet;
 *   - activate: delete caches from older VERSIONs.
 *
 * Bump VERSION when the precache list or caching rules change.
 */
var VERSION = 'v3';
var CACHE = 'niterhub-' + VERSION;

var PRECACHE = [
  '/manifest.json',
  '/',
  '/dashboard/',
  '/study-corner/',
  '/transport/',
  '/static/css/theme.css',
  '/static/css/topbar.css',
  '/static/css/main.css',
  '/static/css/dashboard.css',
  '/static/css/notes.css',
  '/static/css/study.css',
  '/static/css/transport.css',
  '/static/css/notices.css',
  '/static/css/editable_page.css',
  '/static/js/display-preferences.js',
  '/static/pwa/icon-192.png',
  '/static/pwa/icon-512.png',
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE)
      .then(function (cache) { return cache.addAll(PRECACHE); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(
          keys.filter(function (key) { return key !== CACHE; })
            .map(function (key) { return caches.delete(key); })
        );
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  var request = event.request;
  if (request.method !== 'GET') return;

  var url = new URL(request.url);

  // App shell / offline routes: network-first, cached copy when offline.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(function (response) {
          var copy = response.clone();
          caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
          return response;
        })
        .catch(function () {
          return caches.match(request).then(function (cached) {
            return cached || caches.match('/dashboard/');
          });
        })
    );
    return;
  }

  // Same-origin static assets + manifest: cache-first, refresh in background.
  if (
    url.origin === self.location.origin &&
    (url.pathname.indexOf('/static/') === 0 || url.pathname === '/manifest.json')
  ) {
    event.respondWith(
      caches.match(request).then(function (cached) {
        var update = fetch(request).then(function (response) {
          if (response.ok) {
            var copy = response.clone();
            caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
          }
          return response;
        }).catch(function () { return cached; });
        return cached || update;
      })
    );
    return;
  }

  // Everything else (APIs, cross-origin fonts/CDNs): network only.
});
