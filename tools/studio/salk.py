# Salk Institute drawings for the FGA Studio sample board: schematic, not to scale, drawn from the photos and the site's
# own description ("laboratories with service floors between them, around a travertine plaza open to the Pacific").
# Classes: k ink line, k2 thin, g1 g2 g3 greys, red accent (ra stroke, rf fill), sea, hatch fills, ppl entourage.
import json, math
D = {}
DEFS = ('<defs><pattern id="hx" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" class="hxl"/></pattern>'
        '<pattern id="hr" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" class="hrl"/></pattern>'
        '<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" class="arh"/></marker></defs>')
def person(x, y, h=14, flip=False):
    s = h / 14; d = -1 if flip else 1
    return (f'<g class="ppl" transform="translate({x} {y}) scale({s * d} {s})"><circle cx="0" cy="-12.5" r="1.7"/>'
            '<path d="M-1.6 -10.5 h3.2 l.6 5.5 h-1 l-.4 5 h-1.6 l-.4 -5 h-1 z"/></g>')
def tree(x, y, r):
    return f'<circle class="tr" cx="{x}" cy="{y}" r="{r}"/><circle class="tr2" cx="{x - r * .25}" cy="{y - r * .25}" r="{r * .55}"/>'

# ---------- site plan, north up, ocean to the west (left) ----------
W, H = 600, 400
sea = ''.join(f'<path class="k2 wv" d="M{x0} {y} q6 -4 12 0 t12 0"/>' for x0, y in [(16, 60), (40, 100), (14, 150), (46, 190), (20, 240), (38, 290), (16, 330)])
contours = ''.join(f'<path class="k2 ct" d="M{110 + i * 9} 20 C{100 + i * 9} 120 {124 + i * 9} 210 {104 + i * 9} 300 S{118 + i * 9} 380 {112 + i * 9} 400"/>' for i in range(5))
travert = ''.join(f'<path class="k2 jt" d="M{x} 172 V228"/>' for x in range(212, 470, 12))
towers_n = ''.join(f'<rect class="bk" x="{x}" y="164" width="16" height="16" transform="rotate(45 {x + 8} 172)"/>' for x in range(222, 460, 34))
towers_s = ''.join(f'<rect class="bk" x="{x}" y="220" width="16" height="16" transform="rotate(45 {x + 8} 228)"/>' for x in range(222, 460, 34))
grove = ''.join(tree(x, y, 7) for x in range(494, 580, 16) for y in range(150, 260, 16))
D['site'] = f'''<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">{DEFS}
<rect class="pap" width="{W}" height="{H}"/><rect class="sea" width="100" height="{H}"/>{sea}
<path class="land" d="M100 0 H600 V400 H100 C112 320 92 240 108 160 S96 40 100 0 Z"/>{contours}
<rect class="plz" x="200" y="170" width="276" height="60"/>{travert}
<rect class="bk" x="200" y="112" width="276" height="50"/><rect class="bk" x="200" y="238" width="276" height="50"/>
{towers_n}{towers_s}
<path class="ra ch" d="M470 200 H214"/><rect class="rf" x="206" y="194" width="10" height="12"/>
{grove}
<path class="k2" d="M200 170 L160 160 M200 230 L160 240"/>
<g class="nrth"><circle cx="560" cy="44" r="16" class="k2" fill="none"/><path d="M560 28 L566 50 L560 46 L554 50 Z" class="nfill"/><text x="560" y="78" text-anchor="middle" class="lb">N</text></g>
<text x="50" y="384" text-anchor="middle" class="lb">PACIFIC</text>
<path class="k" d="M480 372 h80 M480 368 v8 M520 368 v8 M560 368 v8"/><text x="480" y="362" class="lb">NOT TO SCALE</text>
</svg>'''

# ---------- cross-section through both wings and the plaza ----------
def wing(x0, x1, tower_side):
    out = []
    levels = [('lab', 228, 262), ('svc', 208, 228), ('lab', 170, 208), ('svc', 150, 170), ('lab', 112, 150), ('svc', 94, 112)]
    for kind, y0, y1 in levels:
        if kind == 'svc':
            out.append(f'<rect class="svc" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>')
            out.append(''.join(f'<path class="k2" d="M{x} {y0} L{x + 9} {y1} L{x + 18} {y0}"/>' for x in range(x0, x1 - 17, 18)))
        else:
            out.append(f'<rect class="lab" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>')
        out.append(f'<path class="k slab" d="M{x0} {y1} H{x1}"/>')
    out.append(f'<rect class="k" x="{x0}" y="94" width="{x1 - x0}" height="168" fill="none"/>')
    tx0, tx1 = (x1, x1 + 34) if tower_side == 'r' else (x0 - 34, x0)
    out.append(f'<rect class="twr" x="{tx0}" y="120" width="34" height="108"/>')
    for yy in (132, 172):
        out.append(f'<rect class="teak" x="{tx0 + 6}" y="{yy}" width="22" height="26"/>')
    out.append(f'<path class="k" d="M{tx0} 120 H{tx1} V228 M{tx0} 120 V228"/>')
    return ''.join(out)
