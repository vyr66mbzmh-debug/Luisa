"""PMT revision-question import (v0.75 Core Pure 1, v0.76 Core Pure 2). See README.md, section "PMT topic sheets".

A PMT topic sheet is one PDF per textbook chapter: a "Questions" section (Q1 … Qn, part marks in
brackets, "(Total for question = N marks)") followed by a "Mark Scheme" section in which each
"Qn." label is followed by the Edexcel scheme table for that question as page images.

Commands (always `python3 -I`):
  pages   --set S FILE [--dpi 110]   render every page to <work>/pages/ for transcription and review
  scan    --set S FILE               question starts, totals, scheme regions and images (JSON)
  assets  --set S FILE               scheme crops (complete coverage asserted) and figure crops
  payload --set S FILE               content/pmt/<FILE>.json from prompts/<FILE>.py and the asset record
  integrate --set S FILE             rows in pmt-catalogue.json (idempotent)

Set layout (scripts/import/sets/<S>/): files.py (FILES: id -> rel, sha256, book, chapter, title,
course label), questions.json (per question: marks, difficulty, reason, chapters, skills,
summary), figs.json (per question figure boxes), prompts/<FILE>.py (Q dict, lib helpers).

No duplicates (PAP-077-2, standing from v0.77): `payload` compares the new questions with the whole bank
(scripts/duplicates.py) and stops while any candidate is unconfirmed. A confirmed copy of an official question or of
an earlier PMT question is not imported: list it under "skip" for its file in the set's skip.json. Questions removed as
duplicates (docs/evidence/duplicate-decisions.json) are never rendered, written or integrated again.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import lib  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import duplicates  # noqa: E402

HEADER_Y, FOOTER_Y = 30, 815          # page furniture (running header) is above HEADER_Y
LABEL = re.compile(r'^\s*Q(\d+)\.?\s*$')


class PmtSet:
    def __init__(self, args):
        self.name = args.set
        self.dir = common.HERE / 'sets' / args.set
        self.repo = Path(args.repo).resolve()
        self.files = common.module(self.dir / 'files.py', 'pmt_files_' + self.name.replace('-', '_')).FILES
        self._source = args.source
        self.work = common.private.state_dir() / 'import' / self.name
        self.work.mkdir(parents=True, exist_ok=True)

    @property
    def source(self):
        return Path(self._source or common.private.get('pastPaperSource')).expanduser()

    def pdf(self, file_id):
        import hashlib
        import pymupdf
        spec = self.files[file_id]
        data = (self.source / spec['rel']).read_bytes()
        if hashlib.sha256(data).hexdigest() != spec['sha256']:
            raise SystemExit(f'{file_id}: source PDF hash differs from files.py; identify the file again before importing.')
        return pymupdf.open(stream=data, filetype='pdf')

    def data(self, name, default=None):
        path = self.dir / name
        return json.loads(path.read_text()) if path.exists() else default

    def skipped(self, file_id):
        """Question numbers of this file that stay out of the bank: removed duplicates and confirmed copies (PAP-077-2)."""
        spec = self.files[file_id]
        prefix = f'pmt/{spec["book"]}/ch{spec["chapter"]}/q'
        removed = {int(i[len(prefix):]) for i in duplicates.removed_ids(self.repo) if i.startswith(prefix)}
        return removed | set(self.data('skip.json', {}).get(file_id, []))


def text_blocks(page):
    for b in page.get_text('blocks'):
        t = re.sub(r'\s+', ' ', b[4]).strip()
        if t and b[1] >= HEADER_Y:
            yield b[:4], t


def label_line(page, box, q):
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            text = ''.join(sp['text'] for sp in line['spans']).strip()
            r = line['bbox']
            if re.fullmatch(rf'Q{q}\.?', text) and box[1] - 1 <= r[1] and r[3] <= box[3] + 1:
                return r
    raise SystemExit(f'scheme label Q{q} has no line of its own on page {page.number + 1}')


def scan(doc):
    """Question starts and totals, the first scheme page and the scheme regions per question."""
    pages = [p.get_text() for p in doc]
    first = next(i for i, t in enumerate(pages) if re.search(r'(?im)^\s*mark\s*scheme', t))
    questions, totals = [], []
    for pn in range(first + 1):
        for box, t in text_blocks(doc[pn]):
            if pn == first and re.match(r'(?i)mark scheme', t):
                break
            for m in re.finditer(r'(?:^|\s)Q(\d+)\.(?=\s|$)', t):
                questions.append(dict(q=int(m.group(1)), page=pn + 1, y=round(box[1])))
            for m in re.finditer(r'\(Total for question = (\d+) marks?\)', t):
                totals.append(dict(marks=int(m.group(1)), page=pn + 1, y=round(box[3])))
    # Scheme labels, in order, with their positions.
    labels = []
    for pn in range(first, doc.page_count):
        for box, t in text_blocks(doc[pn]):
            m = re.search(r'(?:^|\s)Q(\d+)\.?$', t)
            if m and (LABEL.match(t) or t.startswith('Mark Scheme')):
                # A block's box can include blank space that overlaps a scheme image; use the label's own line.
                line = label_line(doc[pn], box, int(m.group(1)))
                labels.append(dict(q=int(m.group(1)), page=pn + 1, y0=line[1], y1=line[3]))
    # Each question's scheme: from its label to the next label, page by page.
    regions = {}
    for k, lab in enumerate(labels):
        nxt = labels[k + 1] if k + 1 < len(labels) else dict(page=doc.page_count + 1, y0=0)
        for pn in range(lab['page'], nxt['page'] + 1):
            if pn > doc.page_count:
                break
            top = lab['y1'] if pn == lab['page'] else HEADER_Y
            bottom = nxt['y0'] if pn == nxt['page'] else FOOTER_Y
            if bottom - top > 4:
                regions.setdefault(lab['q'], []).append(dict(page=pn, top=top, bottom=bottom))
    return dict(firstSchemePage=first + 1, questions=questions, totals=totals, labels=labels, regions=regions)


def content_boxes(page):
    """Every image and text block (below the running header) on a page, as rectangles."""
    import pymupdf
    boxes = [pymupdf.Rect(im['bbox']) for im in page.get_image_info()]
    boxes += [pymupdf.Rect(box) for box, t in text_blocks(page) if not LABEL.match(t) and not t.startswith('Mark Scheme')]
    return [b for b in boxes if b.y0 >= HEADER_Y - 1]


def scheme_crops(doc, info, moved=()):
    """Tight crops of each question's scheme region; asserts every content box is in exactly one crop.
    Pages in `moved` belong to another file's question (recorded in scheme-moves.json) and are left out here."""
    import pymupdf
    crops, used = {}, {}
    for q, regs in info['regions'].items():
        for reg in regs:
            if reg['page'] in moved:
                continue
            page = doc[reg['page'] - 1]
            inside = [b for b in content_boxes(page) if b.y0 >= reg['top'] - 2 and b.y1 <= reg['bottom'] + 2]
            if not inside:
                continue
            rect = pymupdf.Rect(inside[0])
            for b in inside[1:]:
                rect |= b
            rect = pymupdf.Rect(rect.x0 - 2, rect.y0 - 2, rect.x1 + 2, rect.y1 + 2) & page.rect
            crops.setdefault(q, []).append(dict(page=reg['page'], rect=[round(v, 2) for v in rect]))
            for b in inside:
                key = (reg['page'], tuple(round(v, 1) for v in b))
                used[key] = used.get(key, 0) + 1
    for pn in range(info['firstSchemePage'], doc.page_count + 1):
        if pn in moved:
            continue
        for b in content_boxes(doc[pn - 1]):
            key = (pn, tuple(round(v, 1) for v in b))
            if used.get(key) != 1:
                raise SystemExit(f'Scheme content on page {pn} at {key[1]} is covered {used.get(key, 0)} times; fix the regions.')
    return crops


