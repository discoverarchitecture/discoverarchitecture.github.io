/* Find Great Architecture: the AI jury presentation generator button in every page's top bar (owner, 24 Oct 2026; the wall has
   its own in app.js). On a computer it goes straight to Studio FGA (/studio/); on a phone it opens the same sheet as on the
   wall, from the bottom, which leads there. Pressing it is counted as studio/ai-button and following the sheet's link as
   studio/ai-link, as on the wall; the address says which kind of page it was pressed on (?ref=building, architect, hub,
   game or page). Styles in ai.css. */
(function () {
  'use strict';
  var me = document.currentScript, up = me ? me.getAttribute('src').replace(/ai\.js.*$/, '') : '/';
  var seg = location.pathname.split('/').filter(Boolean)[0] || '';
  var ref = { buildings: 'building', architects: 'architect', styles: 'hub', types: 'hub', cities: 'hub', ideas: 'hub', play: 'game' }[seg] || 'page';
  var url = up + 'studio/?ref=' + ref, pop = null, veil = null, from = null;
  var phone = function () { return matchMedia('(max-width: 820px)').matches; };
  var count = function (path, title) { if (window.fgaEvent) fgaEvent(path, title); };
  var SPARK = '<svg class="ai-spark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5c.6 4.6 2.9 6.9 7.5 7.5-4.6.6-6.9 2.9-7.5 7.5-.6-4.6-2.9-6.9-7.5-7.5 4.6-.6 6.9-2.9 7.5-7.5z"/><path d="M19 14.5c.3 2 1.3 3 3.3 3.3-2 .3-3 1.3-3.3 3.3-.3-2-1.3-3-3.3-3.3 2-.3 3-1.3 3.3-3.3z"/></svg>';

  // The sheet, written the first time it is needed (the same words as the wall's, in site/index.html).
  function make() {
    if (pop) return;
    veil = document.createElement('div'); veil.className = 'ai-veil'; veil.hidden = true;
    pop = document.createElement('section');
    pop.className = 'ai-pop'; pop.id = 'aiPop'; pop.hidden = true;
    pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-modal', 'false'); pop.setAttribute('aria-labelledby', 'aiTitle');
    pop.innerHTML =
      '<button type="button" class="ai-close" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' +
      '<div class="ai-head">' + SPARK + '<h2 id="aiTitle">AI Jury Presentation Generator</h2></div>' +
      '<p class="ai-soon">Studio FGA · Live now</p>' +
      '<img class="ai-board" src="' + up + 'studio/board.webp" alt="A sample A1 jury board of the Salk Institute, made for this preview" width="600" height="849" loading="lazy">' +
      '<p class="ai-text">You design; it presents. Upload your drawings, name the ideas your board must explain, and get a professional-grade jury board and editable deck.</p>' +
      '<ul class="ai-list"><li>Concept diagrams you guide</li><li>A1, A0 and 24 × 36 in boards</li><li>Editable PowerPoint and PDF</li></ul>' +
      '<a class="ai-go" href="' + url + '">See Studio FGA <span aria-hidden="true">→</span></a>' +
      '<p class="ai-fine">Free preview first · pay once from $11</p>' +
      '<p class="ai-fine ai-legal"><a href="' + up + 'pricing/">Pricing</a> · <a href="' + up + 'terms/">Terms</a> · <a href="' + up + 'refunds/">Refunds</a> · <a href="' + up + 'privacy/">Privacy</a> · <a href="' + up + 'contact/">Contact</a></p>';
    document.body.appendChild(veil); document.body.appendChild(pop);
    pop.querySelector('.ai-go').addEventListener('click', function () { count('studio/ai-link', 'AI panel: See Studio FGA'); });
    pop.querySelector('.ai-close').addEventListener('click', function () { show(false); if (from) from.focus(); });
    veil.addEventListener('click', function () { show(false); });
  }
  function show(open) {
    pop.hidden = !open; veil.hidden = !open;
    if (from) from.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) { pop.querySelector('.ai-go').focus({ preventScroll: true }); count('studio/ai-button', 'AI Jury Presentation Generator'); }
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.ai-btn');
    if (!b) { if (pop && !pop.hidden && !pop.contains(e.target)) show(false); return; }
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return; // a new tab, as the reader asked
    e.preventDefault();
    if (phone()) { make(); var again = from === b && !pop.hidden; from = b; return show(!again); }
    count('studio/ai-button', 'AI Jury Presentation Generator');
    setTimeout(function () { location.href = url; }, 150); // a moment for the count to leave
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && pop && !pop.hidden) { show(false); if (from) from.focus(); } });
  // the buttons written into the page point at the right address before anything is pressed
  document.addEventListener('DOMContentLoaded', function () {
    [].forEach.call(document.querySelectorAll('a.ai-btn'), function (a) { a.href = url; });
  });
})();
