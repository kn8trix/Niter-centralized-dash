/* Register the PWA service worker (scope /) after the page finishes loading.
 * Failures are logged, never fatal — the site works without a service worker. */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').catch(function (err) {
      console.warn('Service worker registration failed:', err);
    });
  });
}
