# FGA Studio waitlist page, round 3: the sample board remade as a competition-style A1 sheet in three layouts
# (board2.py, board2.css, drawings from salk2.py), inside the Pin-up party page. HERO=calm|drawing|editorial picks the
# layout shown in the hero (default calm); the style picker switches between all three.
import json, html as H
import os, sys
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, SP)
import board2 as B
D = B.D; CR = B.CR; img = B.img; layered = B.layered; CONTENT = B.CONTENT
HERO = os.environ.get('HERO', 'calm')
board = lambda ident='', filled=False, layout=None: B.board(layout or HERO, ident, filled)

PILE = [('hero', 2, 4, 60, 28, -5, 'IMG_0412.jpg'), ('axon', 50, 20, 46, 30, 6, 'axo_exploded.pdf'), ('section', 6, 36, 52, 20, -3, 'section_BB.dwg'),
        ('site', 42, 54, 44, 28, 4, 'site_plan.pdf'), ('ph1', 3, 60, 38, 22, -8, 'facade.jpg'), ('ph2', 60, 2, 26, 30, 7, 'stair.jpg'),
        ('long', 10, 84, 56, 13, -2, 'long_section.pdf')]
flyers = ''.join(f'<div class="fly" data-fly="{k}" style="--px:{x}%;--py:{y}%;--pw:{w}%;--ph:{h}%;--pr:{r}deg;--d:{i * 70}ms">{CONTENT[k]}<span class="tag">{lab}</span></div>'
                 for i, (k, x, y, w, h, r, lab) in enumerate(PILE))
extras = ('<div class="note" style="--px:62%;--py:60%;--pr:6deg">axis to the sea?<br>served/servant!!<br>light ✶</div>'
          f'<div class="fly ref" style="--px:68%;--py:80%;--pw:28%;--ph:17%;--pr:-5deg">{img(7)}<span class="tag">refs.jpg</span></div>')
deck = (f'<div class="deck"><div class="sl s3 white">{D["long"]}</div><div class="sl s2 white">{D["axon"]}</div>'
        f'<div class="sl s1">{img(0)}<b>Salk Institute</b></div><span class="dk">Deck · PPTX</span></div>')
PHF = {'calm': 'grayscale(1) contrast(1.04)', 'drawing': 'grayscale(1) contrast(1.02)', 'editorial': 'none'}[HERO]
STAGE = f'''<div class="stage" id="stage" style="--stage-phf: {PHF}" aria-label="Concept mock-up: a pile of drawings and photos turning into a finished jury board and deck">
  <span class="mock">Concept mock-up</span><span class="state"><i class="s-pile">Your files</i><i class="s-built">Your jury board</i></span>
  {board('id="bd0"')}{flyers}{extras}{deck}</div>'''

STEPS = [
    ('Upload', 'Plans, sections, elevations, renders, sketches, model photos and references. Messy is fine.',
     '<div class="v-up">' + ''.join(f'<span><i class="ft">{t}</i>{n}</span>' for t, n in [('PDF', 'site_plan'), ('DWG', 'section_BB'), ('PDF', 'axo_exploded'), ('JPG', 'IMG_0412'), ('JPG', 'stair')]) + '</div>'),
    ('Your ideas', 'Write a short brief and name the 2–4 ideas the board must explain.',
     '<div class="v-ideas"><span class="brief">“Labs around a plaza open to the ocean…”</span><i>Axis to the Pacific</i><i>Served and servant</i><i>Light</i><i class="add">+ idea</i></div>'),
    ('AI board plan', 'It plans the story: which idea goes first and which drawing proves it. You approve or change it.',
     '<ol class="v-plan"><li><b>Axis</b> hero photo + site plan</li><li><b>Served and servant</b> axonometric + section</li><li><b>Light</b> section + plaza photo</li></ol><span class="ok">Approve plan ✓</span>'),
    ('Diagrams & touch-ups', 'Click on your plan or section and it draws clean, editable lines, arrows and fills. Photos get ready for print.',
     f'<div class="v-dia">{layered(D["site"], D["L_axis_site"])}</div>'),
    ('Export', 'An editable PowerPoint (one A1 board per slide) and a print-ready PDF.',
     '<div class="v-exp"><span class="fx ppt">PPTX</span><span class="fx pdf">PDF</span><small>PowerPoint · Keynote · Google Slides · Canva</small></div>'),
]
steps = ''.join(f'<li class="step rv"><span class="sn">{i:02d}</span><h3>{t}</h3><p>{p}</p><div class="sv">{v}</div></li>' for i, (t, p, v) in enumerate(STEPS, 1))

