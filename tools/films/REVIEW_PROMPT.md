# First-pass reviewer prompt

Given to each reviewer with one sheet from `tools/films_sheets.py`. It is deliberately self-contained: a reviewer
reads the sheet and nothing else, so no judgement can rest on a page nobody checked.

---

You are judging candidate documentaries for a wall of architecture films that architecture students browse.

Read `SHEET_PATH`. It is a JSON list of candidate films. Write a JSON list to `DRAFT_PATH` with **exactly one entry
per candidate, in the same order**. Use no tools other than reading that file and writing yours. **Do not search the
web, fetch a page, or use any knowledge of your own about these films.** The sheet is the only evidence that exists.

## The one rule

No invented facts. Every fact you state must come from the words in that candidate's own `extract` (its Wikipedia
opening paragraph) or `overview` (TMDB's). If the sheet does not say it, leave it out. A guessed director or year is
a defect that reaches students; an empty field is correct.

## Keep or reject

Keep a film when **architecture is its subject**: a documentary about architecture, an architect, a building, a city
and how it is built or planned, or how buildings are designed and made.

Reject, with a short reason:
- fiction or drama, however architectural
- a film whose architecture is only a backdrop (a city's politics, a war, a crime, a painter who built one house)
- trailers, clips, news segments, a practice's own promotional film
- anything under about 20 minutes, unless it is a full lecture
- anything you cannot tell from the sheet. **An honest reject beats a thin maybe**: say "the extract does not say
  what it is about" and move on. Rejecting is cheap; a wrong keep reaches students.

## Each kept entry

```json
{"ref": "<copy the candidate's ref exactly>",
 "title": "<copy from the sheet>",
 "verdict": "keep",
 "kind": "feature | series | episode | lecture",
 "genres": ["<one or two of the seven below>"],
 "summary": "<one sentence, under 200 characters, in your own words, saying nothing the quote does not support>",
 "summary_quote": "<the words from extract or overview your summary rests on, copied character for character>",
 "language": "<only if the sheet names it, written out in full: English, Japanese, German>",
 "architects_mentioned": ["<architect names exactly as the sheet spells them>"],
 "buildings_mentioned": ["<building names exactly as the sheet spells them>"]}
```

A rejected entry is `{"ref": "...", "title": "...", "verdict": "reject", "why": "<one short line>"}`.

**The quote is checked mechanically**, character for character, against that candidate's own `extract` and
`overview`. Copy and paste it; do not retype, tidy, shorten inside the sentence, or stitch two sentences together.
A stitched quote fails and the whole batch is sent back. One unbroken run of words from one of those two fields.

## The seven genres, exactly these words

`Portrait of an architect` · `Building story` · `City & urbanism` · `Housing & social` · `Design process` ·
`Movement & history` · `Landscape & sustainability`

One or two per film. Any other word is refused.

## Names

`architects_mentioned` and `buildings_mentioned` are matched against the site's own list afterwards, and a name that
does not match is dropped. So copy the spelling in front of you and **do not correct, expand or complete a name**
from your own memory. Leave the list empty rather than guessing who a film is about.

## Finally

Write the JSON list and nothing else. Then reply with one line: how many you kept, how many you rejected, and the
commonest reason for rejecting.
