#!/usr/bin/env python3
"""Write site/documentaries/<slug>/ pages and the index at /documentaries/.

Called from tools/build_pages.py, which passes itself in as `bp` so the pages share the wall's bar, dock, footer,
legal links and head. The films come from site/data/films.js, generated from the curated seed by
tools/make_films_data.py.

Most visitors to a film page arrive from a search, so the page carries the same facts as the opened card: what the
film is about in one sourced line, who made it, where to look for it, and the buildings on the wall it shows.

Two rules this file keeps:
  * Nothing is claimed that the shelf cannot show. There is no TMDB key yet, so no poster, no score and no list of
    streaming services; the page offers four plain links instead and says so plainly. The title and description
    promise only what the page delivers.
  * A page too thin to be worth a visit is marked noindex and kept out of the sitemap: a film with no summary, or
    with neither a director nor a year, is a stub, and sending Google to a stub costs the whole site.
"""
import json, re
from pathlib import Path

FOLDER = 'documentaries'
GENRES = ['Portrait of an architect', 'Building story', 'City & urbanism', 'Housing & social',
          'Design process', 'Movement & history', 'Landscape & sustainability']


def films(bp):
    return bp.read_js('films.js', 'FILMS') or []


def indexable(f):
    """Worth sending a searcher to: it says what it is about, and names a director or a year."""
    return bool(f.get('summary')) and bool(f.get('director') or f.get('year'))


def title_for(bp, f):
    """Name, year, then what the page offers, shortened step by step until it fits Google's 60 characters."""
    name, year = f['title'], f.get('year')
    stem = f'{name} ({year})' if year else name
    director = (f.get('director') or [None])[0]
    for t in ([f'{stem}: documentary by {director}'] if director else []) + [
            f'{stem}: architecture documentary', f'{stem}: documentary', stem, name]:
        if len(t) <= 60:
            return t
    return name[:60]


def desc_for(bp, f):
    """The sourced line, then who made it, then what else the page holds, within 155 characters."""
    out = (f.get('summary') or '').strip()
    bits = []
    d = ', '.join(f.get('director') or [])
    if d and d.lower() not in out.lower():
        bits.append(f'Directed by {d}.')
    bits.append('Where to find it, and the buildings it shows.')
    for b in bits:
        if len(out) + 1 + len(b) <= 155:
            out = f'{out} {b}'
    return out


def ld_json(bp, f, url):
    """Schema.org for the film. No rating is published: the only licensed score would be TMDB's, and the owner's
    decision is that ratings stay out of the structured data."""
    d = {'@context': 'https://schema.org', '@type': 'Movie' if f.get('kind') != 'series' else 'TVSeries',
         'name': f['title'], 'url': url}
    if f.get('summary'):
        d['description'] = f['summary']
    if f.get('director'):
        d['director'] = [{'@type': 'Person', 'name': n} for n in f['director']]
    if f.get('year'):
        d['datePublished'] = str(f['year'])
    if f.get('runtime_min'):
        d['duration'] = f'PT{int(f["runtime_min"])}M'
    if f.get('language'):
        d['inLanguage'] = f['language']
    same = [f'https://www.wikidata.org/wiki/{f["qid"]}'] if f.get('qid') else []
    if f.get('imdb'):
        same.append(f'https://www.imdb.com/title/{f["imdb"]}/')
    if same:
        d['sameAs'] = same
    if f.get('genres'):
        d['genre'] = f['genres']
    return d


def buildings_of(bp, f, by_id, by_arch):
    """The buildings the film names, then everything on the wall by the architects it is about."""
    out = [by_id[i] for i in (f.get('buildings') or []) if i in by_id]
    for a in f.get('architects') or []:
        for b in by_arch.get(a, []):
            if b not in out:
                out.append(b)
    return out


