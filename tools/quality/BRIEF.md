# Better photos from Commons' best-rated files (Sonnet, checked by Opus)

The owner wants better photos on the wall (19 Oct 2026). Wikimedia Commons rates its best photos as
**Featured pictures**, **Quality images** and **Valued images**. Many buildings on the wall have rated photos on
Commons that are not in their gallery, or a main photo (the wall tile) that is weaker than a rated one. This job
finds those and proposes swaps; the Opus data-collection chat checks every proposal by eye before anything changes.

Read `CLAUDE.md` first (free images only; the main-photo rule; Actions for network jobs).

## 1. The tool: `tools/quality_photos.py` (runs on Actions)

For each building in `site/data/buildings.js` (`--ids a,b,c` or `--first N` by `n`, `--offset K`):

- Look in its Commons category (`commons`), its sub-folders one level down, and Wikidata's main image (P18) if it has
  a `qid`. Reuse helpers from `tools/fetch_images.py` (`api`, `members`, `infos`, `strip`, `OK_LICENSE`, the size
  limits) rather than rewriting them.
- Keep files whose `extmetadata.Assessments` says featured, quality or valued (or POTY), whose licence passes
  `OK_LICENSE` (PD, CC0, CC BY, CC BY-SA; never NC or ND), at least 1,600 px on the long side, JPEG or PNG.
- **Skip** files already in the building's gallery, files in `skip` lists in `tools/image_choices.json`, files
  removed in `tools/image_review.json`, and files whose description, name or categories point to people, events,
  artworks, signs, night, or another named building (reuse `JUNK` and `SURROUNDINGS`).
- **Guard against wrong categories**: on 15 Oct we found buildings whose `commons` field was a same-name category for
  another building. Keep a candidate only if its own categories or description name this building or its city, or
  the file sits directly in the building's category.
- Write `tools/quality/candidates.json`: `{id: {"lead": current lead file, "lead_rated": bool, "found": [{file,
  rating, w, h, license, desc (first 120 chars), cats (first 6)}]}}`, only for buildings where something was found.
- Make **contact sheets** with Pillow on Actions: `tools/quality/sheets/sheet_NN.jpg`, 10 buildings per sheet, one
  row each: label `index id — name (place)`, then the current main photo, a thin gap, then up to 6 rated candidates
  (330 px thumbnails from `thumburl`, each labelled `c1`…`c6` and its rating letter F/Q/V). Keep each sheet under
  about 400 KB.
- Pace requests (sleeps, retries on 429/5xx) and use a User-Agent like `fetch_images.py`'s. Never put any email or
  personal name in requests or files.

Trigger it with `tools/run_request.txt` (first line `python -u tools/quality_photos.py --first 300`), commit and
push to `claude/awesome-clarke-vqongx`. Wait with a background loop on `git fetch` until the latest commit starts
with "Tool results". Note: GitHub ignores the trigger when a push changes more than 300 files, so push the trigger in
a small commit of its own.

## 2. First pass by eye (you)

Open every sheet. For each building write a decision to `tools/quality/proposals_pilot.json`:

```json
{"id": "fallingwater", "new_lead": "File:… or null", "add": ["File:…"], "why": "short"}
```

- `new_lead` only when a candidate is clearly better as the wall tile than the current one: the outside of this
  building, in daylight, the whole building as the clear subject, no people as the subject, not a far view or a
  night shot, not a detail, not another building. When in doubt, null.
- `add`: up to 3 rated candidates that are good gallery photos of this building (interiors and details are welcome
  here, as long as they clearly show this building).
- Leave out buildings where nothing is worth taking.

## Rules

- Change nothing under `site/`, and never edit `buildings.js` or `image_choices.json`; the Opus chat applies the
  proposals.
- Push only to `claude/awesome-clarke-vqongx`. Never open a pull request.
- Be compute-efficient: one Actions run for the pilot, a short look per row.
- End with a short report: buildings scanned, buildings with rated candidates, proposed new leads, proposed
  additions, and anything odd (wrong categories spotted, tool problems).
