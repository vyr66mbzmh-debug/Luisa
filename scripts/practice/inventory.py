#!/usr/bin/env python3
"""Create private native-source and published-PDF inventories.

Explicit paths are required. Write inventories outside Git: they contain private
source locations. Originals are opened read-only. Only exact adjacent-PDF hash
matches qualify as a native source for a published booklet.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pymupdf

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--native-root',type=Path,required=True);p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--private-output',type=Path,required=True);a=p.parse_args()
    a.private_output.mkdir(parents=True,exist_ok=True);pdfs=[]
    for pdf in sorted((a.repo/'resources/practice').glob('*/*.pdf')):
        with pymupdf.open(pdf) as d:pdfs.append({'file':pdf.relative_to(a.repo).as_posix(),'pages':len(d),'sha256':sha(pdf),'metadata':d.metadata,'toc':d.get_toc()})
    hashes={r['sha256']:r['file'] for r in pdfs};native=[]
    for tex in sorted(a.native_root.glob('Year*/*/Chapter*.tex')):
        pdf=tex.with_suffix('.pdf');match=hashes.get(sha(pdf)) if pdf.is_file() else None
        native.append({'path':str(tex.resolve()),'sha256':sha(tex),'publicPdf':match})
    matched=[r['publicPdf'] for r in native if r['publicPdf']]
    if len(matched)!=len(set(matched)) or set(matched)!=set(hashes.values()):raise ValueError('Missing/ambiguous native sources')
    for name,rows in [('native-inventory.json',native),('pdf-inventory.json',pdfs)]:
        (a.private_output/name).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(pdfs)} published PDFs, {sum(x["pages"] for x in pdfs)} pages, {len(matched)} native matches')
if __name__=='__main__':main()
