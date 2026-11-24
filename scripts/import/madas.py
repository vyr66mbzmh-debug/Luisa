"""Build the MADAS index and web vectors from the prepared, private paper collections."""
import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path

import pymupdf as pdf

ROOT = Path(__file__).resolve().parents[2]
TOPIC = re.compile(r'^(?:Pure|Statistics|Mechanics) Year [12], Ch\.')
HEADER = re.compile(r'^(?:Madas Paper [A-Z]\s*[-–]\s*Question \d+|Question\s+\d+\s*(?:\([*+]+\))?)\s*$', re.I)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def page_map(book):
    starts = {int(match[1]): page - 1 for _, title, page in book.get_toc()
              if (match := re.search(r'Question\s+(\d+)$', title))}
    sequence = list(starts.values()) + [len(book)]
    return {q: range(sequence[i], sequence[i + 1]) for i, q in enumerate(starts)}


def excerpt_map(tex):
    result = defaultdict(list)
    number = None
    for line in tex.splitlines():
        if match := re.search(r'\\questionmapping\{Question (\d+)\}', line):
            number = int(match[1])
        if match := re.match(r'\\sourcequestion\{(\d+)\}', line):
            result[number].append(int(match[1]) - 1)
    return result


def fragments(book, pages, folder, prefix, is_solution):
    chunks, words = [], []
    total = None
    for index in pages:
        page = book[index]
        lines = [(pdf.Rect(line['bbox']), ''.join(s['text'] for s in line['spans']).strip())
                 for block in page.get_text('dict')['blocks'] for line in block.get('lines', [])]
        top, bottom = 0, page.rect.height
        for box, text in lines:
            if HEADER.fullmatch(text) and box.y0 < 100:
                top = max(top, box.y1 + 1)
            if TOPIC.match(text):
                bottom = min(bottom, box.y0 - 1)
            match = re.search(r'Total mark for question \d+ is (\d+) marks?', text, re.I)
            if match:
                total = int(match[1])
                bottom = min(bottom, box.y0 - 1)
        if bottom <= top:
            continue
        # Use the rendered ink, including diagram strokes and shaded areas, to find
        # whitespace where printed questions and schemes can split across sheets.
        area = pdf.Rect(0, top, page.rect.width, bottom)
        image = page.get_pixmap(clip=area, colorspace=pdf.csGRAY, alpha=False)
        mask = bytes.maketrans(bytes(range(256)), bytes(int(v < 235) for v in range(256)))
        pixels = image.samples.translate(mask)
        occupied = []
        for row in range(image.height):
            scan = pixels[row*image.stride:row*image.stride+image.width]
            left = scan.find(b'\1')
            if left >= 0:
                occupied.append((row + image.y, left, scan.rfind(b'\1')))
        if not occupied:
            continue
        segments = []
        segment = []
        for line in occupied:
            if segment and line[0] - segment[-1][0] > 4 and line[0] - segment[0][0] > 210:
                segments.append(segment)
                segment = []
            segment.append(line)
        segments.append(segment)
        # Preserve the horizontal alignment of diagrams and calculations when
        # consecutive pieces of one question are placed on the page.
        content_left = max(0, min(row[1] for row in occupied) - 2)
        for seg in segments:
            box = pdf.Rect(content_left, max(top, seg[0][0]-2),
                           min(page.rect.width, max(r[2] for r in seg)+3), min(bottom, seg[-1][0]+3))
            verbal = ' '.join(t for b,t in sorted(lines,key=lambda v:(round(v[0].y0/3),v[0].x0))
                              if box.y0 <= (b.y0+b.y1)/2 <= box.y1 and t)
            verbal = re.sub(r'[\x00-\x08\x0b-\x1f]', '', verbal)
            words.append(verbal)
            fragment = pdf.open()
            dest = fragment.new_page(width=box.width,height=box.height)
            dest.show_pdf_page(dest.rect,book,index,clip=box)
            path = folder / f'{prefix}-{len(chunks)+1}.svg'
            path.write_text(dest.get_svg_image())
            fragment.close()
            alt = html.escape(verbal or ('Worked solution diagram' if is_solution else 'Question diagram'), quote=True)
            # Keep the printed type size consistent across short and long lines.
            width = round(box.width*4/3, 1)
            chunks.append(f'<figure class="madas-excerpt"><img src="{path.relative_to(ROOT).as_posix()}" alt="{alt}" style="--madas-width:{width}px"></figure>')
    return chunks, ' '.join(words), total


