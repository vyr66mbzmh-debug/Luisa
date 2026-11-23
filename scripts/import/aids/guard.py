"""After build_assets.py: no scheme crop may contain another question's left-column label (N(a), N., Qu N).

Usage: python3 -I scripts/import/aids/guard.py --set <set> <paperId>
"""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import pymupdf  # noqa: E402

args = common.parser(__doc__).parse_args()
SET = common.ImportSet(args)
pid = args.paper
P = SET.papers[pid]
a = json.loads(SET.assets_path(pid).read_text())
d = pymupdf.open(SET.pdf(pid, 'ms'))
bad = []
for n, rows in a['markScheme'].items():
    for r in rows:
        x0, y0, x1, y1 = r['boundsPoints']
        for b in d[r['sourcePage'] - 1].get_text('dict')['blocks']:
            for line in b.get('lines', []):
                t = ''.join(s['text'] for s in line['spans']).strip()
                mm = re.match(r'^(?:Qu\s*|Question\s*)?(\d{1,2})\s*(\([a-z]+\)|\.(?=\s|$)|$)', t)
                if mm and line['bbox'][0] < 110 and y0 <= line['bbox'][1] < y1 and int(mm[1]) != int(n) and int(mm[1]) <= P['nq'] and (mm[2] or t.startswith('Qu')):
                    bad.append((n, r['sourcePage'], t[:14]))
print(pid, 'foreign labels', bad or 'none')
raise SystemExit(1 if bad else 0)
