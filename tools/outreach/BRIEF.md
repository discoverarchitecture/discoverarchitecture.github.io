# Library guides: getting Find Great Architecture onto university research guides

SEO strategy chat, 23 Oct 2026. Google trusts a site more when respected sites link to it. University libraries keep
"research guides" (often on LibGuides, `*.libguides.com` or `guides.<university>.edu`) that list free resources for
architecture students: image collections, precedent databases, building directories. A link from one of these is worth
more than hundreds of ordinary ones, and the site fits them exactly: free, credited, reusable photos of real buildings,
with links to drawings and further reading. **The owner sends every email; nobody else contacts a librarian.**
Read `CLAUDE.md` first.

## What to find

About **40 architecture research guides** at universities that teach architecture, **Western-first**: roughly 15 US,
8 UK, 5 Canada, 5 Australia and New Zealand, 5 Ireland and continental Europe (English-language guides), and a few
elsewhere if strong. Prefer, in order:

1. Guides with a section for **images, image databases or free web resources** for architecture (or art and
   architecture, or architectural history). That is where the site belongs.
2. Guides that already list sites like ArchDaily, Great Buildings, WikiArquitectura, Archnet, SAH Archipedia, Wikimedia
   Commons or Artstor's open collections: they show the librarian lists outside sites.
3. Schools with large architecture programmes (accredited professional degrees: NAAB, RIBA, CACB, AACA).

Not: guides behind a sign-in, guides last updated before 2022 (check the "Last updated" line), pages that only list the
library's paid databases with no outside websites, school web pages that are not library guides.

## What to produce

`tools/outreach/candidates_libguides.json`, a list, best first:

```json
{"school": "University of X", "country": "US", "guide": "Architecture: Images", "url": "https://...",
 "section": "the guide's own name for the part the site would go in, e.g. 'Free image sites'",
 "lists_sites": ["ArchDaily", "Great Buildings"], "librarian": "Name as the guide shows it",
 "profile": "https://... the librarian's profile or contact page on the guide, if there is one",
 "updated": "2026-05-12", "why": "eight words at most on why this guide fits"}
```

**Do not write any email address into the repository** (it is public). The librarian's name and a link to their profile
or contact page are enough; the owner finds the address there when sending. Leave `librarian` empty when the guide
names nobody.

## Checking every guide

The cloud chats can only open Wikipedia, so guides are checked on GitHub's servers, the same way as the reading links:

1. Find guides with **WebSearch** (for example `architecture images site:libguides.com`, `architecture research guide
   "image databases"`, `"architecture" "free image" libguide`, a school's name plus `architecture library guide`).
   Take URLs only from real search results; never type an address from memory. Aim for 50 to 60 candidates, so 40
   survive.
2. Write them to `tools/outreach/candidates_libguides.json`, commit and push to your branch
   `claude/outreach-libguides`. That runs `.github/workflows/outreach-check.yml`, which opens every guide with
   `tools/check_outreach.py` and commits back `tools/outreach/libguides.json` (guides that loaded, with the page's real
   title, whether it mentions architecture, the outside sites it links to, whether it already links to us, and the
   librarian's profile link if the page shows one) and `tools/outreach/check_libguides.md` (failures and why).
3. Wait a few minutes, `git pull`, read the check, replace failures and weak guides (no outside sites at all, not about
   architecture), push again, until about 40 good guides remain.

## Working

Work on branch `claude/outreach-libguides`; change only `tools/outreach/candidates_libguides.json` and
`tools/outreach/progress_libguides.md` (what you searched, what you rejected and why). When about 40 good guides pass
the check, open a pull request to `main` titled "Outreach: library guides" and stop. Do not merge; do not touch `site/`;
do not contact anyone.
