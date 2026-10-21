# Salk Institute drawings, round 2, for the FGA Studio sample board: schematic and not to scale, drawn like a studio
# set (cut lines heavy, lines beyond thin, poché, figures for scale, plan trees, contours) from the photos and the site's
# own description of the building. Colours come from CSS variables (board2.css) so each board style recolours them.
# Classes: ln0 hairline · ln1 thin · ln2 medium · ln3 heavy · po poché · g1 g2 g3 greys · sea · wt water · acc / accf / acs red
import json, os, math
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
D = {}
DEFS = ('<defs><pattern id="h45" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="6" class="hl"/></pattern>'
        '<pattern id="h45f" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="4" class="hl2"/></pattern>'
        '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" class="accf"/></marker></defs>')
f1 = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')

def fig(x, y, h=17, pose=0, flip=False):
    """A person, feet at (x, y), h tall. pose 0 standing, 1 walking, 2 sitting on the ground line."""
    s = h / 17 * (-1 if flip else 1)
    if pose == 1:
        body = 'M-1.5 -13.4h3l.7 6.4h-.9l2.3 7h-1.3l-2.1-5.6-1.6 5.6h-1.3l1.5-7h-1z'
    elif pose == 2:
        body = 'M-1.5 -9.4h3l.4 4.4h3.2v1.1h-3.2l.2 3.9h-1.2l-.3-3.9h-1.6v3.9h-1.2v-5.2z'
    else:
        body = 'M-1.5 -13.4h3l.5 6.6h-.9l.3 6.8h-1.1l-.3-5.4h-.1l-.3 5.4h-1.1l.3-6.8h-.9z'
    hy = -15.3 if pose != 2 else -11.3
    return (f'<g class="fig" transform="translate({f1(x)} {f1(y)}) scale({f1(s)} {f1(h / 17)})">'
            f'<circle cx="0" cy="{hy}" r="1.5"/><path d="{body}"/></g>')

def tree_plan(x, y, r):
    return (f'<circle class="ln1 g1" cx="{x}" cy="{y}" r="{r}"/><circle class="ln0" cx="{x}" cy="{y}" r="{r * .55:.1f}" fill="none"/>'
            f'<circle class="po" cx="{x}" cy="{y}" r="1"/>')

def tree_elev(x, y, h, r):
    return (f'<line class="ln1" x1="{x}" y1="{y}" x2="{x}" y2="{y - h + r}"/>'
            f'<circle class="ln1" cx="{x}" cy="{y - h + r * .3:.1f}" r="{r}" fill="none"/>')

# ---------------------------------------------------------------- site plan: north up, the Pacific to the west (left)
W, H = 1000, 700
PX0, PX1, PY0, PY1 = 310, 840, 280, 420          # the plaza
WN = (330, 190, 830, 280); WS = (330, 420, 830, 510)  # the two wings
sea = ''.join(f'<path class="ln0" d="M{x} {y} q7 -4 14 0 t14 0 t14 0"/>' for x, y in
              [(20, 80), (60, 130), (30, 200), (70, 260), (24, 330), (64, 390), (28, 460), (70, 520), (30, 600), (66, 650)])
contours = ''.join(f'<path class="ln0" d="M{150 + i * 18} 0 C{140 + i * 18} 160 {166 + i * 18} 300 {146 + i * 18} 460 S{162 + i * 18} 640 {152 + i * 18} 700"/>' for i in range(6))
joints = ''.join(f'<line class="ln0 jt" x1="{x}" y1="{PY0}" x2="{x}" y2="{PY1}"/>' for x in range(PX0 + 14, PX1, 14))
def wing(x0, y0, x1, y1, towers_y, chamfer):
    out = [f'<rect class="lab" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>']
    out += [f'<line class="ln0" x1="{x}" y1="{y0}" x2="{x}" y2="{y1}"/>' for x in range(x0 + 50, x1, 50)]   # lab modules
    out.append(f'<line class="ln0" x1="{x0}" y1="{(y0 + y1) / 2:.0f}" x2="{x1}" y2="{(y0 + y1) / 2:.0f}"/>')
    out.append(f'<rect class="ln3" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none"/>')
    for x in range(x0 + 30, x1 - 40, 100):   # study towers on the plaza side, angled to face the ocean
        ty0, ty1 = towers_y
        if chamfer == 'n':  # north wing: towers hang below (south) into the plaza
            pts = [(x, ty0), (x + 38, ty0), (x + 38, ty1), (x + 14, ty1), (x, ty1 - 14)]
        else:
            pts = [(x, ty0 + 14), (x + 14, ty0), (x + 38, ty0), (x + 38, ty1), (x, ty1)]
        out.append('<polygon class="twr ln2" points="%s"/>' % ' '.join(f'{a},{b}' for a, b in pts))
        out.append(f'<line class="ln0" x1="{x + 8}" y1="{ty0 + (6 if chamfer == "s" else 0)}" x2="{x + 8}" y2="{ty1 - (6 if chamfer == "n" else 0)}"/>')
        out.append(f'<line class="ln0" x1="{x + 30}" y1="{ty0}" x2="{x + 30}" y2="{ty1}"/>')
    return ''.join(out)
