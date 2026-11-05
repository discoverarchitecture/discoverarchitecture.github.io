"""Studio FGA guides (site/studio/guides/): short, useful articles for architecture students, one search question each.

    python3 tools/build_guides.py          # rewrite site/studio/guides/index.html and every guide, and stamp ?v=

Each guide is a Markdown file in tools/studio_guides/<slug>.md, written by hand. Edit the .md, then rerun this; never edit
the HTML. The file starts with a few `key: value` lines (slug, title, seo_title, description, kicker, published, related),
then a line `---`, then the article:

    The first paragraph is the short answer, shown large under the title.
    ## A section            -> <h2>
    ### A smaller heading   -> <h3>
    - item / 1. item       -> lists
    **bold**, *italic*, [text](/studio/) and [text](guide:other-slug) for a link to another guide
    ## FAQ                 -> the last section: each `### question` and the paragraph under it becomes a visible
                              question and answer, and FAQPage data for search engines

The pages share the Studio look (../app.css, the same tokens as the legal pages from tools/build_studio.py) plus
guides.css for the article parts. Rerun this after app.css or guides.css changes so the ?v= stamps follow them.
"""
import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "studio_guides")
OUT = os.path.join(ROOT, "site", "studio", "guides")
SITE = "https://findgreatarchitecture.com/studio/"
OG_IMAGE = "https://findgreatarchitecture.com/studio/og.jpg?v=2"
AUTHOR = {"@type": "Person", "name": "Akshat Pagaria", "jobTitle": "Architect", "alumniOf": "CEPT University"}
PUBLISHER = {"@type": "Organization", "name": "Find Great Architecture", "url": "https://findgreatarchitecture.com/",
             "logo": {"@type": "ImageObject", "url": "https://findgreatarchitecture.com/icon-512.png"}}
CTA = "Studio FGA turns your drawings into a jury-ready A1 board and a 10–15 slide deck. Free preview first."
CTA_HREF = "/studio/?ref=guides"
# The same strings as the legal pages, so the whole of /studio/ reads as one site.
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:opsz,wght@9..40,400;"
         "9..40,600;9..40,700&family=JetBrains+Mono:wght@500;600&display=swap")
FOOTLINE = ("Studio FGA is run by Akshat Pagaria · 302, Shantinath Residency, Beawar, Rajasthan, India · hello@findgreatarchitecture.com · "
            "Payments handled by Dodo Payments, our merchant of record")
INDEX_TITLE = "Guides for Architecture Students: Boards, Juries and Decks"
INDEX_DESC = ("Practical guides for architecture students from an architect: A1 board layouts, plans and sections, "
              "jury tips, jury decks, portfolios and AI tools.")


def esc(s):
    return html.escape(s, quote=True)


# ---------- Markdown (the small part of it these guides use)

def inline(text, slugs, up):
    s = html.escape(text, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)

    def link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith("guide:"):
            slug = href[6:]
            if slug not in slugs:
                raise SystemExit(f"unknown guide in link: {href}")
            href = f"{up}{slug}/"
        return f'<a href="{href}">{label}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def blocks(md):
    """Splits Markdown into (kind, payload) blocks: h2, h3, p, ul, ol."""
    out = []
    for chunk in re.split(r"\n\s*\n", md.strip()):
        lines = [l.rstrip() for l in chunk.strip().split("\n")]
        first = lines[0]
        if first.startswith("### "):
            out.append(("h3", first[4:].strip()))
            rest = "\n".join(lines[1:]).strip()
            if rest:
                out.extend(blocks(rest))
        elif first.startswith("## "):
            out.append(("h2", first[3:].strip()))
            rest = "\n".join(lines[1:]).strip()
            if rest:
                out.extend(blocks(rest))
        elif all(re.match(r"- ", l) or l.startswith("  ") for l in lines):
            out.append(("ul", items(lines, r"- ")))
        elif all(re.match(r"\d+\. ", l) or l.startswith("  ") for l in lines):
            out.append(("ol", items(lines, r"\d+\. ")))
        else:
            out.append(("p", " ".join(l.strip() for l in lines)))
    return out


def items(lines, marker):
    res = []
    for l in lines:
        if re.match(marker, l):
            res.append(re.sub("^" + marker, "", l).strip())
        else:
            res[-1] += " " + l.strip()
    return res


def render(bl, slugs, up):
    h = []
    for kind, val in bl:
        if kind in ("h2", "h3"):
            h.append(f"<{kind}>{inline(val, slugs, up)}</{kind}>")
        elif kind == "p":
            h.append(f"<p>{inline(val, slugs, up)}</p>")
        else:
            h.append(f"<{kind}>" + "".join(f"<li>{inline(i, slugs, up)}</li>" for i in val) + f"</{kind}>")
    return "\n".join(h)


