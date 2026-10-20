# Hub pages: styles, building types, cities and ideas

Owner's decision, 20 Oct 2026 (SEO strategy chat). Read `CLAUDE.md` first, especially "Rules that never change".

**Why.** The site has a page per building (small searches: "Villa Schreiner") and per architect. The medium-sized
searches where a collection site wins have no page: "brutalist architecture examples", "famous museums architecture",
"architecture in Chicago", "adaptive reuse examples". The buildings are already on the wall; these pages gather them
where Google can rank them. Audience: architecture students worldwide, Western countries the biggest target.

**The list.** `tools/hubs/hubs.json`: 32 hubs (10 styles, 8 building types, 8 cities, 6 ideas). Each has a `kind`
(style, type, city, idea), a `slug`, a `label`, a `match` rule (`movement`, `type`, `city` as "City, Country" the way
`place_full()` in `build_pages.py` writes it, or `concept`), an `h1` and `title_words`. Addresses:
`/styles/<slug>/`, `/types/<slug>/`, `/cities/<slug>/`, `/ideas/<slug>/`.

**Who does what** (owner's rule: Opus only writes; Sonnet does everything else; the SEO strategy chat reviews):

| Step | Who | Branch | Output |
|---|---|---|---|
| A. Sources | Sonnet chat "Hub sources" | `claude/hub-sources` | `tools/hubs/sources.json` |
| B. Introductions | Opus chat "Hub writer" | `claude/hub-intros` | `tools/hubs/results/intros_01.json` |
| C. Pages | Sonnet chat "Hub pages" | `claude/hub-pages` | `tools/hub_pages.py`, `site/hub.css`, the pages |

A and C run at the same time; B starts when A is merged. C builds with placeholder introductions until B lands.
Each chat changes only its own files, opens a pull request to `main`, and does not merge it: the SEO strategy chat
reviews, and the owner sees the pages (phone and computer, day and night) before anything goes live.

---

## A. Sources (Sonnet)

For each of the 32 hubs, collect what the writer needs, from pages free to read: Wikipedia first, then Britannica,
museum, university or city-heritage pages, the Getty Art & Architecture Thesaurus, RIBA, Docomomo, the Society of
Architectural Historians. You can read the web with WebFetch and WebSearch.

Per hub, in `tools/hubs/sources.json` (a list in the order of `hubs.json`):

```json
{
  "slug": "brutalism",
  "facts": [{"claim": "The term was popularised by the critic Reyner Banham in 1955", "source": "https://en.wikipedia.org/wiki/Brutalist_architecture", "quote": "short supporting words from the page"}],
  "overview_links": [{"site": "Wikipedia", "title": "Brutalist architecture", "url": "https://...", "why": "history, key examples", "checked": "2026-10-20"}],
  "key_buildings_on_wall": ["unite-dhabitation", "barbican-estate"]
}
```

- 6 to 10 facts per hub: when and where the style began, who named or led it, what defines it (materials, form,
  structure), how it spread, why students study it. For a city: its architectural history in a few turning points and
  the architects who shaped it. For a building type or idea: what it is, how it developed, what problems it solves.
  Every fact carries its source URL and a few words quoted from that page. No source, no fact.
- 3 to 6 `overview_links` about the whole subject (never one building). Open each with WebFetch; keep only pages that
  load, are not a search page or paywall, and are about this subject. Record the `checked` date.
- `key_buildings_on_wall`: 4 to 8 ids from the wall that the sources name as key examples (search
  `site/data/buildings.js` by name). Never invent an id.
- Global voice: a style is never framed through one country unless the sources do.
- Work in the order of `hubs.json`. Report any hub where sources are thin. Change only `tools/hubs/sources.json` and
  `tools/hubs/progress.md`.

## B. Introductions (Opus)

From `tools/hubs/sources.json` only. In `tools/hubs/results/intros_01.json`, one object per hub:

```json
{"slug": "brutalism", "intro": "110 to 190 words, two short paragraphs.", "facts_used": ["...claims, each from sources.json"], "meta": "one sentence, at most 120 characters, for the page description"}
```

- First sentence answers "what is Brutalism" (or "what makes London's architecture worth studying") at once, with the
  words people search for: "Brutalist architecture", "buildings", "examples".
- Second paragraph: 3 to 5 key examples **from `key_buildings_on_wall`**, named exactly as the wall names them (the page
  links them), what each shows, and what a student can take from it.
- Same voice as the architect write-ups (`tools/architect_bios/BRIEF.md`, "The write-up"): concrete nouns and verbs, one
  idea per sentence, no filler ("iconic", "stunning", "pushes the boundaries"), original wording, no invented facts,
  dates and numbers only from a source, worldwide voice.
- Write the first five (Brutalism, Museums, London, Adaptive reuse, Parametric), stop, and report so the owner can
  approve the voice. Then the rest.

## C. Pages (Sonnet)

Build `tools/hub_pages.py`, called from `tools/build_pages.py` the same way `tools/architect_pages.py` is, and
`site/hub.css`. Start by reading `tools/architect_pages.py` and `site/architect.css`: a hub page is an architect page
(design v24 option B, approved 16 Oct 2026) with these differences, all the owner's:

1. **Layout.** Desktop: two panes that scroll on their own. Left, a third of the screen: the hub name (`h1`), the
   introduction with "Read more", "Read about" links with logos (from `overview_links`), books (from
   `tools/books_seed.json`: books whose tags or buildings match the hub), related hubs (other styles, nearby cities),
   and an **"On the globe"** link. Right: the buildings in **four columns** on a computer (the architect page shows
   two), two on a phone. Phone: one column, introduction first, a red "See the N buildings" button, then the grid.
2. **Order: the buildings with the best data come first** (owner, 20 Oct 2026), not by year. Score each building on
   what its page offers: number of photos (up to 8), a drawing link (WikiArquitectura or ArchDaily, see
   `has_drawings()`), an "About" summary, an architect page, number of links (up to 10, halved), map coordinates.
   Ties go to the more looked-up building (`tools/pageviews.json`). The sort control offers Best first (default) ·
   Year · A to Z · Place.
3. **On the globe.** The link opens the wall's globe with the hub's buildings: add a URL form the wall understands,
   for example `/#map=style:brutalism`, by extending `openFromHash()` in `site/app.js` (it already handles
   `#map=<id>`), so the map fits those buildings. Check it on a phone and a computer.
4. **Tiles** behave as on the architect pages: hover arrows and swipe flip photos, red dots on "worth the swipe" tiles,
   a tap opens the building's popup and closing it returns to the hub page.
5. **Words for Google.** Title `<h1>: <N> buildings with photos & plans` within 60 characters (shorten the way
   `title()` in `build_pages.py` does); counts per hub are allowed. Description: the intro's `meta`. JSON-LD
   `CollectionPage` with an `ItemList` of the first 20 buildings. Canonical address. Add every hub to `sitemap.xml`
   and an index page per kind (`/styles/`, `/types/`, `/cities/`, `/ideas/`).
6. **Links in.** Building pages link their style, type, city and ideas to their hub when one exists (the Details rows
   and "Find more with"); the home page's "About this wall" block lists the hubs. Without links in, Google will not
   find the hubs.
7. Until a hub has an approved introduction, its page says nothing invented: the h1, the buildings and the links only,
   and it is `noindex`.
8. Every rule in `CLAUDE.md` holds: colours only from `site/theme.css`, the slim bar and dock (`TOPBAR`, `DOCK`), day
   and night, square photos and rounded controls, no exact site totals.

Check at 400 px and at desktop width, by day and by night, on Brutalism, London and Adaptive reuse. Take screenshots
(Playwright; Chromium is at `/opt/pw-browsers/chromium`) of each at both widths, put them in
`tools/hubs/screens/`, and list them in the pull request so the owner can see the pages before they go live.

## After launch

The SEO strategy chat reads `search_console/latest.json` on the `analytics-data` branch two and four weeks after
launch: which hubs Google shows, for which searches, and which get clicks. The next batch of hubs (more cities,
style-by-city pages such as "Brutalist buildings in London") follows that evidence, never ahead of it.
