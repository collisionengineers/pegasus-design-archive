/* v48 proposal behaviour, run inside a Proposal page after the live scripts. It binds
   only the hooks the patches add (data-v48-*), so Today markup is untouched:
   - a Files row's name opens the Case viewer on a drawn page bearing the file name
     (there is no file behind a mockup; the live viewer is the one that opens);
   - Rename: the name becomes an input of its stem with .pdf fixed, Enter or blur keeps
     it, Escape cancels, Reset restores the policy name and clears the posted name. */
(function () {
  'use strict';
  function stemOf(name) { return /\.pdf$/i.test(name) ? name.slice(0, -4) : name; }
  function escapeXml(text) {
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pageFor(name) {
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="794" height="1123" viewBox="0 0 794 1123">'
      + '<rect width="794" height="1123" fill="#fff"/>'
      + '<rect x="56" y="56" width="140" height="12" fill="#c8102e"/>'
      + '<text x="56" y="120" font-family="Segoe UI, system-ui, sans-serif" font-size="22" font-weight="700" fill="#202629">' + escapeXml(name) + '</text>'
      + '<text x="56" y="150" font-family="Segoe UI, system-ui, sans-serif" font-size="13" fill="#626b70">Mockup page: the stored file opens here.</text>'
      + Array.apply(null, Array(28)).map(function (_, i) {
        var width = 560 - (i % 5) * 60;
        return '<rect x="56" y="' + (200 + i * 26) + '" width="' + width + '" height="8" fill="#e9edef"/>';
      }).join('')
      + '</svg>';
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }

  function rowOf(element) { return element.closest('[data-v48-file]'); }
  function parts(row) {
    return {
      open: row.querySelector('[data-v48-file-open]'),
      pencil: row.querySelector('[data-v48-rename]'),
      box: row.querySelector('[data-v48-rename-row]'),
      input: row.querySelector('[data-v48-rename-row] input'),
      posted: row.querySelector('[data-v48-file-name]')
    };
  }
  function setName(row, name) {
    var p = parts(row);
    p.open.setAttribute('data-file-name', name);
    p.open.setAttribute('title', 'Open ' + name);
    p.open.querySelector('b').textContent = name;
    p.pencil.setAttribute('aria-label', 'Rename ' + name);
    if (p.posted) { p.posted.value = name === row.getAttribute('data-v48-default') ? '' : name; }
  }
  function startRename(row) {
    var p = parts(row);
    p.input.value = stemOf(p.open.getAttribute('data-file-name'));
    p.open.hidden = true;
    p.pencil.hidden = true;
    p.box.hidden = false;
    p.input.focus();
    p.input.select();
  }
  function endRename(row, keep) {
    var p = parts(row);
    if (p.box.hidden) return;
    if (keep) {
      var stem = p.input.value.trim();
      if (stem) { setName(row, stem + '.pdf'); }
    }
    p.box.hidden = true;
    p.open.hidden = false;
    p.pencil.hidden = false;
    p.open.focus();
  }
  function resetName(row) {
    var p = parts(row);
    setName(row, row.getAttribute('data-v48-default'));
    p.box.hidden = true;
    p.open.hidden = false;
    p.pencil.hidden = false;
    p.open.focus();
  }

  // O: every To / Cc box carries its ×; the live Add To / Add Cc append a bare input, which
  // is wrapped as it arrives. The one remaining To box keeps no × (a send needs one To).
  function decorateRecipients(stack) {
    Array.prototype.forEach.call(stack.querySelectorAll(':scope > input'), function (input) {
      var wrapper = document.createElement('div');
      wrapper.className = 'v48-recipient';
      wrapper.setAttribute('data-v48-recipient', '');
      input.replaceWith(wrapper);
      wrapper.appendChild(input);
      var remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'btn btn--small btn--icon';
      remove.setAttribute('data-v48-remove-recipient', '');
      remove.setAttribute('aria-label', 'Remove recipient');
      remove.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg>';
      wrapper.appendChild(remove);
    });
    keepOne(stack);
  }
  function keepOne(stack) {
    var rows = stack.querySelectorAll('[data-v48-recipient]');
    var sole = stack.hasAttribute('data-v48-keep-one') && rows.length === 1;
    Array.prototype.forEach.call(rows, function (row) {
      var remove = row.querySelector('[data-v48-remove-recipient]');
      if (remove) remove.hidden = sole;
    });
  }
  function watchRecipients() {
    ['report-recipient-to', 'report-recipient-cc'].forEach(function (id) {
      var stack = document.getElementById(id);
      if (!stack || stack.dataset.v48Watched) return;
      stack.dataset.v48Watched = 'true';
      decorateRecipients(stack);
      new MutationObserver(function () { decorateRecipients(stack); }).observe(stack, { childList: true });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watchRecipients); else watchRecipients();

  document.addEventListener('click', function (ev) {
    var remove = ev.target.closest && ev.target.closest('[data-v48-remove-recipient]');
    if (remove) {
      ev.preventDefault();
      var row = remove.closest('[data-v48-recipient]');
      var stack = row && row.parentElement;
      if (row) row.remove();
      if (stack) keepOne(stack);
      return;
    }
    var open = ev.target.closest && ev.target.closest('[data-v48-file-open]');
    if (open) {
      ev.preventDefault();
      var name = open.getAttribute('data-file-name') || '';
      var viewer = window.pegasusCaseViewer;
      if (viewer && typeof viewer.openDocument === 'function') {
        viewer.openDocument({ href: pageFor(name), name: name, download: pageFor(name), downloadLabel: 'Download', invoker: open });
      }
      return;
    }
    var pencil = ev.target.closest && ev.target.closest('[data-v48-rename]');
    if (pencil) { ev.preventDefault(); startRename(rowOf(pencil)); return; }
    var reset = ev.target.closest && ev.target.closest('[data-v48-rename-reset]');
    if (reset) { ev.preventDefault(); resetName(rowOf(reset)); }
  });
  document.addEventListener('keydown', function (ev) {
    var input = ev.target.closest && ev.target.closest('[data-v48-rename-row] input');
    if (!input) return;
    if (ev.key === 'Enter') { ev.preventDefault(); endRename(rowOf(input), true); }
    if (ev.key === 'Escape') { ev.preventDefault(); ev.stopImmediatePropagation(); endRename(rowOf(input), false); }
  }, true);
  document.addEventListener('focusout', function (ev) {
    var input = ev.target.closest && ev.target.closest('[data-v48-rename-row] input');
    if (!input) return;
    var to = ev.relatedTarget;
    if (to && to.closest && to.closest('[data-v48-rename-row]') === input.closest('[data-v48-rename-row]')) return;
    endRename(rowOf(input), true);
  });
})();
