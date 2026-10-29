#!/usr/bin/env python3
"""Which building pages Google may index (owner's decision, 29 Oct 2026, after Google dropped the site on 25 Oct).

Google judges a site by all its pages. Building pages that Google never showed once are template pages with little text
of their own, so they stay on the wall and in every link but carry noindex and leave the sitemap. Building pages that
Google showed at least once before the drop stay indexable. The list is written once and kept by hand afterwards.

Reads  Search Console (GSC_SERVICE_ACCOUNT secret): every page with at least one web impression, 1 Sep to 24 Oct 2026
Writes tools/seo/index_keep.txt   one building id per line; build_pages.py makes only these building pages indexable

Runs on GitHub Actions (.github/workflows/index-keep.yml); the cloud chats cannot reach Google.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_search_console as g

START, END = '2026-09-01', '2026-10-24'  # before the drop on 25 Oct
OUT = Path(__file__).resolve().parent / 'seo' / 'index_keep.txt'

tok = g.access_token()
site = g.pick_site(tok)
rows = g.query(tok, site, START, END, ['page'], rows=25000)
ids = sorted({r['page'].split('/buildings/', 1)[1].strip('/') for r in rows
              if '/buildings/' in r['page'] and r['impressions'] > 0 and r['page'].split('/buildings/', 1)[1].strip('/')})
OUT.write_text(f'# Building pages Google may index: shown at least once in Google search, {START} to {END}.\n'
               '# Made by tools/index_keep.py; add an id by hand when its page gains real written text.\n'
               + '\n'.join(ids) + '\n')
print(f'{len(rows)} pages with impressions, {len(ids)} building pages kept')
