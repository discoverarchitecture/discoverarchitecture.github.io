/* Studio FGA guides: the slim "Try free" bar at the bottom of the screen (tools/build_guides.py writes its markup).
   It shows once the reader has scrolled past the card under the intro, steps aside while the closing box is on screen,
   and a close (×) keeps it closed for the rest of the visit (sessionStorage; private windows may refuse it, so every
   use is wrapped and the bar simply works without memory there). */
(function () {
  var bar = document.getElementById('gbar');
  var top = document.querySelector('.gcta-top');
  var end = document.querySelector('.gcta-end');
  if (!bar || !top) return;
  var KEY = 'studio-guides-bar-closed';
  try { if (sessionStorage.getItem(KEY) === '1') { bar.parentNode.removeChild(bar); return; } } catch (e) { /* no storage */ }

  // The page keeps room at the bottom for the bar, so it never covers the last lines on a phone.
  document.body.classList.add('gbar-pad');
  var pastTop = false, endOnScreen = false;
  function update() { bar.hidden = !(pastTop && !endOnScreen); }

  if (!('IntersectionObserver' in window)) { pastTop = true; update(); }
  else {
    new IntersectionObserver(function (es) {
      var e = es[es.length - 1];
      pastTop = !e.isIntersecting && e.boundingClientRect.top < 0;
      update();
    }).observe(top);
    if (end) new IntersectionObserver(function (es) {
      endOnScreen = es[es.length - 1].isIntersecting;
      update();
    }).observe(end);
  }

  bar.querySelector('.gbar-x').addEventListener('click', function () {
    try { sessionStorage.setItem(KEY, '1'); } catch (e) { /* closes for this page only */ }
    bar.parentNode.removeChild(bar);
    document.body.classList.remove('gbar-pad');
    if (window.fgaEvent) window.fgaEvent('studio/guides/bar-closed', 'Studio · guides · bar closed');
  });
})();
