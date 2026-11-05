#!/usr/bin/env python3
"""Reading lists at /books/<slug>/ (owner, 5 Nov 2026: the SEO plan's best-return pages, one at a time, each better than
what ranks today). Each list is chosen by hand in tools/lists/<slug>.json from the books already on the shelf
(site/data/books.js): a short answer first, sections by when a student needs the book, the shelf's one-line reason for
each (or the list's own note), an FAQ. A shelf cover that shows the wrong book or edition is listed in hide_cover and
drawn as a plain title card. The page uses the guide's look (site/guide.css) and carries Article, ItemList
(of Books), FAQPage and BreadcrumbList data. A book id the shelf doesn't have stops the build, so a list never shows a
missing book.

    python3 tools/list_pages.py            # writes site/books/<slug>/index.html for every list, and site/books/index.html
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pages as bp

SRC = Path(__file__).resolve().parent / 'lists'
OUT = bp.SITE / 'books'


def load():
    return [json.loads(f.read_text()) for f in sorted(SRC.glob('*.json'))]


def cover(b, up, hide=False):
    c = None if hide else b.get('cover')
    if c:
        return f'<img src="{up}{bp.e(c["thumb"])}" alt="Cover of {bp.e(b["title"])}" width="{c["w"]}" height="{c["h"]}" loading="lazy" decoding="async">'
    return f'<span class="standin" aria-hidden="true"><span class="tt">{bp.e(b["title"])}</span><span class="au">{bp.e(b["by"])}</span></span>'


def book_row(b, note, up, hide=False):
    e = bp.e
    links = [f'<a href="{up}#book:{e(b["id"])}">On the shelf →</a>']
    if b.get('ol'):
        links.append(f'<a href="https://openlibrary.org/works/{e(b["ol"])}" rel="noopener">Find a copy →</a>')
    return (f'<li class="book" id="{e(b["id"])}"><div class="cv">{cover(b, up, hide)}</div><div class="tx">'
            f'<h3>{e(b["title"])}</h3><p class="by">{e(b["by"])} · {e(b["year"])}</p>'
            f'<p class="why">{e(note or b["why"])}</p><p class="go">{" ".join(links)}</p></div></li>')


def anchor(h):
    return ''.join(ch if ch.isalnum() else '-' for ch in h.lower().split(':')[0]).strip('-')


def page(g, books):
    up, e = '../../', bp.e
    url = f'{bp.BASE}books/{g["slug"]}/'
    notes, hidden = g.get('notes', {}), set(g.get('hide_cover', []))
    chosen = [books[i] for s in g['sections'] for i in s['books']]
    nav = ''.join(f'<a href="#{anchor(s["h"])}">{e(s["h"].split(":")[0])}</a>' for s in g['sections'])
    secs = ''.join(f'<section class="shelf" id="{anchor(s["h"])}"><h2>{e(s["h"])}</h2><p>{e(s["p"])}</p><ol class="books">'
                   + ''.join(book_row(books[i], notes.get(i), up, i in hidden) for i in s['books']) + '</ol></section>' for s in g['sections'])
    faq = ('<section class="faq"><h2>Questions students ask</h2>' +
           ''.join(f'<details><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in g['faq']) + '</section>')
    first_cover = next((b['cover']['src'] for b in chosen if b.get('cover') and b['id'] not in hidden), None)

    def book_ld(b):
        x = {'@type': 'Book', 'name': b['title'], 'author': {'@type': 'Person', 'name': b['by']}, 'url': f'{url}#{b["id"]}'}
        if str(b.get('y', '')).lstrip('-').isdigit() and b['y'] > 0:
            x['datePublished'] = str(b['y'])
        if b.get('isbn'):
            x['isbn'] = b['isbn']
        return x
    ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': g['title'], 'description': g['description'], 'url': url,
           'datePublished': g['published'], 'dateModified': g.get('updated', g['published']),
           'author': {'@type': 'Person', 'name': g['author'], 'jobTitle': 'Architect', 'alumniOf': 'CEPT University'},
           'publisher': {'@type': 'Organization', 'name': bp.NAME, 'url': bp.BASE, 'logo': bp.BASE + 'icon-512.png'},
           'image': first_cover or bp.BASE + 'og.jpg'},
          {'@context': 'https://schema.org', '@type': 'ItemList', 'name': g['title'], 'numberOfItems': len(chosen),
           'itemListElement': [{'@type': 'ListItem', 'position': n + 1, 'item': book_ld(b)} for n, b in enumerate(chosen)]},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in g['faq']]},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': bp.NAME, 'item': bp.BASE},
              {'@type': 'ListItem', 'position': 2, 'name': 'Reading lists', 'item': bp.BASE + 'books/'},
              {'@type': 'ListItem', 'position': 3, 'name': g['title'], 'item': url}]}]
    extra = (f'<link rel="stylesheet" href="{up}guide.css?v={bp.fingerprint(bp.SITE / "guide.css")}">\n'
             + '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld))
    head = bp.HEAD.format(title=e(g['seo_title']), desc=e(g['description']), url=e(url), site=bp.NAME, ogtype='article',
                          ogtitle=e(g['title']), image=e(first_cover or bp.BASE + 'og.jpg'), up=up,
                          wallhash='', extra=extra, total=bp.TOTAL, css_v=bp.CSS_V)
    body = (f'<main class="guide reading"><article>'
            f'<p class="kicker">{e(g["kicker"])}</p><h1>{e(g["title"])}</h1>'
            f'<p class="byline">Chosen by {e(g["author"])} · {e(g["author_note"])}</p>'
            f'<div class="answer"><p class="label">The short answer</p><p>{e(g["answer"])}</p></div>'
            f'<nav class="jump" aria-label="Sections">{nav}</nav>'
            f'{secs}<p class="how">{e(g["how"])}</p>'
            f'<aside class="cta-card"><h2>The whole shelf</h2><p>Every book on the site, filtered by shelf, idea or architect, each linked to the buildings it covers.</p>'
            f'<a class="cta-go" href="{up}#books">Browse the books →</a></aside>'
            f'{faq}</article></main>\n')
    return head + body + bp.FOOT.format(up=up)


def index(lists):
    up, e = '../', bp.e
    items = ''.join(f'<li><a href="{g["slug"]}/"><b>{e(g["title"])}</b><span>{e(g["description"])}</span></a></li>' for g in lists)
    head = bp.HEAD.format(title=f'Architecture reading lists · {bp.NAME}', desc='Reading lists for architecture students, chosen by an architect from the books on the site.',
                          url=bp.BASE + 'books/', site=bp.NAME, ogtype='website', ogtitle='Architecture reading lists',
                          image=bp.BASE + 'og.jpg', up=up, wallhash='',
                          extra=f'<link rel="stylesheet" href="{up}guide.css?v={bp.fingerprint(bp.SITE / "guide.css")}">', total=bp.TOTAL, css_v=bp.CSS_V)
    return head + f'<main class="guide"><h1>Reading lists</h1><ul class="guide-list">{items}</ul></main>\n' + bp.FOOT.format(up=up)


def build(mod=None):
    """Called by build_pages.main() with its own module, so the pages share its fingerprints and footer."""
    global bp
    if mod is not None:
        bp = mod
    books = {b['id']: b for b in bp.read_js('books.js', 'BOOKS') or []}
    lists = load()
    for g in lists:
        missing = [i for s in g['sections'] for i in s['books'] if i not in books]
        if missing:
            sys.exit(f'{g["slug"]}: not on the shelf: {", ".join(missing)}')
        (OUT / g['slug']).mkdir(parents=True, exist_ok=True)
        (OUT / g['slug'] / 'index.html').write_text(page(g, books))
    if lists:
        (OUT / 'index.html').write_text(index(lists))
    return lists


if __name__ == '__main__':
    bp.CSS_V = bp.fingerprint_all(bp.SITE / 'pages.css', bp.SITE / 'theme.css', bp.SITE / 'theme.js', bp.SITE / 'rows.js', bp.SITE / 'popup.js', bp.SITE / 'ai.css', bp.SITE / 'ai.js')
    print(len(build()), 'reading lists written')
