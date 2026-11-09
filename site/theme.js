// Day or night, decided before the page draws so there is no white flash. A choice made with the switch is kept in
// this browser and used on every page; without one, the page follows the device's own setting, even as it changes.
(function () {
  var root = document.documentElement, KEY = 'night', dark = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function apply(night) {
    if (night) root.setAttribute('data-night', ''); else root.removeAttribute('data-night');
    var bs = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < bs.length; i++) { bs[i].setAttribute('aria-pressed', night ? 'true' : 'false'); bs[i].setAttribute('aria-label', night ? 'Day view' : 'Night view'); }
    try { window.dispatchEvent(new CustomEvent('themechange', { detail: { night: night } })); } catch (e) { /* old browsers */ }
  }
  var s = saved();
  apply(s ? s === '1' : !!(dark && dark.matches));
  if (dark && dark.addEventListener) dark.addEventListener('change', function (e) { if (!saved()) apply(e.matches); });
  window.DA_THEME = {
    night: function () { return root.hasAttribute('data-night'); },
    toggle: function () { var n = !root.hasAttribute('data-night'); try { localStorage.setItem(KEY, n ? '1' : '0'); } catch (e) { /* private mode */ } apply(n); }
  };
  document.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('[data-theme-toggle]'); if (b) DA_THEME.toggle(); });
  document.addEventListener('DOMContentLoaded', function () { apply(root.hasAttribute('data-night')); }); // label the switches once they exist
})();

