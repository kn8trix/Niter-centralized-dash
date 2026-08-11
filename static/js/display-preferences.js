/* ============================================================================
   CampusDash — Global Display Preferences driver
   ----------------------------------------------------------------------------
   Owns the portal-wide theme (light / dark / system), timezone and layout
   density preferences:

   - Applies the active theme by toggling the `dark` class on <html> (and
     <body>) and stamping `data-theme` / `data-theme-mode` / `data-density`
     attributes — every stylesheet (theme.css tokens, Tailwind utilities,
     component CSS) keys off those hooks, including the Website Builder and
     builder-authored public pages.
   - 'system' mode follows `prefers-color-scheme` live via matchMedia.
   - Persists to localStorage (device) and, for signed-in users, syncs the
     account copy over AJAX to the /settings/ endpoint.
   - Emits a `display-prefs-change` event (and a `display-prefs-ready` event)
     so the settings page and other scripts can stay in sync.

   Loaded deferred from templates/partials/display_prefs.html, which already
   applied the saved values to <html> synchronously to avoid a flash.
   ========================================================================== */
(function () {
    'use strict';

    var CONFIG_KEY = 'niter.display.prefs';
    var VALID_THEMES = { light: true, dark: true, system: true };
    var VALID_DENSITIES = { comfortable: true, compact: true };

    // ---- Config from the head partial (server prefs + save endpoint) --------
    var config = { saveUrl: null, authenticated: false };
    var configEl = document.getElementById('display-prefs-config');
    if (configEl) {
        try {
            var parsed = JSON.parse(configEl.textContent || 'null');
            if (parsed && typeof parsed === 'object') config = parsed;
        } catch (e) { /* ignore malformed config */ }
    }
    var hasServerPrefs = Boolean(config.theme || config.density || config.timezone);

    // ---- Prefs state ----------------------------------------------------------
    // Start from the no-flash snapshot (already applied to <html>), then let
    // localStorage refine it; signed-in account prefs (server) win on load.
    var initial = (typeof window.__displayPrefsInitial === 'object' && window.__displayPrefsInitial) || {};
    var prefs = {
        theme: VALID_THEMES[initial.theme] ? initial.theme : 'light',
        density: VALID_DENSITIES[initial.density] ? initial.density : 'comfortable',
        timezone: initial.timezone || null,
    };
    try {
        var stored = JSON.parse(localStorage.getItem(CONFIG_KEY) || 'null');
        if (stored && typeof stored === 'object') {
            if (VALID_THEMES[stored.theme]) prefs.theme = stored.theme;
            if (VALID_DENSITIES[stored.density]) prefs.density = stored.density;
            if (stored.timezone) prefs.timezone = stored.timezone;
        }
    } catch (e) { /* storage unavailable (private mode) — in-memory only */ }

    if (config.authenticated && hasServerPrefs) {
        if (VALID_THEMES[config.theme]) prefs.theme = config.theme;
        if (VALID_DENSITIES[config.density]) prefs.density = config.density;
        if (config.timezone) prefs.timezone = config.timezone;
    }

    // ---- matchMedia for 'system' theme ---------------------------------------
    var systemQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

    function resolveTheme(mode) {
        if (mode === 'system') {
            return systemQuery && systemQuery.matches ? 'dark' : 'light';
        }
        return mode === 'dark' ? 'dark' : 'light';
    }

    // ---- Apply to the DOM ------------------------------------------------------
    function apply() {
        var mode = VALID_THEMES[prefs.theme] ? prefs.theme : 'light';
        var resolved = resolveTheme(mode);
        var density = VALID_DENSITIES[prefs.density] ? prefs.density : 'comfortable';
        var root = document.documentElement;
        root.setAttribute('data-theme', resolved);
        root.setAttribute('data-theme-mode', mode);
        root.setAttribute('data-density', density);
        root.classList.toggle('dark', resolved === 'dark');
        if (document.body) document.body.classList.toggle('dark', resolved === 'dark');
        return resolved;
    }

    function persist() {
        try { localStorage.setItem(CONFIG_KEY, JSON.stringify(prefs)); } catch (e) { /* private mode */ }
    }

    // ---- Server sync (optional AJAX to the UserProfile/settings endpoint) ------
    function getCookie(name) {
        var value = null;
        if (document.cookie && document.cookie !== '') {
            for (var _i = 0, parts = document.cookie.split(';'); _i < parts.length; _i++) {
                var cookie = parts[_i].trim();
                if (cookie.indexOf(name + '=') === 0) {
                    value = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return value;
    }

    function saveToServer(patch) {
        if (!config.saveUrl || !config.authenticated) return Promise.resolve(null);
        // Translate the driver's localStorage keys to the backend's field
        // names: density ('compact' | 'comfortable') → compact_layout (bool).
        var payload = {};
        Object.keys(patch).forEach(function (key) {
            if (key === 'density') payload.compact_layout = patch.density === 'compact';
            else payload[key] = patch[key];
        });
        return fetch(config.saveUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        })
            .then(function (r) { return r.json().catch(function () { return null; }); })
            .catch(function () { return null; });
    }

    // ---- Public API --------------------------------------------------------------
    /**
     * Update preferences: `set({ theme: 'dark', density: 'compact' })`.
     * Applies instantly, persists to localStorage, syncs the account copy via
     * AJAX (signed-in users) and fires `display-prefs-change`.
     * Returns the save promise (resolves null when skipped).
     */
    function set(patch) {
        var changed = false;
        if (patch && typeof patch === 'object') {
            Object.keys(patch).forEach(function (key) {
                if (prefs[key] !== patch[key]) {
                    prefs[key] = patch[key];
                    changed = true;
                }
            });
        }
        if (!changed) return Promise.resolve(null);
        persist();
        apply();
        document.dispatchEvent(new CustomEvent('display-prefs-change', {
            detail: Object.assign({}, prefs),
        }));
        return saveToServer(patch);
    }

    function get(key) {
        return key ? prefs[key] : Object.assign({}, prefs);
    }

    // Live 'system' mode: re-apply when the OS theme flips.
    function onSystemChange() {
        if (prefs.theme === 'system') apply();
    }
    if (systemQuery) {
        if (systemQuery.addEventListener) systemQuery.addEventListener('change', onSystemChange);
        else if (systemQuery.addListener) systemQuery.addListener(onSystemChange); // Safari < 14
    }

    apply();

    window.DisplayPrefs = { get: get, set: set, apply: apply };

    // Tell late scripts (e.g. the settings page UI) we are ready and synced.
    document.dispatchEvent(new CustomEvent('display-prefs-ready', {
        detail: Object.assign({}, prefs),
    }));
})();
