"""Build vector assets for one past paper: figure crops from the question paper and ordered mark-scheme crops.

Usage: python3 -I scripts/import/build_assets.py --set <set> <paperId> [--figures-only]
Figures come from the set's figs.json {pid: {q: [[page, [x0,y0,x1,y1]] or [page, box, "clip"]]}} (approximate boxes snapped to
drawings and text unless "clip"). Mark-scheme regions come from papers.py msstart/msend (page, or [page, y] for a mid-page start).
Writes resources/exams/<pid>/*.svg and the asset record <state>/import/<set>/assets/<pid>.json, asserting full scheme coverage
(every text span and image lies in exactly one crop; breaks only in empty bands).
--figures-only re-creates only the question-figure SVGs (needs the question paper alone) and keeps the scheme crops.
"""
import hashlib, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import pymupdf  # noqa: E402
pymupdf.TOOLS.set_small_glyph_heights(True)
ap = common.parser(__doc__)
ap.add_argument('--figures-only', action='store_true')
ARGS = ap.parse_args()
SET = common.ImportSet(ARGS)
ROOT, PID = SET.repo, ARGS.paper
P = SET.papers[PID]
QP = SET.pdf(PID, 'qp')
MS = None if ARGS.figures_only else SET.pdf(PID, 'ms')
OUT = ROOT / 'resources/exams' / PID
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('*-figure*.svg' if ARGS.figures_only else '*.svg'): old.unlink()
FIGS = SET.data('figs.json').get(PID, {})
# msstart entries: page (question starts at the top of that page) or [page, y] (starts mid-page at the gap above y).
S = [x if isinstance(x, list) else [x, None] for x in P['msstart']] + [[P['msend'] + 1, None]]
REGIONS = {}
for n in range(1, P['nq'] + 1):
    (p0, y0), (p1, y1) = S[n - 1], S[n]
    last = p1 if y1 is not None else p1 - 1
    REGIONS[n] = [(pg, y0 if pg == p0 else None, y1 if pg == p1 else None) for pg in range(p0, last + 1)]
for k, v in P.get('mspages', {}).items(): REGIONS[int(k)] = [(pg, None, None) for pg in v]  # explicit non-contiguous pages
MS_PAGES = {n: [pg for pg, _, _ in r] for n, r in REGIONS.items()}
MAX_H = 420.0

def whole(box):
    """Grow a figure box evenly so its width and height are whole points (browsers round natural SVG sizes)."""
    x0, y0, x1, y1 = box; dw = math.ceil(x1 - x0) - (x1 - x0); dh = math.ceil(y1 - y0) - (y1 - y0)
    return [x0 - dw / 2, y0 - dh / 2, x1 + dw / 2, y1 + dh / 2]

def write_svg(src, page, box, name):
    r = pymupdf.Rect(box); tmp = pymupdf.open(); p = tmp.new_page(width=r.width, height=r.height)
    p.show_pdf_page(p.rect, src, page - 1, clip=r)
    target = OUT / name; target.write_text(p.get_svg_image(text_as_path=True)); tmp.close()
    data = target.read_bytes()
    return {'asset': target.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
            'sourcePage': page, 'boundsPoints': [round(v, 3) for v in box]}

