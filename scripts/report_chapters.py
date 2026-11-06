"""Refresh chapter resource links and derive course totals from the displayed rows."""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {'Pure': 'maths-pure-year', 'Core Pure': 'further-core-pure',
         'Statistics': 'maths-applied-year', 'Mechanics': 'maths-applied-year'}
RESOURCES = [('slides', 'Slides'), ('booklet', 'Booklet'), ('pdf', 'Textbook'),
             ('practice', 'Practice chapter')]


def rebuild(match, catalogue):
    name, table = match.groups()
    course, year = name.rsplit(' ', 1)
    if course not in BOOKS:
        return match[0]
    chapters = catalogue[f'{BOOKS[course]}-{year}']['chapters']
    counts = []
    def row(m):
        cells = m[1]
        num = re.match(r'<td>(\d+)\.', cells)
        if num:
            chapter = next(ch for ch in chapters if ch['number'] == int(num[1]))
            links = []
            for key, label in RESOURCES:
                url = chapter.get(key)
                if url:
                    if not (ROOT / unquote(urlsplit(url).path)).is_file():
                        raise ValueError(f'{name} {num[1]} missing {url}')
                    links.append(f'<a href="{html.escape(url)}">{label}</a>')
            cells, n = re.subn(r'<span class="chapter-links">.*?</span>',
                               '<span class="chapter-links">' + ' · '.join(links) + '</span>', cells)
            if n != 1:
                raise ValueError(f'Missing chapter cell: {name} {num[1]}')
            counts.append([(int(a),int(b)) for a,b in re.findall(r'(\d+)/(\d+) \(', cells)])
        elif '<b>Total</b>' in cells:
            totals = []
            for column in zip(*counts, strict=True):
                done, total = map(sum, zip(*column))
                state = 'complete' if done == total else 'progress' if done else 'not-started'
                totals.append(f'<td class="status-{state}">{done}/{total} ({done/total:.1%})</td>')
            cells = '<td><b>Total</b></td>' + ''.join(totals)
        return '<tr>' + cells + '</tr>'
    return f'<h2>{name}</h2><table>' + re.sub(r'<tr>(.*?)</tr>', row, table, flags=re.S) + '</table>'


if __name__ == '__main__':
    catalogue = json.loads((ROOT/'teaching-catalogue.js').read_text().split('=',1)[1].strip().rstrip(';'))
    for filename in sys.argv[1:]:
        path = Path(filename)
        path.write_text(re.sub(r'<h2>([^<]+)</h2><table>(.*?)</table>',
                               lambda m: rebuild(m,catalogue), path.read_text(), flags=re.S))
