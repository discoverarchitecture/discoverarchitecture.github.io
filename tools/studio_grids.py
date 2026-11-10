#!/usr/bin/env python3
"""Free board grids to download (SEO strategy chat, owner's go-ahead 10 Nov 2026): true-size PDF and SVG layout grids
for A1, A0 and the US ARCH D / ARCH E sheets, linked from the guide "Architecture presentation board templates"
(tools/studio_guides/architecture-presentation-board-templates.md). Writes site/studio/grids/<name>.pdf and .svg, a
zip of all of them, and preview.webp for the guide. Our own drawings, released under CC0. Every number in the guide's
table comes from GRIDS below, so change both together.

    python3 tools/studio_grids.py
"""
import io, os, zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'studio', 'grids')
IN = 25.4  # mm per inch

# name, label, width, height (mm), margin, columns, rows, gutter, title band height (0 = none), unit for the label
GRIDS = [
    ('a1-portrait-4-columns',   'A1 portrait',   594, 841, 25, 4, 6, 10, 60, 'mm'),
    ('a1-landscape-6-columns',  'A1 landscape',  841, 594, 25, 6, 4, 10, 0, 'mm'),
    ('a0-landscape-8-columns',  'A0 landscape', 1189, 841, 30, 8, 6, 12, 0, 'mm'),
    ('arch-d-24x36-portrait-4-columns',  'ARCH D 24 × 36 in portrait',  24 * IN, 36 * IN, 1 * IN, 4, 6, 0.4 * IN, 2.4 * IN, 'in'),
    ('arch-d-24x36-landscape-6-columns', 'ARCH D 24 × 36 in landscape', 36 * IN, 24 * IN, 1 * IN, 6, 4, 0.4 * IN, 0, 'in'),
    ('arch-e-36x48-landscape-8-columns', 'ARCH E 36 × 48 in landscape', 48 * IN, 36 * IN, 1.25 * IN, 8, 6, 0.5 * IN, 0, 'in'),
]
BLUE, TITLE = (0.0, 0.55, 0.85), (0.85, 0.23, 0.15)


def boxes(g):
    """The grid as rectangles in mm from the top-left: (kind, x, y, w, h)."""
    name, label, W, H, m, cols, rows, gut, band, unit = g
    uw, uh = W - 2 * m, H - 2 * m
    cw = (uw - (cols - 1) * gut) / cols
    top = m + (band + gut if band else 0)
    rh = (H - m - top - (rows - 1) * gut) / rows
    out = [('margin', m, m, uw, uh)]
    if band:
        out.append(('title', m, m, uw, band))
    for c in range(cols):
        out.append(('col', m + c * (cw + gut), top, cw, H - m - top))
        for r in range(rows):
            out.append(('cell', m + c * (cw + gut), top + r * (rh + gut), cw, rh))
    return out, cw, rh


def fmt(v, unit):
    return f'{v / IN:.2f} in'.replace('.00 in', ' in') if unit == 'in' else f'{v:.1f} mm'.replace('.0 mm', ' mm')


def note(g, cw, rh):
    name, label, W, H, m, cols, rows, gut, band, unit = g
    size = f'{fmt(W, unit)} × {fmt(H, unit)}'.replace(' in ×', ' ×')
    t = (f'{label} · {size} · margins {fmt(m, unit)} · {cols} columns of {fmt(cw, unit)} · {rows} rows of {fmt(rh, unit)} · '
         f'gutters {fmt(gut, unit)}' + (f' · title band {fmt(band, unit)}' if band else ''))
    return t + ' · Free grid from Find Great Architecture (findgreatarchitecture.com), CC0. Put it on its own layer and hide it before you print.'


def pdf(g):
    name, label, W, H, *_ = g
    bx, cw, rh = boxes(g)
    pt = 72 / IN
    b = io.BytesIO()
    c = canvas.Canvas(b, pagesize=(W * pt, H * pt))
    c.setTitle(f'{label} grid · Find Great Architecture'); c.setAuthor('Find Great Architecture'); c.setSubject('CC0 layout grid')
    for kind, x, y, w, h in bx:
        Y = (H - y - h) * pt
        if kind == 'cell':
            c.setFillColor(Color(*BLUE, alpha=0.07)); c.setStrokeColor(Color(*BLUE, alpha=0.55)); c.setLineWidth(0.5)
            c.rect(x * pt, Y, w * pt, h * pt, stroke=1, fill=1)
        elif kind == 'title':
            c.setFillColor(Color(*TITLE, alpha=0.10)); c.setStrokeColor(Color(*TITLE, alpha=0.7)); c.setLineWidth(0.75)
            c.rect(x * pt, Y, w * pt, h * pt, stroke=1, fill=1)
            c.setFillColor(Color(*TITLE, alpha=0.8)); c.setFont('Helvetica', 14); c.drawString((x + 6) * pt, Y + (h - 9) * pt, 'Title band')
        elif kind == 'margin':
            c.setStrokeColor(Color(0, 0, 0, alpha=0.6)); c.setLineWidth(0.75); c.setDash(6, 4)
            c.rect(x * pt, Y, w * pt, h * pt, stroke=1, fill=0); c.setDash()
    c.setFillColor(Color(0, 0, 0, alpha=0.55)); c.setFont('Helvetica', 9)
    c.drawString(g[4] * pt, g[4] * 0.4 * pt, note(g, cw, rh))
    c.showPage(); c.save()
    return b.getvalue()


