"""Studio FGA pages (site/studio/): the three legal pages and the ?v= fingerprints.

    python3 tools/build_studio.py                      # refresh the ?v= stamps only
    python3 tools/build_studio.py --legal PATH         # also rewrite terms/, privacy/, refund/ from a legal.js

The legal text lives in the studio project (studio/legal/*.md), which the prototype's tools/build_legal.py turns
into legal.js (window.LEGAL = {...}); point --legal at that file, e.g.
~/FindGreatArchitecture/studio/prototype/app/legal.js. Rerun this after changing any file in site/studio/:
the deploy workflow's build_pages.py --stamp covers the wall's files only, not these.
"""
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO = os.path.join(ROOT, "site", "studio")
SITE = "https://findgreatarchitecture.com/studio/"
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:opsz,wght@9..40,400;"
         "9..40,600;9..40,700&family=JetBrains+Mono:wght@500;600&display=swap")
FOOTLINE = ("Studio FGA is run by Akshat Pagaria · 302, Shantinath Residency, Beawar, Rajasthan, India · hello@findgreatarchitecture.com · "
            "Payments handled by Dodo Payments, our merchant of record")
DESC = {"terms": "The terms for using Studio FGA, the board and deck maker for architecture students at findgreatarchitecture.com/studio.",
        "privacy": "How Studio FGA handles your uploads, answers and email: kept for 30 days, never sold, never used to train AI models.",
        "refund": "Studio FGA's refund policy: you preview free before you pay, and every project gets one free redo within 7 days."}


def legal_pages(path):
    s = open(path, encoding="utf-8").read()
    data = json.loads(s[s.index("{"):s.rstrip().rstrip(";").rindex("}") + 1])
    for key in ("terms", "privacy", "refund"):
        L = data[key]
        out = os.path.join(STUDIO, key)
        os.makedirs(out, exist_ok=True)
        links = ('<a class="link" href="../terms/">Terms</a> · <a class="link" href="../privacy/">Privacy</a> · '
                 '<a class="link" href="../refund/">Refund policy</a>')
        page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(L["title"])} · Studio FGA</title>
<meta name="description" content="{html.escape(DESC[key])}">
<link rel="canonical" href="{SITE}{key}/">
<meta name="theme-color" content="#FFF6EA">
<link rel="icon" type="image/png" href="../../favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../app.css?v=0">
</head>
<body data-screen="{key}">
<!-- Made from studio/legal/{key}.md by tools/build_studio.py. Edit the draft there, not this file. -->
<header class="top lnav"><a class="logo" href="../"><i aria-hidden="true">✦</i>Studio FGA</a><span class="spacer"></span><a class="btn small on" href="../#upload">Start free</a></header>
<main class="land"><article class="wrap narrow legal"><a class="link" href="../">← Back to Studio FGA</a><p class="kicker">Legal</p><h1 class="big">{html.escape(L["title"])}</h1>{L["html"]}</article>
<footer class="lfoot wrap"><a class="logo" href="../"><i aria-hidden="true">✦</i>Studio FGA</a><p>{FOOTLINE}</p><p class="row">{links}</p>
<p>Part of <a class="link" href="/">Find Great Architecture</a> · findgreatarchitecture.com/studio · @findgreatarchitecture</p></footer></main>
</body>
</html>
"""
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
        print("wrote", os.path.relpath(os.path.join(out, "index.html"), ROOT))


def stamp():
    """Every local script and style sheet named with ?v= gets the first 8 hex of its content's hash."""
    pages = [os.path.join(STUDIO, "index.html")] + [os.path.join(STUDIO, k, "index.html") for k in ("terms", "privacy", "refund")]
    for p in pages:
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()

        def fp(m):
            ref = m.group(2)
            f = os.path.normpath(os.path.join(os.path.dirname(p), ref))
            if not os.path.exists(f):
                return m.group(0)
            return '%s="%s?v=%s"' % (m.group(1), ref, hashlib.sha1(open(f, "rb").read()).hexdigest()[:8])
        s2 = re.sub(r'(src|href)="([^":?]+)\?v=[^"]*"', fp, s)
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            print("stamped", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    if "--legal" in sys.argv:
        legal_pages(os.path.expanduser(sys.argv[sys.argv.index("--legal") + 1]))
    stamp()
