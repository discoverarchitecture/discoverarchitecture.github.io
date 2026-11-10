"""Studio FGA's flow switch for the site's static pages (owner, 10 Nov 2026; studio DECISIONS D108).

The app (site/studio/app.js) reads `window.STUDIO_FLOW` from site/studio/config.js when the page opens:
    "paywall"  upload -> questions -> pay (no free preview), the default since 10 Nov 2026
    "preview"  upload -> questions -> free preview -> pay, as before
Static text that crawlers and AI tools read without running the app (the studio page's meta and <noscript>, its FAQ data,
/pricing/, /terms/, llms.txt, the wall's Studio sheet, the guides' Studio cards) cannot read config.js, so each such
sentence is kept here in both versions, and this tool writes the one that matches the setting:

    python3 tools/studio_flow.py              # follow config.js (tools/build_studio.py and tools/build_guides.py call it)
    python3 tools/studio_flow.py preview      # write the free-preview wording whatever config.js says (a check)

To flip the whole site back to the free preview: set FLOW in site/studio/config.js to "preview", then run
`python3 tools/build_studio.py`, `python3 tools/build_guides.py` and `python3 tools/guide_pages.py`, and commit. The server
must flip too (STUDIO_FLOW=preview in the Modal secret, then redeploy). Prices are not here: they are the same in both flows.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "site", "studio", "config.js")
FLOWS = ("paywall", "preview")

# (file under the repo root, preview wording, paywall wording): whole sentences, so a stray edit shows up as "not found"
VARIANTS = [
    # the studio page: meta, structured data, and the <noscript> copy AI crawlers read
    ("site/studio/index.html",
     "Get a jury-ready A1 board and a 10–15 slide deck, editable, from $6.49. Free preview first.",
     "Get a jury-ready A1 board and a 10–15 slide deck, editable, from $6.49. Free redo or money back."),
    ("site/studio/index.html",
     "into a jury-ready A1 board and a 10–15 slide jury deck, editable, with a free preview first.",
     "into a jury-ready A1 board and a 10–15 slide jury deck, editable, from $6.49, with a free redo or money back."),
    ("site/studio/index.html",
     "You preview your whole board and deck before you pay. Not jury-ready? One free redo, or your money back within 7 days.",
     "Not jury-ready? One free redo, or your money back within 7 days. Email hello@findgreatarchitecture.com with your order number."),
    ("site/studio/index.html",
     "\"name\": \"How many free previews can I make?\",\n     \"acceptedAnswer\": {\n      \"@type\": \"Answer\",\n      \"text\": "
     "\"Two a day. Each one is a full preview of your board and deck.\"",
     "\"name\": \"How long does it take?\",\n     \"acceptedAnswer\": {\n      \"@type\": \"Answer\",\n      \"text\": "
     "\"About 5 to 7 minutes after you pay. We email you the link to your board and deck when they are ready.\""),
    ("site/studio/index.html",
     "Upload, answer a few quick questions, preview free, then pay once (Polish $6.49, Transform $9.34)",
     "Upload, answer a few quick questions, pay once (Polish $6.49, Transform $9.34)"),
    ("site/studio/index.html",
     "<li>See a free preview of your whole A1 board and jury deck (two free previews a day).</li>\n"
     "      <li>Pay once, then edit in Studio's editor and download.</li>",
     "<li>Pay once: Polish $6.49 or Transform $9.34. Your board and deck are ready in about 5 to 7 minutes.</li>\n"
     "      <li>Edit in Studio's editor and download. Not jury-ready? One free redo, or your money back within 7 days.</li>"),
    ("site/studio/index.html",
     "<h3>How many free previews can I make?</h3>\n    <p>Two a day. Each one is a full preview of your board and deck.</p>",
     "<h3>How long does it take?</h3>\n    <p>About 5 to 7 minutes after you pay. We email you the link to your board and deck "
     "when they are ready.</p>"),
    # /pricing/
    ("site/pricing/index.html",
     "One payment, no subscription, free preview first.\">",
     "One payment, no subscription, free redo or money back.\">"),
    ("site/pricing/index.html",
     "You see a free preview of your whole board and deck before you pay. Everything is digital",
     "You pay once, and it is ready in about 5 to 7 minutes. Everything is digital"),
    ("site/pricing/index.html",
     "new diagrams in the same family.</td></tr>\n<tr><td>Preview</td><td>Free</td><td>A full preview of your board and deck before "
     "you pay, up to 2 a day.</td></tr>\n</tbody>",
     "new diagrams in the same family.</td></tr>\n</tbody>"),
    # /terms/ (Part 2, Studio FGA)
    ("site/terms/index.html",
     "Prices are shown in US dollars and in your local currency at checkout. The preview is free, up to 2 a day.",
     "Prices are shown in US dollars and in your local currency at checkout."),
    # llms.txt
    ("site/llms.txt",
     "InDesign. Free preview first (two a day); then one payment: Polish US$6.49",
     "InDesign. One payment: Polish US$6.49"),
    # the wall's Studio sheet (home page and every other page)
    ("site/index.html", "<p class=\"ai-fine\">Free preview first · pay once from $6.49</p>",
     "<p class=\"ai-fine\">Pay once from $6.49 · free redo or money back</p>"),
    ("site/ai.js", "'<p class=\"ai-fine\">Free preview first · pay once from $6.49</p>' +",
     "'<p class=\"ai-fine\">Pay once from $6.49 · free redo or money back</p>' +"),
    # the /guides/ cards (tools/guides/*.json, built by tools/guide_pages.py)
    ("tools/guides/a1-presentation-board.json",
     "answer a few quick questions, and see a free preview of a jury-ready A1 board and a matching jury deck. Pay once ($6.49 or $9.34) "
     "to download it",
     "answer a few quick questions, and pay once ($6.49 or $9.34) for a jury-ready A1 board and a matching jury deck, to download"),
    ("tools/guides/a1-presentation-board.json", "\"link\": \"Try it free\"", "\"link\": \"Start · from $6.49\""),
    ("tools/guides/jury-deck.json", "See a free preview first, then pay once ($6.49 or $9.34)",
     "Pay once ($6.49 or $9.34), free redo or money back,"),
    ("tools/guides/jury-presentation.json", "See a free preview first, then pay once ($6.49 or $9.34)",
     "Pay once ($6.49 or $9.34), free redo or money back,"),
    # Studio guides' article text (tools/studio_guides/*.md, built by tools/build_guides.py)
    ("tools/studio_guides/ai-tools-for-architecture-students.md",
     "answer a few questions, and get a preview of an A1 presentation board and a 10–15 slide jury deck built from your drawings. "
     "The preview is free; if you want the files, you pay once, $6.49 for Polish or $9.34 for Transform, and download",
     "answer a few questions, and pay once, $6.49 for Polish or $9.34 for Transform, for an A1 presentation board and a 10–15 slide "
     "jury deck built from your drawings. Not jury-ready? One free redo, or your money back within 7 days. You download"),
    ("tools/studio_guides/ai-tools-for-architecture-students.md", "More detail, and the free preview, is [on its page](/studio/).",
     "More detail, and real boards it made, are [on its page](/studio/)."),
    ("tools/studio_guides/ai-tools-for-architecture-students.md", "![Studio FGA's free preview screen: an A1 board",
     "![Studio FGA's layout screen: an A1 board"),
    ("tools/studio_guides/ai-tools-for-architecture-students.md", "Caption: Studio FGA's free preview screen, from the Law Garden",
     "Caption: Studio FGA's layout screen, from the Law Garden"),
    ("tools/studio_guides/ai-tools-for-architecture-students.md", "it works from your uploads, the preview is free,",
     "it works from your uploads, you pay once (from $6.49) with a free redo or your money back,"),
    ("tools/studio_guides/architecture-jury-presentation-ideas.md", "builds a matching jury deck, with a free preview, so",
     "builds a matching jury deck, from $6.49, so"),
    ("tools/studio_guides/what-architecture-jurors-look-for.md", "builds a matching jury deck; the preview is free, and",
     "builds a matching jury deck from $6.49, and"),
    ("tools/studio_guides/how-to-photograph-architecture-models.md",
     "with your drawings and a matching jury deck, with a free preview.",
     "with your drawings and a matching jury deck, from $6.49."),
    ("tools/studio_guides/architecture-concept-diagram-ideas.md", "builds the matching jury deck; the preview is free.",
     "builds the matching jury deck, from $6.49."),
    ("tools/studio_guides/architecture-presentation-board-templates.md", "jury deck that you can then edit; the preview is free.",
     "jury deck that you can then edit, from $6.49."),
    ("tools/studio_guides/architecture-sheet-sizes-a1-a0-24x36.md", "to adjust to your school's sheet; the preview is free.",
     "to adjust to your school's sheet, from $6.49."),
    ("tools/studio_guides/how-to-present-site-analysis.md", "with the rest of your drawings; the preview is free.",
     "with the rest of your drawings, from $6.49."),
]


def configured():
    """FLOW in site/studio/config.js (window.STUDIO_FLOW = "paywall" | "preview")."""
    try:
        m = re.search(r"^window\.STUDIO_FLOW\s*=\s*['\"](\w+)['\"]", open(CONFIG, encoding="utf-8").read(), re.M)
    except OSError:
        m = None
    flow = m.group(1) if m else "paywall"
    if flow not in FLOWS:
        raise SystemExit("site/studio/config.js: STUDIO_FLOW must be \"paywall\" or \"preview\", not %r" % flow)
    return flow


def apply(flow=None, quiet=False):
    """Write `flow`'s wording into every file in VARIANTS. Returns the number of sentences changed."""
    flow = flow or configured()
    changed, missing = 0, []
    for rel, preview, paywall in VARIANTS:
        want, other = (paywall, preview) if flow == "paywall" else (preview, paywall)
        p = os.path.join(ROOT, rel)
        s = open(p, encoding="utf-8").read()
        if other in s and want not in s:   # (one may contain the other: then only a missing `want` is replaced)
            s = s.replace(other, want)
            open(p, "w", encoding="utf-8").write(s)
            changed += 1
        elif want not in s:
            missing.append("%s: %s…" % (rel, want[:70]))
    if missing:
        raise SystemExit("studio_flow: these sentences were not found (edit VARIANTS to match the page):\n  " + "\n  ".join(missing))
    if not quiet:
        print("studio flow: %s (%d sentence%s changed)" % (flow, changed, "" if changed == 1 else "s"))
    return changed


if __name__ == "__main__":
    apply(sys.argv[1] if len(sys.argv) > 1 else None)