def svg(g):
    name, label, W, H, *_ = g
    bx, cw, rh = boxes(g)
    r = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{r(W)}mm" height="{r(H)}mm" viewBox="0 0 {r(W)} {r(H)}">',
             f'<title>{label} grid · Find Great Architecture (CC0)</title>', f'<rect width="{r(W)}" height="{r(H)}" fill="#fff"/>']
    for kind, x, y, w, h in bx:
        if kind == 'cell':
            parts.append(f'<rect x="{r(x)}" y="{r(y)}" width="{r(w)}" height="{r(h)}" fill="#008cd9" fill-opacity=".07" stroke="#008cd9" stroke-opacity=".55" stroke-width=".18"/>')
        elif kind == 'title':
            parts.append(f'<rect x="{r(x)}" y="{r(y)}" width="{r(w)}" height="{r(h)}" fill="#d93b26" fill-opacity=".1" stroke="#d93b26" stroke-opacity=".7" stroke-width=".26"/>')
            parts.append(f'<text x="{r(x + 6)}" y="{r(y + 9)}" font-family="Helvetica, Arial, sans-serif" font-size="5" fill="#d93b26">Title band</text>')
        elif kind == 'margin':
            parts.append(f'<rect x="{r(x)}" y="{r(y)}" width="{r(w)}" height="{r(h)}" fill="none" stroke="#000" stroke-opacity=".6" stroke-width=".26" stroke-dasharray="2 1.4"/>')
    t = note(g, cw, rh).replace('&', '&amp;')
    parts.append(f'<text x="{r(g[4])}" y="{r(H - g[4] * 0.4)}" font-family="Helvetica, Arial, sans-serif" font-size="3.2" fill="#000" fill-opacity=".55">{t}</text></svg>\n')
    return '\n'.join(parts)


def preview():
    """One picture of all six grids for the guide, each drawn to the same scale per row."""
    pad, gap = 40, 60
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
    short = {'A1 portrait': 'A1 portrait', 'A1 landscape': 'A1 landscape', 'A0 landscape': 'A0 landscape',
             'ARCH D 24 × 36 in portrait': '24 × 36 in', 'ARCH D 24 × 36 in landscape': '24 × 36 in',
             'ARCH E 36 × 48 in landscape': '36 × 48 in'}
    rows = [GRIDS[:3], GRIDS[3:]]
    scale = 0.36  # px per mm
    width = pad * 2 + max(sum(g[2] * scale for g in row) + gap * (len(row) - 1) for row in rows)
    height = pad + sum(max(g[3] * scale for g in row) + 80 + gap for row in rows)
    im = Image.new('RGB', (int(width), int(height)), 'white'); d = ImageDraw.Draw(im, 'RGBA')
    y0 = pad
    for row in rows:
        x0 = pad
        for g in row:
            bx, cw, rh = boxes(g)
            W, H = g[2] * scale, g[3] * scale
            d.rectangle([x0, y0, x0 + W, y0 + H], outline=(0, 0, 0, 90), width=2)
            for kind, x, y, w, h in bx:
                q = [x0 + x * scale, y0 + y * scale, x0 + (x + w) * scale, y0 + (y + h) * scale]
                if kind == 'cell': d.rectangle(q, fill=(0, 140, 217, 26), outline=(0, 140, 217, 150), width=1)
                elif kind == 'title': d.rectangle(q, fill=(217, 59, 38, 30), outline=(217, 59, 38, 180), width=1)
            d.text((x0, y0 + H + 14), short[g[1]], fill=(30, 30, 30), font=font)
            x0 += W + gap
        y0 += max(g[3] * scale for g in row) + 80 + gap
    im.save(os.path.join(OUT, 'preview.webp'), 'WEBP', quality=90)
    return im.size


os.makedirs(OUT, exist_ok=True)
z = zipfile.ZipFile(os.path.join(OUT, 'find-great-architecture-board-grids.zip'), 'w', zipfile.ZIP_DEFLATED)
for g in GRIDS:
    p, s = pdf(g), svg(g)
    open(os.path.join(OUT, g[0] + '.pdf'), 'wb').write(p); open(os.path.join(OUT, g[0] + '.svg'), 'w').write(s)
    # fixed timestamps so the zip only changes when a grid does
    for ext, data in (('pdf', p), ('svg', s.encode())):
        zi = zipfile.ZipInfo(f'{g[0]}.{ext}', (2026, 11, 10, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, data)
    _, cw, rh = boxes(g)
    print(f'{g[1]}: column {fmt(cw, g[9])}, row {fmt(rh, g[9])}')
z.close()
print('preview', preview())
