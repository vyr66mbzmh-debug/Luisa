"""Check source hashes, then compare each question's total in the question paper with the last total in its scheme region.

Usage: python3 -I scripts/import/aids/marks.py --set <set>   (prints AGREE or CHECK per paper; text-layer papers only)
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import pymupdf  # noqa: E402

args = common.parser(__doc__, paper=False).parse_args()
SET = common.ImportSet(args)
for pid, P in SET.papers.items():
    q, m = pymupdf.open(SET.pdf(pid, 'qp')), pymupdf.open(SET.pdf(pid, 'ms'))
    qmarks, qpages = {}, {}
    for i, page in enumerate(q, 1):
        for n, x in re.findall(r'Total for Question (\d+) is (\d+) marks', ' '.join(page.get_text().split())):
            qmarks[int(n)] = int(x)
            qpages.setdefault(int(n), i)
    S = [x[0] if isinstance(x, list) else x for x in P['msstart']] + [P['msend'] + 1]
    msm = {n: [int(x) for x in re.findall(r'\((\d+) marks?\)', ' '.join(' '.join(m[i - 1].get_text().split()) for i in range(S[n - 1], max(S[n], S[n - 1] + 1))))]
           for n in range(1, P['nq'] + 1)}
    ok = all(msm[n] and msm[n][-1] == qmarks.get(n) for n in qmarks) and sorted(qmarks) == list(range(1, P['nq'] + 1)) and sum(qmarks.values()) == P['total']
    print(pid, 'QP', [qmarks.get(n) for n in range(1, P['nq'] + 1)], 'sum', sum(qmarks.values()), 'end pages', qpages)
    print('   MS totals', msm, 'AGREE' if ok else 'CHECK')
