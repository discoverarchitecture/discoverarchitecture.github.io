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

- `results/bios_03.json` (19 Oct 2026), 30 architects, ranks 41–70. Bios 176–190 words. 236 facts, every one with a
  source; 3 of them are building attributions confirmed on Wikidata (architect, P84) by the checker, for buildings
  with no English article. Unsourced facts: 0. Links: 92 kept, all checked 19 Oct 2026.

- `results/bios_04.json` (19 Oct 2026), 30 architects, ranks 71–100 (the Utzon duplicate is rank 216, not in this
  range). Bios 161–190 words. 213 facts, every one with a source; 7 are building attributions confirmed on Wikidata
  (architect, P84) by the checker. Unsourced facts: 0. Links: 95 kept, all checked 19 Oct 2026 (two check runs).

- `results/bios_05.json` (19 Oct 2026), 30 architects, ranks 101–130. Bios 158–190 words. 205 facts, every one with a
  source; 2 are building attributions confirmed on Wikidata. Unsourced facts: 0. Links: 92 kept, all checked 19 Oct 2026 (two check runs).

- `results/bios_06.json` (19 Oct 2026), 30 entries, ranks 131–160. Bios 166–190 words. 178 facts, every one with a
  source; 5 are building attributions confirmed on Wikidata. Unsourced facts: 0. Links: 93 kept, all checked
  19 Oct 2026 (two check runs).

- `results/bios_07.json` (20 Oct 2026), 29 entries, ranks 161–190 without Snohetta (rank 172, the same practice as
  Snøhetta in bios_04). Bios 175–190 words. 139 facts, every one with a source; 4 are building attributions confirmed
  on Wikidata. Unsourced facts: 0. Links: 94 kept, all checked 20 Oct 2026 (three check runs).

- `results/bios_08.json` (20 Oct 2026), ranks 191–220: 27 bios plus **Joseon builders** marked `"skip": true`.
  Glenn Murcutt (rank 202) is already in bios_01 and Jorn Utzon (rank 216) is the Jørn Utzon of bios_03, so neither
  is repeated. Bios 175–189 words. 101 facts, every one with a source; 3 are building attributions confirmed on
  Wikidata. Unsourced facts: 0. Links: 105 kept, all checked 20 Oct 2026 (one check run).

- `results/bios_09.json` (21 Oct 2026), 30 architects, ranks 221–250. Bios 176–190 words. 106 facts, every one with a
  source; 4 are building attributions confirmed on Wikidata. Unsourced facts: 0. Links: 113 kept, all checked
  21 Oct 2026 (two check runs).

- `results/bios_10.json` (21 Oct 2026), the last 6 entries, ranks 251–256. Bios 179–189 words. 20 facts, every one
  with a source. Unsourced facts: 0. Links: 22 kept, all checked 21 Oct 2026 (two check runs). With this file every
  entry in `todo.json` has a write-up, apart from the three listed under Skipped.

## Skipped
- **Joseon builders** (rank 218), marked `"skip": true`: not an architect or practice but the wall's label for the
  anonymous builders of Jongmyo Shrine, Byeongsan Seowon and Janggyeong Panjeon. Every other entry in ranks
  1–256 is a real person or practice with enough sources to write about.
- Glenn Murcutt (rank 202) was written in bios_01 and is not repeated.
- Jorn Utzon (rank 216) is Jørn Utzon (bios_03) under a second spelling on the wall; not repeated.
- Snohetta (rank 172) is left out as a duplicate: it is Snøhetta (bios_04) under a second spelling on the wall. The data
  side may want to merge them.

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

## Batch 3 notes
- Seven architects have only two checked links: Carlos Raúl Villanueva, Charles Rennie Mackintosh, Eliel Saarinen,
  Mimar Sinan (Archnet rate-limited the checker, 429), Ricardo Bofill (his site breaks the checker's SSL), Félix
  Candela and Hans Scharoun (their archive pages load but are built by JavaScript, so the name check cannot see them).
- Several practice and personal sites fail the checker's certificate check (sanaa.co.jp, seidler.net.au, utzon.dk,
  ricardobofill.com); probably fine in a browser, unchecked, so left out.
