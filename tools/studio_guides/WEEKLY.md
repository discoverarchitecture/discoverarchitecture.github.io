# Weekly guides (owner, 15 Nov 2026)

The owner asked for two or three new guides a week, published without asking first, with a short note in the SEO
strategy chat each time one goes live. A routine runs this once a week. Publish **two** a week, a third only when a
topic is clearly strong; quality comes first while Google is re-judging the site (CLAUDE.md, 29 Oct 2026).

## Each week

1. **Pick** the top two topics in `TOPICS.md` that pass its test. Before writing, re-read the titles in this folder and
   in `tools/guides/` so the new guide is not a near-duplicate (`CHECKLIST.md`). If a topic overlaps an existing guide,
   improve that guide instead (add a section, set `updated:`) and pick the next topic.
2. **Write** each guide exactly as `CHECKLIST.md` says: 1,100–1,600 words, the first paragraph answers the question,
   British spelling, no invented facts, statistics, names or quotes, made-up examples labelled, pictures only from the
   allowed folders, one or two `/studio/` links, two to four `guide:` links, an FAQ of three questions, and the new slug
   added to the `related:` line of one or two older guides. Studio FGA sentences must not promise a free preview while
   `STUDIO_FLOW` is `paywall` (say "from $6.49", or no price).
3. **Build** with `python3 tools/build_guides.py` (it updates `sitemap.xml` and `llms.txt` too).
4. **Check** each page at 390 px and at desktop width, by day and by night (a Playwright screenshot of each): no
   sideways scroll, every picture loads, no script errors. Read the guide once more, start to finish, as a student
   would; cut anything that doesn't help.
5. **Publish:** commit on a branch `claude/guide-<slug>`, open a pull request, and merge it (no permission needed).
   Wait for the "Deploy site" run to succeed.
6. **Tell the owner** in the chat, one short note per guide: "Published: [title](live link): one line on what it
   gives students." Then move the topic to "Done" in `TOPICS.md` (in the same pull request, or the next).
7. A week later, look at the guide's Search Console queries and `studio/guides/cta/...` clicks, and note anything
   learned at the bottom of `TOPICS.md`.

## Never

- Publish a guide that fails the checklist just to make the weekly number.
- Rewrite or remove an existing guide's address (Google already knows it).
- Add a guide whose main value is search traffic rather than help for a student.
