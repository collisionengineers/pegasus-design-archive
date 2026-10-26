/* v42 mockup bridge. Runs first inside every composed page.
   Provides interactive Inbox message dialogs (#mailMessageDialog), cog settings
   menu actions (1-step Email type select, Case / PO autocomplete & 1-click link/unlink,
   Open query & Mark done, Change case), scope tabs, Principal/quick filters,
   composer replies, row dismissal, search and sorting. */
(function () {
  'use strict';
  var host = window.parent;
  var ORIGIN = 'https://localhost:7139';
  var DEFAULT_LOC = ORIGIN + '/Inbox';

  function post(message) {
    try { host.postMessage(message, '*'); } catch (e) { /* detached */ }
  }
  function toast(text) {
    post({ type: 'toast', text: text });
  }
  function local(url) {
    var text = String(url || '');
    var match = text.match(/^[a-z]+:\/\/[^/]+(\/.*)$/i);
    return match ? match[1] : text;
  }

  // Wrap window.URL so site.js calls like `new URL(window.location.href)` and
  // `new URL(href, window.location.href)` succeed inside an about:srcdoc iframe.
  var NativeURL = window.URL;
  function PatchedURL(url, base) {
    var u = String(url == null ? '' : url);
    var b = base !== undefined ? String(base) : undefined;
    if (!u || u.indexOf('about:') === 0) u = DEFAULT_LOC;
    if (b !== undefined && (!b || b.indexOf('about:') === 0)) b = DEFAULT_LOC;
    return b !== undefined ? new NativeURL(u, b) : new NativeURL(u, ORIGIN);
  }
  PatchedURL.prototype = NativeURL.prototype;
  Object.setPrototypeOf(PatchedURL, NativeURL);
  if (NativeURL.createObjectURL) PatchedURL.createObjectURL = NativeURL.createObjectURL.bind(NativeURL);
  if (NativeURL.revokeObjectURL) PatchedURL.revokeObjectURL = NativeURL.revokeObjectURL.bind(NativeURL);
  window.URL = PatchedURL;

  var fragments = (host && host.__mockFragments) || {};
  var dialogs = (host && host.__mockDialogs) || { today: {}, proposal: {} };

  var CASES = [
    { ref: 'QDOS26214', id: '85de4c48-ed02-445f-a2ce-d97a087c19dd', vrm: 'MA59BDY', vehicle: 'Ford Focus · MA59 BDY', claimant: 'R. Whitfield', reportSent: true, canHoldClose: false },
    { ref: 'QDOS26220', id: 'bee37ce3-c710-4a5b-8e2c-67e8ed6ad8cb', vrm: 'LK21ABC', vehicle: 'Vauxhall Corsa · LK21 ABC', claimant: 'Meridian Claims', reportSent: false, canHoldClose: true },
    { ref: 'QDOS26190', id: '2dc71cf4-debc-403d-be99-241d73c16bd2', vrm: 'PO16DDF', vehicle: 'Mercedes A180 · PO16 DDF', claimant: 'K. Osei', reportSent: true, canHoldClose: false },
    { ref: 'PCH26102', id: '8a63804e-c66d-4725-a5db-312d9870311e', vrm: 'EF56GHJ', vehicle: 'BMW 320d · EF56 GHJ', claimant: 'P. Marsh', reportSent: false, canHoldClose: true }
  ];
  function findCase(ref) {
    var upper = String(ref || '').trim().toUpperCase();
    return CASES.filter(function (c) { return c.ref === upper || c.vrm === upper; })[0] || null;
  }

  var TYPE_INFO = {
    'correspondence': { value: 'correspondence', display: 'Case correspondence', short: 'Correspondence', sub: null, group: 'correspondence' },
    'new-instruction': { value: 'new-instruction:Inspection', display: 'New instruction · Inspection', short: 'New instruction', sub: 'Inspection', group: 'instructions' },
    'new-instruction:Inspection': { value: 'new-instruction:Inspection', display: 'New instruction · Inspection', short: 'New instruction', sub: 'Inspection', group: 'instructions' },
    'new-instruction:Audit': { value: 'new-instruction:Audit', display: 'New instruction · Audit', short: 'New instruction', sub: 'Audit', group: 'instructions' },
    'new-instruction:InspectionAndAudit': { value: 'new-instruction:InspectionAndAudit', display: 'New instruction · Inspection & Audit', short: 'New instruction', sub: 'Inspection & Audit', group: 'instructions' },
    'triage-request': { value: 'triage-request', display: 'Triage request', short: 'Triage request', sub: 'Early triage', group: 'instructions' },
    'cancellation': { value: 'cancellation', display: 'Cancellation', short: 'Cancellation', sub: 'Withdrawn claim', group: 'cancellations' }
  };

  var overrides = {};
  function getOverride(msgId) {
    if (!overrides[msgId]) overrides[msgId] = {};
    return overrides[msgId];
  }

  function currentMode() {
    var m = document.documentElement.getAttribute('data-v42-mode');
    return m === 'proposal' ? 'proposal' : 'today';
  }

  function htmlResponse(html) {
    return Promise.resolve(new Response(html, {
      status: 200,
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    }));
  }

  function buildCasePickerOptions(query) {
    var q = String(query || '').trim().toUpperCase();
    var matches = CASES.filter(function (c) {
      return !q || c.ref.indexOf(q) !== -1 || c.vrm.indexOf(q) !== -1 || c.claimant.toUpperCase().indexOf(q) !== -1;
    });
    if (!matches.length) matches = CASES;
    return matches.map(function (c, idx) {
      return '<button type="button" role="option" id="mailLinkCaseOptions-' + idx + '" class="command-result" '
        + 'aria-selected="false" value="' + c.ref + '" data-case-picker-choice="' + c.ref + '">'
        + c.ref + ' · ' + c.vrm + ' · ' + c.claimant + '</button>';
    }).join('');
  }

  function applyOverridesToDialogHtml(msgId, html) {
    var ov = overrides[msgId];
    if (!ov || (!ov.typeInfo && !ov.queryState && ov.caseRef === undefined && !ov.notice)) return html;
    var doc = new DOMParser().parseFromString('<div>' + html + '</div>', 'text/html');
    var root = doc.body.firstElementChild;
    syncDialogDom(root, msgId);
    return root.innerHTML;
  }

  window.fetch = function (input) {
    var raw = typeof input === 'string' ? input : (input && input.url);
    var pathAndQuery = local(raw);
    if (typeof fragments[pathAndQuery] === 'string') {
      return htmlResponse(fragments[pathAndQuery]);
    }
    var parsed;
    try { parsed = new NativeURL(pathAndQuery, ORIGIN); } catch (e) { parsed = null; }
    if (parsed) {
      var handler = parsed.searchParams.get('handler') || '';
      if (handler === 'LinkCaseOptions' || handler === 'CorrespondenceCaseOptions') {
        var q = parsed.searchParams.get('q') || parsed.searchParams.get('query') || '';
        return htmlResponse(buildCasePickerOptions(q));
      }
      var m = parsed.pathname.match(/^\/Inbox\/([0-9a-f-]{36})$/i);
      if (m && handler === 'Dialog') {
        var msgId = m[1].toLowerCase();
        var mode = currentMode();
        var bag = (dialogs[mode] && dialogs[mode][msgId]) || (dialogs.proposal && dialogs.proposal[msgId]);
        if (bag) {
          var compose = parsed.searchParams.get('compose');
          var aiJob = parsed.searchParams.get('aiJob');
          var section = parsed.searchParams.get('section') || 'message';
          var viewKey = compose ? (aiJob ? 'ai-reply' : compose) : section;
          var template = bag[viewKey] || bag.message;
          return htmlResponse(applyOverridesToDialogHtml(msgId, template));
        }
      }
    }
    return new Promise(function () {});
  };

  window.XMLHttpRequest = function () {
    return { open: function () {}, send: function () {}, setRequestHeader: function () {}, addEventListener: function () {}, abort: function () {} };
  };
  if (navigator.sendBeacon) navigator.sendBeacon = function () { return true; };
  window.EventSource = function () { return { close: function () {}, addEventListener: function () {} }; };
  history.pushState = function () {};
  history.replaceState = function () {};
  try { void window.localStorage.length; } catch (e) {
    var store = {};
    Object.defineProperty(window, 'localStorage', { value: {
      getItem: function (k) { return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; },
      setItem: function (k, v) { store[k] = String(v); },
      removeItem: function (k) { delete store[k]; },
      clear: function () { store = {}; },
      key: function (i) { return Object.keys(store)[i] || null; },
      get length() { return Object.keys(store).length; }
    } });
  }

  function markRowRead(row) {
    if (!row) return;
    row.classList.remove('unread');
    var dot = row.querySelector('.unread-indicator');
    var sr = dot && dot.nextElementSibling;
    if (dot) dot.remove();
    if (sr && sr.classList.contains('sr-only')) sr.remove();
  }

  function syncRowDom(msgId) {
    var row = document.querySelector('.inbox-row[data-mail-row="' + msgId + '"]');
    if (!row) return;
    var ov = overrides[msgId] || {};
    var caseCell = row.querySelector('.inbox-cell-case');
    if (caseCell && ov.caseRef !== undefined) {
      if (ov.caseRef) {
        var cObj = findCase(ov.caseRef) || { ref: ov.caseRef, id: '85de4c48-ed02-445f-a2ce-d97a087c19dd', vehicle: 'Linked Case' };
        caseCell.innerHTML = '<a class="mail-row-case" href="/Cases/' + cObj.id + '">' + cObj.ref + '</a>'
          + '<small class="inbox-cell-sub">' + cObj.vehicle + '</small>';
      } else {
        caseCell.innerHTML = '<span class="status status--amber">No Case Found</span>'
          + '<small class="inbox-cell-sub">Unlinked</small>';
      }
    }
    var typeCell = row.querySelector('.inbox-cell-type');
    if (typeCell) {
      if (ov.queryState === 'open') {
        row.setAttribute('data-type-group', 'queries');
        typeCell.innerHTML = '<span class="status status--purple" data-row-query>Query</span>'
          + '<small class="inbox-cell-sub">Unassigned</small>';
      } else if (ov.queryState === 'done') {
        typeCell.innerHTML = '<span class="status status--green" data-row-query>Done</span>';
      } else if (ov.typeInfo) {
        var ti = ov.typeInfo;
        row.setAttribute('data-type-group', ti.group);
        if (ti.short === 'New instruction') {
          typeCell.innerHTML = '<span class="status status--navy">New instruction</span>'
            + '<span class="row-meta" hidden>New instruction</span>'
            + '<small class="inbox-cell-sub">' + (ti.sub || 'Inspection') + '</small>';
        } else if (ti.short === 'Triage request') {
          typeCell.innerHTML = '<span class="status status--amber">Triage request</span>'
            + '<span class="row-meta" hidden>Triage request</span>'
            + '<small class="inbox-cell-sub">Early triage</small>';
        } else if (ti.short === 'Cancellation') {
          typeCell.innerHTML = '<span class="status status--red">Cancellation</span>'
            + '<span class="row-meta" hidden>Cancellation</span>'
            + '<small class="inbox-cell-sub">Withdrawn claim</small>';
        } else {
          typeCell.innerHTML = '<span class="inbox-type-correspondence">Correspondence</span>';
        }
      }
    }
  }

  function syncDialogDom(root, msgId) {
    var ov = overrides[msgId];
    if (!ov) return;
    var dialog = root.querySelector('#mailMessageDialog') || root;

    if (ov.notice) {
      var dBody = dialog.querySelector('.dialog-body');
      if (dBody) {
        var oldNotice = dBody.querySelector('[data-live-notice]');
        if (oldNotice) oldNotice.remove();
        dBody.insertAdjacentHTML('afterbegin',
          '<div class="notice notice--success" role="status" data-live-notice>'
          + '<svg class="icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>'
          + '<span>' + ov.notice + '</span></div>');
      }
    }

    if (ov.typeInfo) {
      var ti = ov.typeInfo;
      var ctxType = dialog.querySelector('[data-context-type]');
      if (ctxType) ctxType.textContent = ti.display;
      var sel = dialog.querySelector('#mailTypeSelect');
      if (sel) sel.value = ti.value;
    }

    if (ov.caseRef !== undefined) {
      var cObj = ov.caseRef ? (findCase(ov.caseRef) || { ref: ov.caseRef, id: '85de4c48-ed02-445f-a2ce-d97a087c19dd', vehicle: 'Linked Case', reportSent: true }) : null;
      var caseRowStrong = dialog.querySelector('.decision-facts .decision-row strong');
      if (caseRowStrong) {
        caseRowStrong.className = cObj ? '' : 'quiet';
        caseRowStrong.innerHTML = cObj ? '<a href="/Cases/' + cObj.id + '">' + cObj.ref + '</a>' : 'None';
      }
      var sugBanner = dialog.querySelector('[data-suggested-case]');
      if (sugBanner && cObj) sugBanner.remove();
      var ctxBar = dialog.querySelector('[data-mail-context-bar]');
      if (ctxBar) {
        var ctxCase = ctxBar.querySelector('[data-context-case]');
        var linkBtn = ctxBar.querySelector('[data-open-settings-case]');
        if (cObj) {
          if (linkBtn) linkBtn.remove();
          if (ctxCase) {
            ctxCase.outerHTML = '<a class="mail-pill mail-pill--case" href="/Cases/' + cObj.id + '" data-context-case>'
              + '<svg class="icon" aria-hidden="true"><use href="#icon-folder-open"></use></svg>'
              + '<span>Case</span><strong>' + cObj.ref + '</strong>'
              + (cObj.vehicle ? '<small> · ' + cObj.vehicle + '</small>' : '') + '</a>';
          }
        } else if (ctxCase) {
          ctxCase.outerHTML = '<span class="status status--amber" data-context-case>No Case Found</span>'
            + '<button type="button" class="mail-pill mail-pill--action" data-open-settings-case>'
            + '<svg class="icon" aria-hidden="true"><use href="#icon-link"></use></svg><span>Link to Case</span></button>';
        }
      }
    }

    if (ov.queryState) {
      var qBlock = dialog.querySelector('[data-mail-query]');
      var ctxBar2 = dialog.querySelector('[data-mail-context-bar]');
      var oldCtxQ = ctxBar2 && ctxBar2.querySelector('[data-context-query], [data-quick-open-query]');
      if (ov.queryState === 'open') {
        if (qBlock) {
          qBlock.innerHTML = '<form method="post" action="/Inbox/' + msgId + '?handler=MarkQueryDone">'
            + '<button class="mail-settings-item" type="submit" data-busy-label="Saving…">'
            + '<span class="mail-settings-item-left"><svg class="icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>'
            + '<span>Mark query done</span></span>'
            + '<span class="status status--purple">Query · Unassigned</span></button></form>';
        }
        var openPill = '<span class="status status--purple" data-context-query>Query · Unassigned</span>';
        if (oldCtxQ) oldCtxQ.outerHTML = openPill;
        else if (ctxBar2) ctxBar2.insertAdjacentHTML('beforeend', '<span class="mail-context-sep">·</span>' + openPill);
      } else if (ov.queryState === 'done') {
        if (qBlock) {
          qBlock.innerHTML = '<div class="mail-settings-item"><span>Query</span><span class="status status--green">Done</span></div>';
        }
        var donePill = '<span class="status status--green" data-context-query>Query · Done</span>';
        if (oldCtxQ) oldCtxQ.outerHTML = donePill;
        else if (ctxBar2) ctxBar2.insertAdjacentHTML('beforeend', '<span class="mail-context-sep">·</span>' + donePill);
      }
    }
  }

  // Live Inbox filtering (Principal, Mailbox, Quick Filter pills, Search text)
  function applyInboxFilters() {
    var pSel = document.getElementById('principal-filter');
    var mSel = document.getElementById('mailbox-filter');
    var tSel = document.getElementById('type-filter');
    var sInp = document.getElementById('mail-search');
    var activeQ = document.querySelector('.inbox-qpill[aria-pressed="true"]');
    var principal = pSel ? pSel.value : '';
    var mailbox = mSel ? mSel.value : '';
    var search = (sInp ? sInp.value : '').trim().toLowerCase();
    var qfilter = tSel ? tSel.value : (activeQ ? activeQ.getAttribute('data-mail-qfilter') : 'all');

    var shown = 0;
    document.querySelectorAll('.inbox-row[data-mail-row]').forEach(function (row) {
      var ok = true;
      if (principal && row.getAttribute('data-principal') !== principal) ok = false;
      if (mailbox && row.getAttribute('data-mailbox') !== mailbox) ok = false;
      if (qfilter && qfilter !== 'all') {
        if (qfilter === 'unread') {
          if (!row.classList.contains('unread')) ok = false;
        } else if (row.getAttribute('data-type-group') !== qfilter) {
          ok = false;
        }
      }
      if (search && row.textContent.toLowerCase().indexOf(search) === -1) ok = false;
      row.hidden = !ok;
      if (ok) shown++;
    });
    var meta = document.querySelector('[data-inbox-count], .inbox-messages-head .meta');
    if (meta) meta.textContent = shown + (shown === 1 ? ' message' : ' messages');
  }

  window.addEventListener('change', function (ev) {
    var target = ev.target instanceof Element ? ev.target : null;
    if (!target) return;
    if (target.matches('input[data-mail-tick]')) {
      var bulkForm = document.getElementById('mail-bulk');
      var nTicked = document.querySelectorAll('input[data-mail-tick]:checked').length;
      if (bulkForm && currentMode() === 'proposal') bulkForm.hidden = nTicked === 0;
      return;
    }
    if (target.matches('#principal-filter, #mailbox-filter, #type-filter')) {
      applyInboxFilters();
      toast('Filtered Inbox list');
      return;
    }
    if (target.matches('#mailTypeSelect, [data-mail-type-select]')) {
      var dlg = target.closest('#mailMessageDialog');
      var msgId = dlg && dlg.getAttribute('data-mail-message');
      var ti = TYPE_INFO[target.value] || TYPE_INFO.correspondence;
      if (msgId) {
        var ov = getOverride(msgId);
        ov.typeInfo = ti;
        ov.notice = 'Email type updated to ' + ti.display + '.';
        syncDialogDom(document, msgId);
        syncRowDom(msgId);
      }
      toast('Email type set to ' + ti.display);
    }
  });

  window.addEventListener('input', function (ev) {
    var target = ev.target instanceof Element ? ev.target : null;
    if (target && target.id === 'mail-search') {
      applyInboxFilters();
    }
  });

  window.addEventListener('click', function (ev) {
    var target = ev.target instanceof Element ? ev.target : null;
    if (!target) return;

    // 0. Choosing an option in the cog menu's Case / PO autocomplete links immediately
    var pickerChoice = target.closest('#mailLinkCaseOptions [data-case-picker-choice]');
    if (pickerChoice) {
      var pickedRef = pickerChoice.getAttribute('data-case-picker-choice');
      var dlgPick = pickerChoice.closest('#mailMessageDialog');
      var mIdPick = dlgPick && dlgPick.getAttribute('data-mail-message');
      if (mIdPick && pickedRef) {
        var ovPick = getOverride(mIdPick);
        ovPick.caseRef = pickedRef;
        ovPick.notice = 'Linked to Case ' + pickedRef + '.';
        syncDialogDom(document, mIdPick);
        syncRowDom(mIdPick);
        toast('Linked to ' + pickedRef);
      }
      return;
    }
    // 1. Scope tabs (All, No Case Found, Dismissed)
    var scopeBtn = target.closest('[data-scope-switch]');
    if (scopeBtn) {
      ev.preventDefault();
      var sc = scopeBtn.getAttribute('data-scope-switch');
      if (sc === 'no_case_found') post({ type: 'nav', href: '/Inbox?queue=no_case_found' });
      else if (sc === 'dismissed') post({ type: 'nav', href: '/Inbox?folder=dismissed' });
      else post({ type: 'nav', href: '/Inbox' });
      return;
    }

    // 2. Quick filter pills (All types, Instructions, Queries, Cancellations, Unread)
    var qpill = target.closest('[data-mail-qfilter]');
    if (qpill) {
      ev.preventDefault();
      document.querySelectorAll('[data-mail-qfilter]').forEach(function (b) {
        b.setAttribute('aria-pressed', b === qpill ? 'true' : 'false');
      });
      applyInboxFilters();
      return;
    }

    // 3. 1-click Suggested Case link inside cog settings menu
    var quickLinkBtn = target.closest('[data-quick-link-case]');
    if (quickLinkBtn) {
      ev.preventDefault();
      var sugRef = quickLinkBtn.getAttribute('data-quick-link-case');
      var dlgSug = quickLinkBtn.closest('#mailMessageDialog');
      var mIdSug = dlgSug && dlgSug.getAttribute('data-mail-message');
      if (mIdSug && sugRef) {
        var ovSug = getOverride(mIdSug);
        ovSug.caseRef = sugRef;
        ovSug.notice = 'Linked to Case ' + sugRef + '.';
        syncDialogDom(document, mIdSug);
        syncRowDom(mIdSug);
        toast('Linked to ' + sugRef);
      }
      return;
    }

    // 4. Context bar triggers inside #mailMessageDialog
    var openCaseBtn = target.closest('[data-open-settings-case]');
    if (openCaseBtn) {
      ev.preventDefault();
      var menu = document.querySelector('details[data-mail-settings]');
      if (menu) {
        menu.open = true;
        var inp = menu.querySelector('#mailLinkCaseReference');
        if (inp) setTimeout(function () { inp.focus(); }, 20);
      }
      return;
    }
    var openTypeBtn = target.closest('[data-open-settings-type]');
    if (openTypeBtn) {
      ev.preventDefault();
      var menu2 = document.querySelector('details[data-mail-settings]');
      if (menu2) {
        menu2.open = true;
        var sel = menu2.querySelector('#mailTypeSelect');
        if (sel) setTimeout(function () { sel.focus(); }, 20);
      }
      return;
    }
    var quickOpenQ = target.closest('[data-quick-open-query]');
    if (quickOpenQ) {
      ev.preventDefault();
      var dlg = quickOpenQ.closest('#mailMessageDialog');
      var mId = dlg && dlg.getAttribute('data-mail-message');
      if (mId) {
        var ov = getOverride(mId);
        ov.queryState = 'open';
        ov.notice = 'The query was opened.';
        syncDialogDom(document, mId);
        syncRowDom(mId);
        toast('Query opened (Unassigned)');
      }
      return;
    }
    var previewAtt = target.closest('[data-preview-attachment]');
    if (previewAtt) {
      ev.preventDefault();
      toast('Opened attachment: ' + previewAtt.getAttribute('data-preview-attachment'));
      return;
    }

    // 5. Sort toggle on /Inbox (Received ↓ / Received ↑)
    var sortLink = target.closest('a.sort-toggle');
    if (sortLink) {
      ev.preventDefault();
      var rowList = document.querySelector('[data-mail-workspace] [data-row-list]:not([data-mail-scopes])');
      if (rowList) {
        var items = Array.prototype.slice.call(rowList.querySelectorAll('.inbox-row'));
        items.reverse().forEach(function (r) { rowList.appendChild(r); });
        var desc = sortLink.textContent.indexOf('↓') !== -1;
        sortLink.textContent = 'Received ' + (desc ? '↑' : '↓');
        toast('Sorted ' + (desc ? 'oldest first' : 'newest first'));
      }
      return;
    }

    // 6. Clicking anywhere on an .inbox-row opens the email dialog.
    var clickedRow = target.closest('.inbox-row[data-mail-row]');
    if (clickedRow && !target.closest('a, button, form, label, input, select, textarea')) {
      markRowRead(clickedRow);
      var openLink = clickedRow.querySelector('a[data-mail-open]');
      if (openLink) {
        ev.preventDefault();
        openLink.click();
        return;
      }
    }
    if (target.closest('a[data-mail-open]')) {
      markRowRead(target.closest('.inbox-row[data-mail-row]'));
    }

    if (ev.defaultPrevented) return;
    var link = target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href') || '';
    if (!href || href.charAt(0) === '#' || /^(mailto:|tel:|javascript:)/i.test(href)) return;
    ev.preventDefault();
    post({ type: 'nav', href: local(href), text: (link.textContent || '').trim() });
  });

  function updateInboxCounts(delta) {
    var meta = document.querySelector('[data-inbox-count], .inbox-messages-head .meta');
    if (meta) {
      var m = meta.textContent.match(/(\d+)/);
      if (m) {
        var next = Math.max(0, parseInt(m[1], 10) + delta);
        meta.textContent = next + (next === 1 ? ' message' : ' messages');
      }
    }
    var pressedScope = document.querySelector('.inbox-scope-tab[aria-pressed="true"] .tab-count, .scope-list .scope-button[aria-pressed="true"] .tabular');
    if (pressedScope) {
      var n = parseInt(pressedScope.textContent.trim(), 10);
      if (!isNaN(n)) pressedScope.textContent = String(Math.max(0, n + delta));
    }
  }

  window.addEventListener('submit', function (ev) {
    if (ev.defaultPrevented) return;
    var form = ev.target;
    if (!(form instanceof HTMLFormElement)) return;
    ev.preventDefault();
    var button = ev.submitter;
    var action = form.getAttribute('action') || '';
    var method = (form.getAttribute('method') || 'get').toLowerCase();

    if (method === 'get') {
      if (form.classList.contains('inbox-filter')) {
        applyInboxFilters();
        return;
      }
      var queueInput = form.querySelector('input[name="queue"]');
      var folderInput = form.querySelector('input[name="folder"]');
      if (queueInput && queueInput.value === 'no_case_found') {
        post({ type: 'nav', href: '/Inbox?queue=no_case_found' });
        return;
      }
      if (folderInput && folderInput.value === 'dismissed') {
        post({ type: 'nav', href: '/Inbox?folder=dismissed' });
        return;
      }
      if (!folderInput && !queueInput && form.closest('.scope-list')) {
        post({ type: 'nav', href: '/Inbox' });
        return;
      }
    }

    if (form.id === 'mailClassificationForm') {
      var dlg = form.closest('#mailMessageDialog');
      var msgId = dlg && dlg.getAttribute('data-mail-message');
      var sel = form.querySelector('#mailTypeSelect');
      var val = sel ? sel.value : ((button && button.getAttribute('value')) || 'correspondence');
      var ti = TYPE_INFO[val] || TYPE_INFO.correspondence;
      if (msgId) {
        var ov = getOverride(msgId);
        ov.typeInfo = ti;
        ov.notice = 'Email type updated to ' + ti.display + '.';
        syncDialogDom(document, msgId);
        syncRowDom(msgId);
      }
      toast('Email type set to ' + ti.display);
      return;
    }

    if (action.indexOf('handler=OpenQuery') !== -1 && form.closest('#mailMessageDialog')) {
      var dlgOpen = form.closest('#mailMessageDialog');
      var mIdOpen = dlgOpen.getAttribute('data-mail-message');
      var ovOpen = getOverride(mIdOpen);
      ovOpen.queryState = 'open';
      ovOpen.notice = 'The query was opened.';
      syncDialogDom(document, mIdOpen);
      syncRowDom(mIdOpen);
      toast('Query opened (Unassigned)');
      return;
    }
    if (action.indexOf('handler=MarkQueryDone') !== -1 && form.closest('#mailMessageDialog')) {
      var dlgDone = form.closest('#mailMessageDialog');
      var mIdDone = dlgDone.getAttribute('data-mail-message');
      var ovDone = getOverride(mIdDone);
      ovDone.queryState = 'done';
      ovDone.notice = 'The query was marked done.';
      syncDialogDom(document, mIdDone);
      syncRowDom(mIdDone);
      toast('Query marked done');
      return;
    }

    if (action.indexOf('handler=LinkCase') !== -1 || action.indexOf('handler=ChangeLinkedCase') !== -1) {
      var pickerInput = document.getElementById('mailLinkCaseReference');
      var chosenRef = (pickerInput && pickerInput.value.trim().toUpperCase()) || 'QDOS26214';
      var openDlg = document.getElementById('mailMessageDialog');
      var mIdLink = openDlg && openDlg.getAttribute('data-mail-message');
      if (mIdLink) {
        var ovLink = getOverride(mIdLink);
        ovLink.caseRef = chosenRef;
        ovLink.notice = 'Linked to Case ' + chosenRef + '.';
        syncDialogDom(document, mIdLink);
        syncRowDom(mIdLink);
      }
      var confirmBackdrop = form.closest('.dialog-backdrop');
      if (confirmBackdrop && typeof confirmBackdrop.pegasusClose === 'function') confirmBackdrop.pegasusClose();
      toast('Linked to ' + chosenRef);
      return;
    }
    if (action.indexOf('handler=UnlinkCase') !== -1) {
      var openDlgU = document.getElementById('mailMessageDialog');
      var mIdU = openDlgU && openDlgU.getAttribute('data-mail-message');
      if (mIdU) {
        var ovU = getOverride(mIdU);
        ovU.caseRef = null;
        ovU.queryState = undefined;
        ovU.notice = 'Unlinked from Case.';
        syncDialogDom(document, mIdU);
        syncRowDom(mIdU);
      }
      var unlinkBackdrop = form.closest('.dialog-backdrop');
      if (unlinkBackdrop && typeof unlinkBackdrop.pegasusClose === 'function') unlinkBackdrop.pegasusClose();
      toast('Unlinked from Case');
      return;
    }

    if (form.id === 'mailComposerForm') {
      var dlgComp = form.closest('#mailMessageDialog');
      var mIdComp = dlgComp && dlgComp.getAttribute('data-mail-message');
      var resolveTick = form.querySelector('input[data-resolve-query]');
      if (mIdComp) {
        var ovComp = getOverride(mIdComp);
        if (resolveTick && resolveTick.checked) {
          ovComp.queryState = 'done';
          ovComp.notice = 'Reply sent and query marked done.';
        } else {
          ovComp.notice = 'Reply queued for sending.';
        }
        syncRowDom(mIdComp);
        var cancelBtn = dlgComp.querySelector('.dialog-foot a[data-mail-dialog-link]');
        if (cancelBtn) cancelBtn.click();
      }
      toast(resolveTick && resolveTick.checked ? 'Sent reply and marked query done' : 'Reply sent');
      return;
    }

    if (form.hasAttribute('data-message-dismissal')) {
      var dlgDis = form.closest('#mailMessageDialog');
      var mIdDis = dlgDis && dlgDis.getAttribute('data-mail-message');
      var nextInput = form.querySelector('[data-mail-next-id]');
      var nextId = nextInput && nextInput.value;
      if (mIdDis) {
        var rDis = document.querySelector('.inbox-row[data-mail-row="' + mIdDis + '"]');
        if (rDis) rDis.remove();
        updateInboxCounts(-1);
      }
      if (nextId) {
        var nextRow = document.querySelector('.inbox-row[data-mail-row="' + nextId + '"]');
        var nextLink = nextRow && nextRow.querySelector('a[data-mail-open]');
        if (nextLink) {
          toast('Dismissed — moved to next message');
          nextLink.click();
          return;
        }
      }
      if (dlgDis && typeof dlgDis.pegasusClose === 'function') dlgDis.pegasusClose();
      toast('Message dismissed');
      return;
    }
    if (form.hasAttribute('data-mail-row-action')) {
      var isRestore = form.getAttribute('data-mail-row-action') === 'restore';
      var rowAct = form.closest('.inbox-row[data-mail-row]');
      if (rowAct) {
        rowAct.remove();
        updateInboxCounts(-1);
      }
      toast(isRestore ? 'Message restored to Inbox' : 'Message dismissed');
      return;
    }
    if (form.id === 'mail-bulk') {
      var ticked = document.querySelectorAll('input[data-mail-tick]:checked');
      if (ticked.length > 0) {
        ticked.forEach(function (cb) {
          var r = cb.closest('.inbox-row');
          if (r) r.remove();
        });
        updateInboxCounts(-ticked.length);
        var bulkCnt = document.querySelector('[data-bulk-count]');
        if (bulkCnt) bulkCnt.textContent = '0';
        toast('Updated ' + ticked.length + ' message(s)');
      } else {
        toast('Tick one or more rows first');
      }
      return;
    }

    toast((button && button.textContent.trim()) || 'Submitted');
  });

  window.open = function (url) { post({ type: 'nav', href: local(url) }); return null; };
  window.addEventListener('load', function () { post({ type: 'loaded' }); });
})();
