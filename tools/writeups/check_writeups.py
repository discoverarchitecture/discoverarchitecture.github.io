#!/usr/bin/env python3
"""Checks building write-ups against their facts before they reach a page (tools/writeups/BRIEF.md, step 2).

    python3 tools/writeups/check_writeups.py <facts files...> -- <write-up files...>

For each write-up: 90-140 words; no hype words; every number in the text appears in that building's facts, quotes or
its own fields (year, name); every capitalised name of two or more words appears there too; under 15% of the
paragraph sits in six-word runs copied from its quotes. Name flags are often false alarms ("World War II" written
"Second World War"): check each against the quotes by eye. Prints one line per
problem and a total; exits 1 if any write-up fails, so a bad one never goes live unnoticed."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANNED = ('iconic', 'stunning', 'breathtaking', 'nestled', 'masterpiece', 'jewel', 'striking', 'boasts', 'testament',
          'renowned', 'world-famous', 'unique', 'awe-inspiring', 'awe', 'must-see', 'gem')


OPENERS = {'During', 'On', 'In', 'With', 'The', 'At', 'For', 'From', 'After', 'Before', 'Built', 'Its', 'It', 'Inside', 'Outside',
           'Opened', 'Completed', 'Designed', 'Here', 'Like', 'Unlike', 'Where', 'When', 'While', 'Today', 'Along', 'Above', 'Below',
           'Beyond', 'Over', 'Under', 'Between', 'Behind', 'Across', 'Through', 'Rather', 'Instead', 'Both', 'Each', 'Every', 'This', 'That'}


def wall():
    out = {}
    for line in (ROOT / 'site' / 'data' / 'wall.js').read_text().splitlines():
        if line.startswith('{"id"'):
            b = json.loads(line.rstrip(','))
            out[b['id']] = b
    return out


def main():
    args = sys.argv[1:]
    cut = args.index('--')
    facts = {}
    for f in args[:cut]:
        for r in json.loads(Path(f).read_text()):
            facts[r['id']] = r
    W, bad, n = wall(), 0, 0
    import hashlib
    rv = Path(__file__).resolve().parent / 'reviewed.txt'  # flags checked by eye, tied to the exact text
    seen = {tuple(x.strip() for x in l.split('|')) for l in rv.read_text().splitlines() if '|' in l and not l.startswith('#')} if rv.exists() else set()
    for f in args[cut + 1:]:
        for w in json.loads(Path(f).read_text()):
            n += 1
            b, fr = W.get(w['id'], {}), facts.get(w['id'], {})
            pool = ' '.join([b.get('name', ''), b.get('by', ''), b.get('place', ''), str(b.get('year', '')), b.get('type', ''),
                             b.get('movement', '')] + [x['fact'] + ' ' + x['quote'] for x in fr.get('facts', [])])
            low = pool.lower()
            text, probs = w['text'], []
            k = len(text.split())
            if not 90 <= k <= 140:
                probs.append(f'{k} words')
            for word in BANNED:
                if re.search(r'\b' + re.escape(word) + r'\b', text, re.I):
                    probs.append(f'hype word "{word}"')
            for num in re.findall(r'\d[\d,.]*\d|\d', text):
                if num.replace(',', '') not in pool.replace(',', ''):
                    probs.append(f'number {num} not in sources')
            for name in re.findall(r'(?:[A-Z][\w\'’-]+(?:\s+(?:de|da|van|von|der|of|the|and|la|le|du|di)?\s*[A-Z][\w\'’-]+)+)', text):
                parts = [re.sub(r"['’]s$", '', p) for p in re.split(r'\s+', name) if p[:1].isupper() and p not in OPENERS]
                if not all(p.lower() in low for p in parts):
                    probs.append(f'name "{name}" not in sources')
            q6 = set()
            for x in fr.get('facts', []):
                t = re.findall(r'[a-z0-9]+', x['quote'].lower()); q6 |= {tuple(t[i:i + 6]) for i in range(len(t) - 5)}
            t = re.findall(r'[a-z0-9]+', text.lower()); cov = set()
            for i in range(len(t) - 5):
                if tuple(t[i:i + 6]) in q6:
                    cov.update(range(i, i + 6))
            if t and len(cov) / len(t) >= 0.15:  # our own words: under 15% of a paragraph in six-word runs from its quotes
                probs.append(f'{len(cov) / len(t):.0%} copied from the quotes')
            if probs and (w['id'], hashlib.md5(text.encode()).hexdigest()[:12]) in seen:
                probs = []
            if probs:
                bad += 1
                print(f'{w["id"]}: ' + '; '.join(probs))
    print(f'{n} write-ups checked, {bad} with problems')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
