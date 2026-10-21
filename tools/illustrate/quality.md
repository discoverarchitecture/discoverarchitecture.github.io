# Quality watch, round by round

The owner's rule (CLAUDE.md, 14 Oct 2026): every round reports these five numbers and warns before quality drops.

| Signal | Warn | Stop |
|---|---|---|
| Leads held back in photo review | 8% | 15% |
| Proposals with no free photo | 35% | 50% |
| Proposals already on the wall | 25% | 40% |
| Facts failing the source check | 3% | 6% |
| Ordinary types (offices, housing, hotels, malls) | 20% | 30% |

A steady rise across rounds is also a warning, even below the levels.

## Round 7 (14 Oct 2026), first batch: UK and Ireland, France and Italy, USA east and west, Eastern Europe (first 10), Canada and Mexico

395 proposals from six Sonnet chats.

| Signal | Number | Level |
|---|---|---|
| Leads held back in photo review | 8 of 334 (2%) | fine |
| No free photo | 39 of 395 (10%) | fine |
| Already on the wall | 4 of 395 (1%): Grand Théâtre de Rabat, Neutra VDL House, San Antonio Central Library, and the Bourse de Commerce proposed twice | fine |
| Facts failing the source check | 0 of 40 checked at random (0%) | fine |
| Ordinary types | 76 of 358 with full facts (21%) as proposed; 15% after 23 ordinary towers and hotels were held back | **warned** (owner told on 14 Oct) |

Also found: five older pairs on the wall were the same building under two names (Klippan church, MuBE, Anacleto Angelini centre, Yamanashi centre, Smiling Lion); the second of each was removed, and `add_illustrated.py` now skips a proposal whose Commons category and year match a building already on the wall.

Galleries: about 370 off-topic pictures (people, signs, artworks, street views, other buildings) were taken out of the new buildings' galleries by eye.

## Round 7, second batch (14 Oct 2026): USA east (rest), Eastern Europe (rest), Benelux, Southeast Asia

184 new proposals from four Sonnet chats.

| Signal | Number | Level |
|---|---|---|
| Leads held back in photo review | 7 of 162 (4%): Kozara monument, Manila Film Center, Pasig Revolving Tower, Capitan Luis Gonzaga Building, IFI Cathedral, Blue Cross-Blue Shield Chicago, Highfield House (its photos showed other buildings) | fine, but up from 2% |
| No free photo | 6 of 184 (3%) | fine |
| Already on the wall | 0 | fine |
| Facts failing the source check | 0 of 35 checked at random | fine |
| Ordinary types | 43 of 184 (23%) as proposed, Southeast Asia about 30%; 17% after 15 generic towers were held back | **warned**, and rising (21% → 23%) |

For the next round: the brief should ask Southeast Asian and other skyline-heavy themes for fewer office towers, and the photo check should open the Commons category, not only file names (the Southeast Asia and Manila chats could not see thumbnails).

## Round 8, first batch (14 Oct 2026): South America, Middle East and Turkey, South Asia

276 proposals from three Sonnet chats, under the round 8 brief (few ordinary types, photos seen, not picked by name).

| Signal | Number | Level |
|---|---|---|
| Leads held back in photo review | 9 of 243 (4%): Troy Museum, Abboud Building, Mohammed Bin Rashid Library, Mathaf, Education City Stadium, Hamad Airport, Tbilisi Wedding Palace, Vigyan Bhawan, Visvesvaraya Centre | fine, level with round 7b |
| No free photo | 30 of 276 (11%), South Asia 18% | fine |
| Already on the wall | 2 of 276 (1%): Tomb of Avicenna, NCPA Mumbai | fine |
| Facts failing the source check | 0 of 40 checked at random | fine |
| Ordinary types | 21 of 276 (8%) as proposed | fine, down from 23%: the brief change worked |

Galleries are still the weak spot: 348 off-topic pictures (tourists, plaques, other buildings, one gallery of the Empire State Building) taken out by eye.

## Round 8, second batch (14 Oct 2026): Africa, Japan and Korea

89 proposals from two Sonnet chats (the Africa chat picked from Commons categories without seeing thumbnails).