// Studio FGA corner card (owner, 5 Nov 2026): a small card bottom-right on computers only, never on phones, never on
// /studio and never inside the wall's popup frame. It opens on every page load (refresh included) after half a page or
// 20 seconds; closing it keeps it away for the rest of that visit (owner, 5 Nov 2026). On building pages it steps aside
// while the "Jury coming up?" banner is on screen. The picture is the Studio landing page's before → after art (images/studio-card/), loaded only when it opens.
(function () {
  var CARD = {
    eyebrow: 'Studio FGA',
    heading: 'Jury coming up?',
    text: 'Your own drawings, renders and brief, laid out as an editable A1 jury board + deck.',
    link_text: 'Try Studio FGA →',
    fine: 'Polish $6.49 · Transform $9.34 · No subscription',
    link: 'studio/?utm_source=site&utm_campaign=corner_card',   // from the site root
    alt: 'Before: six rough sketches and drawings. After: one finished A1 jury board.'
  };
  var KEY = 'fga-studio-card', WAIT = 20000;
  var me = document.currentScript, base = me ? me.src.replace(/theme\.js.*$/, '') : '/';
  if (window.top !== window || /\/studio(\/|$)/.test(location.pathname) || !window.matchMedia) return;
  var wide = matchMedia('(min-width: 821px) and (hover: hover) and (pointer: fine)');
  function get(s, k) { try { return s.getItem(k); } catch (e) { return null; } }
  function put(s, k, v) { try { s.setItem(k, v); } catch (e) { /* private mode */ } }
  function away() { return get(sessionStorage, KEY) === 'closed'; }
  try { localStorage.removeItem(KEY); } catch (e) { /* the old 30-day setting, no longer used */ }
  if (away()) return;
  var card = null, shown = false, timer = null;
  var MONO = 'var(--mono, "Barlow Condensed", system-ui, sans-serif)';

  function css() {
    var s = document.createElement('style');
    s.textContent =
      '.scard{position:fixed;z-index:58;right:20px;bottom:96px;width:372px;max-width:calc(100vw - 40px);background:var(--surface);color:var(--ink);border:1px solid var(--hair);border-radius:18px;box-shadow:0 18px 48px rgba(0,0,0,.2);overflow:hidden;font-family:var(--sans, Barlow, system-ui, sans-serif)}' +
      '.scard[hidden]{display:none}' +
      '.scard .sc-art{display:block;height:214px;padding:10px 14px 6px;background:#FFF6EA url("' + base + 'images/studio-card/light.webp") center/contain no-repeat;background-origin:content-box;border-bottom:1px solid var(--hair)}' +
      ':root[data-night] .scard .sc-art{background-color:#191814;background-image:url("' + base + 'images/studio-card/night.webp")}' +
      '.scard .sc-body{display:grid;gap:8px;padding:14px 18px 16px}' +
      '.scard .sc-eye{font-family:' + MONO + ';font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--red-ink)}' +
      ':root[data-night] .scard .sc-eye{color:var(--red)}' +
      '.scard h2{margin:0;font-family:inherit;font-weight:700;font-size:21px;line-height:1.1;letter-spacing:0;text-transform:none;color:var(--ink)}' +
      '.scard p{margin:0;font-family:inherit;font-weight:400;font-size:15px;line-height:1.4}' +
      '.scard .sc-go{display:flex;align-items:center;justify-content:center;min-height:44px;margin-top:2px;border-radius:10px;background:var(--red);color:#fff;font-family:inherit;font-weight:600;font-size:15px;text-decoration:none}' +
      '.scard .sc-go:hover{background:var(--red-ink);color:#fff}' +
      '.scard .sc-go:focus-visible,.scard .sc-x:focus-visible{outline:2px solid var(--ink);outline-offset:2px}' +
      '.scard .sc-fine{font-family:' + MONO + ';font-weight:500;font-size:12px;letter-spacing:.02em;color:var(--graphite);text-align:center}' +
      '.scard .sc-x{position:absolute;top:10px;right:10px;width:32px;height:32px;display:grid;place-items:center;padding:0;border:0;border-radius:50%;background:var(--surface);color:var(--graphite);font:400 20px/1 system-ui, sans-serif;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,.14)}' +
      '.scard .sc-x:hover{color:var(--red)}';
    document.head.appendChild(s);
  }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text) n.textContent = text; return n; }
  function build() {
    css();
    card = el('aside', 'scard');
    card.setAttribute('aria-labelledby', 'scard-h');
    card.setAttribute('data-nosnippet', '');
    var x = el('button', 'sc-x', '×'); x.type = 'button'; x.setAttribute('aria-label', 'Close');
    var art = el('span', 'sc-art'); art.setAttribute('role', 'img'); art.setAttribute('aria-label', CARD.alt);
    var body = el('div', 'sc-body'), h = el('h2', '', CARD.heading); h.id = 'scard-h';
    var go = el('a', 'sc-go', CARD.link_text); go.href = base + CARD.link;
    body.append(el('span', 'sc-eye', CARD.eyebrow), h, el('p', '', CARD.text), go, el('p', 'sc-fine', CARD.fine));
    card.append(x, art, body);
    x.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && card) close(); });
    document.body.appendChild(card);
    var banner = document.querySelector('.studio-banner'), onBanner = false;   // building pages: never the same offer twice on one screen
    function fit() { if (card) card.hidden = onBanner || !wide.matches; }
    if (banner && window.IntersectionObserver) new IntersectionObserver(function (es) { onBanner = es[0].isIntersecting; fit(); }).observe(banner);
    if (wide.addEventListener) wide.addEventListener('change', fit);
  }
  function close() {
    put(sessionStorage, KEY, 'closed');   // gone for this visit
    if (card) { card.remove(); card = null; }
    stop();
  }
  function open() {
    if (shown || away() || !wide.matches) return;
    shown = true;
    stop();
    build();
  }
  function stop() { clearTimeout(timer); document.removeEventListener('scroll', onScroll, true); }
  function onScroll(e) {   // the page, or a panel that scrolls on its own (architect and topic pages)
    var t = e.target && e.target.nodeType === 1 ? e.target : document.scrollingElement || document.documentElement;
    if (t.scrollHeight > t.clientHeight * 1.5 && t.scrollTop > 200 && t.scrollTop + t.clientHeight >= t.scrollHeight * 0.5) open();
  }
  function start() {
    timer = setTimeout(open, WAIT);
    document.addEventListener('scroll', onScroll, { passive: true, capture: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
