"""Install exported two-up booklet panels into their approved chapter pages.

The reference PDF supplies the title panel, teaching banners and page geometry.
The panel PDFs contain the typeset teaching and the appropriate answer state.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import subprocess

import pymupdf as pdf


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def banner(page, slide):
    lower = slide % 2 == 0
    matches = [
        shape['rect'] for shape in page.get_drawings()
        if shape.get('fill') and shape['rect'].width > 500
        and max(abs(channel - target) for channel, target in
                zip(shape['fill'], (.0941, .2235, .3412))) < .008
        and (shape['rect'].y0 > page.rect.height / 2) == lower
    ]
    if len(matches) != 1:
        raise ValueError(f'Unrecognised teaching banner on slide {slide}')
    return matches[0]


def add_question_alternative(page, rectangle, description):
    """Put the crop description in PDF reading order without drawing over it."""
    page.insert_text((rectangle.x0 + 1, rectangle.y0 + 2), ' ', fontsize=1, render_mode=3)
    document = page.parent
    stream = page.get_contents()[-1]
    content = document.xref_stream(stream)
    actual = (b'\xfe\xff' + description.encode('utf-16-be')).hex().encode('ascii')
    document.update_stream(stream, b'/Span <</ActualText <' + actual + b'>>> BDC\n' + content + b'EMC\n')


def update(chapter, key, edition, slides, args):
    relative = Path(chapter['booklet' if edition == 'student' else 'solutions'])
    source = args.stage/'baseline'/relative
    target = args.stage/'updated'/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        with source.open('wb') as stream:
            subprocess.run(['git', 'show', f'{args.revision}:{relative}'],
                           cwd=args.repository, stdout=stream, check=True)
    with pdf.open(source) as reference, pdf.open() as document:
        by_page = defaultdict(list)
        for slide in slides:
            by_page[(slide - 1) // 2].append(slide)
        for index, original in enumerate(reference):
            selected = by_page.get(index, [])
            if not selected:
                document.insert_pdf(reference, from_page=index, to_page=index)
                continue
            page = document.new_page(width=original.rect.width, height=original.rect.height)
            cuts, inserts, paint = [], [], []
            for slide in selected:
                header = banner(original, slide)
                bottom = 829.125 if slide % 2 == 0 else 415.875
                area = pdf.Rect(header.x0 + 1.1, header.y1 + 1.25, header.x1 - 1.1, bottom - 1.5)
                cuts.append(area)
                body = pdf.Rect(area.x0 + 2.1, area.y0 + 1.8, area.x1 - 2.1, area.y1 - 2.1)
                inserts.append((body, args.stage/'panels'/key/f'{edition}-{slide}.pdf'))
                if key == 'maths-pure-year-1-14' and slide in (8, 9):
                    old = pdf.Rect(18, header.y0 + .75, 60, header.y1 - .3)
                    cuts.append(old)
                    paint.append(old)
                    formula = pdf.Rect(21.668, header.y0 + 3.0, 55.5, header.y1 - 3.0)
                    inserts.append((formula, args.stage/'header-equation.pdf'))
            # Impose the retained original strips at 1:1. Native PDF clipping
            # leaves the edited teaching area out of both page drawing and
            # searchable text, and preserves untouched glyph positions exactly.
            y = 0
            for cut in sorted(cuts, key=lambda box: box.y0):
                for keep in [pdf.Rect(0, y, page.rect.width, cut.y0),
                             pdf.Rect(0, cut.y0, cut.x0, cut.y1),
                             pdf.Rect(cut.x1, cut.y0, page.rect.width, cut.y1)]:
                    if not keep.is_empty:
                        page.show_pdf_page(keep, reference, index, clip=keep)
                y = cut.y1
            keep = pdf.Rect(0, y, page.rect.width, page.rect.height)
            if not keep.is_empty:
                page.show_pdf_page(keep, reference, index, clip=keep)
            for old in paint:
                page.draw_rect(old, color=None, fill=(.0941, .2235, .3412))
            for area, name in inserts:
                with pdf.open(name) as panel:
                    if len(panel) != 1:
                        raise ValueError(f'Unexpected pagination for {name.name}')
                    page.show_pdf_page(area, panel, 0)
                    scale = min(area.width / panel[0].rect.width, area.height / panel[0].rect.height)
                    dx = area.x0 + (area.width - panel[0].rect.width * scale) / 2
                    dy = area.y0 + (area.height - panel[0].rect.height * scale) / 2
                    matrix = pdf.Matrix(scale, 0, 0, scale, dx, dy)
                    for note in args.alternatives.get(str(name.relative_to(args.stage)), []):
                        add_question_alternative(page, pdf.Rect(note['area']) * matrix, note['text'])
                    for link in panel[0].get_links():
                        if link.get('uri'):
                            page.insert_link({'kind':pdf.LINK_URI, 'uri':link['uri'], 'from':link['from'] * matrix})
            for link in original.get_links():
                if link.get('uri') and all((link['from'] & cut).is_empty for cut in cuts):
                    page.insert_link({'kind':pdf.LINK_URI, 'uri':link['uri'], 'from':link['from']})
        document.save(target, garbage=4, deflate=True, no_new_id=True)
    return {'file': str(relative), 'sha256': sha(target), 'baselineSha256': sha(source)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repository', type=Path)
    p.add_argument('stage', type=Path)
    p.add_argument('revision')
    p.add_argument('plans', nargs='+', type=Path)
    p.add_argument('--alternatives', type=Path, help='Printed question crop descriptions and PDF rectangles')
    args = p.parse_args()
    args.alternatives = json.loads(args.alternatives.read_text()) if args.alternatives else {}
    catalogue = json.loads((args.repository/'teaching-catalogue.js').read_text().split('=', 1)[1].strip().rstrip(';'))
    chapters = {f'{book}-{entry["number"]}': entry for book, volume in catalogue.items()
                for entry in volume['chapters']}
    selected = defaultdict(set)
    for plan in args.plans:
        for item in json.loads(plan.read_text()):
            selected[item['chapterKey']].add(item['slide'])
    records = {}
    for key, slides in sorted(selected.items()):
        ordered = sorted(slides)
        record = {'slides': ordered}
        for edition in ('student','solution'):
            record[edition] = update(chapters[key], key, edition, ordered, args)
        records[key] = record
        print(key, len(slides), flush=True)
    (args.stage/'assembled.json').write_text(json.dumps(records, indent=2)+'\n')


if __name__ == '__main__':
    main()
