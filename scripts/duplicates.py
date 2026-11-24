"""Question-bank duplicate detection (PAP-077-2, standing rule from v0.77). Python stdlib only.

From v0.77 no question may exist twice in the bank. This module finds candidate pairs across every
source (Luisa skill questions, Practice Booklet questions, official past papers and PMT topic-sheet
questions) from normalised question text, marks and equations; an agent confirms each candidate by
looking at both rendered questions and records the decision in docs/evidence/duplicate-decisions.json.

Rule (PAP-077-2):
* an official past paper always beats a PMT question (the PMT copy is deleted, its ID mapped to the paper's);
* between two PMT questions the earlier one (lower import order: book, chapter, question) is kept;
* the same official paper imported twice: the second copy is skipped (the importer refuses it);
* any other pair is recorded as a decision with the question kept.

Commands:
  python3 scripts/duplicates.py candidates [--root R] [--json]   every unresolved candidate pair
  python3 scripts/duplicates.py check [--root R]                 exit 1 when the bank breaks the rule
  python3 scripts/duplicates.py incoming FILE [--root R]         classify candidates between a new payload and the bank
  python3 scripts/duplicates.py remove --removed ID --retained ID --reason TEXT
                                                                 delete a PMT copy (carry-over, files, migration, record)

`errors(root)` is the gate check used by `scripts/luisa.py check`.
"""
import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = 'docs/evidence/duplicate-decisions.json'
# A pair is a candidate when its similarity reaches the threshold for its sources. Any pair that involves an
# imported exam question (official or PMT) is checked from IMPORTED: on the v0.76 bank every one of the 51
# confirmed PMT copies scored 0.535 or more, and the highest other pair 0.506. The owner's own Luisa and
# Practice Booklet questions hold many parallel exercises ("as Q4 with new numbers"), so only near-identical
# pairs among them are candidates.
IMPORTED = 0.4
OWN = 0.95
IMPORT_KINDS = {'official', 'pmt', 'madas'}
SHINGLE = 3
MIN_TOKENS = 12           # shorter prompts ("Simplify x^2 x^3") repeat legitimately across exercises
COMMON = 40               # shingles shared by more questions than this are boilerplate

MATH = re.compile(r'<[^>]*\bdata-math="([^"]*)"[^>]*>')
IMG = re.compile(r'<img\b[^>]*\bsrc="([^"]*)"[^>]*>')
TAG = re.compile(r'<[^>]+>')
MARKS = re.compile(r'<span class="marks">\(\d+\)</span>')
TEX_NOISE = re.compile(r'\\(?:left|right|displaystyle|textstyle|,|;|:|!|quad|qquad)\b|\\[,;:! ]')


def norm_tex(tex):
    tex = html.unescape(tex)
    tex = TEX_NOISE.sub('', tex)
    tex = re.sub(r'\\[dt]frac', r'\\frac', tex)
    tex = re.sub(r'\\(?:mathrm|text|operatorname|textrm|mathit|mathbf|boldsymbol|bm)\s*', '', tex)
    tex = re.sub(r'\\(?:begin|end)\{(?:aligned|gathered|align\*?|array)\}(?:\{[^}]*\})?|&', '', tex)
    tex = re.sub(r'[{}\s]', '', tex)
    return tex.lower()


def tokens(question_html):
    """Word and maths tokens of a prompt; marks, tags and LaTeX spacing are ignored."""
    text = MARKS.sub(' ', question_html or '')
    out = []
    pos = 0
    for m in MATH.finditer(text):
        out += words(text[pos:m.start()])
        tex = norm_tex(m.group(1))
        out += re.findall(r'\\[a-z]+|[a-z]+|\d+(?:\.\d+)?|[^\sa-z\d]', tex)
        pos = m.end()
    out += words(text[pos:])
    return out


def words(fragment):
    # A figure counts by its file name, so exercises that differ only in their diagrams stay distinct.
    fragment = IMG.sub(lambda m: ' img' + re.sub(r'[^a-z0-9]', '', Path(m.group(1)).stem.lower()) + ' ', fragment)
    plain = html.unescape(TAG.sub(' ', fragment)).lower()
    return re.findall(r'[a-z]+|\d+(?:\.\d+)?|[=<>+\-*/^()]', plain)


