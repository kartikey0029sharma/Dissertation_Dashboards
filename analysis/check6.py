#!/usr/bin/env python3
"""Harvard cross-check: every reference cited, and every in-text year resolves."""
import re, sys, unicodedata
f = sys.argv[1] if len(sys.argv) > 1 else 'Sharma_250559280_Dissertation_Draft_v6.tex'
s = open(f, encoding='utf-8').read()
def norm(x):
    x = unicodedata.normalize('NFKD', x)
    x = ''.join(c for c in x if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', x).strip()

body, rest = s.split(r'\phantomsection\label{toc:refs}')
parts = rest.split(r'\phantomsection\label{toc:apps}')
reflist = parts[0]
text = norm(re.sub(r'[{}]', ' ', re.sub(r'\\[a-zA-Z@]+\*?', ' ',
                   body + ' ' + (parts[1] if len(parts) > 1 else ''))))

# --- reference-list entries: (lead author or corporate author, year)
refs = []
for m in re.finditer(r'\\rf\s+(.+?)\s*\((\d{4}[a-z]?)\)', reflist, re.S):
    first = norm(re.sub(r'\\emph\{|\}', '', m.group(1)))
    if ',' in first and re.match(r'^[A-Z][a-zA-Z\'\-]*,\s*[A-Z]\.', first):
        lead = first.split(',')[0].strip()          # personal author
    else:
        lead = first.rstrip('.').strip()            # corporate author
    refs.append((lead, m.group(2), first[:60]))

def cited(lead, year):
    """Is 'lead ... year' present in the text within a short window?"""
    for m in re.finditer(re.escape(lead), text):
        w = text[m.end(): m.end() + 170]
        if re.search(r'\b' + re.escape(year) + r'\b', w):
            return True
    return False

uncited = [(l, y, t) for l, y, t in refs if not cited(l, y)]

# --- every parenthetical year in the text should belong to some reference
years_in_list = {y for _, y, _ in refs}
orphan_years = sorted({m.group(1) for m in re.finditer(r'\((?:[^()]{0,200}?)\b(\d{4}[a-z]?)\)', text)}
                      - years_in_list)

print(f'{f}')
print(f'  reference list entries : {len(refs)}')
print(f'  UNCITED references     : {len(uncited)}')
for l, y, t in uncited: print(f'     ! {l} ({y}) -> {t}')
print(f'  in-text years with no list entry : {len(orphan_years)}  {orphan_years}')
print(f'  em dashes (U+2014)     : {s.count(chr(8212))}')
dup = [r for r in refs if [x[:2] for x in refs].count(r[:2]) > 1]
print(f'  duplicate list entries : {len(dup)}')
