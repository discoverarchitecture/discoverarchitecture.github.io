# FGA Studio: search plan

SEO strategy chat, 29 Oct 2026, at the owner's request ("as soon as we launch, Google has to pick it up rightly; when
somebody searches for presentation boards, how are we seen and what is written"). Product copy changes need the owner's
yes; the Studio chat makes changes inside `site/studio/`. Western-first, worldwide (CLAUDE.md).

## The honest starting point

- **Google is re-judging the whole domain** after it dropped most of the site on 25 Oct (see CLAUDE.md, "Which building
  pages Google may index"). No manual action. `/studio/` shares that verdict, so expect Google to be slow for 6–8
  weeks whatever we do on the page. **Bing, ChatGPT search, Copilot and DuckDuckGo are unaffected**: IndexNow tells
  Bing within minutes of each deploy, so those are the first search engines to bring sign-ups.
- **No search volumes yet.** Free sources give none for these phrases. The owner can read them in Google Keyword Planner
  (free inside a Google Ads account; prompt at the end). The order below is by intent, from what ranks today.

## Who ranks today and what they offer

| Search | Ranks today | What they sell | Our opening |
|---|---|---|---|
| architecture presentation board (tips, examples, layout) | First In Architecture, Archisoup, illustrarch, ArchDaily (competition boards), Portfoliobox | Articles, Udemy courses, paid templates | A guide written by an architect, with a real before/after board |
| architecture board template (A1, Canva, InDesign) | Etsy, Gumroad sellers ($2–17), illustrarch | Static templates you fill in yourself | A board made **from your own drawings**, editable |
| AI architecture presentation / AI presentation board | illustrarch tool lists; general AI deck tools (Beautiful.ai, Gamma); Morpholio Board | Generic slide makers, or a layout app | The only one made for an architecture jury: A1 board **and** jury deck |
| jury presentation tips, crit tips | illustrarch, student blogs, Reddit | Advice | Guide + tool |

## Keyword map (one page per intent)

| Intent | Phrases (US/UK spelling both) | Page |
|---|---|---|
| Buy / try the tool | AI architecture presentation board, architecture presentation board generator, make an architecture board from my drawings, jury presentation maker | `/studio/` |
| Price | FGA Studio price, architecture presentation board cost | `/pricing/` |
| Learn (biggest, steadiest) | how to make an architecture presentation board, A1 presentation board layout, architecture board layout ideas, presentation board examples | Guide 1 |
| Learn | architecture jury presentation tips, how to present at a crit, final review tips | Guide 2 |
| Template seekers | architecture board template A1, A1 sheet layout template, InDesign architecture board template | Guide 3 (free layout grids to download, then Studio) |
| Deck | architecture jury presentation PowerPoint, thesis presentation architecture slides | Guide 4 |
| Portfolio (later) | architecture portfolio board, portfolio page layout | Guide 5, after launch |

## /studio/ on-page (proposal for the owner; the Studio chat implements)

- **Title (≤ 60):** `AI Architecture Presentation Boards from Your Drawings · FGA Studio`
- **Description (≤ 155):** `Upload your plans, sections and sketches. Get a jury-ready A1 board and a 10–15 slide deck, editable, from $11. Free preview first.`
- **H1:** keep the big headline as it looks, but make the heading text say what it is, e.g. a small line above it as the
  H1: "AI architecture presentation boards from your own drawings", and "Design the building. Skip the all-nighter." as
  the visual headline (same look, different tag). Google reads the H1 to decide what the page is.
- **H2s, in order:** How it works (upload · answer · preview · pay once) · What you get (A1 board, jury deck, PDF,
  PowerPoint, InDesign) · Before and after (the real sample project) · Pricing (Polish $11 · Transform $16) · FAQ.
- **Words students use, somewhere on the page:** A1 board, presentation board, jury, crit, final review, precedent study,
  plans, sections, elevations, renders, PowerPoint, InDesign, portfolio.
- **Structured data:** `SoftwareApplication` (applicationCategory DesignApplication, operatingSystem Web, offers: two
  `Offer`s, 11 and 16 USD, each with its name), `FAQPage` from the visible FAQ (Google no longer shows FAQ boxes for
  most sites, but Bing and AI answers read it), `BreadcrumbList` (Find Great Architecture › Studio), `Organization`
  with the logo. Only prices that the page and `/pricing/` actually show.
- **Share image:** a before/after board at 1200 × 630 with the words "From your drawings to a jury-ready board".
- **Must match everywhere:** `/pricing/`, `/terms/` Part 2 and `/refunds/` still describe credit packs of $5–25
  (CLAUDE.md, Money). If the offer is now Polish $11 / Transform $16 per board, those pages and the structured data have
  to say the same thing before launch, or Google and payment providers see a mismatch. **Owner to confirm.**

## Indexing

- `/studio/` is in `sitemap.xml`, canonical and indexable. `/pricing/`, `/terms/`, `/privacy/`, `/refunds/` and
  `/contact/` were not in the sitemap: added on 29 Oct (this change).
- Every page already links to Studio twice (the AI button in the top bar and the footer line).
- "Make a board for your case study" on building pages: a visible change, so it goes on the design canvas first.
- On launch day: Search Console › URL inspection › Request indexing for `/studio/` and `/pricing/`; the deploy tells
  Bing through IndexNow on its own.

## Content plan (guides)

Five guides at `/guides/<slug>/`, each written from the owner's own training (CEPT University, Ahmedabad), with the
real sample project before and after, and a short "Make yours with FGA Studio" at the end. **One a week, not all at once**,
and only when each is genuinely better than what ranks today (the site is being re-judged; thin pages hurt).

1. How to make an architecture presentation board (A1): layout, hierarchy, what goes where, with the sample board.
2. Architecture jury presentation tips: how to tell the story in 3 minutes, what juries look at first.
3. A1 board layout grids: free downloadable grids (PDF/InDesign) in exchange for nothing; the best link-earner.
4. The jury deck: 10–15 slides that follow the board.
5. Portfolio pages from your boards (after launch).

## Measurement

- Search Console: queries and clicks for `/studio/`, `/pricing/` and `/guides/`. The daily fetch is paused (owner,
  28 Oct); resume it at launch ("resume the Search Console fetch").
- GoatCounter already counts `studio/ai-button`, `studio/ai-link`, `studio/signup`. The app should add
  `studio/preview` (free preview shown), `studio/checkout` (pay pressed) and `studio/paid/<polish|transform>`
  (payment confirmed), numbers only, so the funnel from search to sale is visible.
- Every outside link carries `?ref=<channel>` (directories, Reddit, Instagram) so sales can be traced to a channel.

## Keyword Planner prompt (owner, Claude in Chrome)

> Open Google Keyword Planner (ads.google.com › Tools › Keyword Planner › Get search volume and forecasts). Enter these
> keywords, one per line: architecture presentation board, architectural presentation board, a1 presentation board,
> architecture board template, architecture presentation board template, architecture board layout, how to make a
> presentation board architecture, architecture jury presentation, ai architecture presentation, ai presentation board,
> architecture portfolio board, architecture thesis presentation. Set locations to United States, United Kingdom,
> Canada, Australia, Germany, and language English. Tell me each keyword's average monthly searches, competition and
> top-of-page bid range. Change nothing else and create no campaign.