def equations(question_html):
    return sorted({norm_tex(m) for m in MATH.findall(question_html or '') if len(norm_tex(m)) > 3})


def _json(path):
    return json.loads(Path(path).read_text())


def _payload(root, path, cache):
    if path not in cache:
        data = _json(root / path)
        cache[path] = data['questions'] if isinstance(data, dict) else data
    return cache[path]


def bank(root=ROOT):
    """Every question in the bank: id, kind, marks, order, html."""
    root = Path(root)
    cache, out = {}, []
    textbook = _json(root / 'textbook-catalogue.json')
    for q in textbook['questions']:
        content = _payload(root, f'content/{q["skill"]}.json', cache)
        item = next((c for c in content if str(c.get('number')) == str(q['question']) and not c.get('reference')), None)
        if item:
            out.append({'id': 'luisa/' + q['id'], 'kind': 'luisa', 'marks': None, 'order': (3, q['id']),
                        'html': (item.get('contextHtml') or '') + item['question']})
    for q in _json(root / 'practice-catalogue.json')['questions']:
        item = next(c for c in _payload(root, q['dataPath'], cache) if c['id'] == q['id'])
        out.append({'id': q['id'], 'kind': 'practice', 'marks': None, 'order': (2, q['id']),
                    'html': (item.get('contextHtml') or '') + item['question']})
    for q in _json(root / 'exam-catalogue.json')['questions']:
        item = next(c for c in _payload(root, q['dataPath'], cache) if c['id'] == q['id'])
        out.append({'id': q['id'], 'kind': 'official', 'marks': q['marks'], 'paper': q['paperId'],
                    'order': (0, q.get('examDate') or q.get('seriesDate') or '', q['id']),
                    'html': item['question']})
    pmt = root / 'pmt-catalogue.json'
    if pmt.exists():
        for i, q in enumerate(_json(pmt)['questions']):
            item = next(c for c in _payload(root, q['dataPath'], cache) if c['id'] == q['id'])
            out.append({'id': q['id'], 'kind': 'pmt', 'marks': q['marks'], 'order': (1, pmt_order(q['id'])),
                        'duplicateOf': q.get('duplicateOf'), 'html': item['question']})
    madas = root / 'madas-catalogue.json'
    if madas.exists():
        for q in _json(madas)['questions']:
            item = next(row for row in _payload(root, q['dataPath'], cache) if row['id'] == q['id'])
            out.append({'id': q['id'], 'kind': 'madas', 'marks': q['marks'], 'order': (4, q['id']),
                        'html': html.escape(item['promptText'])})
    return out


def pmt_order(qid):
    """Import order of a PMT question: Core Pure 1 before 2, then chapter, then question."""
    m = re.fullmatch(r'pmt/pure-core-(\d)/ch(\d+)/q(\d+)', qid)
    return tuple(int(x) for x in m.groups()) if m else (9, 0, 0)


def shingles(toks):
    return {tuple(toks[i:i + SHINGLE]) for i in range(max(0, len(toks) - SHINGLE + 1))}


def similarity(a, b):
    """Jaccard similarity of token shingles, blended with equation overlap when both have equations."""
    sa, sb = a['_sh'], b['_sh']
    text = len(sa & sb) / len(sa | sb) if sa and sb else 0.0
    ea, eb = set(a['_eq']), set(b['_eq'])
    if ea and eb:
        return round(0.5 * text + 0.5 * len(ea & eb) / len(ea | eb), 3)
    return round(text, 3)


def threshold_for(a, b):
    return IMPORTED if {a['kind'], b['kind']} & IMPORT_KINDS else OWN


