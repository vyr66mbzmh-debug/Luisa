"""Print text lines and the union of drawings on question-paper pages, to set figure boxes in figs.json.

Usage: python3 -I scripts/import/aids/figscan.py --set <set> <paperId> <page> [<page> ...]
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import pymupdf  # noqa: E402

ap = common.parser(__doc__)
ap.add_argument('pages', nargs='+', type=int)
args = ap.parse_args()
SET = common.ImportSet(args)
d = pymupdf.open(SET.pdf(args.paper, 'qp'))
for pg in args.pages:
    page = d[pg - 1]
    print('== p', pg, 'rect', page.rect)
    lines = []
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            t = ''.join(s['text'] for s in line['spans']).strip()
            if t and not re.match(r'^_{5,}|DO NOT WRITE|^PMT$', t) and 40 < line['bbox'][0] < 560:
                lines.append((pymupdf.Rect(line['bbox']), t))
    draws = [dd['rect'] for dd in page.get_drawings() if dd['rect'].width < 480 and not (dd['rect'].height < 1.5 and dd['rect'].width > 400)]
    for r, t in sorted(lines, key=lambda x: x[0].y0):
        print(f'  T {r.x0:5.0f}{r.y0:5.0f}{r.x1:5.0f}{r.y1:5.0f}  {t[:60]}')
    if draws:
        u = draws[0]
        for r in draws[1:]:
            u |= r
        print('  drawings union', [round(v) for v in u], len(draws))
