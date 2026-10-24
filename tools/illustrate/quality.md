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

## Haiku pipeline, fifth pool (21 Oct 2026): 300 contemporary candidates (1990 or later)

At most 4 per architect, at most 25 towers; no stadiums, stations, hotels, malls, offices or housing by type. 221 of
the 300 came from the scored list without the harvest's facts; `cheap_prep.py` now fills those from Wikidata, and
`cheap_leads.py` gave 81 buildings without an English article a lead from another language's Wikipedia (Japanese,
German, Spanish, French…). Haiku judged all 300; Sonnet checked every judgement; Opus checked every gallery.
82 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 1 of 83 (1%): Biblioteca Raúl Rangel Frías (only a fence and a sculpture); 4 better leads chosen | fine |
| No free photo | 13 of 300 (4%) | fine |
| Already on the wall | 11 of 300 (4%), found by Wikipedia article and by distance (a wall building within 200 m), plus Beetham Tower, turned down in round 7 | fine |
| Facts failing the source check | Haiku's keeps: 12 of 84 needed a fact fixed and 16 were wrong keeps (33%), mostly towers kept without a design reason. All fixed by Sonnet before anything was added | **stop level for Haiku alone**, as in pools 3 and 4 |
| Ordinary types | 13 of 82 (16%): 6 towers, 5 housing, 2 workplaces, each with a reason in its lead (a record, a prize, a named innovation) | fine, but the highest of the Haiku pools |

Held: 5 without a sourced year and the Shizuoka City Museum of History, whose SANAA credit nothing in the lead
supports (`tools/cheap/pool5_held.json`). 75 candidates had no Wikipedia lead in any language and were skipped.
The pool filter now needs the distance check too: 11 duplicates had a different Wikidata item from the wall's entry.

## Haiku pipeline, sixth pool (21–22 Oct 2026): 300 candidates from 1900–1989

