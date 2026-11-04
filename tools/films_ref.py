#!/usr/bin/env python3
"""How a draft entry points back at the candidate it came from.

Candidates arrive from Wikidata with a `qid`, and from TMDB with none at all. The first-pass tools used to index
them by `qid` alone, so a draft about a film TMDB found could never be matched and was reported as unknown. This
module is the one place that decides what a candidate may be called, so the checker and the batch converter
cannot drift apart.
"""
import re, unicodedata


def key_of(title, year):
    """The same key films_batch.py uses. It must stay the same, or a rejected film comes back as unreviewed."""
    t = ' '.join(w for w in _fold(re.split(r'[:(]', title or '')[0]) if w not in ('the', 'a', 'an'))
    return f"{t}|{year or ''}"


def _fold(s):
    return re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', s or '')
                  .encode('ascii', 'ignore').decode().lower()).split()


def refs_of(c):
    """Every name a draft may use for this candidate, most specific first."""
    out = []
    if c.get('qid'):
        out.append(c['qid'])
    if c.get('tmdb'):
        out.append(f"tmdb:{c.get('tmdb_kind') or 'movie'}:{c['tmdb']}")
    out.append(key_of(c.get('title'), c.get('year')))
    return out


def index(cands):
    """Candidates under each of their names. The first candidate to claim a name keeps it."""
    out = {}
    for c in cands:
        for r in refs_of(c):
            out.setdefault(r, c)
    return out


def find(idx, d):
    """The candidate a draft entry points at, by whichever name it gives."""
    for r in (d.get('ref'), d.get('qid'), key_of(d.get('title'), d.get('year'))):
        if r and r in idx:
            return idx[r]
    return None


def source_url(c, quote, norm):
    """Where a quote came from: the Wikipedia article if its words are there, else the TMDB page.

    Never guesses. A quote in neither text gets no url, and the caller drops the entry rather than cite a page
    that does not hold the words.
    """
    if quote and c.get('extract') and norm(quote) in norm(c['extract']):
        return 'https://en.wikipedia.org/wiki/' + (c.get('enwiki') or c.get('title') or '').replace(' ', '_')
    if quote and c.get('overview') and norm(quote) in norm(c['overview']) and c.get('tmdb'):
        return f"https://www.themoviedb.org/{c.get('tmdb_kind') or 'movie'}/{c['tmdb']}"
    if c.get('enwiki'):
        return 'https://en.wikipedia.org/wiki/' + c['enwiki'].replace(' ', '_')
    return None