STUDIO = f'''<div class="dstudio" id="dstudio">
  <div class="ds-side">
    <label class="ds-label">Idea</label>
    <div class="ds-input"><span class="typed" id="typed"></span><span class="caret"></span></div>
    <div class="ds-chips" id="dsChips"><button type="button" data-k="axis" class="on">Axis to the Pacific</button><button type="button" data-k="svc">Served and servant</button><button type="button" data-k="light">Light</button></div>
    <ol class="ds-log" id="dsLog"></ol>
    <p class="ds-note">Clean lines, arrows and fills you can still move, recolour and delete. Not a filter.</p>
  </div>
  <div class="ds-canvas">
    <div class="ds-view plan" id="dsPlan"><span class="ds-cap">Site plan · yours</span>{D['site'].replace(' preserveAspectRatio="xMidYMid slice"', '')}</div>
    <div class="ds-view sec" id="dsSec"><span class="ds-cap">Section · yours</span>{D['section'].replace(' preserveAspectRatio="xMidYMid slice"', '')}</div>
    <span class="cursor" id="cursor"><svg viewBox="0 0 24 24"><path d="M4 2l16 9-7 2-3 7z"/></svg></span>
  </div>
</div>'''
DIA = json.dumps({
    'axis': {'w': 'axis to the Pacific', 'plan': D['L_axis_site'], 'sec': '', 'pts': [['plan', 828, 350], ['plan', 310, 350]], 'log': ['Click the end of the water channel', 'Click the open end of the plaza', 'Draw the axis out to the Pacific']},
    'svc': {'w': 'served and servant', 'plan': D['L_svc_site'], 'sec': D['L_svc_sec'], 'pts': [['sec', 200, 286], ['sec', 760, 198]], 'log': ['Click a service floor', 'Click the other wing', 'Fill the servant floors on plan and section']},
    'light': {'w': 'light', 'plan': D['L_light_site'], 'sec': D['L_light_sec'], 'pts': [['sec', 480, 300], ['plan', 580, 350]], 'log': ['Click the plaza in section', 'Click it on the plan', 'Show the sky falling between the wings']}})

TOUCH = f'''<div class="touch" id="touch">
  <div class="tc-frame" id="tcFrame"><div class="tc-ext"><img id="tcImg" src="images/salk/0.webp" alt="The Salk Institute plaza"></div><canvas id="tcPix" width="640" height="374"></canvas><span class="tc-crop"></span><span class="tc-badge" id="tcBadge">Original</span></div>
  <div class="tc-chips" id="tcChips"><button type="button" data-t="up" class="on">Upscale for print</button><button type="button" data-t="crop">Smart crop</button><button type="button" data-t="ext">Extend the edge</button><button type="button" data-t="col">Colour-match</button></div>
  <p class="tc-note">The building itself is never changed.</p>
</div>'''

STYLES = B.LAYOUTS
STYLER = ('<div class="styler" id="styler"><div class="st-btns">' + ''.join(f'<button type="button" data-s="{k}"{" class=on" if k == HERO else ""}>{n}</button>' for k, n in STYLES)
          + '</div><div class="st-board">' + ''.join(board(f'data-layout="{k}"' + ('' if k == HERO else ' hidden'), True, k) for k, n in STYLES) + '</div></div>')
