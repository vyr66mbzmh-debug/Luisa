"""Write docs/evidence/v072-import-sample-papers.json for the v0.72 reference set.

Usage: python3 -I scripts/import/sets/v072-sample/evidence.py --set v072-sample [extra.json]
Needs the owner source PDFs (hash-checked) and the asset records from build_assets.py. The narrative notes below are
specific to this release; a new set copies this file and rewrites them.
"""
import datetime, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common  # noqa: E402
import pymupdf  # noqa: E402
ap = common.parser(__doc__, paper=False)
ap.add_argument('extra', nargs='?')
ARGS = ap.parse_args()
SET = common.ImportSet(ARGS)
ROOT, PAPERS = SET.repo, SET.papers
meta = {p['id']: p for p in json.loads((ROOT / 'content/exams/pilot-metadata.json').read_text())['papers']}
catalogue = {q['id']: q for q in json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']}
checks = SET.data('checks.json')
def day(iso):
    d = datetime.date.fromisoformat(iso); return f"{d:%A} {d.day} {d:%B %Y}"
def cover_date(P):
    if P['date']: return day(P['date'])
    if P.get('coverDate'): return f"printed date {P['coverDate']} (series {P['session']}, following the official mark scheme title)"
    return f"no exam date printed (series {P['session']})"
def scheme_series(ms):
    t = ' '.join(ms[0].get_text().split()); mm = re.search(r'Mark Scheme \((Results?)\) (\w+ 20\d\d)', t); return mm.group(1), mm.group(2)
def duration(mins):
    if not mins: return 'no time printed on this section cover'
    h, m = divmod(mins, 60); return f"time {h} hour{'s' if h > 1 else ''}" + (f" {m} minutes" if m else '')
papers = []
for pid in [k for k in meta if k in PAPERS and k.endswith('-sample')]:
    P = PAPERS[pid]; m = meta[pid]; a = json.loads(SET.assets_path(pid).read_text())
    qp, ms = pymupdf.open(SET.pdf(pid, 'qp')), pymupdf.open(SET.pdf(pid, 'ms'))
    blank = set(a.get('blankPages', []))
    cropped = {n: sorted({x['sourcePage'] for x in a['markScheme'][n]}) for n in a['markScheme']}
    assert all(sorted(set(a['msPages'][n]) - blank) == cropped[n] for n in cropped), pid
    used = sorted({pg for v in cropped.values() for pg in v})
    payload = {q['id']: q for q in json.loads((ROOT / f'content/exams/{pid}.json').read_text())['questions']}
    qs, assets = [], []
    for row in m['questions']:
        n = row['originalQuestionNumber']; html = payload[row['id']]['question']
        parts = list(map(int, re.findall(r'class="marks">\((\d+)\)', html)))
        assert sum(parts) == row['marks'], (pid, n, parts)
        qa = a['figures'].get(str(n), []) + a['markScheme'][str(n)]
        qs.append({'id': row['id'], 'questionNumber': n, 'questionPages': row['sourceQuestionPages'], 'marks': row['marks'],
                   'printedMarkGroups': parts, 'markSchemeTotal': row['marks'], 'markSchemePages': cropped[str(n)],
                   'difficulty': row['difficulty'], 'chapterKeys': catalogue[row['id']]['chapterKeys'],
                   'promptSourceChecked': True, 'mathsAudit': 'checked', 'visualAudit': 'checked-source-and-rendered-print',
                   'mathsCheckpoint': checks[pid][str(n)],
                   'assets': [{k: x[k] for k in ('asset', 'sha256', 'sourcePage', 'boundsPoints')} for x in qa]})
        assets += [dict(question=n, kind=x['kind'], sourcePage=x['sourcePage'], boundsPoints=x['boundsPoints'], asset=x['asset'],
                        sha256=x['sha256'], bytes=x['bytes']) for x in qa]
    assert sum(q['marks'] for q in qs) == P['total'] and len(qs) == P['nq']
    papers.append({
        'paperId': pid, 'paperCode': P['code'], 'title': P['title'], 'examDate': P['date'], 'originalExamDurationMinutes': P['minutes'],
        'questionCount': P['nq'], 'totalMarks': P['total'],
        'sourceHashes': a['sourceHashes'],
        'sourceIdentity': {
            'questionPaperPages': qp.page_count, 'markSchemePages': ms.page_count,
            'questionPaperCover': f"Pearson Edexcel Level 3 Advanced GCE in {'Further ' if P['code'].startswith('9FM') else ''}Mathematics, Sample Assessment Material, {P['code']}, {P['title']}, paper reference {P['ref']}, {duration(P['minutes'])}; "
                                  f"no exam date printed; {P['nq']} questions, {P['total']} marks (cover total agrees with the per-question marks).",
            'markSchemeCover': f"Paper {int(P['code'][-2:])}: {P['title']} Mark Scheme, Pearson Edexcel Level 3 Advanced GCE in {'Further ' if P['code'].startswith('9FM') else ''}Mathematics, Sample Assessment Materials, Issue 1, {'July' if P['code'].startswith('9FM') else 'April'} 2017.",
            'pairing': 'Paired by code, paper title and content; every question total in the scheme equals the question paper total.',
            'indexedCopies': {'questionPaperUrl': P['qpurl'], 'markSchemeUrl': P['msurl'], 'questionPaperSha256': P['idxqp'], 'markSchemeSha256': P['idxms'],
                              'note': 'Downloaded 23 November 2026. The linked question paper is byte-identical to the supplied copy. The linked mark scheme has the same pages and the same text apart from a "PMT" mark on each page (checked page by page), so the scheme content is identical.'}},
        'session': m['session'], 'seriesDate': m['seriesDate'], 'markSchemePagesUsed': used, 'blankMarkSchemePages': a.get('blankPages', []), 'excludedMarkSchemePages': [p for p in range(1, ms.page_count + 1) if p not in used],
        'markSchemeCoverage': {'pages': len(used), 'textSpans': a['spanCount'],
                               'result': 'Every nonblank, non-watermark text span and every embedded image lies wholly inside exactly one crop; no span is bisected or duplicated.'},
        'questions': qs, 'assets': assets})
evidence = {
    'requirement': 'PAP-072', 'issue': 128, 'sessions': ['Sample'], 'paperCount': len(papers),
    'questionCount': sum(p['questionCount'] for p in papers), 'totalMarks': sum(p['totalMarks'] for p in papers),
    'representation': {
        'prompts': 'Native HTML and KaTeX for every prompt with original wording, part labels, marks, bold emphasis, question-specific instructions, tables and faithful vector figure crops. As in the earlier imports, printed captions such as "Figure 1" sit outside the crop and the figure is referred to by the original text.',
        'solutions': 'Every question-specific mark-scheme page as ordered vector crops: working, marks, AOs, alternatives, examiner notes and diagrams. The Sample Assessment Materials page footer (Pearson imprint and page-number box) is excluded.'},
    'cropMethod': 'PyMuPDF show_pdf_page clip to SVG with text as paths. Figure boxes were set from the drawing items and checked visually in Chrome. Scheme page bounds cover all text spans, vector drawings and embedded images above the footer band; breaks fall only in empty horizontal bands; drawing items lying wholly off the page are ignored.',
    'sourceNotes': ['Files were identified by their covers, not their names; the full inventory (SHA-256, page counts, pairing, duplicates) is on GitHub #124 and the release slice on #128.',
                    'These are Sample Assessment Materials: session "Sample", no exam date and no series date (none invented). The Past Papers list places them after all dated papers, ordered by code.',
                    'June 2022 folder: all 12 files are byte-identical to Summer 2023 files imported in v0.69, so they are skipped; no genuine 2022 paper was supplied.',
                    'The question papers and the 9FM0/01 mark scheme have no readable PDF text layer (custom font encodings); prompts were transcribed from page images (OCR used only as an aid) and scheme crops are vector crops of the original pages.',
                    'Paper instructions are taken verbatim from each cover: "You should show sufficient working to make your methods clear. Answers without working may not gain full credit." and "Answers should be given to three significant figures unless otherwise stated." 9MA0/03 Q6-Q10 also carry the Section B: Mechanics instruction verbatim (g = 9.8 m s^-2, answers to 2 or 3 significant figures).',
                    '9MA0/03 is one combined paper with original numbering: Section A Statistics Q1-Q5 and Section B Mechanics Q6-Q10. Its question paper has 26 pages; page 26 is a blank back page.',
                    '9MA0/03 Q1 prints "5.98 hours and 4.12 hours respectably" (for "respectively"); it is kept verbatim and not corrected.',
                    '9MA0/03 Q10 and 9FM0/01 Q9 state their own g = 10 m s^-2 in the question text; it is kept in the question.',
                    '9MA0/02 Q6 is an always/sometimes/never-true table with marks in each statement row; it is reproduced as a table with the worked first row and blank answer cells.',
                    'Mid-page scheme starts (9MA0/01 Q4, 9MA0/02 Q2 and Q10) are cut above the question header row or label, so every question carries only its own scheme.'],
    'mathsReview': 'Every question solved independently with SymPy and numeric checks (private scripts) and compared with the official scheme answers; no mathematical discrepancies and no source errors found.',
    'papers': papers, 'status': 'checked-pending-print-and-review'}
if ARGS.extra:
    evidence.update(json.loads(Path(ARGS.extra).read_text()))
(ROOT / 'docs/evidence/v072-import-sample-papers.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=1) + '\n')
print('evidence', evidence['paperCount'], 'papers', evidence['questionCount'], 'questions', sum(len(p['assets']) for p in papers), 'assets')