- SESC 24 de Maio (Paulo Mendes da Rocha) was dropped from his text: no English article and no architect on Wikidata.
- "Jørn Utzon" (rank 59) and "Jorn Utzon" (rank 216) are the same person under two spellings on the wall; batch 3
  covers the wall buildings filed under "Jørn". The data side may want to merge them.
- The building-text search that runs when a wall building has no Wikidata item can still pick the wrong article
  (Casa no Butantã got the Pinacoteca's). Every fact was read against the article's title before use.

## Batch 10 notes
- **Fewer than three wall buildings** because the wall has only these: **Liu Jiakun** (two), **Richard and Su
  Rogers** and **Robert Venturi** (one each). Each text names all of them.
- **Werner Düttmann** has no English article; he is written from the German articles on him and on the Brücke-Museum.
  **Liu Jiakun**'s short English article is filled out from the Pritzker Prize page and articles in Architectural
  Record and Azure.
- **Richard and Su Rogers** (no qid; no Wikidata item for the partnership) is written from the articles on Su Rogers,
  Richard Rogers and 22 Parkside, and covers only the couple's practice of 1967–1970, so it does not repeat the
  Richard Rogers page.
- Robert Venturi's Pritzker going to him alone despite a request to include Denise Scott Brown is stated in one
  sentence.
- Links left out after the checker: the English articles on the Brücke Museum and the Academy of Arts (Düttmann's name
  is not on them) and the Rechter Architects site (no answer).
- Disagreements, noted on the facts: the Mivtachim Sanitarium (1966 in the article, 1969 on the wall), 22 Parkside
  (1967 for the design, 1969 for the house) and West Village (2014 or 2015). The wall's years are used in the text.

## Batch 9 notes
- New in the fetcher: `--pages FILE` saves the text of other pages (any-language Wikipedia through its API, other
  sites from their HTML) into `page_sources.json`, for architects and buildings with no English article. The list
  for this batch is `pages_09.json`. Facts taken from these pages cite the page itself.
- Written partly or mainly from non-English sources: **Masato Otaka** (Japanese Wikipedia, the Centre Pompidou's
  page on his Sakaide model, and the English article on Metabolism), **Van den Broek en Bakema** (Dutch and German
  articles on the firm and its buildings, with the English article on Jaap Bakema), **Shin Takamatsu** (his English
  works list and the Japanese article), **Sedad Hakkı Eldem** (Turkish article for the Atatürk Library), **Mario
  Roberto Álvarez** (Spanish article for the SOMISA Building), **Domènech i Montaner** (Spanish article for Casa
  Fuster), **Tezuka Architects** (the museum's own page for Kyororo) and **UNStudio** (a project page for the
  Galleria façade).
- **No qid**: **Tezuka Architects** (no Wikidata item found for the practice).
- Wall credits the data side may want to look at: the **Government House of the Kazakh ASSR (now KBTU)**, whose
  article says the building now houses the Kazakh National Academy of Arts; **Preston Bus Station** (designed by
  Building Design Partnership, engineered by Ove Arup & Partners) and **Dunelm House** (designed by the Architects'
  Co-Partnership, completed under Ove Arup's supervision), both filed under Ove Arup; **Central Hall, University of
  York** and the **Royal Commonwealth Pool**, designed by John Speight and John Richards of RMJM, filed under Robert
  Matthew; the **Fondation Avicenne**, designed by Foroughi and Heydar Ghiai with André Bloc and Claude Parent. The
  texts say who did what.
- Paired entries written so they do not repeat each other: **Leslie Martin** and **Robert Matthew** (the Royal
  Festival Hall told from each side); **Ove Arup** (the man) and **Arup** (the firm, bios_07); **Van den Broek en
  Bakema** and **Brinkman & Van der Vlugt** (bios_07).
- Hard facts stated in one plain sentence each: Piacentini's role in Fascist architecture under Mussolini; the 2004
  collapse at Andreu's Terminal 2E; Speer's report that Hitler admired Behrens's Saint Petersburg embassy; the
  criticism of Wang Shu's Pritzker for leaving out Lu Wenyu.
- Links left out after the checker: guessed Architectuul pages for Leslie Martin, Álvarez, Rewal, Takamatsu and
  González de León (404), ArchDaily's Kris Yao tag (404) and UNStudio office page (name not found), the Kris Yao and
  MRA office sites, Arup's founder page (404), Wikipedia's Niavaran Palace and Harvey Court pages (name not found or
  404).
- Disagreements, noted on the facts: Domènech i Montaner's birth year (1849 in the article, 1850 on Wikidata), Eldem's
  birth day (31 or 18 August 1908), Lundgaard & Tranberg's founding (1985 or 1983), the Kingsgate Bridge's opening
  (1963 or 1964); and building years that differ from the wall (Kannikegården, Centro Cultural General San Martín,
  Sun House, Behrens's embassy and crematorium, Faculty of Architecture in Montevideo, Zeyrek, Atatürk Library, Marl
  Town Hall, Independence Monument in Phnom Penh). The wall's years are used in the text.

## Batch 8 notes
- **National Monument (Indonesia)** is filed on the wall under Friedrich Silaban, but his article says his 1955 entry
  was ranked highest yet placed second and the monument was designed by **Soedarsono**. The text says exactly that;
  the data side may want to change the wall's architect for this building.
- **No qid**: **Diller Scofidio + Renfro** (the Wikidata search found no item). **Heatherwick Studio** carries Thomas
  Heatherwick's item (Q3051023), as the search found no item for the studio itself; noted on the fact.
- **Kant-Dreieck** (Kleihues) has no English article or Wikidata architect; it is sourced from the architects' own
  project page (kleihues.com), which gives 1992–1995 against the wall's 1994.
- **Sansad Bhavan (Old Parliament House)** is on the wall under both Lutyens and Baker; Lutyens's page tells of his
  circular plan, Baker's of the Secretariat and their falling-out, so the two pages do not repeat each other.
- Hard facts stated in one plain sentence each: Herbert Baker's Nairobi plan (racial segregation) and his Bank of
  England rebuilding; Helmut Jahn's death in a cycling accident; Henselmann's Nazi-era ban for his partly Jewish
  ancestry; Domenig as the son of a Nazi judge.
- Not stated for want of a source: that the Lanserhof Sylt is a health resort (the wall's type says Health).
- Links left out after the checker: guessed Architectuul pages for Lutyens, Scott, Guimard, Baker, Andrews and Stein
  (404), ArchDaily's Gigon/Guyer office page (404), French Wikipedia "Houchang Seyhoun" (404) and Vitra's Prouvé
  page (403). Every architect kept at least three checked links.
- Disagreements, noted on the facts: Ramos de Azevedo's death day (13 June on Wikipedia, 1 June on Wikidata), the
  Palace of Justice's inauguration (2 January or 2 August 1933), Joseph Allen Stein's death day (6 or 14 October
  2001), Gigon/Guyer's founding (1987 on Wikidata, 1989 in the article), the Steinhaus (more than 30 years of work, or
  1980–2008), Guimard's façade competition (1898 or 1899); and building years that differ from the wall (ICA Boston,
  Museo Enzo Ferrari, Church of the Autostrada del Sole, Longarone church, Haus des Rundfunks, IG Farben Building,
  Messeturm, Hochhaus an der Weberwiese, Tomb of Nader Shah, Gifu Kitagata Apartment, Kant-Dreieck). The wall's years
  are used in the text.

## Batch 7 notes
- Only two checked links: **Aris Konstantinidis** (Architectuul and ArchDaily have no page; Impactalk and UCL answer
  403; archINFORM answers 300). Left out after the checker: several guessed Architectuul and ArchDaily addresses
  (404), Docomomo US (404), the NGV history page (404), Pritzker `/laureates/2026` (404; Radić's page is
  `/laureates/smiljan-radic-clarke`), the UNESCO Van Nelle page (the firm's name is not on it), barbican.org.uk (404),
  Armeniapedia (403), and the Architecture-Studio and Fundació Enric Miralles sites (no answer).
- **No qid**: **O'Donnell + Tuomey** (no Wikidata item found for the practice; written from the articles on Sheila
  O'Donnell and John Tuomey) and **Alexander Tamanian** (the search found no item).
- **Ammar Khammash**: his Wikidata item (Q12228283) describes him as a "Dubaite numismatist", which does not match
  the article; the article is followed and the mismatch is noted on the fact.
- **Thom Mayne** and **Morphosis** (bios_05) are written so they do not repeat each other. Reports of his temper and
  his remark after 9/11 are not included; the owner may want to decide whether they belong.
- Wall buildings left out for want of a source: Villa Stein-de Monzie (Pierre Jeanneret), Rivesaltes Camp Memorial
  (Ricciotti), ADAC Headquarters (Sauerbruch Hutton), Flower Kiosk at Malmö Eastern Cemetery (Lewerentz), Swiss
  National Park Visitor Centre (Olgiati) and the National Museum of Japanese History (Ashihara).
- Disagreements, noted on the facts: Roy Grounds's death day (Wikipedia 2 March, Wikidata 7 March 1981) and his
  partnership's dates; Benedetta Tagliabue's birth day (23 or 24 June 1963) and EMBT's founding (1993 or 1994);
  the Parc de la Villette competition (1982 and 1983 in the same article); Olgiati's birthplace (not used); and
  building years that differ from the wall (Riksbank, St Mark's Church, Diamond Ranch, Goldman & Salatsch,
  Pedregulho, MAM Rio, Notre-Dame-de-l'Arche-d'Alliance, Le Fresnoy, Sonneveld House, Golden
  Lane). The wall's years are used in the text.

## Batch 6 notes
- Four entries have only two checked links: **Berthold Lubetkin and Tecton**, **Charles Girault**, **Henry N. Cobb**
  and **Nayyar Ali Dada**. Historic England, the Royal Academy and Structurae answer the checker with 403; several
  ArchDaily tag and Architectuul addresses do not exist.
- **No qid**: **J. Mayer H.** (no Wikidata item found for the firm) and **Kevin Roche John Dinkeloo and Associates**
  (none found either); both are written from the English articles on Jürgen Mayer and Roche-Dinkeloo.
- **Grafton Architects** has no English article of its own; it is written from the articles on its founders,
  Shelley McNamara and Yvonne Farrell (Wikidata Q69570584).
- Pairs on the wall written as separate pages without repeating each other: **Berthold Lubetkin** (the man, his
  four wall buildings) and **Berthold Lubetkin and Tecton** (the group, its four); **Kevin Roche** (the man) and
  **Kevin Roche John Dinkeloo and Associates** (the firm). **Behnisch Architekten** (Stefan Behnisch's firm) is kept
  apart from Behnisch & Partner in batch 5.
- Tecton's end date: its own article says it disbanded in 1939, Lubetkin's that it was dissolved in 1948. Both are
  given in the text and `born_died` is "1932–1948"; the data side may prefer "founded 1932".
- David Adjaye: the 2023 sexual assault and harassment allegations are stated in one plain sentence, with his denial
  and the fact that no charges were brought, as earlier batches did for similar matters.
- Wall buildings not named: SantralIstanbul (Arolat), Novocomum (Terragni), Lister County Courthouse (Asplund) and
  Friendship Hospital Satkhira (Chowdhury) for want of a source; Gaddafi Stadium (Nayyar Ali Dada) is sourced but was
  cut to keep the bio within 190 words.
- Disagreements, noted on the facts: Enric Miralles's birth day (12 or 25 February 1955), Henry van de Velde's death
  day (15 or 25 October 1957), Gerrit Rietveld's birth date (the article gives two); Frei Otto's
  Royal Gold Medal (2006 on Wikipedia, 2005 on Wikidata); Nayyar Ali Dada's Alhamra (1981 in his list, 1992 completion);
  and building years that differ from the wall (Gorilla House, Dutch Pavilion, Santa Caterina, Santa Fe Federal,
  Central Library UNAM, The Pyramids, Boekentoren, Royal Collections Gallery, Castellón, Sheraton Huzhou).

## Batch 5 notes
- Four entries have only two checked links: **Hiroshi Hara** (his office site does not answer; Archiweb's page does
  not show his name to the checker), **Artur Tarkhanyan** (no English article; the Karen Demirchyan Complex article
  spells him "Tarkhanian"), **Ashton Raggatt McDougall** (ArchDaily lists it as "ARM Architecture") and **Behnisch &
  Partner**. Structurae (403), Floornature (403) and several museum pages failed the checker.
- **Artur Tarkhanyan** has no English Wikipedia article. A second Wikidata search under "Arthur Tarkhanyan" found him
  (Q4452251, 1932–2006); his dates and awards come from Wikidata, his buildings from the articles on Tsitsernakaberd,
  Zvartnots Airport and the Karen Demirchyan Complex. The Rossiya Cinema could not be sourced and is not named.
- **Architectus**: the Wikidata search matched a 2020 video game, and Wikipedia gives no founding year, so the entry
  has `"qid": null` and an empty `born_died`. Its Sydney Modern building is "Naala Badu" in the source; the wall's
  name says "Naala Nura".
- **Behnisch & Partner** has no English article of its own; the write-up uses Günter Behnisch's article. The NORD/LB
  building in Hanover is listed both in his works and in Behnisch Architekten's (his son's firm); noted on the fact.
- **Raili and Reima Pietilä** share all five wall buildings. Each write-up leads with a different part of their
  joint work so the two pages do not repeat each other.
- Wall buildings left out for want of a source: Yamaguchi Prefectural Museum (Sakakura), Brasília Bus Station
  (Costa), Rectorate Tower (Pani), Hotel Nacional de Cuba (McKim, Mead & White), Colección Fortabat and Carrasco
  Airport (Viñoly), Hotakubo Housing and Saitama Prefectural University (Riken Yamamoto; Wikidata gives no
  architect), Meguro City Office and Prince Kyoto Takaragaike (Murano), Jaú Bus Station (Artigas), Bauhaus-Archiv
  (Gropius), Glaspalast Sindelfingen (Behnisch), Rossiya Cinema (Tarkhanyan).
- Disagreements, noted on the facts: Mario Pani's birth date (Wikipedia 29 March, Wikidata 20 March 1911); the height
  and year of the Adziogol Lighthouse (70 m and 1910 in Shukhov's article, 64 m in its own, 1911 on the wall; no
  height used); and several building years that differ from the wall's (Parque Guinle, Diagoon Houses, Morumbi, The
  Circle, Future University Hakodate, School of the Arts). The wall's years are used in the text.

## Batch 4 notes
- Two architects have only two checked links: **Louis Sullivan** (the Art Institute of Chicago collection answers 403;
  Architectuul has no page) and **Mahendra Raj** (the Kiran Nadar Museum's exhibition page answers 401 or 404; the
  MASH India review loads but the name check cannot see his name).
- Left out after the checker: ArchDaily office pages for Yamasaki, Erickson, Sullivan and Wilford (404; the tag pages
  are used instead where they work), spacea.com and morphosis.com (built by JavaScript), melnikovhouse.org and
  www.dentoncorkermarshall.com (certificate errors; dentoncorkermarshall.com without "www" works and is used), the
  Harvard GSD Kikutake exhibition page (404), and ArchDaily's ELEMENTAL page (Aravena's name is not on it).