FORMATS = ''.join(f'<li class="fm {c}"><span class="fr"></span><b>{t}</b><small>{s}</small>{"<em>Later</em>" if later else ""}</li>' for c, t, s, later in [
    ('a1', 'A1 board', '594 × 841 mm', 0), ('a0', 'A0 board', '841 × 1189 mm', 0), ('arch', '24 × 36 in', 'ARCH D', 0), ('ppt', 'Slide deck', '16:9 PowerPoint', 0), ('sq', 'Square', 'for Instagram', 1), ('web', 'Web deck', 'a link to share', 1)])
FAQ = [('How do I lay out an architecture presentation board?', 'Decide the two to four ideas the board must explain, then let one strong image lead and give every other drawing a job: a plan, a section or a diagram that proves one idea. Keep a clear reading order, plans and sections at stated scales, short captions and plenty of white space. FGA Studio plans this story with you and lays it out on a grid you can still change.'),
       ('What size is an architecture presentation board?', 'Usually A1 (594 × 841 mm) in the UK, Europe, India and Australia, and 24 × 36 in (ARCH D) in the US; some schools ask for A0 (841 × 1189 mm) at final reviews. Check your studio brief. FGA Studio makes all three and a 16:9 slide deck.'),
       ('Which formats can I make?', 'An A1, A0 or 24 × 36 in board, or a slide deck. Square posts and a web deck come later. You can switch before you export.'),
       ('How much does it cost?', 'You buy a one-time pack of prepaid credits and use them to export your boards and decks; there is no subscription and nothing renews. [[FILL: One credit exports one board or one deck.]] You see a free, watermarked preview before you pay anything. Packs and prices are on the <a href="/pricing/">pricing page</a>.'),
       ('Does it work with PowerPoint and Canva?', 'Yes. You get an editable PowerPoint file: a whole A1 board sits on one slide, and it opens in PowerPoint, Keynote, Google Slides and Canva. You also get a print-ready PDF.'),
       ('Is it allowed for my coursework?', 'It lays out your drawings and draws the ideas you point to; the design and the thinking are yours. Words are written only from your own brief. Check your school’s rules on AI tools, and say you used it if they ask.'),
       ('Do my drawings stay private?', 'Yes. Your files are made into the board in your own browser, not on our servers: they never leave your device. See the <a href="/privacy/">Privacy Policy</a>.')]
