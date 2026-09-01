#!/usr/bin/env python3
"""Word count on the declared basis: Chapters 1-6 prose, floats excluded."""
import re, sys
def strip(body):
    for env in ['figure','table','longtable','tabularx','tikzpicture']:
        body=re.sub(r'\\begin\{'+env+r'\*?\}.*?\\end\{'+env+r'\*?\}','',body,flags=re.S)
    body=re.sub(r'\\[a-zA-Z@]+\*?(\[[^\]]*\])?','',body)
    body=re.sub(r'%.*','',body)
    body=re.sub(r'[{}$&\\~^_]',' ',body)
    return len(body.split())
f=sys.argv[1] if len(sys.argv)>1 else 'Sharma_250559280_Dissertation_Draft_v6.tex'
s=open(f,encoding='utf-8').read()
body=s.split(r'\chapt{1}')[1].split(r'\phantomsection\label{toc:refs}')[0]
tot=strip(body)
parts=re.split(r'\\chapt\{(\d)\}',body)
print(f'{f}\n  TOTAL Chapters 1-6 prose: {tot}')
segs=[('1',parts[0])]+[(parts[i],parts[i+1]) for i in range(1,len(parts)-1,2)]
for n,seg in segs:
    print(f'   Ch {n}: {strip(seg):6d}')
# per-section within chapters 2 and 3
for chn in ('2','3'):
    for n,seg in segs:
        if n!=chn: continue
        secs=re.split(r'\\section\{',seg)
        print(f'  -- Chapter {chn} sections --')
        for sc in secs[1:]:
            title=sc.split('}')[0][:52]
            print(f'     {strip(sc):5d}  {title}')
