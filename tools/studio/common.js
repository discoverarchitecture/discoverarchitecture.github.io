const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const $ = (s, el = document) => el.querySelector(s);
// hidden waitlist fields: where they came from (?ref=ig) and which building (?b=)
const qs = new URLSearchParams(location.search);
document.querySelectorAll('input[name=ref]').forEach(i => i.value = qs.get('ref') || '');
document.querySelectorAll('input[name=b]').forEach(i => i.value = qs.get('b') || '');

// 1. the pile of files that becomes a board and a deck
const stage = $('#stage');
function place() {
  const r = stage.getBoundingClientRect();
  stage.querySelectorAll('.fly[data-fly]').forEach(f => {
    const s = stage.querySelector(`[data-slot="${f.dataset.fly}"]`).getBoundingClientRect();
    f.style.setProperty('--bx', (s.left - r.left) + 'px'); f.style.setProperty('--by', (s.top - r.top) + 'px');
    f.style.setProperty('--bw', s.width + 'px'); f.style.setProperty('--bh', s.height + 'px');
  });
}
place(); addEventListener('resize', place); document.fonts && document.fonts.ready.then(place);
async function loop() {
  if (reduce || qs.has('built')) { stage.classList.add('built', 'drawn', 'decked'); return; }
  if (qs.has('pile')) return;
  for (;;) {
    await sleep(1800); place(); stage.classList.add('built');
    await sleep(1500); stage.classList.add('drawn');
    await sleep(1600); stage.classList.add('decked');
    await sleep(4200); stage.classList.remove('decked', 'drawn'); await sleep(300); stage.classList.remove('built');
  }
}
loop();

// 2. the diagram studio: type the idea, click on the drawing, the lines draw
const studio = $('#dstudio'), typed = $('#typed'), cursor = $('#cursor');
const layer = (view, html) => { const svg = $(view + ' svg', studio); let g = $('.dlayer', svg); if (!g) { g = document.createElementNS('http://www.w3.org/2000/svg', 'g'); g.setAttribute('class', 'dlayer'); svg.appendChild(g); } g.innerHTML = html; return g; };
let run = 0, auto = true;
async function playIdea(k) {
  const me = ++run, d = DIA[k], word = d.w;
  studio.querySelectorAll('.ds-chips button').forEach(b => b.classList.toggle('on', b.dataset.k === k));
  const gp = layer('#dsPlan', d.plan), gs = layer('#dsSec', d.sec);
  [gp, gs].forEach(g => g.querySelectorAll('*').forEach(e => e.classList.add('hide')));
  const log = $('#dsLog'); log.innerHTML = d.log.map(t => `<li>${t}</li>`).join('');
  typed.textContent = '';
  for (const ch of word) { if (me !== run) return; typed.textContent += ch; await sleep(reduce ? 0 : 70); }
  const box = studio.querySelector('.ds-canvas').getBoundingClientRect();
  for (let i = 0; i < d.pts.length; i++) {
    const [v, x, y] = d.pts[i], svg = $(v === 'plan' ? '#dsPlan svg' : '#dsSec svg'), vb = svg.getBoundingClientRect(), v0 = svg.viewBox.baseVal;
    cursor.style.transform = `translate(${vb.left - box.left + (x - v0.x) / v0.width * vb.width}px, ${vb.top - box.top + (y - v0.y) / v0.height * vb.height}px)`;
    await sleep(reduce ? 0 : 650); if (me !== run) return;
    cursor.classList.add('click'); setTimeout(() => cursor.classList.remove('click'), 250);
    log.children[Math.min(i, log.children.length - 1)].classList.add('done');
    const g = v === 'plan' ? gp : gs;
    // show the dot nearest this click, and the lines leaving it
    g.querySelectorAll('.hide').forEach(e => {
      const cx = +(e.getAttribute('cx') || 0), cy = +(e.getAttribute('cy') || 0), dd = e.getAttribute('d') || '';
      const m = dd.match(/^M\s*([\d.]+)\s+([\d.]+)/);
      const near = (cx && Math.hypot(cx - x, cy - y) < 30) || (m && Math.hypot(+m[1] - x, +m[2] - y) < 30);
      if (near || i === d.pts.length - 1) e.classList.remove('hide');
    });
  }
  log.lastElementChild.classList.add('done');
  [gp, gs].forEach(g => g.querySelectorAll('.hide').forEach(e => e.classList.remove('hide')));
}
studio.querySelector('.ds-chips').addEventListener('click', e => { const b = e.target.closest('button'); if (b) { auto = false; playIdea(b.dataset.k); } });
async function studioLoop() { const ks = ['axis', 'svc', 'light']; let i = 0; while (auto) { await playIdea(ks[i++ % 3]); await sleep(3200); } }
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); if (e.target === studio && !studio.dataset.go) { studio.dataset.go = 1; studioLoop(); } } }), { threshold: .2 });
document.querySelectorAll('.rv, .sec, #dstudio').forEach(el => io.observe(el));
if (qs.has('studio')) { studio.dataset.go = 1; auto = false; playIdea(qs.get('studio')); }