def page(bp, f, all_films, by_id, by_arch):
    e, up = bp.e, '../../'
    url = f'{bp.BASE}{FOLDER}/{f["slug"]}/'
    bs = buildings_of(bp, f, by_id, by_arch)
    meta = ' · '.join(str(x) for x in [f.get('year'), f'{f["runtime_min"]} min' if f.get('runtime_min') else None, f.get('language')] if x)

    head = bp.HEAD.format(title=e(title_for(bp, f)), desc=e(desc_for(bp, f)), url=e(url), site=bp.NAME, ogtype='article',
                          ogtitle=e(f'{f["title"]}{" — " + ", ".join(f["director"]) if f.get("director") else ""}'),
                          image=e(bp.BASE + 'og.jpg'), up=up, wallhash='#film:' + f['id'],
                          extra=('<meta name="robots" content="noindex,follow">' if not indexable(f) else '') +
                                '<link rel="stylesheet" href="' + up + 'architect.css?v=' + bp.CSS_V + '">'
                                '<script type="application/ld+json">' + json.dumps(ld_json(bp, f, url), ensure_ascii=False) + '</script>',
                          total=bp.TOTAL, css_v=bp.CSS_V)

    genres = ''.join(f'<a class="tag" href="{up}{FOLDER}/#{e(slugify(g))}">{e(g)}</a>' for g in f.get('genres') or [])
    director = ', '.join(f.get('director') or [])
    byline = f'<p class="fp-by"><i>directed by</i> <b>{e(director)}</b></p>' if director else ''

    # Where to watch, once there is TMDB data; until then the four places a student can look, named honestly.
    if f.get('watch'):
        rows = ''.join(f'<a href="{e(w["url"])}"><span>{e(w.get("type", ""))}</span>{e(w.get("provider", ""))} ↗</a>' for w in f['watch'])
        watch = f'<h2>Where to watch</h2><div class="fp-links">{rows}</div><p class="fp-note">Streaming data from JustWatch, through TMDB.</p>'
    else:
        rows = ''.join(f'<a href="{e(u)}"><span>{e(kind)}</span>{e(name)} ↗</a>' for kind, name, u in f.get('find') or [])
        watch = (f'<h2>Find it</h2><div class="fp-links">{rows}</div>'
                 f'<p class="fp-note">This shelf does not list streaming services yet, so these go straight to the places that do.</p>')

    inflm = ''
    if bs:
        who = (f.get('architects') or [None])[0]
        cards = ''.join(
            f'<a class="fp-b" href="{up}buildings/{e(b["id"])}/">'
            + (f'<span class="ph"><img src="{e(bp.at(up, b["images"][0]["thumb"]))}" alt="" loading="lazy"></span>' if (b.get('images') or []) else '<span class="ph"></span>')
            + f'<b>{e(b["name"])}</b><small>{e(b.get("year", ""))} · {e(b["place"].split(",")[0])}</small></a>'
            for b in bs[:8])
        more = ''
        if who and who in bp.ARCH:
            more = f'<a class="fp-all" href="{up}architects/{e(bp.ARCH[who])}/">All {e(who)} buildings →</a>'
        inflm = f'<h2>In the film{" · by " + e(who) if who else ""}</h2><div class="fp-bs">{cards}</div>{more}'

    kin = [x for x in all_films if x is not f and set(x.get('genres') or []) & set(f.get('genres') or [])][:6]
    more_films = ''
    if kin:
        cards = ''.join(f'<a class="fp-f" href="{up}{FOLDER}/{e(x["slug"])}/"><span class="g">{e((x.get("genres") or [""])[0])}</span>'
                        f'<b>{e(x["title"])}</b><small>{e(str(x.get("year") or ""))}</small></a>' for x in kin)
        more_films = f'<h2>More like this</h2><div class="fp-fs">{cards}</div>'

    src = ''
    if f.get('sources'):
        s = f['sources'][0]
        src = (f'<h2>Where this came from</h2><p class="fp-src">“{e(s.get("quote", ""))}” — '
               f'<a href="{e(s.get("url", ""))}">source</a></p>')

    return (head + '<main class="fp">\n'
            f'<nav class="crumbs"><a href="{up}">Find Great Architecture</a> · <a href="{up}{FOLDER}/">Documentaries</a></nav>\n'
            f'<header class="fp-head"><p class="fp-kick">{e((f.get("genres") or [""])[0])}{" · Series" if f.get("kind") == "series" else ""}</p>'
            f'<h1>{e(f["title"])}</h1>{byline}'
            f'<p class="fp-meta">{e(meta)}</p>'
            f'<div class="fp-tags">{genres}</div></header>\n'
            f'<section class="fp-about"><h2>What it is about</h2><p>{e(f.get("summary") or "")}</p></section>\n'
            f'<section class="fp-watch">{watch}</section>\n'
            + (f'<section class="fp-in">{inflm}</section>\n' if inflm else '')
            + (f'<section class="fp-more">{more_films}</section>\n' if more_films else '')
            + (f'<section class="fp-source">{src}</section>\n' if src else '')
            + bp.DOCK.replace('{up}', up)
            + f'<footer class="foot" data-nosnippet><p>Facts about each film come from Wikipedia and Wikidata, quoted and linked above.</p>'
              f'<p><a href="{up}">Find Great Architecture</a> · <a href="{up}{FOLDER}/">All documentaries</a> · <a href="{up}buildings/">All buildings</a></p>'
              f'{bp.legal_foot(up)}</footer></main>\n</body>\n</html>\n')


