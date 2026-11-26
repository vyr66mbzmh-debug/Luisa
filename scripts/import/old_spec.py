"""Publish the converted revision collection, retaining its solutions and marking evidence."""
import argparse
from collections import defaultdict
from html import escape
import json
from pathlib import Path
import re
import subprocess
import tempfile

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = Path('resources/old-spec')
GROUP = 'old spec revision questions'
# Same assessed tasks, verified against the live bank after conversion. REV07-06
# and the 2024 paper have different mark allocations; each keeps its own scheme.
ADDITIONAL_MATCHES = {
    "REV02-02": "pmt/pure-core-1/ch3/q4",
    "REV05-01": "exam/edexcel-8fm0-01-2020-october/q8",
    "REV07-06": "exam/edexcel-9fm0-01-2024-june/q4",
    "REV10-04": "pmt/pure-core-2/ch3/q3",
    "REV11-01": "exam/edexcel-9fm0-01-2019-june/q2",
    "REV17-15": "pmt/pure-core-2/ch1/q1",
    "REV20-04": "pmt/pure-core-2/ch2/q9"
}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def argument(text, start):
    assert text[start] == '{', text[start:start + 80]
    depth = 1
    for end in range(start + 1, len(text)):
        if text[end] in '{}' and text[end - 1] != '\\':
            depth += 1 if text[end] == '{' else -1
            if depth == 0:
                return text[start + 1:end], end + 1
    raise ValueError(text[start:])


def maths(tex, display=False):
    tex = re.sub(r'\\(sech|cosech|cosec|arsinh|arcosh|artanh)\b', r'\\operatorname{\1}', tex)
    while m := re.search(r'\\mii\s*(?=\{)', tex):
        pos = m.end()
        entries = []
        for _ in range(4):
            item, pos = argument(tex, pos)
            entries.append(item)
        a, b, c, d = entries
        tex = tex[:m.start()] + r'\begin{pmatrix}' + a + '&' + b + r'\\' + c + '&' + d + r'\end{pmatrix}' + tex[pos:]
    if display:
        return f'<div class="equation" data-display="true" data-math="{escape(tex.strip())}"></div>'
    return f'<span class="inline-math" data-math="{escape(tex.strip())}"></span>'


def figure(path, label, scheme=False):
    cls = 'exam-solution-source' if scheme else 'old-spec-diagram'
    size = 'width:100%;max-height:210mm' if scheme else 'max-width:100%;max-height:65mm'
    return f'<figure class="{cls}" style="margin:2mm 0"><img src="{path}" alt="{escape(label)}" style="display:block;margin:auto;height:auto;object-fit:contain;{size}"></figure>'


def svg_page(pdf, index, destination):
    with pymupdf.open(pdf) as doc:
        destination.write_text(doc[index].get_svg_image(text_as_path=True))


class Transcription:
    def __init__(self, source, name, tmp):
        self.source, self.name, self.tmp = source, name.lower(), tmp
        self.diagram_count = 0

    def tikz(self, tex):
        self.diagram_count += 1
        name = f'{self.name}-solution-{self.diagram_count}'
        document = r'\documentclass[border=3pt]{standalone}\usepackage{tikz,amsmath,amssymb}\begin{document}' + tex + r'\end{document}'
        (self.tmp / 'figure.tex').write_text(document)
        subprocess.run(['lualatex', '-no-shell-escape', '-halt-on-error', '-interaction=batchmode', 'figure.tex'],
                       cwd=self.tmp, check=True, stdout=subprocess.DEVNULL)
        path = ASSETS / (name + '.svg')
        svg_page(self.tmp / 'figure.pdf', 0, ROOT / path)
        return figure(path, f'Worked diagram for {self.name.upper()}')

    def blocks(self, text):
        # Protect complete mathematical expressions and block content before handling prose.
        values = []
        def save(value, block=False):
            key = f'§{len(values)}§'
            values.append(value)
            return '\n\n' + key + '\n\n' if block else key
        text = re.sub(r'\\begin\{center\}\s*(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})\s*\\end\{center\}',
                      lambda m: save(self.tikz(m[1]), True), text, flags=re.S)
        def table(m):
            rows = m[1].replace(r'\hline', '').strip().split(r'\\')
            rows = ['<tr>' + ''.join('<td>' + ''.join(self.blocks(cell.replace(r'\hspace{10mm}', ' '))) + '</td>' for cell in row.split('&')) + '</tr>' for row in rows if row.strip()]
            return save('<table><tbody>' + ''.join(rows) + '</tbody></table>', True)
        text = re.sub(r'\\begin\{center\}\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}\\end\{center\}', table, text, flags=re.S)
        text = re.sub(r'\\begin\{(align|equation)\*\}(.*?)\\end\{\1\*\}', lambda m: save(maths((r'\begin{aligned}' + m[2] + r'\end{aligned}') if m[1]=='align' else m[2], True), True), text, flags=re.S)
        text = re.sub(r'\\\[(.*?)\\\]', lambda m: save(maths(m[1], True), True), text, flags=re.S)
        text = re.sub(r'\\\((.*?)\\\)', lambda m: save(maths(m[1])), text, flags=re.S)
        while m := re.search(r'\\(MathLine|SourceFigure|ExamMarks|credit|emph|textbf|textsuperscript)\{', text):
            arg, end = argument(text, m.end()-1)
            cmd = m[1]
            if cmd == 'MathLine':
                value = save(maths(arg, True), True)
            elif cmd == 'SourceFigure':
                label, end = argument(text, end)
                path = ASSETS / (arg.lower() + '.svg')
                svg_page(self.source / 'figures' / (arg + '.pdf'), 0, ROOT / path)
                value = save(figure(path, label or 'Question diagram') + (f'<p>{escape(label)}</p>' if label else ''), True)
            elif cmd in ('ExamMarks', 'credit'):
                value = save(f'<span class="marks">({int(arg)})</span>' if cmd == 'ExamMarks' else f'<small class="step-credit">[{int(arg)}]</small>')
            else:
                tag = {'emph':'em', 'textbf':'strong', 'textsuperscript':'sup'}[cmd]
                value = save(f'<{tag}>') + arg + save(f'</{tag}>')
            text = text[:m.start()] + value + text[end:]
        text = text.replace(r'\textquotesingle{}', '′').replace('--','–').replace('~',' ').replace(r'\%', '%')
        text = text.replace(r'\quad', ' ').replace(r'\\', '\n\n')
        text = re.sub(r'\\par\b', '\n\n', text)
        text = re.sub(r'\\(?:smallskip|medskip)\b', '', text)
        result = []
        for p in re.split(r'\n\s*\n',text):
            p = p.strip()
            if not p:
                continue
            if '\\' in p:
                raise ValueError(f'{self.name}: unknown prose markup {p}')
            html = re.sub(r'§(\d+)§', lambda m: values[int(m[1])], escape(p))
            result.append(html if html.startswith(('<figure','<table','<div')) else '<p>'+html+'</p>')
        return result