- Two Wikidata attributions failed: the Gabriel García Márquez Cultural Center has no architect on Wikidata and no
  English article, so it was taken out of Salmona's text; Bolgen's architect on Wikidata is the firm, not the man,
  so it is sourced instead from the Henning Larsen Architects article, which lists it as "The Wave" (Bølgen), 2009.
- Wikidata spells Aravena's name "Alejandro Alavena" (Q3609433); the write-up uses the correct spelling.
- Wall buildings with no source, so not named in the text: RCR's La Lira Theatre Public Space, Tossols-Basil
  Athletics Track and Crematorium Hofheide; Snøhetta's Norwegian Wild Reindeer Pavilion and Powerhouse Brattørkaia.
- Disagreements, noted on the facts: RCR's founding (Wikipedia 1988, Wikidata 1987); Nikken Sekkei's founding
  (Wikidata 1900); Michael Wilford's birthplace (Hartfield or Surbiton in the same article, neither used); the Fashion
  and Textile Museum called Legorreta's "only building in Europe" though his works list has Madrid and Bilbao (not
  used); several building years differ from the wall (Diamond Ranch, Hôtel Tassel, Bozar, Shri Ram Centre,
  Musikhochschule, Garden & House, Quinta Monroy, Villa Verde, Hospital Naval). The wall's years are used in the text.

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
- `python -u tools/check_overview_links.py --files bios_04.json` (link check, and the Wikidata check of facts that
  carry `architect_qid`)
- `python -u tools/fetch_architect_sources.py --pages tools/architect_bios/pages_09.json` (saves other-language
  Wikipedia articles and other pages into `page_sources.json`)
