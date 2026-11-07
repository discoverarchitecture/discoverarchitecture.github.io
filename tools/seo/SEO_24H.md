# Studio FGA: 24-hour SEO push (7 Nov 2026 02:45 IST → **8 Nov 2026 16:45 IST**)

End moved from 02:45 to 16:45 IST on 8 Nov (MAIN chat, 7 Nov 17:15 IST) to make up the ~14 hours lost to the Mac sleeping.

Brief from the FGA Studio MAIN chat. If this chat restarts, read this file first and carry on from **Next**.
Rules: PRs only, never merge or deploy without the owner's OK; don't touch `site/studio/app.js`, `app.css`,
`index.html` (the build chat owns them); no posting, sign-ups or paid APIs; Google-safe only.

Target searches: architecture jury presentation ideas · architecture presentation generator · AI architecture
presentation · architecture jury presentation · A1 sheet layout architecture · architecture board layout ·
architecture presentation board.

## Audit (7 Nov, from 02:45 IST)

What is already good:
- `/studio/`: canonical, description (131 chars), one H1 that says what it is, SoftwareApplication with two Offers,
  FAQPage, VideoObject, BreadcrumbList, Organization; the walkthrough video is `preload="none"` with a poster, so its
  16 MB never blocks the page; the whole offer is in `<noscript>` for AI crawlers. In the sitemap.
- Guides (8, 1,100–1,380 words each): titles ≤ 60, descriptions, canonicals, Article + BreadcrumbList + FAQPage,
  CTA card, closing box, sticky bar, related links. In the sitemap. Images lazy with width and height (no layout shift).
- `robots.txt` welcomes every crawler and names the AI ones. IndexNow already runs after every deploy
  (`tools/indexnow.py` in `pages.yml`), so Bing / ChatGPT search / Copilot hear about changed pages within minutes.
- `/pricing/`: title and description match the offer (Polish $11, Transform $16).

Gaps found:
1. `llms.txt` lists only the one FGA guide, none of the 8 Studio guides (AI assistants read this file). → PR A
2. `sitemap.xml` has no `<lastmod>` anywhere, so search engines can't tell which guides are new. → PR A
3. A new guide only reaches the sitemap after a full `build_pages.py` run (slow, owner's Mac only). → PR A
   (`build_guides.py` now updates the sitemap and llms.txt itself)
4. The FGA guide `/guides/a1-presentation-board/` and `/guides/` don't link to the Studio guides. → PR A
5. Guide Article data uses the generic share image only; their own pictures would help image search. → PR A
6. **For the build chat (files I must not edit):**
   - `/studio/` `<title>` is 75 characters; Google cuts at ~60, so "Jury-Ready Boards" is lost. Suggest
     `AI Architecture Presentation Generator for A1 Boards · Studio FGA` (60) or
     `AI Architecture Presentation Generator: Board + Jury Deck` (57).
   - `/studio/` `<noscript>` links the FGA guide but not `/studio/guides/`; add one line:
     `<p>More guides: <a href="guides/">boards, juries, jury decks and AI tools for architecture students</a>.</p>`
   - `/studio/` loads 9 Google font families in one render-blocking stylesheet; the landing uses ~3 above the fold.
     Trimming the families used only inside the editor would help phone load (LCP).
   - SoftwareApplication could add `"featureList"` (A1 board, 10–15 slide jury deck, PDF, PowerPoint, InDesign export,
     free preview) and `"screenshot": "https://findgreatarchitecture.com/studio/preview-shot.webp"`.

## Done

- 02:49 IST · PR A [#170](https://github.com/discoverarchitecture/discoverarchitecture.github.io/pull/170): sitemap
  lastmod, llms.txt guide list, guide sets cross-linked, guide image data; build_guides.py now updates sitemap + llms.txt.
- 02:53 IST · Guides batch 1 [#172](https://github.com/discoverarchitecture/discoverarchitecture.github.io/pull/172)
  (branch `seo/guides-batch-1`, built on #170): `architecture-jury-presentation-ideas`,
  `architecture-sheet-sizes-a1-a0-24x36`.
- 02:54 IST · Added to #172: `architecture-concept-diagram-ideas`.
- Mac asleep about 03:00–08:45 and again about 08:50–17:05 IST; run paused both times.
- 17:07 IST · Added to #172: `how-to-present-site-analysis`, `tools/studio_guides/CHECKLIST.md` (the builder skips it).
- 17:08 IST · Added to #172: `architecture-presentation-board-templates`.
- 17:09 IST · Added to #172: the AI tools roundup gains "How to judge an AI architecture presentation generator" (a seven-question checklist, Studio FGA's own answers beside it) and an FAQ; `updated: 2026-11-07`.
- 17:11 IST · Off-site ideas PR [#176](https://github.com/discoverarchitecture/discoverarchitecture.github.io/pull/176) (branch `seo/offsite-ideas`, from main): `tools/seo/OFFSITE_IDEAS.md`, drafts only.
- 17:58 IST · Added to #172: `what-architecture-jurors-look-for` (a juror's ten questions, each with a self-check). Thesis structure dropped: the slides guide already has a thesis section, so a new page would be a near-copy.
- 17:58 IST · Added to #172: guides index description names the new topics; updated guides show "updated <date>" in the byline.

## Next

1. New guides, added to batch PRs (each guide's own commit), in this order (search → guide):
   - (skipped: "how to make a presentation board step by step" would near-duplicate `/guides/a1-presentation-board/`
     and `how-to-lay-out-an-a1-architecture-board`; strengthen those instead)
   - (list done; further ideas only if clearly distinct: "architecture portfolio layout" is covered by the portfolio
     guide; "architecture model photography" and "how to render for a jury" are candidates)
2. Next guide: how to photograph architecture models for a jury board (`architecture-model-photography`), using the
   sample's model photos before and after (raw sheet 3 → board/model-*.jpg).
3. Deferred, with reasons: a site-wide footer link to `/studio/guides/` needs a full `build_pages.py` run that rewrites
   every page and would collide with the other open PRs; the A1 guide (already in every footer) now links the Studio
   guides instead (#170). `/pricing/` structured data: skipped, low value (prices already in /studio/'s data).
4. After the owner merges: check the live pages, sitemap and llms.txt; re-run the IndexNow job if the deploy failed.