faq = ''.join(f'<details class="fq"><summary>{q}<i></i></summary><p>{a}</p></details>' for q, a in FAQ)
ROLE = '<option value="" disabled selected>I am a…</option><option value="student">Student</option><option value="teacher">Teacher</option><option value="architect">Practising architect</option>'
WHEN = '<div class="seg">' + ''.join(f'<label><input type="radio" name="when" value="{v}"><span>{t}</span></label>' for v, t in [('this-month', 'This month'), ('1-3-months', '1–3 months'), ('later', 'Later'), ('other', 'Other')]) + '</div>'
QUICK = f'''<form class="qf" id="qf" action="#" method="post">
  <div class="qf-row"><input type="email" name="email" required placeholder="Your email" autocomplete="email" aria-label="Your email"><select name="role" required aria-label="I am a">{ROLE}</select><button class="cta" type="submit">Get early access</button></div>
  <input type="hidden" name="ref" value=""><input type="hidden" name="b" value="">
  <p class="qf-fine">Launching November 2026 · early access and a launch discount · we’ll only email you about FGA Studio · <a href="/privacy/">Privacy</a></p>
  <div class="qf-more"><b>You’re on the list ✓</b><span>Two optional questions, so we build for your next jury:</span>
    <label class="f"><span>What are you presenting next?</span><input type="text" name="next" placeholder="e.g. a library by a river, final review"></label>
    <fieldset class="f"><legend>When is your next jury?</legend>{WHEN}</fieldset><button class="cta" type="button" onclick="this.closest('.qf').classList.add('done')">Send</button></div>
  <p class="qf-thanks">Thanks. See you before your jury.</p>
</form>'''
FORM = f'''<form class="wl" id="join" action="#" method="post" onsubmit="event.preventDefault(); this.classList.add('sent'); this.querySelector('[type=submit]').disabled = true">
  <label class="f"><span>Email</span><input type="email" name="email" required placeholder="you@school.edu" autocomplete="email"></label>
  <fieldset class="f"><legend>I am a</legend><div class="seg"><label><input type="radio" name="role" value="student" required><span>Student</span></label><label><input type="radio" name="role" value="teacher"><span>Teacher</span></label><label><input type="radio" name="role" value="architect"><span>Practising architect</span></label></div></fieldset>
  <label class="f"><span>What are you presenting next? <em>optional</em></span><input type="text" name="next" placeholder="e.g. a library by a river, final review"></label>
  <fieldset class="f"><legend>When is your next jury? <em>optional</em></legend>{WHEN}</fieldset>
  <input type="hidden" name="ref" value=""><input type="hidden" name="b" value="">
  <button class="cta big" type="submit"><span class="j-go">Join the waitlist</span><span class="j-done">✓ You’re on the list</span></button>
  <p class="consent">We’ll email you when FGA Studio opens, and about your early-access discount. Nothing else. <a href="/privacy/">Privacy</a></p>
  <p class="thanks">See you before your jury.</p>
</form>'''
SKIP = '''<section class="sec skip"><p class="kick">Who it’s for</p><h2>Your hours belong<br>to the design.</h2>
  <p class="sub">For students who would rather be designing than fighting software. You design the building; FGA Studio makes the presentation.</p>
  <ul class="skips"><li><s>Building the InDesign grid</s></li><li><s>Cleaning renders in Photoshop</s></li><li><s>Redrawing diagrams in Illustrator</s></li><li><s>Re-exporting at 4 a.m.</s></li><li class="yes">Designing</li></ul></section>'''

def page(d):
    headline = {'A': 'Design the building.<br><span class="hl">Skip the</span> <span class="hl2">all-nighter.</span>',
                'B': 'You design.<br><span class="lit">It presents.</span>'}[d]
    eyebrow = 'Architecture presentation boards from your own drawings'
    lede = 'Upload your plans, sections, renders and sketches and name the ideas your board must explain. Get a professional-grade presentation board for your jury or crit, and a deck you can still edit, without the nights in InDesign and Photoshop.'
    words = ['pin-up', 'jury board', 'crit', 'jury sheets', 'final review', 'láminas', 'pranchas'] * 4
    marquee = '<div class="marquee" aria-hidden="true"><div>' + ''.join(f'<span>{w}</span><i>✦</i>' for w in words) + '</div></div>'
    css = open(SP + f'style_{d}.css').read() + open(SP + 'style_common.css').read() + open(SP + 'draw2.css').read() + open(SP + 'board2.css').read()
    fonts = 'family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Inter+Tight:wght@500;600;700;800&family=Inter:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@500&family=Caveat:wght@600'
    credits = ' · '.join(f'<a href="{H.escape(c["source"])}">{H.escape(c["credit"])}</a>, {c["license"]}' for c in [CR[i] for i in (0, 1, 5, 7)])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FGA Studio</title><meta name="description" content="You design, FGA Studio presents: professional-grade jury boards and decks from your own drawings. Launching November 2027.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body class="dir-{d}"><svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="rough"><feTurbulence type="fractalNoise" baseFrequency=".04" numOctaves="2"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter></svg>
<header class="nav"><a class="brand" href="#"><span class="logo">{'<i>✦</i>' if d == 'A' else '<i></i>'}FGA Studio</span><span class="by">by Find Great Architecture</span></a>
  <nav><a href="#how">How it works</a><a href="#diagrams">Diagrams</a><a href="#price">Price</a><a href="#faq">FAQ</a></nav><a class="cta sm" href="#top">Get early access</a></header>
<main id="top">
<section class="hero">
  <div class="hero-copy">
    <span class="pill">{'<i>✦</i> ' if d == 'A' else '<i class="dot"></i>'}{eyebrow}</span>
    <h1>{headline}</h1>
    <p class="lede">{lede}</p>
    {QUICK}
  </div>
  <div class="hero-stage">{STAGE}</div>
