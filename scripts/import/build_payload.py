"""Write content/exams/<paperId>.json from the set's prompt file and the paper's asset record.

Usage: python3 -I scripts/import/build_payload.py --set <set> <paperId>
Each question gets its native HTML prompt (prompts/<paperId>.py: Q {n: html}, CONTEXT html or {n: html}) and
its ordered mark-scheme crops as solution steps. Every figure in the asset record must be used by a prompt.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import lib  # noqa: E402

args = common.parser(__doc__).parse_args()
SET = common.ImportSet(args)
PID = args.paper
lib.load(json.loads(SET.assets_path(PID).read_text()))
sys.path.insert(0, str(SET.dir))
mod = SET.prompts(PID)
P = SET.papers[PID]
assert sorted(mod.Q) == list(range(1, P['nq'] + 1)), 'prompts must cover every question'
used = {r['asset'] for rs in lib.ASSETS['figures'].values() for r in rs}
for a in used:
    assert any(a in q for q in mod.Q.values()), ('unused figure', a)
questions = []
for n in range(1, P['nq'] + 1):
    rows = lib.ASSETS['markScheme'][str(n)]
    steps = [(f'<figure class="exam-solution-source" style="margin:2mm 0"><img src="{r["asset"]}" alt="Official mark scheme '
              f'for original question {n}; source page {r["sourcePage"]}, segment {r["segment"]} of {r["segments"]}. '
              'Includes the original working, marks, alternative methods and examiner guidance in source order." '
              'style="display:block;width:100%;height:auto;max-width:100%"></figure>') for r in rows]
    questions.append({'id': f'exam/{PID}/q{n}', 'question': mod.Q[n], 'steps': steps,
                      'contextHtml': mod.CONTEXT[n] if isinstance(mod.CONTEXT, dict) else mod.CONTEXT})
    if note := P.get('schemeNotes', {}).get(str(n)):
        questions[-1]['schemeNote'] = note
(SET.repo / 'content/exams' / f'{PID}.json').write_text(json.dumps({'schemaVersion': 1, 'questions': questions}, ensure_ascii=False, indent=2) + '\n')
print('wrote', PID, len(questions), 'questions,', sum(len(q['steps']) for q in questions), 'scheme images')
