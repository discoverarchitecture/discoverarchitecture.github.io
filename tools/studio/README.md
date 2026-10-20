# FGA Studio waitlist page: prototype sources

The design prototype for the FGA Studio waitlist page (canvas boards v30 and v31, direction **A · Pin-up party**, chosen by the
owner on 21 Oct 2026). Live sample: https://claude.ai/artifact/GZnT6zfPvUvbor8VUBCZSp

The owner likes the page but **not the sample case study / jury board on it**: it doesn't look professional enough. The board
is the part to remake.

- `salk.py` draws the Salk Institute site plan, sections and exploded axonometric (our own schematic SVGs) into `salk.json`.
- `gen.py` builds the page into `web/A.html` from `style_A.css` (the Pin-up party look), `style_common.css` (layout and moving
  parts), `board.css` (the sample board in three styles: Minimal Swiss, Bold Editorial, Technical Blueprint) and `common.js`
  (the pile-to-board animation, diagram studio, style picker, image touch-ups, first-screen sign-up).
- `credits.json` holds the credit, licence and source of the eight Salk photos.

To run it:

    python3 tools/studio/salk.py
    mkdir -p tools/studio/web/images/salk && cp site/images/salk-institute/*.webp tools/studio/web/images/salk/
    python3 tools/studio/gen.py          # writes tools/studio/web/A.html
    cd tools/studio/web && python3 -m http.server 8768   # open http://localhost:8768/A.html

URL parameters for screenshots: `?built` (board shown), `?pile` (files shown), `?studio=axis|svc|light`,
`?style=swiss|editorial|blueprint`, `?touch=up|crop|ext|col`, `?sent` (sign-up answered).

`web/` and `salk.json` are generated; don't commit them.