def candidates(items, threshold=None):
    """Candidate pairs (a, b, score) with a kept before b by the precedence rule."""
    for it in items:
        it['_tok'] = tokens(it['html'])
        it['_sh'] = shingles(it['_tok'])
        it['_eq'] = equations(it['html'])
    index = defaultdict(list)
    for n, it in enumerate(items):
        if len(it['_tok']) >= MIN_TOKENS:
            for s in it['_sh']:
                index[s].append(n)
    shared = defaultdict(int)
    for members in index.values():
        if 1 < len(members) <= COMMON:
            for i, x in enumerate(members):
                for y in members[i + 1:]:
                    shared[(x, y)] += 1
    out = []
    for (x, y), count in shared.items():
        a, b = items[x], items[y]
        if count < 0.25 * min(len(a['_sh']), len(b['_sh'])):
            continue
        score = similarity(a, b)
        if score >= (threshold if threshold is not None else threshold_for(a, b)):
            keep, drop = sorted((a, b), key=precedence)
            out.append((keep, drop, score))
    return sorted(out, key=lambda p: (-p[2], p[1]['id']))


def precedence(item):
    """Lower sorts first and is kept: official, then PMT (earliest first), then other sources."""
    return item['order']


def decisions(root=ROOT):
    path = Path(root) / DECISIONS
    if not path.exists():
        return {'duplicates': [], 'notDuplicates': []}
    return _json(path)


def pair_key(a, b):
    return tuple(sorted((a, b)))


def decided_pairs(known):
    return {pair_key(d['id'], d['checkedAgainst']) for d in known.get('notDuplicates', [])}


def removed_ids(root=ROOT):
    return {d['removed'] for d in decisions(root).get('duplicates', [])}


def migrations(root=ROOT):
    result = {}
    for name in ('pmt', 'practice'):
        path = Path(root) / f'{name}-catalogue.json'
        if path.exists():
            result.update(_json(path).get('migrations', {}))
    return result


def unresolved(root=ROOT, items=None):
    items = bank(root) if items is None else items
    decided = decided_pairs(decisions(root))
    return [(k, d, s) for k, d, s in candidates(items) if pair_key(k['id'], d['id']) not in decided]


def errors(root=ROOT):
    """Gate check: no copy links, no undecided candidate and no confirmed duplicate left in the bank."""
    root = Path(root)
    items = bank(root)
    ids = {it['id'] for it in items}
    errs = []
    for it in items:
        if it.get('duplicateOf'):
            errs.append(f'{it["id"]} is a copy of {it["duplicateOf"]}; delete the copy (PAP-077-1)')
    known = decisions(root)
    for d in known.get('duplicates', []):
        if d['removed'] in ids:
            errs.append(f'{d["removed"]} was confirmed a duplicate of {d["retained"]} but is still in the bank')
        if d['retained'] not in ids:
            errs.append(f'{d["retained"]} (kept for {d["removed"]}) is missing from the bank')
    for keep, drop, score in unresolved(root, items):
        errs.append(f'possible duplicate {drop["id"]} of {keep["id"]} (similarity {score}); confirm it and run '
                    f'"scripts/duplicates.py remove", or record it under notDuplicates in {DECISIONS}')
    removed = {d['removed'] for d in known.get('duplicates', [])}
    moves = migrations(root)
    for old, new in moves.items():
        if old in ids or new not in ids or old not in removed:
            errs.append(f'question migration {old} -> {new} is stale or unrecorded')
    for d in known.get('duplicates', []):
        if d['removed'].startswith(('pmt/', 'practice/')) and moves.get(d['removed']) != d['retained']:
            errs.append(f'removed {d["removed"]} has no migration to {d["retained"]}')
    return errs