MAX_RATIO = 1.0   # a scheme crop is at most as tall as it is wide, so it fits one printed scheme page with its heading


def safe_cuts(doc, page, rect):
    """Heights (in points from rect top) where a horizontal cut crosses no text: only white space, a horizontal rule,
    or the vertical borders of a table. Cutting there loses nothing; every pixel stays in exactly one crop."""
    import pymupdf
    scale = 2
    pix = doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=pymupdf.Rect(rect), colorspace=pymupdf.csGRAY)
    w, h, data = pix.width, pix.height, pix.samples
    dark = [[data[y * pix.stride + x] < 160 for x in range(w)] for y in range(h)]
    # Vertical rules: columns dark in most rows. They cross every cut, so they are ignored when looking for text.
    rule_cols = {x for x in range(w) if sum(dark[y][x] for y in range(h)) > 0.6 * h}
    rule_cols |= {x + d for x in rule_cols for d in (-2, -1, 1, 2)}
    cuts = []
    for y in range(h):
        ink = sum(1 for x in range(w) if dark[y][x] and x not in rule_cols)
        if ink == 0 or ink > 0.6 * w:  # blank row or a horizontal rule
            cuts.append(rect[1] + y / scale)
    return cuts


def split_rect(doc, page, rect):
    x0, y0, x1, y1 = rect
    limit = (x1 - x0) * MAX_RATIO
    if y1 - y0 <= limit:
        return [rect]
    cuts = safe_cuts(doc, page, rect)
    out, top = [], y0
    while y1 - top > limit:
        options = [c for c in cuts if top + 20 < c <= top + limit and y1 - c >= 20]  # no sliver crops
        if not options:
            raise SystemExit(f'page {page}: no safe cut within {limit:.0f}pt below y={top:.0f}; the scheme cannot be split without crossing text.')
        cut = round(max(options), 2)
        out.append([x0, top, x1, cut])
        top = cut
    out.append([x0, top, x1, y1])
    return out