grove = ''.join(tree_plan(x, y, r) for x, y, r in [
    (875, 215, 14), (905, 250, 11), (940, 222, 16), (975, 262, 12), (890, 300, 13), (930, 318, 10), (965, 345, 15), (885, 395, 11),
    (920, 385, 14), (955, 420, 12), (900, 450, 15), (940, 470, 11), (975, 500, 14), (880, 505, 12), (915, 535, 13), (960, 560, 11),
    (870, 160, 10), (925, 140, 13), (980, 180, 10), (985, 600, 12), (940, 605, 10)])
D['site'] = f'''<svg class="sp" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">{DEFS}
<rect class="pap" width="{W}" height="{H}"/>
<rect class="sea" width="140" height="{H}"/>{sea}
<path class="ln1" d="M140 0 C150 180 128 320 146 470 S128 640 140 700"/>{contours}
<rect class="g2" x="250" y="{PY0 + 34}" width="60" height="{PY1 - PY0 - 68}"/>
<rect class="wt ln1" x="262" y="{PY0 + 52}" width="40" height="{PY1 - PY0 - 104}"/>
<rect class="plz" x="{PX0}" y="{PY0}" width="{PX1 - PX0}" height="{PY1 - PY0}"/>{joints}
<line class="ln3" x1="{PX0}" y1="{PY0}" x2="{PX0}" y2="{PY1}"/>
{wing(*WN, (PY0, PY0 + 30), 'n')}{wing(*WS, (PY1 - 30, PY1), 's')}
<line class="acc" x1="{PX1 - 12}" y1="350" x2="{PX0}" y2="350"/><rect class="accf" x="{PX1 - 18}" y="345" width="10" height="10"/>
<line class="acc ln0" x1="{PX0}" y1="350" x2="282" y2="350"/>
<path class="ln0" d="M840 350 H1000"/><line class="ln1" x1="840" y1="330" x2="840" y2="370"/>
{grove}
<g class="nth"><circle class="ln1" cx="940" cy="52" r="18" fill="none"/><path class="po" d="M940 34 L946 58 L940 53 L934 58 Z"/><text class="tx" x="940" y="88" text-anchor="middle">N</text></g>
<text class="tx" x="70" y="676" text-anchor="middle">PACIFIC</text>
<text class="tx" x="580" y="165" text-anchor="middle">NORTH LABORATORY</text>
<text class="tx" x="580" y="548" text-anchor="middle">SOUTH LABORATORY</text>
<text class="tx s" x="580" y="320" text-anchor="middle">TRAVERTINE PLAZA</text>
<text class="tx s" x="280" y="470" text-anchor="middle">LOWER</text><text class="tx s" x="280" y="484" text-anchor="middle">TERRACE</text>
<text class="tx s" x="930" y="650" text-anchor="middle">GROVE</text>
<path class="ln0" d="M700 290 L720 262"/><text class="tx s" x="724" y="258">STUDY TOWERS</text>
</svg>'''

# ---------------------------------------------------------------- cross-section through both wings and the plaza
GL = 300  # the plaza level
LEVELS = [('lab', 360, 300), ('svc', 300, 272), ('lab', 272, 212), ('svc', 212, 184), ('lab', 184, 124), ('svc', 124, 96)]
def truss(x0, x1, y0, y1):
    out = [f'<rect class="svcf" x="{x0}" y="{y1}" width="{x1 - x0}" height="{y0 - y1}"/>']
    out += [f'<line class="ln1" x1="{x}" y1="{y1}" x2="{x}" y2="{y0}"/>' for x in range(x0 + 24, x1, 24)]
    out.append(f'<rect class="ln1" x="{x0 + 3}" y="{y1 + 3}" width="{x1 - x0 - 6}" height="{y0 - y1 - 6}" fill="none"/>')
    return ''.join(out)
