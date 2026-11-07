"""Studio FGA guides (site/studio/guides/): short, useful articles for architecture students, one search question each.

    python3 tools/build_guides.py          # rewrite site/studio/guides/index.html and every guide, and stamp ?v=

Each guide is a Markdown file in tools/studio_guides/<slug>.md, written by hand. Edit the .md, then rerun this; never edit
the HTML. The file starts with a few `key: value` lines (slug, title, seo_title, description, kicker, published, related),
(add `updated: YYYY-MM-DD` when a guide changes a lot), then a line `---`, then the article:

    The first paragraph is the short answer, shown large under the title.
    ## A section            -> <h2>
    ### A smaller heading   -> <h3>
    - item / 1. item       -> lists
    **bold**, *italic*, [text](/studio/) and [text](guide:other-slug) for a link to another guide
    ![alt text](/studio/sample/thumbs/board.jpg)   -> a picture; put two or three such lines in one block to set them
    Caption: what the picture honestly is             side by side, and end the block with a `Caption:` line
    ## FAQ                 -> the last section: each `### question` and the paragraph under it becomes a visible
                              question and answer, and FAQPage data for search engines

Pictures may only come from our own files (IMAGES_OK below): the Law Garden sample, which the student allowed us to
use, the before/after picture and the preview screen. Never site/studio/board.webp (a Salk Institute precedent board
with other people's photos) and never anything from studio/references/. Width and height are read from the file.

Every guide gets the same calls to action (owner, 5 Nov 2026: "ensure the button to get them to use our product is
prominent"): a card under the intro, a closing box, and a slim bar at the bottom of the screen (guides.js) that shows
once the reader has scrolled past the card. Each link carries ?ref=guides-top / guides-end / guides-bar (and the
in-text links ?ref=guides-text) so GoatCounter can tell them apart.

The pages share the Studio look (../app.css, the same tokens as the legal pages from tools/build_studio.py) plus
guides.css for the article parts. Rerun this after app.css or guides.css changes so the ?v= stamps follow them.

It also puts every guide, with its date as <lastmod>, into site/sitemap.xml and rewrites the "## Studio FGA guides"
list in site/llms.txt, so a new guide is findable as soon as it is merged (the deploy then tells Bing through IndexNow).
Before writing a new guide, read tools/studio_guides/CHECKLIST.md.
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
CTA_PIC = ('<img class="gcta-pic" src="/studio/og.jpg?v=2" width="1200" height="630" loading="lazy" decoding="async" '
           'alt="Before and after: a student\'s six rough drawing sheets, an arrow, and the finished A1 board made from them">')
# The landing's sparkle (site/studio/app.js SPARK), so the button reads as the same "Start free" button.
SPARK = ('<svg class="spark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.2 6.3L20.5 10.5l-6.3 2.2L12 19l-2.2-6.3L3.5 '
         '10.5l6.3-2.2z"/><path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/></svg>')
SITE_DIR = os.path.join(ROOT, "site")
# Pictures a guide may show: only our own (see the note at the top).
IMAGES_OK = ("/studio/sample/", "/studio/og.jpg", "/studio/preview-shot.webp")
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
        elif href == "/studio/":
            href = "/studio/?ref=guides-text"
        return f'<a href="{href}">{label}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def blocks(md):
    """Splits Markdown into (kind, payload) blocks: h2, h3, p, ul, ol."""
    out = []
    for chunk in re.split(r"\n\s*\n", md.strip()):
        lines = [l.rstrip() for l in chunk.strip().split("\n")]
        first = lines[0]
        if IMG.match(first):
            cap = lines[-1][len("Caption:"):].strip() if lines[-1].startswith("Caption:") else ""
            pics = lines[:-1] if cap else lines
            if not cap or not 1 <= len(pics) <= 3 or not all(IMG.match(l) for l in pics):
                raise SystemExit(f"a picture block is one to three ![alt](src) lines, then a Caption: line: {chunk[:80]}")
            out.append(("fig", {"pics": [IMG.match(l).groups() for l in pics], "cap": cap}))
        elif first.startswith("### "):
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


IMG = re.compile(r"^!\[([^\]]+)\]\((/studio/[^)\s]+)\)$")


def image_size(src):
    """(width, height) of one of our pictures, read from the file's header (JPEG, PNG or WebP), so no library is needed."""
    if not src.startswith(IMAGES_OK) or ".." in src:
        raise SystemExit(f"picture not allowed in a guide (only our own files, see IMAGES_OK): {src}")
    path = os.path.join(SITE_DIR, src.split("?")[0].lstrip("/"))
    if not os.path.exists(path):
        raise SystemExit(f"picture not found: {src}")
    b = open(path, "rb").read()
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8 ":
            return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
        if kind == b"VP8L":
            n = int.from_bytes(b[21:25], "little")
            return (n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1
        if kind == b"VP8X":
            return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    if b[:2] == b"\xff\xd8":
        i = 2
        while i < len(b):
            while b[i] != 0xFF:
                i += 1
            while b[i] == 0xFF:
                i += 1
            marker, size = b[i], int.from_bytes(b[i + 1:i + 3], "big")
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return int.from_bytes(b[i + 6:i + 8], "big"), int.from_bytes(b[i + 4:i + 6], "big")
            i += 1 + size
    raise SystemExit(f"cannot read the size of {src}")


def figure(fig, slugs, up):
    """One to three pictures side by side, each column as wide as its picture's shape so they line up at one height."""
    pics, cols = [], []
    for alt, src in fig["pics"]:
        w, h = image_size(src)
        cols.append(f"minmax(0,{w / h:.3f}fr)")
        pics.append(f'<img src="{esc(src)}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(alt)}">')
    w, h = image_size(fig["pics"][0][1])
    tall = " tall" if len(pics) == 1 and h > w else ""
    return (f'<figure class="gfig{tall}"><div class="gfig-pics" style="--cols:{" ".join(cols)}">{"".join(pics)}</div>'
            f'<figcaption>{inline(fig["cap"], slugs, up)}</figcaption></figure>')


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
        elif kind == "fig":
            h.append(figure(val, slugs, up))
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
        if not name.endswith(".md") or name[:-3].isupper():  # CHECKLIST.md and other notes in capitals are not guides
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
        text = "\n".join(l for l in body.split("\n") if not IMG.match(l) and not l.startswith("Caption:"))
        g["words"] = len(re.sub(r"<[^>]+>", " ", text.replace("## FAQ", "")).split())
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


def cta_button(ref, page):
    """The landing's shiny lime button. ?ref= tells GoatCounter where the visit came from; the click event says which page."""
    return (f'<a class="btn shiny" href="/studio/?ref={ref}" data-goatcounter-click="studio/guides/cta/{ref}/{page}" '
            f'data-goatcounter-title="Studio · guides · {ref} · {page}">{SPARK}<span class="cta"><b>Try Studio FGA free</b>'
            f'<small>Free preview · no login</small></span><span class="arrow" aria-hidden="true">→</span></a>')


def cta_card(where, page):
    """The card under the intro (where="top") and the closing box (where="end"): the same size, picture and button."""
    head = "Messy drawings → jury-ready board" if where == "top" else "Jury coming up? Get your A1 board and deck."
    return (f'<aside class="gcta gcta-{where}" aria-label="Studio FGA"><div class="gcta-pic-wrap">{CTA_PIC}</div>'
            f'<div class="gcta-body"><p class="kicker">Studio FGA</p><p class="gcta-hd">{esc(head)}</p><p class="gcta-sub">{esc(CTA)}</p></div>'
            f'<div class="gcta-go">{cta_button("guides-" + where, page)}</div></aside>\n')


def cta_bar(page, js):
    """The slim bar at the bottom of the screen; guides.js shows it after the top card and remembers a close for the visit."""
    return (f'<div class="gbar" id="gbar" hidden><a class="gbar-go" href="/studio/?ref=guides-bar" '
            f'data-goatcounter-click="studio/guides/cta/guides-bar/{page}" data-goatcounter-title="Studio · guides · guides-bar · {page}">'
            f'<span class="gbar-t">Jury coming up? <b>Get your A1 board + deck →</b></span><span class="gbar-btn">Try free</span></a>'
            f'<button class="gbar-x" type="button" aria-label="Close this bar">×</button></div>\n'
            f'<script src="{js}?v=0" defer></script>\n')


def foot(up, bar=""):
    links = (f'<a class="link" href="{up}guides/">Guides</a> · <a class="link" href="{up}terms/">Terms</a> · '
             f'<a class="link" href="{up}privacy/">Privacy</a> · <a class="link" href="{up}refund/">Refund policy</a>')
    return (f'<footer class="lfoot wrap"><a class="logo" href="{up}"><i aria-hidden="true">✦</i>Studio FGA</a><p>{FOOTLINE}</p>'
            f'<p class="row">{links}</p>\n<p>Part of <a class="link" href="/">Find Great Architecture</a> · '
            f'findgreatarchitecture.com/studio · @findgreatarchitecture</p></footer></main>\n{bar}</body>\n</html>\n')


def topbar(up):
    return (f'<header class="top lnav"><a class="logo" href="{up}"><i aria-hidden="true">✦</i>Studio FGA</a>'
            f'<span class="spacer"></span><a class="btn small on" href="{up}?ref=guides-nav#upload">Start free</a></header>\n')


def date_text(iso):
    y, m, d = iso.split("-")
    months = "January February March April May June July August September October November December".split()
    return f"{int(d)} {months[int(m) - 1]} {y}"


def own_images(g):
    """Absolute addresses of the guide's own pictures (up to three), for the Article data, so image search can show them."""
    srcs = [src for kind, val in g["body"] if kind == "fig" for _, src in val["pics"]]
    return ["https://findgreatarchitecture.com" + s for s in dict.fromkeys(srcs)][:3]


def lastmod(g):
    return g.get("updated", g["published"])


def sitemap_entries(guides=None):
    """[(address, lastmod)] for the guides index and every guide; build_pages.py writes the same lines into sitemap.xml."""
    guides = guides if guides is not None else load()
    if not guides:
        return []
    return ([(SITE + "guides/", max(lastmod(g) for g in guides))] +
            [(f"{SITE}guides/{g['slug']}/", lastmod(g)) for g in sorted(guides, key=lambda g: g["slug"])])


def sitemap_line(url, mod=None):
    """One <url> line of sitemap.xml, the same in build_pages.py and here."""
    return f"  <url><loc>{url}</loc><lastmod>{mod}</lastmod></url>\n" if mod else f"  <url><loc>{url}</loc></url>\n"


def update_sitemap(guides):
    """Puts every guide into site/sitemap.xml (with its date), so a new guide needs no full build_pages.py run."""
    p = os.path.join(SITE_DIR, "sitemap.xml")
    if not os.path.exists(p):
        return
    s = open(p, encoding="utf-8").read()
    lines = "".join(sitemap_line(u, m) for u, m in sitemap_entries(guides))
    pat = re.compile(r"(?:  <url><loc>" + re.escape(SITE) + r"guides/[^<]*</loc>(?:<lastmod>[^<]*</lastmod>)?</url>\n)+")
    s = pat.sub(lambda m: lines, s, count=1) if pat.search(s) else s.replace("</urlset>", lines + "</urlset>")
    open(p, "w", encoding="utf-8").write(s)


def update_llms(guides):
    """Rewrites the "## Studio FGA guides" part of site/llms.txt (the summary AI assistants read) from the guides."""
    p = os.path.join(SITE_DIR, "llms.txt")
    if not os.path.exists(p):
        return
    s = open(p, encoding="utf-8").read()
    part = ("## Studio FGA guides\n\nPractical guides for architecture students, written by an architect (CEPT University):\n\n" +
            "".join(f"- [{g['title']}]({SITE}guides/{g['slug']}/): {g['description']}\n" for g in guides) + "\n")
    pat = re.compile(r"## Studio FGA guides\n.*?(?=^## |\Z)", re.S | re.M)
    if pat.search(s):
        s = pat.sub(lambda m: part, s, count=1)
    else:
        s = s.replace("## Browse buildings", part + "## Browse buildings", 1)
    open(p, "w", encoding="utf-8").write(s)


def guide_page(g, by_slug):
    slugs, up = set(by_slug), "../../"
    url = f"{SITE}guides/{g['slug']}/"
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["description"],
           "image": own_images(g) + [OG_IMAGE], "url": url, "mainEntityOfPage": url, "datePublished": g["published"],
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
            f'{cta_card("top", g["slug"])}'
            f'{render(g["body"], slugs, "../")}\n{faq}'
            f'{cta_card("end", g["slug"])}'
            f'<nav class="related" aria-labelledby="rel"><h2 id="rel">Related guides</h2><ul>{related}</ul></nav></article>\n' +
            foot(up, cta_bar(g["slug"], "../guides.js")))


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
            f'{cta_card("top", "index")}'
            f'<ul class="glist">{cards}</ul>\n'
            f'<p>For the whole process from idea to plot, with a real student board before and after, read '
            f'<a href="/guides/a1-presentation-board/">How to make an A1 architecture presentation board</a> on Find Great Architecture.</p>\n'
            f'{cta_card("end", "index")}</div>\n' +
            foot(up, cta_bar("index", "guides.js")))


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
    update_sitemap(guides)
    update_llms(guides)
    print("updated site/sitemap.xml and site/llms.txt")


if __name__ == "__main__":
    main()
