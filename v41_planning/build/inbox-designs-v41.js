/* v41 Inbox proposal: the message opens as a dialog over the Inbox. Its right column holds the
   Classification chips (one pressed, applied at once as an image tag is) and the Case picker.
   Rows carry a checkbox beside one bulk form (I18). Runs inside the captured live Inbox page
   (build-v41.py replaces the page content with [data-ibx]). Demo behaviour only. Not application code.
   window.__ibx = { preset: { selected, scope, dialog, fresh, data, ai, ticked, dismissed, busy } }
   ticked and dismissed are comma lists of message ids; busy names the bulk control drawn pressed (dismiss). */
(function () {
  'use strict';
  var cfg = window.__ibx || {};
  var CASE_HREF = '/Cases/QDOS26214';

  var CATEGORIES = ['New instruction', 'Triage request', 'Pre-instruction', 'Images received', 'Case update',
    'Cancellation', 'Query', 'Billing', 'General', 'Not client related', 'Internal CC'];
  var MAILBOX = 'desk@collisionengineers.co.uk';
  // The live Received sort toggle is a link per scope (captured-live/inbox/*.html); here it only draws.
  var SORT_OLDEST = {
    incoming: '/Inbox?sort=oldest', nocase: '/Inbox?queue=no_case_found&amp;sort=oldest',
    sent: '/Inbox?folder=sent&amp;sort=oldest', dismissed: '/Inbox?folder=dismissed&amp;sort=oldest'
  };

  // Cases from the live Cases capture, as the Case picker lists them: Case/PO · registration · claimant.
  var CASES = [
    { ref: 'QDOS26214', text: 'QDOS26214 · MA59BDY · J. Patel' },
    { ref: 'QDOS26215', text: 'QDOS26215 · KL19XYZ · K. Okafor' },
    { ref: 'QDOS26216', text: 'QDOS26216 · LB68HNR · M. Hargreaves' },
    { ref: 'QDOS26217', text: 'QDOS26217 · SG17PKD · R. Alvarez' }
  ];

  // The same messages the live capture seeded (ZzMockupCaptureInbox). nocase marks the three the live No Case Found
  // queue lists (captured-live/inbox/inbox-no-case-found.html): m1, m3 and m5.
  var MAIL = [
    { id: 'm1', scope: 'incoming', nocase: true, unread: true, sender: 'instructions@northline.example',
      subject: 'New instruction — MA59 BDY — rear impact',
      body: ['Please instruct an engineer to inspect our insured vehicle following a rear impact on 24 September.', "The vehicle is at the policyholder's address."],
      date: '13 Oct 2026', time: '09:14', decided: '13 Oct 2026 09:16',
      classification: 'New instruction', outcome: 'No Case Found', tone: 'amber', caseRef: null,
      files: [['rear-quarter.jpg', 'Image', '1.2 MB'], ['odometer.jpg', 'Image', '0.4 MB']],
      offer: { eyebrow: 'New instruction', label: 'Create case', icon: 'plus' } },
    { id: 'm2', scope: 'incoming', unread: false, sender: 'claims@northline.example',
      subject: 'Update — QDOS26214 — repair authority',
      body: ['Repair authority is attached. Please proceed on QDOS26214 and confirm the engineer.'],
      date: '13 Oct 2026', time: '08:02', decided: '13 Oct 2026 08:04',
      classification: 'Case update', outcome: 'Case created', tone: 'green', caseRef: 'QDOS26214',
      files: [['repair-authority.pdf', 'PDF', '205 KB']] },
    { id: 'm3', scope: 'incoming', nocase: true, unread: true, sender: null,
      subject: 'Please see attached', body: ['Photographs attached. No reference in the message.'],
      date: '12 Oct 2026', time: '17:48', decided: '12 Oct 2026 17:50',
      classification: null, outcome: 'No Case Found', tone: 'amber', caseRef: null,
      files: [['IMG_0001.jpg', 'Image', '879 KB'], ['IMG_0002.jpg', 'Image', '850 KB'], ['IMG_0003.jpg', 'Image', '859 KB']] },
    { id: 'm4', scope: 'incoming', unread: false, sender: 'claims@northline.example',
      subject: 'Query — QDOS26214 — hire charges', body: ['Please explain the hire charges on the report for QDOS26214.'],
      date: '12 Oct 2026', time: '11:20', decided: '12 Oct 2026 11:22',
      classification: 'Query', outcome: 'Case created', tone: 'green', caseRef: 'QDOS26214', files: [], query: true },
    { id: 'm5', scope: 'incoming', nocase: true, unread: true, sender: 'photos@northline.example',
      subject: 'Images — MA59 BDY', body: ['Further photographs of the rear quarter and the odometer.'],
      date: '11 Oct 2026', time: '15:05', decided: '11 Oct 2026 15:07',
      classification: 'Images received', outcome: 'No Case Found', tone: 'amber', caseRef: null,
      files: [['rear-quarter-2.jpg', 'Image', '1.0 MB'], ['odometer-2.jpg', 'Image', '371 KB']],
      offer: { eyebrow: 'Images received', label: 'Register images', icon: 'image' } },
    { id: 'm6', scope: 'sent', unread: false, sender: MAILBOX, to: 'claims@northline.example',
      subject: "Re: QDOS26214 — engineer's report", body: ["The engineer's report is attached."],
      date: '10 Oct 2026', time: '14:11', classification: null, outcome: null, sent: true, caseRef: 'QDOS26214',
      files: [['QDOS26214_report.pdf', 'PDF', '625 KB']] }
  ];

  var state = {
    scope: 'incoming', fresh: 'current', data: 'present', dialog: '', selected: 'm1',
    ai: 'start', dismissed: {}, ticked: {}, caseQuery: ''
  };
  var preset = cfg.preset || {};
  function fromList(text) {
    var map = {};
    String(text || '').split(',').forEach(function (id) { id = id.trim(); if (id) map[id] = true; });
    return map;
  }
  if (preset.ai) state.ai = preset.ai;
  ['selected', 'scope', 'dialog', 'fresh', 'data'].forEach(function (k) { if (preset[k]) state[k] = preset[k]; });
  if (preset.dismissed) state.dismissed = fromList(preset.dismissed);
  if (preset.ticked) state.ticked = fromList(preset.ticked);
  if (state.scope === 'nocase' && !preset.selected) state.selected = 'm3';
  if (state.scope === 'sent' && !preset.selected) state.selected = 'm6';
  state.composeAi = state.dialog === 'compose' && state.ai === 'ready';

  function esc(v) {
    return String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function icon(id) { return '<svg class="icon" aria-hidden="true"><use href="#icon-' + id + '"></use></svg>'; }
  function chip(text, tone) { return '<span class="status status--' + (tone || 'neutral') + '">' + esc(text) + '</span>'; }
  function caseLink(ref) { return '<a class="mono" href="' + CASE_HREF + '">' + esc(ref) + '</a>'; }
  function post(message) { try { window.parent.postMessage(message, '*'); } catch (e) { /* detached */ } }
  function toast(text) { post({ type: 'toast', text: text }); }
  function sync() {
    post({ type: 'ibx-state', state: {
      selected: state.selected, scope: state.scope, dialog: state.dialog,
      fresh: state.fresh === 'current' ? '' : state.fresh, data: state.data === 'present' ? '' : state.data,
      ticked: Object.keys(state.ticked).join(','), dismissed: Object.keys(state.dismissed).join(',')
    } });
  }

  function senderOf(m) { return m.sender || 'Sender not recorded'; }
  function byId(id) { return MAIL.filter(function (m) { return m.id === id; })[0] || null; }

  function visible() {
    if (state.data === 'empty' || state.scope === 'deleted') return [];
    if (state.scope === 'nocase') return MAIL.filter(function (m) { return m.nocase && !state.dismissed[m.id]; });
    if (state.scope === 'sent') return MAIL.filter(function (m) { return m.scope === 'sent'; });
    if (state.scope === 'dismissed') return MAIL.filter(function (m) { return state.dismissed[m.id]; });
    return MAIL.filter(function (m) { return m.scope === 'incoming' && !state.dismissed[m.id]; });
  }
  function current() {
    var rows = visible();
    return rows.filter(function (m) { return m.id === state.selected; })[0] || rows[0] || null;
  }

  // -- bulk (I18) ------------------------------------------------------------
  // Incoming scopes: Dismiss and Correct classification. Dismissed: Restore. Sent Items and Deleted Items: none.
  function bulkScope() { return state.scope === 'incoming' || state.scope === 'nocase' || state.scope === 'dismissed'; }
  function ticks() {
    return visible().filter(function (m) { return state.ticked[m.id]; }).map(function (m) { return m.id; });
  }
  // The buttons are always enabled: a post with nothing ticked writes nothing (finding-mail-bulk-actions criterion 5),
  // and a disabled button cannot be enabled without script (criterion 11). The busy words are the existing
  // OperatorLabels.Busy ones the single-message Dismiss carries.
  function bulkBar() {
    if (!bulkScope() || !visible().length) return '';
    var buttons = state.scope === 'dismissed'
      ? '<button type="submit" class="btn btn--small" data-bulk="restore" data-busy-label="Restoring…">' + icon('undo') + '<span>Restore</span></button>'
      : '<button type="submit" class="btn btn--small" data-bulk="dismiss" data-busy-label="Dismissing…">' + icon('x') + '<span>Dismiss</span></button>'
        + '<button type="button" class="btn btn--small" data-bulk="classify">Correct classification</button>';
    return '<form id="ibx-bulk" class="ibx-bulk" method="post" data-v41-change="I18">'
      + '<span class="ibx-bulk-count tabular" data-bulk-count>' + ticks().length + '</span>' + buttons + '</form>';
  }
  function tickBox(m) {
    return '<label class="ibx-row-tick"><input type="checkbox" form="ibx-bulk" name="ids" value="' + m.id + '" data-tick="' + m.id + '" data-v41-change="I18"'
      + ' aria-label="' + esc(m.subject) + '"' + (state.ticked[m.id] ? ' checked' : '') + ' /></label>';
  }
  function updateBulk() {
    var n = ticks().length;
    var count = mount && mount.querySelector('[data-bulk-count]');
    if (count) count.textContent = String(n);
  }
  // The busy state (finding-mail-bulk-actions criterion 13): the pressed bulk control says its Busy word and the
  // loader glyph turns, as site.js (pegasusBusy) shows any action. Drawn once, for the `busy` preset, after
  // site.js has loaded.
  function drawBusy() {
    var form = mount && mount.querySelector('#ibx-bulk');
    var control = form && form.querySelector('[data-bulk="' + preset.busy + '"]');
    if (control && window.pegasusBusy) window.pegasusBusy.start(control, form);
  }
  if (preset.busy) window.addEventListener('load', drawBusy);

  // -- the Inbox -------------------------------------------------------------
  function freshness() {
    var label = state.fresh === 'stale' ? 'Stale' : state.fresh === 'unavailable' ? 'Unavailable' : 'Current';
    var never = state.fresh === 'unavailable' && state.data === 'empty';
    var dot = state.fresh === 'stale' ? 'partial' : state.fresh === 'unavailable' ? 'failed' : '';
    var notice = state.fresh === 'stale' ? chip('Stale', 'amber') : state.fresh === 'unavailable' ? chip('Unavailable', 'red') : '';
    return '<div class="freshness"><span class="freshness-status"><span class="health-dot ' + dot + '"></span><span><time>' + (never ? 'Never updated' : label + ' · 09:20') + '</time></span>' + notice + '</span>'
      + '<div class="refresh-button"><button type="button" class="btn btn--small" title="Refresh">' + icon('refresh-cw') + '<span>Refresh</span></button></div></div>';
  }

  function scopeRail() {
    var empty = state.data === 'empty';
    var live = MAIL.filter(function (m) { return !state.dismissed[m.id]; });
    var counts = {
      incoming: live.filter(function (m) { return m.scope === 'incoming'; }).length,
      nocase: live.filter(function (m) { return m.nocase; }).length,
      sent: MAIL.filter(function (m) { return m.sent; }).length,
      dismissed: Object.keys(state.dismissed).length, deleted: 0
    };
    return [
      ['incoming', 'inbox', 'All incoming'], ['nocase', 'search', 'No Case Found'], ['sent', 'send', 'Sent Items'],
      ['dismissed', 'x', 'Dismissed'], ['deleted', 'trash-2', 'Deleted Items']
    ].map(function (s) {
      return '<button type="button" class="scope-button" data-scope="' + s[0] + '" aria-pressed="' + (state.scope === s[0]) + '"'
        + (s[0] === 'deleted' ? ' data-v41-change="I1"' : '') + '>'
        + '<span class="scope-visual-icon">' + icon(s[1]) + '</span><span>' + s[2] + '</span>'
        + (empty ? '' : '<span class="tabular">' + counts[s[0]] + '</span>') + '</button>';
    }).join('');
  }

  function filters() {
    var categoryOff = state.scope === 'sent' || state.scope === 'deleted';
    return '<form class="inbox-filter ibx-filter" aria-label="Mail view" data-v41-change="I1">'
      + '<div class="field"><label for="ibx-mailbox">Mailbox</label><select id="ibx-mailbox"><option selected>All Mailboxes</option><option>' + MAILBOX + '</option></select></div>'
      + '<div class="field"><label for="ibx-category">Category</label><select id="ibx-category"' + (categoryOff ? ' disabled' : '') + '><option>All categories</option>'
      + CATEGORIES.map(function (c) { return '<option>' + c + '</option>'; }).join('') + '</select></div>'
      + '<div class="field inbox-filter__search"><label for="ibx-search">Search</label><input id="ibx-search" type="search" maxlength="200" /></div>'
      + '<button class="btn btn--dark" type="button">' + icon('search') + '<span>Search</span></button></form>';
  }

  function row(m) {
    var selected = current() && current().id === m.id;
    var reply = !m.sent && state.scope !== 'dismissed';
    var dismiss = state.scope === 'incoming' || state.scope === 'nocase';
    var restore = state.scope === 'dismissed';
    var ticking = bulkScope();
    var files = m.files.length ? m.files.length + ' attachment' + (m.files.length === 1 ? '' : 's') : '';
    return '<div class="row-button inbox-row' + (m.unread ? ' unread' : '') + (reply && (dismiss || restore) ? ' inbox-row--two-actions' : '') + (ticking ? ' inbox-row--ticks' : '') + '" data-mail-row="' + m.id + '" aria-current="' + selected + '">'
      + (ticking ? tickBox(m) : '')
      + '<span class="row-top"><span class="row-title">' + (m.unread ? '<span class="unread-indicator" aria-hidden="true"></span><span class="sr-only">Unread</span>' : '') + esc(m.sent ? m.to : senderOf(m)) + '</span>'
      + '<span class="row-time"><time>' + m.date + '</time><time>' + m.time + '</time></span></span>'
      + '<button type="button" class="row-title" data-open-dialog="' + m.id + '">' + esc(m.subject) + '</button>'
      + '<span class="row-excerpt">' + esc(m.body[0]) + '</span>'
      + '<span class="row-top">' + (m.sent ? '<span class="cluster"></span>' : '<span class="cluster">' + chip(m.outcome, m.tone) + '<span class="row-meta">' + esc(m.classification || 'Unclassified') + '</span></span>')
      + (m.caseRef ? '<span class="row-meta">' + caseLink(m.caseRef) + (files ? ' · ' + files : '') + '</span>' : files ? '<span class="row-meta">' + files + '</span>' : '') + '</span>'
      + ((reply || dismiss || restore) ? '<div class="inbox-row-actions">'
        + (reply ? '<button type="button" class="icon-button" data-compose="' + m.id + '" title="Reply" aria-label="Reply ' + esc(m.subject) + '">' + icon('reply') + '</button>' : '')
        + (dismiss ? '<button type="button" class="icon-button" data-dismiss="' + m.id + '" title="Dismiss" aria-label="Dismiss ' + esc(m.subject) + '">' + icon('x') + '</button>' : '')
        + (restore ? '<button type="button" class="icon-button" data-restore="' + m.id + '" title="Restore" aria-label="Restore ' + esc(m.subject) + '">' + icon('undo') + '</button>' : '')
        + '</div>' : '')
      + '</div>';
  }

  function emptyCopy() {
    if (state.scope === 'deleted') return '<p>Deleted items messages are not kept in Pegasus yet. Only received mail is retained.</p>';
    if (state.scope === 'dismissed') return '<p>No dismissed messages.</p>';
    if (state.scope === 'sent') return '';
    return '<p>No mail has been received.</p>';
  }

  function listBody() {
    if (state.fresh === 'unavailable' && state.data === 'empty') {
      return '<div class="notice notice--danger" role="status">' + icon('info') + '<span>Unavailable</span></div>';
    }
    var rows = visible();
    if (!rows.length) return '<div class="empty">' + emptyCopy() + '</div>';
    return '<div data-row-list>' + rows.map(row).join('') + '</div>';
  }

  function inboxPage() {
    var count = visible().length;
    return '<header class="page-header"><div class="page-title"><p class="eyebrow">Emails</p><h1>Inbox</h1></div><div class="page-actions"><div class="page-action-group">' + freshness() + '</div></div></header>'
      + '<section class="pane-layout pane-layout--2 inbox-layout" aria-label="Emails" data-v41-change="I4">'
      + '<aside class="pane"><div class="pane-body pane-scroll"><div class="scope-list">' + scopeRail() + '</div></div></aside>'
      + '<div class="pane">' + filters()
      + '<div class="pane-head inbox-messages-head"><div class="inbox-message-title"><h2>Messages</h2></div><span class="meta">' + count + ' message' + (count === 1 ? '' : 's') + '</span>'
      + (state.scope === 'deleted' ? '' : '<a class="btn btn--small sort-toggle" aria-label="Received order: newest first; activate for oldest first" href="' + SORT_OLDEST[state.scope] + '">Received ↓</a>') + '</div>'
      + bulkBar()
      + '<div class="pane-body pane-scroll" tabindex="0">' + listBody() + '</div></div></section>';
  }

  // -- the message dialog ----------------------------------------------------
  var AI_DRAFT = 'Dear Northline Claims,\n\nThank you for your e-mail of 12 October. The hire charges on the report for QDOS26214 cover 14 days at the agreed daily rate while the vehicle was off the road awaiting parts.\n\nKind regards,\nCollision Engineers';

  /* The one primary of the dialog: the classification's next action, as the live
     record bar offers it (Create case, Register images, PR 1331's AI reply). */
  function primaryAction(m) {
    if (m.query) {
      if (state.ai === 'queued') return '<span class="meta ibx-ai-pending" data-v41-change="I16">AI draft · Queued</span>';
      if (state.ai === 'ready') return '<button type="button" class="btn btn--dark" data-ai-reply="' + m.id + '">' + icon('sparkles') + '<span>Reply with AI draft</span></button>';
      return '<button type="button" class="btn btn--dark" data-ai-start>' + icon('sparkles') + '<span>Draft reply with AI</span></button>';
    }
    if (!m.offer) return '';
    return '<button type="button" class="btn btn--dark">' + icon(m.offer.icon) + '<span>' + esc(m.offer.label) + '</span></button>';
  }

  /* Classification: the eleven categories as chips, one pressed, applied at once as an image tag is. */
  function chipSet(m) {
    return '<div class="ibx-chipset" role="group" aria-labelledby="ibx-class-label">' + CATEGORIES.map(function (c) {
      var on = m.classification === c;
      return '<button type="button" class="ibx-chip" data-set-classification="' + esc(c) + '" aria-pressed="' + on + '">' + (on ? icon('check') : '') + '<span>' + esc(c) + '</span></button>';
    }).join('') + '</div>';
  }

  /* The Case picker, as the live composer draws it: Case / PO, its hint, and the option list under the input. */
  function casePicker() {
    return '<div class="field case-picker" data-case-picker>'
      + '<label for="ibx-case-query">Case / PO</label>'
      + '<input id="ibx-case-query" type="text" maxlength="100" autocomplete="off" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="ibx-case-options" value="' + esc(state.caseQuery) + '" />'
      + '<span class="field-hint">Search by Case / PO, registration, claimant, claim number, or Principal.</span>'
      + '<div id="ibx-case-options" class="case-picker-options" data-case-picker-options hidden></div></div>';
  }

  /* v41 items I9, I12: Decision states the facts once. The chips are Classification, the picker sits under the
     Case, and Change linked Case, Unlink (or Link to Case) are one row of small buttons beneath it. */
  function decision(m) {
    var caseValue = m.caseRef ? caseLink(m.caseRef) : '<span class="quiet">None</span>';
    if (m.sent) {
      return '<section class="decision-card ibx-decision" data-v41-change="I9 I12"><h2 class="decision-head">Decision</h2><div class="decision-body"><div class="decision-facts">'
        + '<div class="decision-row"><span>Classification</span><strong>Not recorded</strong></div>'
        + '<div class="decision-row"><span>Case</span><strong>' + caseValue + '</strong></div>'
        + '</div></div></section>';
    }
    var actions = '<div class="ibx-decision-actions">'
      + (m.caseRef
        ? '<button type="button" class="btn btn--small" data-open-link>Change linked Case</button><button type="button" class="btn btn--small" data-open-unlink>Unlink</button>'
        : '<button type="button" class="btn btn--small" data-open-link>Link to Case</button>')
      + '</div>';
    return '<section class="decision-card ibx-decision" data-v41-change="I9 I12"><h2 class="decision-head">Decision</h2><div class="decision-body"><div class="decision-facts">'
      + '<div class="ibx-decision-block"><span class="ibx-decision-label" id="ibx-class-label">Classification</span>' + chipSet(m) + '</div>'
      + '<div class="decision-row"><span>Case</span><strong>' + caseValue + '</strong></div>'
      + '<div class="ibx-decision-block">' + casePicker() + '</div>'
      + actions
      + (m.decided ? '<div class="decision-row"><span>Decided</span><strong><time>' + m.decided + '</time> · Automatic</strong></div>' : '')
      + '</div></div></section>';
  }

  function messageBody(m) {
    return '<div class="mail-body">' + m.body.map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('') + '</div>';
  }

  function attachments(m) {
    if (!m.files.length) return '<div class="empty"><p>This message has no attachments.</p></div>';
    return '<div class="table-wrap message-attachments"><table class="table table--compact"><thead><tr><th scope="col">File</th><th scope="col">Type</th><th scope="col">Size</th><th scope="col"><span class="sr-only">Open</span></th></tr></thead><tbody>'
      + m.files.map(function (f) { return '<tr><td>' + esc(f[0]) + '</td><td>' + f[1] + '</td><td class="tabular">' + f[2] + '</td><td class="right"><button type="button" class="btn btn--small">Open file</button></td></tr>'; }).join('')
      + '</tbody></table></div>';
  }

  function thread(m) {
    var related = MAIL.filter(function (x) { return x.caseRef && x.caseRef === m.caseRef; });
    if (related.length < 2) related = [m];
    return '<div data-row-list>' + related.map(function (x) {
      return '<div class="row-button"' + (x.id === m.id ? ' aria-current="page"' : '') + '><span class="row-top"><span class="row-title">' + esc(x.sent ? x.sender : senderOf(x)) + '</span><span class="row-time"><time>' + x.date + '</time><time>' + x.time + '</time></span></span><span class="row-title">' + esc(x.subject) + '</span></div>';
    }).join('') + '</div>';
  }

  /* The composer: the live fields, with From, To and Case on one route line. */
  function compose(m) {
    var ai = m.query && state.ai === 'ready' && state.composeAi;
    return '<div class="stack ibx-compose">'
      + '<p class="mail-route">From ' + MAILBOX + ' · To ' + esc(m.sender || '') + (m.caseRef ? ' · Case ' + caseLink(m.caseRef) : '') + '</p>'
      + '<div class="field"><label for="ibx-reply-subject">Subject</label><input id="ibx-reply-subject" value="Re: ' + esc(m.subject) + '" /></div>'
      + (ai ? '<div class="notice" role="status" data-ai-draft>' + icon('sparkles') + '<span><span class="src-tag src-tag--ai">AI</span> Draft written 12 Oct 2026 11:31 by Claude. Edit before sending.</span></div>' : '')
      + '<div class="field"><label for="ibx-reply-body">Message</label><textarea id="ibx-reply-body" rows="9">' + (ai ? esc(AI_DRAFT) : '') + '</textarea></div>'
      + (m.query ? '<label class="choice"><input type="checkbox" data-resolve-query' + (ai ? ' checked' : '') + ' /> Also resolve query</label>' : '')
      + '</div>';
  }

  function dialogBody(m, section) {
    if (section === 'attachments') return attachments(m);
    if (section === 'thread') return thread(m);
    return '<div class="ibx-split"><div class="ibx-read">' + messageBody(m) + '</div><aside class="stack">' + decision(m) + '</aside></div>';
  }

  function navigation(m) {
    var rows = visible();
    var i = rows.map(function (x) { return x.id; }).indexOf(m.id);
    var prev = i > 0 ? rows[i - 1].id : '';
    var next = i >= 0 && i < rows.length - 1 ? rows[i + 1].id : '';
    return '<span class="cluster ibx-nav" data-v41-change="I6">'
      + '<button type="button" class="icon-button" data-go-message="' + prev + '" aria-label="Previous message" title="Previous message"' + (prev ? '' : ' disabled') + '>' + icon('chevron-left') + '</button>'
      + '<button type="button" class="icon-button" data-go-message="' + next + '" aria-label="Next message" title="Next message"' + (next ? '' : ' disabled') + '>' + icon('chevron-right') + '</button></span>';
  }

  function messageDialog(m) {
    var composing = state.dialog === 'compose';
    var section = ['attachments', 'thread'].indexOf(state.dialog) !== -1 ? state.dialog : 'message';
    var tabs = composing ? '' : '<nav class="tabs ibx-tabs" aria-label="Sections">' + [['message', 'Message'], ['attachments', 'Attachments' + (m.files.length ? ' <span class="tab-count">' + m.files.length + '</span>' : '')], ['thread', 'Thread']].map(function (t) {
      return '<button type="button" class="tab" data-section="' + t[0] + '" aria-current="' + (section === t[0] ? 'page' : 'false') + '">' + t[1] + '</button>';
    }).join('') + '</nav>';
    var route = 'From ' + esc(senderOf(m)) + ' · To ' + esc(m.sent ? m.to : MAILBOX) + ' · <time>' + m.date + ' ' + m.time + '</time>';
    var foot = composing
      ? '<button type="button" class="btn" data-section="message">Cancel</button><button type="button" class="btn btn--dark" data-send>' + icon('send') + '<span>Send</span></button>'
      : (m.sent ? '' : '<span class="left"><button type="button" class="btn" data-dismiss="' + m.id + '">' + icon(state.scope === 'dismissed' ? 'undo' : 'x') + '<span>' + (state.scope === 'dismissed' ? 'Restore' : 'Dismiss') + '</span></button></span>')
        + (m.sent ? '' : '<button type="button" class="btn" data-compose="' + m.id + '">' + icon('reply') + '<span>Reply</span></button><button type="button" class="btn" data-compose="' + m.id + '">Reply all</button>')
        + '<button type="button" class="btn" data-compose="' + m.id + '">Forward</button>'
        + primaryAction(m);
    return '<div class="dialog-backdrop" data-dialog="message"><section class="dialog dialog--mail" role="dialog" aria-modal="true" aria-labelledby="ibx-message-title" data-v41-change="I2 I17">'
      + '<div class="dialog-head"><div class="ibx-head-title"><h2 id="ibx-message-title" class="wrap" tabindex="-1">' + (composing ? 'Reply · ' : '') + esc(m.subject) + '</h2>'
      + (composing ? '' : '<p class="mail-route">' + route + '</p>') + '</div>'
      + '<span class="ibx-head-tools">' + (composing ? '' : navigation(m)) + '<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">' + icon('x') + '</button></span></div>'
      + tabs
      + '<div class="dialog-body">' + (composing ? compose(m) : dialogBody(m, section)) + '</div>'
      + '<div class="dialog-foot">' + foot + '</div></section></div>';
  }

  /* I18: the existing Correct classification inputs, entered once for every ticked row. */
  function classifyDialog() {
    return '<div class="dialog-backdrop" data-dialog="classify"><section class="dialog" role="dialog" aria-modal="true" aria-labelledby="ibx-classify-title" data-v41-change="I18">'
      + '<div class="dialog-head"><h2 id="ibx-classify-title" tabindex="-1">Correct classification</h2></div><form data-ibx-reason><div class="dialog-body stack">'
      + '<div class="field"><label for="ibx-classification">Classification</label><select id="ibx-classification"><option value="">Choose classification</option>'
      + CATEGORIES.map(function (c) { return '<option>' + c + '</option>'; }).join('') + '<option>Unclassified</option></select></div>'
      + '<div class="field" data-work-type-field hidden><label class="req" for="ibx-work-type">Case type</label><select id="ibx-work-type"><option value="">Choose case type</option><option>Inspection</option><option>Audit</option><option>Inspection and Audit</option></select></div>'
      + '<div class="field"><label class="req" for="ibx-correction-reason">Reason for correction</label><textarea id="ibx-correction-reason" rows="3" required></textarea></div>'
      + '</div><div class="dialog-foot"><button type="button" class="btn" data-dialog-close>Cancel</button><button type="submit" class="btn btn--dark" data-busy-label="Saving…">Save correction</button></div></form></section></div>';
  }

  function reasonDialog(title) {
    return '<div class="dialog-backdrop" data-dialog="link"><section class="dialog" role="dialog" aria-modal="true" aria-labelledby="ibx-link-title" data-v41-change="I13">'
      + '<div class="dialog-head"><h2 id="ibx-link-title" tabindex="-1">' + esc(title) + '</h2></div><form data-ibx-reason><div class="dialog-body stack">'
      + '<div class="field"><label class="req" for="ibx-link-reason">Reason for action</label><textarea id="ibx-link-reason" rows="3" required></textarea></div>'
      + '</div><div class="dialog-foot"><button type="button" class="btn" data-dialog-close>Cancel</button><button type="submit" class="btn btn--primary">Confirm Action</button></div></form></section></div>';
  }

  // -- rendering ---------------------------------------------------------------
  var mount = document.querySelector('[data-ibx]');
  var dialogRoot = document.createElement('div');
  dialogRoot.className = 'ibx';
  dialogRoot.setAttribute('data-ibx-dialog', '');
  document.body.appendChild(dialogRoot);
  var shell = document.querySelector('.app-shell');

  function renderDialogs() {
    var m = current();
    var bulk = state.dialog === 'bulk-classify' && state.data !== 'empty';
    if (!state.dialog || (!bulk && !m) || state.data === 'empty') {
      dialogRoot.innerHTML = '';
      if (shell) shell.removeAttribute('inert');
      return;
    }
    var parts = [];
    if (bulk) {
      parts.push(classifyDialog());
    } else {
      parts.push(messageDialog(m));
      if (state.dialog === 'link') parts.push(reasonDialog(m.caseRef ? 'Change linked Case' : 'Link to Case'));
      if (state.dialog === 'unlink') parts.push(reasonDialog('Unlink from ' + m.caseRef));
    }
    dialogRoot.innerHTML = parts.join('');
    if (shell) shell.setAttribute('inert', '');
    var dialogs = dialogRoot.querySelectorAll('[role=dialog]');
    var heading = dialogs[dialogs.length - 1].querySelector('h2[tabindex]');
    if (heading) heading.focus({ preventScroll: true, focusVisible: false });
  }

  function render() {
    if (mount) mount.innerHTML = inboxPage();
    renderDialogs();
    sync();
  }
  function set(patch) {
    if (patch.selected && patch.selected !== state.selected) state.caseQuery = '';
    Object.keys(patch).forEach(function (k) { state[k] = patch[k]; });
    render();
  }
  function closeTop() {
    var nested = ['link', 'unlink'].indexOf(state.dialog) !== -1;
    set({ dialog: nested ? 'message' : '' });
  }

  function showCaseOptions() {
    var box = dialogRoot.querySelector('[data-case-picker-options]');
    var input = dialogRoot.querySelector('#ibx-case-query');
    if (!box || !input) return;
    var term = state.caseQuery.trim().toLowerCase();
    var hits = term.length < 2 ? [] : CASES.filter(function (c) { return c.text.toLowerCase().indexOf(term) !== -1; });
    box.innerHTML = hits.length
      ? '<ul class="command-results" role="listbox" data-case-picker-list>' + hits.map(function (c, i) {
        return '<li role="none"><button type="button" role="option" id="ibx-case-option-' + i + '" class="command-result" aria-selected="false" data-case-option="' + c.ref + '">' + esc(c.text) + '</button></li>';
      }).join('') + '</ul>'
      : '';
    box.hidden = !hits.length;
    input.setAttribute('aria-expanded', String(hits.length > 0));
  }

  function inScope(el) { return el && el.closest && el.closest('[data-ibx],[data-ibx-dialog]'); }

  document.addEventListener('click', function (ev) {
    if (!inScope(ev.target)) return;
    if (ev.target.closest('.sort-toggle')) { ev.preventDefault(); return; }
    var t = ev.target.closest('[data-ai-start],[data-ai-reply],[data-open-dialog],[data-scope],[data-dialog-close],[data-set-classification],[data-case-option],[data-bulk],[data-compose],[data-dismiss],[data-restore],[data-section],[data-open-link],[data-open-unlink],[data-send],[data-go-message],[data-mail-row]');
    if (!t) return;
    if (t.hasAttribute('data-open-dialog')) { ev.preventDefault(); set({ selected: t.getAttribute('data-open-dialog'), dialog: 'message' }); }
    else if (t.hasAttribute('data-scope')) set({ scope: t.getAttribute('data-scope'), dialog: '', ticked: {} });
    else if (t.hasAttribute('data-dialog-close')) { ev.preventDefault(); closeTop(); }
    else if (t.hasAttribute('data-set-classification')) {
      var category = t.getAttribute('data-set-classification');
      var viewed = current();
      if (viewed) viewed.classification = category;
      set({});
      var pressed = dialogRoot.querySelector('[data-set-classification="' + category + '"]');
      if (pressed) pressed.focus({ preventScroll: true });
    }
    else if (t.hasAttribute('data-case-option')) {
      var ref = t.getAttribute('data-case-option');
      state.caseQuery = ref;
      var field = dialogRoot.querySelector('#ibx-case-query');
      if (field) { field.value = ref; field.setAttribute('aria-expanded', 'false'); field.focus({ preventScroll: true }); }
      var list = dialogRoot.querySelector('[data-case-picker-options]');
      if (list) { list.innerHTML = ''; list.hidden = true; }
    }
    else if (t.hasAttribute('data-bulk')) { if (t.getAttribute('data-bulk') === 'classify' && ticks().length) set({ dialog: 'bulk-classify' }); }
    else if (t.hasAttribute('data-compose')) { ev.preventDefault(); set({ selected: t.getAttribute('data-compose'), dialog: 'compose' }); }
    else if (t.hasAttribute('data-section')) set({ dialog: t.getAttribute('data-section') });
    else if (t.hasAttribute('data-open-link')) set({ dialog: 'link' });
    else if (t.hasAttribute('data-open-unlink')) set({ dialog: 'unlink' });
    else if (t.hasAttribute('data-send')) { set({ dialog: 'message', composeAi: false }); toast('Sent'); }
    else if (t.hasAttribute('data-ai-start')) set({ ai: 'queued' });
    else if (t.hasAttribute('data-ai-reply')) set({ selected: t.getAttribute('data-ai-reply'), dialog: 'compose', composeAi: true });
    else if (t.hasAttribute('data-go-message')) { var to = t.getAttribute('data-go-message'); if (to) set({ selected: to, dialog: 'message' }); }
    else if (t.hasAttribute('data-dismiss') || t.hasAttribute('data-restore')) {
      var mid = t.getAttribute('data-dismiss') || t.getAttribute('data-restore');
      var restoring = t.hasAttribute('data-restore') || state.scope === 'dismissed';
      var rows = visible(); var at = rows.map(function (x) { return x.id; }).indexOf(mid);
      var following = rows[at + 1] || rows[at - 1];
      if (restoring) delete state.dismissed[mid]; else state.dismissed[mid] = true;
      delete state.ticked[mid];
      var inDialog = !!t.closest('[data-ibx-dialog]');
      set(inDialog && following ? { selected: following.id, dialog: 'message' } : { dialog: inDialog ? '' : state.dialog });
      toast(restoring ? 'Restored' : 'Dismissed');
    }
    // A tick, or the gutter that holds it, neither opens nor pins the row.
    else if (t.hasAttribute('data-mail-row') && !ev.target.closest('button,a,details,input,select,form,label')) set({ selected: t.getAttribute('data-mail-row') });
  });

  document.addEventListener('change', function (ev) {
    if (ev.target.matches && ev.target.matches('[data-tick]')) {
      var id = ev.target.getAttribute('data-tick');
      if (ev.target.checked) state.ticked[id] = true; else delete state.ticked[id];
      updateBulk();
      sync();
    }
    if (ev.target.id === 'ibx-classification') {
      var field = dialogRoot.querySelector('[data-work-type-field]');
      if (field) field.hidden = ev.target.value !== 'New instruction';
    }
  });

  document.addEventListener('input', function (ev) {
    if (ev.target.id !== 'ibx-case-query') return;
    state.caseQuery = ev.target.value;
    showCaseOptions();
  });

  document.addEventListener('submit', function (ev) {
    if (!inScope(ev.target)) return;
    ev.preventDefault();
    if (ev.target.id === 'ibx-bulk') {
      var kind = ev.submitter && ev.submitter.getAttribute('data-bulk');
      var ids = ticks();
      if (!ids.length || (kind !== 'dismiss' && kind !== 'restore')) return;
      ids.forEach(function (mid) {
        if (kind === 'restore') delete state.dismissed[mid]; else state.dismissed[mid] = true;
        delete state.ticked[mid];
      });
      set({});
      toast(kind === 'restore' ? 'Restored' : 'Dismissed');
      return;
    }
    if (ev.target.closest('[data-ibx-reason]')) {
      if (state.dialog === 'bulk-classify') {
        var select = ev.target.querySelector('#ibx-classification');
        if (select && select.value) {
          var label = select.options[select.selectedIndex].text;
          ticks().forEach(function (mid) { byId(mid).classification = label === 'Unclassified' ? null : label; });
          state.ticked = {};
        }
      }
      closeTop();
    }
  }, true);

  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && state.dialog) { ev.preventDefault(); closeTop(); }
  });

  window.InboxDesigns = {
    state: function () { return state; },
    preset: function (search) {
      var q = new URLSearchParams(search);
      ['selected', 'scope', 'dialog', 'fresh', 'data'].forEach(function (k) { if (q.has(k)) state[k] = q.get(k); });
      if (q.has('dismissed')) state.dismissed = fromList(q.get('dismissed'));
      if (q.has('ticked')) state.ticked = fromList(q.get('ticked'));
      render();
    }
  };
  render();
})();
