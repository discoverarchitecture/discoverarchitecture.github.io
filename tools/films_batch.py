#!/usr/bin/env python3
"""Curate candidate films into the Films shelf in batches.

  python3 tools/films_batch.py next 40          the next 40 candidates nobody has reviewed yet (compact JSON)
  python3 tools/films_batch.py add batch.json   check a batch and add it to tools/films_seed.json
  python3 tools/films_batch.py stats            write tools/films_progress.md
  python3 tools/films_batch.py count            how many candidates are left

Linking fields use the wall's own words: `architects` (names as the wall resolves them), `buildings` (wall ids),
`movements` and `topics` (values from the wall's movement, type, city and idea lists), `genres` (GENRES below),
`featured` (rank 1-5 or null), `ratings` [{source, value, scale, votes, url, checked}] (only TMDB carries a number;
IMDb and Letterboxd are `links` with no number), `imdb`, `letterboxd`, `qid`.

A batch file is {"add": [film, ...], "reject": ["candidate key", ...]}. A film has the seed fields:
id, title, year, y, kind (feature|series|episode|lecture), director[], runtime_min, language, summary,
about{architects[], buildings[]}, tags[], sources[{url, quote}], watch[{provider, country, type, url, checked}],
trailer (a YouTube video id), image{tmdb_poster, credit}. Facts with no source stay empty, never guessed.
`add` refuses the whole batch if anything is wrong: unknown kind, an architect name the wall does not use,
a building id that does not exist, a duplicate id, a missing summary or source, a summary over 200 characters,
a free watch link with no checked date, or a trailer that is not an 11-character YouTube id.
"""
import collections, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / 'tools' / 'films_seed.json'
CANDS = ROOT / 'tools' / 'films_candidates.json'
REVIEWED = ROOT / 'tools' / 'films_reviewed.json'
PROGRESS = ROOT / 'tools' / 'films_progress.md'
KINDS = ['feature', 'series', 'episode', 'lecture']
GENRES = ['Portrait of an architect', 'Building story', 'City & urbanism', 'Housing & social', 'Design process', 'Movement & history', 'Landscape & sustainability']
WATCH_TYPES = ['free', 'subscription', 'rent', 'buy']


def fold(s):
    return re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).split()


def key_of(title, year):
    t = ' '.join(w for w in fold(re.split(r'[:(]', title or '')[0]) if w not in ('the', 'a', 'an'))
    return f"{t}|{year or ''}"


def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default


def wall():
    t = (ROOT / 'site' / 'data' / 'buildings.js').read_text()
    B = json.loads(t[t.index('['):t.rindex(']') + 1])
    return B, collections.Counter(a.strip() for b in B for a in b['by'].split(',')), {b['id'] for b in B}


# Telling an architecture documentary from the noise the broad searches bring in. Two kinds of noise arrive:
# fiction (Wikipedia's "Films about architecture" holds The Brutalist and the Dwayne Johnson Skyscraper), and
# films whose subject is a structure but whose story is an event (the Twin Towers, a bridge, a city square).
# Wikidata answers the first by data: is_doc says whether it is a documentary at all. Nothing is deleted here;
# relevant() only decides what `next` puts in front of a reviewer first.
ARCH = re.compile(r'architect|architectur|urban(ism|ist|\s+plan)|city plan|town plan|bauhaus|brutalis|'
                  r'skyscraper|housing estate|built environment|landscape design|interior design|'
                  r'construction of the|design process|cityscape|city symphony', re.I)
EVENT = re.compile(r'\b9/11\b|september 11|terroris|al-qaeda|hijack|bombing|massacre|genocide|holocaust|'
                   r'\bwar\b|invasion|occupation|siege|coup|riot|uprising|'
                   r'covid|pandemic|epidemic|virus|cancer|famine|refugee|'
                   r'earthquake|tsunami|hurricane|flood|wildfire|disaster|'
                   r'murder|serial killer|kidnap|trial of|prison|drug|trafficking', re.I)
