# FGA Studio waitlist page: prototype sources

The design prototype for the FGA Studio waitlist page (canvas boards v30 and v31, direction **A · Pin-up party**, chosen by the
owner on 21 Oct 2026). Live sample: https://claude.ai/artifact/GZnT6zfPvUvbor8VUBCZSp

The owner likes the page but **not the sample case study / jury board on it**: it doesn't look professional enough. The board
is the part to remake.

- `salk2.py` draws the Salk Institute site plan, cross-section, long section, exploded axonometric and three small concept
  diagrams (our own schematic SVGs, drawn like a studio set: cut lines heavy, lines beyond thin, poché, figures for scale)
  into `salk2.json`; `draw2.css` is their line system.
- `board2.py` and `board2.css` are the sample board, round 3 (canvas v32): a competition-style A1 sheet on a 12-column grid in
  three layouts, **Calm grid**, **Drawing first** and **Editorial**. Every layout has the same seven slots (hero, axon, section,
  long, site, ph1, ph2), so the hero's pile-to-board animation works on any of them. `preview2.py` renders the three on their
  own (`web/boards.html`).
- `gen.py` builds the page into `web/A.html` from `style_A.css` (the Pin-up party look), `style_common.css` (layout and moving
  parts), the board files above and `common.js` (the pile-to-board animation, diagram studio, style picker, image touch-ups,
  first-screen sign-up). `HERO=drawing` or `HERO=editorial` puts that layout in the hero instead (`web/A_drawing.html`,
  `web/A_editorial.html`); the style picker switches between all three.
- `credits.json` holds the credit, licence and source of the eight Salk photos.

To run it:

    python3 tools/studio/salk2.py
    mkdir -p tools/studio/web/images/salk && cp site/images/salk-institute/*.webp tools/studio/web/images/salk/
    python3 tools/studio/gen.py          # writes tools/studio/web/A.html
    python3 tools/studio/preview2.py     # writes tools/studio/web/boards.html, the three boards alone
    cd tools/studio/web && python3 -m http.server 8768   # open http://localhost:8768/A.html

URL parameters for screenshots: `?built` (board shown), `?pile` (files shown), `?studio=axis|svc|light`,
`?style=calm|drawing|editorial`, `?touch=up|crop|ext|col`, `?sent` (sign-up answered).

`web/` and `salk2.json` are generated; don't commit them.
