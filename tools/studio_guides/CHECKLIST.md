# Writing a new Studio FGA guide: checklist

For any chat (or person) adding a guide to `/studio/guides/`. Read the top of `tools/build_guides.py` for the file format.

## Before writing

- [ ] **One search question per guide.** Write the phrase a student types (e.g. "architecture jury presentation ideas")
      at the top of your notes. Check it in Google from a US or UK point of view, not only India (CLAUDE.md: global,
      Western-first).
- [ ] **No near-duplicates.** Read the titles in `tools/studio_guides/*.md` and `tools/guides/*.json`. If an existing
      guide already answers the question, improve that guide instead (add a section, set `updated:`). Google treats
      near-copies as thin pages, and the site is being re-judged (CLAUDE.md, 29 Oct 2026).
- [ ] **Better than what ranks today.** Open the top five results. Ours must be more useful: clearer steps, real
      numbers that are true, our own pictures.

## Writing

- [ ] 1,100–1,600 words, an architect's plain voice, short paragraphs, British spelling as in the other guides.
- [ ] First paragraph answers the question in three or four sentences (it is shown large, and AI assistants quote it).
- [ ] No invented statistics, names, schools, quotes or testimonials. Made-up examples are labelled as examples.
- [ ] Facts that can be checked (sizes, standards, tools) are checked. Name tools only for what they really do, and
      say Studio FGA is ours when it appears.
- [ ] One or two in-text links to `/studio/` (becomes `?ref=guides-text`), placed where the tool genuinely helps;
      the CTA card, closing box and bottom bar are added by the builder, so don't add more.
- [ ] Two to four `guide:` links to related guides in the text, plus `related:` (3–4 slugs). Add the new slug to the
      `related:` line of one or two older guides so it gets links in.
- [ ] Links to building pages on the wall only if the id is in `tools/seo/index_keep.txt` and the page exists.
- [ ] An `## FAQ` with three questions people really ask, each answered in two or three sentences.

## Pictures

- [ ] Only from `site/studio/sample/` (the Law Garden sample, used with the student's permission),
      `site/studio/sample/gallery/` and `site/studio/preview-shot.webp`. Never `site/studio/board.webp`, never
      `studio/references/`. The builder refuses other paths.
- [ ] Gallery boards k1–k4 are **test projects based on famous buildings, never student work**: say so in the
      caption, and copy the photo credit and licence links from `site/studio/sample/gallery/credits.json`.
- [ ] Alt text says what the picture shows; the caption says honestly what it is and who made it.
- [ ] Very wide pictures (more than 3 : 1) go in a figure of their own, not side by side, or they shrink to a strip
      on a phone.

## Building and checking

- [ ] `python3 tools/build_guides.py` (it also updates `site/sitemap.xml` with dates and the guide list in
      `site/llms.txt`).
- [ ] `seo_title` ≤ 60 characters (the builder adds " · Studio FGA" only when the result stays ≤ 60); description
      ≤ 160 characters.
- [ ] Look at the page at about 400 px and at desktop width: no sideways scroll, pictures load, the bottom bar
      doesn't hide anything important.
- [ ] `published:` is today's date; when you change a guide a lot later, add `updated:`.
- [ ] Commit the `.md`, the generated HTML, `sitemap.xml` and `llms.txt` together; open a pull request. The owner
      merges. The deploy pings Bing through IndexNow on its own.

## After it's live

- [ ] Search Console › URL inspection › Request indexing (owner, by hand).
- [ ] A week later, check GoatCounter for `studio/guides/cta/…/<slug>` clicks and Search Console for the page's
      queries; note what you learn in `tools/seo/SEO_24H.md` or the next plan.
