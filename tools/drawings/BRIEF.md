# Drawings for the most-studied buildings (Sonnet, checked by Opus)

Architecture students study a building through its plans, sections and elevations. Only about 9% of the wall shows
a drawing. This job finds free drawings on Wikimedia Commons for the 1,000 most-studied buildings
(`tools/top1000.txt`, made by `tools/fetch_pageviews.py`).

Read `CLAUDE.md` first: free images only, network work on GitHub Actions.

## 1. The tool: `tools/drawings_scan.py` (runs on Actions)

For each id in `tools/top1000.txt` (`--first N`, `--offset K` and `--ids a,b` to slice), using the helpers in
`tools/fetch_images.py` (`api`, `members`, `infos`, `strip`, `describe`, `DRAWINGS`, `OK_LICENSE`):
- **Look in three places:**
  - the building's Commons category (`commons`) and its sub-folders two levels down, preferring folders named
    plan, section, elevation, drawing, sketch, model, blueprint or HABS;
  - a Commons search for `"<name>" plan OR section OR elevation OR drawing`, limited to 30 hits;
  - HABS/HAER drawings for US buildings, which are public domain and often in "HABS" sub-folders.
- **Keep a file only if all of these hold:**
  - it is a drawing (`describe()` gives one of `DRAWINGS`, or its name or categories say plan, section, elevation,
    drawing, sketch, blueprint or axonometric);
  - its licence passes `OK_LICENSE`;
  - it is at least 700 px on its long side;
  - it is JPEG, PNG, GIF or TIFF, or a PDF/DjVu that has a page thumbnail;
  - it is not already in the building's gallery and not in a `skip` list in `tools/image_choices.json`.
- **Write `tools/drawings/candidates.json`:**
  `{id: [{file, kind, w, h, license, author, desc (120 chars), cats (6), thumb}]}`, at most 6 per building, plans
  and sections first.
- **Make contact sheets `tools/drawings/sheets/sheet_NN.jpg`:**
  - 8 buildings per sheet, one row each;
  - each row starts with a label (`index id — name`), then the current main photo (so the building can be
    recognised), then candidates `d1`…`d6`;
  - thumbnails about 260 px, each sheet under about 450 KB.
- Pace requests and retry on 429/5xx. Use a User-Agent like `fetch_images.py`'s, with no personal data.

Run it with `tools/run_request.txt` (first line `python -u tools/drawings_scan.py --first 200`), in a small commit of
its own. GitHub skips the trigger when a push changes more than 300 files. Wait with a background loop on
`git fetch` until the newest commit starts with "Tool results". The Actions queue is shared with other jobs, so it
may wait its turn.

## 2. First check by eye (you)

Open each sheet once and decide for every candidate, writing `tools/drawings/proposals.json`:
`[{"id", "add": ["File:…", …], "kinds": {"File:…": "Plan|Section|Elevation|Drawing|Sketch|Model"}, "why"}]`.

Take a drawing only if it is all of these:
- of **this** building, not another work by the same architect or a neighbour;
- a real architectural drawing (plan, section, elevation, axonometric, site plan, construction drawing, or a
  sketch by the architect);
- readable at gallery size.

Skip:
- diagrams of something else, maps of a whole city, logos, signs and photos;
- near-duplicates: keep the clearest.

Take at most 4 per building, plans and sections first.

## Rules

- Never edit `site/`, `buildings.js` or `image_choices.json`; the Opus chat applies your proposals after checking
  them.
- Push only to `claude/awesome-clarke-vqongx`, and never open a pull request.
- Be compute-efficient: one Actions run per 200 buildings, and look at each sheet once.
- End with a short report: buildings scanned, buildings with candidates, drawings proposed, and anything odd.