# Categories whose films are about architecture itself, so an event or a plain description need not be argued with.
TRUSTED = re.compile(r'wikipedia:(Documentary films about architecture|Films about architecture|'
                     r'Documentary films about architects|Documentary films about urban planning|'
                     r'Documentary films about buildings)', re.I)


def relevant(c):
    """True when a candidate is worth a reviewer's eye."""
    bits = [c.get('title'), c.get('wd_desc'), c.get('overview'), c.get('extract')] + list(c.get('subjects') or [])
    text = ' '.join(b for b in bits if b)
    src = ' '.join(c.get('sources') or [])
    if c.get('is_doc') is False:
        return False                      # Wikidata says it is not a documentary: fiction, however architectural
    if c.get('architects'):
        return True                       # its subject is an architect the wall already shows
    if TRUSTED.search(src) or 'architect-subject' in src:
        return True
    if EVENT.search(text) and not ARCH.search(text):
        return False                      # the building is the setting, not the subject
    return bool(ARCH.search(text))


def cmd_next(n):
    seed, reviewed = load(SEED, []), set(load(REVIEWED, []))
    have = {key_of(f['title'], f.get('year')) for f in seed}
    out = []
    for c in sorted(load(CANDS, []), key=lambda c: (-len(c.get('architects', [])), -(c.get('votes') or 0))):
        k = key_of(c['title'], c.get('year'))
        if k in reviewed or k in have or not relevant(c):
            continue
        out.append({'key': k, **{f: c.get(f) for f in ('title', 'year', 'director', 'runtime_min', 'subjects', 'architects', 'wd_desc', 'overview', 'qid', 'tmdb', 'imdb', 'votes') if c.get(f)}})
        if len(out) >= n:
            break
    print(json.dumps(out, ensure_ascii=False, indent=0))


