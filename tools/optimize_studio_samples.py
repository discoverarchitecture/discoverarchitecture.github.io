#!/usr/bin/env python3
"""Make the Studio FGA sample pictures light (owner, 13 Nov 2026: "solve the lag issue").

  python3 tools/optimize_studio_samples.py

For every site/studio/sample/{board,deck,raw}/*.jpg this writes, next to it (the JPG itself is never touched):
  X.webp     the same picture at the same size as WebP (about 55% smaller, no visible loss at quality 80)
  X-m.webp   (board and deck only) a copy at most 1000 px wide for thumbnails and previews. The sample board is drawn
             at 300-480 px on the landing page, so the 2900 px original was ten times more than it needs.
The app reads the WebP files (project.js and app.js name them); the editor uses X.webp, small sheets use X-m.webp.
Re-run it after replacing a sample picture. Needs Pillow.
"""
import io, sys
from pathlib import Path
from PIL import Image

SAMPLE = Path(__file__).resolve().parent.parent / 'site' / 'studio' / 'sample'


def save(im, path, quality):
    b = io.BytesIO()
    im.save(b, 'WEBP', quality=quality, method=6)
    path.write_bytes(b.getvalue())
    return len(b.getvalue())


def main():
    total_in = total_full = total_m = 0
    for folder in ('board', 'deck', 'raw'):
        for src in sorted((SAMPLE / folder).glob('*.jpg')):
            im = Image.open(src).convert('RGB')
            total_in += src.stat().st_size
            total_full += save(im, src.with_suffix('.webp'), 80)
            if folder != 'raw':
                m = im if im.width <= 1000 else im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
                total_m += save(m, src.with_name(src.stem + '-m.webp'), 78)
    print(f'JPG {total_in // 1024} KB -> WebP {total_full // 1024} KB (+ {total_m // 1024} KB of small copies)')


if __name__ == '__main__':
    sys.exit(main())
