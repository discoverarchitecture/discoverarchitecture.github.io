#!/usr/bin/env python3
"""Reads the chosen library guides for what the owner's emails need: the librarian's name, their public contact address,
the guide's own name for the part listing free websites, and the outside sites that part already lists.
Runs on GitHub Actions (outreach-contacts.yml). The result goes into a workflow artifact kept for one day, never into
the repository and never into the log, because the repository is public. Brief: tools/outreach/BRIEF.md.

    python3 tools/outreach_contacts.py <index> <index> ...   (positions in tools/outreach/libguides.json)
"""
import html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_reading_links import UA

DIR = Path(__file__).resolve().parent / 'outreach'
KNOWN = ('archdaily', 'greatbuildings', 'archnet', 'wikiarquitectura', 'commons.wikimedia', 'sah-archipedia', 'artstor',
         'archinform', 'dezeen', 'europeana', 'loc.gov', 'riba')


def text(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())


def read(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-GB,en;q=0.9'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.geturl(), r.read(2_000_000).decode('utf8', 'replace')


def main():
    guides = json.loads((DIR / 'libguides.json').read_text())
    out = []
    for i in map(int, sys.argv[1:]):
        g = guides[i]
        rec = {'i': i, 'school': g['school'], 'guide_url': g['url']}
        try:
            final, body = read(g['url'])
        except Exception as e:
            out.append({**rec, 'error': str(e)})
            continue
        m = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
        rec['title'] = text(m.group(1)) if m else ''
        names = [text(x) for x in re.findall(r'class="[^"]*s-lib-profile-name[^"]*"[^>]*>(.*?)</', body, re.S)]
        mails = sorted({urllib.parse.unquote(x) for x in re.findall(r'mailto:([^"\'?<>\s]+@[^"\'?<>\s]+)', body)})
        rec['librarians'] = [n for n in names if n][:3]
        rec['emails'] = mails[:5]
        prof = re.findall(r'href="([^"]*(?:prf\.php\?account_id=\d+|/profile/[^"]+))"', body)
        rec['profile'] = urllib.parse.urljoin(final, prof[0]) if prof else ''
        rec['suggest_form'] = bool(re.search(r'suggest (a|an) (resource|purchase|title)', body, re.I))
        # LibGuides boxes: a title, then the box's links; find the boxes listing outside image or building sites
        boxes = re.split(r'<h2[^>]*class="[^"]*s-lib-box-title[^"]*"[^>]*>', body)[1:]
        found = []
        for b in boxes:
            title = text(b.split('</h2>', 1)[0])
            links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', b.split('</h2>', 1)[-1][:60000], re.S)
            hits = [text(t) for u, t in links if any(k in u for k in KNOWN)]
            if hits:
                found.append({'section': title, 'lists': hits[:6], 'n_links': len(links)})
        rec['sections'] = found[:4]
        out.append(rec)
        print(f"{i} {g['school']}: {len(rec['librarians'])} names, {len(rec['emails'])} addresses, {len(found)} matching sections")
    Path('contacts.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
