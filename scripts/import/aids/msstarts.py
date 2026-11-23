"""Print each question's start (page, y) in a mark scheme from left-column labels "N" or "N(x)" (helps fill msstart).

Usage: python3 -I scripts/import/aids/msstarts.py --set <set> <paperId>
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import pymupdf  # noqa: E402

args = common.parser(__doc__).parse_args()
SET = common.ImportSet(args)
nq = SET.papers[args.paper]['nq']
d = pymupdf.open(SET.pdf(args.paper, 'ms'))
pat = re.compile(r'^(\d{1,2})\s*(\(.*\))?$')
starts = {}
for i, page in enumerate(d, 1):
    for b in page.get_text('dict')['blocks']:
        if b['type']:
            continue
        for line in b['lines']:
            t = ''.join(s['text'] for s in line['spans']).strip()
            m = pat.match(t)
            if m and line['bbox'][0] < 85:
                n = int(m[1])
                if 1 <= n <= nq and n not in starts and all(k < n for k in starts):
                    starts[n] = (i, round(line['bbox'][1]))
print(' '.join(f'Q{n}:p{p}@{y}' for n, (p, y) in sorted(starts.items())), '| pages', len(d), '| missing', [n for n in range(1, nq + 1) if n not in starts])
