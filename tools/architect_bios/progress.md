# Architect write-ups: progress

## Done
- `results/bios_01.json` (16 Oct 2026), first ten for the owner to approve the voice: Norman Foster, Renzo Piano,
  Oscar Niemeyer, Zaha Hadid, Le Corbusier, Alvar Aalto, Frank Gehry, Herzog & de Meuron, OMA, Glenn Murcutt.
  Bios 161–190 words. Every fact sourced (Wikipedia/Wikidata, fetched by `tools/fetch_architect_sources.py` into
  `sources.json`, plus the buildings' own Wikipedia articles). Unsourced facts: 0.
  Links: 53 addresses tried, 39 kept, all checked 16 Oct 2026 by `tools/check_overview_links.py` (report: `links_report.json`).

- `results/bios_02.json` (19 Oct 2026), 31 architects: ranks 9–40 of `todo.json` without OMA (already in bios_01), so
  I. M. Pei and Tadao Ando are here. The owner approved the voice of bios_01 on 19 Oct (said in the data-collection
  chat). Bios 172–190 words. 262 facts, every one with a source (architect articles in `sources.json`, building
  articles in `building_sources/batch_02.json`). Unsourced facts: 0. Links: 100 kept, all checked 19 Oct 2026.

## Skipped
- None. Every architect in ranks 1–40 is a real, well-sourced person or practice.

## Links that failed and were left out
- Encyclopaedia Britannica (all ten): answers automated checks with 403. Probably fine in a browser, but unchecked.
- Pritzker page for Oscar Niemeyer (1988, shared with Gordon Bunshaft): `/laureates/1988`, `/1988-0`, `/1988-1`,
  `/oscar-niemeyer` all 404. Find the real address before the Bunshaft batch.
- herzogdemeuron.com: redirect loop for the checker (302).
- zaha-hadid.com/architecture/ 404 (the home page, now zha.com, is used instead).

## Links that failed in batch 2 and were left out
- Personal or practice sites that time out, refuse or have a bad certificate for the checker: tangeweb.com,
  toyo-ito.co.jp, richardmeier.com, rsh-p.com, kisho.co.jp. Probably fine in a browser, but unchecked.
- Guessed archive pages that do not exist (404): MoMA (Mies), McGill (Safdie), UPenn (Kahn), Yale (Saarinen),
  Harvard Houghton (Richardson), RIBA (Correa), savewright.org (520).
- Pritzker pages for 2023 (Chipperfield): `/laureates/2023`, `/david-chipperfield`, `/david-alan-chipperfield` all 404.
  2019 (Isozaki) works as `/laureates/arata-isozaki`; 1988 is `/laureates/1988-niemeyer` and `/1988-bunshaft`
  (Niemeyer's is now added to bios_01).
- WikiArquitectura `/architect/<name>/` addresses all 404: its address pattern is different; not used.
- Only two links for **Kunio Maekawa** and **Henry Hobson Richardson** (below the brief's three).

## Weak spots to note
- Glenn Murcutt: Wikipedia has no articles on his houses, so the bio says little about each one. His materials list
  carries a "citation needed" tag on Wikipedia.
- Delirious New York: the OMA article says 1975, the Koolhaas article 1978 (publication). No year used.
- Paimio Sanatorium: wall says 1933, Wikipedia 1929–32. The wall's year is used.
- Batch 2 disagreements, noted on the facts: Philip Johnson's death (Wikidata 2007, wrong; Wikipedia 25 Jan 2005,
  used); BIG's founding (Wikidata 2005, Wikipedia late 2006, used); Maekawa's death day (Wikipedia 26 June,
  Britannica 27 June; only the year used); several building years differ between the wall and Wikipedia, and the
  wall's years are used in the text.
- Thin building sources in batch 2: Isozaki, Ito, Maekawa and Kurokawa have short or missing English articles for
  many buildings, so their write-ups lean on the architect article. Mario Botta's Ticino houses could not be sourced
  and were left out of his text.
- Hard facts written in that the owner may want to see: Philip Johnson's 1930s Nazi sympathies and Richard Meier's
  2018 harassment allegations are each stated in one plain sentence, as Le Corbusier's politics were in bios_01.

## How to run the tools
Put the command on the first line of `tools/architect_bios/request.txt` and push to `claude/architect-bios`
(workflow `.github/workflows/architect-bios.yml`):
- `python -u tools/fetch_architect_sources.py --ranks 41-70 --buildings batch_03` (Wikidata + Wikipedia for the
  architects into `sources.json`, and every wall building's article into `building_sources/batch_03.json`; one run)
- `python -u tools/check_overview_links.py --files bios_02.json`
