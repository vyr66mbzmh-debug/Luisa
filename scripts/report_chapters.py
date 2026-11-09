"""Refresh chapter resource links and derive course totals from the displayed rows."""
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {'Pure': 'maths-pure-year', 'Core Pure': 'further-core-pure',
         'Statistics': 'maths-applied-year', 'Mechanics': 'maths-applied-year'}
RESOURCES = [('slides', 'Slides'), ('booklet', 'Booklet'), ('solutions', 'Solutions'), ('pdf', 'Textbook'),
             ('practice', 'Practice chapter')]


def release_counts(cells, record, chapter):
    booklet = ROOT / unquote(urlsplit(chapter['booklet']).path)
    deck = booklet.parent.parent / f"chapter-{chapter['number']:02}.json"
    for path, key in [(deck,'deckSha256'),(booklet,'bookletSha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != record[key]:
            raise ValueError(f'Review out of date: {path}')
    total = len(json.loads(deck.read_text())['slides'])
    if total != record['slides'] or record['pages'] != (total+1)//2:
        raise ValueError(f'Chapter count mismatch: {deck}')
    columns = re.findall(r'<td.*?</td>', cells, flags=re.S)
    for i, (done, target) in enumerate([(total,total),(record['slidesChecked'],total),
                                        (1,1),(record['bookletChecked'],1)],1):
        if not 0 <= done <= target:
            raise ValueError(f'Invalid checked count: {deck}')
        state = 'complete' if done == target else 'progress' if done else 'not-started'
        columns[i] = f'<td class="status-{state}">{done}/{target} ({done/target:.1%})</td>'
    return ''.join(columns)


def rebuild(match, catalogue, acceptance=None, release=None):
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
            if release is not None:
                key = f'{BOOKS[course]}-{year}-{num[1]}'
                cells = release_counts(cells, release[key], chapter)
            if course == 'Statistics' and acceptance:
                record = acceptance[f'{year}-{num[1]}']
                base = ROOT / f'resources/teaching/v003/applied-year-{year}'
                stem = f'chapter-{int(num[1]):02}'
                for artifact, fingerprint in [(base / (stem + '.json'), 'deckSha256'),
                                              (base / 'booklets' / (stem + '.pdf'), 'bookletSha256')]:
                    if hashlib.sha256(artifact.read_bytes()).hexdigest() != record[fingerprint]:
                        raise ValueError(f'Review out of date: {artifact.name}')
                columns = re.findall(r'<td.*?</td>', cells, flags=re.S)
                for index, total in [(2, record['slides']), (4, 1)]:
                    columns[index] = f'<td class="status-complete">{total}/{total} (100.0%)</td>'
                cells = ''.join(columns)
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
        content = path.read_text()
        acceptance = None
        if '<title>Luisa v0.33 chapter progress</title>' in content:
            acceptance = json.loads((ROOT/'docs/evidence/v033-statistics.json').read_text())['chapters']
        release = None
        if any(f'<title>Luisa v{v}' in content for v in ('0.36', '0.37')):
            release = json.loads((ROOT/'docs/evidence/v036-acceptance.json').read_text())['chapters']
        elif '<title>Luisa v0.35' in content:
            release = json.loads((ROOT/'docs/evidence/v035-acceptance.json').read_text())['chapters']
        elif '<title>Luisa v0.34' in content:
            release = json.loads((ROOT/'docs/evidence/v034-acceptance.json').read_text())['chapters']
        path.write_text(re.sub(r'<h2>([^<]+)</h2><table>(.*?)</table>',
                               lambda m: rebuild(m,catalogue,acceptance,release), content, flags=re.S))