def spans(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0: continue
        for line in b['lines']:
            for s in line['spans']:
                t = s['text'].strip()
                if t.startswith(('Pearson Education Limited. Registered company', 'with its registered office at 80 Strand')): continue  # publisher footer, not scheme content
                if t and not (t == 'PMT' and (s['bbox'][1] < 25 or s['bbox'][1] > page.rect.height - 25)):
                    r = pymupdf.Rect(s['bbox'])
                    if s['size'] >= 20: r.y0 -= 0.15 * s['size']  # large glyphs (e.g. 41pt integral signs) ink above their span box
                    out.append((s['text'], r))
    return out

def tight(page, rect):
    """Drawn extent of the drawing whose control-point rect is `rect` (curves sampled), else rect unchanged."""
    for d in page.get_drawings():
        if pymupdf.Rect(d['rect']) != rect: continue
        pts = []
        for it in d['items']:
            if it[0] == 'c':
                p0, p1, p2, p3 = it[1:5]
                for k in range(65):
                    s = k / 64; w = (1 - s) ** 3, 3 * s * (1 - s) ** 2, 3 * s * s * (1 - s), s ** 3
                    pts.append(pymupdf.Point(sum(c * q.x for c, q in zip(w, (p0, p1, p2, p3))), sum(c * q.y for c, q in zip(w, (p0, p1, p2, p3)))))
            elif it[0] == 'l': pts += it[1:3]
            elif it[0] == 're': pts += [it[1].tl, it[1].br]
            elif it[0] == 'qu': pts += [it[1].ul, it[1].ur, it[1].ll, it[1].lr]
        if not pts: return rect
        w = (d.get('width') or 0) / 2
        return pymupdf.Rect(min(p.x for p in pts) - w, min(p.y for p in pts) - w, max(p.x for p in pts) + w, max(p.y for p in pts) + w)
    return rect

def snap(page, box):
    a = pymupdf.Rect(box); u = None
    items = [(t, r) for t, r in spans(page)] + [('[draw]', d['rect']) for d in page.get_drawings()] + [('[image]', pymupdf.Rect(i['bbox'])) for i in page.get_image_info()]
    for t, r in items:
        r = pymupdf.Rect(r.x0, r.y0, max(r.x1, r.x0 + 0.5), max(r.y1, r.y0 + 0.5))
        if r not in a and t == '[draw]' and r.intersects(a) and not (r.width > 400 or r.height > 400):
            r = tight(page, r)  # a Bezier's rect is its control-point hull; use the drawn extent
        if r in a: u = r if u is None else u | r
        elif r.intersects(a) and not (r.width > 400 or r.height > 400):
            raise AssertionError(('item straddles figure box', page.number + 1, t, tuple(round(v) for v in r), box))
    assert u is not None, (page.number + 1, box)
    return [u.x0 - 3, u.y0 - 3, u.x1 + 3, u.y1 + 3]

def gapcut(page, y):
    """Cut just above a mid-page question label at y: in the clear gap above it (a table rule there if any)."""
    sp = spans(page); dr = [d['rect'] for d in page.get_drawings()]
    hdr = [r.y0 for t, r in sp if t.strip() == 'Question' and 0 <= y - r.y1 < 30]  # the question's own table header row ("Question | Scheme | Marks | AOs") belongs with it
    if hdr: y = min(hdr)
    above = [r.y1 for _, r in sp if r.y1 <= y + 0.5 and r.y0 < y - 2] + [r.y1 for r in dr if r.height > 2 and r.y1 <= y + 0.5]
    lo = max(above) if above else y - 6
    rules = [r.y0 for r in dr if r.width > 200 and r.height < 2 and lo - 0.5 <= r.y0 <= y]
    cut = max(rules) if rules else (lo + y) / 2
    for t, r in sp: assert not (r.y0 + 0.5 < cut < r.y1 - 0.5), ('mid-page cut through text', page.number + 1, t, cut)
    return cut

def segments(page, lo=None, hi=None):
    lo = gapcut(page, lo) if lo is not None else -1e9; hi = gapcut(page, hi) if hi is not None else 1e9
    if P.get('msfoot'): hi = min(hi, P['msfoot'])  # sample schemes: drop the page footer band (rule, Pearson imprint, page-number box)
    inr = lambda r: lo <= (r.y0 + r.y1) / 2 <= hi
    clip = lambda r: pymupdf.Rect(r.x0, max(r.y0, lo), r.x1, min(r.y1, hi))
    sp = [(t, r) for t, r in spans(page) if inr(r)]
    draws = [clip(d['rect']) for d in page.get_drawings() if d['rect'].width < page.rect.width - 20 and d['rect'].x1 > 0 and d['rect'].x0 < page.rect.width  # off-page items are invisible
             and not (d.get('type') == 'f' and d.get('fill') and min(d['fill']) > 0.99)  # skip invisible white backgrounds
             and d['rect'].y1 > lo and d['rect'].y0 < hi]
    rules = sorted({round(r.y0, 2) for r in draws if r.width > 200 and r.height < 2.5})  # thin and thick (2.16pt) table rules
    wide = [r for r in draws if r.width > 200 and r.height < 2.5]
    rowrule = lambda r: r.height < 2.5 and any(abs(w.y0 - r.y0) < 0.6 for w in wide)  # label-column segment of a full-width table rule
    occupied = [(r.y0 - 0.5, r.y1 + 0.5) for _, r in sp]
    occupied += [(r.y0 - 0.5, r.y1 + 0.5) for r in draws if not ((r.width > 200 and r.height < 2.5) or rowrule(r) or r.width < 2 or (r.width < 4 and r.height > 20)
                 or (r.width < 4 and r.height > 3 * r.width))]  # table rules and vertical table borders (thin or thick, any segment length) are safe to cut through
    images = [pymupdf.Rect(i['bbox']) for i in page.get_image_info() if inr(pymupdf.Rect(i['bbox']))]
    draws = draws + images
    occupied += [(r.y0 - 1, r.y1 + 1) for r in images]
    occupied.sort(); merged = []
    for a, b in occupied:
        if merged and a <= merged[-1][1]: merged[-1][1] = max(b, merged[-1][1])
        else: merged.append([a, b])
    top = max(min([r.y0 for _, r in sp] + [r.y0 for r in draws]) - 2, lo)
    bottom = min(max([r.y1 for _, r in sp] + [r.y1 for r in draws]) + 2, hi)
    gaps = [(a[1], b[0]) for a, b in zip(merged, merged[1:]) if b[0] - a[1] >= 1.5]
    for n in range(math.ceil((bottom - top) / MAX_H), math.ceil((bottom - top) / MAX_H) + 4):
        cuts = [top]
        for i in range(1, n):
            target = top + (bottom - top) * i / n; cands = []
            for lo, hi in gaps:
                if not cuts[-1] + 120 < (lo + hi) / 2 < bottom - 60: continue
                ruled = [y for y in rules if lo <= y <= hi]
                y = ruled[0] if ruled else (lo + hi) / 2
                cands.append((abs(y - target) - (40 if ruled else 0) - 4 * min(hi - lo, 12), y))
            if not cands and bottom - top <= MAX_H + 120: cuts = [top]; break  # whole page fits the allowance: one crop
            assert cands, ('no safe break', page.number + 1)
            cuts.append(min(cands)[1])
        cuts.append(bottom)
        if all(b - a <= MAX_H + 120 for a, b in zip(cuts, cuts[1:])): break
    x0 = min([r.x0 - 2 for _, r in sp] + [r.x0 - 1 for r in draws])
    x1 = max([r.x1 + 2 for _, r in sp] + [r.x1 + 1 for r in draws])
    x0, x1 = max(x0, 1.0), min(x1, page.rect.width - 1.0)  # content bleeding off the page is clipped by the page itself
    assert all(b - a <= MAX_H + 120 for a, b in zip(cuts, cuts[1:])), cuts
    for y in cuts[1:-1]: assert not any(lo < y < hi for lo, hi in merged), (page.number + 1, y)
    for text, r in sp + [('[image]', r) for r in images]:
        if r.x1 > page.rect.width - 1 or r.x0 < 1: continue  # off-page glyphs are invisible in the source too
        inside = [i for i, (a, b) in enumerate(zip(cuts, cuts[1:])) if a <= r.y0 and r.y1 <= b and x0 <= r.x0 and r.x1 <= x1]
        assert len(inside) == 1, (page.number + 1, text, r, cuts)
    return cuts, len(sp), (x0, x1)

qdoc = pymupdf.open(QP)
record_path = SET.assets_path(PID)
if ARGS.figures_only:
    if not record_path.exists():
        raise SystemExit('No asset record yet; run without --figures-only first (it needs the mark scheme).')
    record = json.loads(record_path.read_text())
    record['figures'] = {}
else:
    record = {'paperId': PID, 'sourceHashes': {'questionPaperSha256': P['qpsha'], 'markSchemeSha256': P['mssha']},
              'figures': {}, 'markScheme': {}, 'spanCount': 0, 'msPages': MS_PAGES}
for n, items in FIGS.items():
    record['figures'][n] = []
    for k, item in enumerate(items, 1):
        page, box = item[0], item[1]
        # 'clip': use the box exactly (a path's bounding box overstates its visible extent); checked visually in Chrome.
        b = list(box) if len(item) > 2 and item[2] == 'clip' else snap(qdoc[page - 1], box)
        name = f'q{int(n):02d}-figure.svg' if len(items) == 1 else f'q{int(n):02d}-figure-{k}.svg'
        record['figures'][n].append(dict(write_svg(qdoc, page, whole(b), name), question=int(n), kind='question-figure'))
if not ARGS.figures_only:
    mdoc = pymupdf.open(MS)
    for n, regions in REGIONS.items():
        rows = []
        for pg, lo, hi in regions:
            pgo = mdoc[pg - 1]
            if not spans(pgo) and not pgo.get_drawings() and not pgo.get_image_info():
                record.setdefault('blankPages', []).append(pg); continue  # blank page (only the PMT watermark)
            cuts, count, (x0, x1) = segments(pgo, lo, hi); record['spanCount'] += count
            for s, (a, b) in enumerate(zip(cuts, cuts[1:]), 1):
                rows.append(dict(write_svg(mdoc, pg, (x0, a, x1, b), f'q{n:02d}-ms-p{pg:02d}-{s}.svg'),
                                 question=n, kind='mark-scheme', segment=s, segments=len(cuts) - 1))
        record['markScheme'][n] = rows
record_path.parent.mkdir(parents=True, exist_ok=True)
record_path.write_text(json.dumps(record, indent=1))
print(PID, 'figures', sum(len(v) for v in record['figures'].values()), 'scheme crops', sum(len(v) for v in record['markScheme'].values()),
      'pages', sum(len(v) for v in MS_PAGES.values()), 'spans', record['spanCount'])
