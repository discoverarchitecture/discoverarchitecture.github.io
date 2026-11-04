#!/usr/bin/env python3
"""Fill in each curated film's poster, score and where-to-watch from TMDB. Writes tools/films_seed.json.

  python3 tools/fetch_films_tmdb.py [--force]

Needs the repository secret TMDB_API_KEY, so it runs on GitHub Actions (first line of tools/films_request.txt:
python -u tools/fetch_films_tmdb.py). Without the key it stops and changes nothing.

For each film on the shelf it finds the TMDB record — by the id Wikidata already gave, else by title and year —
and saves:
  * `tmdb` and `tmdb_kind`, so a later run goes straight there;
  * `image`: the poster path and its credit;
  * `ratings`: TMDB's score only. IMDb's and Letterboxd's numbers stay off the site, because IMDb's data is
    licensed for non-commercial use and this site may carry ads later;
  * `watch`: the services per country, which TMDB takes from JustWatch. Both are credited on the page.
    Only the countries in COUNTRIES are kept, so the file a phone downloads stays small.

A film TMDB does not have keeps its four plain links and loses nothing. Facts already in the seed are never
overwritten: this only fills what is empty, so a hand-checked line always wins.
"""
import io, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / 'tools' / 'films_seed.json'
REPORT = ROOT / 'tools' / 'films_tmdb_report.md'
IMG_DIR = ROOT / 'site' / 'images' / 'films'
LOGO_DIR = IMG_DIR / 'p'
THUMB_W = 342          # the width the wall shows a poster at
WIDE_W = 1280          # the wide still behind the Top 5 hero
IMAGE = 'https://image.tmdb.org/t/p/'
TMDB = 'https://api.themoviedb.org/3'
UA = 'FindGreatArchitecture/1.0 (https://findgreatarchitecture.com/)'
# Western countries first, as the audience is, plus India where a good deal of the under-represented work sits.
COUNTRIES = ['US', 'GB', 'DE', 'FR', 'CA', 'AU', 'IN']
# TMDB's own words for how a film is offered; "flatrate" is a subscription anyone with that service can watch.
KINDS = {'free': 'free', 'ads': 'free', 'flatrate': 'subscription', 'rent': 'rent', 'buy': 'buy'}
# TMDB gives a two-letter code; the page shows a name, because "ja" tells a reader nothing. A code with no name
# here is left out rather than printed raw.
LANGS = { "en": "English", "ja": "Japanese", "de": "German", "fr": "French", "es": "Spanish", "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ca": "Catalan", "sv": "Swedish", "da": "Danish", "no": "Norwegian", "fi": "Finnish", "pl": "Polish", "cs": "Czech", "ru": "Russian", "zh": "Chinese", "ko": "Korean", "hi": "Hindi", "ml": "Malayalam", "bn": "Bengali", "ta": "Tamil", "ar": "Arabic", "he": "Hebrew", "tr": "Turkish", "fa": "Persian", "el": "Greek", "hu": "Hungarian", "ro": "Romanian", "sr": "Serbian", "hr": "Croatian", "sl": "Slovenian", "sk": "Slovak", "uk": "Ukrainian", "is": "Icelandic" }


def get(url, key):
    sep = '&' if '?' in url else '?'
    for attempt in range(5):
        try:
            req = urllib.request.Request(f'{url}{sep}api_key={key}', headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read())
            time.sleep(0.3)
            return out
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(int(e.headers.get('Retry-After') or 0) or 5 * (attempt + 1)); continue
            print(f'  HTTP {e.code} {url.split("?")[0][-48:]}', file=sys.stderr)
            return None
        except Exception as e:
            print(f'  retry after {e}', file=sys.stderr); time.sleep(3 * (attempt + 1))
    return None


def fetch(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            print(f'  image retry after {e}', file=sys.stderr); time.sleep(2 * (attempt + 1))
    return None


def save_thumb(data, path, width):
    """Save a small WebP of our own. The posters are hotlinked no longer: image.tmdb.org is blocked by some
    networks, India's among them, and a reader there saw empty boxes. The site serves the thumbnail and TMDB is
    still credited and linked, as the book covers are from Open Library."""
    try:
        im = Image.open(io.BytesIO(data))
    except Exception as e:
        print(f'  not an image: {e}', file=sys.stderr); return None
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA' if 'A' in im.mode else 'RGB')
    im.thumbnail((width, width * 3), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, 'WEBP', quality=82, method=6)
    return im.size


def fold(s):
    return re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())


def find(f, key):
    """The film's TMDB record: the id Wikidata gave, else a title search that must match the title closely."""
    for kind in (['tv'] if f.get('kind') == 'series' else ['movie', 'tv']):
        if f.get('tmdb'):
            d = get(f'{TMDB}/{kind}/{f["tmdb"]}', key)
            if d and d.get('id'):
                return kind, d
        q = urllib.parse.quote(f['title'])
        d = get(f'{TMDB}/search/{kind}?query={q}' + (f'&year={f["y"]}' if f.get('y') else ''), key)
        for x in (d or {}).get('results', [])[:5]:
            name = x.get('title') or x.get('name') or ''
            got_year = (x.get('release_date') or x.get('first_air_date') or '')[:4]
            # the title must really match, and the year must agree where both sides have one
            if fold(name) != fold(f['title']):
                continue
            if f.get('y') and got_year and abs(int(got_year) - int(f['y'])) > 1:
                continue
            full = get(f'{TMDB}/{kind}/{x["id"]}', key)
            if full:
                return kind, full
    return None, None


