# Building write-ups: real written text for the top building pages

SEO strategy chat, 6 Nov 2026, owner's go-ahead to use spare compute over the weekend. Read `CLAUDE.md` first.

**Why:** Google dropped most of the site on 25 Oct as thin template pages. The pages it still trusts are the ones with
writing of their own (architect pages). Each of the 300 building pages Google showed most before the drop
(`todo_1.json` to `todo_3.json`, best first) gets a short original paragraph built only from sourced facts. Nothing
goes live until the owner approves the drafts and the design on Monday.

## Step 1: facts (Sonnet, one chat per todo file)

For each building, find **5 to 8 facts** a student studying it would want: what it is for, who designed it and when,
the main design idea, structure and materials, how people move through it, light and climate, its context, and why it
matters (influence, awards, restoration). Sources: the building's English Wikipedia article first (search by name and
architect; `qid` is its Wikidata id), then other pages you can open. Every fact carries the exact sentence it comes
from and that page's address. **No fact without a quote. No numbers (heights, areas, costs) unless the quote states
them.** If sources disagree, keep both and say so. If you find fewer than 4 good facts, mark the building `thin: true`
and move on.

Write `tools/writeups/results/facts_<n>.json` (n = the todo file's number), a list in todo order:

```json
{"id": "casa-gaspar", "facts": [{"fact": "plain sentence in your words", "quote": "exact sentence from the source",
  "source": "https://en.wikipedia.org/wiki/..."}], "thin": false}
```

Work on branch `claude/writeups-facts-<n>`, commit every 20 buildings, push, and open a pull request "Write-up facts
<n>" when the file is done. Don't touch `site/`. Don't merge.

## Step 2: writing (Opus, the SEO strategy chat)

From the facts only, write **90 to 140 words** per building in plain, worldwide English: what it is, the idea, how it
works, why a student should look at it. No adjectives the facts don't support, no invented details, no "nestled",
"stunning", "iconic". Then a design for where the paragraph sits on the page goes on the canvas for the owner.