def marking_page(pdf, index, path):
    with pymupdf.open(pdf) as doc:
        page = doc[index]
        if page.get_image_info():
            # Export only the visible page. Keep scanned pixels in a binary image
            # rather than carrying a full base64 scan inside a vector drawing.
            path = path.with_suffix('.webp')
            pix = page.get_pixmap(dpi=240, colorspace=pymupdf.csRGB, alpha=False)
            Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(ROOT/path, lossless=True, method=3)
        else:
            path = path.with_suffix('.svg')
            (ROOT/path).write_text(page.get_svg_image(text_as_path=True))
    return path


def marking(src, q, conv):
    steps = []
    if q['markSchemeSources']:
        tex = (src/q['markScheme']).read_text()
        steps.extend('<p>'+escape(s)+'</p>' for s in re.findall(r'\{\\small ([^{}]+)\}', tex))
        for n, (kind, filename, page) in enumerate(re.findall(r'\\Evidence(Image|PDF)\{([^}]+)\}(?:\{(\d+)\})?', tex), 1):
            path = ASSETS / f'{conv.name}-ms-{n:02}'
            if kind == 'PDF':
                path = marking_page(src/filename, int(page)-1, path)
            else:
                path = path.with_suffix('.webp')
                with Image.open(src/filename) as image:
                    image.save(ROOT/path, lossless=True, method=3)
            steps.append(figure(path, f'Source marking table for {q["sourceLabel"]}, extract {n}', True))
        assert any('<figure' in s for s in steps)
    else:
        steps.append('<p>Suggested marking guide. Credit equivalent methods that satisfy the question.</p>')
        for part in q['markingCriteriaParts']:
            steps.append('<p><strong>'+escape(part['label'])+f' · {part["total"]} marks</strong></p>')
            for criterion in part['criteria']:
                steps.extend(conv.blocks(f'[{criterion["marks"]}] '+criterion['tex']))
    return steps


def convert(src):
    manifest = json.loads((src/'manifest.json').read_text())
    catalogue, payloads = [], defaultdict(list)
    (ROOT/ASSETS).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for number, q in enumerate(manifest['questions'], 1):
            conv = Transcription(src, q['id'], Path(tmp))
            uid = 'old-spec/' + conv.name
            pack = q['id'].split('-')[0].lower()
            data_path = 'content/old-spec/'+pack+'.json'
            keys = ['further-maths-a-level/'+k for k in q['chapterKeys']]
            marks = sum(part['total'] for part in q['markingCriteriaParts'])
            assert marks == q['suggestedTotalMarks'] and marks > 0
            descriptor = dict(id=uid, paperId='old-spec-revision', sourceLabel=q['sourceLabel'],
                              questionNumber=number, marks=marks, difficulty=q['difficulty'], chapterKeys=keys,
                              edited=q['edited'], packs=[m['appearance'] for m in q['packMemberships']],
                              markScheme='source' if q['markSchemeSources'] else 'editorial', dataPath=data_path)
            original = ADDITIONAL_MATCHES.get(q['id'], q['existingLuisaId'])
            if original:
                descriptor['canonicalId'] = original
            catalogue.append(descriptor)
            payloads[data_path].append(dict(id=uid, question=''.join(conv.blocks((src/q['question']).read_text())),
                                            steps=conv.blocks((src/q['solution']).read_text()), markSchemeSteps=marking(src,q,conv)))
    for path, data in payloads.items():
        write_json(ROOT/path, data)
    write_json(ROOT/'old-spec-catalogue.json', dict(version=1, group=GROUP, questions=catalogue))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('collection', type=Path)
    convert(parser.parse_args().collection)