At most 4 per architect, at most 20 towers; no stadiums, stations, hotels, malls, offices, housing, post offices or
courthouses by type (US federal buildings by the Supervising Architect's office left out). 275 rows filled from
Wikidata; 115 leads from other-language Wikipedias (German 62). Haiku judged all 300; Sonnet checked every judgement;
Opus checked every gallery. 114 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 5 of 119 (4%): Gamble House (drawings only), Majestic Theatre (sign only), Ormen Långe, Crater Lake residence; Villa Primavesi for an unsourced year | fine |
| No free photo | 11 of 300 (4%) | fine |
| Already on the wall | 10 of 300 (3%): 9 by article or distance, and Jyväskylä City Theatre, which the distance check missed because the wall's entry has no coordinates | fine |
| Facts failing the source check | Haiku's keeps: about 21 of 151 needed a fact fixed and 31 were wrong keeps (34%), mostly revival theatres, libraries and houses kept only because the architect is on the wall, and one 1981 building credited to Louis Kahn (died 1974). All fixed by Sonnet | **stop level for Haiku alone**, as in every Haiku pool |
| Ordinary types | 20 of 114 (18%): 9 offices and towers, 5 workplaces, 3 housing, 3 hotels | below the 20% warning, **but rising across the Haiku pools: 10%, 10%, 16%, 18%** |

Held for a year: 8 (Seth Peterson Cottage, Rietveld and Aldo van Eyck pavilions, Palace Moravia, Riverside Art
Museum, Georg Kolbe Museum, De Bijenkorf Rotterdam, the Leuven institute); 2 more for no main photo
(`tools/cheap/pool6_held.json`). 35 of the 114 are houses.

## Haiku pipeline, seventh pool (22 Oct 2026): 300 candidates from 1900 on, no ordinary types in the pool

Owner's rule for this pool: keep ordinary types under 20%. Towers, offices, housing, hotels, shops and cinemas were
left out of the pool by type, and so were 280 local US houses and theatres by architects not on the wall (they had
filled earlier pools). Sonnet tagged every ordinary type it kept. 102 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 102 (4 better leads chosen) | fine |
| No free photo | 13 of 300 (4%) | fine |
| Already on the wall | 7 of 300 (2%): 6 by article or distance, and Wright's Madison meeting house, caught by name when adding | fine |
| Facts failing the source check | Haiku's keeps: 36 of 139 were wrong keeps and about 6 needed a fact fixed (30%), mostly campus halls, revival theatres and town halls kept on a style or listing, and 5 kept with an empty lead. All fixed by Sonnet | **stop level for Haiku alone**, as in every Haiku pool |
| Ordinary types | 8 of 102 (8%) by type; 11% by Sonnet's stricter tag | fine; **the rise stopped** (10%, 10%, 16%, 18%, now 8%) |

Held: 6 without a sourced year, 1 without a main photo (`tools/cheap/pool7_held.json`); Festspielhaus Hellerau left
off for want of an exterior photo. 80 of the 102 are in Europe.

## Haiku pipeline, eighth pool (22 Oct 2026): 300 candidates, batch 7's rules

Same pool rules as the seventh pool, plus local US halls, libraries and churches by architects not on the wall
left out (468 local US entries in all). The candidate list is running thin: Haiku kept only 58 of 300, and Sonnet
ended with 59. Two of the weakest ordinary keeps (the Morbegno library, kept only for its architect, and Aalto's
Philologica dormitory) were dropped so ordinary types stay under the owner's 20%. 52 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 1 of 53 (2%): Villa Tonder (only historic photos; unclear whether it stands) | fine |
| No free photo | 14 of 300 (5%) | fine |
| Already on the wall | 2 of 300 (1%): the Bellinzona public bath and the Cottbus library | fine |
| Facts failing the source check | Haiku's keeps: 7 of 58 were wrong keeps and about 12 needed a fact fixed (33%) | **stop level for Haiku alone**, as in every Haiku pool |
| Ordinary types | 9 of 52 (17%) by Sonnet's tag; 5 (10%) by type | fine, under 20% after dropping two |

Held for a year: Thiel Gallery, Mercado Central (Valencia), Hans Christian Andersen Museum, Lake Suwa Museum
(`tools/cheap/pool8_held.json`). After this pool the harvest has few strong candidates left: the next round should
come from a new search (contemporary work, the Pritzker winners' full lists, under-represented regions) rather than
deeper into this list.

## Haiku pipeline, ninth pool (23 Oct 2026): 139 buildings by Pritzker Prize winners, not yet on the wall

A new search (see the eighth pool's note): every building in `tools/pritzker/buildings.json` not on the wall or
judged before, no ordinary types in the pool, at most 12 per laureate. 37 had no Wikipedia article in any language
(skipped: nothing to source the key features from). Haiku kept 54; Sonnet found 11 wrong keeps (a sculpture, two
duplicates of wall buildings, eight with no design reason in the lead) and rescued 2. Six ordinary keeps were set
aside to keep under the owner's 20% (`tools/cheap/pool9_held.json`, "ordinary type, over the 20% cap"). 22
buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 22 (1 better lead chosen) | fine |
| No free photo | 18 of 139 (13%) | fine |
| Already on the wall | 3 of 139 (2%): Olympic Roof Munich, Shenzhen Library, MOMA Tainan | fine |
| Facts failing the source check | Haiku's keeps: 11 of 54 were wrong keeps and 12 needed a fact fixed (43%), mostly features naming the architect when the lead doesn't | **stop level for Haiku alone**, as in every Haiku pool |
| Ordinary types | 4 of 22 (18%) by Sonnet's tag | fine, after setting six aside |

Held for a year: 12 (`tools/cheap/pool9_held.json`).

## Fix-up round (23 Oct 2026): sourced years for the 51 held buildings

`tools/held_years.py` (on Actions) gathered Wikidata dates and the build/open/complete sentences from up to three
Wikipedia articles per building; a Sonnet chat picked the completion year and quoted its source
(`tools/cheap/held_years_picked.json`, quotes kept in each entry's `year_source`). 39 were added: 29 with a high, 9
with a medium confidence year, and Wall House II (2001, built after Hejduk's death). Left held: 5 with no year in any
source, 4 low-confidence (CityLife, Historisches Museum Saar, Aldo van Eyck pavilion, Lake Suwa), Prins Hendrikkade
600 (Piano's pavilion was rebuilt) and Glenstone (its main buildings are Phifer's); UOB Plaza was already on the
wall. Photo review: 2 better leads, 53 gallery photos removed across both rounds (events, signs, artworks, models,
and Andersen's birthplace in the Kuma museum's gallery). Ordinary types: 4 of 39 (10%).

## Haiku pipeline, tenth pool (23 Oct 2026): 300 candidates from a new harvest of buildings from 2000 on

`tools/harvest_recent.py` (Wikidata, works with an architect and at least two sitelinks, 2000–2026) gave 3,964;
`tools/cheap/make_pool10.py` kept 300: no ordinary types by name or instance, no earliest date before 1998 (old
buildings reopened later), none by architects whose wall work ends before 1975, at most 4 per architect. The fame
bar is low: Haiku kept 94, and Sonnet threw out 46 of them, mostly kept only because the architect is on the wall
with nothing in the lead about the design, and rescued 5. Left out by hand: House Okamura (the private home of a
named politician) and Bunker 599 (an installation; owner to decide); the Deloitte office building was set aside for
the 20% rule. 45 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 45 (1 better lead chosen; 37 gallery photos removed) | fine |
| No free photo | 14 of 300 (5%) | fine |
| Already on the wall | 0 of 300 | fine |
| Facts failing the source check | Haiku's keeps: 46 of 94 were wrong keeps and 21 needed a fact fixed (71%) | **stop level for Haiku alone**: Haiku is not reliable on a low-fame list; Sonnet's full check is essential |
| Ordinary types | 8 of 45 (18%) by Sonnet's tag | fine, after setting one aside |

Held: 3 without a sourced year, 2 without a main photo, and the three above (`tools/cheap/pool10_held.json`).

## Haiku pipeline, eleventh pool (23 Oct 2026): 299 candidates from under-represented regions

From `tools/harvest/regions.json` (the 11 Oct regional harvest: Africa, Latin America and Asia beyond Japan, China,
Korea, Taiwan and Russia), not used before, dated 1900 on, no ordinary types by name, at most 4 per architect and 20
per country (`tools/cheap/make_pool11.py`). Haiku kept 45; Sonnet threw out 18 (12 revival-style cathedrals and
palaces with nothing in the lead about their design, 3 already on the wall, 3 ordinary civic buildings) and rescued
5, of which three Barluzzi churches were left out by hand for the same want of a design reason. Muzharul Islam's
Fine Arts building in Dhaka came off `rejected.txt`: a daylight photo of the building itself was found and checked
by eye. Three ordinary keeps were set aside for the 20% rule. 24 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 24 (1 better lead chosen; 18 gallery photos removed) | fine |
| No free photo | 9 of 299 (3%), among them Africa Hall, Manik Bagh, Duhart's Concepción library and Guedes's Zambi | fine |
| Already on the wall | 8 of 299 (3%): Israel Museum, Pearl Palace, Weizmann House, Villa Shodhan, Villa Baizeau, Coconut Palace, Chaktomuk Hall, Holy Sacrifice | fine |
| Facts failing the source check | Haiku's keeps: 18 of 45 were wrong keeps and 13 needed a fact fixed (69%) | **stop level for Haiku alone**, as in every Haiku pool |
| Ordinary types | 4 of 24 (17%) by Sonnet's tag | fine, after setting three aside |

Held: Independence Hall (no year), Botter Apartment (no main photo), and the three ordinary keeps
(`tools/cheap/pool11_held.json`). The regional harvest is thin past this pool: 300 more candidates would mostly be
revival churches and offices. Five strong buildings were skipped only for want of any Wikipedia text (House of
Victoria Ocampo, the Senate Palace and the Glass Building in Tehran, the Ab-o-Atash amphitheatre, Igreja Matriz in
Presidente Getúlio): worth a hand-written entry from a source later.

## Haiku pipeline, twelfth pool (24 Oct 2026): 117 prize-winning buildings

A new search: Wikidata records few prize winners for buildings (`tools/harvest_awards.py`, 48), so
`tools/harvest_award_lists.py` read the winner lists in 29 prizes' Wikipedia articles (Stirling, RIBA International,
Mies van der Rohe, Aga Khan, AIA Twenty-five Year, Kasper Salin, Houens, Équerre d'argent, the Spanish and German
national prizes, Japan's AIJ and BCS prizes and others) and kept the linked pages that have an architect: 376, of
which 117 were new to the wall (`tools/cheap/make_pool12.py`). Lesson: a link from a prize's article does not mean the
building won it (shortlists and mentions are linked too), and Japan's BCS Prize is a builders' prize given to many
ordinary offices and hotels. Haiku was told to treat the prize as a design reason and kept 79; Sonnet then counted a
prize only when the building's own lead confirms it, and threw out 51. Four ordinary keeps were set aside for the 20%
rule. 22 buildings reached the wall.

| Number | This pool | Level |
|---|---|---|
| Leads held back in photo review | 0 of 22 (13 gallery photos removed) | fine |
| No free photo | 6 of 117 (5%) | fine |
| Already on the wall | 4 of 117 (3%): Sea Ranch Condominium One, Sony City Osaki, Grande Arche, the Badalona arena | fine |
| Facts failing the source check | Haiku's keeps: 51 of 79 were wrong keeps (65%), most for an unconfirmed prize | **stop level for Haiku alone**; next time, tell Haiku a linked prize is not a reason |
| Ordinary types | 3 of 22 (14%) by Sonnet's tag | fine, after setting four aside |

Held: the General Motors Technical Center (Saarinen) and Domkyrkoforum for a sourced year (`tools/cheap/pool12_held.json`).
Also in this round: Go deeper links for the last 151 buildings without, so every building on the wall has them.

## "Year unavailable" and hand-written entries (24 Oct 2026)

**25 buildings with no sourced year** go on the wall with "Year unavailable" (owner, 24 Oct 2026): no year in their
titles or descriptions, no decade in the date filter, sorted last (`tools/illustrate/results/zz_noyear.json`). Their
photos were checked by eye: no lead held back; 24 gallery photos removed (a museum's bells, stained glass filed under
the wrong Commons category, dancers, shrines near Lake Suwa, a defibrillator); the Chapel of St. Basil now leads with
its cross wall. The General Motors Technical Center stays off: its only free photo shows a newer office.

**Hand-written entries**, for buildings with no Wikipedia article. `tools/fetch_pages.py` saved 20 of 27 source pages
on Actions (`tools/cheap/handwritten_pages/`); a Sonnet check quoted every fact from them, each quote checked word for
word (`tools/cheap/handwritten_quotes.json`); Opus decided:

| Building | Decision |
|---|---|
| Senate Palace, Tehran (Ghiai, Foroughi) | added; year shown as 1954–59, the span Encyclopaedia Iranica gives (sources differ on one year) |
| House of Victoria Ocampo (Bustillo) | added, 1928 (all three pages) |
| Plassen Cultural Centre (3XN) | added, 2012 (opened 14 July 2012) |
| Tikkurila Church (OOPEAA) | added, 2021 (inaugurated January 2021) |
| Vennesla Church (LINK arkitektur) | added, 2022 (completed and consecrated) |
| Blessed Augustin Kažotić Church, Zagreb (Magaš) | held: no page describes the design; 1998 or 2004 |
| Knin church (Rošin) | held: no page describes the design |
| Igreja Matriz (Böhm), Ab-o-Atash, the Glass Building | held: no source page could be saved |

The draft facts were often wrong (a stone-building award, "long church", a Le Corbusier influence the house in fact
rejects, the Knin architect's name): 6 of 7 drafts had at least one unsupported fact, which is why only quoted facts
reached the wall. Each entry keeps its sources and quotes in `tools/illustrate/results/zz_handwritten.json`.
