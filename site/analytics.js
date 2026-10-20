// Visitor counting with GoatCounter (free, no cookies, no consent banner).
// To switch it off, empty the quotes after CODE: nothing is then sent anywhere.
(function () {
  var CODE = 'akshatpagaria';
  if (!CODE) return;
  window.goatcounter = { endpoint: 'https://' + CODE + '.goatcounter.com/count' };
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://gc.zgo.at/count.js';
  document.head.appendChild(s);

  // Things people do without loading a new page (opening a building, the map, finishing a game) are counted as
  // events, so the daily visits number stays visits and nothing else. Other scripts call fgaEvent('map/open', 'Map').
  window.fgaEvent = function (path, title) {
    var tries = 0;
    (function send() {
      if (window.goatcounter && window.goatcounter.count) {
        window.goatcounter.count({ path: path, title: title || path, event: true });
      } else if (tries++ < 20) setTimeout(send, 500);
    })();
  };

  // The wall opens a building (or book) by changing only the #address. It changes it with history.pushState, which
  // fires no event of its own, so the two history calls are wrapped here to look at the address after each one.
  var last = '';
  function countOpened() {
    var id = '';
    try { id = decodeURIComponent((location.hash || '').slice(1)); } catch (e) { return; }
    if (!id) { last = ''; return; }
    if (id === last) return;
    var isBook = id.indexOf('book:') === 0, key = isBook ? id.slice(5) : id;
    var list = (isBook ? window.BOOKS : window.BUILDINGS) || [], item = null;
    for (var i = 0; i < list.length; i++) if (list[i].id === key) { item = list[i]; break; }
    if (!item) return;  // not a building or book (a filter, say)
    last = id;
    window.fgaEvent((isBook ? 'book/' : 'building/') + key, item.name || item.title || key);
  }
  ['pushState', 'replaceState'].forEach(function (name) {
    var original = history[name];
    if (typeof original !== 'function') return;
    history[name] = function () {
      var result = original.apply(this, arguments);
      setTimeout(countOpened, 0);
      return result;
    };
  });
  window.addEventListener('hashchange', countOpened);
  window.addEventListener('popstate', countOpened);
  window.addEventListener('load', countOpened);
})();
