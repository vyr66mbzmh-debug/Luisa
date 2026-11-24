"""Read reviewed question paragraphs, equations and mark allocations from the AS import set."""
import html
import re
from pathlib import Path
from itertools import groupby

from lib import eq, fig, m, mk, p, table, ul

def inline(text):
    fields = text.split('$')
    if len(fields) % 2 == 0:
        raise ValueError(f'Unclosed maths in {text}')
    return ''.join(m(part) if i % 2 else html.escape(part) for i, part in enumerate(fields))

def read_questions(path):
    questions = {}
    for section in Path(path).read_text().strip().split('\n# '):
        heading, body = section.removeprefix('# ').split('\n', 1)
        number = int(heading)
        blocks = []
        figure_number = 0
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        for is_table, group in groupby(lines, key=lambda line: line.startswith('|')):
            if is_table:
                cells = [[inline(cell.strip()) for cell in line.strip('|').split('|')]
                         for line in group if not re.fullmatch(r'[ |:\-]+', line)]
                blocks.append(table(cells, head=1))
                continue
            for line in group:
                if line.startswith('@figure '):
                    width, alt = line.removeprefix('@figure ').split(' ', 1)
                    figure_number += 1
                    blocks.append(fig(number, int(width), alt, figure_number))
                elif re.fullmatch(r'\[\d+\]', line):
                    blocks.append(p(mk(int(line[1:-1]))))
                elif line.startswith('$$') and line.endswith('$$'):
                    blocks.append(eq(line[2:-2]))
                elif line.startswith('• '):
                    blocks.append(ul([inline(line[2:])]))
                else:
                    text, mark = re.fullmatch(r'(.*?)(?: \[(\d+)\])?', line).groups()
                    content = inline(text) + (' ' + mk(int(mark)) if mark else '')
                    blocks.append(p(content))
        if number in questions:
            raise ValueError(f'Duplicate question {number}')
        questions[number] = ''.join(blocks)
    return questions