// 3. the style picker
const styler = $('#styler'); let sAuto = !qs.has('style');
function setStyle(s) { styler.querySelectorAll('.st-board .bd').forEach(b => b.hidden = b.dataset.layout !== s); styler.querySelectorAll('.st-btns button').forEach(b => b.classList.toggle('on', b.dataset.s === s)); }
styler.addEventListener('click', e => { const b = e.target.closest('button'); if (b) { sAuto = false; setStyle(b.dataset.s); } });
if (qs.has('style')) setStyle(qs.get('style'));
(async () => { const ss = STYLE_KEYS; let i = 1; while (!reduce) { await sleep(3200); if (!sAuto) break; setStyle(ss[i++ % 3]); } })();

// 4. image touch-ups
const touch = $('#touch'), frame = $('#tcFrame'), badge = $('#tcBadge'), pix = $('#tcPix');
(() => { // a low-resolution copy of the photo, to show what upscaling fixes
  const img = $('#tcImg'), draw = () => { const c = pix.getContext('2d'), t = document.createElement('canvas'); t.width = 64; t.height = 37; t.getContext('2d').drawImage(img, 0, 0, 64, 37); c.imageSmoothingEnabled = false; c.drawImage(t, 0, 0, pix.width, pix.height); };
  if (img.complete && img.naturalWidth) draw(); else img.addEventListener('load', draw);
})();
const TC = { up: 'Upscaled for A1 print', crop: 'Cropped to the board’s slot', ext: 'Sky and plaza extended', col: 'Colours matched to the board' };
let tAuto = true;
async function setTouch(t) {
  touch.querySelectorAll('.tc-chips button').forEach(b => b.classList.toggle('on', b.dataset.t === t));
  frame.className = 'tc-frame t-' + t; badge.textContent = 'Before';
  await sleep(reduce ? 0 : 900); frame.classList.add('after'); badge.textContent = TC[t];
}
touch.addEventListener('click', e => { const b = e.target.closest('button'); if (b) { tAuto = false; setTouch(b.dataset.t); } });
(async () => { const ts = ['up', 'crop', 'ext', 'col']; let i = 0; setTouch(qs.get('touch') || 'up'); if (qs.has('touch')) return; while (!reduce) { await sleep(3400); if (!tAuto) break; setTouch(ts[++i % 4]); } })();

// 5. the first-screen sign-up: email and role, then two optional questions
const qf = $('#qf');
qf.addEventListener('submit', e => { e.preventDefault(); qf.classList.add('sent'); const t = qf.querySelector('.qf-more input'); t && t.focus({ preventScroll: true }); });
if (qs.has('sent')) qf.classList.add('sent');