def render(doc, page, rect, path, dpi):
    import pymupdf
    pix = doc[page - 1].get_pixmap(dpi=dpi, clip=pymupdf.Rect(rect))
    path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(path))
    return pix.width, pix.height


def cmd_pages(ps, file_id, dpi):
    doc = ps.pdf(file_id)
    out = ps.work / 'pages'
    out.mkdir(parents=True, exist_ok=True)
    for k, page in enumerate(doc, 1):
        page.get_pixmap(dpi=dpi).save(str(out / f'{file_id}-p{k:02}.png'))
    print(json.dumps({'event': 'pages', 'file': file_id, 'pages': doc.page_count, 'folder': 'work/pages'}))


def cmd_scan(ps, file_id):
    doc = ps.pdf(file_id)
    info = scan(doc)
    images = [dict(page=pn + 1, bbox=[round(v) for v in im['bbox']]) for pn in range(info['firstSchemePage'])
              for im in doc[pn].get_image_info() if pn + 1 < info['firstSchemePage'] or im['bbox'][1] < min(
                  [l['y0'] for l in info['labels'] if l['page'] == pn + 1] or [1e9])]
    info['questionImages'] = images
    print(json.dumps(info, indent=1))


def cmd_assets(ps, file_id):
    spec = ps.files[file_id]
    doc = ps.pdf(file_id)
    info = scan(doc)
    qs = sorted({q['q'] for q in info['questions']})
    if qs != list(range(1, len(qs) + 1)) or sorted(info['regions']) != qs:
        raise SystemExit(f'{file_id}: questions {qs} and scheme labels {sorted(info["regions"])} do not pair one to one.')
    if [t['marks'] for t in info['totals']] != [ps.data('questions.json')[file_id][str(q)]['marks'] for q in qs]:
        raise SystemExit(f'{file_id}: question totals differ from questions.json marks.')
    folder = f'resources/pmt/{file_id}'
    record = {'file': file_id, 'figures': {}, 'schemes': {}}
    moves = ps.data('scheme-moves.json', {})
    moved = {pg for m in moves.get(file_id, []) for pg in m['pages']}
    skipped = ps.skipped(file_id)
    for q, crops in scheme_crops(doc, info, moved).items():
        if q in skipped:
            continue
        crops = [dict(page=c['page'], rect=r) for c in crops for r in split_rect(doc, c['page'], c['rect'])]
        for k, c in enumerate(crops, 1):
            name = f'{folder}/q{q:02}-ms-p{c["page"]:02}-{k}.png'
            w, h = render(doc, c['page'], c['rect'], ps.repo / name, 150)
            record['schemes'].setdefault(str(q), []).append(dict(asset=name, page=c['page'], rect=c['rect'], width=w, height=h))
    # Scheme pages another file misplaced, which belong to a question here: appended after its own scheme, in page order.
    for src, entries in sorted(moves.items()):
        for m in entries:
            if m['to'] != file_id or m['q'] in skipped:
                continue
            sdoc = ps.pdf(src)
            pieces = []
            for pg in m['pages']:
                boxes = content_boxes(sdoc[pg - 1])
                rect = boxes[0]
                for b in boxes[1:]:
                    rect |= b
                rect = [round(v, 2) for v in (rect.x0 - 2, rect.y0 - 2, rect.x1 + 2, rect.y1 + 2)]
                pieces += [(pg, r) for r in split_rect(sdoc, pg, rect)]
            for k, (pg, r) in enumerate(pieces, 1):
                name = f'{folder}/q{m["q"]:02}-ms-from-{src}-p{pg:02}-{k}.png'
                w, h = render(sdoc, pg, r, ps.repo / name, 150)
                record['schemes'][str(m['q'])].append(dict(asset=name, page=pg, rect=r, width=w, height=h, sourceFile=src))
    for q, boxes in (ps.data('figs.json', {}).get(file_id) or {}).items():
        if int(q) in skipped:
            continue
        for k, (page, *rect) in enumerate(boxes, 1):
            name = f'{folder}/q{int(q):02}-fig-{k}.png'
            w, h = render(doc, page, rect, ps.repo / name, 200)
            record['figures'].setdefault(q, []).append(dict(asset=name, page=page, rect=rect, width=w, height=h))
    (ps.work / f'assets-{file_id}.json').write_text(json.dumps(record, indent=1))
    (ps.dir / 'assets').mkdir(exist_ok=True)
    (ps.dir / 'assets' / f'{file_id}.json').write_text(json.dumps(record, indent=1) + '\n')
    print(json.dumps({'event': 'pmt_assets', 'file': file_id, 'questions': len(qs),
                      'schemeCrops': sum(map(len, record['schemes'].values())), 'figures': sum(map(len, record['figures'].values()))}))


