#!/usr/bin/env python3
"""Turn checked first-pass drafts into a batch file for tools/films_batch.py add.

  python3 tools/films_draft_to_batch.py <candidates.json> <out.json> <draft1.json> [draft2.json ...]

Run tools/films_check_draft.py first: this does not re-check the quotes, it only carries them across.

A draft names architects and buildings as its source spells them. Those names are matched against the wall here,
and a name that does not match exactly is dropped rather than bent to fit, because films_batch.py refuses a batch
holding an architect the wall does not use, and a wrong link is worse than a missing one. Facts the draft does
not have are left out, never guessed: the director, year and runtime come from Wikidata, and the one sourced
line and its quote come from the draft.
"""
import json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fold(s):
    """Spelling only: drop accents, punctuation and spacing, so "I.M. Pei" meets the wall's "I. M. Pei"."""
    return re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())


def key_of(title, year):
    """The same key films_batch.py uses. It must stay the same, or a rejected film comes back as unreviewed."""
    w = [x for x in re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', re.split(r'[:(]', title or '')[0])
         .encode('ascii', 'ignore').decode().lower()).split() if x not in ('the', 'a', 'an')]
    return f"{' '.join(w)}|{year or ''}"


def words(s):
    return [w for w in re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).split()
            if w not in ('the', 'of', 'a', 'an', 'and', 'museum', 'institute', 'centre', 'center', 'building', 'house')]


def wall():
    t = (ROOT / 'site' / 'data' / 'buildings.js').read_text()
    B = json.loads(t[t.index('['):t.rindex(']') + 1])
    names = {a.strip() for b in B for a in b['by'].split(',')}
    by_fold = {}
    for n in names:
        by_fold.setdefault(fold(n), n)
    builds = {}
    for b in B:
        builds.setdefault(fold(b['name']), b['id'])
    return names, by_fold, builds


def wall_raw():
    """The same tables keyed by the name as written, for reporting near misses to a person."""
    t = (ROOT / 'site' / 'data' / 'buildings.js').read_text()
    B = json.loads(t[t.index('['):t.rindex(']') + 1])
    arch = {}
    for b in B:
        for a in b['by'].split(','):
            arch.setdefault(a.strip(), a.strip())
    return arch, {b['name']: f"{b['name']} [{b['id']}]" for b in B}


ALIASES = json.loads((ROOT / 'tools' / 'films' / 'aliases.json').read_text())


def main(cand_path, out_path, drafts):
    cands = {c['qid']: c for c in json.loads(Path(cand_path).read_text()) if c.get('qid')}
    names, by_fold, builds = wall()
    by_fold_raw, builds_raw = wall_raw()
    add, reject, dropped_links, near = [], [], [], []

    def near_misses(raw, table):
        """Entries sharing every distinctive word, for a person to confirm. Never linked automatically."""
        w = set(words(raw))
        return [v for k, v in table.items() if w and (w <= set(words(k)) or set(words(k)) <= w)][:3]

    for dp in drafts:
        for d in json.loads(Path(dp).read_text()):
            c = cands.get(d.get('qid'))
            if not c:
                continue
            key = key_of(c['title'], c.get('year'))
            if d.get('verdict') != 'keep':
                reject.append(key)
                continue

            arch, bld = [], []
            for raw in d.get('architects_mentioned') or []:
                hit = by_fold.get(fold(ALIASES['architects'].get(raw, raw)))
                if hit and hit.count(')') != hit.count('('):
                    # the wall splits a credit like "Venturi (with Denise Scott Brown)" on the comma, leaving a
                    # stray bracket on the name. Linking to it would print the bracket, so leave it for the data chat.
                    dropped_links.append(f"architect {hit!r} is written with a stray bracket on the wall ({c['title'][:30]})")
                    hit = None
                if hit:
                    if hit not in arch:
                        arch.append(hit)
                else:
                    dropped_links.append(f"architect {raw!r} ({c['title'][:34]})")
                    for n in near_misses(raw, {k: v for k, v in by_fold_raw.items()}):
                        near.append(f"{c['title'][:30]}: architect {raw!r} ~ {n!r}")
            for raw in d.get('buildings_mentioned') or []:
                hit = ALIASES['buildings'].get(raw) or builds.get(fold(raw))
                if hit:
                    if hit not in bld:
                        bld.append(hit)
                else:
                    dropped_links.append(f"building {raw!r} ({c['title'][:34]})")
                    for n in near_misses(raw, builds_raw):
                        near.append(f"{c['title'][:30]}: building {raw!r} ~ {n!r}")

            entry = {'key': key, 'qid': c['qid'], 'title': c['title'], 'year': c.get('year'), 'kind': d.get('kind'),
                     'genres': d.get('genres') or [], 'summary': d.get('summary'),
                     'about': {'architects': arch, 'buildings': bld},
                     'sources': [{'url': 'https://en.wikipedia.org/wiki/' + (c.get('enwiki') or '').replace(' ', '_'),
                                  'quote': d.get('summary_quote')}]}
            for field, src in (('director', c.get('director')), ('runtime_min', c.get('runtime_min')),
                               ('language', d.get('language')), ('imdb', c.get('imdb')), ('tmdb', c.get('tmdb'))):
                if src:
                    entry[field] = src
            add.append(entry)

    Path(out_path).write_text(json.dumps({'add': add, 'reject': sorted(set(reject))}, ensure_ascii=False, indent=1) + '\n')
    print(f'{len(add)} to add, {len(reject)} rejected -> {out_path}')
    print(f'{sum(1 for e in add if e["about"]["architects"] or e["about"]["buildings"])} of {len(add)} link to the wall')
    if near:
        print(f'\n{len(set(near))} near misses — the wall may hold these under another spelling, confirm by eye:')
        for x in sorted(set(near))[:20]:
            print('  ?', x)
    if dropped_links:
        print(f'\n{len(dropped_links)} names the wall does not use, left out rather than bent to fit:')
        for x in sorted(set(dropped_links))[:25]:
            print('  -', x)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
