"""Inventory every PDF in the source folder: SHA-256, pages, cover text, and whether it is already imported.

Usage: python3 -I scripts/import/aids/inventory.py --set <set> [--source DIR]
Writes <state>/import/<set>/inventory.json (private: it contains file names from the owner's folder) and prints one line per
file. Identify papers by their covers, not their file names; byte-identical duplicates show the paper they duplicate.
"""
import hashlib
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import pymupdf  # noqa: E402

args = common.parser(__doc__, paper=False).parse_args()
SET = common.ImportSet(args)
known = {}
for p in json.loads((SET.repo / 'content/exams/pilot-metadata.json').read_text())['papers']:
    for k in ('questionPaperSha256', 'markSchemeSha256', 'indexedQuestionPaperSha256', 'indexedMarkSchemeSha256'):
        if p['source'].get(k):
            known.setdefault(p['source'][k], set()).add(p['id'] + ':' + ('QP' if 'Question' in k else 'MS'))
out = []
for d, _, files in sorted(os.walk(SET.source)):
    for f in sorted(files):
        if f == '.DS_Store' or not f.lower().endswith('.pdf'):
            continue
        path = os.path.join(d, f)
        data = open(path, 'rb').read()
        h = hashlib.sha256(data).hexdigest()
        doc = pymupdf.open(path)
        cover = ' '.join(doc[0].get_text().split())
        out.append(dict(file=os.path.relpath(path, SET.source), bytes=len(data), sha256=h, pages=len(doc), known=sorted(known.get(h, [])),
                        cover=cover[:900], p2=' '.join(doc[1].get_text().split())[:300] if len(doc) > 1 else ''))
(SET.work / 'inventory.json').write_text(json.dumps(out, indent=1))
for o in out:
    print(o['file'], o['pages'], o['sha256'][:12], o['known'] or 'new')