def scheme_html(spec, q, crops):
    out = []
    for k, c in enumerate(crops, 1):
        where = f'source page {c["page"]}' if 'sourceFile' not in c else f'appendix printed on page {c["page"]} of the {c["sourceFile"]} sheet'
        alt = (f'PMT mark scheme for {spec["course"]} {spec["sheet"]} Q{q}; {where}, segment {k} of {len(crops)}. '
               'Includes the working, marks, alternative methods and notes in source order.')
        out.append(f'<figure class="exam-solution-source" style="margin:2mm 0"><img src="{c["asset"]}" width="{c["width"]}" height="{c["height"]}" '
                   f'alt="{html.escape(alt, quote=True)}" style="display:block;width:100%;height:auto;max-width:100%"></figure>')
    return out


def cmd_payload(ps, file_id):
    spec = ps.files[file_id]
    record = json.loads((ps.dir / 'assets' / f'{file_id}.json').read_text())
    lib.load(record)
    prompts = common.module(ps.dir / 'prompts' / f'{file_id}.py', 'pmt_prompts_' + file_id.replace('-', '_')).Q
    meta = ps.data('questions.json')[file_id]
    skipped = ps.skipped(file_id)
    kept = sorted(q for q in prompts if q not in skipped)
    if sorted(prompts) != sorted(int(q) for q in meta) or kept != sorted(int(q) for q in record['schemes'] if int(q) not in skipped):
        raise SystemExit(f'{file_id}: prompts, questions.json and scheme crops cover different questions.')
    questions = []
    for q in kept:
        crops = record['schemes'][str(q)]
        questions.append({'id': f'pmt/{spec["book"]}/ch{spec["chapter"]}/q{q}', 'question': prompts[q],
                          'steps': scheme_html(spec, q, crops), 'contextHtml': '',
                          'sourceScheme': dict({'kind': 'source', 'page': sorted({c['page'] for c in crops if 'sourceFile' not in c})},
                                               **({'appendix': [{'file': f, 'page': sorted({c['page'] for c in crops if c.get('sourceFile') == f})}
                                                                for f in sorted({c['sourceFile'] for c in crops if 'sourceFile' in c})]}
                                                  if any('sourceFile' in c for c in crops) else {}))})
    duplicates.guard_import(questions, ps.repo, file_id)
    path = ps.repo / 'content' / 'pmt' / f'{file_id}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'schemaVersion': 1, 'questions': questions}, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'event': 'pmt_payload', 'file': file_id, 'questions': len(questions)}))


def skill_library(repo):
    # The skill taxonomy the app ships (data.js): skill id -> (book id, topic id). Every PMT mapping must name a real pair.
    text = (repo / 'data.js').read_text()
    lib = json.loads(text[text.index('{'):text.rindex('}') + 1])
    return {k['id']: (b['id'], t['id']) for c in lib['courses'] if c['id'] == 'further-maths-a-level'
            for b in c['books'] for t in b['topics'] for k in t['skills']}


def mappings(skills, library, where):
    out = []
    for s in skills:
        topic, skill = s.split(':')
        if library.get(skill, (None, None))[1] != topic:
            raise SystemExit(f'{where}: unknown skill mapping {s}')
        out.append({'courseId': 'further-maths-a-level', 'bookId': library[skill][0], 'topicId': topic, 'skillId': skill})
    if not out:
        raise SystemExit(f'{where}: no skill mapping')
    return out


