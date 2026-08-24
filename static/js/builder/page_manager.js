/* ============================================================================
   Page Builder (builder/edit_page.html) — drag-and-drop block manager.
   ----------------------------------------------------------------------------
   Wires the page-settings toolbar (Save Draft / Publish / toggles / SEO),
   drag-and-drop block reordering, the section palette, the inline block
   editor, the on-canvas "+ Add New Section" insert handles that open the
   block library drawer, and the soft-confirmation delete modal. All mutations
   hit the JSON endpoints and refresh the canvas/preview without a full page
   reload (add/delete reload once to re-render server-side).
   ========================================================================== */
(function () {
    'use strict';

    var body = document.body;
    var PAGE_SLUG = body.dataset.pageSlug;
    var PAGE_ID = body.dataset.pageId;
    var URLS = {
        pageSave: body.dataset.pageSaveUrl,
        blocksSave: body.dataset.blocksSaveUrl,
        blocksReorder: body.dataset.blocksReorderUrl,
        blockCreate: body.dataset.blockCreateUrl,
        blockDeleteTemplate: body.dataset.blockDeleteTemplate, // '/builder/api/blocks/0/delete/'
    };

    var toast = document.getElementById('pb-toast');
    var titleInput = document.getElementById('pb-title');
    var publishedToggle = document.getElementById('pb-published');
    var navToggle = document.getElementById('pb-nav');
    var navOrderInput = document.getElementById('pb-nav-order');
    var navIconInput = document.getElementById('pb-nav-icon');
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
    var canvas = document.getElementById('pb-canvas');
    var libModal = document.getElementById('pb-lib-modal');
    var confirmModal = document.getElementById('pb-confirm-modal');
    var confirmTarget = document.getElementById('pb-confirm-target');
    var confirmDeleteBtn = document.getElementById('pb-confirm-delete');

    // Pending actions: where the next library section goes + which block a
    // delete confirmation applies to.
    var pendingOrder = null;  // order_index for the next library insert (null = append)
    var pendingDelete = null; // {pk, elementId}

    /* ------------------------------------------------------------------ */
    /* Helpers                                                             */
    /* ------------------------------------------------------------------ */
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

    function requestFailed() {
        showToast('Request failed — check your connection and try again.', true);
    }

    function postJson(url, payload) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload || {}),
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

    function blockDeleteUrl(pk) {
        return URLS.blockDeleteTemplate.replace('/0/delete/', '/' + pk + '/delete/');
    }

    /* ------------------------------------------------------------------ */
    /* Modals (library drawer + delete confirmation)                       */
    /* ------------------------------------------------------------------ */
    function openModal(modal) { modal.hidden = false; }
    function closeModal(modal) { modal.hidden = true; }
    function closeAllModals() {
        closeModal(libModal);
        closeModal(confirmModal);
        closeStylePopover();
        pendingOrder = null;
        pendingDelete = null;
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAllModals();
    });

    [libModal, confirmModal].forEach(function (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) closeModal(modal);
        });
    });

    var libClose = document.getElementById('pb-lib-close');
    if (libClose) libClose.addEventListener('click', function () { closeModal(libModal); });
    var confirmClose = document.getElementById('pb-confirm-close');
    if (confirmClose) confirmClose.addEventListener('click', function () { closeModal(confirmModal); });

    // Default state: both dialogs MUST start closed. The .pb-modal-backdrop
    // display:grid rule can override the hidden attribute (same defect class
    // as the §98 emergency modal), which stacks the delete-confirm modal over
    // the block library on load. Force the closed state + clear any pending
    // actions here so no modal ever auto-opens without a user click.
    if (libModal) libModal.hidden = true;
    if (confirmModal) confirmModal.hidden = true;
    pendingOrder = null;
    pendingDelete = null;

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
            nav_order: navOrderInput ? parseInt(navOrderInput.value, 10) || 0 : 0,
            nav_icon: navIconInput ? navIconInput.value.trim() || 'file-lines' : 'file-lines',
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
    /* Drag & drop block reordering (left panel list)                      */
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
    /* Section palette (left panel quick add)                              */
    /* ------------------------------------------------------------------ */
    var DEFAULTS = {
        html: '<h2>New section</h2><p>Write your content here.</p>',
        hero: { headline: 'A bold headline', subheadline: 'Supporting line', primary_label: 'Learn More', primary_url: '/departments/' },
        features: { title: 'Why choose us', items: [{ icon: 'fa-star', title: 'Feature', text: 'Describe it here.' }] },
        split: { heading: 'Our mission', text: 'Rich text content goes here.', image_url: '', image_alt: '' },
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
                location.reload(); // refresh list + canvas from the server
            }).catch(requestFailed);
        });
    }

    /* ------------------------------------------------------------------ */
    /* Block library drawer (modal) — create from a section template       */
    /* ------------------------------------------------------------------ */
    function openLibrary(orderIndex) {
        pendingOrder = (typeof orderIndex === 'number') ? orderIndex : null;
        openModal(libModal);
    }

    function createBlockFromLibrary(type) {
        postJson(URLS.blockCreate, {
            page_id: parseInt(PAGE_ID, 10),
            block_type: type,
            order_index: pendingOrder,
        }).then(function (_a) {
            if (!_a.ok) {
                showToast((_a.data && _a.data.message) || 'Could not add section.', true);
                return;
            }
            closeAllModals();
            showToast('Section added.');
            location.reload(); // refresh list + canvas from the server
        }).catch(requestFailed);
    }

    document.querySelectorAll('.pb-insert').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var order = btn.dataset.order;
            openLibrary(order ? parseInt(order, 10) : null);
        });
    });

    document.querySelectorAll('.pb-lib-card').forEach(function (card) {
        function pick() {
            createBlockFromLibrary(card.dataset.blockType);
        }
        card.addEventListener('click', pick);
        card.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                pick();
            }
        });
    });

    /* ------------------------------------------------------------------ */
    /* Inline block editor                                                 */
    /* ------------------------------------------------------------------ */
    // The json_script payload is an ARRAY of block dicts — index it by
    // element_id so the editor can look blocks up by their canvas id.
    var blocksData = {};
    try {
        var raw = document.getElementById('pb-blocks-data');
        var blocksArray = raw ? JSON.parse(raw.textContent) : [];
        for (var i = 0; i < blocksArray.length; i++) {
            var b = blocksArray[i];
            if (b && b.element_id) blocksData[b.element_id] = b;
        }
    } catch (err) { blocksData = {}; }

    function parseJson(text) {
        try { return JSON.parse(text); } catch (err) { return null; }
    }

    function closeEditor() {
        editor.hidden = true;
        var active = document.querySelectorAll('.pb-item.editing, .pb-section.editing');
        for (var i = 0; i < active.length; i++) active[i].classList.remove('editing');
    }

    function openEditor(elementId) {
        var data = blocksData[elementId];
        if (!data) return;
        editorEid.textContent = elementId;
        editorType.value = data.block_type;
        editorHtml.value = data.content_html || '';
        editorJson.value = (data.content_json && Object.keys(data.content_json).length)
            ? JSON.stringify(data.content_json, null, 2)
            : '';
        editor.hidden = false;
        editor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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

    /* ------------------------------------------------------------------ */
    /* Soft-confirmation delete modal                                      */
    /* ------------------------------------------------------------------ */
    function openDeleteConfirm(pk, elementId) {
        pendingDelete = { pk: pk, elementId: elementId };
        confirmTarget.textContent = elementId;
        openModal(confirmModal);
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (!pendingDelete) return;
            var pk = pendingDelete.pk;
            confirmDeleteBtn.disabled = true;
            postJson(blockDeleteUrl(pk), {}).then(function (_a) {
                confirmDeleteBtn.disabled = false;
                if (!_a.ok) {
                    showToast((_a.data && _a.data.message) || 'Could not delete section.', true);
                    return;
                }
                closeAllModals();
                pendingDelete = null;
                showToast('Section deleted.');
                location.reload();
            }).catch(function () {
                confirmDeleteBtn.disabled = false;
                requestFailed();
            });
        });
    }

    var confirmCancel = document.getElementById('pb-confirm-cancel');
    if (confirmCancel) confirmCancel.addEventListener('click', function () {
        closeModal(confirmModal);
        pendingDelete = null;
    });

    /* ------------------------------------------------------------------ */
    /* Canvas + left-panel toolbar actions (edit / delete)                 */
    /* ------------------------------------------------------------------ */
    function handleToolbarClick(container, rowSelector) {
        container.addEventListener('click', function (e) {
            var btn = e.target.closest('.pb-icon-btn');
            if (!btn) return;
            var row = e.target.closest(rowSelector);
            if (!row) return;
            var elementId = row.dataset.blockId;
            var action = btn.dataset.action;
            if (action === 'edit') {
                openEditor(elementId);
            } else if (action === 'delete') {
                openDeleteConfirm(row.dataset.blockPk, elementId);
            } else if (action === 'style') {
                openStylePopover(btn, row);
            } else if (action === 'toggle') {
                toggleVisibility(elementId);
            }
        });
    }

    if (canvas) handleToolbarClick(canvas, '.pb-section');
    if (list) handleToolbarClick(list, '.pb-item');

    /* ------------------------------------------------------------------ */
    /* Visibility toggle (show / hide a section on the live page)         */
    /* ------------------------------------------------------------------ */
    function toggleVisibility(elementId) {
        var data = blocksData[elementId];
        if (!data) return;
        var next = !data.visible;
        postJson(URLS.blocksSave, {
            page_slug: PAGE_SLUG,
            element_id: elementId,
            visible: next,
        }).then(function (_a) {
            if (!_a.ok) {
                showToast((_a.data && _a.data.message) || 'Could not update visibility.', true);
                return;
            }
            data.visible = next;
            var buttons = document.querySelectorAll('[data-block-id="' + elementId + '"] [data-action="toggle"]');
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].classList.toggle('off', !next);
                var icon = buttons[i].querySelector('i');
                icon.className = next ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
                buttons[i].title = next ? 'Hide section on the live page' : 'Show section on the live page';
                buttons[i].setAttribute('aria-label', next ? 'Hide section' : 'Show section');
            }
            showToast(next ? 'Section shown on the live page.' : 'Section hidden on the live page.');
            refreshPreview();
        }).catch(requestFailed);
    }

    /* ------------------------------------------------------------------ */
    /* Inline contenteditable editing + 64-colour style picker             */
    /* ------------------------------------------------------------------ */
    function deepCopy(obj) {
        return JSON.parse(JSON.stringify(obj || {}));
    }

    function setPath(obj, path, value) {
        var parts = path.split('.');
        var node = obj;
        for (var i = 0; i < parts.length - 1; i++) {
            var key = parts[i];
            if (node[key] == null || typeof node[key] !== 'object') node[key] = {};
            node = node[key];
        }
        node[parts[parts.length - 1]] = value;
        return obj;
    }

    function persistFieldEdit(el) {
        var section = el.closest('.pb-section');
        if (!section) return;
        var elementId = section.dataset.blockId;
        var block = blocksData[elementId];
        if (!block) return;

        if (el.hasAttribute('data-edit-html')) {
            // Whole-body rich-text edit on a Text Block → save content_html.
            postJson(URLS.blocksSave, {
                page_slug: PAGE_SLUG,
                element_id: elementId,
                block_type: block.block_type,
                content_html: el.innerHTML,
            }).then(function (_a) {
                if (!_a.ok) {
                    showToast((_a.data && _a.data.message) || 'Could not save edit.', true);
                    return;
                }
                block.content_html = el.innerHTML;
                showToast('Saved.');
            }).catch(requestFailed);
            return;
        }

        var fieldPath = el.getAttribute('data-edit-field');
        if (!fieldPath) return;
        var newJson = deepCopy(block.content_json);
        setPath(newJson, fieldPath, el.innerText.trim());
        postJson(URLS.blocksSave, {
            page_slug: PAGE_SLUG,
            element_id: elementId,
            block_type: block.block_type,
            content_json: newJson,
        }).then(function (_a) {
            if (!_a.ok) {
                showToast((_a.data && _a.data.message) || 'Could not save edit.', true);
                return;
            }
            blocksData[elementId].content_json = newJson;
            showToast('Saved.');
        }).catch(requestFailed);
    }

    // Every canvas field that carries a binding becomes directly editable.
    document.querySelectorAll('#pb-canvas [data-edit-field], #pb-canvas [data-edit-html]').forEach(function (el) {
        el.setAttribute('contenteditable', 'true');
        el.setAttribute('spellcheck', 'false');
        el.addEventListener('blur', function () {
            // Debounce so rapid field-to-field edits coalesce into one save.
            clearTimeout(window.__pbFieldSaveTimer);
            window.__pbFieldSaveTimer = setTimeout(function () {
                persistFieldEdit(el);
            }, 350);
        });
    });

    /* Style popover (64-swatch text + background pickers) */
    var stylePop = document.getElementById('pb-style-pop');
    var styleTarget = document.getElementById('pb-style-target');
    var styleSection = null;

    function openStylePopover(btn, section) {
        styleSection = section;
        styleTarget.textContent = '#' + section.dataset.blockId;
        stylePop.hidden = false;
        var rect = btn.getBoundingClientRect();
        var left = Math.max(8, Math.min(rect.left, window.innerWidth - (stylePop.offsetWidth || 288) - 8));
        var top = rect.top - (stylePop.offsetHeight || 360) - 10;
        if (top < 8) top = rect.bottom + 10;
        stylePop.style.left = left + 'px';
        stylePop.style.top = top + 'px';
    }

    function closeStylePopover() {
        if (stylePop) stylePop.hidden = true;
        styleSection = null;
    }

    function applyStyleToSection(section, styleJson) {
        var bodyEl = section.querySelector('.pb-section-body');
        if (!bodyEl) return;
        bodyEl.style.background = styleJson.background || '';
        bodyEl.style.color = styleJson.color || '';
    }

    function saveStyle(kind, color) {
        if (!styleSection) return;
        var elementId = styleSection.dataset.blockId;
        var block = blocksData[elementId];
        if (!block) return;
        var styleJson = deepCopy(block.style_json || {});
        if (kind === 'text') styleJson.color = color;
        else styleJson.background = color;
        postJson(URLS.blocksSave, {
            page_slug: PAGE_SLUG,
            element_id: elementId,
            block_type: block.block_type,
            style_json: styleJson,
        }).then(function (_a) {
            if (!_a.ok) {
                showToast((_a.data && _a.data.message) || 'Could not save style.', true);
                return;
            }
            blocksData[elementId].style_json = styleJson;
            applyStyleToSection(styleSection, styleJson);
            showToast(kind === 'text' ? 'Text colour saved.' : 'Background colour saved.');
        }).catch(requestFailed);
    }

    document.querySelectorAll('#pb-text-swatches .pb-swatch').forEach(function (sw) {
        sw.addEventListener('click', function () { saveStyle('text', sw.dataset.color); });
    });
    document.querySelectorAll('#pb-bg-swatches .pb-swatch').forEach(function (sw) {
        sw.addEventListener('click', function () { saveStyle('background', sw.dataset.color); });
    });

    var styleReset = document.getElementById('pb-style-reset');
    if (styleReset) {
        styleReset.addEventListener('click', function () {
            if (!styleSection) return;
            var elementId = styleSection.dataset.blockId;
            var block = blocksData[elementId];
            if (!block) return;
            var styleJson = deepCopy(block.style_json || {});
            delete styleJson.color;
            delete styleJson.background;
            postJson(URLS.blocksSave, {
                page_slug: PAGE_SLUG,
                element_id: elementId,
                block_type: block.block_type,
                style_json: styleJson,
            }).then(function (_a) {
                if (!_a.ok) {
                    showToast((_a.data && _a.data.message) || 'Could not reset style.', true);
                    return;
                }
                blocksData[elementId].style_json = styleJson;
                applyStyleToSection(styleSection, styleJson);
                showToast('Colours reset.');
            }).catch(requestFailed);
        });
    }

    document.addEventListener('click', function (e) {
        if (!stylePop || stylePop.hidden) return;
        if (stylePop.contains(e.target)) return;
        closeStylePopover();
    });

    /* ------------------------------------------------------------------ */
    /* Canvas / Live Preview tabs                                          */
    /* ------------------------------------------------------------------ */
    var canvasWrap = document.getElementById('pb-canvas-wrap');
    var previewWrap = document.getElementById('pb-preview-wrap');
    var tabCanvas = document.getElementById('pb-tab-canvas');
    var tabPreview = document.getElementById('pb-tab-preview');

    function setView(tab) {
        var isCanvas = tab === 'canvas';
        if (canvasWrap) canvasWrap.hidden = !isCanvas;
        if (previewWrap) previewWrap.hidden = isCanvas;
        if (tabCanvas) {
            tabCanvas.classList.toggle('active', isCanvas);
            tabCanvas.setAttribute('aria-selected', isCanvas ? 'true' : 'false');
        }
        if (tabPreview) {
            tabPreview.classList.toggle('active', !isCanvas);
            tabPreview.setAttribute('aria-selected', isCanvas ? 'false' : 'true');
        }
        if (!isCanvas) refreshPreview(); // fresh when the iframe becomes visible
    }

    if (tabCanvas) tabCanvas.addEventListener('click', function () { setView('canvas'); });
    if (tabPreview) tabPreview.addEventListener('click', function () { setView('preview'); });

    /* ------------------------------------------------------------------ */
    /* Inline editor buttons                                               */
    /* ------------------------------------------------------------------ */
    var closeBtn = document.getElementById('pb-editor-close');
    var cancelBtn = document.getElementById('pb-editor-cancel');
    var saveBlockBtn = document.getElementById('pb-editor-save');
    if (closeBtn) closeBtn.addEventListener('click', closeEditor);
    if (cancelBtn) cancelBtn.addEventListener('click', closeEditor);
    if (saveBlockBtn) saveBlockBtn.addEventListener('click', saveBlock);
})();
