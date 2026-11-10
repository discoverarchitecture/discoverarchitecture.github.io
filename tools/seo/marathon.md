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
- [x] 11. Write-ups round 2: the next 300 building pages by Google impressions (`todo_4-6.json`). Three Sonnet sessions
      gather facts (`claude/writeups-facts-4/5/6`: session_01MLZuXpm4Fji2w1CbrabzhX, session_01MLZuXn19kLBQvwhPhv2oDQ,
      session_01MLZuXq8Kg6g9SyhLDbSNen). When their `facts_4/5/6.json` land: write (Opus agents, `in_*.json` style), then a
      strict fact-check against the quotes, then the own-words pass (`measure.py`-style copied share under 0.15), then
      `check_writeups.py`, then add to `writeups.json` on `claude/writeups-faqs` (PR #175, still unmerged). Process in
      `tools/writeups/BRIEF.md`, "What actually happened".
- [x] 12. Write-ups round 3: the next 300 pages by Google impressions (`todo_7-9.json` on `claude/writeups-round3`).
      Articles fetched on GitHub Actions (request "7 8 9"), then for each todo: two Opus agents take exact quotes from the
      saved texts (`verify.py`), two write (quotes only, own words), two fact-check, then merge into PR #175 with
      `check_writeups.py` passing, and commit `facts_7-9.json` to `claude/writeups-round3`. Same as todo_6 (scratchpad
      `wu3/` has the tools: `verify.py`, `measure.py`).
- [x] 13. Write-ups round 4: the next 300 indexable pages (`todo_10-12.json` on `claude/writeups-round3`; request
      "10 11 12"). Same steps as round 3 (scratchpad `wu4/` tools: `verify.py`, `measure.py`, `mkin.py`).
- [x] 14. Write-ups round 5: the next 300 indexable pages (`todo_13-15.json` on `claude/writeups-round5`, request
      "13 14 15"). None of the remaining 1,198 indexable pages without a write-up has had a Google impression, so these
      follow the wall's order (best-known first). Same steps as round 4 (scratchpad `wu5/` tools; `merge.py`).
- [x] 15. Write-ups round 6: `todo_16-18.json` on `claude/writeups-round6` (request "16 17 18"), wall order; 898
      indexable pages without a write-up remain before this round. Same steps (scratchpad `wu6/` tools; copy to `wu7/`).
      The round's PR also removes round 5's saved article texts from main (they came in with PR #180).
- [x] 16. Write-ups round 7: `todo_19-21.json` on `claude/writeups-round7` (request "19 20 21"); copy wu7 tools to
      `wu8/`. Give each agent its own scratch folder name (two agents clashed in round 6). Yield is falling (77% round 5,
      58% round 6): the remaining pages are buildings Wikipedia barely covers. Remove articles_19-21 in the round's PR.
- [x] 17. Write-ups round 8, the last: `todo_22-24.json` (298 pages) on `claude/writeups-round8` (request
      "22 23 24"); copy wu8 tools to `wu9/`. After it, every indexable building page has been tried once. Push notes PRs on
      a new branch name (a force-push to reuse a branch name was refused).
- [-] 18. (Stopped by the owner, 7 Nov) Write-ups, second pass: the 627 indexable pages still without a write-up after rounds 1-8 (too little in
      the article the first search found, or the wrong article). `todo_r1-r5.json` on `claude/writeups-retry1`; the
      fetcher now looks each up by Wikidata id, then exact name, then name + city (request "r1 r2 r3 r4 r5"). Same steps
      after that (wu10/). Expect a low yield: many have no English article at all.
- [x] 10. Final report to the owner: what went live, what waits for their decision, numbers to watch.

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
- 7 Nov 02:20 UTC check-in: session 6 gave up (Wikipedia 429s the cloud chats' shared connection; this session too). Now fetched on GitHub Actions instead: `.github/workflows/writeups-articles.yml` + `tools/writeups/fetch_articles.py` on `claude/writeups-facts-6` (request file `articles_request.txt`, first line = todo number) commits `tools/writeups/articles_6/<id>.json` (search candidates + plain text of the top two). Next: from those texts, an agent picks the right article and takes 5-8 exact quotes per building into `facts_6.json` (check every quote is a substring of the saved text), then write, fact-check, own words, merge into PR #175. Three titles need care: The Arnold House, Gobierno Civil de Tarragona, Hamilton City Hall.
- 7 Nov 04:20 UTC check-in: articles_6 landed (100). Two Opus agents take exact quotes from the saved texts into scratchpad wu3/facts_a.json and facts_b.json (verify.py checks every quote is word for word in the saved page). Then: write, fact-check, merge into PR #175, and commit facts_6.json to claude/writeups-facts-6.
- 7 Nov ~06:00 UTC: todo_6 finished (facts from GitHub-fetched articles, quotes verified word for word; 74 written, 69 kept). PR #175 now has **407 building write-ups**, checker passes. Task 11 done. Remaining: owner's approval of PR #175; final report (task 10) by 8 Nov 14:00 UTC.
- 7 Nov 06:15 UTC check-in: round 3 started (task 12); the article fetch for todo_7-9 runs on GitHub Actions.
- 7 Nov 08:20 UTC check-in: round 3 articles landed (300). Six agents take quotes into scratchpad wu4/facts_a..f.json (verify.py). Next: writers, checkers, merge into PR #175, commit facts_7-9.json to claude/writeups-round3.
- 7 Nov ~09:50 UTC: round 3 done: 245 had facts, 242 kept (fact-check: 7-24 changes per batch). PR #175 now has **649 building write-ups**; checker passes; canvas v38 updated. Credit and year disagreements from rounds 2-3 noted in the agents' reports (e.g. Aéro-Habitat, Van Gogh Museum, Singapore Flyer, Secretariat Chandigarh 1953, MUSAC 2005): add to year_conflicts.md.
- 7 Nov 10:15 UTC check-in: 1,536 indexable pages still have no write-up (70 with recent impressions). Round 4 started (task 13); articles fetching on GitHub Actions.
- 7 Nov 12:20 UTC check-in: round 4 articles landed (300, todo_10-12). Six agents take quotes into scratchpad wu5/facts_a..f.json (verify.py). Main now carries PR #177 (data collection's Winnipeg rebuild); the round 4 write-ups go in a new PR on top of it, since PR #175's look is approved and merged.
- 7 Nov ~13:00 UTC: round 4 done and **merged (PR #178)**: 257 more write-ups (262 had facts; 5 under 85 words left out), 906 in all; checker passes (22 flags checked by eye, in reviewed.txt). Credit and year notes in year_conflicts.md (PR #179, merged). Round 5 started: articles for todo_13-15 fetching on GitHub Actions.
- 7 Nov 14:15 UTC check-in: round 5 articles landed (300, todo_13-15). Six agents take quotes into scratchpad wu6/facts_a..f.json. Also merged the outreach roundup list (PR #162, owner's request), after removing one email address the checker had read as a website.
- 7 Nov ~15:05 UTC: round 5 done and **merged (PR #180)**: 228 more write-ups, 1,134 in all; 68 of 300 had too little on Wikipedia (less-known buildings), 4 more under 85 words left out; fact-check made 4-23 corrections per batch; checker passes (25 flags checked by eye). 62 credit/year notes in year_conflicts.md (PR #181, merged). Round 6 started: articles for todo_16-18 fetching.
- 7 Nov 16:15 UTC check-in: round 6 articles landed (300, todo_16-18). Six agents take quotes into scratchpad wu7/facts_a..f.json.
- 7 Nov ~16:45 UTC: round 6 done and **merged (PR #182)**: 166 more write-ups, 1,300 in all; 125 of 300 had too little on Wikipedia, 8 under 85 words, Silver Hut held back (wall data mixes two buildings). 53 credit/year notes (PR #183, merged). Saved article texts for rounds 5-6 removed from main. Round 7 started (todo_19-21).
- 7 Nov 18:15 UTC check-in: round 7 articles landed (300, todo_19-21). Six agents take quotes into scratchpad wu8/facts_a..f.json, each with its own scratch folder.
- 7 Nov ~20:00 UTC: round 7 done and **merged (PR #184)**: 249 more write-ups, 1,549 in all (83% yield: better-documented Western buildings). 46 credit/year notes (PR #185, merged). Round 8 started: the last 298 indexable pages (todo_22-24).
- 7 Nov 20:15 UTC check-in: round 8 articles landed (298, todo_22-24). Six agents take quotes into scratchpad wu9/facts_a..f.json.
- 7 Nov ~21:00 UTC: round 8 done and **merged (PR #186)**: 222 more write-ups, **1,771 in all**; every indexable building page has now been tried once. 67 credit/year/Key-features notes (PR #187, merged). Second pass started (task 18) on the 627 still without one.
- 7 Nov ~22:00 UTC: **marathon stopped early at the owner's request** (save compute). Second-pass fetch cancelled; routine trig_01SP4cYZG3qmjtpp1817PWS2 disabled. Owner asked for indexing instead: the 1,771 write-up pages were already indexable, so the sitemap now dates each (`<lastmod>`) and tools/seo/request_indexing.md lists 50 for Search Console (PR #188, merged). Final report sent in the chat.

# Second run, 10–11 Nov 2026 (owner: "whatever we can do for SEO, keep it running, even if the session ends")

Ends **Wed 11 Nov 2026, 09:00 UTC**. The same routine (trig_01SP4cYZG3qmjtpp1817PWS2) wakes the SEO strategy chat
every 3 hours; each check-in does the first unfinished task below, ticks it, logs one line and pushes. Low compute:
no write-up rounds (the owner dropped the second pass), no new guide (one a week; the next is due about 14 Nov), no
visible change to the site without the owner's yes, no new routines. The last check-in reports to the owner and
disables the routine.

- [x] A. Bing, ChatGPT search, Copilot and DuckDuckGo: send the whole sitemap through IndexNow (a manual run of
      `pages.yml` does it), so the 1,771 write-up pages are re-read. Check the run succeeded.
- [ ] B. Keep the numbers coming: run `analytics.yml` and `search-console.yml` by hand once a day (GitHub only, no
      Claude time); note in the log Google's impressions and clicks for the last days and any change in `indexing.json`.
- [ ] C. Students' missing buildings: from Search Console queries (`search_console/latest.json`) and `search/none/...`
      events (GoatCounter), list the buildings and architects students look for that the wall lacks or ranks badly for.
      Write `tools/seo/missing_buildings.md` and send the list to the data collection chat. No site change.
- [ ] D. Roundup outreach (35 blogs in `tools/outreach/roundups.json`): pick the ones with a real editor and a public
      contact route, and write one short template in `tools/outreach/ROUNDUPS_EMAIL.md` for the owner to approve. Send
      nothing.
- [ ] E. `site/llms.txt`: one plain line that every building page now has a sourced "About the building" paragraph
      (no totals); add the four guides if missing. Small PR; check the live file after the deploy.
- [x] H. (Owner, 10 Nov: "make these now, we can upload later") Write-ups second pass on the 627 indexable pages still
      without one: articles fetching on `claude/writeups-retry1` (request "r1 r2 r3 r4 r5"); then the usual three passes
      (facts with exact quotes, writing, strict fact-check; scratchpad `wu10/`, copy tools from `wu9/`), merge into
      `writeups.json` with `added`, `check_writeups.py` passing, rebuild, and open the pull request **without merging**:
      the owner publishes it. Give each agent its own scratch folder.
- [x] I. (Owner, 10 Nov) Next Studio guide, "How to do an architecture site analysis"
      (`tools/studio_guides/architecture-site-analysis.md`, built by `tools/build_guides.py`): checked at 390 px and
      desktop, day and night; pull request opened **without merging**, for the owner to approve.
- [ ] F. Outreach check (separate routine, Tue 14:30 UTC): replies, bounces, report. Nothing to do here.
- [ ] G. Final report to the owner (short), then disable the routine.

## Log (second run)
- 10 Nov 08:50 UTC: plan written at the owner's request; routine re-enabled every 3 hours until 11 Nov 09:00 UTC.
- 10 Nov ~09:05 UTC: owner asked for the write-ups second pass and the next guide now, published later (tasks H, I). Second-pass fetch restarted; guide draft being written.
- 10 Nov 09:15 UTC: A done (manual deploy run 161 at 08:47 succeeded; IndexNow sent the whole sitemap). I done differently: the owner asked to merge the two site-analysis guides, so the new text went into the existing page (PR #199, not merged; draft #198 closed). Also merged #197: four guides no longer promise a free preview. Next: B.
- 10 Nov ~12:30 UTC: H done: 147 new write-ups (1,918 in all), PR #207, not merged (owner publishes). Also merged with the owner's yes: #202 (photos from Wikimedia, site 949 → 458 MB) and #205 (robots.txt keeps crawlers off /?q= searches).
