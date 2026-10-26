/* v42 mockup bridge. Runs first inside every composed page. There is no server
   behind the mockup: requests for captured fragments are answered from the
   capture, every other request never settles (so nothing flips to an error
   state), and links between captured pages switch state in the parent. */
(function () {
  'use strict';
  var host = window.parent;
  function post(message) {
    try { host.postMessage(message, '*'); } catch (e) { /* detached */ }
  }
  function local(url) {
    var text = String(url || '');
    var match = text.match(/^[a-z]+:\/\/[^/]+(\/.*)$/i);
    return match ? match[1] : text;
  }

  var fragments = (host && host.__mockFragments) || {};
  window.fetch = function (input) {
    var url = local(typeof input === 'string' ? input : (input && input.url));
    var html = fragments[url];
    if (typeof html === 'string') {
      return Promise.resolve(new Response(html, { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' } }));
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

  window.addEventListener('click', function (ev) {
    if (ev.defaultPrevented) return;
    var link = ev.target.closest && ev.target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href') || '';
    if (!href || href.charAt(0) === '#' || /^(mailto:|tel:|javascript:)/i.test(href)) return;
    ev.preventDefault();
    post({ type: 'nav', href: local(href), text: (link.textContent || '').trim() });
  });
  window.addEventListener('submit', function (ev) {
    if (ev.defaultPrevented) return;
    ev.preventDefault();
    var button = ev.submitter;
    post({ type: 'toast', text: (button && button.textContent.trim()) || 'Submitted' });
  });
  window.open = function (url) { post({ type: 'nav', href: local(url) }); return null; };
  window.addEventListener('load', function () { post({ type: 'loaded' }); });
})();
