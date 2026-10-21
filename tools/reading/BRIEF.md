# Further reading: 10 to 15 strong links per hub and architect page

Owner's request, 20 Oct 2026: the "Read about" links on the hub pages (styles, types, cities, ideas) and the architect
pages are too thin, mostly Wikipedia. Brutalism, Zaha Hadid or London have been written about at length by credible
publishers; each page should point a student to the best of it. **10 to 15 links per page, free or paid.** Sonnet
chats find and check the links; the SEO strategy chat reviews and merges. Read `CLAUDE.md` first.

## The lists

`tools/reading/todo.json` has five groups: `hubs` (32) and `architects_01` to `architects_04` (190 architects with a
page). Each entry: `key` (`hub:<kind>:<slug>` or `architect:<name>`), `name`, and `have` (links already on the page;
keep the good ones, they count towards the 10 to 15).

## What to produce

One file per group: `tools/reading/<group>.json`, a list in the order of `todo.json`:

```json
{"key": "hub:style:brutalism", "links": [
  {"site": "The Architectural Review", "title": "The page's own title", "url": "https://...",
   "kind": "essay", "paid": false, "why": "eight words at most on what a student gets from it", "checked": "2026-10-20"}
]}
```

`kind` is one of: `overview` (encyclopaedia or reference entry), `essay` (criticism, history, argument), `guide` (a
curated list or tour of buildings), `profile` (an architect or practice profile, works list), `interview`, `obituary`,
`video` (a talk or documentary), `museum` (a collection, archive or exhibition page), `news` (a major feature).

## What makes a good link

- **About the whole subject**: the style, building type, city or idea as a whole, or the architect's whole body of
  work. Never a page about one building (those belong on building pages).
- **Credible publishers**, for example: The Architectural Review, Architects' Journal, Dezeen, ArchDaily (guides,
  profiles, "AD Classics" series pages), Domus, Architectural Record, Architectural Digest, Icon, Wallpaper*, Metropolis,
  Places Journal, Log, e-flux Architecture, The Guardian, The New York Times, The New Yorker, Financial Times, BBC
  Culture, The Atlantic, Smithsonian, Britannica, Smarthistory, Khan Academy, Google Arts & Culture, MoMA, Tate, the V&A,
  the Met, the Getty, the Canadian Centre for Architecture, RIBA, the Twentieth Century Society, Docomomo, the Society of
  Architectural Historians, Open House, the Pritzker Prize, the architect's own practice or foundation, university
  pages, Louisiana Channel and other serious video channels.
- **Not**: content farms and SEO blogs (Rethinking The Future, Novatr, listicle sites with no author), Pinterest,
  Scribd or SlideShare uploads, student essays, shops, AI-written pages, pages behind a sign-up wall with nothing
  visible, pages not in English unless the subject has nothing better (say so in `why`).
- **A mix**: an overview, two or three essays, a guide, a profile or interview, a video and a museum or archive page
  where they exist. At most 3 links from one site and at most 1 from Wikipedia.
- **Western-first, worldwide**: the biggest audience is in the US, UK, Europe, Canada and Australia, so prefer
  publishers read there; but cover the subject worldwide (Brutalism is not only British).
- **Paid is fine** (the owner's words): mark it `"paid": true` (The New York Times, the FT, The Architectural Review's
  subscriber pieces). Keep paid links to at most a third of the list.
- **Order**: most useful to a student first.

## Checking every link

The cloud chats can only open Wikipedia, so links are checked on GitHub's servers (21 Oct 2026):

1. Find candidates with **WebSearch** (and WebFetch for Wikipedia). Take URLs only from real search results or pages
   you opened; never type an address from memory. Aim for 14 to 18 candidates per page, so 10 to 15 survive.
2. Write them to `tools/reading/candidates_<group>.json` (same format as above, without `checked`), commit and push to
   your branch. That runs `.github/workflows/reading-check.yml`, which opens every link with
   `tools/check_reading_links.py` and commits back `tools/reading/<group>.json` (only links that loaded, with `checked`
   and the page's real title) and `tools/reading/check_<group>.md` (every failure and why, and pages under 10).
3. Wait a few minutes, `git pull`, read `check_<group>.md`, add replacements for failures to the candidates file, push
   again. Repeat until every page has 10 to 15, or a small subject honestly has fewer (say why in
   `progress_<group>.md`).

Big publishers that turn away automated visitors (the NYT, the FT, Dezeen and others listed in the script) are kept when
they answer 403, marked `blocked_check`. Never edit `<group>.json` by hand: only the check writes it.

## Working

Each Sonnet chat takes one group, works on its own branch `claude/reading-<group>`, changes only
`tools/reading/<group>.json` and `tools/reading/progress_<group>.md`, commits as it goes, and when the group is done
opens a pull request to `main` titled "Further reading: <group>" and stops. Do not merge; do not touch `site/`.

## Showing them (the "Hub pages" Sonnet chat)

`tools/hub_pages.py` and `tools/architect_pages.py` read `tools/reading/*.json` (merged with the links each page has
now, without duplicates, in the file's order). The left pane shows the first 6 under "Read about …" with the site's
logo (or its first letter), the title and a small "Subscription" mark on paid links, then "See all N" opens the rest in
place, the way "Go deeper" works on building pages. Same look by day and by night, at 400 px and on a computer. Pages
without a reading file keep their current links.
