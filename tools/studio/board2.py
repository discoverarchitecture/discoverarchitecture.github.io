# The sample board, round 3: three layout directions for the Salk Institute board, each a competition-style A1 sheet.
# Every layout has the same seven slots (hero, axon, section, long, site, ph1, ph2) so the hero's pile-to-board
# animation works on any of them. Markup only; the look is in board2.css.
import json, os
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
D = json.load(open(SP + 'salk2.json'))
CR = json.load(open(SP + 'credits.json'))
img = lambda i, cls='': f'<img class="ph {cls}" src="images/salk/{i}.webp" alt="" loading="lazy">'
def layered(svg, L): return svg.replace('</svg>', f'<g class="dlayer">{L}</g></svg>')
CONTENT = {'hero': img(0), 'axon': D['axon'], 'section': layered(D['section'], D['L_svc_sec']), 'long': D['long'],
           'site': layered(D['site'], D['L_axis_site']), 'ph1': img(1), 'ph2': img(5)}
IDEAS = [('Axis to the Pacific', 'A channel of water runs down the plaza toward the ocean.', 'dia_axis'),
         ('Served and servant', 'Service floors run between the laboratory floors.', 'dia_svc'),
         ('Light on the plaza', 'The open travertine plaza takes the sky between the two wings.', 'dia_light')]
STATEMENT = 'Laboratories with service floors between them, around a travertine plaza open to the Pacific.'
CAPS = {'hero': 'The plaza, looking west to the Pacific', 'axon': 'Exploded axonometric · service floors in red', 'section': 'Cross-section through both laboratories',
        'long': 'Long section along the water channel', 'site': 'Site plan', 'ph1': 'South laboratory from the plaza', 'ph2': 'Stair and skylight'}
CREDIT = 'Photos: Jason Taellious CC BY-SA 2.0 · Daniel L. Lu CC BY-SA 4.0 · Beyond My Ken CC BY-SA 4.0, Wikimedia Commons'
LAYOUTS = [('calm', 'Calm grid'), ('drawing', 'Drawing first'), ('editorial', 'Editorial')]

def board(layout='calm', ident='', filled=False, n0=1):
    n = [n0]
    def fig(k, cls=''):
        inner = CONTENT[k] if filled else ''
        num = f'{n[0]:02d}'; n[0] += 1
        return (f'<figure class="fg {cls}"><div class="bslot" data-slot="{k}">{inner}</div>'
                f'<figcaption><b>{num}</b>{CAPS[k]}</figcaption></figure>')
    ideas = ''.join(f'<li><span class="ico">{D[d]}</span><span><b>{i:02d}</b><em>{t}</em>{s}</span></li>' for i, (t, s, d) in enumerate(IDEAS, 1))
    names = ''.join(f'<li><b>{i:02d}</b>{t}</li>' for i, (t, s, d) in enumerate(IDEAS, 1))
    text = f'<div class="btext"><h5>Concept</h5><p class="lead">{STATEMENT}</p><ol class="bideas">{ideas}</ol></div>'
    foot = f'<footer class="bf"><span>{CREDIT}</span><span>Concept mock-up · drawings not to scale</span></footer>'
    if layout == 'calm':
        body = f'''<header class="bh"><div><small>Precedent study · A1</small><h4>Salk Institute</h4><p>Louis Kahn · La Jolla, California · 1965</p></div>
    <ol class="bh-ideas">{names}</ol></header>
  {fig('hero', 'r-hero')}
  <div class="row c5-7">{text}{fig('axon')}</div>
  {fig('long', 'r-long')}
  <div class="row c4-5-3">{fig('site')}{fig('section')}<div class="col">{fig('ph1')}{fig('ph2')}</div></div>
  {foot}'''
    elif layout == 'drawing':
        body = f'''<header class="bh"><div><small>Precedent study · A1</small><h4>Salk Institute</h4><p>Louis Kahn · La Jolla, California · 1965</p></div>
    <ol class="bh-ideas">{names}</ol></header>
  <div class="row c5-7 tall">{text}{fig('axon', 'r-axon')}</div>
  <div class="row c4-4-4 strip">{fig('hero')}{fig('ph1')}{fig('ph2')}</div>
  {fig('long', 'r-long')}
  <div class="row c5-7">{fig('site')}{fig('section')}</div>
  {foot}'''
    else:
        body = f'''{fig('hero', 'r-bleed')}
  <header class="bh"><div><h4>Salk <em>Institute</em></h4><p>Louis Kahn · La Jolla, California · 1965</p></div><div class="bh-r"><p>{STATEMENT}</p></div></header>
  {fig('long', 'r-long')}
  <div class="row c5-7">{text}{fig('axon')}</div>
  <div class="row c4-5-3">{fig('site')}{fig('section')}<div class="col">{fig('ph1')}{fig('ph2')}</div></div>
  {foot}'''
    return f'<div class="bd l-{layout}" {ident}><div class="bdi">{body}</div></div>'