def slugify(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')


def index_page(bp, all_films):
    e, up = bp.e, '../'
    url = f'{bp.BASE}{FOLDER}/'
    head = bp.HEAD.format(title=f'Architecture documentaries to watch · {bp.NAME}',
                          desc=e('Documentaries about architects, buildings and cities, each with what it is about, '
                                 'where to look for it and the buildings on the wall it shows.'),
                          url=url, site=bp.NAME, ogtype='website', ogtitle='Architecture documentaries',
                          image=bp.BASE + 'og.jpg', up=up, wallhash='#documentaries',
                          extra='<link rel="stylesheet" href="' + up + 'architect.css?v=' + bp.CSS_V + '">',
                          total=bp.TOTAL, css_v=bp.CSS_V)
    out = []
    for g in GENRES:
        mine = [f for f in all_films if g in (f.get('genres') or [])]
        if not mine:
            continue
        cards = ''.join(f'<a class="fp-f" href="{up}{FOLDER}/{e(f["slug"])}/"><span class="g">{e(str(f.get("year") or ""))}</span>'
                        f'<b>{e(f["title"])}</b><small>{e(", ".join(f.get("director") or []))}</small></a>' for f in mine)
        out.append(f'<section><h2 id="{slugify(g)}">{e(g)} <span class="n">{len(mine)}</span></h2><div class="fp-fs">{cards}</div></section>')
    return (head + '<main class="fp fp-index">\n'
            f'<nav class="crumbs"><a href="{up}">Find Great Architecture</a></nav>\n'
            '<header class="fp-head"><h1>Architecture documentaries</h1>'
            '<p class="fp-lede">Films about architects, buildings and cities. Each one says what it is about, where to look for it, '
            'and which buildings on the wall it shows.</p></header>\n'
            + '\n'.join(out) + '\n'
            + bp.DOCK.replace('{up}', up)
            + f'<footer class="foot" data-nosnippet><p>Facts about each film come from Wikipedia and Wikidata, quoted and linked on its page.</p>'
              f'<p><a href="{up}">Find Great Architecture</a> · <a href="{up}buildings/">All buildings</a></p>'
              f'{bp.legal_foot(up)}</footer></main>\n</body>\n</html>\n')


def build(bp, items):
    """Write every film page and the index; remove pages left over from earlier runs. Returns the indexable urls."""
    all_films = films(bp)
    if not all_films:
        print('  no films.js yet; skipping the documentary pages')
        return []
    by_id = {b['id']: b for b in items}
    by_arch = {}
    for b in items:
        for a in bp.NM.list(b['by']) if hasattr(bp, 'NM') and bp.NM else [x.strip() for x in b['by'].split(',')]:
            by_arch.setdefault(a, []).append(b)
    out = bp.SITE / FOLDER
    out.mkdir(exist_ok=True)
    keep = set()
    for f in all_films:
        d = out / f['slug']
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(bp.outward(page(bp, f, all_films, by_id, by_arch)))
        keep.add(f['slug'])
    (out / 'index.html').write_text(bp.outward(index_page(bp, all_films)))
    for d in out.iterdir():
        if d.is_dir() and d.name not in keep:
            for x in d.iterdir():
                x.unlink()
            d.rmdir()
    urls = [f'{bp.BASE}{FOLDER}/'] + [f'{bp.BASE}{FOLDER}/{f["slug"]}/' for f in all_films if indexable(f)]
    thin = sum(1 for f in all_films if not indexable(f))
    print(f'  {len(all_films)} documentary pages; {len(urls) - 1} in the sitemap, {thin} too thin to index')
    return urls
