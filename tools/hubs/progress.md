# Hub sources: progress (20 Oct 2026)

All 32 hubs done in `tools/hubs/sources.json`. Every quote was checked by script against the live Wikipedia page text; 15 facts whose quote could not be found (or was a duplicate) were removed. Every overview link was opened and loads.

## Big caveat
Only en.wikipedia.org and commons.wikimedia.org could be reached from this sandbox. Britannica, Getty, RIBA, Docomomo, SAH, UNESCO, museum and heritage sites all failed (DNS). So **every fact and link is Wikipedia or Wikimedia Commons**. Someone with open web access should add 1–2 non-Wikipedia overview links per hub. Commons category links were opened (they load) but not read in full.

## Thin hubs
| Hub | Facts | Links | Buildings | Why thin |
|---|---|---|---|---|
| parametric | 7 | 3 | 6 | only 3 of 6 buildings named by sources |
| regionalism | 8 | 2 | 6 | 2 links; only 2 buildings named by the source (others picked by the architects the page lists) |
| museums | 9 | 3 | 5 | 5 buildings |
| pavilions | 8 | 4 | 5 | 5 buildings, weak examples |
| schools-and-campuses | 8 | 3 | 3 | 3 buildings; Bauhaus Dessau implied, Apple Park is a corporate campus |
| new-york | 8 | 4 | 5 | 5 buildings |
| paris | 9 | 3 | 4 | 4 buildings (Notre-Dame, Louvre, Sainte-Chapelle not on the wall); 3 links incl. one single-building page |
| cantilever | 8 | 3 | 4 | 4 buildings, facts rest on one page |
| brise-soleil | 9 | 3 | 7 | few independent sources |

## Links that failed (dropped)
Britannica, UNESCO, Getty, RIBA, ArchDaily, NPS, Met, V&A, British Museum, nyc.gov, chicagoarchitecture.org, Los Angeles Conservancy (not reachable). Wikipedia 404s: Library_architecture, Modern_architecture_of_Berlin_housing_estates, Counter-monument, Memorial_architecture, Bauhaus_Building, Tall_timber_buildings, Kogod_Courtyard, Multihalle_Mannheim, Bruder_Klaus_Field_Chapel, Tropical_modernism, Modernist_residential_architecture, Conversion_(architecture), Solar_shading, Regionalism_(architecture). Per-hub details are under `notes.dropped` in sources.json.

## For the writer
- Building ids all exist on the wall. Some ids are not named by the source itself (see `notes`): e.g. Regionalism examples, Barbican Estate, Blue Mosque, Church of the Light, Neue Wache. Stoclet Palace is tagged Art Nouveau on the wall but Wikipedia calls it an Art Deco prototype.
- Weak facts to avoid or re-check: Hansaviertel (quote is only "Interbau"), Hollyhock House (quote is "California Romanza").
