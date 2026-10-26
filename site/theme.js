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
