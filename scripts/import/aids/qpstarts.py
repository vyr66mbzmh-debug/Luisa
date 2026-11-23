"""Per question paper: each question's start (page, y) from left-margin labels and its end page from "Total for Question N".

Usage: python3 -I scripts/import/aids/qpstarts.py --set <set>   (helps fill qpends.json; text-layer papers only)
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
    q = pymupdf.open(SET.pdf(pid, 'qp'))
    st, en = {}, {}
    for i, page in enumerate(q, 1):
        for n, _ in re.findall(r'Total for Question (\d+) is (\d+) marks', ' '.join(page.get_text().split())):
            en[int(n)] = i
        for b in page.get_text('dict')['blocks']:
            if b['type']:
                continue
            for line in b['lines']:
                s = ''.join(x['text'] for x in line['spans']).strip()
                if line['bbox'][0] < 60 and re.fullmatch(r'\d{1,2}\.?', s) and int(s.rstrip('.')) <= P['nq']:
                    st.setdefault(int(s.rstrip('.')), (i, round(line['bbox'][1])))
    print(pid, [(n, st.get(n), en.get(n)) for n in range(1, P['nq'] + 1)])
