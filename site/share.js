/* Find Great Architecture: the Share button (top right of every page) and the footer's Instagram / YouTube links
   (owner, 13 Nov 2026). One file for every page type: the wall, building, architect, topic and guide pages, the game and
   Studio FGA. The button and the footer row are written into each page by its template (so nothing jumps when this loads);
   this file only wires them up (by event delegation, so Studio's redrawn header works too) and writes the popover the
   first time it is opened. Styles: share.css.
   Counted as GoatCounter events (numbers only, through fgaEvent): share/open, share/copy, share/native, share/whatsapp,
   share/x, share/linkedin, share/email, social/instagram, social/youtube. No third-party script is loaded: the share
   targets are plain links. */
(function () {
  'use strict';
  var inFrame = false;
  try { inFrame = window.parent !== window && /[?&]embed\b/.test(location.search); } catch (e) { inFrame = true; }   // the wall inside a popup (popup.js)
  function removeButtons() { [].forEach.call(document.querySelectorAll('.fga-share'), function (b) { b.remove(); }); }
  if (inFrame) { removeButtons(); return; }
  var IG = 'https://www.instagram.com/findgreatarchitecture/', YT = 'https://www.youtube.com/@findgreatarchitecture';
  var count = function (path, title) { if (window.fgaEvent) window.fgaEvent(path, title); };
  var ICON = {
    whatsapp: '<path d="M4 20l1.3-4.2A8 8 0 1 1 8.4 18.8z"/><path d="M9.5 8.8c.2 2.6 2.4 4.8 5 5l1-1.3-1.8-.9-.8.6a4 4 0 0 1-1.9-1.9l.6-.8-.9-1.8z"/>',
    x: '<path d="M5 5l14 14M19 5L5 19"/>',
    linkedin: '<path d="M6 10v8M6 6.2v.1M10.5 18v-8M10.5 13.5c0-2 1.3-3.5 3.2-3.5 1.9 0 2.8 1.2 2.8 3.4V18"/>',
    email: '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="m4 7 8 6 8-6"/>',
    copy: '<rect x="8.5" y="8.5" width="11" height="11" rx="2"/><path d="M15.5 8.5v-2a2 2 0 0 0-2-2h-7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2"/>',
    share: '<circle cx="18" cy="5.5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="m8.2 10.8 7.6-4M8.2 13.2l7.6 4"/>',
    instagram: '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.2 6.8v.1"/>',
    youtube: '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10 9.2 5 2.8-5 2.8z"/>'
  };
  var svg = function (k) { return '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICON[k] + '</svg>'; };
  var esc = encodeURIComponent;

  // The address people get: the page's own canonical address with ?ref=share (GoatCounter lists it as "Campaign: share").
  // The wall keeps the opened building's #address; Studio's screens are never shared by their #step.
  function shareUrl() {
    var c = document.querySelector('link[rel="canonical"]'), u = c && c.href ? c.href : location.origin + location.pathname;
    u = u.split('#')[0];
    u += (u.indexOf('?') < 0 ? '?' : '&') + 'ref=share';
    if (/^\/(index\.html)?$/.test(location.pathname) && location.hash.length > 1) u += location.hash;
    return u;
  }
  var pageTitle = function () { return (document.title || 'Find Great Architecture').replace(/\s+/g, ' ').trim(); };

  var pop = null, veil = null, btn = null;
  function link(href, key, label, ev, evTitle, newTab) {
    return '<a class="fga-s-link" href="' + href + '"' + (newTab ? ' target="_blank" rel="noopener"' : '') + ' data-ev="' + ev + '" data-evt="' + evTitle + '">' + svg(key) + '<span>' + label + '</span></a>';
  }
  function build() {
    var u = shareUrl(), t = pageTitle(), native = !!navigator.share;
    veil = document.createElement('div'); veil.className = 'fga-s-veil'; veil.hidden = true;
    pop = document.createElement('div');
    pop.className = 'fga-s-pop'; pop.id = 'fgaSharePop'; pop.hidden = true;
    pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', 'Share this page'); pop.setAttribute('data-nosnippet', '');
    pop.innerHTML =
      '<p class="fga-s-h">Share this page</p>' +
      (native ? '<button type="button" class="fga-s-main" data-do="native">' + svg('share') + '<span>Share this page…</span></button>'
              : '<button type="button" class="fga-s-main" data-do="copy">' + svg('copy') + '<span class="fga-s-copy">Copy link</span></button>') +
      '<p class="fga-s-live" role="status" aria-live="polite"></p>' +
      '<p class="fga-s-sub">Send it on</p><div class="fga-s-row">' +
        link('https://wa.me/?text=' + esc(t + ' ' + u), 'whatsapp', 'WhatsApp', 'share/whatsapp', 'Share: WhatsApp', true) +
        link('https://twitter.com/intent/tweet?text=' + esc(t) + '&url=' + esc(u), 'x', 'X', 'share/x', 'Share: X', true) +
        link('https://www.linkedin.com/sharing/share-offsite/?url=' + esc(u), 'linkedin', 'LinkedIn', 'share/linkedin', 'Share: LinkedIn', true) +
        link('mailto:?subject=' + esc(t) + '&body=' + esc(t + '\n' + u), 'email', 'Email', 'share/email', 'Share: email', false) +
      '</div>' +
      '<p class="fga-s-sub">Follow us</p><div class="fga-s-row fga-s-follow">' +
        link(IG, 'instagram', 'Instagram <small>@findgreatarchitecture</small>', 'social/instagram', 'Follow: Instagram', true) +
        link(YT, 'youtube', 'YouTube <small>@findgreatarchitecture</small>', 'social/youtube', 'Follow: YouTube', true) +
      '</div>';
    document.body.appendChild(veil); document.body.appendChild(pop);
    pop.addEventListener('click', function (e) {
      var d = e.target.closest('[data-do]');
      if (d) { if (d.getAttribute('data-do') === 'native') doNative(); else doCopy(d); return; }
      var a = e.target.closest('[data-ev]');
      if (a) count(a.getAttribute('data-ev'), a.getAttribute('data-evt'));
    });
    veil.addEventListener('click', function () { close(true); });
    pop.addEventListener('focusout', function (e) { if (!pop.hidden && e.relatedTarget && !pop.contains(e.relatedTarget) && e.relatedTarget !== btn) close(false); });
  }
  function say(m) { var l = pop.querySelector('.fga-s-live'); if (l) l.textContent = m; }
  function doNative() {
    count('share/native', 'Share: this page (phone sheet)');
    navigator.share({ title: pageTitle(), url: shareUrl() }).then(function () { close(true); }, function () { /* closed without sharing */ });
  }
  function doCopy(b) {
    var u = shareUrl(), lab = b.querySelector('.fga-s-copy');
    var done = function () {
      count('share/copy', 'Share: copy link');
      if (lab) lab.textContent = 'Copied';
      b.classList.add('is-done'); say('Link copied');
      setTimeout(function () { if (lab) lab.textContent = 'Copy link'; b.classList.remove('is-done'); }, 2200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(u).then(done, function () { fallback(u, done); }); } else fallback(u, done);
  }
  function fallback(u, done) {
    var ta = document.createElement('textarea'); ta.value = u; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
    document.body.appendChild(ta); ta.select();
    try { if (document.execCommand('copy')) done(); else say('Press Ctrl+C to copy: ' + u); } catch (e) { say('Press Ctrl+C to copy: ' + u); }
    ta.remove();
  }
  // Under the button on a computer (kept inside the window); a sheet from the bottom on a narrow screen.
  function place() {
    if (!pop || pop.hidden || !btn) return;
    var vw = document.documentElement.clientWidth, sheet = vw <= 560;
    pop.classList.toggle('is-sheet', sheet); veil.hidden = !sheet;
    if (sheet) { pop.style.left = pop.style.top = pop.style.width = ''; return; }
    var r = btn.getBoundingClientRect(), w = Math.min(340, vw - 24);
    pop.style.width = w + 'px';
    pop.style.left = Math.max(12, Math.min(r.right - w, vw - w - 12)) + 'px';
    pop.style.top = Math.max(8, r.bottom + 8) + 'px';
  }
  function open(b) {
    if (!pop) build();
    btn = b; pop.hidden = false; b.setAttribute('aria-expanded', 'true');
    place();
    count('share/open', 'Share: opened');
    var f = pop.querySelector('.fga-s-main'); if (f) f.focus({ preventScroll: true });
  }
  function close(refocus) {
    if (!pop || pop.hidden) return;
    pop.hidden = true; veil.hidden = true;
    if (btn) { btn.setAttribute('aria-expanded', 'false'); if (refocus && btn.isConnected) btn.focus({ preventScroll: true }); }
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.fga-share');
    if (b) { e.stopPropagation(); if (pop && !pop.hidden && btn === b) close(true); else { close(false); open(b); } return; }
    if (pop && !pop.hidden && !pop.contains(e.target)) close(false);
    var a = e.target.closest && e.target.closest('.fga-social a[data-social]');   // the footer's row
    if (a) count('social/' + a.getAttribute('data-social'), 'Follow: ' + a.getAttribute('data-social'));
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && pop && !pop.hidden) { e.stopPropagation(); close(true); } }, true);
  window.addEventListener('resize', place);
})();