| Signal | Number | Level |
|---|---|---|
| Leads held back in photo review | 1 of 82 (1%): Heroes' Acre, Windhoek | fine |
| No free photo | 6 of 89 (7%) | fine |
| Already on the wall | 0 | fine |
| Facts failing the source check | 1 of 81, every building checked (1%): Daejeon science museum year 1984 → 1990, corrected. The first random 25 showed 4%, over the warning level, so the whole batch was checked. | fine |
| Ordinary types | 3 of 89 (3%); Carlton Centre held back | fine |

110 off-topic gallery pictures out; 26 buildings got a better lead from their own gallery.

## Gallery clean-up (15 Oct 2026), after the owner's and tester's reports

Every gallery photo on the wall was checked again (13,471 photos from rounds 1–6 by seven Sonnet helpers, every flag then checked by eye; every round 7–8 main photo re-checked by eye with the stricter rule).

- 1,626 photos taken out: people, events, sculptures, paintings, objects, signs, streets and unrelated views. 269 interiors that were labelled "Exterior" were relabelled.
- 193 buildings got a new main photo of the building itself, chosen from their own gallery.
- 54 buildings came off the wall because no photo shows the building (listed in `recheck.md`; the photo rescue looks for them later). Of these, 14 were added in rounds 7–8.
- 3 duplicates merged (Omar Khayyam mausoleum, Yale A&A Building, Entebbe hospital); `add_illustrated.py` now also catches the same architect, year and place under reworded names.

What went wrong in rounds 7–8: the review looked at leads and galleries in one pass, at small size, and let through main photos where the building was small, far off, at night or seen from inside a stadium. From now on a main photo must show the whole building from outside, in daylight, as the clear subject; a building whose only photos fail this stays off the wall.

## Design chat flags (15 Oct 2026)

The Design chat, checking galleries for the "Worth the swipe" dots, flagged 43 problems in 40 buildings (`tools/worth_swipe_flags.md` on `claude/design`). Each was checked by eye; 39 were right.

