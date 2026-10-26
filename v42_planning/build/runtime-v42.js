/* v42 mockup runtime: composes each captured page into the frame and runs the strip. */
(function () {
  'use strict';
  var STATES = __STATES__;
  var ROUTES = __ROUTES__;
  window.__mockFragments = __FRAGMENTS__;
  window.__mockDialogs = __DIALOGS__;

  var byKey = {};
  STATES.forEach(function (s) { byKey[s.key] = s; });
  var frame = document.getElementById('mock-frame');
  var strip = document.getElementById('mock-strip');
  var select = document.getElementById('mock-state');
  var changeList = document.getElementById('mock-changes');
  var toastEl = document.getElementById('mock-toast');

  var query = new URLSearchParams(location.search);
  var current = {
    key: byKey[query.get('state')] ? query.get('state') : (STATES[0] && STATES[0].key),
    mode: query.get('mode') === 'proposal' ? 'proposal' : 'today',
    diff: query.get('diff') === '1'
  };
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

  function compose(state, body) {
    var head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
      + '<base href="https://localhost:7139/">'
      + '<title>' + esc(state.label) + '</title>'
      + state.css.map(function (c) { return asset('a-css-' + c); }).join('')
      + asset('a-css-frame');
    var htmlAttrs = Object.assign({}, state.htmlAttrs, { 'data-v42-mode': current.mode });
    if (current.diff) htmlAttrs['data-v42-diff'] = '';
    return '<!DOCTYPE html><html' + attrs(htmlAttrs) + '><head>' + head + '</head><body' + attrs(state.bodyAttrs) + '>'
      + asset('a-js-bridge') + asset('a-sprite') + body
      + state.js.map(function (j) { return asset('a-js-' + j); }).join('')
      + '</body></html>';
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
    if (done) setTimeout(done, 30);
  });

  function syncUrl() {
    var p = new URLSearchParams();
    p.set('state', current.key);
    p.set('mode', current.mode);
    if (current.diff) p.set('diff', '1');
    if (document.body.classList.contains('mock-strip-hidden')) p.set('strip', '0');
    try { history.replaceState(null, '', '?' + p.toString()); } catch (e) { /* file: */ }
  }

  function syncStrip(state) {
    if (select.value !== current.key) select.value = current.key;
    strip.querySelectorAll('[data-mode]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-mode') === current.mode));
    });
    strip.querySelector('[data-diff]').setAttribute('aria-pressed', String(current.diff));
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
    var best = null;
    ROUTES.forEach(function (r) {
      if (r[0] === path) best = best || r[1];
    });
    if (best) return best;
    ROUTES.forEach(function (r) { if (!best && r[0] === bare) best = r[1]; });
    if (best) return best;
    var longest = '';
    ROUTES.forEach(function (r) {
      if (r[0].length > longest.length && r[0] !== '/' && bare.indexOf(r[0]) === 0) { longest = r[0]; best = r[1]; }
    });
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
    if (msg.type === 'nav') {
      var key = resolveRoute(msg.href);
      if (key && byKey[key]) { current.key = key; render(); }
      else toast('Not drawn in this mockup: ' + msg.href);
    }
  });

  select.addEventListener('change', function () { current.key = select.value; render(); });
  strip.querySelectorAll('[data-mode]').forEach(function (b) {
    b.addEventListener('click', function () { current.mode = b.getAttribute('data-mode'); render(); });
  });
  strip.querySelector('[data-diff]').addEventListener('click', function () { current.diff = !current.diff; render(); });
  strip.querySelector('[data-hide-strip]').addEventListener('click', function () {
    document.body.classList.add('mock-strip-hidden');
    syncUrl();
  });

  window.__mock = {
    states: STATES.map(function (s) { return s.key; }),
    meta: function (key) { return byKey[key || current.key]; },
    get state() { return current.key; },
    get mode() { return current.mode; },
    go: function (key, mode, options) {
      if (!byKey[key]) return Promise.reject(new Error('Unknown state ' + key));
      current.key = key;
      if (mode) current.mode = mode === 'proposal' ? 'proposal' : 'today';
      options = options || {};
      current.diff = !!options.diff;
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