def plain(s):
    """Markdown inline -> plain text, for JSON-LD."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return re.sub(r"\*+", "", s)


# ---------- guides

def load():
    guides = []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".md"):
            continue
        raw = open(os.path.join(SRC, name), encoding="utf-8").read()
        head, body = raw.split("\n---\n", 1)
        g = {}
        for line in head.strip().split("\n"):
            k, v = line.split(":", 1)
            g[k.strip()] = v.strip()
        g["related"] = [r.strip() for r in g.get("related", "").split(",") if r.strip()]
        g["order"] = int(g.get("order", 99))
        bl = blocks(body)
        if "## FAQ" in body:
            i = bl.index(("h2", "FAQ"))
            bl, faq_bl = bl[:i], bl[i + 1:]
        else:
            faq_bl = []
        g["lede"], g["body"] = bl[0][1], bl[1:]
        faq = []
        for kind, val in faq_bl:
            if kind == "h3":
                faq.append({"q": val, "a": []})
            elif kind == "p":
                faq[-1]["a"].append(val)
        g["faq"] = faq
        g["words"] = len(re.sub(r"<[^>]+>", " ", body.replace("## FAQ", "")).split())
        if name[:-3] != g["slug"]:
            raise SystemExit(f"{name}: slug {g['slug']} does not match the file name")
        guides.append(g)
    return sorted(guides, key=lambda g: g["order"])


def head(title, desc, url, up, og_type, ld, css):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Studio FGA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="A student's rough drawing sheets beside the finished A1 presentation board made from them">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FFF6EA">
<link rel="icon" type="image/png" href="{up}../favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{up}app.css?v=0">
<link rel="stylesheet" href="{css}?v=0">
<script src="{up}../analytics.js"></script>
""" + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld) + "</head>\n"


def foot(up):
    links = (f'<a class="link" href="{up}guides/">Guides</a> · <a class="link" href="{up}terms/">Terms</a> · '
             f'<a class="link" href="{up}privacy/">Privacy</a> · <a class="link" href="{up}refund/">Refund policy</a>')
    return (f'<footer class="lfoot wrap"><a class="logo" href="{up}"><i aria-hidden="true">✦</i>Studio FGA</a><p>{FOOTLINE}</p>'
            f'<p class="row">{links}</p>\n<p>Part of <a class="link" href="/">Find Great Architecture</a> · '
            f'findgreatarchitecture.com/studio · @findgreatarchitecture</p></footer></main>\n</body>\n</html>\n')


def topbar(up):
    return (f'<header class="top lnav"><a class="logo" href="{up}"><i aria-hidden="true">✦</i>Studio FGA</a>'
            f'<span class="spacer"></span><a class="btn small on" href="{up}#upload">Start free</a></header>\n')


def date_text(iso):
    y, m, d = iso.split("-")
    months = "January February March April May June July August September October November December".split()
    return f"{int(d)} {months[int(m) - 1]} {y}"


def guide_page(g, by_slug):
    slugs, up = set(by_slug), "../../"
    url = f"{SITE}guides/{g['slug']}/"
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["description"],
           "image": OG_IMAGE, "url": url, "mainEntityOfPage": url, "datePublished": g["published"],
           "dateModified": g.get("updated", g["published"]), "author": AUTHOR, "publisher": PUBLISHER, "inLanguage": "en"},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Studio FGA", "item": SITE},
              {"@type": "ListItem", "position": 2, "name": "Guides", "item": SITE + "guides/"},
              {"@type": "ListItem", "position": 3, "name": g["title"], "item": url}]}]
    if g["faq"]:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(f["q"]), "acceptedAnswer": {"@type": "Answer", "text": plain(" ".join(f["a"]))}}
            for f in g["faq"]]})
    title = g["seo_title"] + " · Studio FGA" if len(g["seo_title"]) <= 52 else g["seo_title"]
    faq = ""
    if g["faq"]:
        faq = ('<section class="gfaq" aria-labelledby="faq"><h2 id="faq">Questions students ask</h2>' +
               "".join(f'<h3>{inline(f["q"], slugs, "../")}</h3>' + "".join(f"<p>{inline(a, slugs, '../')}</p>" for a in f["a"])
                       for f in g["faq"]) + "</section>\n")
    related = "".join(f'<li><a href="../{r}/">{esc(by_slug[r]["title"])}</a></li>' for r in g["related"])
    return (head(title, g["description"], url, up, "article", ld, "../guides.css") +
            f'<body data-screen="guide">\n<!-- Made from tools/studio_guides/{g["slug"]}.md by tools/build_guides.py. Edit the .md there, not this file. -->\n' +
            topbar(up) +
            f'<main class="land"><article class="wrap narrow gpage"><a class="link" href="../">← All guides</a>'
            f'<p class="kicker">Guide · {esc(g["kicker"])}</p><h1 class="big">{esc(g["title"])}</h1>'
            f'<p class="lede">{inline(g["lede"], slugs, "../")}</p>'
            f'<p class="byline">By Akshat Pagaria, architect · <time datetime="{g["published"]}">{date_text(g["published"])}</time></p>\n'
            f'{render(g["body"], slugs, "../")}\n{faq}'
            f'<aside class="cta-box"><p>{esc(CTA)}</p><a class="btn primary" href="{CTA_HREF}">Try Studio FGA free →</a></aside>\n'
            f'<nav class="related" aria-labelledby="rel"><h2 id="rel">Related guides</h2><ul>{related}</ul></nav></article>\n' +
            foot(up))