def providers(kind, tid, key):
    d = get(f'{TMDB}/{kind}/{tid}/watch/providers', key) or {}
    today, out = date.today().isoformat(), []
    for cc in COUNTRIES:
        row = (d.get('results') or {}).get(cc)
        if not row:
            continue
        for tmdb_kind, ours in KINDS.items():
            for p in row.get(tmdb_kind) or []:
                logo = None
                if p.get('logo_path') and p.get('provider_id'):
                    name = f'{p["provider_id"]}.webp'
                    if not (LOGO_DIR / name).exists():
                        raw = fetch(f'{IMAGE}w92{p["logo_path"]}')
                        if raw:
                            save_thumb(raw, LOGO_DIR / name, 92)
                    if (LOGO_DIR / name).exists():
                        logo = f'images/films/p/{name}'
                out.append({'provider': p.get('provider_name'), 'country': cc, 'type': ours,
                            'url': row.get('link'), 'checked': today, 'logo': logo})
    return out


def main(force=False):
    key = os.environ.get('TMDB_API_KEY')
    if not key:
        print('No TMDB_API_KEY: nothing changed.'); return 1
    seed = json.loads(SEED.read_text())
    found = posters = scored = watched = wides = trailers = 0
    for f in seed:
        if f.get('watch') and not force:
            continue
        kind, d = find(f, key)
        if not d:
            print(f'  not on TMDB: {f["title"][:48]}')
            continue
        found += 1
        f['tmdb'], f['tmdb_kind'] = d['id'], kind
        # the wide still for the hero, and a real trailer for its Trailer button
        if d.get('backdrop_path'):
            raw = fetch(f'{IMAGE}w{WIDE_W}{d["backdrop_path"]}')
            size = save_thumb(raw, IMG_DIR / f'{f["id"]}-wide.webp', WIDE_W) if raw else None
            if size:
                f['backdrop'] = {'local': f'images/films/{f["id"]}-wide.webp', 'w': size[0], 'h': size[1],
                                 'credit': 'TMDB', 'source': f'https://www.themoviedb.org/{kind}/{d["id"]}'}
                wides += 1
        if not f.get('trailer'):
            v = get(f'{TMDB}/{kind}/{d["id"]}/videos', key) or {}
            for x in v.get('results') or []:
                if x.get('site') == 'YouTube' and x.get('type') in ('Trailer', 'Teaser') and x.get('key'):
                    f['trailer'] = x['key']
                    trailers += 1
                    break
        if d.get('poster_path'):
            raw = fetch(f'{IMAGE}w{THUMB_W}{d["poster_path"]}')
            size = save_thumb(raw, IMG_DIR / f'{f["id"]}.webp', THUMB_W) if raw else None
            f['image'] = {'poster': d['poster_path'], 'credit': 'TMDB',
                          'source': f'https://www.themoviedb.org/{kind}/{d["id"]}'}
            if size:
                f['image'].update({'local': f'images/films/{f["id"]}.webp', 'w': size[0], 'h': size[1]})
                posters += 1
        if d.get('vote_average') and d.get('vote_count'):
            f['ratings'] = [{'source': 'TMDB', 'value': round(d['vote_average'] * 10), 'scale': 100,
                             'votes': d['vote_count'], 'url': f'https://www.themoviedb.org/{kind}/{d["id"]}',
                             'checked': date.today().isoformat()}]
            scored += 1
        # facts the seed already carries are left alone: a hand-checked line always wins
        if not f.get('runtime_min') and (d.get('runtime') or (d.get('episode_run_time') or [None])[0]):
            f['runtime_min'] = d.get('runtime') or d['episode_run_time'][0]
        if not f.get('language') and LANGS.get(d.get('original_language')):
            f['language'] = LANGS[d['original_language']]
        w = providers(kind, d['id'], key)
        if w:
            f['watch'] = w
            watched += 1
        print(f'  {f["title"][:40]:<42} tmdb {d["id"]:<8} {"poster" if d.get("poster_path") else "no poster":<10} {len(w)} services')
    SEED.write_text(json.dumps(seed, ensure_ascii=False, indent=1) + '\n')
    lines = ['# Films on TMDB', '', f'- Films on the shelf: {len(seed)}', f'- Found on TMDB: {found}',
             f'- With a poster: {posters}', f'- With a wide still for the hero: {wides}',
             f'- With a trailer: {trailers}', f'- With a TMDB score: {scored}', f'- With streaming services: {watched}',
             '', 'Services come from JustWatch, through TMDB; both are credited on the page.']
    REPORT.write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main('--force' in sys.argv))
