"""PAP-074-1: derive the internal mark-scheme flag for every question in the Papers bank.

Every catalogue row carries ``markScheme``:

* ``official`` - the paired official exam-board mark scheme (past papers: crops of the official scheme PDF);
* ``source``   - an equivalent marking scheme printed in the question's own source (method/accuracy marks);
* ``worked``   - Luisa worked solutions only (never presented as a mark scheme);
* ``none``     - neither.

Only ``official`` and ``source`` questions are eligible for the teacher-only exam paper (PAP-074-2).
The value is derived from the question payloads, never typed by hand:

    python3 scripts/mark_schemes.py apply   # write the derived values into the three catalogues
    python3 scripts/mark_schemes.py check   # fail if any stored value differs from the derivation
    python3 scripts/mark_schemes.py counts  # counts per source, for the release issue
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ('official', 'source', 'worked', 'none')
ELIGIBLE = ('official', 'source')
CATALOGUES = {  # file -> (json dump options)
    'textbook-catalogue.json': dict(separators=(',', ':'), ensure_ascii=False),
    'practice-catalogue.json': dict(indent=2, ensure_ascii=False),
    'exam-catalogue.json': dict(indent=2, ensure_ascii=False),
    'pmt-catalogue.json': dict(indent=2, ensure_ascii=False),
}
# Every historical import stores the official scheme as figures cropped from the board's mark-scheme PDF,
# named resources/exams/<paper>/q<N>-ms-..., with alt text starting "Official" or "Original".
OFFICIAL_STEP = re.compile(r'^<figure[^>]*>\s*<img src="(resources/exams/([a-z0-9-]+)/q\d+[a-z]?-ms-[^"]+)"[^>]*'
                           r'alt="(?:Official|Original) [^"]*"[^>]*>\s*</figure>$', re.I)


def _json(path):
    return json.loads(path.read_text())


def _steps_kind(steps):
    return 'worked' if any(str(step).strip() for step in steps or []) else 'none'


def exam_kind(question, root=ROOT):
    """Past papers: every step must be a crop of the official mark scheme; anything else is a data error."""
    steps = question.get('steps') or []
    paper = question['id'].split('/')[1]
    for step in steps:
        match = OFFICIAL_STEP.match(step.strip())
        if not match or match.group(2) != paper or not (root / match.group(1)).is_file():
            raise ValueError(f"{question['id']}: past-paper steps are not all official mark-scheme crops of this paper")
    if not steps:
        raise ValueError(f"{question['id']}: past paper without its official mark scheme")
    return 'official'


def source_kind(question, root=ROOT):
    """Questions imported with their source's own marking scheme (for example PMT revision sheets)."""
    scheme = question.get('sourceScheme')
    if scheme:
        if scheme.get('kind') not in ELIGIBLE or not scheme.get('page'):
            raise ValueError(f"{question['id']}: sourceScheme needs kind official|source and its source page")
        if question['id'].startswith('pmt/'):
            # Every step must be a crop of this question's own scheme in its source sheet (v0.75 review).
            book, chapter, q = question['id'].split('/')[1:]
            crop = re.compile(rf'<figure class="exam-solution-source"[^>]*><img src="(resources/pmt/{re.escape(book)}-{chapter}/'
                              rf'q{int(q[1:]):02}-ms-(?:from-[a-z0-9-]+-)?p\d+-\d+\.png)"[^>]*></figure>')
            steps = question.get('steps') or []
            found = [crop.fullmatch(step) for step in steps]
            if not steps or not all(m and (root / m.group(1)).is_file() for m in found):
                raise ValueError(f"{question['id']}: a source scheme must consist of this question's own scheme crops")
        return scheme['kind']
    return _steps_kind(question.get('steps'))


