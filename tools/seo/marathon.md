# SEO marathon, 6–8 Nov 2026

The owner's request (6 Nov 2026, evening): use the available compute for about 40 hours to make the site better for
search (real text, articles, better pages), and carry on by itself after a usage limit resets. The SEO strategy chat
runs it. A routine wakes that session every 2 hours (routine `trig_01SP4cYZG3qmjtpp1817PWS2`, 13 past every second hour UTC); each check-in reads this file,
continues the first unfinished task, ticks what it finished, and pushes. **Ends Sun 8 Nov 2026, 14:00 UTC**: the last
check-in reports to the owner and disables the routine.

Rules that hold the whole time (CLAUDE.md):
- Nothing new and visual goes live without a design the owner has approved. Reusing an approved look (the guide page,
  v36; the building page's About section; the hub page) is fine; anything else goes on the canvas and waits.
- Every change is checked at about 400 px and at desktop width, by day and by night, before its pull request.
- No invented facts: every sentence in a write-up, FAQ or guide is backed by a source in its results file.
- Global audience, Western-first; never exact totals of buildings.
- Google is re-judging the site (since 25 Oct): don't add building pages in bulk; add an id to
  `tools/seo/index_keep.txt` only when its page gains real written text of its own.
- Each piece of work goes through its own small pull request and is checked on the live site after merging.

## Tasks, in order

- [x] Search, rebuilt (canvas v37), merged 6 Nov (PR #169).
- [x] 1. Search suggestions on every other page (building, architect, hub, guide, A–Z, policy pages): a small search
      index loaded the first time the field is used, the same box as on the wall; a building opens its own page, an
      architect their page, a style or type its hub or the wall's filter, "See all" the wall's search.
- [x] 2. Count searches that find nothing (`search/none/<words>`, letters and digits only, at most 40 characters, once a
      visit) so we learn what students want and the wall lacks; one line on the privacy page.
- [ ] 3. Building write-ups for the 300 most-seen building pages: wait for `facts_1/2/3.json` from the three Sonnet
      sessions (branches `claude/writeups-facts-1/2/3`), then write 90–140 words each from those facts only
      (`tools/writeups/BRIEF.md`), shown in the building page's About section.
- [ ] 4. Hub FAQs: review `claude/hub-faqs` (`tools/hubs/results/faq_01.json`), then show 3–4 questions on each hub
      page in the guide's FAQ look, with FAQPage data.
- [x] 5. Hub introductions for the hubs that have none (those pages are noindex until they do).
- [ ] 6. Guide 2: How to do an architecture precedent study (case study): the question students ask most that the
      wall answers; links into the wall, the hubs and the architect pages.
- [ ] 7. Guide 3: Architecture jury presentation tips.
- [ ] 8. Guide 4: The jury deck (10–15 slides that follow the board).
- [ ] 9. Internal links: every guide linked from the hubs it mentions and from the home page's About block; `llms.txt`
      and the sitemap carry the new pages.
- [ ] 11. Write-ups round 2: the next 300 building pages by Google impressions (`todo_4-6.json`). Three Sonnet sessions
      gather facts (`claude/writeups-facts-4/5/6`: session_01MLZuXpm4Fji2w1CbrabzhX, session_01MLZuXn19kLBQvwhPhv2oDQ,
      session_01MLZuXq8Kg6g9SyhLDbSNen). When their `facts_4/5/6.json` land: write (Opus agents, `in_*.json` style), then a
      strict fact-check against the quotes, then the own-words pass (`measure.py`-style copied share under 0.15), then
      `check_writeups.py`, then add to `writeups.json` on `claude/writeups-faqs` (PR #175, still unmerged). Process in
      `tools/writeups/BRIEF.md`, "What actually happened".
- [ ] 10. Final report to the owner: what went live, what waits for their decision, numbers to watch.

## Log

- 6 Nov 21:15 UTC: plan written; search merged.
- 6 Nov 22:40 UTC: tasks 1 and 2 merged (PR #173): the box on every page, and search/none counting.
- 7 Nov 00:30 UTC: task 5 needs nothing (all 32 hubs already have introductions). Tasks 3, 4, 6, 7, 8 and 9 are built on
  branch `claude/writeups-faqs` and shown on the canvas as v38, **waiting for the owner's approval** (the briefs promised
  it): 185 write-ups (4 Opus writers, then 2 strict fact-checkers; the 115 thin ones left out), hub questions on all 32
  hubs with FAQPage data, guides 2-4 (precedent study, jury presentation, jury deck), guides listed in llms.txt and the
  home page's text. Next: finish the fact-check, merge `final_*.json` into `tools/writeups/results/writeups.json`, run
  `tools/writeups/check_writeups.py`, rebuild, re-shoot v38, open the PR (unmerged).
- 6 Nov 22:05 UTC (the clock above is UTC): tasks 3, 4, 6, 7, 8, 9 finished and in **PR #175, unmerged, waiting for the
  owner** (canvas v38 refreshed). 185 write-ups went through write, strict fact-check (made-up details removed), and own
  words (under 15% copied; was up to 73%); hub answers rewritten so they don't repeat the intro. Round 2 started (task 11).
- 6 Nov 22:15 UTC check-in: tasks 3-9 wait for the owner (PR #175). Task 11: facts_4 has 30 of 100 (2 thin); facts_5 and facts_6 not pushed yet. Writing starts when a whole file lands.
- 7 Nov 00:20 UTC check-in: facts_4 (100, 21 thin) and facts_5 (100, 20 thin) landed; 159 being written by four Opus writers (scratchpad wu2/, quotes only and own words from the start), fact-check to follow. Session 6 had stopped on a Wikipedia rate limit (0 of 100); asked to resume slowly.
- 7 Nov ~01:30 UTC: round 2 written, fact-checked (light: 1-17 changes per batch) and merged into PR #175: 153 more, 338 write-ups in all; six under 85 words left out; checker passes; canvas v38 updated. facts_6 (session 6) still pending after the rate limit; when it lands, do the same for it.