D['section'] = f'''<svg viewBox="0 0 800 300" preserveAspectRatio="xMidYMid slice">{DEFS}
<rect class="pap" width="800" height="300"/><rect class="sky" width="800" height="228"/>
<path class="gnd" d="M0 228 H70 V270 H260 V228 H540 V270 H730 V228 H800 V300 H0 Z"/>
{wing(70, 226, 'r')}{wing(574, 730, 'l')}
<rect class="plzs" x="260" y="226" width="280" height="4"/><rect class="rf" x="396" y="226" width="8" height="5"/>
<path class="k" d="M0 228 H70 M730 228 H800 M260 228 H540"/>
{person(300, 226)}{person(318, 226, 13, True)}{person(452, 226)}{person(470, 226, 13)}{person(505, 226, 14, True)}{person(120, 206, 12)}{person(640, 168, 12, True)}{person(160, 262, 12)}

<text x="148" y="86" text-anchor="middle" class="lb">SOUTH LABORATORIES</text><text x="652" y="86" text-anchor="middle" class="lb">NORTH LABORATORIES</text>
<text x="400" y="250" text-anchor="middle" class="lb">TRAVERTINE PLAZA</text>
</svg>'''

# ---------- long section along the water axis, to the Pacific ----------
D['long'] = f'''<svg viewBox="0 0 800 260" preserveAspectRatio="xMidYMid slice">{DEFS}
<rect class="pap" width="800" height="260"/><rect class="sky" width="800" height="200"/>
<path class="sea2" d="M0 200 H150 V260 H0 Z"/><path class="k2" d="M0 150 H800" stroke-dasharray="2 6"/>
<path class="gnd" d="M150 200 C180 196 196 170 214 166 H250 V172 H800 V260 H150 Z"/>
<rect class="elev" x="290" y="62" width="490" height="110"/>
{''.join(f'<rect class="twr2" x="{x}" y="96" width="22" height="76"/>' for x in range(304, 770, 38))}
<path class="k" d="M250 172 H800 M250 166 V172 M290 62 V172 M290 62 H780 V172"/>
<path class="ra" d="M262 169 H760"/><rect class="rf" x="254" y="166" width="12" height="6"/>
{person(700, 170, 15, True)}{person(560, 170, 14)}{person(420, 170, 13, True)}
<text x="70" y="228" text-anchor="middle" class="lb">PACIFIC</text><text x="520" y="190" text-anchor="middle" class="lb">PLAZA AND WATER CHANNEL</text>
</svg>'''

# ---------- exploded axonometric ----------
S = 7.2
def P(x, y, z):
    return (240 + (x + y) * .866 * S, 250 + (x - y) * .5 * S - z * S)
def poly(cls, pts): return '<polygon class="%s" points="%s"/>' % (cls, ' '.join('%.1f,%.1f' % P(*p) for p in pts))
def box(x0, y0, x1, y1, z0, z1, top='bt', s='bs', e='be'):
    return (poly(s, [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]) + poly(e, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)])
            + poly(top, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]))
def line(cls, a, b, extra=''):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{extra}/>'
def lab(x, y, z, t, anchor='start', dx=0, dy=0):
    a, b = P(x, y, z)
    return f'<text class="lb" x="{a + dx:.1f}" y="{b + dy:.1f}" text-anchor="{anchor}">{t}</text>'
parts = []
# the ocean and the cliff, to the west (x < 0)
parts.append(poly('sea', [(-22, -16, -3), (-8, -16, -3), (-8, 38, -3), (-22, 38, -3)]))
parts.append(poly('land', [(-8, -16, 0), (66, -16, 0), (66, 38, 0), (-8, 38, 0)]))
# north wing, exploded upwards (far side)
gap = 5
lv = [('bt', 0, 3), ('svc3', 3, 4.6), ('bt', 4.6, 7.6), ('svc3', 7.6, 9.2)]
for i, (cls, z0, z1) in enumerate(lv):
    o = i * gap
    parts.append(box(0, 24, 60, 34, z0 + o, z1 + o, top=('svct' if cls == 'svc3' else 'bt')))
for x in range(4, 58, 7):
    parts.append(box(x, 21, x + 3.4, 23.6, 0, 6, top='bt'))
