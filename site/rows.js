/* Find Great Architecture: a hint on every row that scrolls sideways (owner, 22 Oct 2026). Red dots under the row say how far
   along you are (a dot jumps there) and arrows over its ends move it on; both stay hidden while everything already fits.
   Shared by the wall and every generated page. A row is anything matching SEL, or marked data-row. */
(function () {
  'use strict';
  var SEL = '[data-row], .arch .books, .onward > .row, .gallery > .slides, #relBooksRow';
  var OWN_ARROWS = { relBooksRow: true }; // the wall's related books already have arrows beside their heading

  function arrow(row, d) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'rowarr ' + (d < 0 ? 'prev' : 'next');
    b.setAttribute('aria-label', d < 0 ? 'Scroll back' : 'Scroll on');
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + (d < 0 ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7') + '"/></svg>';
    b.hidden = true;
    b.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      row.scrollBy({ left: d * Math.max(120, row.clientWidth * 0.85), behavior: 'smooth' });
    });
    return b;
  }

  function setup(row) {
    if (row.fgaRow) return;
    row.fgaRow = true;
    var host = row.parentNode, prev = null, next = null, raf = 0;
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    var dots = document.createElement('div');
    dots.className = 'rowdots';
    dots.setAttribute('aria-hidden', 'true');
    host.insertBefore(dots, row.nextSibling);
    if (!OWN_ARROWS[row.id]) { prev = arrow(row, -1); next = arrow(row, 1); host.appendChild(prev); host.appendChild(next); }

    function update() {
      raf = 0;
      var max = row.scrollWidth - row.clientWidth;
      var n = max > 4 ? Math.max(2, Math.min(10, Math.ceil(row.scrollWidth / row.clientWidth - 0.05))) : 0;
      var at = n ? Math.round(row.scrollLeft / max * (n - 1)) : 0;
      if (dots.children.length !== n) {
        var h = '';
        for (var i = 0; i < n; i++) h += '<button type="button" tabindex="-1" data-i="' + i + '"></button>';
        dots.innerHTML = h;
      }
      for (var j = 0; j < dots.children.length; j++) dots.children[j].className = j === at ? 'on' : '';
      if (prev) {
        // halfway down the covers or photos, not the whole row with its captions
        var pic = row.querySelector('img, .cv, .standin'), r0 = row.getBoundingClientRect(), mid = row.offsetHeight / 2;
        if (pic) { var r1 = pic.getBoundingClientRect(); if (r1.height) mid = r1.top - r0.top + r1.height / 2; }
        var top = row.offsetTop + mid - 18;
        prev.style.top = next.style.top = top + 'px';
        prev.style.left = (row.offsetLeft + 6) + 'px';
        next.style.left = (row.offsetLeft + row.offsetWidth - 42) + 'px';
        prev.hidden = !(n && row.scrollLeft > 4);
        next.hidden = !(n && row.scrollLeft < max - 4);
      }
    }
    var later = function () { if (!raf) raf = requestAnimationFrame(update); };
    dots.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-i]'), n = dots.children.length;
      if (b && n > 1) row.scrollTo({ left: +b.getAttribute('data-i') / (n - 1) * (row.scrollWidth - row.clientWidth), behavior: 'smooth' });
    });
    row.addEventListener('scroll', later, { passive: true });
    row.addEventListener('load', later, true); // covers arriving change how wide the row is
    window.addEventListener('resize', later);
    if (window.ResizeObserver) new ResizeObserver(later).observe(row);
    if (window.MutationObserver) new MutationObserver(later).observe(row, { childList: true }); // rows filled later (the wall's related books)
    later();
  }

  function scan() { [].forEach.call(document.querySelectorAll(SEL), setup); }
  window.fgaRows = { scan: scan };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
})();
