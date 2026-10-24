/* Find Great Architecture: a building opened on an architect's page or a topic page (a style, type, city or idea) opens over
   that page in the wall's own popup, and Previous / Next step through the buildings the page lists, in its order
   (owner, 22 Oct 2026). The popup is the wall itself (/?embed) in a see-through frame, so it looks and works the same.
   The page sets fgaPopup.list (its building ids, in order) and calls fgaPopup.open(id); the frame calls ready(), at(id) and
   closed(id). The address carries #<id> while a building is open, so Back closes it and a shared link opens it again. */
(function () {
  'use strict';
  var me = document.currentScript, root = me ? me.getAttribute('src').replace(/popup\.js.*$/, '') : '/';
  var html = document.documentElement, frame = null, api = null, want = null, pushed = false, back = null, first = '';

  function make() {
    if (frame) return;
    frame = document.createElement('iframe');
    frame.className = 'fga-pop';
    frame.title = 'Building';
    frame.src = root + '?embed=1';
    document.body.appendChild(frame);
  }
  function hide() { html.classList.remove('fga-pop-on', 'fga-pop-live'); }
  function go() {
    var w = want; want = null;
    html.classList.add('fga-pop-live');
    frame.focus();
    api.open(w.id, w.ids);
  }
  var P = window.fgaPopup = {
    list: function () { return []; },
    warm: make,
    open: function (id, fromAddress) {
      make();
      back = document.activeElement;
      first = id;
      want = { id: id, ids: P.list() };
      html.classList.add('fga-pop-on');
      if (!fromAddress && !pushed) { try { history.pushState({ fgaPop: id }, '', '#' + id); pushed = true; } catch (e) { /* fine without */ } }
      if (api) go();
    },
    ready: function (a) { api = a; if (want) go(); },
    at: function (id) { try { history.replaceState({ fgaPop: id }, '', '#' + id); } catch (e) { /* fine without */ } },
    closed: function (id) {
      hide();
      if (pushed) { pushed = false; history.back(); } else { try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* ignore */ } }
      // stepped to another building: the page behind shows its tile, if it has one
      var t = id && id !== first && document.querySelector('[data-id="' + (window.CSS && CSS.escape ? CSS.escape(id) : id) + '"]');
      if (t) { t.scrollIntoView({ block: 'center' }); back = t.querySelector('a, button') || back; }
      if (back && back.focus) back.focus({ preventScroll: true });
    }
  };
  // Back (the phone's gesture too) closes the popup.
  window.addEventListener('popstate', function (e) {
    if (!html.classList.contains('fga-pop-on') || (e.state && e.state.fgaPop)) return;
    pushed = false; want = null;
    if (api) api.hide();
    hide();
  });
  // Pointing at or touching a building starts loading the popup, so it is ready by the time it is opened.
  ['pointerover', 'pointerdown', 'focusin'].forEach(function (k) {
    document.addEventListener(k, function f(e) {
      if (e.target.closest && e.target.closest('.wallpane .t')) { make(); document.removeEventListener(k, f); }
    }, { passive: true });
  });
  // A link with a building in its address (/architects/le-corbusier/#villa-savoye) opens it at once.
  document.addEventListener('DOMContentLoaded', function () {
    var id = '';
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
    if (id && P.list().indexOf(id) > -1) P.open(id, true);
  });
})();
