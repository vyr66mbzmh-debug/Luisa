"""Add one past paper to content/exams/pilot-metadata.json and exam-catalogue.json (idempotent).

Usage: python3 -I scripts/import/integrate.py --set <set> <paperId>
Inputs from the set: papers.py (PAPERS, ORDER = metadata order of every paper, newest session first), maps.py
(MAPS {pid: {n: (topic summary, skill ids, chapter keys or [])}}), marks.json {pid: [marks per question]} and
qpends.json {pid: [last question-paper page per question]}. Difficulty follows the original paper order in thirds.

PAP-077-2 (standing): before anything is written, the paper's payload is compared with the whole bank
(scripts/duplicates.py). A question that copies an official question already in the bank (the same paper imported
twice) stops the import; a question that copies a PMT question is imported and the PMT question is then removed with
`scripts/duplicates.py remove`. Chapter keys and skill mappings a question gained from a removed duplicate are kept
when the paper is integrated again.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import duplicates  # noqa: E402

args = common.parser(__doc__).parse_args()
SET = common.ImportSet(args)
ROOT, PID, PAPERS, ORDER = SET.repo, args.paper, SET.papers, SET.order
assert ORDER and PID in ORDER, 'papers.py must define ORDER including this paper'
MAPS = SET.maps()
P = PAPERS[PID]; SESSION = P['session']; MAP = MAPS[PID]; nq = P['nq']
marks = SET.data('marks.json')[PID]; assert len(marks) == nq and sum(marks) == P['total']
ends = SET.data('qpends.json')[PID]
pages = [[(ends[n - 2] + 1) if n > 1 else 2, ends[n - 1]] for n in range(1, nq + 1)]
band = nq // 3; easy, diff = band, band
level = lambda n: 'easy' if n <= easy else 'difficult' if n > nq - diff else 'medium'
lib = json.loads((ROOT / 'data.js').read_text().removeprefix('window.FMQ_LIBRARY=').rstrip(';\n'))
where = {s['id']: (c['id'], b['id'], t['id']) for c in lib['courses'] for b in c['books'] for t in b['topics'] for s in t['skills']}
textbook = json.loads((ROOT / 'textbook-catalogue.json').read_text())
targets = {}
for q in textbook['questions']:
    targets.setdefault(q['skill'], set()).update(t['book'] + '/' + str(t['chapter']) for t in q['targets'])
course = 'further-maths-a-level' if P['code'].startswith('9FM') else 'maths-a-level'
rank = {b['id'] + '/' + c['id']: i for i, (b, c) in enumerate((b, c) for b in textbook['books'] for c in b['chapters'])}
short = P['code'].replace('/', '')
rows = []
for n in range(1, nq + 1):
    summary, skills, chapters = MAP[n]
    mappings = [dict(zip(('courseId', 'bookId', 'topicId'), where[s]), skillId=s) for s in skills]
    derived = set().union(*(targets.get(s, set()) for s in skills))
    keys = chapters or sorted(derived, key=rank.get)
    assert keys and all(k in rank for k in keys), (n, keys)
    rows.append({'id': f'exam/{PID}/q{n}', 'originalQuestionNumber': n, 'originalQuestionLabel': str(n), 'marks': marks[n - 1],
                 'difficulty': level(n), 'topicSummary': summary, 'skillMappings': mappings, 'printable': True, 'contentStatus': 'checked',
                 'sourceQuestionPages': pages[n - 1], 'questionNumber': n, 'sourceLabel': f'Edexcel {SESSION} {P["code"]} Q{n}',
                 '_chapterKeys': [course + '/' + k for k in keys]})
payload = json.loads((ROOT / f'content/exams/{PID}.json').read_text())
duplicates.guard_import(payload['questions'], ROOT, PID)
cat_path = ROOT / 'exam-catalogue.json'; cat = json.loads(cat_path.read_text())
earlier = {q['id']: q for q in cat['questions'] if q.get('paperId') == PID}
skill_key = lambda s: (s['courseId'], s['bookId'], s['topicId'], s['skillId'])
for r in rows:  # keep what a removed duplicate added to this question (PAP-077-1)
    old = earlier.get(r['id'])
    if old:
        r['skillMappings'] += [s for s in old['skillMappings'] if skill_key(s) not in {skill_key(x) for x in r['skillMappings']}]
        r['_chapterKeys'] += [k for k in old['chapterKeys'] if k not in r['_chapterKeys']]
source = {'questionPaperUrl': P['qpurl'], 'markSchemeUrl': P['msurl'], 'questionPaperSha256': P['qpsha'], 'markSchemeSha256': P['mssha'],
          'indexedQuestionPaperSha256': P['idxqp'], 'indexedMarkSchemeSha256': P['idxms'], 'basis': 'Owner-supplied original PDF attachment'}
paper = {'id': PID, 'board': 'Edexcel', 'qualification': 'A level', 'paperCode': P['code'], 'title': P['title'], 'examDate': P['date'],
         'seriesDate': P['series'], 'session': SESSION, 'questionCount': nq, 'totalMarks': P['total'], 'source': source,
         'difficultyPolicy': {'basis': 'original-paper-order', 'easyQuestions': [1, easy], 'mediumQuestions': [easy + 1, nq - diff],
                              'difficultQuestions': [nq - diff + 1, nq]},
         'questions': [{k: v for k, v in r.items() if k != '_chapterKeys'} for r in rows],
         'sourceVerification': {'questionPaperAndMarkSchemeTotalsAgree': True, 'originalQuestionOrderPreserved': True, 'totalMarksChecked': P['total']}}
meta_path = ROOT / 'content/exams/pilot-metadata.json'; meta = json.loads(meta_path.read_text())
meta['papers'] = [p for p in meta['papers'] if p['id'] != PID]
present = [p['id'] for p in meta['papers']]
later = [x for x in ORDER[ORDER.index(PID) + 1:] if x in present]
at = present.index(later[0]) if later else len(meta['papers'])
meta['papers'].insert(at, paper)
meta['questionCount'] = sum(p['questionCount'] for p in meta['papers']); meta['totalMarks'] = sum(p['totalMarks'] for p in meta['papers'])
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
cat['questions'] = [q for q in cat['questions'] if q.get('paperId') != PID]
new = [dict({k: v for k, v in r.items() if k != '_chapterKeys'}, board='Edexcel', paperId=PID, paperCode=P['code'], examDate=P['date'],
            seriesDate=P['series'], session=SESSION, status='checked', dataPath=f'content/exams/{PID}.json', chapterKeys=r['_chapterKeys']) for r in rows]
order = [p['id'] for p in meta['papers']]
cat['questions'] = sorted(cat['questions'] + new, key=lambda q: (order.index(q['paperId']), q['questionNumber']))
cat_path.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + '\n')
print(PID, 'papers', len(meta['papers']), 'questions', meta['questionCount'], 'marks', meta['totalMarks'], 'catalogue', len(cat['questions']))
for r in rows: print(' ', r['id'][-3:], r['difficulty'], r['marks'], r['sourceQuestionPages'], r['topicSummary'], [k.split('/', 1)[1] for k in r['_chapterKeys']])
