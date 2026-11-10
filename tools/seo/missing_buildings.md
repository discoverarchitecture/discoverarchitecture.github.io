# Buildings students search for that the wall lacks or misses (10 Nov 2026)

SEO strategy chat, task C of the second run (`marathon.md`). Source: Search Console, 28 days to 9 Nov 2026 (1,000 web
and 526 image queries), checked against `site/data/wall.js`. Impressions are small because Google is still re-judging
the site; these are leads, not proof of demand. For the **data collection chat**: check each against the usual rules
(free photo of the building itself, sourced facts) before adding. No site change was made.

The site's own "searches that found nothing" (`search/none/<words>`) were never saved, so they are not in this list:
`fetch_analytics.py` saves them in `events.csv` from 10 Nov (PR #209). Read them in a week.

## Not on the wall

| Query | Impressions | Our position | Building (to confirm) |
|---|---|---|---|
| villa baizeau | 7 | 74 | Villa Baizeau, Le Corbusier, Carthage (Tunisia) |
| casa das canoas | 2 | 55 | Casa das Canoas, Oscar Niemeyer, Rio de Janeiro |
| southbank centre | 1 | 39 | Southbank Centre, London |
| eye film museum architect | 1 | 53 | EYE Filmmuseum, Amsterdam |
| internationaal strafhof | 1 | 19 | International Criminal Court building, The Hague |
| corwin hall | 1 | 82 | Corwin Hall, Princeton |
| carigali tower | 2 | 38 | Carigali Tower, Kuala Lumpur |
| arc de triomphe | 3 | 77 | Arc de Triomphe, Paris (historic; only if it fits the wall's mix) |
| featherstone house / featherton house | 3 + 1 | 47 | unclear which building; check |
| byoma | 7 | 6 | unclear; we already show at position 6, so a page links it: check which |
| casa galardi | 1 | 40 | unclear; check |

## On the wall, but searched by another name

Google shows us low for the local-language name, because our page only uses the English one. Adding the local name
as an alternative name (page text and `search.js` aliases) is a building-page change for the data collection or
building page chat, not done here.

| Query | Impressions | Our position | Our page |
|---|---|---|---|
| fredensborghusene | 15 | 36 | Fredensborg Houses |
| hubertushuis | 6 | 9 | Hubertus House |
| erasmusbrug architect / ontwerper | 1 + 1 | 40 / 54 | Erasmus Bridge |
| flageygebouw | 1 | 56 | Flagey Building (Radio House) |
| diagoonwoningen | 1 | 8 | Diagoon Houses |
| e1027, e1027 plan, e1027 house | 3 + 1 + 1 | 41–70 | E-1027 (people type it without the hyphen) |

## Noise (ignored)

Misspellings of common words (libary, headquaters, instabul), generic searches (museum hallway, victorian house, 1930s
newspapers) and a film title that shares a building's name (abar kanchanjungha).