def incoming(new, root=ROOT):
    """Classify candidates between new questions (payload rows) and the bank, by the PAP-077-2 rule.

    Returns (skip, replace, decide):
      skip    - new question loses: it copies an official question, or an earlier PMT question;
      replace - new official question copies an existing PMT question: import it, then run `remove`;
      decide  - any other candidate (for example against a Luisa or Practice Booklet question): confirm and
                record it under notDuplicates (or remove the copy) before importing.
    """
    root = Path(root)
    new_ids = {q['id'] for q in new}
    existing = [it for it in bank(root) if it['id'] not in new_ids]
    known = decisions(root)
    decided = decided_pairs(known)
    removed = {d['removed'] for d in known.get('duplicates', [])}
    fresh = []
    for q in new:
        if q['id'] in removed:
            continue
        kind = 'pmt' if q['id'].startswith('pmt/') else 'official'
        fresh.append({'id': q['id'], 'kind': kind, 'marks': None, 'html': q['question'], '_new': True,
                      'order': (1, pmt_order(q['id'])) if kind == 'pmt' else (0, '9999', q['id'])})
    skip, replace, decide = [], [], []
    for a, b, score in candidates(existing + fresh):
        if a.get('_new') == b.get('_new') or pair_key(a['id'], b['id']) in decided:
            continue
        new_q, old_q = (a, b) if a.get('_new') else (b, a)
        entry = {'new': new_q['id'], 'existing': old_q['id'], 'similarity': score}
        if old_q['kind'] in IMPORT_KINDS and not (new_q['kind'] == 'official' and old_q['kind'] == 'pmt'):
            skip.append(entry)
        elif new_q['kind'] == 'official' and old_q['kind'] in ('pmt', 'practice'):
            replace.append(entry)
        else:
            decide.append(entry)
    return skip, replace, decide


def guard_import(new, root=ROOT, label='import'):
    """Importer hook: stop an import while it holds an unconfirmed candidate (PAP-077-2)."""
    skip, replace, decide = incoming(new, root)
    if skip or decide:
        raise SystemExit(json.dumps({'event': 'duplicate_candidates', 'import': label, 'skip': skip, 'decide': decide,
                                     'action': 'Look at each pair. A confirmed copy is not imported: add its ID to the '
                                               'set\'s skip list (or, for an official paper imported twice, drop the paper). '
                                               f'A pair that is not a copy goes under notDuplicates in {DECISIONS}.'}, indent=1))
    for r in replace:
        print(json.dumps({'event': 'duplicate_replaces_' + r['existing'].split('/')[0], 'import': label, **r,
                          'action': f'after integrating, confirm visually and run: python3 scripts/duplicates.py remove '
                                    f'--removed {r["existing"]} --retained {r["new"]} --reason "..."'}))
    return replace


def _dump(path, data, **opts):
    path.write_text(json.dumps(data, ensure_ascii=False, **opts) + '\n')


def _assets(question):
    return set(re.findall(r'src="(resources/[^"]+)"', question['question'] + ''.join(question.get('steps', []))))


