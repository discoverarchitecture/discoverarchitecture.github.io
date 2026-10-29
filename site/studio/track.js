// Counts what people do in FGA Studio as GoatCounter events, so the owner can see at which step people stop
// (owner, 29 Oct 2026). Numbers only: never a file name, an answer, an email or anything a student typed.
// Loaded after ../analytics.js (which defines fgaEvent) and after app.js; it only listens, it changes nothing.
//   studio/screen/<screen>          a step reached: home, upload, q, heard, planning, plan, price, making, result, edit, files, share
//   studio/click/<screen>/<action>  a button or link pressed, named by its data-act (and its choice, e.g. tier-transform)
//   studio/files/<screen>           files chosen or dropped
//   studio/typed/<screen>           started typing in a box (what was typed is never sent)
//   studio/scroll/<25|50|75|100>    how far down the landing page people read
// Each is counted once per visit, so the numbers read as "how many visitors got this far".
(function () {
  if (!window.fgaEvent) return;
  var sent = {};
  function once(path) {
    if (sent[path]) return;
    sent[path] = 1;
    window.fgaEvent(path, 'Studio · ' + path.slice(7).replace(/\//g, ' · '));
  }
  function screen() { return document.body.dataset.screen || 'home'; }
  var safe = /^[a-z][a-z0-9-]{0,23}$/i;  // short words only: no indices, file names or typed text

  // Steps reached: app.js writes the screen's name on <body data-screen> each time it draws one.
  var last = '';
  function seen() {
    var s = document.body.dataset.screen;
    if (s && s !== last) { last = s; once('studio/screen/' + s); if (s === 'home') depth(); }
  }
  new MutationObserver(seen).observe(document.body, { attributes: true, attributeFilter: ['data-screen'] });
  seen();

  // Every button and link.
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('[data-act], a[href], button, summary');
    if (!el) return;
    var what;
    if (el.dataset.act && safe.test(el.dataset.act)) {
      var choice = el.dataset.v || el.dataset.s || '';
      what = el.dataset.act + (safe.test(choice) ? '-' + choice : '');
    } else if (el.tagName === 'A') {
      var u;
      try { u = new URL(el.getAttribute('href'), location.href); } catch (err) { return; }
      what = u.host === location.host ? 'link' + (u.pathname.replace(/\/+$/, '').replace(/[^a-z0-9]+/gi, '-').toLowerCase() || '-home')
        : 'out-' + u.host.replace(/^www\./, '').split('.')[0];
    } else what = el.tagName === 'SUMMARY' ? 'open-details' : 'button';
    once('studio/click/' + screen() + '/' + what);
  }, true);

  // Files chosen or dropped, and typing started (the content itself is never read).
  document.addEventListener('change', function (e) {
    if (e.target.type === 'file' && e.target.files && e.target.files.length) once('studio/files/' + screen());
  }, true);
  document.addEventListener('drop', function () { once('studio/files/' + screen()); }, true);
  document.addEventListener('input', function (e) {
    if (/^(text|email|search|url|tel)$|^$/.test(e.target.type || '') || e.target.tagName === 'TEXTAREA') once('studio/typed/' + screen());
  }, true);

  // How far down the landing page people read.
  var marks = [25, 50, 75, 100], watching = false;
  function depth() {
    if (watching) return;
    watching = true;
    addEventListener('scroll', function () {
      if (screen() !== 'home') return;
      var h = document.documentElement.scrollHeight - innerHeight;
      var at = h > 0 ? (scrollY / h) * 100 : 100;
      marks.forEach(function (m) { if (at >= m - 1) once('studio/scroll/' + m); });
    }, { passive: true });
  }
})();
