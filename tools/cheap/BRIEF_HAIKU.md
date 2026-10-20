# Judging prepared candidates (cheap-model brief, Haiku experiment)

You get buildings that a script has already looked up. **Do not browse or search the web.** Everything you need is
in two places:
- `tools/cheap/prep.json`: per building, Wikidata facts (`label`, `architect`, `year`, `country`, `located`,
  `coords`, `commons`, `instance`, `sitelinks`), the English Wikipedia lead (`lead`), and up to 7 free photos
  (`photos`: file, rating F/Q/V, size, licence, description `desc`, categories `cats`, `main` = Wikidata's photo).
- `tools/cheap/sheets/sheet_NN.jpg`: the same photos as thumbnails, 8 buildings per sheet in prep order, labelled
  `main`, `p1`…`p6`. Open each sheet once with the Read tool.

For each building, decide and write one entry.

## 1. Keep or skip

The site is a wall for architecture students worldwide (Western countries first). **Keep** a building only if a
student would study it:
- modern, contemporary, parametric, brutalist or regionalist work, or a key historic precedent;
- the lead names an architect and says why it matters (a first, a prize, a famous architect's key work, a named
  movement).

**Skip:**
- Ordinary stadiums, arenas, airports, office towers, hotels, malls and housing, unless the lead gives such a reason.
- Engineering-only bridges.
- Monuments, statues, cities and ruins.
- Anything whose lead is empty or doesn't describe the building.

When in doubt, skip. Write `"status": "skip"` and a short `"why"`.

## 2. Facts, only from prep.json

Use `name` (the English Wikipedia title or label), `by` (architects from `architect`, joined with ", "), `city` (the
first `located` that is a city), `cc` (two-letter country code), and `year`. Then:
- `type`, `movement` and `concepts` (exactly 3): choose only from `tools/illustrate/vocab.json`.
- `features`: one sentence of at most 20 words, saying what makes it worth studying, using only what the lead says.

Never add a fact that isn't in prep.json.

## 3. The main photo, chosen by eye from the sheet

- `photos`: up to 4 files, best first. The first becomes the wall tile.
- It must show the whole building from outside, in daylight, as the clear subject: no people, crowds, signs, cars
  or sculptures as the subject, no night shot, no far skyline, no detail and no other building.
- If no photo passes, use `"status": "unsure"` and `"note": "no main photo"`.
- Prefer rated (F/Q) photos when they are as good.

## Output

Write `tools/cheap/haiku_results.json`: a list in prep order. Each entry has:
- `id` (lower-case words of the name joined by `-`), `qid`, `status` (`photo`, `skip` or `unsure`) and `why`.
- For kept buildings, also `name`, `by`, `city`, `cc`, `year`, `type`, `movement`, `concepts`, `features`,
  `commons_category` (the `commons` value prefixed with `Category:`) and `coords`.
- `photos` as `[{"file", "license", "seen": true}]`.

Don't change any other file, and don't commit. End with one line: kept, skipped, unsure.