def remove(root, removed, retained, reason, similarity=None):
    """Delete the PMT or practice question `removed` in favour of `retained` (PAP-077-1/2).

    The survivor gains the copy's chapter keys and skill mappings it lacks (never its wording, marks, scheme or
    difficulty); the copy leaves the PMT catalogue, its payload and its own image files; copies of the copy and
    earlier migrations to it move to the survivor; the migration and the decision are recorded."""
    root = Path(root)
    family = removed.split('/')[0]
    if family not in ('pmt', 'practice') or (family == 'practice' and not retained.startswith('exam/')):
        raise SystemExit('A practice copy requires an official survivor. Official questions cannot be removed here.')
    cat_path = root / f'{family}-catalogue.json'
    cat = _json(cat_path)
    rows = {r['id']: r for r in cat['questions']}
    copy = rows.get(removed)
    if copy is None:
        raise SystemExit(f'{removed} is not in the {family} catalogue')
    exam_path, meta_path = root / 'exam-catalogue.json', root / 'content/exams/pilot-metadata.json'
    exam = _json(exam_path)
    exam_rows = {r['id']: r for r in exam['questions']}
    survivor = rows.get(retained) or exam_rows.get(retained)
    if survivor is None or retained == removed:
        raise SystemExit(f'{retained} is not a question in the bank')
    if retained.startswith('pmt/') and pmt_order(retained) > pmt_order(removed):
        raise SystemExit(f'{retained} is later than {removed}; the earlier PMT question is kept (PAP-077-2)')
    skill = lambda s: (s['courseId'], s['bookId'], s['topicId'], s['skillId'])
    if family == 'practice':
        source_skills = _json(root / 'textbook-catalogue.json')['skills']
        topics = {s['id']: s['topicId'] for s in cat['skills']}
        topics.update({sid: entry['topic'] for sid, entry in source_skills.items()})
        copy['chapterKeys'] = [f"{copy['courseId']}/{copy['bookId']}/{copy['chapterNumber']}"]
        copy['skillMappings'] = [dict(courseId=copy['courseId'], bookId=copy['bookId'],
                                      topicId=topics[sid], skillId=sid) for sid in copy['skillIds']]
    keys = [k for k in copy['chapterKeys'] if k not in survivor['chapterKeys']]
    skills = [s for s in copy['skillMappings'] if skill(s) not in {skill(x) for x in survivor['skillMappings']}]
    survivor['chapterKeys'] = survivor['chapterKeys'] + keys
    survivor['skillMappings'] = survivor['skillMappings'] + skills
    if retained in exam_rows:
        _dump(exam_path, exam, indent=2)
        meta = _json(meta_path)
        for paper in meta['papers']:
            for q in paper['questions']:
                if q['id'] == retained:
                    q['skillMappings'] = survivor['skillMappings']
        _dump(meta_path, meta, indent=2)
    # Remove the copy from its payload and delete image files no remaining question uses.
    payload_path = root / copy['dataPath']
    payload = _json(payload_path)
    gone = next(q for q in payload['questions'] if q['id'] == removed)
    payload['questions'] = [q for q in payload['questions'] if q['id'] != removed]
    _dump(payload_path, payload, indent=2 if family == 'practice' else 1)
    still = set()
    for f in (root / 'content/pmt').glob('*.json') if family == 'pmt' else ():
        for q in _json(f)['questions']:
            still |= _assets(q)
    deleted = sorted(a for a in _assets(gone) - still if a.startswith('resources/pmt/') and (root / a).is_file())
    for a in deleted:
        (root / a).unlink()
    cat['questions'] = [r for r in cat['questions'] if r['id'] != removed]
    for r in cat['questions']:
        if r.get('duplicateOf') == removed:
            r['duplicateOf'] = retained
    moves = cat.get('migrations', {})
    moves = {old: (retained if new == removed else new) for old, new in moves.items()}
    moves[removed] = retained
    cat['migrations'] = dict(sorted(moves.items()))
    _dump(cat_path, cat, indent=2)
    dec_path = root / DECISIONS
    dec = decisions(root)
    dec.setdefault('duplicates', [])
    dec['duplicates'] = [d for d in dec['duplicates'] if d['removed'] != removed]
    for d in dec['duplicates']:
        if d['retained'] == removed:
            d['retained'] = retained
    dec['duplicates'].append({k: v for k, v in {'removed': removed, 'retained': retained, 'reason': reason,
                                                 'similarity': similarity}.items() if v is not None})
    _dump(dec_path, dec, indent=1)
    return {'removed': removed, 'retained': retained, 'chapterKeysAdded': keys,
            'skillMappingsAdded': [s['skillId'] for s in skills], 'filesDeleted': len(deleted)}


def report(pairs):
    return [{'retained': k['id'], 'candidate': d['id'], 'similarity': s} for k, d, s in pairs]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('command', choices=['candidates', 'check', 'incoming', 'remove'])
    parser.add_argument('file', nargs='?', help='incoming: a payload JSON (content/pmt/... or content/exams/...)')
    parser.add_argument('--root', default=str(ROOT))
    parser.add_argument('--removed')
    parser.add_argument('--retained')
    parser.add_argument('--reason')
    args = parser.parse_args()
    root = Path(args.root)
    if args.command == 'candidates':
        print(json.dumps(report(unresolved(root)), indent=1))
    elif args.command == 'incoming':
        data = _json(args.file)
        skip, replace, decide = incoming(data['questions'] if isinstance(data, dict) else data, root)
        print(json.dumps({'skip': skip, 'replace': replace, 'decide': decide}, indent=1))
    elif args.command == 'remove':
        if not (args.removed and args.retained and args.reason):
            parser.error('remove needs --removed, --retained and --reason')
        print(json.dumps(remove(root, args.removed, args.retained, args.reason)))
    else:
        errs = errors(root)
        for e in errs:
            print(json.dumps({'event': 'duplicate_failure', 'message': e}))
        print(json.dumps({'event': 'duplicates_pass' if not errs else 'duplicates_fail', 'questions': len(bank(root))}))
        raise SystemExit(1 if errs else 0)


if __name__ == '__main__':
    main()