def xwing(x0, x1, tower_x):
    out = []
    for kind, y0, y1 in LEVELS:
        out.append(truss(x0, x1, y0, y1) if kind == 'svc' else f'<rect class="lab" x="{x0}" y="{y1}" width="{x1 - x0}" height="{y0 - y1}"/>')
        out.append(f'<line class="ln3" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}"/>')   # cut slab
    out.append(f'<rect class="ln3" x="{x0}" y="96" width="{x1 - x0}" height="264" fill="none"/>')
    out.append(f'<line class="ln2" x1="{x0 + (x1 - x0) * .5:.0f}" y1="96" x2="{x0 + (x1 - x0) * .5:.0f}" y2="360" stroke-dasharray="0"/>'.replace(' stroke-dasharray="0"', ''))
    # the study tower on the plaza side: four studies, teak window walls, cut through
    tx0, tx1 = tower_x
    out.append(f'<rect class="twr" x="{tx0}" y="100" width="{tx1 - tx0}" height="200"/>')
    for i in range(4):
        y = 100 + i * 50
        out.append(f'<line class="ln3" x1="{tx0}" y1="{y + 50}" x2="{tx1}" y2="{y + 50}"/>')
        wx = tx1 - 14 if tx0 < 500 else tx0 + 4
        out.append(f'<rect class="teak" x="{wx}" y="{y + 10}" width="10" height="30"/>')
    out.append(f'<rect class="ln3" x="{tx0}" y="100" width="{tx1 - tx0}" height="200" fill="none"/>')
    return ''.join(out)
people = (fig(400, GL, 17, 1) + fig(424, GL, 16) + fig(560, GL, 17, 1, True) + fig(590, GL, 15, 0, True)
          + fig(650, GL, 16, 1) + fig(200, 272, 14) + fig(760, 212, 14, 0, True) + fig(118, 360, 14, 1) + fig(500, GL, 12, 2))
D['section'] = f'''<svg viewBox="0 0 1000 420" preserveAspectRatio="xMidYMid slice">{DEFS}
<rect class="pap" width="1000" height="420"/>
<rect class="gnd" x="0" y="{GL}" width="1000" height="120"/>
<rect class="lab" x="40" y="{GL}" width="40" height="60"/><rect class="lab" x="920" y="{GL}" width="40" height="60"/>
{xwing(80, 320, (320, 372))}{xwing(640, 880, (588, 640))}
<line class="ln3" x1="0" y1="{GL}" x2="40" y2="{GL}"/><line class="ln3" x1="40" y1="{GL}" x2="40" y2="360"/><line class="ln3" x1="40" y1="360" x2="80" y2="360"/>
<line class="ln3" x1="920" y1="360" x2="960" y2="360"/><line class="ln3" x1="960" y1="360" x2="960" y2="{GL}"/><line class="ln3" x1="960" y1="{GL}" x2="1000" y2="{GL}"/>
<line class="ln3" x1="372" y1="{GL}" x2="588" y2="{GL}"/>
<rect class="accf" x="476" y="{GL - 1}" width="8" height="5"/>
<path class="ln0 jt" d="{' '.join(f'M{x} {GL} v4' for x in range(384, 588, 12))}"/>
{people}
<text class="tx" x="200" y="80" text-anchor="middle">SOUTH LABORATORY</text><text class="tx" x="760" y="80" text-anchor="middle">NORTH LABORATORY</text>
<text class="tx s" x="480" y="{GL + 22}" text-anchor="middle">TRAVERTINE PLAZA</text>
<text class="tx s" x="60" y="392" text-anchor="middle">LIGHT COURT</text>
<path class="ln0" d="M880 158 h40"/><text class="tx s" x="924" y="161">LABORATORY</text>
<path class="ln0" d="M880 198 h40"/><text class="tx s" x="924" y="201">SERVICE FLOOR</text>
<path class="ln0" d="M346 100 v-14 h30"/><text class="tx s" x="380" y="89">STUDY TOWER</text>
</svg>'''

# ---------------------------------------------------------------- long section along the water channel, to the Pacific
PL = 250  # the plaza level
def tower_elev(x, w):
    out = [f'<rect class="twr" x="{x}" y="46" width="{w}" height="204"/>']
    for i in range(4):
        y = 50 + i * 51
        out.append(f'<rect class="teak" x="{x + 10}" y="{y + 10}" width="{w - 40}" height="32"/>')
        out.append(f'<line class="ln0" x1="{x}" y1="{y + 51}" x2="{x + w}" y2="{y + 51}"/>')
    out.append(f'<path class="ln1" d="M{x + w - 30} 46 L{x + w} 60 V250 M{x + w - 30} 46 V250" fill="none"/>')
    out.append(f'<rect class="ln1" x="{x}" y="46" width="{w}" height="204" fill="none"/>')
    return ''.join(out)
