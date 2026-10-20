# Art Institute of Chicago drawings for the most-studied buildings (Sonnet, checked by Opus)

The owner allowed one source besides Commons (20 Oct 2026): the Art Institute of Chicago's public-domain (CC0)
works, mainly architectural drawings. They must be credited "Art Institute of Chicago" and linked to the artwork's
page. The museum holds large architecture collections: Chicago School, Sullivan, Wright, Mies, Burnham, Goff and
many more.

## 1. The tool: `tools/aic_scan.py` (runs on GitHub Actions)

- **Search:** for each id in `tools/top1000.txt` (`--first N`, `--offset K`), and for every other building on the
  wall in the USA, look up the museum's open API (no key needed):
  `https://api.artic.edu/api/v1/artworks/search?q=<building name>&query[term][is_public_domain]=true&fields=id,title,artist_title,date_display,classification_title,department_title,image_id,thumbnail,is_public_domain&limit=15`
  - Send a polite User-Agent with no personal data.
  - Pause about 1 s between requests.
- **Keep a hit only if all of these hold:**
  - `is_public_domain` is true and `image_id` is set;
  - its classification or department says architectural drawing, architecture, drawing, print, photograph or
    model;
  - its title names the building, or names the architect together with a word from the building's name.
- **Write `tools/aic/candidates.json`:** `{id: [{aic_id, title, artist, date, classification, image_id,
  page: "https://www.artic.edu/artworks/<aic_id>", iiif: "https://www.artic.edu/iiif/2/<image_id>/full/843,/0/default.jpg"}]}`,
  at most 6 per building.
- **Make contact sheets `tools/aic/sheets/sheet_NN.jpg`:** like `tools/drawings/BRIEF.md`'s — 8 buildings a sheet,
  the building's current main photo first, then candidates `a1`…`a6` from the IIIF image at 400 px, each sheet
  under about 450 KB.

Run it with `tools/run_request.txt` (`python -u tools/aic_scan.py --first 1000`), in a small commit of its own. The
Actions queue is shared, so wait your turn. Wait with a background `git fetch` loop until the newest commit starts
with "Tool results".

## 2. First check by eye (you)

Write `tools/aic/proposals.json`: `[{"id", "add": [aic_id, …], "kinds": {aic_id: "Plan|Section|Elevation|Drawing|Sketch|Model|Exterior"}, "why"}]`.

Take a work only if it is all of these:
- of **this** building, not a different project by the same architect and not an unbuilt scheme of another name;
- readable at gallery size.

Drawings come first. A historic photograph is fine if it clearly shows the building. Take at most 4 per building.

## Rules

- Never edit `site/`, `buildings.js` or `image_choices.json`; the Opus chat adds the accepted works after checking
  them.
- Push only to `claude/awesome-clarke-vqongx` (always `git pull --no-rebase` first, because other chats push there
  too), and never open a pull request.
- End with a short report: buildings searched, buildings with hits, works proposed, and anything odd.