</section>
{marquee}
{SKIP}
<section class="sec" id="how"><p class="kick">How it works</p><h2>Five steps from<br>pile to pin-up</h2><ol class="steps">{steps}</ol></section>
<section class="sec feat" id="diagrams"><div class="fhead"><p class="kick">The diagram studio</p><h2>You name the idea.<br><em>It draws it.</em></h2><p class="sub">Say what the board must explain, click where it happens on your plan or section, and get clean lines, arrows and fills you can still edit.</p></div>{STUDIO}</section>
<section class="sec feat two"><div><p class="kick">Image touch-ups</p><h2>Ready for print,<br>not redrawn</h2><p class="sub">Upscale for an A1 print, crop to the slot, extend a photo’s edge to fit, match colours across the board.</p></div>{TOUCH}</section>
<section class="sec feat"><div class="fhead"><p class="kick">Your look</p><h2>Pick a style.<br>Keep your work.</h2><p class="sub">The same drawings and ideas, laid out three ways. Change your mind any time before you export.</p></div>{STYLER}</section>
<section class="sec"><p class="kick">Formats</p><h2>Board, deck,<br>and more later</h2><ul class="formats">{FORMATS}</ul><p class="sub fsub">Every board exports as an editable PowerPoint (a whole A1 board fits on one slide) and a print-ready PDF.</p></section>
<section class="sec words"><p class="kick">Words</p><h2>Written from your brief. <span class="mute">Never made up.</span></h2><p class="sub">Your concept statement, story and captions come only from what you wrote. No invented facts, no made-up numbers: if it isn’t in your brief, it isn’t on your board.</p></section>
<section class="sec price" id="price"><div><p class="kick">Price</p><h2>Pay per board.<br>No subscription.</h2><p class="sub">Buy a one-time pack of prepaid credits and spend them when you export a board or deck. Nothing renews and there is nothing to cancel.</p></div>
  <div class="pcards"><div class="pc"><b>Free</b><span>Watermarked preview of your whole board</span></div><div class="pc hot"><b>Credits</b><span>Pay only when you export. [[FILL: 1 credit = one exported board or deck.]] Packs from [[FILL: US$ price]]. <a href="/pricing/">See pricing</a></span></div><div class="pc"><b>Your files</b><span>Editable PPTX and print-ready PDF, yours to keep</span></div></div></section>
<section class="sec honest"><p class="kick">Coursework</p><h2>It lays out and draws your ideas.<br><span class="mute">The thinking stays yours.</span></h2></section>
<section class="sec join" id="waitlist"><div><p class="kick">Waitlist</p><h2>Launching November 2026.</h2><p class="sub">Join for early access and a launch discount.</p></div>{FORM}</section>
<section class="sec" id="faq"><p class="kick">FAQ</p><h2>Questions</h2><div class="faq">{faq}</div></section>
</main>
<footer class="foot"><span>FGA Studio · by <a href="https://findgreatarchitecture.com/">Find Great Architecture</a></span>
<span>Sample board: the Salk Institute (Louis Kahn). Drawings are our own diagrams, not to scale. Photos via Wikimedia Commons: {credits}</span><span class="legal-links"><a href="/pricing/">Pricing</a> · <a href="/terms/">Terms</a> · <a href="/privacy/">Privacy</a> · <a href="/refunds/">Refunds</a> · <a href="/contact/">Contact</a></span><span>Find Great Architecture · run by Akshat Pagaria · India</span></footer>
<script>const DIA = {DIA}; const STYLE_KEYS = {json.dumps([k for k, n in STYLES])};
{open(SP + 'common.js').read()}</script>
</body></html>'''
import os
os.makedirs(SP + 'web', exist_ok=True)
for d in ('A',):
    open(SP + f'web/{d}{"" if HERO == "calm" else "_" + HERO}.html', 'w').write(page(d))
print('ok')