elev = ''.join(f'<line class="ln0" x1="320" y1="{y}" x2="1000" y2="{y}"/>' for y in (96, 124, 184, 212))
towers = ''.join(tower_elev(x, 74) for x in (352, 480, 608, 736, 864))
cols = ''.join(f'<line class="ln1" x1="{x}" y1="212" x2="{x}" y2="250"/>' for x in range(336, 1000, 32))
grove_e = ''.join(tree_elev(x, PL, h, r) for x, h, r in [(1030, 150, 30), (1075, 190, 36), (1120, 160, 28), (1165, 200, 34), (1195, 140, 26)])
D['long'] = f'''<svg viewBox="0 0 1200 380" preserveAspectRatio="xMidYMid slice">{DEFS}
<rect class="pap" width="1200" height="380"/>
<rect class="sea" x="0" y="330" width="90" height="50"/>
<path class="gnd" d="M90 330 C130 326 150 304 170 300 H200 V290 H300 V250 H1200 V380 H90 Z"/>
<path class="ln2" d="M90 330 C130 326 150 304 170 300 H200 V290 H300" fill="none"/>
<rect class="lab" x="320" y="46" width="680" height="204"/>{elev}{cols}{towers}
<line class="ln1" x1="320" y1="46" x2="1000" y2="46"/>
<line class="ln3" x1="300" y1="290" x2="300" y2="250"/><line class="ln3" x1="300" y1="250" x2="1200" y2="250"/>
<rect class="wt ln1" x="236" y="282" width="64" height="8"/>
<line class="acc" x1="980" y1="248" x2="300" y2="248"/><line class="acc" x1="300" y1="248" x2="300" y2="282"/><rect class="accf" x="978" y="244" width="8" height="6"/>
{grove_e}
{fig(940, PL, 17, 1, True)}{fig(820, PL, 16)}{fig(700, PL, 17, 1)}{fig(540, PL, 15, 1, True)}{fig(312, PL, 17)}{fig(262, 290, 15, 0, True)}{fig(420, PL, 12, 2)}
<text class="tx" x="45" y="364" text-anchor="middle">PACIFIC</text>
<text class="tx s" x="640" y="272" text-anchor="middle">PLAZA AND WATER CHANNEL</text>
<text class="tx s" x="250" y="312" text-anchor="middle">LOWER TERRACE</text>
<text class="tx" x="660" y="30" text-anchor="middle">NORTH LABORATORY, SEEN ACROSS THE PLAZA</text>
</svg>'''

# ---------------------------------------------------------------- exploded axonometric, seen from the south-west
S = 8.6
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def P(x, y, z):  # x east, y north, z up; isometric, seen from the south-west (west and south are near)
    return (300 + (x - y) * C30 * S, 330 + (-x - y) * S30 * S - z * S)
def poly(cls, pts, extra=''):
    return '<polygon class="%s" points="%s"%s/>' % (cls, ' '.join('%.1f,%.1f' % P(*p) for p in pts), extra)
def box(x0, y0, x1, y1, z0, z1, top='bt', south='bs', east='be', outline='ln1'):
    """Seen from the south-west, the visible faces are the top, the south face (y = y0) and the west face (x = x0)."""
    return (poly(f'{south} {outline}', [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)])
            + poly(f'{east} {outline}', [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)])
            + poly(f'{top} {outline}', [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]))
def line(cls, a, b, extra=''):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{extra}/>'
parts = []
# the ground: the cliff, the sea to the west (x < -10), the plaza between the wings
parts.append(poly('sea', [(-34, -30, -4), (-10, -30, -4), (-10, 56, -4), (-34, 56, -4)]))
parts.append(poly('g1 ln1', [(-10, -30, 0), (74, -30, 0), (74, 56, 0), (-10, 56, 0)]))
parts.append(poly('g2 ln1', [(-10, -30, -4), (-10, 56, -4), (-10, 56, 0), (-10, -30, 0)]))   # the cliff face
parts.append(poly('g2 ln1', [(-10, 4, -1.2), (-2, 4, -1.2), (-2, 24, -1.2), (-10, 24, -1.2)]))   # the lower terrace
parts.append(poly('g3 ln1', [(-10, 4, -1.2), (-10, 24, -1.2), (-10, 24, -4), (-10, -4 + 0, -4)][:0] + [(-10, 4, -1.2), (-10, 24, -1.2), (-10, 24, -4), (-10, 4, -4)]))
# the north wing, whole, drawn light so the exploded south wing reads
parts.append(box(0, 28, 60, 48, 0, 22.5, top='bt', south='bs', east='be'))
for x in range(4, 58, 11):
    parts.append(box(x, 24.6, x + 4.4, 28, 0, 17, top='bt', south='bs', east='be'))
