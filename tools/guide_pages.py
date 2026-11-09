#!/usr/bin/env python3
"""Guide pages at /guides/<slug>/ (owner, 3 Nov 2026; plan in tools/seo/studio_seo.md). Each guide is written by hand in
tools/guides/<slug>.json and answers one question students ask Google and AI assistants, with a short answer first,
numbered steps, a real before and after, a link to Studio FGA and an FAQ. The page uses the site's bar, footer and night
colours (site/guide.css) and carries Article, FAQPage and BreadcrumbList data.

    python3 tools/guide_pages.py            # writes site/guides/<slug>/index.html for every guide, and site/guides/index.html
"""
import json, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pages as bp

SRC = Path(__file__).resolve().parent / 'guides'
OUT = bp.SITE / 'guides'  # the same folders whichever copy of build_pages is used
SAMPLE = bp.SITE / 'studio' / 'sample'


def load():
    return [json.loads(f.read_text()) for f in sorted(SRC.glob('*.json'))]


def studio_guides():
    """Studio FGA's guides (tools/build_guides.py), so the two sets of guides link to each other."""
    import build_guides
    return build_guides.load()


def more_guides(up, n=None):
    """A list of Studio FGA's guides; `up` leads from the page to the site root."""
    gs = studio_guides()[:n] if n else studio_guides()
    return ''.join(f'<li><a href="{up}studio/guides/{g["slug"]}/"><b>{bp.e(g["title"])}</b><span>{bp.e(g["description"])}</span></a></li>'
                   for g in gs)


def images(g):
    """Copies the before/after pictures next to the page, so the guide doesn't break when the Studio sample changes."""
    ba, folder = g.get('before_after'), OUT / g['slug'] / 'img'
    if not ba:
        return []
    folder.mkdir(parents=True, exist_ok=True)
    names = []
    for rel in ba['before'] + [ba['after']]:
        src = SAMPLE / rel
        name = rel.replace('/', '-')
        if src.exists():
            shutil.copyfile(src, folder / name)
        names.append(name)
    return names


def page(g):
    up, e = '../../', bp.e
    url = f'{bp.BASE}guides/{g["slug"]}/'
    names = images(g)
    ba = g.get('before_after')
    steps = ''.join(f'<section class="step"><h2>{s["h"]}</h2>' + ''.join(f'<p>{p}</p>' for p in s['p']) + '</section>' for s in g['steps'])
    pics = ''
    if ba:
        before = ''.join(f'<img src="img/{n}" alt="Student sheet {i + 1}, before" loading="lazy">' for i, n in enumerate(names[:-1]))
        pics = (f'<section class="ba"><h2>{e(ba["h"])}</h2><p>{e(ba["p"])}</p><div class="pair">'
                f'<figure class="before"><div class="sheets">{before}</div><figcaption>Before · {len(names) - 1} sheets</figcaption></figure>'
                f'<span class="arrow" aria-hidden="true">→</span>'
                f'<figure class="after"><img src="img/{names[-1]}" alt="The finished A1 presentation board" loading="lazy"><figcaption>After · one A1 board</figcaption></figure>'
                f'</div><p class="credit">{e(ba["credit"])}</p></section>')
    c = g['cta']
    cta = (f'<aside class="cta-card"><h2>{e(c["h"])}</h2><p>{e(c["p"])}</p>'
           f'<a class="cta-go" href="{up}{c["href"]}">{e(c["link"])} →</a></aside>')
    faq = ('<section class="faq"><h2>Questions students ask</h2>' +
           ''.join(f'<details><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in g['faq']) + '</section>')
    ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': g['title'], 'description': g['description'], 'url': url,
           'datePublished': g['published'], 'dateModified': g.get('updated', g['published']),
           'author': {'@type': 'Person', 'name': g['author'], 'jobTitle': 'Architect', 'alumniOf': 'CEPT University'},
           'publisher': {'@type': 'Organization', 'name': bp.NAME, 'url': bp.BASE, 'logo': bp.BASE + 'icon-512.png'},
           'image': f'{url}img/{names[-1]}' if names else bp.BASE + 'og.jpg'},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in g['faq']]},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': bp.NAME, 'item': bp.BASE},
              {'@type': 'ListItem', 'position': 2, 'name': 'Guides', 'item': bp.BASE + 'guides/'},
              {'@type': 'ListItem', 'position': 3, 'name': g['title'], 'item': url}]}]
    extra = (f'<link rel="stylesheet" href="{up}guide.css?v={bp.fingerprint(bp.SITE / "guide.css")}">\n'
             + '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld))
    head = bp.HEAD.format(title=e(g['seo_title']), desc=e(g['description']), url=e(url), site=bp.NAME, ogtype='article',
                          ogtitle=e(g['title']), image=e(f'{url}img/{names[-1]}' if names else bp.BASE + 'og.jpg'), up=up,
                          wallhash='', extra=extra, total=bp.TOTAL, css_v=bp.CSS_V)
    body = (f'<main class="guide"><article>'
            f'<p class="kicker">{e(g["kicker"])}</p><h1>{e(g["title"])}</h1>'
            f'<p class="byline">By {e(g["author"])} · {e(g["author_note"])}</p>'
            f'<div class="answer"><p class="label">The short answer</p><p>{e(g["answer"])}</p></div>'
            f'{steps}{pics}{cta}{faq}'
            f'<section class="more"><h2>More guides</h2><ul class="guide-list">{more_guides(up, 4)}</ul>'
            f'<p><a href="{up}studio/guides/">All guides for architecture students →</a></p></section></article></main>\n')
    return head + body + bp.FOOT.format(up=up)


def index(guides):
    up, e = '../', bp.e
    items = ''.join(f'<li><a href="{g["slug"]}/"><b>{e(g["title"])}</b><span>{e(g["description"])}</span></a></li>' for g in guides)
    head = bp.HEAD.format(title=f'Guides for architecture students · {bp.NAME}', desc='Short, practical guides for architecture students: presentation boards, juries and precedent studies.',
                          url=bp.BASE + 'guides/', site=bp.NAME, ogtype='website', ogtitle='Guides for architecture students',
                          image=bp.BASE + 'og.jpg', up=up, wallhash='',
                          extra=f'<link rel="stylesheet" href="{up}guide.css?v={bp.fingerprint(bp.SITE / "guide.css")}">', total=bp.TOTAL, css_v=bp.CSS_V)
    return head + (f'<main class="guide"><h1>Guides</h1><ul class="guide-list">{items}{more_guides(up)}</ul></main>\n') + bp.FOOT.format(up=up)


def build(mod=None):
    """Called by build_pages.main() with its own module, so the pages share its fingerprints and footer."""
    global bp
    if mod is not None:
        bp = mod
    guides = load()
    for g in guides:
        (OUT / g['slug']).mkdir(parents=True, exist_ok=True)
        (OUT / g['slug'] / 'index.html').write_text(page(g))
    (OUT / 'index.html').write_text(index(guides))
    return guides


if __name__ == '__main__':
    bp.CSS_V = bp.fingerprint_all(bp.SITE / 'pages.css', bp.SITE / 'theme.css', bp.SITE / 'theme.js', bp.SITE / 'rows.js')
    print(len(build()), 'guides written')
