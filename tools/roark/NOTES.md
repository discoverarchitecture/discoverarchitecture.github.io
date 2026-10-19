# roark.archi: what we found (19 Oct 2026)

A one-off look at about 20 public pages (home, about, terms, content and rights, sitemaps, a few building and
architect pages), to plan a photo extraction the owner asked about.

- **What it is:** an archive of important buildings run by Soliton Co. Its structure comes from Wikidata. Its
  photographs, plans and drawings come from Wikimedia Commons, Europeana and the Art Institute of Chicago, each with
  author, licence and source. Pages are `/p/<building>`, `/a/<architect>` (about 385 architects), and `/i/<image>`.
  There is also `/e/<id>`: members' "curated" images, often taken from Divisare, Fubiz and similar sites. Those are
  copyrighted and never usable here.
- **Its terms (8 Oct 2026, section 3) forbid** "download or copy the archive in bulk, by script or otherwise".
  robots.txt welcomes search engines only. So we do not scrape Roark. The survey script and the saved pages were
  removed from this repository.
- **The same photos are available at their sources, which allow bulk use:**
  - Wikimedia Commons, which we already use. Roark's lead photos are often Commons "Quality images" or "Featured
    pictures".
  - Europeana's API, using only items marked CC0, PD, CC BY or CC BY-SA.
  - The Art Institute of Chicago's open API, where public-domain images are CC0, including its architectural drawings.
- **Allowed:** browsing Roark by hand for study, and noting a Commons file name to fetch from Commons ourselves. We may
  also ask Soliton Co for permission or a data export (the owner writes; Claude doesn't sign up or send email).