# the plaza, with the water channel on its axis, and the joints
parts.append(poly('plz ln1', [(0, 1, .4), (60, 1, .4), (60, 27, .4), (0, 27, .4)]))
for x in range(2, 60, 2):
    parts.append(line('ln0 jt', (x, 1, .45), (x, 27, .45)))
parts.append(line('acc', (58, 14, .5), (-1, 14, .5)))
parts.append(line('acc dash', (-1, 14, .5), (-30, 14, -3.5), ' marker-end="url(#arr)"'))
# the south wing, exploded: ground laboratory and its study towers in place, the layers above lifted
lv = [('lab', 0, 5), ('svc', 5, 7.5), ('lab', 7.5, 12.5), ('svc', 12.5, 15), ('lab', 15, 20), ('svc', 20, 22.5)]
gap = 3
for i, (kind, z0, z1) in enumerate(lv):
    o = i * gap
    if kind == 'svc':
        parts.append(box(0, -20, 60, 0, z0 + o, z1 + o, top='svct', south='svcs', east='svce', outline='ln1 accl'))
    else:
        parts.append(box(0, -20, 60, 0, z0 + o, z1 + o, top='bt', south='bs', east='be'))
    if i:  # dotted guide lines at the corners, showing where each layer sits
        parts.append(line('ln0 dash', (0, -20, z0 + o - gap), (0, -20, z0 + o)))
        parts.append(line('ln0 dash', (60, -20, z0 + o - gap), (60, -20, z0 + o)))
for x in range(4, 58, 11):   # the study towers on the plaza side, with their angled faces
    parts.append(box(x, 0, x + 4.4, 3.4, 0, 17, top='bt', south='bs', east='be'))
    parts.append(poly('teak ln0', [(x, .4, 1), (x, 3, 1), (x, 3, 16), (x, .4, 16)]))
parts.append(line('ln0', (60, -20, 0), (60, -20, 22.5 + 5 * gap)))
# labels with leaders
lbls = [((60, -20, 22.5 + 5 * gap - 1.2), 'Service floor', 40, 0), ((60, -20, 20 + 4 * gap - 2.5), 'Laboratory', 40, 0),
        ((60, -20, 15 + 3 * gap - 1.2), 'Service floor', 40, 0), ((60, -20, 12.5 + 2 * gap - 2.5), 'Laboratory', 40, 0),
        ((60, -20, 7.5 + gap - 1.2), 'Service floor', 40, 0), ((60, -20, 2.5), 'Laboratory', 40, 0),
        ((48, 1.5, 17), 'Study towers', 30, -40), ((6, 14, .5), 'Travertine plaza', -50, 40), ((-28, 14, -3.2), 'To the Pacific', -30, 24),
        ((10, 48, 22.5), 'North laboratory', -40, -30), ((-6, 24, -1.2), 'Lower terrace', -60, -10)]
for (x, y, z), t, dx, dy in lbls:
    a, b = P(x, y, z)
    parts.append(f'<path class="ln0" d="M{a:.1f} {b:.1f} l{dx} {dy} h{6 if dx >= 0 else -6}"/>')
    parts.append(f'<text class="tx" x="{a + dx + (9 if dx >= 0 else -9):.1f}" y="{b + dy + 3:.1f}" text-anchor="{"start" if dx >= 0 else "end"}">{t.upper()}</text>')
import re
allp = []
for p in parts:
    allp += [(float(a), float(b)) for a, b in re.findall(r'(-?[\d.]+),(-?[\d.]+)', p)]
    allp += [(float(a), float(b)) for a, b in re.findall(r'x="(-?[\d.]+)" y="(-?[\d.]+)"', p)]