def cmd_integrate(ps, file_id):
    spec = ps.files[file_id]
    record = json.loads((ps.dir / 'assets' / f'{file_id}.json').read_text())
    meta = ps.data('questions.json')[file_id]
    doc = ps.pdf(file_id)
    info = scan(doc)
    starts = {q['q']: q['page'] for q in info['questions']}
    ends = {k + 1: t['page'] for k, t in enumerate(info['totals'])}
    path = ps.repo / 'pmt-catalogue.json'
    catalogue = json.loads(path.read_text()) if path.exists() else {'version': 1, 'questions': []}
    prefix = f'pmt/{spec["book"]}/ch{spec["chapter"]}/'
    rows = [r for r in catalogue['questions'] if not r['id'].startswith(prefix)]
    library = skill_library(ps.repo)
    skipped = ps.skipped(file_id)
    meta = {q: m for q, m in meta.items() if int(q) not in skipped}
    for q, m in meta.items():
        if m['difficulty'] not in ('easy', 'medium', 'difficult') or not m['reason'].strip():
            raise SystemExit(f'{file_id} Q{q}: difficulty needs easy/medium/difficult and a reason')
        if m['marks'] != info['totals'][int(q) - 1]['marks']:
            raise SystemExit(f'{file_id} Q{q}: marks {m["marks"]} differ from the printed total')
        if m.get('duplicateOf'):
            raise SystemExit(f'{file_id} Q{q}: a copy of {m["duplicateOf"]} is not imported (PAP-077-2); add it to skip.json')
    for q in sorted(meta, key=int):
        m, n = meta[q], int(q)
        # A chapter is a number in this book, or 'book/number' for another book (a copy keeps its original's chapters).
        chapter_keys = [f'further-maths-a-level/{c if isinstance(c, str) else f"{spec["book"]}/{c}"}'
                        for c in m.get('chapters', [spec['chapter']])]
        rows.append({
            'id': prefix + f'q{n}', 'markScheme': 'source', 'questionNumber': n, 'originalQuestionLabel': f'Q{n}',
            'marks': m['marks'], 'difficulty': m['difficulty'], 'difficultyReason': m['reason'], 'topicSummary': m['summary'],
            'chapterKeys': chapter_keys,
            'skillMappings': mappings(m['skills'], library, f'{file_id} Q{n}'),
            'sourceLabel': f'PMT {spec["course"]} {spec["sheet"]} Q{n}', 'sheetId': file_id, 'sheetTitle': spec['title'],
            'board': 'PMT', 'status': 'checked', 'dataPath': f'content/pmt/{file_id}.json',
            'sourceSha256': spec['sha256'], 'sourceQuestionPages': list(range(starts[n], ends[n] + 1)),
            'schemePages': sorted({c['page'] for c in record['schemes'][q] if 'sourceFile' not in c}),
            'sourceNote': m.get('note')})
    order = {fid: k for k, fid in enumerate(sorted(ps.files))}
    rows.sort(key=lambda r: (r['dataPath'], r['questionNumber']))
    # Keep what removed duplicates added to a question here (PAP-077-1), and the migration map.
    earlier = {r['id']: r for r in catalogue['questions']}
    skill_key = lambda s: (s['courseId'], s['bookId'], s['topicId'], s['skillId'])
    for r in rows:
        old = earlier.get(r['id'])
        if old:
            r['chapterKeys'] += [k for k in old['chapterKeys'] if k not in r['chapterKeys']]
            r['skillMappings'] += [s for s in old['skillMappings'] if skill_key(s) not in {skill_key(x) for x in r['skillMappings']}]
    catalogue['questions'] = rows
    path.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'event': 'pmt_integrated', 'file': file_id, 'questions': len(meta), 'catalogue': len(rows)}))


def main():
    p = common.parser(__doc__, paper=False)
    p.add_argument('command', choices=['pages', 'scan', 'assets', 'payload', 'integrate'])
    p.add_argument('file', help='file id from files.py, e.g. pure-core-1-ch1')
    p.add_argument('--dpi', type=int, default=110)
    args = p.parse_args()
    ps = PmtSet(args)
    if args.file not in ps.files:
        raise SystemExit(f'Unknown file id {args.file!r}; see files.py')
    {'pages': lambda: cmd_pages(ps, args.file, args.dpi), 'scan': lambda: cmd_scan(ps, args.file),
     'assets': lambda: cmd_assets(ps, args.file), 'payload': lambda: cmd_payload(ps, args.file),
     'integrate': lambda: cmd_integrate(ps, args.file)}[args.command]()


if __name__ == '__main__':
    sys.exit(main())