# Removed source appearances map to the retained problem for saved selections.
REMOVED_COPIES = {
    'madas/alevel-applied-f/q11': 'madas/alevel-applied-d/q12',
    'madas/alevel-applied-v/q2': 'madas/alevel-applied-a/q4',
    'madas/alevel-pure-o/q12': 'madas/alevel-applied-s/q2',
}


def merge_topics(index, removed):
    by_id = {row['id']: row for row in index}
    for old, retained in REMOVED_COPIES.items():
        for key in ('chapterKeys', 'skills'):
            row = by_id[retained]
            row[key] = list(dict.fromkeys(row[key] + removed[old][key]))


def run(source):
    index = []
    removed = {}
    catalogue = json.loads((ROOT/'textbook-catalogue.json').read_text())
    valid = {f"{b['course']}/{b['id']}/{ch['id']}" for b in catalogue['books'] for ch in b['chapters']}
    for folder in sorted(source.iterdir()):
        group = folder.name
        meta = json.loads(next(folder.glob('*.json')).read_text())
        as_level = group == 'as-pure'
        papers = defaultdict(list)
        if as_level:
            for paper in meta['papers']:
                papers[paper['paper']] = paper['questions']
        else:
            for q in meta:
                papers[q['paper_id'][-1]].append(q)
        for letter, questions in sorted(papers.items()):
            slug = f'{group}-{letter.lower()}'
            assets = ROOT/'resources/madas'/slug
            assets.mkdir(parents=True,exist_ok=True)
            data_path = f'content/madas/{slug}.json'
            sb = pdf.open(next(folder.glob(f'*Paper_{letter}_solutions.pdf')))
            qb = pdf.open(next(folder.glob(f'*Paper_{letter}' + ('.pdf' if as_level else '_verbatim.pdf'))))
            qm = page_map(qb) if as_level else excerpt_map(next(folder.glob(f'*Paper_{letter}.tex')).read_text())
            sm = page_map(sb)
            payload = []
            for q in questions:
                n = q['number'] if as_level else q['question_number']
                uid = f'madas/{slug}/q{n}'
                if as_level:
                    topics = [(s['id'].split(':')[0],s['id'].split(':')[1].split('.')[0],s['chapter']) for s in q['skills']]
                    skills = [s['id'] for s in q['skills']]
                else:
                    topics = [(s['book_id'],str(s['chapter']),s['title']) for s in q['topics']]
                    skills = [s['book_id']+':'+v['id'] for s in q['topics'] for v in s.get('skills',[])]
                keys = list(dict.fromkeys(f'maths-a-level/{b}/{c}' for b,c,_ in topics))
                if not keys or not set(keys)<=valid:
                    raise ValueError((uid,keys))
                if uid in REMOVED_COPIES:
                    removed[uid] = dict(chapterKeys=keys, skills=skills)
                    continue
                a,text,_ = fragments(qb,qm[n],assets,f'q{n}-question',False)
                steps,_,marks = fragments(sb,sm[n],assets,f'q{n}-solution',True)
                expected = q.get('part_marks',q.get('marks'))
                if expected and marks != sum(expected):
                    raise ValueError((uid,marks,expected))
                if not (a and steps and marks):
                    raise ValueError((uid,'missing content or marks',marks))
                level = {'as-pure':'AS Pure','alevel-pure':'A-level Pure','alevel-applied':'A-level Applied'}[group]
                label = f'MADAS {level} Paper {letter} Q{n}'
                index.append(dict(id=uid, marks=marks, markScheme='worked', difficulty='standard' if letter<'J' else 'hard' if letter<'S' else 'very-hard',
                                  sourceDifficulty='standard' if letter<'S' else 'extremely hard' if letter<'U' else 'hard',
                                  chapterKeys=keys, skills=skills, topicSummary=', '.join(dict.fromkeys(t for _,_,t in topics)),
                                  sourceLabel=label, questionNumber=n, dataPath=data_path, paperId=slug))
                steps.append(f'<p class="madas-total">Total mark for question {n} is {marks} marks.</p>')
                payload.append(dict(id=uid,question=''.join(a),steps=steps,promptText=text))
            sb.close()
            qb.close()
            write_json(ROOT/data_path,payload)
            print(slug,len(payload),flush=True)
    merge_topics(index, removed)
    write_json(ROOT/'madas-catalogue.json',dict(version=1,syllabus='Mostly follows the Pearson/Edexcel syllabus introduced for teaching from 2017.',sourceDifficulty='A–R standard, generally increasing. S and T extremely hard. U–Z hard.',questions=index,migrations=REMOVED_COPIES))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('prepared',type=Path,help='Folder containing as-pure, alevel-pure and alevel-applied prepared collections')
    run(parser.parse_args().prepared)