def index_page(guides):
    up, url = "../", SITE + "guides/"
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": INDEX_TITLE, "description": INDEX_DESC, "url": url,
           "publisher": PUBLISHER, "hasPart": [{"@type": "Article", "headline": g["title"], "url": f"{url}{g['slug']}/"} for g in guides]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Studio FGA", "item": SITE},
              {"@type": "ListItem", "position": 2, "name": "Guides", "item": url}]}]
    cards = "".join(f'<li class="card"><p class="kicker">{esc(g["kicker"])}</p><h2><a href="{g["slug"]}/">{esc(g["title"])}</a></h2>'
                    f'<p>{esc(g["description"])}</p></li>' for g in guides)
    return (head("Guides for Architecture Students · Studio FGA", INDEX_DESC, url, up, "website", ld, "guides.css") +
            '<body data-screen="guides">\n<!-- Made by tools/build_guides.py from tools/studio_guides/*.md. Edit those, not this file. -->\n' +
            topbar(up) +
            f'<main class="land"><div class="wrap narrow gpage"><a class="link" href="../">← Back to Studio FGA</a>'
            f'<p class="kicker">Guides</p><h1 class="big">Guides for architecture students</h1>'
            f'<p class="lede">Plain, practical advice on presentation boards, plans and sections, jury presentations and decks, '
            f'written by an architect. Each one works whether or not you ever use Studio FGA.</p>\n'
            f'<ul class="glist">{cards}</ul>\n'
            f'<p>For the whole process from idea to plot, with a real student board before and after, read '
            f'<a href="/guides/a1-presentation-board/">How to make an A1 architecture presentation board</a> on Find Great Architecture.</p>\n'
            f'<aside class="cta-box"><p>{esc(CTA)}</p><a class="btn primary" href="{CTA_HREF}">Try Studio FGA free →</a></aside></div>\n' +
            foot(up))


def stamp(paths):
    """Every local script and style sheet named with ?v= gets the first 8 hex of its content's hash (as build_studio.py)."""
    for p in paths:
        s = open(p, encoding="utf-8").read()

        def fp(m):
            ref = m.group(2)
            f = os.path.normpath(os.path.join(os.path.dirname(p), ref))
            if not os.path.exists(f):
                return m.group(0)
            return '%s="%s?v=%s"' % (m.group(1), ref, hashlib.sha1(open(f, "rb").read()).hexdigest()[:8])
        open(p, "w", encoding="utf-8").write(re.sub(r'(src|href)="([^":?]+)\?v=[^"]*"', fp, s))


def main():
    guides = load()
    by_slug = {g["slug"]: g for g in guides}
    for g in guides:
        for r in g["related"]:
            if r not in by_slug:
                raise SystemExit(f"{g['slug']}: unknown related guide {r}")
    written = []
    for g in guides:
        folder = os.path.join(OUT, g["slug"])
        os.makedirs(folder, exist_ok=True)
        p = os.path.join(folder, "index.html")
        open(p, "w", encoding="utf-8").write(guide_page(g, by_slug))
        written.append(p)
        print(f"wrote {os.path.relpath(p, ROOT)}  ({g['words']} words)")
    p = os.path.join(OUT, "index.html")
    open(p, "w", encoding="utf-8").write(index_page(guides))
    written.append(p)
    print("wrote", os.path.relpath(p, ROOT))
    stamp(written)


if __name__ == "__main__":
    main()