- 17 buildings got a new main photo: 11 from their own gallery, and 6 from photos newly picked on Commons and checked by eye (Park Güell, Széchenyi Bath, the Art Institute's Modern Wing, Fondazione Prada, 330 North Wabash, Cleo Rogers Library).
- 70 photos taken out: other buildings (Tower of London in the Curtain Wall House, a pagoda forest in the Centre for Earth Architecture, Trump Tower in 330 North Wabash, Emerson's Boston buildings, Hotel Adlon, the Bundeskunsthalle), plus artworks, people, night shots and a satellite view.
- 4 buildings came off the wall because no free photo shows them from outside: Grande Arche (France has no freedom of panorama, so Commons keeps only details), Athens Olympic Stadium roof, Notre-Dame-de-Lourdes in Casablanca, and the Fagnano Olona school. The photo rescue will look again.
- Left as it is: the Capanema Palace main photo (the pilotis are the subject; the child is tiny).

## Coordinates check (15 Oct 2026)

Adding map coordinates exposed a hidden photo problem. 16 buildings had a `commons` field naming a same-name Commons category for another building, in another country, so their galleries showed that other building. Examples: the Beirut Cinema Opera showed the Reims one, Halifax Central Library (Canada) showed the one in England, and the Merck headquarters showed SAS in Stockholm.
- Wrong photos came out of 7 galleries, and 5 buildings were held back.
- These were caught only because the coordinates landed in the wrong country. Same-country mix-ups would not show up this way.

## Better photos pilot (19 Oct 2026): Commons-rated photos, first 300 buildings

A Sonnet helper (`tools/quality_photos.py`, `tools/quality/BRIEF.md`) found Featured, Quality and Valued photos on
Commons that were missing from galleries. 56 of the 300 buildings had some. Opus checked every proposal by eye:
5 new main photos (NMAAHC, Danish Maritime Museum, Portugal Pavilion, Parliament House, Robson Square) and
63 gallery photos for 40 buildings. 5 proposals were turned down: a bell frame, a sculpture in front of the
Guggenheim, a far skyline, a near-duplicate and a lamp close-up.

## Round 9 (19–20 Oct 2026): China and Taiwan, central USA, Germany/Austria/Switzerland, the Nordic countries, award winners, Australia and New Zealand

329 buildings proposed by six Sonnet helpers; 260 reached the wall. The target was 500: the helpers found fewer
buildings with a free daylight photo of the building than hoped, and quality came first.

| Number | Round 9 | Level |
|---|---|---|
| Leads held back in photo review | 4 of 264 (2%): Brisbane Powerhouse, Centenary Pool, Perth Stadium, Kölnturm | fine |
| No free photo | 61 of 329 (19%): China 27%, central USA 20%, DACH 32%, the rest 0% | fine (DACH alone is near the 35% warning) |
| Already on the wall | 3 of 329 (1%): Zollverein, Kuggen, Baker House | fine |
| Facts failing the source check | 1 of 26 checked (4%): VitraHaus typed "Culture & sport", now Pavilion. Edmund Barton Building moved from Civic to Office & tower. Architect, year and place matched on all 26. | warning: small sample, just over 3%. The next round checks every building |
| Ordinary types | 31 of 260 (12%) | fine |

Photo review: 16 buildings got a better main photo from their own gallery. A second Sonnet check of all 260
galleries, verified by eye on the contact sheets, took out 223 more photos: people and events, museum objects,
signs, night shots, maps, near-duplicates, and photos of other buildings (the Munich Olympic Stadium in the HfG Ulm
gallery, the cathedral next door in Perth's Council House, paintings in the Röhsska Museum, a French château in
Château Neuf).

## Haiku pipeline, third pool (21 Oct 2026): 287 candidates by architects with 2+ buildings on the wall

Haiku judged all 287 from prepared facts, Wikipedia leads and contact sheets. Sonnet checked every keep, every
unsure and every skip; Opus checked every gallery by eye. 98 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 98 (4 better leads chosen) | fine |
| No free photo | 3 of 287 (1%); 35 more had no usable outside photo | fine |
| Already on the wall | 32 of 287 (11%): 25 caught by Wikipedia article, 5 by Sonnet, 2 by the add step | fine |
| Facts failing the source check | Haiku's raw output: about 25 fact errors and 15 wrong keeps in 124 keeps (over 20%). All fixed by Sonnet's full check before anything was added | **stop level for Haiku alone** — Haiku must not run without a full Sonnet check |
| Ordinary types | 10 of 98 (10%) | fine |

What Haiku got wrong: it trusts Wikidata's architect (Sinan credited for a 1347 Mamluk mosque, Horta for an 1844
museum, renovation architects for older buildings), takes demolished or rebuilt buildings at face value, uses a
district as the city, and does not check the wall for duplicates. 21 good buildings are held in
`tools/cheap/held_no_year.json` because no source in the prepared data gives a year. 25 of the 98 are Ottoman
mosques by Sinan: fine as historic precedents, but the next pool should lean modern.

## Haiku pipeline, fourth pool (21 Oct 2026): 300 modern candidates (built 1900 or later)

94 by architects already on the wall, 206 well-scored new ones. Haiku judged all 300 with the brief's new
"lessons" section; Sonnet checked every keep, unsure and skip; Opus checked every gallery by eye. 79 reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 79 (1 better lead chosen: Nuevos Ministerios; 8 more swapped by Sonnet) | fine |
| No free photo | not counted separately; the pool was built from candidates with Commons photos | fine |
| Already on the wall | 0 of 300: the pool filter now checks the Wikipedia article and the Commons category | fine |
| Facts failing the source check | Haiku's keeps: 9 of 62 needed a fact fixed, 3 were wrong keeps (19%). All fixed by Sonnet before anything was added | **stop level for Haiku alone**, as in pool 3 |
| Ordinary types | 8 of 79 (10%): 3 housing, 3 office, 2 hotels | fine |

Haiku was now too strict: it skipped buildings whose Wikipedia lead names no architect. The brief was loosened
(accept Wikidata's architect unless the lead names someone else or the dates rule it out), and Sonnet rescued 37
good skips. 7 buildings wait in `tools/cheap/held_no_year.json` for a sourced year. Opus took 90 weak photos out of
47 galleries (people, interiors of other rooms, night shots, near-duplicates). Six credits that listed a firm and its
partners were shortened to the firm (Heureka, 013, MAAT, Rosecliff, De Doelen, Pasadena City Hall).
