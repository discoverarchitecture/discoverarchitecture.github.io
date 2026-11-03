"""Studio FGA's share image, site/studio/og.jpg (1200 x 630): the sample student's own sheets, scattered, then the
lime arrow, then the A1 board made from them. No words except the small "Studio FGA" mark (owner, 29 Oct 2026).
The sample is the owner's real project, shown with permission.

    python3 tools/studio_og.py      # then python3 tools/build_studio.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "site", "studio")
W, H, K = 1200, 630, 2                      # drawn at 2x, then reduced, for clean edges
PAPER, INK, LIME, CORAL, CARD = (255, 246, 234), (27, 26, 23), (207, 242, 90), (255, 90, 54), (255, 255, 255)
FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"


def sheet(path, width, border=3):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    out = Image.new("RGBA", (im.width + 2 * border, im.height + 2 * border), INK + (255,))
    out.paste(im, (border, border))
    return out


def drop(canvas, im, x, y, angle=0, shadow=9):
    """paste with a hard offset shadow, like the page's cards"""
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", im.size, INK + (255,))
    canvas.paste(sh, (x + shadow, y + shadow), im.split()[3])
    canvas.paste(im, (x, y), im)


def main():
    c = Image.new("RGBA", (W * K, H * K), PAPER + (255,))
    raw = os.path.join(S, "sample", "raw")
    # before: five of the student's sheets in a loose pile (site map, process sketches, entrance view, section, plan)
    pile = [("sheet-1.jpg", 300, 30, 40, -7), ("sheet-5.jpg", 290, 310, 70, 6), ("sheet-3.jpg", 320, 20, 270, -4),
            ("sheet-4.jpg", 300, 280, 300, 5), ("sheet-6.jpg", 300, 160, 170, -2)]
    for f, w, x, y, a in pile:
        drop(c, sheet(os.path.join(raw, f), w * K, 3 * K), x * K, y * K, a, 8 * K)
    # the arrow (the landing page's .garrow: lime, ink outline, hard shadow)
    ax, ay, s = 628 * K, 283 * K, 1.45 * K
    pts = [(3, 15), (43, 15), (43, 4), (69, 22), (43, 40), (43, 29), (3, 29)]
    poly = [(ax + p[0] * s, ay + p[1] * s) for p in pts]
    d = ImageDraw.Draw(c)
    d.polygon([(x + 6 * K, y + 6 * K) for x, y in poly], fill=INK)
    d.polygon(poly, fill=LIME, outline=INK, width=3 * K)
    # after: the finished A1 board (the sample's thumbnail, its tiny footer line trimmed)
    b = Image.open(os.path.join(S, "sample", "thumbs", "board.jpg")).convert("RGB")
    b = b.crop((0, 0, b.width, b.height - 22))
    bh = 556 * K
    b = b.resize((round(b.width * bh / b.height), bh), Image.LANCZOS)
    bb = Image.new("RGBA", (b.width + 6 * K, b.height + 6 * K), INK + (255,))
    bb.paste(b, (3 * K, 3 * K))
    drop(c, bb, W * K - bb.width - 56 * K, 30 * K, 0, 10 * K)
    # the small "Studio FGA" mark, bottom left (the page's logo chip)
    f = ImageFont.truetype(FONT, 22 * K)
    lx, ly = 40 * K, H * K - 76 * K
    tw = d.textlength("Studio FGA", font=f)
    chip = (lx, ly, lx + 46 * K + tw + 16 * K, ly + 46 * K)
    d.rounded_rectangle([chip[0] + 4 * K, chip[1] + 4 * K, chip[2] + 4 * K, chip[3] + 4 * K], 14 * K, fill=INK)
    d.rounded_rectangle(chip, 14 * K, fill=CARD, outline=INK, width=2 * K)
    sq = (lx + 7 * K, ly + 7 * K, lx + 39 * K, ly + 39 * K)
    d.rounded_rectangle(sq, 8 * K, fill=CORAL, outline=INK, width=2 * K)
    cx, cy, r = (sq[0] + sq[2]) / 2, (sq[1] + sq[3]) / 2, 10 * K   # four-point star
    d.polygon([(cx, cy - r), (cx + r * .28, cy - r * .28), (cx + r, cy), (cx + r * .28, cy + r * .28), (cx, cy + r),
               (cx - r * .28, cy + r * .28), (cx - r, cy), (cx - r * .28, cy - r * .28)], fill=INK)
    d.text((lx + 48 * K, ly + 23 * K), "Studio FGA", font=f, fill=INK, anchor="lm")
    out = c.convert("RGB").resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1, 40, 2))
    out.save(os.path.join(S, "og.jpg"), quality=86, optimize=True, progressive=True)
    print("wrote site/studio/og.jpg", out.size, os.path.getsize(os.path.join(S, "og.jpg")) // 1024, "KB")


if __name__ == "__main__":
    main()