def derive(root=ROOT):
    """Return {catalogue file: {row id: value}} derived from the payloads."""
    out = {name: {} for name in CATALOGUES}
    skills = {}
    for q in _json(root / 'textbook-catalogue.json')['questions']:
        if q['skill'] not in skills:
            skills[q['skill']] = {str(x['number']): x for x in _json(root / 'content' / (q['skill'] + '.json'))}
        out['textbook-catalogue.json'][q['id']] = _steps_kind(skills[q['skill']][str(q['question'])].get('steps'))
    payloads = {}
    for q in _json(root / 'practice-catalogue.json')['questions']:
        if q['dataPath'] not in payloads:
            payloads[q['dataPath']] = {x['id']: x for x in _json(root / q['dataPath'])['questions']}
        out['practice-catalogue.json'][q['id']] = source_kind(payloads[q['dataPath']][q['id']], root)
    for q in _json(root / 'pmt-catalogue.json')['questions']:
        if q['dataPath'] not in payloads:
            payloads[q['dataPath']] = {x['id']: x for x in _json(root / q['dataPath'])['questions']}
        out['pmt-catalogue.json'][q['id']] = source_kind(payloads[q['dataPath']][q['id']], root)
    for q in _json(root / 'exam-catalogue.json')['questions']:
        if q['dataPath'] not in payloads:
            payloads[q['dataPath']] = {x['id']: x for x in _json(root / q['dataPath'])['questions']}
        out['exam-catalogue.json'][q['id']] = exam_kind(payloads[q["dataPath"]][q["id"]], root)
    return out


def _with_flag(row, value):
    """Insert markScheme right after the id so diffs stay small and the field is easy to find."""
    result = {}
    for key, item in row.items():
        if key == 'markScheme':
            continue
        result[key] = item
        if key == 'id':
            result['markScheme'] = value
    return result


def apply(root=ROOT):
    derived = derive(root)
    for name, options in CATALOGUES.items():
        path = root / name
        data = _json(path)
        data['questions'] = [_with_flag(q, derived[name][q['id']]) for q in data['questions']]
        path.write_text(json.dumps(data, **options) + '\n')
    return derived


def errors(root=ROOT):
    try:
        derived = derive(root)
    except (ValueError, KeyError, StopIteration) as error:
        return ['Mark-scheme flag cannot be derived: ' + str(error)]
    found = []
    for name in CATALOGUES:
        for q in _json(root / name)['questions']:
            if q.get('markScheme') not in VALUES:
                found.append(f'{name}: {q["id"]} has no valid markScheme')
            elif q['markScheme'] != derived[name][q['id']]:
                found.append(f'{name}: {q["id"]} markScheme {q["markScheme"]} but the payload gives {derived[name][q["id"]]}')
    return found


def counts(root=ROOT):
    """Counts per Papers source (the tickboxes) and value."""
    table = collections.Counter()
    practice = {q['id']: q for q in _json(root / 'practice-catalogue.json')['questions']}
    for name in CATALOGUES:
        for q in _json(root / name)['questions']:
            if name == 'textbook-catalogue.json':
                source = 'Practice questions (Luisa skill questions)'
            elif name == 'exam-catalogue.json':
                source = 'Past Papers'
            elif name == 'pmt-catalogue.json':
                source = 'PMT (' + q['sheetId'].split('-ch')[0] + ')'
            else:
                source = q.get('sourceLabel') or ('Exam style (Practice Booklet)' if practice[q['id']].get('bank') == 'exam' else 'Practice questions (Practice Booklet)')
            table[(source, q['markScheme'])] += 1
    return table


def main(argv):
    command = argv[1] if len(argv) > 1 else 'check'
    if command == 'apply':
        derived = apply()
        print(json.dumps({'event': 'mark_schemes_applied', 'questions': sum(map(len, derived.values()))}))
    elif command == 'check':
        found = errors()
        for error in found[:20]:
            print(json.dumps({'event': 'mark_scheme_failure', 'message': error}))
        if found:
            raise SystemExit(1)
        print(json.dumps({'event': 'mark_schemes_pass'}))
    elif command == 'counts':
        for (source, value), n in sorted(counts().items()):
            print(f'{source}\t{value}\t{n}')
    else:
        raise SystemExit('usage: mark_schemes.py apply|check|counts')


if __name__ == '__main__':
    main(sys.argv)
