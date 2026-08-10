/* ============================================================================
   Page Builder (builder/edit_page.html) — drag-and-drop block manager.
   ----------------------------------------------------------------------------
   Wires the page-settings toolbar (Save Draft / Publish / toggles / SEO),
   drag-and-drop block reordering (atomic POST to /builder/api/blocks/reorder/),
   the section palette (adds blocks via /builder/api/blocks/save/), and the
   inline block editor. All mutations refresh the live preview iframe without
   a full page reload.
   ========================================================================== */
(function () {
    'use strict';

    var body = document.body;
    var PAGE_SLUG = body.dataset.pageSlug;
    var URLS = {
        pageSave: body.dataset.pageSaveUrl,
        blocksSave: body.dataset.blocksSaveUrl,
        blocksReorder: body.dataset.blocksReorderUrl,
    };

    var toast = document.getElementById('pb-toast');
    var titleInput = document.getElementById('pb-title');
    var publishedToggle = document.getElementById('pb-published');
    var navToggle = document.getElementById('pb-nav');
    var seoInput = document.getElementById('pb-seo');
    var saveDraftBtn = document.getElementById('pb-save-draft');
    var publishBtn = document.getElementById('pb-publish');
    var preview = document.getElementById('pb-preview');
    var list = document.getElementById('pb-block-list');
    var addBtn = document.getElementById('pb-add-block');
    var palette = document.getElementById('pb-palette');
    var editor = document.getElementById('pb-editor');
    var editorEid = document.getElementById('pb-editor-eid');
    var editorType = document.getElementById('pb-editor-type');
    var editorHtml = document.getElementById('pb-editor-html');
    var editorJson = document.getElementById('pb-editor-json');

    function getCookie(name) {
        if (!document.cookie || document.cookie === '') return null;
        for (var _a = document.cookie.split(';'), i = 0; i < _a.length; i++) {
            var pair = _a[i].trim();
            if (pair.indexOf(name + '=') === 0) {
                return decodeURIComponent(pair.slice(name.length + 1));
            }
        }
        return null;
    }

    function showToast(message, isError) {
        toast.textContent = message;
        toast.classList.toggle('error', !!isError);
        toast.classList.add('show');
        clearTimeout(window.__pbToastTimer);
        window.__pbToastTimer = setTimeout(function () {
            toast.classList.remove('show');
        }, 2600);
    }

    function postJson(url, payload) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        }).then(function (response) {
            return response.json().catch(function () { return {}; }).then(function (data) {
                return { ok: response.ok, data: data };
            });
        });
    }

    function refreshPreview() {
        if (preview && preview.contentWindow) {
            preview.contentWindow.location.reload();
        }
    }

    function requestFailed() {
        showToast('Request failed — check your connection and try again.', true);
    }

    /* ------------------------------------------------------------------ */
    /* Page settings — Save Draft / Publish                                */
    /* ------------------------------------------------------------------ */
    function savePage(publish) {
        saveDraftBtn.disabled = true;
        publishBtn.disabled = true;
        postJson(URLS.pageSave, {
            page_slug: PAGE_SLUG,
            title: titleInput.value,
            is_published: !!publish,
            show_in_nav: navToggle.checked,
            seo_description: seoInput.value,
        }).then(function (_a) {
            saveDraftBtn.disabled = false;
            publishBtn.disabled = false;
            if (!_a.ok) {
                showToast((_a.data && _a.data.message) || 'Could not save the page.', true);
                return;
            }
            publishedToggle.checked = !!_a.data.is_published;
            showToast(publish ? 'Page published.' : 'Draft saved.');
            refreshPreview();
        }).catch(function () {
            saveDraftBtn.disabled = false;
            publishBtn.disabled = false;
            requestFailed();
        });
    }

    if (saveDraftBtn) saveDraftBtn.addEventListener('click', function () { savePage(false); });
    if (publishBtn) publishBtn.addEventListener('click', function () { savePage(true); });

    /* ------------------------------------------------------------------ */
    /* Drag & drop block reordering (atomic reorder endpoint)              */
    /* ------------------------------------------------------------------ */
    var dragItem = null;

    function getDragAfterElement(container, y) {
        var items = Array.prototype.slice.call(container.querySelectorAll('.pb-item:not(.dragging)'));
        return items.reduce(function (closest, child) {
            var box = child.getBoundingClientRect();
            var offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            }
            return closest;
        }, { offset: Number.NEGATIVE_INFINITY, element: null }).element;
    }

    if (list) {
        list.addEventListener('dragstart', function (e) {
            var item = e.target.closest('.pb-item');
            if (!item) return;
            dragItem = item;
            item.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            try { e.dataTransfer.setData('text/plain', item.dataset.blockId); } catch (err) {}
        });

        list.addEventListener('dragend', function (e) {
            var item = e.target.closest('.pb-item');
            if (item) item.classList.remove('dragging');
            dragItem = null;
        });

        list.addEventListener('dragover', function (e) {
            if (!dragItem) return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            var after = getDragAfterElement(list, e.clientY);
            if (after == null) list.appendChild(dragItem);
            else list.insertBefore(dragItem, after);
        });

        list.addEventListener('drop', function (e) {
            e.preventDefault();
            if (!dragItem) return;
            dragItem.classList.remove('dragging');
            var ids = Array.prototype.map.call(
                list.querySelectorAll('.pb-item'),
                function (el) { return el.dataset.blockId; }
            );
            dragItem = null;

            postJson(URLS.blocksReorder, {
                page_slug: PAGE_SLUG,
                reorder: ids.map(function (elementId, index) {
                    return { element_id: elementId, order: index };
                }),
            }).then(function (_a) {
                if (!_a.ok) {
                    showToast((_a.data && _a.data.message) || 'Reorder failed.', true);
                    location.reload(); // restore the server order
                    return;
                }
                showToast('Block order saved.');
                refreshPreview();
            }).catch(requestFailed);
        });
    }

    /* ------------------------------------------------------------------ */
    /* Section palette — add a block of the chosen type                    */
    /* ------------------------------------------------------------------ */
    var DEFAULTS = {
        html: '<h2>New section</h2><p>Write your content here.</p>',
        hero: { headline: 'A bold headline', subheadline: 'Supporting line', primary_label: 'Learn More', primary_url: '/departments/' },
        features: { title: 'Why choose us', items: [{ icon: 'fa-star', title: 'Feature', text: 'Describe it here.' }] },
        faq: { title: 'FAQs', items: [{ question: 'A question?', answer: 'An answer.' }] },
        stats: { title: 'At a glance', items: [{ value: '100+', label: 'Highlight', icon: 'fa-chart-simple' }] },
        testimonials: { title: 'What people say', items: [{ quote: 'A quote worth sharing.', author: 'Name', title: 'Role' }] },
        cta: { headline: 'Ready to start?', subtext: 'Join us today.', primary_label: 'Apply Now', primary_url: '/signup/' },
    };

    if (addBtn && palette) {
        addBtn.addEventListener('click', function () {
            var open = palette.hidden;
            palette.hidden = !open;
            addBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });

        palette.addEventListener('click', function (e) {
            var btn = e.target.closest('.pb-palette-item');
            if (!btn) return;
            var type = btn.dataset.blockType;
            palette.hidden = true;
            addBtn.setAttribute('aria-expanded', 'false');

            var elementId = type + '-' + Math.floor(Date.now() / 1000).toString(36);
            postJson(URLS.blocksSave, {
                page_slug: PAGE_SLUG,
                element_id: elementId,
                block_type: type,
                content_html: type === 'html' ? DEFAULTS.html : '',
                content_json: type === 'html' ? {} : (DEFAULTS[type] || {}),
            }).then(function (_a) {
                if (!_a.ok) {
                    showToast((_a.data && _a.data.message) || 'Could not add block.', true);
                    return;
                }
                showToast('Block added.');
                location.reload(); // refresh list + preview from the server
            }).catch(requestFailed);
        });
    }

    /* ------------------------------------------------------------------ */
    /* Inline block editor                                                 */
    /* ------------------------------------------------------------------ */
    var blocksData = {};
    try {
        var raw = document.getElementById('pb-blocks-data');
        if (raw) blocksData = JSON.parse(raw.textContent) || {};
    } catch (err) { blocksData = {}; }

    function parseJson(text) {
        try { return JSON.parse(text); } catch (err) { return null; }
    }

    function closeEditor() {
        editor.hidden = true;
        var active = document.querySelectorAll('.pb-item.editing');
        for (var i = 0; i < active.length; i++) active[i].classList.remove('editing');
    }

    function saveBlock() {
        var elementId = editorEid.textContent.trim();
        if (!elementId) return;
        var payload = {
            page_slug: PAGE_SLUG,
            element_id: elementId,
            block_type: editorType.value,
            content_html: editorHtml.value,
        };
        var jsonText = editorJson.value.trim();
        if (jsonText) {
            var parsed = parseJson(jsonText);
            if (parsed === null) {
                showToast('Invalid JSON in the content editor.', true);
                return;
            }
            payload.content_json = parsed;
        } else if (editorType.value !== 'html') {
            showToast('Structured blocks need JSON content.', true);
            return;
        }

        postJson(URLS.blocksSave, payload).then(function (_a) {
            if (!_a.ok) {
                showToast((_a.data && _a.data.message) || 'Could not save block.', true);
                return;
            }
            showToast('Block saved.');
            closeEditor();
            refreshPreview();
        }).catch(requestFailed);
    }

    if (list) {
        list.addEventListener('click', function (e) {
            var btn = e.target.closest('.pb-icon-btn');
            if (!btn) return;
            var item = e.target.closest('.pb-item');
            if (!item) return;
            var elementId = item.dataset.blockId;
            var action = btn.dataset.action;

            if (action === 'delete') {
                if (!window.confirm('Delete block "' + elementId + '"? This cannot be undone.')) return;
                postJson(URLS.blocksSave, {
                    page_slug: PAGE_SLUG,
                    element_id: elementId,
                    delete: true,
                }).then(function (_a) {
                    if (!_a.ok) {
                        showToast((_a.data && _a.data.message) || 'Delete failed.', true);
                        return;
                    }
                    showToast('Block deleted.');
                    location.reload();
                }).catch(requestFailed);
                return;
            }

            if (action === 'edit') {
                var data = blocksData[elementId];
                if (!data) return;
                editorEid.textContent = elementId;
                editorType.value = data.block_type;
                editorHtml.value = data.content_html || '';
                editorJson.value = (data.content_json && Object.keys(data.content_json).length)
                    ? JSON.stringify(data.content_json, null, 2)
                    : '';
                editor.hidden = false;
                item.classList.add('editing');
                editor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }

    var closeBtn = document.getElementById('pb-editor-close');
    var cancelBtn = document.getElementById('pb-editor-cancel');
    var saveBlockBtn = document.getElementById('pb-editor-save');
    if (closeBtn) closeBtn.addEventListener('click', closeEditor);
    if (cancelBtn) cancelBtn.addEventListener('click', closeEditor);
    if (saveBlockBtn) saveBlockBtn.addEventListener('click', saveBlock);

    var refreshBtn = document.getElementById('pb-refresh-preview');
    if (refreshBtn) refreshBtn.addEventListener('click', function () {
        if (preview && preview.contentWindow) preview.contentWindow.location.reload();
    });
})();
