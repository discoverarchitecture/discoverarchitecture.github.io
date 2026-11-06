# FAQs for the style, type, city and idea pages

SEO strategy chat, 6 Nov 2026 (owner's go-ahead for weekend work). Read `CLAUDE.md` first. Nothing goes live until the
owner approves the drafts and a design on the canvas.

**Why:** ChatGPT, Perplexity, Gemini and Google's answer boxes quote short, direct answers to the questions students
ask. Each of the 32 pages in `tools/hubs/hubs.json` gets **3 or 4 questions with answers of 40 to 80 words**, in
plain, worldwide English.

**Questions:** the ones a student would really type, for example "What is Brutalist architecture?", "What are the key
features of Brutalism?", "Which brutalist buildings should architecture students study?", "Where can I see brutalist
buildings?" (or for a city: "Which modern buildings in London should architecture students visit?"; for an idea:
"What is adaptive reuse in architecture?", "What are good examples of adaptive reuse?").

**Facts:** only from `tools/hubs/sources.json` (quote-checked facts with sources), the page's own introduction in
`tools/hubs/results/intros_*.json`, and the buildings on the wall (`site/data/buildings.js`: name, architect, year,
place, movement, type, concepts). Building examples must be buildings on the wall that match the page (use
`tools/hub_pages.py`'s `matches()` rule). No new facts, no numbers that aren't in those sources, no "iconic",
"stunning", "nestled". Each answer names its source page in `sources` (one or more addresses from sources.json, or
"wall" for examples from the wall).

**Output:** `tools/hubs/results/faq_01.json`, a list in hubs.json order:

```json
{"slug": "brutalism", "faq": [{"q": "What is Brutalist architecture?", "a": "…", "sources": ["https://…"]}]}
```

Work on branch `claude/hub-faqs`, commit as you go, and open a pull request "Hub page FAQs (drafts)" when all 32 are
done. Don't touch `site/`. Don't merge.