xs = [a for a, b in allp]; ys = [b for a, b in allp]
x0, y0, x1, y1 = min(xs) - 150, min(ys) - 14, max(xs) + 130, max(ys) + 14
D['axon'] = f'<svg class="ax" viewBox="{x0:.0f} {y0:.0f} {x1 - x0:.0f} {y1 - y0:.0f}" preserveAspectRatio="xMidYMid meet">{DEFS}' + ''.join(parts) + '</svg>'
D['axon_vb'] = [round(x0), round(y0), round(x1 - x0), round(y1 - y0)]

# ---------------------------------------------------------------- three small concept diagrams, one per idea
def dia(body): return f'<svg viewBox="0 0 200 140" preserveAspectRatio="xMidYMid meet">{DEFS}<rect class="pap" width="200" height="140"/>{body}</svg>'
D['dia_axis'] = dia('<rect class="sea" x="0" y="0" width="34" height="140"/><rect class="po" x="70" y="34" width="110" height="24"/><rect class="po" x="70" y="82" width="110" height="24"/>'
                    '<rect class="plz ln1" x="64" y="58" width="116" height="24"/>'
                    '<line class="acc" x1="178" y1="70" x2="40" y2="70" marker-end="url(#arr)"/><path class="acs" d="M64 58 L8 30 V110 L64 82 Z"/>')
D['dia_svc'] = dia(''.join(f'<rect class="{"accf" if i % 2 else "lab ln1"}" x="40" y="{112 - (i + 1) * 15}" width="120" height="15"/>' for i in range(6))
                   + '<rect class="ln2" x="40" y="22" width="120" height="90" fill="none"/><line class="ln3" x1="20" y1="112" x2="180" y2="112"/>'
                   + ''.join(f'<path class="acc" d="M{x} 82 v-8 M{x} 52 v-8" marker-end="url(#arr)"/>' for x in (70, 130)))
D['dia_light'] = dia('<rect class="po" x="22" y="40" width="40" height="72"/><rect class="po" x="138" y="40" width="40" height="72"/><line class="ln3" x1="0" y1="112" x2="200" y2="112"/>'
                     + ''.join(f'<line class="acc sun" x1="{x}" y1="8" x2="{x + 14}" y2="110" marker-end="url(#arr)"/>' for x in (72, 94, 116))
                     + '<path class="acs" d="M62 112 H138 L124 8 H76 Z"/>')

# ---------------------------------------------------------------- diagram layers for the studio, drawn over the base drawings
D['L_axis_site'] = ('<path class="dg" d="M828 350 H150"/><path class="dg" d="M150 350 L60 300 M150 350 L60 400"/>'
                    '<path class="dgf" d="M310 280 L40 170 L40 530 L310 420 Z"/><circle class="dpt" cx="828" cy="350" r="7"/><circle class="dpt" cx="310" cy="350" r="7"/>')
D['L_axis_long'] = '<path class="dg" d="M980 246 L40 150"/><circle class="dpt" cx="980" cy="246" r="6"/><path class="dgf" d="M980 246 L40 110 L40 190 Z"/>'
D['L_svc_sec'] = ''.join(f'<rect class="dgf2" x="{x0}" y="{y1}" width="240" height="{y0 - y1}"/>' for x0 in (80, 640) for y0, y1 in ((300, 272), (212, 184), (124, 96))) + \
    '<circle class="dpt" cx="200" cy="286" r="6"/><circle class="dpt" cx="760" cy="198" r="6"/>' + \
    ''.join(f'<path class="dg" d="M{x} {y} v{d}" marker-end="url(#arr)"/>' for x in (200, 760) for y, d in ((272, -24), (212, 24), (184, -24), (124, 24)))
D['L_svc_site'] = '<rect class="dgf2" x="330" y="190" width="500" height="90"/><rect class="dgf2" x="330" y="420" width="500" height="90"/>'
D['L_light_sec'] = ''.join(f'<path class="dg sun" d="M{x} 20 L{x + 60} {GL - 2}" marker-end="url(#arr)"/>' for x in (330, 390, 450, 510)) + \
    f'<path class="dgf" d="M372 {GL} L588 {GL} L540 20 L330 20 Z" opacity=".5"/><circle class="dpt" cx="480" cy="{GL}" r="6"/>'
D['L_light_site'] = '<path class="dgf" d="M330 280 H830 V420 H330 Z"/><circle class="dpt" cx="580" cy="350" r="7"/>'
json.dump(D, open(SP + 'salk2.json', 'w'))
print({k: len(v) for k, v in D.items() if isinstance(v, str)}, D['axon_vb'])