# the plaza, with the water channel on its axis
parts.append(poly('plz3', [(0, 2, .02), (60, 2, .02), (60, 20, .02), (0, 20, .02)]))
for x in range(3, 60, 3):
    parts.append(line('jt3', (x, 2, .03), (x, 20, .03)))
parts.append(line('ra3', (58, 11, .05), (-1, 11, .05)))
parts.append(line('ra3 dash', (-1, 11, .05), (-26, 11, -3), ' marker-end="url(#ar)"'))
# south wing: just its outline on the ground (near side), so the plaza shows
parts.append(poly('gh', [(0, -12, 0), (60, -12, 0), (60, -2, 0), (0, -2, 0)]))
for x in range(4, 58, 7):
    parts.append(poly('gh', [(x, -1.6, 0), (x + 3.4, -1.6, 0), (x + 3.4, 1, 0), (x, 1, 0)]))
# labels with leaders
lbls = [((60, 34, 3 + 0), 'Laboratory', 26, 4), ((60, 34, 4.6 + gap * 1 - .8), 'Service floor', 26, 4), ((60, 34, 7.6 + gap * 2), 'Laboratory', 26, 4), ((60, 34, 9.2 + gap * 3 - .8), 'Service floor', 26, 4),
        ((18, 22, 6), 'Study towers', -30, -70), ((26, 4, 0), 'Travertine plaza', -40, 50), ((-14, 11, -2.6), 'To the Pacific', -6, 26), ((40, -7, 0), 'South wing, footprint', 0, 30)]
for (x, y, z), t, dx, dy in lbls:
    a, b = P(x, y, z)
    parts.append(f'<path class="ldr" d="M{a:.1f} {b:.1f} l{dx:.1f} {dy:.1f}"/>')
    parts.append(f'<text class="lb ax" x="{a + dx + (4 if dx >= 0 else -4):.1f}" y="{b + dy + (4 if dy >= 0 else -4):.1f}" text-anchor="{"start" if dx >= 0 else "end"}">{t.upper()}</text>')
allp = []
import re
for p in parts:
    allp += [(float(a), float(b)) for a, b in re.findall(r'(-?[\d.]+),(-?[\d.]+)', p)]
xs = [a for a, b in allp]; ys = [b for a, b in allp]
vb = f'{min(xs) - 10:.0f} {min(ys) - 20:.0f} {max(xs) - min(xs) + 150:.0f} {max(ys) - min(ys) + 40:.0f}'
D['axon'] = f'<svg viewBox="{vb}" preserveAspectRatio="xMidYMid meet">{DEFS}' + ''.join(parts) + '</svg>'
D['axon_vb'] = vb

# ---------- diagram layers for the studio (drawn over site and sections) ----------
D['L_axis_site'] = ('<path class="dg" d="M470 200 H96"/><path class="dg" d="M96 200 L40 170 M96 200 L40 230" />'
                    '<path class="dgf" d="M200 170 L60 120 L60 280 L200 230 Z"/><circle class="dpt" cx="470" cy="200" r="7"/><circle class="dpt" cx="200" cy="200" r="7"/>')
D['L_axis_long'] = '<path class="dg" d="M700 155 L40 150"/><circle class="dpt" cx="700" cy="155" r="6"/><path class="dgf" d="M700 155 L40 120 L40 185 Z"/>'
D['L_svc_sec'] = ''.join(f'<rect class="dgf2" x="{x0}" y="{y0}" width="156" height="{y1 - y0}"/>' for x0 in (70, 574) for y0, y1 in ((208, 228), (150, 170), (94, 112))) + \
    '<circle class="dpt" cx="148" cy="218" r="6"/><circle class="dpt" cx="652" cy="160" r="6"/>' + \
    '<path class="dg" d="M148 160 V128" marker-end="url(#ar)"/><path class="dg" d="M148 218 V240" marker-end="url(#ar)"/><path class="dg" d="M652 218 V240" marker-end="url(#ar)"/><path class="dg" d="M652 160 V128" marker-end="url(#ar)"/>'
D['L_svc_site'] = '<rect class="dgf2" x="200" y="112" width="276" height="50"/><rect class="dgf2" x="200" y="238" width="276" height="50"/>'
D['L_light_sec'] = ''.join(f'<path class="dg sun" d="M{x} 20 L{x + 60} 226" marker-end="url(#ar)"/>' for x in (250, 300, 350, 400)) + \
    '<path class="dgf" d="M260 228 L540 228 L470 20 L250 20 Z" opacity=".5"/><circle class="dpt" cx="400" cy="226" r="6"/>'
D['L_light_site'] = '<path class="dgf" d="M200 170 H476 V230 H200 Z"/><circle class="dpt" cx="330" cy="200" r="7"/>'
json.dump(D, open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'salk.json'), 'w'))
print({k: len(v) for k, v in D.items()}, vb)