def cmd_add(path):
    batch = json.loads(Path(path).read_text())
    seed, reviewed = load(SEED, []), load(REVIEWED, [])
    _, names, ids = wall()
    have_ids = {f['id'] for f in seed}
    have_keys = {key_of(f['title'], f.get('year')) for f in seed}
    errors, new = [], []
    for f in batch.get('add', []):
        if f.get('title') and not f.get('id'):
            f['id'] = '-'.join(fold(f['title']))[:60].strip('-')
        tag = f.get('id', '?')
        for k in ('id', 'title', 'kind', 'summary'):
            if not f.get(k):
                errors.append(f'{tag}: missing {k}')
        if f.get('kind') not in KINDS:
            errors.append(f'{tag}: unknown kind {f.get("kind")!r}')
        if len(f.get('summary', '')) > 200:
            errors.append(f'{tag}: summary is longer than 200 characters')
        if not f.get('sources'):
            errors.append(f'{tag}: no source (url and quote)')
        for s in f.get('sources', []):
            if not (s.get('url') and s.get('quote')):
                errors.append(f'{tag}: every source needs a url and a quote')
        about = f.get('about') or {'architects': f.get('architects', []), 'buildings': f.get('buildings', [])}
        for g in f.get('genres', []):
            if g not in GENRES:
                errors.append(f'{tag}: unknown genre {g!r}')
        if not f.get('genres'):
            errors.append(f'{tag}: needs at least one genre')
        if f.get('featured') not in (None, 1, 2, 3, 4, 5):
            errors.append(f'{tag}: featured must be 1-5 or null')
        for r in f.get('ratings', []):
            if r.get('source') != 'TMDB' or not (r.get('value') and r.get('checked')):
                errors.append(f'{tag}: only TMDB ratings carry a number, with a checked date')
        for a in about.get('architects', []):
            if a not in names:
                errors.append(f'{tag}: the wall has no architect named {a!r}')
        for b in about.get('buildings', []):
            if b not in ids:
                errors.append(f'{tag}: no building with id {b!r}')
        for w in f.get('watch', []):
            if w.get('type') not in WATCH_TYPES or not (w.get('provider') and w.get('country') and w.get('url')):
                errors.append(f'{tag}: a watch entry needs provider, country, url and a type of {WATCH_TYPES}')
            if w.get('type') == 'free' and not w.get('checked'):
                errors.append(f'{tag}: a free watch link needs a checked date')
        if f.get('trailer') and not re.fullmatch(r'[A-Za-z0-9_-]{11}', f['trailer']):
            errors.append(f'{tag}: trailer must be an 11-character YouTube id')
        if f.get('id') in have_ids or any(x['id'] == f.get('id') for x in new):
            errors.append(f'{tag}: id already used')
        if key_of(f.get('title', ''), f.get('year')) in have_keys:
            errors.append(f'{tag}: already on the shelf')
        try:
            y = int(f.get('y', str(f.get('year', ''))[:4]))
        except ValueError:
            errors.append(f'{tag}: year {f.get("year")!r} is not a number; give "y"'); y = 0
        new.append({'id': f.get('id'), 'title': f.get('title'), 'year': str(f.get('year') or ''), 'y': y, 'kind': f.get('kind'),
                    'director': f.get('director', []), 'runtime_min': f.get('runtime_min'), 'language': f.get('language'),
                    'summary': f.get('summary'), 'about': {'architects': about.get('architects', []), 'buildings': about.get('buildings', [])},
                    'genres': f.get('genres', []), 'topics': f.get('topics', []), 'movements': f.get('movements', []),
                    'featured': f.get('featured'), 'ratings': f.get('ratings', []), 'imdb': f.get('imdb'), 'letterboxd': f.get('letterboxd'), 'qid': f.get('qid'),
                    'tags': f.get('tags', []), 'sources': f.get('sources', []), 'watch': f.get('watch', []),
                    'trailer': f.get('trailer'), 'image': f.get('image'), 'tmdb': f.get('tmdb')})
    if errors:
        print('Batch refused, nothing added:\n  ' + '\n  '.join(errors)); sys.exit(1)
    seed += new
    keys = [f['key'] for f in batch.get('add', []) if f.get('key')] + list(batch.get('reject', []))
    SEED.write_text(json.dumps(seed, ensure_ascii=False, indent=1) + '\n')
    REVIEWED.write_text(json.dumps(sorted(set(reviewed) | set(keys)), ensure_ascii=False, indent=0) + '\n')
    print(f'Added {len(new)}, rejected {len(batch.get("reject", []))}. The shelf has {len(seed)} films.')
    cmd_stats()


def cmd_stats():
    seed, cands, reviewed = load(SEED, []), load(CANDS, []), load(REVIEWED, [])
    free = sum(1 for f in seed if any(w['type'] == 'free' for w in f.get('watch', [])))
    lines = ['# Films progress', '', '| | |', '|---|---|', f'| Films on the shelf | {len(seed)} |', f'| With a free watch link | {free} |',
             f'| With a trailer | {sum(1 for f in seed if f.get("trailer"))} |',
             f'| Candidates reviewed | {len(reviewed)} of {len(cands)} |', '', '## By kind', ''] + \
            [f'- {k}: {n}' for k, n in collections.Counter(f['kind'] for f in seed).most_common()]
    PROGRESS.write_text('\n'.join(lines) + '\n')
    print(f'{len(seed)} films; {free} with a free link.')


if __name__ == '__main__':
    a = sys.argv[1:]
    {'next': lambda: cmd_next(int(a[1]) if len(a) > 1 else 40), 'add': lambda: cmd_add(a[1]), 'stats': cmd_stats,
     'count': lambda: print(sum(1 for c in load(CANDS, []) if relevant(c)), 'relevant candidates;',
                            len([c for c in load(CANDS, []) if relevant(c)]) - len(load(REVIEWED, [])), 'still unreviewed')}[a[0] if a else 'stats']()
