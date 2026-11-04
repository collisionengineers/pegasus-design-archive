/* v48 mockup runtime: composes each captured page into the frame and runs the strip.
   Presets (query string and strip): state, mode, diff, strip, dialog=send-report,
   viewer=N, rename=1, opt=width:880|1100,files:below|beside,card:after-figures|before-figures,
   money:pence|pounds. */
(function () {
  'use strict';
  var STATES = __STATES__;
  var ROUTES = __ROUTES__;
  window.__mockFragments = __FRAGMENTS__;

  var OPT_DEFAULTS = { width: '880', files: 'below', card: 'after-figures', money: 'pence' };
  var OPT_VALUES = { width: ['880', '1100'], files: ['below', 'beside'], card: ['after-figures', 'before-figures'], money: ['pence', 'pounds'] };

  var byKey = {};
  STATES.forEach(function (s) { byKey[s.key] = s; });
  var frame = document.getElementById('mock-frame');
  var strip = document.getElementById('mock-strip');
  var select = document.getElementById('mock-state');
  var changeList = document.getElementById('mock-changes');
  var toastEl = document.getElementById('mock-toast');

  function parseOpt(text) {
    var opt = Object.assign({}, OPT_DEFAULTS);
    String(text || '').split(',').forEach(function (pair) {
      var kv = pair.split(':');
      if (kv.length === 2 && OPT_VALUES[kv[0]] && OPT_VALUES[kv[0]].indexOf(kv[1]) >= 0) opt[kv[0]] = kv[1];
    });
    return opt;
  }
  function optText(opt) {
    return Object.keys(OPT_DEFAULTS).filter(function (k) { return opt[k] !== OPT_DEFAULTS[k]; })
      .map(function (k) { return k + ':' + opt[k]; }).join(',');
  }
  var stored = null;
  try { stored = localStorage.getItem('v48.opt'); } catch (e) { /* file: */ }

  var query = new URLSearchParams(location.search);
  var current = {
    key: byKey[query.get('state')] ? query.get('state') : (STATES[0] && STATES[0].key),
    mode: query.get('mode') === 'today' ? 'today' : 'proposal',
    diff: query.get('diff') === '1',
    dialog: query.get('dialog') === 'send-report' || query.get('dialog') === '1',
    viewer: query.get('viewer') !== null && query.get('viewer') !== '' ? parseInt(query.get('viewer'), 10) || 0 : null,
    rename: query.get('rename') === '1' || query.get('rename') === 'report',
    opt: parseOpt(query.get('opt') !== null ? query.get('opt') : stored)
  };
  if (current.viewer !== null || current.rename) current.dialog = true;
  var state0 = byKey[current.key];
  if (state0 && state0.dialog && !query.has('dialog') && !query.has('viewer') && !query.has('rename')) {
    current.dialog = true;
    if (state0.viewer !== undefined && state0.viewer !== null) current.viewer = state0.viewer;
    if (state0.rename) current.rename = true;
  }
  if (query.get('strip') === '0') document.body.classList.add('mock-strip-hidden');

  function esc(value) {
    return String(value == null ? '' : value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  }
  function asset(id) {
    var t = document.getElementById(id);
    return t ? t.innerHTML : '';
  }
  function attrs(map) {
    return Object.keys(map || {}).map(function (k) {
      var v = map[k];
      if (Array.isArray(v)) v = v.join(' ');
      return v === '' ? ' ' + k : ' ' + k + '="' + esc(v) + '"';
    }).join('');
  }

  var BODIES = JSON.parse(document.getElementById('mock-bodies').textContent);
  var unpacked = {};
  function body(id) {
    if (unpacked[id]) return Promise.resolve(unpacked[id]);
    var bytes = Uint8Array.from(atob(BODIES[id]), function (c) { return c.charCodeAt(0); });
    var stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    return new Response(stream).text().then(function (text) { unpacked[id] = text; return text; });
  }

  function compose(state, markup) {
    var proposal = current.mode === 'proposal' && state.hasProposal;
    var head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
      + '<title>' + esc(state.label) + '</title>'
      + state.css.map(function (c) { return asset('a-css-' + c); }).join('')
      + asset('a-css-frame');
    var htmlAttrs = Object.assign({}, state.htmlAttrs, { 'data-v48-mode': current.mode });
    if (current.diff) htmlAttrs['data-v48-diff'] = '';
    Object.keys(current.opt).forEach(function (k) { htmlAttrs['data-v48-opt-' + k] = current.opt[k]; });
    return '<!DOCTYPE html><html' + attrs(htmlAttrs) + '><head>' + head + '</head><body' + attrs(state.bodyAttrs) + '>'
      + asset('a-js-bridge') + asset('a-sprite') + markup
      + state.js.map(function (j) { return asset('a-js-' + j); }).join('')
      + (proposal ? asset('a-js-proposal') : '')
      + '</body></html>';
  }

  function money(value, guide) {
    var text = current.opt.money === 'pounds'
      ? '£' + Math.round(value).toLocaleString('en-GB')
      : '£' + value.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return text + (guide ? ' (' + guide + ')' : '');
  }

  // The presets a state opens on, applied once the page has loaded and its scripts bound.
  function applyPresets(state) {
    var d = frame.contentDocument;
    if (!d || !d.body) return;
    var card = d.querySelector('[data-v48-original-report]');
    var figures = d.querySelector('[data-case-aside] [data-figures]');
    if (card && figures) {
      if (current.opt.card === 'before-figures') figures.before(card); else figures.after(card);
    }
    Array.prototype.forEach.call(d.querySelectorAll('[data-v48-money]'), function (dd) {
      dd.textContent = money(parseFloat(dd.getAttribute('data-v48-money')), dd.getAttribute('data-v48-guide'));
    });
    if (current.dialog) {
      if (current.mode === 'proposal') {
        var opener = d.querySelector('[data-v48-send-open]');
        if (opener) opener.click();
      } else {
        var form = d.querySelector('form[data-send-report]');
        if (form) form.scrollIntoView({ block: 'start', behavior: 'instant' });
      }
    }
    if (current.dialog && current.mode === 'proposal' && current.rename) {
      var pencil = d.querySelector('[data-v48-file="AssessmentReport"] [data-v48-rename]');
      if (pencil) pencil.click();
    }
    if (current.dialog && current.mode === 'proposal' && current.viewer !== null) {
      var opens = d.querySelectorAll('[data-v48-file-open]');
      var open = opens[Math.min(current.viewer, opens.length - 1)];
      if (open) open.click();
    }
  }

  var pending = null;
  function render() {
    var state = byKey[current.key];
    if (!state) return Promise.resolve();
    var proposal = current.mode === 'proposal' && state.hasProposal;
    return body(state.key + '-' + (proposal ? 'proposal' : 'today')).then(function (markup) {
      return new Promise(function (resolve) {
        pending = resolve;
        frame.srcdoc = compose(state, markup);
        syncStrip(state);
        syncUrl();
      });
    });
  }
  frame.addEventListener('load', function () {
    var done = pending;
    pending = null;
    var state = byKey[current.key];
    if (state && state.scroll) {
      var target = frame.contentDocument && frame.contentDocument.querySelector(state.scroll);
      if (target) target.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
    if (state) applyPresets(state);
    if (done) setTimeout(done, 120);
  });

  function syncUrl() {
    var p = new URLSearchParams();
    p.set('state', current.key);
    p.set('mode', current.mode);
    if (current.diff) p.set('diff', '1');
    if (current.dialog) p.set('dialog', 'send-report');
    if (current.viewer !== null) p.set('viewer', String(current.viewer));
    if (current.rename) p.set('rename', '1');
    var opt = optText(current.opt);
    if (opt) p.set('opt', opt);
    if (document.body.classList.contains('mock-strip-hidden')) p.set('strip', '0');
    try { history.replaceState(null, '', '?' + p.toString()); } catch (e) { /* file: */ }
  }

  function syncStrip(state) {
    if (select.value !== current.key) select.value = current.key;
    strip.querySelectorAll('[data-mode]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-mode') === current.mode));
    });
    strip.querySelector('[data-diff]').setAttribute('aria-pressed', String(current.diff));
    strip.querySelectorAll('[data-preset]').forEach(function (b) {
      var p = b.getAttribute('data-preset');
      var on = p === 'dialog' ? current.dialog : p === 'viewer' ? current.viewer !== null : current.rename;
      b.setAttribute('aria-pressed', String(!!on));
    });
    strip.querySelectorAll('[data-opt]').forEach(function (s) { s.value = current.opt[s.getAttribute('data-opt')]; });
    changeList.innerHTML = state.changes && state.changes.length
      ? state.changes.map(function (c) { return '<li><strong>' + esc(c.id) + '</strong> ' + esc(c.summary) + '</li>'; }).join('')
      : '<li class="mock-none">No change proposed on this page.</li>';
  }

  var groups = {};
  STATES.forEach(function (s) {
    if (!groups[s.group]) {
      groups[s.group] = document.createElement('optgroup');
      groups[s.group].label = s.group;
      select.appendChild(groups[s.group]);
    }
    var option = document.createElement('option');
    option.value = s.key;
    option.textContent = s.label + (s.hasProposal ? '' : ' (no change)');
    groups[s.group].appendChild(option);
  });

  function resolveRoute(href) {
    var path = String(href || '').split('#')[0];
    var bare = path.split('?')[0];
    var view = /[?&]view=inspection\b/.test(path) ? bare + '?view=inspection' : null;
    var best = null;
    ROUTES.forEach(function (r) { if (!best && r[0] === path) best = r[1]; });
    if (view) ROUTES.forEach(function (r) { if (!best && r[0] === view) best = r[1]; });
    ROUTES.forEach(function (r) { if (!best && r[0] === bare) best = r[1]; });
    return best;
  }

  var toastTimer = null;
  function toast(text) {
    toastEl.textContent = text;
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.hidden = true; }, 2600);
  }

  window.addEventListener('message', function (ev) {
    var msg = ev.data || {};
    if (msg.type === 'toast') toast(msg.text);
    if (msg.type === 'posted') {
      window.__mock.lastPost = msg.fields;
      toast(msg.text + ': posted ' + msg.fields.length + ' fields (demo; nothing is sent)');
    }
    if (msg.type === 'nav') {
      var key = resolveRoute(msg.href);
      if (key && byKey[key] && key !== current.key) { current.key = key; current.dialog = false; current.viewer = null; current.rename = false; render(); }
      else if (!key) toast('Not drawn in this mockup: ' + msg.href);
    }
  });

  function presetsOf(key) {
    var s = byKey[key] || {};
    current.dialog = !!s.dialog;
    current.viewer = s.viewer !== undefined && s.viewer !== null ? s.viewer : null;
    current.rename = !!s.rename;
  }
  select.addEventListener('change', function () { current.key = select.value; presetsOf(current.key); render(); });
  strip.querySelectorAll('[data-mode]').forEach(function (b) {
    b.addEventListener('click', function () { current.mode = b.getAttribute('data-mode'); render(); });
  });
  strip.querySelector('[data-diff]').addEventListener('click', function () { current.diff = !current.diff; render(); });
  strip.querySelectorAll('[data-preset]').forEach(function (b) {
    b.addEventListener('click', function () {
      var p = b.getAttribute('data-preset');
      if (p === 'dialog') { current.dialog = !current.dialog; if (!current.dialog) { current.viewer = null; current.rename = false; } }
      if (p === 'viewer') { current.viewer = current.viewer === null ? 0 : null; if (current.viewer !== null) current.dialog = true; }
      if (p === 'rename') { current.rename = !current.rename; if (current.rename) current.dialog = true; }
      render();
    });
  });
  strip.querySelectorAll('[data-opt]').forEach(function (s) {
    s.addEventListener('change', function () {
      current.opt[s.getAttribute('data-opt')] = s.value;
      try { localStorage.setItem('v48.opt', optText(current.opt)); } catch (e) { /* file: */ }
      render();
    });
  });
  strip.querySelector('[data-opt-reset]').addEventListener('click', function () {
    current.opt = Object.assign({}, OPT_DEFAULTS);
    try { localStorage.removeItem('v48.opt'); } catch (e) { /* file: */ }
    render();
  });
  strip.querySelector('[data-hide-strip]').addEventListener('click', function () {
    document.body.classList.add('mock-strip-hidden');
    syncUrl();
  });

  window.__mock = {
    states: STATES.map(function (s) { return s.key; }),
    meta: function (key) { return byKey[key || current.key]; },
    get state() { return current.key; },
    get mode() { return current.mode; },
    get opt() { return Object.assign({}, current.opt); },
    lastPost: null,
    go: function (key, mode, options) {
      if (!byKey[key]) return Promise.reject(new Error('Unknown state ' + key));
      current.key = key;
      if (mode) current.mode = mode === 'proposal' ? 'proposal' : 'today';
      options = options || {};
      current.diff = !!options.diff;
      if (options.dialog === undefined && options.viewer === undefined && options.rename === undefined) {
        presetsOf(key);
      } else {
        current.dialog = !!options.dialog;
        current.viewer = options.viewer === undefined || options.viewer === null ? null : options.viewer;
        current.rename = !!options.rename;
        if (current.viewer !== null || current.rename) current.dialog = true;
      }
      current.opt = options.opt ? parseOpt(options.opt) : Object.assign({}, OPT_DEFAULTS);
      window.__mock.lastPost = null;
      return render();
    },
    doc: function () { return frame.contentDocument; },
    win: function () { return frame.contentWindow; },
    expand: function (on) {
      document.body.classList.toggle('mock-expanded', !!on);
      if (on) {
        var d = frame.contentDocument;
        frame.style.height = Math.max(d.documentElement.scrollHeight, d.body.scrollHeight) + 'px';
      } else {
        frame.style.height = '';
      }
    },
    toast: toast
  };
  render().then(function () { window.__mockReady = true; });
})();
