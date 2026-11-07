# Roundup articles: "best websites for architecture students"

SEO strategy chat, 6 Nov 2026 (owner's go-ahead for weekend work). Read `CLAUDE.md` and `tools/outreach/BRIEF.md`
first; the same rules apply: **the owner sends every message, nobody else contacts anyone, and no email address goes
into the repository.**

**Why:** articles that list useful websites for architecture students (resource lists, "best free tools", "where to find
precedents and images") are read by students and by AI assistants. A mention there brings visitors and the outside
links Google and ChatGPT trust.

**Find about 30**, Western-first (US, UK, Europe, Canada, Australia): blog posts, university pages, magazine lists and
newsletters that list websites or tools for architecture students, updated since 2023, with a named author or a way to
suggest a resource. Search with WebSearch: "best websites for architecture students", "architecture student
resources", "free architecture precedent websites", "architecture image sites for students", "websites every
architecture student should know", and similar. Take addresses only from real search results.

Write `tools/outreach/candidates_roundups.json` (same checker as the library guides):

```json
{"school": "Publisher or site name", "country": "US", "guide": "Article title", "url": "https://...",
 "section": "the list it would join", "lists_sites": ["ArchDaily", "Archinect"], "librarian": "Author name if shown",
 "profile": "the author's or site's contact page, if any", "updated": "2025-03-01", "why": "eight words at most"}
```

Push to branch `claude/outreach-roundups`; `.github/workflows/outreach-check.yml` checks every page and commits
`tools/outreach/roundups.json` and `check_roundups.md`. Replace failures until about 30 good ones pass. Keep notes in
`tools/outreach/progress_roundups.md`, then open a pull request "Outreach: roundup articles" and stop. Don't merge.
