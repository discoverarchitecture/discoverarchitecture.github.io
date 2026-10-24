#!/usr/bin/env python3
"""Save the text of web pages, so a checker without open internet access can quote them.

  python -u tools/fetch_pages.py tools/cheap/handwritten_urls.json tools/cheap/handwritten_pages

The list holds {qid, url, publisher}. Each page's readable text (scripts, styles and tags removed) is written to
<out>/<n>.txt with the URL on the first line, and <out>/index.json says which file holds which URL and whether the
fetch worked. PDFs are turned into text with pypdf when it is installed. Runs on GitHub Actions (run-tool.yml).
"""
import html, io, json, re, sys, time, urllib.request
from pathlib import Path

UA = {'User-Agent': 'Mozilla/5.0 (compatible; FindGreatArchitecture/1.0; +https://findgreatarchitecture.com/)'}


def text_of(raw, ctype):
    if 'pdf' in ctype or raw[:4] == b'%PDF':
        try:
            from pypdf import PdfReader
        except ImportError:
            return '(PDF: pypdf not installed)'
        return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages)
    s = raw.decode('utf-8', 'replace')
    s = re.sub(r'(?is)<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>', ' ', s)
    s = re.sub(r'(?i)<br\s*/?>|</p>|</h\d>|</li>|</div>', '\n', s)
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    lines = [' '.join(l.split()) for l in s.splitlines()]
    return '\n'.join(l for l in lines if len(l) > 2)


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for n, row in enumerate(json.loads(src.read_text(encoding='utf-8'))):
        rec = {'n': n, 'qid': row.get('qid'), 'url': row['url'], 'file': f'{n:03d}.txt', 'ok': False}
        try:
            with urllib.request.urlopen(urllib.request.Request(row['url'], headers=UA), timeout=60) as r:
                raw, ctype = r.read(), r.headers.get('Content-Type', '')
            t = text_of(raw, ctype)
            (out / rec['file']).write_text(f"{row['url']}\n\n{t}", encoding='utf-8')
            rec['ok'], rec['chars'] = True, len(t)
        except Exception as e:  # a page that won't load is noted, not fatal
            rec['error'] = str(e)[:200]
        print(f"  {n} {'ok' if rec['ok'] else 'FAIL'} {row['url'][:90]}", flush=True)
        index.append(rec)
        time.sleep(1)
    (out / 'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"{sum(r['ok'] for r in index)} of {len(index)} pages saved to {out}", flush=True)


if __name__ == '__main__':
    sys.exit(main())
