/* ============================================================================
   CampusDash — Website Builder Visual Editor
   ----------------------------------------------------------------------------
   Split-screen editor logic for templates/builder/editor.html.

   The canvas is a same-origin <iframe> of the live page. Editing a sidebar
   field updates the matching [data-editable-id] element inside the iframe in
   real time; "Publish / Save All" POSTs everything to the builder API and
   shows a toast.
   ========================================================================== */
(function () {
    'use strict';

    const body = document.body;
    const pageSlug = body.dataset.pageSlug;
    const saveBlockUrl = body.dataset.saveBlockUrl;
    const saveCssUrl = body.dataset.saveCssUrl;

    const iframe = document.getElementById('page-preview');
    const canvasFrame = document.getElementById('canvas-frame');
    const editorBody = document.getElementById('editor-body');
    const inspectorToggle = document.getElementById('inspector-toggle');
    const cssInput = document.getElementById('custom-css');
    const pageBgPicker = document.getElementById('page-bg');
    const blockBgPicker = document.getElementById('block-bg');
    const inspectorList = document.getElementById('inspector-blocks');
    const blockCount = document.getElementById('block-count');
    const liveToggle = document.getElementById('live-preview');
    const saveAllBtn = document.getElementById('save-all');
    const saveCssBtn = document.getElementById('save-css');
    const toastEl = document.getElementById('builder-toast');

    let doc = null;          // iframe contentDocument (same-origin)
    let previewStyle = null; // <style> injected into the iframe with user CSS
    let highlightStyle = null;
    let selectedId = null;
    let toastTimer = null;

    // ---------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------
    function getCookie(name) {
        let value = null;
        if (document.cookie && document.cookie !== '') {
            for (const part of document.cookie.split(';')) {
                const cookie = part.trim();
                if (cookie.startsWith(name + '=')) {
                    value = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return value;
    }

    async function postJSON(url, payload) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        });
        let data = {};
        try { data = await response.json(); } catch (e) { /* non-JSON body */ }
        if (!response.ok && !data.status) data = { status: 'error', message: 'HTTP ' + response.status };
        return data;
    }

    function showToast(message, ok) {
        toastEl.textContent = message;
        toastEl.classList.toggle('ok', !!ok);
        toastEl.classList.toggle('err', !ok);
        toastEl.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 3200);
    }

    // Insert or replace `selector { prop: value; }` inside a CSS string.
    // NOTE: the regex intentionally has no 'g' flag — a global regex would
    // advance lastIndex on test() and make the subsequent replace() miss.
    function setCssRule(css, selector, prop, value) {
        const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const re = new RegExp(escaped + '\\s*\\{[^}]*\\}');
        const block = selector + ' { ' + prop + ': ' + value + '; }';
        if (re.test(css)) return css.replace(re, block);
        return (css + '\n' + block).trim();
    }

    // ---------------------------------------------------------------------
    // iframe access (same-origin)
    // ---------------------------------------------------------------------
    function ensureDoc() {
        try { doc = iframe.contentDocument; } catch (e) { doc = null; }
        return doc;
    }

    function getPreviewStyle() {
        if (!doc) return null;
        if (!previewStyle) {
            previewStyle = doc.createElement('style');
            previewStyle.id = 'builder-preview-css';
            doc.head.appendChild(previewStyle);
        }
        return previewStyle;
    }

    function getHighlightStyle() {
        if (!doc) return null;
        if (!highlightStyle) {
            highlightStyle = doc.createElement('style');
            highlightStyle.id = 'builder-preview-highlight';
            doc.head.appendChild(highlightStyle);
        }
        return highlightStyle;
    }

    function applyCss() {
        const styleEl = getPreviewStyle();
        if (styleEl) styleEl.textContent = cssInput.value;
    }

    function applyHighlightState() {
        const styleEl = getHighlightStyle();
        if (!styleEl) return;
        if (!liveToggle.checked) {
            styleEl.textContent = [
                '[data-editable-id] { outline: 2px dashed rgba(39,39,42,.30); outline-offset: 3px; transition: outline-color .15s ease, background-color .15s ease; }',
                '[data-editable-id]:hover { outline-color: #27272a; }',
                '[data-editable-id].builder-selected { outline: 2px solid #27272a; background-color: rgba(232,226,216,.30); }',
            ].join('\n');
        } else {
            styleEl.textContent = '';
        }
    }

    // ---------------------------------------------------------------------
    // Inspector <-> canvas sync
    // ---------------------------------------------------------------------
    function iframeElement(id) {
        return doc ? doc.querySelector('[data-editable-id="' + id + '"]') : null;
    }

    function applyStyleToElement(id, input) {
        const el = iframeElement(id);
        if (!el) return;
        const edit = input.dataset.edit;
        let value = input.value.trim();

        if (edit === 'fontSize' && /^\d+$/.test(value)) value += 'px';

        if (edit === 'html') {
            el.innerHTML = input.value;
            return;
        }
        if (value) {
            el.style[edit] = value;
        } else {
            el.style[edit] = '';
        }
    }

    function buildItem(id, contentHtml) {
        const node = document.createElement('article');
        node.className = 'inspector-block';
        node.dataset.blockId = id;
        node.innerHTML =
            '<div class="inspector-block-head"><span class="block-id">#' + id + '</span>' +
            '<span class="block-actions" role="group" aria-label="Block actions">' +
            '<button type="button" class="block-action-btn" data-action="up" title="Move block up" aria-label="Move block up"><i class="fa-solid fa-arrow-up"></i></button>' +
            '<button type="button" class="block-action-btn" data-action="down" title="Move block down" aria-label="Move block down"><i class="fa-solid fa-arrow-down"></i></button>' +
            '<button type="button" class="block-action-btn danger" data-action="delete" title="Delete block" aria-label="Delete block"><i class="fa-solid fa-trash"></i></button>' +
            '</span></div>' +
            '<label class="inspector-field"><span>Content (HTML)</span>' +
            '<textarea rows="3" spellcheck="false" data-edit="html"></textarea></label>' +
            '<div class="inspector-styles">' +
            '<label class="inline-field"><span>Align</span><select data-edit="textAlign">' +
            '<option value="">Default</option><option value="left">Left</option>' +
            '<option value="center">Center</option><option value="right">Right</option></select></label>' +
            '<label class="inline-field"><span>Color</span><input type="color" data-edit="color" value="#1f2937"></label>' +
            '<label class="inline-field"><span>Font size</span><input type="number" data-edit="fontSize" min="8" max="96" placeholder="18"></label>' +
            '<label class="inline-field"><span>Padding</span><input type="text" data-edit="padding" placeholder="1rem"></label>' +
            '</div>';
        node.querySelector('[data-edit="html"]').value = contentHtml;
        wireItem(node, id);
        return node;
    }

    function wireItem(item, id) {
        if (item.dataset.wired === '1') return; // idempotent — server & dynamic cards
        item.dataset.wired = '1';
        item.querySelectorAll('[data-edit]').forEach(function (input) {
            input.addEventListener('input', function () {
                applyStyleToElement(id, input);
                if (id !== selectedId) selectItem(id, item);
            });
            input.addEventListener('focus', function () {
                selectItem(id, item);
            });
        });
        item.addEventListener('click', function (e) {
            if (e.target.closest('textarea, input, select, .block-actions')) return;
            selectItem(id, item);
            const el = iframeElement(id);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        // Block management handles: move up / move down / delete.
        const upBtn = item.querySelector('[data-action="up"]');
        const downBtn = item.querySelector('[data-action="down"]');
        const deleteBtn = item.querySelector('[data-action="delete"]');
        if (upBtn) upBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            moveBlock(item, -1);
        });
        if (downBtn) downBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            moveBlock(item, 1);
        });
        if (deleteBtn) deleteBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            deleteBlock(item);
        });
    }

    function blockItems() {
        return Array.from(inspectorList.querySelectorAll('.inspector-block'));
    }

    function refreshBlockActionState() {
        const items = blockItems();
        items.forEach(function (item, i) {
            const upBtn = item.querySelector('[data-action="up"]');
            const downBtn = item.querySelector('[data-action="down"]');
            if (upBtn) upBtn.disabled = i === 0;
            if (downBtn) downBtn.disabled = i === items.length - 1;
        });
    }

    function refreshCanvas() {
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.location.reload();
        }
    }

    async function moveBlock(item, dir) {
        const items = blockItems();
        const index = items.indexOf(item);
        const target = index + dir;
        if (target < 0 || target >= items.length) return;
        const originalOrder = blockItems().slice();
        // Swap in the DOM first so the change is visible instantly.
        if (dir < 0) {
            inspectorList.insertBefore(item, items[target]);
        } else {
            inspectorList.insertBefore(items[target], item);
        }
        refreshBlockActionState();
        // Persist the whole order in ONE atomic reorder call.
        const reorder = blockItems().map(function (n, i) {
            return { element_id: n.dataset.blockId, order: i };
        });
        const data = await postJSON(saveBlockUrl, { page_slug: pageSlug, reorder: reorder });
        if (data.status === 'success') {
            showToast('Block order saved — refreshing canvas…', true);
            refreshCanvas();
        } else {
            // Revert the optimistic swap so the UI always matches the DB.
            originalOrder.forEach(function (node) { inspectorList.appendChild(node); });
            refreshBlockActionState();
            showToast('Reorder failed — order restored.', false);
        }
    }

    async function deleteBlock(item) {
        const id = item.dataset.blockId;
        if (!confirm('Delete block #' + id + '? This cannot be undone.')) return;
        const data = await postJSON(saveBlockUrl, { page_slug: pageSlug, element_id: id, delete: true });
        if (data.status === 'success') {
            item.remove();
            refreshBlockActionState();
            if (blockCount) {
                blockCount.textContent = inspectorList.querySelectorAll('.inspector-block').length;
            }
            showToast('Block deleted — refreshing canvas…', true);
            refreshCanvas();
        } else {
            showToast('Delete failed — please try again.', false);
        }
    }

    function selectItem(id, item) {
        selectedId = id;
        inspectorList.querySelectorAll('.inspector-block').forEach(function (n) {
            n.classList.toggle('active', n === item);
        });
        const el = iframeElement(id);
        if (el) {
            doc.querySelectorAll('.builder-selected').forEach(function (n) {
                n.classList.remove('builder-selected');
            });
            el.classList.add('builder-selected');
        }
    }

    function syncInspector() {
        if (!doc) return;
        const ids = Array.from(doc.querySelectorAll('[data-editable-id]'))
            .map(function (el) { return el.getAttribute('data-editable-id'); });
        let added = 0;
        ids.forEach(function (id) {
            if (!inspectorList.querySelector('[data-block-id="' + id + '"]')) {
                const el = doc.querySelector('[data-editable-id="' + id + '"]');
                inspectorList.appendChild(buildItem(id, el.innerHTML));
                added += 1;
            }
        });
        if (added) blockCount.textContent = inspectorList.querySelectorAll('.inspector-block').length;
    }

    function wireClickToSelect() {
        if (!doc) return;
        doc.addEventListener('click', function (e) {
            const el = e.target.closest('[data-editable-id]');
            if (!el) return;
            const id = el.getAttribute('data-editable-id');
            let item = inspectorList.querySelector('[data-block-id="' + id + '"]');
            if (!item) {
                item = buildItem(id, el.innerHTML);
                inspectorList.appendChild(item);
                if (blockCount) {
                    blockCount.textContent = inspectorList.querySelectorAll('.inspector-block').length;
                }
            }
            selectItem(id, item);
        });
    }

    // ---------------------------------------------------------------------
    // Color pickers -> custom_css
    // ---------------------------------------------------------------------
    function bindColorPicker(picker, selector, prop) {
        picker.addEventListener('input', function () {
            cssInput.value = setCssRule(cssInput.value, selector, prop, picker.value);
            applyCss();
        });
    }

    // ---------------------------------------------------------------------
    // Save All
    // ---------------------------------------------------------------------
    function collectBlockPayload(item) {
        const id = item.dataset.blockId;
        const html = item.querySelector('[data-edit="html"]').value;
        const style = {};
        item.querySelectorAll('[data-edit]').forEach(function (input) {
            if (input.dataset.edit === 'html') return;
            const value = input.value.trim();
            if (value) style[input.dataset.edit] = value;
        });
        return { page_slug: pageSlug, element_id: id, content_html: html, style_json: style };
    }

    saveAllBtn.addEventListener('click', async function () {
        saveAllBtn.disabled = true;
        const requests = [postJSON(saveCssUrl, { page_slug: pageSlug, custom_css: cssInput.value })];

        inspectorList.querySelectorAll('.inspector-block').forEach(function (item) {
            requests.push(postJSON(saveBlockUrl, collectBlockPayload(item)));
        });

        const settled = await Promise.allSettled(requests);
        const ok = settled.every(function (r) {
            return r.status === 'fulfilled' && r.value && r.value.status === 'success';
        });
        saveAllBtn.disabled = false;
        showToast(
            ok ? 'All changes saved & published ✓' : 'Some changes failed to save — check the fields and try again.',
            ok
        );
    });

    // ---------------------------------------------------------------------
    // Save CSS — persist, then inject straight into the iframe <head>.
    // No page reload: typing already previews live; this button persists it
    // and re-applies the <style> block in place.
    // ---------------------------------------------------------------------
    if (saveCssBtn) {
        saveCssBtn.addEventListener('click', async function () {
            saveCssBtn.disabled = true;
            const data = await postJSON(saveCssUrl, { page_slug: pageSlug, custom_css: cssInput.value });
            saveCssBtn.disabled = false;
            if (data.status === 'success') {
                applyCss(); // re-inject into the live iframe <head>
                showToast('Custom CSS saved & injected ✓', true);
            } else {
                showToast('Failed to save CSS — try again.', false);
            }
        });
    }

    // ---------------------------------------------------------------------
    // Viewport switcher
    // ---------------------------------------------------------------------
    document.querySelectorAll('.viewport-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.viewport-btn').forEach(function (b) {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            canvasFrame.dataset.viewport = btn.dataset.viewport;
            const widths = { desktop: 'fluid', tablet: '768px', mobile: '375px' };
            showToast('Preview: ' + btn.textContent.trim() + ' (' + (widths[btn.dataset.viewport] || 'fluid') + ')', true);
        });
    });

    // ---------------------------------------------------------------------
    // Live preview toggle (edit highlights on/off)
    // ---------------------------------------------------------------------
    liveToggle.addEventListener('change', function () {
        applyHighlightState();
        showToast(liveToggle.checked ? 'Live preview — as visitors see it' : 'Edit mode — click any block to edit', true);
    });

    // ---------------------------------------------------------------------
    // Inspector collapse
    // ---------------------------------------------------------------------
    inspectorToggle.addEventListener('click', function () {
        const collapsed = editorBody.classList.toggle('inspector-collapsed');
        inspectorToggle.setAttribute('aria-expanded', String(!collapsed));
        inspectorToggle.querySelector('i').className = collapsed ? 'fa-solid fa-angles-right' : 'fa-solid fa-angles-left';
    });

    // ---------------------------------------------------------------------
    // Init
    // ---------------------------------------------------------------------
    iframe.addEventListener('load', function () {
        // The iframe may have navigated (link clicks, reloads), which destroys
        // the old document and its injected <style> elements — drop stale refs.
        previewStyle = null;
        highlightStyle = null;
        ensureDoc();
        applyCss();
        applyHighlightState();
        syncInspector();
        wireClickToSelect();
    });

    // Wire the server-rendered inspector cards (edits + action handles) and
    // initialise the move-button disabled state.
    inspectorList.querySelectorAll('.inspector-block').forEach(function (item) {
        wireItem(item, item.dataset.blockId);
    });
    refreshBlockActionState();

    cssInput.addEventListener('input', applyCss);
    bindColorPicker(pageBgPicker, 'body', 'background-color');
    bindColorPicker(blockBgPicker, '.content-block', 'background-color');

    // Re-sync if the page is already cached/loaded
    if (iframe.contentDocument && iframe.contentDocument.readyState === 'complete') {
        iframe.dispatchEvent(new Event('load'));
    }

    // ---------------------------------------------------------------------
    // WYSIWYG overlay — inline text editing + floating style toolbar
    // ---------------------------------------------------------------------
    // Server-rendered block state (type + style per element) for the canvas.
    const wysiwygBlocks = (function () {
        try {
            return JSON.parse(document.getElementById('wysiwyg-blocks').textContent);
        } catch (e) { return []; }
    })();
    const blockMeta = {};
    wysiwygBlocks.forEach(function (b) {
        blockMeta[b.element_id] = { block_type: b.block_type || 'html', style: b.style || {} };
    });

    const wysiwygSaveUrl = body.dataset.wysiwygSaveUrl;
    const pageId = body.dataset.pageId;
    const wysiwygToolbar = document.getElementById('wysiwyg-toolbar');
    const fontSizeInput = document.getElementById('wysiwyg-font-size');
    const colorInput = document.getElementById('wysiwyg-color');
    const bgInput = document.getElementById('wysiwyg-bg');
    const alignButtons = Array.from(document.querySelectorAll('.wysiwyg-align-btn'));
    const editTextBtn = document.getElementById('wysiwyg-edit-text');
    const wysiwygCloseBtn = document.getElementById('wysiwyg-close');
    const targetLabel = document.getElementById('wysiwyg-target');
    const publishBtn = document.getElementById('publish-page');

    let selectedBlockId = null;
    let selectedSection = null;
    const dirtyBlocks = {};   // element_id -> { content_html?, style_json? }

    function blockType(id) { return (blockMeta[id] || {}).block_type || 'html'; }
    function isHtmlBlock(id) { return blockType(id) === 'html'; }

    function readBlockStyle(id) {
        const base = (blockMeta[id] || {}).style || {};
        const dirty = (dirtyBlocks[id] || {}).style_json || {};
        return Object.assign({}, base, dirty);
    }

    function applyToolbarStyleToSection(id) {
        const el = iframeElement(id);
        if (!el) return;
        const style = readBlockStyle(id);
        ['fontSize', 'color', 'backgroundColor', 'textAlign'].forEach(function (prop) {
            if (style[prop]) el.style[prop] = style[prop];
        });
    }

    function setStyleProp(id, key, value) {
        if (!dirtyBlocks[id]) dirtyBlocks[id] = {};
        if (!dirtyBlocks[id].style_json) dirtyBlocks[id].style_json = {};
        if (value === '' || value == null) {
            delete dirtyBlocks[id].style_json[key];
        } else {
            dirtyBlocks[id].style_json[key] = value;
        }
        applyToolbarStyleToSection(id);
    }

    function populateToolbar(id) {
        const style = readBlockStyle(id);
        const size = parseInt(style.fontSize || '', 10);
        fontSizeInput.value = isNaN(size) ? '' : String(size);
        colorInput.value = style.color || '#1f2937';
        bgInput.value = style.backgroundColor || '#ffffff';
        alignButtons.forEach(function (btn) {
            btn.classList.toggle('active', style.textAlign === btn.dataset.align);
        });
        targetLabel.textContent = '#' + id;
        editTextBtn.disabled = !isHtmlBlock(id);
        editTextBtn.innerHTML = isHtmlBlock(id)
            ? '<i class="fa-solid fa-pen"></i> Edit text'
            : '<i class="fa-solid fa-pen"></i> Text blocks only';
    }

    function positionToolbar() {
        if (!wysiwygToolbar || !doc || !selectedSection) return;
        const frameRect = canvasFrame.getBoundingClientRect();
        const elRect = selectedSection.getBoundingClientRect();
        const toolbarW = wysiwygToolbar.offsetWidth || 280;
        const toolbarH = wysiwygToolbar.offsetHeight || 150;
        let left = frameRect.left + elRect.left + 8;
        let top = frameRect.top + elRect.top - toolbarH - 10;
        if (top < frameRect.top + 8) top = frameRect.top + elRect.bottom + 8;
        left = Math.max(frameRect.left + 4, Math.min(left, frameRect.right - toolbarW - 4));
        wysiwygToolbar.style.left = left + 'px';
        wysiwygToolbar.style.top = top + 'px';
        wysiwygToolbar.hidden = false;
    }

    function showToolbarFor(id) {
        if (liveToggle.checked) return; // live preview — no editing chrome
        selectedBlockId = id;
        selectedSection = iframeElement(id);
        if (!selectedSection) return;
        populateToolbar(id);
        positionToolbar();
    }

    function hideToolbar() {
        if (wysiwygToolbar) wysiwygToolbar.hidden = true;
        selectedBlockId = null;
        selectedSection = null;
    }

    function commitInlineEdit(id, section) {
        if (!section || section.getAttribute('contenteditable') !== 'true') return;
        section.contentEditable = 'false';
        const html = section.innerHTML.trim();
        if (!dirtyBlocks[id]) dirtyBlocks[id] = {};
        if (dirtyBlocks[id].content_html !== html) {
            dirtyBlocks[id].content_html = html;
            showToast('Text edited — Save Changes to persist', true);
        }
    }

    function enableInlineEdit(id) {
        const section = iframeElement(id);
        if (!section) return;
        section.contentEditable = 'true';
        section.focus();
        showToast('Editing text on the canvas — click away when done', true);
    }

    // Click a text element / section on the canvas → floating style toolbar.
    function wireWysiwygClicks() {
        if (!doc) return;
        doc.addEventListener('click', function (e) {
            if (liveToggle.checked) return;
            const section = e.target.closest('[data-editable-id]');
            if (!section) return;
            showToolbarFor(section.getAttribute('data-editable-id'));
        });
        // Double-click text on an html block → inline contenteditable editing.
        doc.addEventListener('dblclick', function (e) {
            if (liveToggle.checked) return;
            const section = e.target.closest('[data-editable-id]');
            if (!section) return;
            const id = section.getAttribute('data-editable-id');
            if (isHtmlBlock(id)) enableInlineEdit(id);
        });
        doc.addEventListener('focusout', function (e) {
            const section = e.target.closest ? e.target.closest('[data-editable-id]') : null;
            if (!section) return;
            commitInlineEdit(section.getAttribute('data-editable-id'), section);
        });
        doc.addEventListener('input', function (e) {
            const section = e.target.closest ? e.target.closest('[data-editable-id]') : null;
            if (!section) return;
            const id = section.getAttribute('data-editable-id');
            if (isHtmlBlock(id)) {
                if (!dirtyBlocks[id]) dirtyBlocks[id] = {};
                dirtyBlocks[id].content_html = section.innerHTML.trim();
            }
        });
    }

    function collectSaveBlocks() {
        const blocks = [];
        const seen = {};
        // Inspector blocks (content + styles edited in the left sidebar).
        inspectorList.querySelectorAll('.inspector-block').forEach(function (item) {
            const payload = collectBlockPayload(item);
            blocks.push(payload);
            seen[payload.element_id] = true;
        });
        // WYSIWYG dirty blocks (canvas text edits + toolbar styles).
        Object.keys(dirtyBlocks).forEach(function (id) {
            const dirty = dirtyBlocks[id];
            const payload = { page_slug: pageSlug, element_id: id };
            if (dirty.content_html) payload.content_html = dirty.content_html;
            if (dirty.style_json && Object.keys(dirty.style_json).length) payload.style_json = dirty.style_json;
            if (seen[id]) {
                const existing = blocks.find(function (b) { return b.element_id === id; });
                Object.assign(existing, payload);
            } else {
                blocks.push(payload);
            }
        });
        return blocks;
    }

    // ---- Top-bar: Save Changes (POST /api/builder/pages/<id>/save/) ----
    if (wysiwygSaveUrl) {
        saveAllBtn.addEventListener('click', async function () {
            saveAllBtn.disabled = true;
            const requests = [];
            const blocks = collectSaveBlocks();
            if (blocks.length) {
                requests.push(postJSON(wysiwygSaveUrl, { page_id: Number(pageId), blocks: blocks }));
            }
            requests.push(postJSON(saveCssUrl, { page_slug: pageSlug, custom_css: cssInput.value }));
            const settled = await Promise.allSettled(requests);
            const ok = settled.every(function (r) {
                return r.status === 'fulfilled' && r.value && r.value.status === 'success';
            });
            saveAllBtn.disabled = false;
            if (ok) {
                // Flush the dirty map — everything just saved.
                Object.keys(dirtyBlocks).forEach(function (id) { delete dirtyBlocks[id]; });
                showToast('All changes saved ✓', true);
            } else {
                showToast('Some changes failed to save — check the fields and try again.', false);
            }
        });

        // ---- Top-bar: Publish Page (toggles is_published live) ----
        publishBtn.addEventListener('click', async function () {
            publishBtn.disabled = true;
            const payload = { page_id: Number(pageId), is_published: true };
            const blocks = collectSaveBlocks();
            if (blocks.length) payload.blocks = blocks;
            const data = await postJSON(wysiwygSaveUrl, payload);
            publishBtn.disabled = false;
            if (data.status === 'success') {
                publishBtn.dataset.published = 'true';
                showToast('Page published — live for visitors ✓', true);
            } else {
                showToast('Publish failed — try again.', false);
            }
        });
    }

    // ---- Floating toolbar controls ----
    if (wysiwygToolbar) {
        fontSizeInput.addEventListener('input', function () {
            if (!selectedBlockId) return;
            const v = fontSizeInput.value.trim();
            setStyleProp(selectedBlockId, 'fontSize', v ? v + 'px' : '');
        });
        colorInput.addEventListener('input', function () {
            if (selectedBlockId) setStyleProp(selectedBlockId, 'color', colorInput.value);
        });
        bgInput.addEventListener('input', function () {
            if (selectedBlockId) setStyleProp(selectedBlockId, 'backgroundColor', bgInput.value);
        });
        alignButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (!selectedBlockId) return;
                const value = btn.dataset.align;
                setStyleProp(selectedBlockId, 'textAlign', value);
                alignButtons.forEach(function (b) { b.classList.toggle('active', b === btn); });
            });
        });
        editTextBtn.addEventListener('click', function () {
            if (!selectedBlockId) return;
            if (isHtmlBlock(selectedBlockId)) enableInlineEdit(selectedBlockId);
        });
        wysiwygCloseBtn.addEventListener('click', hideToolbar);
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && wysiwygToolbar && !wysiwygToolbar.hidden) hideToolbar();
        });
        // Keep the toolbar pinned to the section on canvas scroll/resize.
        if (doc) doc.addEventListener('scroll', positionToolbar, { passive: true });
        window.addEventListener('resize', positionToolbar);
    }

    // Wire WYSIWYG after each iframe navigation (the existing load handler
    // re-syncs the inspector; this one re-arms the canvas editing overlay).
    iframe.addEventListener('load', function () {
        ensureDoc();
        hideToolbar();
        wireWysiwygClicks();
    });
})();
