# Checking documentary candidates

For the chats and subagents that sift `tools/films_candidates.json` into batches for `tools/films_batch.py add`.
High-volume first-pass work follows this brief; the Documentaries chat checks every batch by eye before it is added,
and nothing reaches `site/` without that check.

## The one rule

**No invented facts.** Every fact comes from a source you can quote. If a director, year, runtime or language has no
source in front of you, leave it empty. An empty field is right; a guessed one is a defect that reaches students.
This is CLAUDE.md's rule, and it is why every entry carries `sources[]` with a url and the exact words relied on.

## What counts

- **feature** — a documentary film about architecture, an architect, a building, a city or how buildings are made.
- **series** — a documentary series (for example *Abstract*, BBC architecture series).
- **episode** — one episode worth naming on its own.
- **lecture** — a full-length talk or lecture, free to watch, from a university or institution channel.

Include a film when architecture is its **subject**, not its backdrop. A film about a city's politics that happens to
show buildings is out. A film about a painter who designed one house is out. If you cannot tell from the sources in
front of you, reject it and say why: a thin "maybe" costs more to undo later than it saves now.

Always out: fiction and drama, trailers and clips, promotional films made by a practice about itself, news segments,
anything under about 20 minutes unless it is a lecture, and anything whose only source is a sales page.

## The genres (exactly these seven)

Portrait of an architect · Building story · City & urbanism · Housing & social · Design process ·
Movement & history · Landscape & sustainability

One or two per film. `films_batch.py` refuses any other word.

## Linking into the site

These make the film findable from the rest of the wall, so they must use the wall's own vocabulary:

- `about.architects[]` — names exactly as the wall writes them. A name the wall does not use is refused.
- `about.buildings[]` — wall building ids.
- `movements[]`, `topics[]` — movements, building types, cities and ideas as the wall spells them.

Leave a link out rather than bending a name to fit. A wrong link is worse than a missing one.

## Ratings and where to watch

- Only **TMDB**'s score is a number, with its `checked` date. IMDb and Letterboxd are links with no number, because
  IMDb's data is licensed for non-commercial use and this site may carry ads later.
- `watch[]`: provider, country, type (`free`, `subscription`, `rent`, `buy`), url, and a `checked` date. A **free**
  link always needs that date, because free links go stale faster than any other fact here.

## What a batch looks like

```json
{"add": [{"key": "<candidate key>", "title": "My Architect", "year": 2003, "kind": "feature",
          "genres": ["Portrait of an architect"], "director": ["Nathaniel Kahn"], "runtime_min": 116,
          "language": "English", "summary": "<one sourced line, under 200 characters>",
          "about": {"architects": ["Louis Kahn"], "buildings": []},
          "sources": [{"url": "https://…", "quote": "<the words the facts come from>"}]}],
 "reject": ["<candidate key>", "…"]}
```

Run `python3 tools/films_batch.py add batch.json`. It refuses the **whole** batch if anything is wrong, and names
every fault, so fix them all and run it again.

## Quality watch

CLAUDE.md's rule applies: warn before quality drops, not after. Report these each round, and stop and ask if a stop
level is passed.

| | warn | stop |
|---|---|---|
| Candidates rejected as not really about architecture | 40% | 60% |
| Films with no free or streaming link anywhere | 35% | 50% |
| Facts failing the source check | 3% | 6% |
| Films with no architect, building or movement link | 30% | 45% |

A steady rise across rounds is a warning too, even below these levels.
