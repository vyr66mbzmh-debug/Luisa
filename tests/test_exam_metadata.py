"""Source contracts: retain question identity, verified metadata and complete printable joins."""
import collections
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text())


class PracticeClassification(unittest.TestCase):
    def test_complete_unique_mapping_without_source_changes(self):
        mapping = read('content/practice-classification.json')
        rows = mapping['questions']
        self.assertEqual(mapping['version'], 1)
        self.assertEqual(len(rows), 2475)
        by_id = {q['id']: q for q in rows}
        self.assertEqual(len(by_id), len(rows))
        originals = [q for p in (ROOT / 'content/practice').glob('*/chapter-*.json')
                     for q in json.loads(p.read_text())['questions']]
        retired = set(read('practice-catalogue.json')['migrations'])
        self.assertEqual(set(by_id) - retired, {q['id'] for q in originals})
        for q in originals:
            mapped = by_id[q['id']]
            tier = q['questionLabel'].lower()
            if tier in ('bronze', 'silver', 'gold'):
                self.assertEqual(mapped['bank'], 'exam')
                self.assertEqual(mapped['examType'], tier)
                self.assertEqual(mapped['difficulty'],
                                 {'bronze': 'easy', 'silver': 'medium', 'gold': 'difficult'}[tier])
            elif q['subchapterTitle'] == 'Selected exam question bank questions':
                self.assertEqual(mapped['bank'], 'exam')
                self.assertEqual(mapped['examType'], 'exam-style')
                self.assertIsNone(mapped['difficulty'])
            else:
                self.assertEqual(mapped['bank'], 'practice')
                self.assertIsNone(mapped['examType'])
                self.assertIsNone(mapped['difficulty'])
        self.assertEqual(collections.Counter(q['bank'] for q in rows),
                         {'practice': 1921, 'exam': 554})
        for chapter in read('docs/evidence/v059-practice-classification.json')['chapters']:
            expected_hash = chapter['sha256']
            if chapter['path'] == 'content/practice/pure-year-1/chapter-12.json':
                # v0.79 retired two first-principles copies in favour of their official sources.
                expected_hash = 'c4b51ba6c7193777b68639614db937536981edecb9ef23753b65f40511e9f9ca'
            self.assertEqual(hashlib.sha256((ROOT / chapter['path']).read_bytes()).hexdigest(), expected_hash)


class PilotMetadata(unittest.TestCase):
    def test_source_numbers_marks_difficulty_and_syllabus_joins(self):
        data = read('content/exams/pilot-metadata.json')
        lib = json.loads((ROOT / 'data.js').read_text().removeprefix('window.FMQ_LIBRARY=').rstrip(';\n'))
        valid = {(c['id'], b['id'], t['id'], s['id']) for c in lib['courses']
                 for b in c['books'] for t in b['topics'] for s in t['skills']}
        expected = {
            'edexcel-9ma0-01-2025-june': ([4,5,5,5,3,7,7,5,9,6,8,8,5,7,9,7], (5,6,5)),
            'edexcel-9ma0-02-2025-june': ([3,4,2,5,7,6,4,9,8,9,11,8,3,8,13], (5,5,5)),
            'edexcel-9ma0-32-2025-june': ([4,10,8,9,8,11], (2,2,2)),
            'edexcel-9ma0-31-2025-june': ([9,5,6,9,10,11], (2,2,2)),
            'edexcel-9fm0-01-2025-june': ([6,5,5,8,5,5,8,12,9,12], (3,4,3)),
            'edexcel-9fm0-02-2025-june': ([6,8,12,10,4,8,12,8,7], (3,3,3)),
            'edexcel-9ma0-01-2024-june': ([3,4,6,3,6,6,8,11,6,9,4,11,8,9,6], (5,5,5)),
            'edexcel-9ma0-02-2024-june': ([5,5,4,5,3,7,5,7,7,6,5,12,9,8,12], (5,5,5)),
            'edexcel-9ma0-32-2024-june': ([3,8,7,11,12,9], (2,2,2)),
            'edexcel-9ma0-31-2024-june': ([11,6,6,6,10,11], (2,2,2)),
            'edexcel-9fm0-01-2024-june': ([9,8,8,10,9,6,10,15], (2,4,2)),
            'edexcel-9fm0-02-2024-june': ([7,8,5,6,9,14,9,7,10], (3,3,3)),
            'edexcel-9ma0-01-2023-june': ([4,6,3,5,6,6,8,10,7,9,7,5,7,4,13], (5,5,5)),
            'edexcel-9ma0-02-2023-june': ([4,6,5,4,5,6,7,6,7,7,10,10,13,7,3], (5,5,5)),
            'edexcel-9ma0-32-2023-june': ([3,4,9,10,11,13], (2,2,2)),
            'edexcel-9ma0-31-2023-june': ([6,9,7,6,8,14], (2,2,2)),
            'edexcel-9fm0-01-2023-june': ([5,6,10,5,12,12,12,13], (2,4,2)),
            'edexcel-9fm0-02-2023-june': ([4,6,10,7,9,6,8,11,14], (3,3,3)),
            'edexcel-9fm0-01-2021-november': ([6,7,6,9,7,12,8,9,11], (3,3,3)),
            'edexcel-9fm0-02-2021-november': ([5,5,6,9,8,14,9,11,8], (3,3,3)),
            'edexcel-9ma0-01-2021-october': ([3,4,6,9,6,5,9,9,11,8,8,9,3,4,6], (5,5,5)),
            'edexcel-9ma0-02-2021-october': ([4,5,3,3,7,5,9,9,3,6,10,7,6,12,11], (5,5,5)),
            'edexcel-9ma0-32-2021-october': ([4,12,10,10,14], (1,3,1)),
            'edexcel-9ma0-31-2021-october': ([7,6,8,11,11,7], (2,2,2)),
            'edexcel-9ma0-01-2020-october': ([5,3,4,5,6,7,5,2,9,10,8,8,7,10,7,4], (5,6,5)),
            'edexcel-9ma0-02-2020-october': ([5,3,5,3,4,7,10,6,6,8,7,11,6,7,8,4], (5,6,5)),
            'edexcel-9ma0-32-2020-october': ([9,8,12,10,11], (1,3,1)),
            'edexcel-9ma0-31-2020-october': ([8,7,10,10,15], (1,3,1)),
            'edexcel-9fm0-01-2020-october': ([10,7,9,9,17,12,11], (2,3,2)),
            'edexcel-9fm0-02-2020-october': ([7,9,14,10,10,14,11], (2,3,2)),
            'edexcel-9ma0-01-2019-june': ([3,5,5,6,10,8,7,10,5,6,7,10,11,7], (4,6,4)),
            'edexcel-9ma0-02-2019-june': ([3,4,3,6,3,10,7,6,9,6,11,7,10,15], (4,6,4)),
            'edexcel-9ma0-32-2019-june': ([6,8,12,11,13], (1,3,1)),
            'edexcel-9ma0-31-2019-june': ([8,11,9,9,13], (1,3,1)),
            'edexcel-9fm0-01-2019-june': ([9,7,10,5,13,6,7,18], (2,4,2)),
            'edexcel-9fm0-02-2019-june': ([10,8,6,8,12,9,11,11], (2,4,2)),
            'edexcel-9ma0-01-2018-june': ([3,7,4,4,5,10,7,5,10,8,10,10,7,10], (4,6,4)),
            'edexcel-9ma0-02-2018-june': ([6,5,5,7,6,6,9,7,5,8,7,9,10,10], (4,6,4)),
            'edexcel-9ma0-03-2018-june': ([5,7,11,13,14,6,8,8,13,15], (3,4,3)),
            # PAP-072: Sample Assessment Materials (no date) follow all dated papers, ordered by code.
            'edexcel-9fm0-01-sample': ([5,6,9,9,10,9,8,7,12], (3,3,3)),
            'edexcel-9fm0-02-sample': ([8,8,12,7,10,13,17], (2,3,2)),
            'edexcel-9ma0-01-sample': ([7,5,4,4,3,7,5,6,5,5,9,9,13,10,8], (5,5,5)),
            'edexcel-9ma0-02-sample': ([3,3,4,5,4,6,5,7,5,4,6,8,9,9,10,12], (5,6,5)),
            'edexcel-9ma0-03-sample': ([13,6,12,10,9,6,8,10,13,13], (3,4,3)),
        }
        self.assertTrue(data['printable'])
        legacy = [p for p in data['papers'] if p['qualification'] != 'AS']
        self.assertEqual([p['id'] for p in legacy], list(expected))
        as_marks = read('scripts/import/sets/v079-as/marks.json')
        sources = read('scripts/import/sets/v079-as/sources.json')
        self.assertEqual({p['id'] for p in data['papers'] if p['qualification'] == 'AS'}, set(as_marks))
        self.assertEqual((len(as_marks), sum(map(len, as_marks.values())), sum(map(sum, as_marks.values()))), (37, 322, 2320))
        for pid, marks in as_marks.items():
            third = len(marks) // 3
            expected[pid] = marks, (third, len(marks)-2*third, third)
        all_rows = []
        for paper in data['papers']:
            rows = paper['questions']; marks, bands = expected[paper['id']]
            all_rows.extend(rows)
            self.assertEqual([q['originalQuestionNumber'] for q in rows], list(range(1, len(rows)+1)))
            self.assertEqual([q['marks'] for q in rows], marks)
            self.assertEqual(paper['questionCount'], len(rows))
            self.assertEqual(paper['totalMarks'], sum(marks))
            self.assertEqual([q['difficulty'] for q in rows],
                             ['easy']*bands[0] + ['medium']*bands[1] + ['difficult']*bands[2])
            if paper['qualification'] == 'AS':
                for key, source_key in [('questionPaperSha256', 'qpsha'), ('markSchemeSha256', 'mssha')]:
                    self.assertEqual(paper['source'][key], sources[paper['id']][source_key])
                    self.assertRegex(paper['source'][key], '^[0-9a-f]{64}$')
            for field in (() if paper['qualification'] == 'AS' else ('questionPaperUrl', 'markSchemeUrl')):
                self.assertTrue(paper['source'][field].startswith('https://pmt.physicsandmathstutor.com/'))
            for q in rows:
                self.assertTrue(q['printable'])
                self.assertEqual(q['contentStatus'], 'checked')
                self.assertEqual(q['id'], 'exam/'+paper['id']+'/q'+str(q['originalQuestionNumber']))
                self.assertEqual(q['questionNumber'], q['originalQuestionNumber'])
                self.assertTrue(q['skillMappings'])
                for s in q['skillMappings']:
                    self.assertIn(tuple(s[k] for k in ('courseId','bookId','topicId','skillId')), valid)
                self.assertTrue(set(q).isdisjoint({'question','questionHtml','steps','solution','hints','assets'}))
        self.assertEqual(len(all_rows), data['questionCount'])
        self.assertEqual(len({q['id'] for q in all_rows}), 766)
        self.assertEqual(sum(q['marks'] for q in all_rows), data['totalMarks'])
        self.assertEqual(data['totalMarks'], 5770)


    def test_printable_payloads_and_assets_are_complete(self):
        import re
        catalogue = read('exam-catalogue.json')['questions']
        metadata = {q['id']: q for p in read('content/exams/pilot-metadata.json')['papers'] for q in p['questions']}
        self.assertEqual({q['id'] for q in catalogue}, set(metadata))
        self.assertEqual(len(catalogue), 766)
        self.assertEqual(sum(q['marks'] for q in catalogue), 5770)
        for row in catalogue:
            self.assertEqual(row['status'], 'checked')
            for key in ('marks','difficulty','sourceLabel','skillMappings'):
                self.assertEqual(row[key], metadata[row['id']][key])
            payload = read(row['dataPath'])['questions']
            matches = [q for q in payload if q['id'] == row['id']]
            self.assertEqual(len(matches), 1)
            q = matches[0]
            self.assertTrue(q['question'])
            self.assertTrue(q['steps'])
            self.assertIn('You should show sufficient working to make your methods clear.', q['contextHtml'])
            for src in re.findall(r'src="([^"]+)"', q['question'] + ''.join(q['steps'])):
                self.assertTrue(src.startswith('resources/exams/'))
                self.assertTrue((ROOT / src).is_file(), src)
            self.assertNotIn('-ms-', q['question'])

    def test_pure_mathematics_2_source_identity_and_complete_schemes(self):
        import re
        paper = next(p for p in read('content/exams/pilot-metadata.json')['papers'] if p['id'] == 'edexcel-9ma0-02-2025-june')
        self.assertEqual((paper['id'], paper['title'], paper['examDate'], paper['questionCount'], paper['totalMarks']),
                         ('edexcel-9ma0-02-2025-june', 'Pure Mathematics 2', '2025-06-12', 15, 100))
        self.assertEqual(paper['source']['questionPaperSha256'], '3a96003a088b89a198288e8b7d1d836f6a4cef190e0768047bf856730840fd6e')
        self.assertEqual(paper['source']['markSchemeSha256'], '000beb634c58b2bc03c724c98a1f18e65fa635dfb0214eacbd875bd3b4be2f58')
        evidence = read('docs/evidence/v062-import-pure2.json')
        payload = {q['id']: q for q in read('content/exams/edexcel-9ma0-02-2025-june.json')['questions']}
        self.assertEqual(list(payload), [f'exam/edexcel-9ma0-02-2025-june/q{n}' for n in range(1, 16)])
        scheme_pages = []
        for row, record in zip(paper['questions'], evidence['questions']):
            q = payload[row['id']]
            self.assertEqual(record['id'], row['id'])
            self.assertEqual(sum(map(int, re.findall(r'class="marks">\((\d+)\)', q['question']))), row['marks'])
            sources = re.findall(r'src="([^"]+-ms-p(\d+)-\d+\.svg)"', ''.join(q['steps']))
            self.assertEqual(sorted({int(page) for _, page in sources}), record['markSchemePages'])
            self.assertTrue(all(f'/q{row["originalQuestionNumber"]:02d}-ms-' in src for src, _ in sources))
            scheme_pages += record['markSchemePages']
            for asset in record['assets']:
                self.assertEqual(hashlib.sha256((ROOT / asset['asset']).read_bytes()).hexdigest(), asset['sha256'])
        self.assertEqual(scheme_pages, list(range(5, 42)))

    def test_june_2024_source_identity_and_complete_schemes(self):
        self.assert_session_evidence('docs/evidence/v064-import-june2024.json', 'June 2024', strict_order=True)

    def test_june_2023_source_identity_and_complete_schemes(self):
        evidence = self.assert_session_evidence('docs/evidence/v069-import-june2023.json', 'June 2023')
        hashes = {p['paperId']: p['sourceHashes']['questionPaperSha256'][:12] for p in evidence['papers']}
        self.assertEqual(hashes, {'edexcel-9ma0-01-2023-june': '5dfb0d628e52', 'edexcel-9ma0-02-2023-june': '5af2f862c6a0',
                                  'edexcel-9ma0-31-2023-june': '4b5e3dc04ba1', 'edexcel-9ma0-32-2023-june': 'c8edd3050af7',
                                  'edexcel-9fm0-01-2023-june': 'a9c5b3117e26', 'edexcel-9fm0-02-2023-june': '9d9d21ecb6c5'})
        core2 = next(p for p in evidence['papers'] if p['paperId'] == 'edexcel-9fm0-02-2023-june')
        self.assertEqual(core2['questions'][4]['printedMarkGroups'], [2, 2, 1, 4])
        self.assertTrue(any('(11 marks)' in note and 'misprint' in note for note in evidence['sourceNotes']))
        stats = next(p for p in evidence['papers'] if p['paperId'] == 'edexcel-9ma0-31-2023-june')
        self.assertEqual(stats['questions'][4]['markSchemePages'], [11, 13])
        self.assertTrue(all('Agrees with scheme.' in q['mathsCheckpoint'] for p in evidence['papers'] for q in p['questions']))

    def test_june_2018_and_2019_source_identity_and_complete_schemes(self):
        ids = ['edexcel-9ma0-01-2019-june', 'edexcel-9ma0-02-2019-june', 'edexcel-9ma0-32-2019-june', 'edexcel-9ma0-31-2019-june',
               'edexcel-9fm0-01-2019-june', 'edexcel-9fm0-02-2019-june', 'edexcel-9ma0-01-2018-june', 'edexcel-9ma0-02-2018-june',
               'edexcel-9ma0-03-2018-june']
        evidence = self.assert_session_evidence('docs/evidence/v070-import-june2018-2019.json', ['June 2019', 'June 2018'],
                                                strict_order=True, shared_boundary_pages=True, counts=(9, 92, 750),
                                                codes=('9MA0/01', '9MA0/02', '9MA0/32', '9MA0/31', '9FM0/01', '9FM0/02', '9MA0/01', '9MA0/02', '9MA0/03'))
        self.assertEqual([p['paperId'] for p in evidence['papers']], ids)
        self.assertEqual([p['session'] for p in evidence['papers']], ['June 2019'] * 6 + ['June 2018'] * 3)
        hashes = {p['paperId']: (p['sourceHashes']['questionPaperSha256'][:12], p['sourceHashes']['markSchemeSha256'][:12]) for p in evidence['papers']}
        self.assertEqual(hashes, {
            'edexcel-9ma0-01-2019-june': ('89d654b995cc', '2434be9cf4c0'),
            'edexcel-9ma0-02-2019-june': ('d094426b762d', '570335fc41ba'),
            'edexcel-9ma0-32-2019-june': ('d73f786d6451', '1cea1a52fc62'),
            'edexcel-9ma0-31-2019-june': ('b16d31919b74', 'a371cf9f3660'),
            'edexcel-9fm0-01-2019-june': ('f158309912ea', 'c6f793847b4d'),
            'edexcel-9fm0-02-2019-june': ('09b4c0fbeb7b', 'b20aa6b99f8e'),
            'edexcel-9ma0-01-2018-june': ('4af4686ecb66', 'f9f093e7fa09'),
            'edexcel-9ma0-02-2018-june': ('bcfbd7d2ba86', '4f0d162bae39'),
            'edexcel-9ma0-03-2018-june': ('a37e940340d4', '2ccf29e3da8c')})
        pages = {p['paperId']: (p['sourceIdentity']['questionPaperPages'], p['sourceIdentity']['markSchemePages']) for p in evidence['papers']}
        self.assertEqual(pages, dict(zip(ids, [(44, 31), (48, 40), (20, 16), (20, 10), (32, 27), (28, 24), (44, 27), (44, 41), (36, 21)])))
        blanks = {p['paperId']: p['blankMarkSchemePages'] for p in evidence['papers'] if p['blankMarkSchemePages']}
        self.assertEqual(blanks, {'edexcel-9ma0-02-2018-june': [10, 22, 32], 'edexcel-9ma0-03-2018-june': [12]})
        meta = {p['id']: p for p in read('content/exams/pilot-metadata.json')['papers']}
        combined = meta['edexcel-9ma0-03-2018-june']
        self.assertEqual((combined['paperCode'], combined['title'], combined['questionCount'], combined['totalMarks']),
                         ('9MA0/03', 'Statistics and Mechanics', 10, 100))
        books = [{s['bookId'] for s in q['skillMappings']} for q in combined['questions']]
        self.assertTrue(all(any('statistics' in b for b in bs) for bs in books[:5]))
        self.assertTrue(all(any('mechanics' in b for b in bs) for bs in books[5:]))
        payload = read('content/exams/edexcel-9ma0-03-2018-june.json')['questions']
        self.assertTrue(all('take' in q['contextHtml'] and '9.8' in q['contextHtml'] for q in payload[5:]))
        self.assertTrue(all('9.8' not in q['contextHtml'] for q in payload[:5]))
        self.assertTrue(all('Agrees with scheme.' in q['mathsCheckpoint'] for p in evidence['papers'] for q in p['questions']))

    def test_october_2020_october_2021_and_november_2021_source_identity_and_complete_schemes(self):
        ids = ['edexcel-9fm0-01-2021-november', 'edexcel-9fm0-02-2021-november', 'edexcel-9ma0-01-2021-october', 'edexcel-9ma0-02-2021-october',
               'edexcel-9ma0-32-2021-october', 'edexcel-9ma0-31-2021-october', 'edexcel-9ma0-01-2020-october', 'edexcel-9ma0-02-2020-october',
               'edexcel-9ma0-32-2020-october', 'edexcel-9ma0-31-2020-october', 'edexcel-9fm0-01-2020-october', 'edexcel-9fm0-02-2020-october']
        evidence = self.assert_session_evidence('docs/evidence/v071-import-oct2020-oct2021-nov2021.json', ['November 2021', 'October 2021', 'October 2020'],
                                                strict_order=True, shared_boundary_pages=True, counts=(12, 115, 900),
                                                codes=('9FM0/01', '9FM0/02', '9MA0/01', '9MA0/02', '9MA0/32', '9MA0/31',
                                                       '9MA0/01', '9MA0/02', '9MA0/32', '9MA0/31', '9FM0/01', '9FM0/02'))
        self.assertEqual((evidence['requirement'], evidence['issue']), ('PAP-071', 126))
        self.assertEqual([p['paperId'] for p in evidence['papers']], ids)
        self.assertEqual([p['session'] for p in evidence['papers']], ['November 2021'] * 2 + ['October 2021'] * 4 + ['October 2020'] * 6)
        self.assertEqual([p['examDate'] for p in evidence['papers']],
                         [None, None, '2021-10-06', '2021-10-13', '2021-10-18', '2021-10-18', '2020-10-07', '2020-10-14', '2020-10-19', '2020-10-19', None, None])
        hashes = {p['paperId']: (p['sourceHashes']['questionPaperSha256'][:12], p['sourceHashes']['markSchemeSha256'][:12]) for p in evidence['papers']}
        self.assertEqual(hashes, {
            'edexcel-9fm0-01-2021-november': ('5181985f57b0', 'c5205673ae27'),
            'edexcel-9fm0-02-2021-november': ('647a11a9c3dd', '47deaa607e62'),
            'edexcel-9ma0-01-2021-october': ('c224c59b8b60', 'd1cc4be8f2bd'),
            'edexcel-9ma0-02-2021-october': ('5456d81cfe94', 'de806a7b524f'),
            'edexcel-9ma0-32-2021-october': ('1b8f4a64c837', 'b3022e7fc2a1'),
            'edexcel-9ma0-31-2021-october': ('475acbd43a85', '390d014d74a7'),
            'edexcel-9ma0-01-2020-october': ('e24c394b8917', 'e480deba960f'),
            'edexcel-9ma0-02-2020-october': ('28c3089d47d2', '58cc5ec8242c'),
            'edexcel-9ma0-32-2020-october': ('f2aee6b076e5', '93c9e0ba4797'),
            'edexcel-9ma0-31-2020-october': ('7e3d73972f48', 'a7ebc141d7ab'),
            'edexcel-9fm0-01-2020-october': ('82cb92edc5c1', 'a22236727a84'),
            'edexcel-9fm0-02-2020-october': ('9919535f5ee7', '92e1f107d6c3')})
        pages = {p['paperId']: (p['sourceIdentity']['questionPaperPages'], p['sourceIdentity']['markSchemePages']) for p in evidence['papers']}
        self.assertEqual(pages, dict(zip(ids, [(36, 18), (32, 23), (52, 26), (48, 27), (20, 14), (20, 11), (52, 29), (52, 28), (20, 14), (20, 10), (28, 20), (28, 17)])))
        covers = {p['paperId']: p['sourceIdentity'] for p in evidence['papers']}
        self.assertIn('printed date Monday 11 May 2020', covers['edexcel-9fm0-01-2020-october']['questionPaperCover'])
        self.assertIn('printed date Thursday 14 May 2020', covers['edexcel-9fm0-02-2020-october']['questionPaperCover'])
        self.assertIn('no exam date printed (series November 2021)', covers['edexcel-9fm0-01-2021-november']['questionPaperCover'])
        self.assertIn('November 2021', covers['edexcel-9ma0-01-2021-october']['markSchemeCover'])
        self.assertIn('Autumn 2020', covers['edexcel-9ma0-02-2020-october']['markSchemeCover'])
        meta = {p['id']: p for p in read('content/exams/pilot-metadata.json')['papers']}
        self.assertEqual({k: (meta[k]['examDate'], meta[k]['seriesDate']) for k in ids if meta[k]['examDate'] is None},
                         {'edexcel-9fm0-01-2021-november': (None, '2021-11'), 'edexcel-9fm0-02-2021-november': (None, '2021-11'),
                          'edexcel-9fm0-01-2020-october': (None, '2020-10'), 'edexcel-9fm0-02-2020-october': (None, '2020-10')})
        for pid in ('edexcel-9ma0-32-2020-october', 'edexcel-9ma0-32-2021-october'):
            payload = read(f'content/exams/{pid}.json')['questions']
            self.assertTrue(all('9.8' in q['contextHtml'] and 'Inexact' not in q['contextHtml'] for q in payload))
        mech = read('content/exams/edexcel-9ma0-32-2021-october.json')['questions']
        self.assertIn('The acceleration due to gravity is modelled as having magnitude', mech[3]['question'])
        for pid in ids:
            payload = read(f'content/exams/{pid}.json')['questions']
            if '-32-' not in pid:
                self.assertTrue(all('Inexact answers should be given to three significant figures' in q['contextHtml'] for q in payload), pid)
        self.assertTrue(all('Agrees with scheme.' in q['mathsCheckpoint'] for p in evidence['papers'] for q in p['questions']))

    def test_sample_assessment_materials_source_identity_and_complete_schemes(self):
        ids = ['edexcel-9fm0-01-sample', 'edexcel-9fm0-02-sample', 'edexcel-9ma0-01-sample', 'edexcel-9ma0-02-sample', 'edexcel-9ma0-03-sample']
        evidence = self.assert_session_evidence('docs/evidence/v072-import-sample-papers.json', 'Sample', strict_order=True,
                                                shared_boundary_pages=True, counts=(5, 57, 450),
                                                codes=('9FM0/01', '9FM0/02', '9MA0/01', '9MA0/02', '9MA0/03'))
        self.assertEqual((evidence['requirement'], evidence['issue']), ('PAP-072', 128))
        self.assertEqual([p['paperId'] for p in evidence['papers']], ids)
        self.assertEqual([p['session'] for p in evidence['papers']], ['Sample'] * 5)
        hashes = {p['paperId']: (p['sourceHashes']['questionPaperSha256'][:12], p['sourceHashes']['markSchemeSha256'][:12]) for p in evidence['papers']}
        self.assertEqual(hashes, {
            'edexcel-9fm0-01-sample': ('c52ca71952d7', '75adbba38a00'),
            'edexcel-9fm0-02-sample': ('912b1f5d5f93', '8737ed77a9a8'),
            'edexcel-9ma0-01-sample': ('dfb3d5e84c96', '0aea6a31199c'),
            'edexcel-9ma0-02-sample': ('2bc25b62b1b8', 'fc838ce639b8'),
            'edexcel-9ma0-03-sample': ('b22c0b36290c', '702bd8368771')})
        pages = {p['paperId']: (p['sourceIdentity']['questionPaperPages'], p['sourceIdentity']['markSchemePages']) for p in evidence['papers']}
        self.assertEqual(pages, dict(zip(ids, [(25, 12), (17, 11), (32, 18), (26, 16), (26, 15)])))
        covers = {p['paperId']: p['sourceIdentity'] for p in evidence['papers']}
        self.assertTrue(all('Sample Assessment Material' in c['questionPaperCover'] and 'no exam date printed' in c['questionPaperCover'] for c in covers.values()))
        self.assertIn('paper reference S54261A', covers['edexcel-9ma0-03-sample']['questionPaperCover'])
        self.assertTrue(any('June 2022' in note and 'byte-identical' in note for note in evidence['sourceNotes']))
        self.assertTrue(any('respectably' in note for note in evidence['sourceNotes']))
        meta = {p['id']: p for p in read('content/exams/pilot-metadata.json')['papers']}
        self.assertEqual({k: (meta[k]['session'], meta[k]['examDate'], meta[k]['seriesDate']) for k in ids}, {k: ('Sample', None, None) for k in ids})
        self.assertEqual([k for k in meta if meta[k]["qualification"] != "AS"][-5:], ids)
        for pid in ids:
            self.assertTrue(meta[pid]['source']['questionPaperUrl'].endswith('/QP/Sample%20QP.pdf'))
            self.assertEqual(meta[pid]['source']['questionPaperSha256'], meta[pid]['source']['indexedQuestionPaperSha256'])
            payload = read(f'content/exams/{pid}.json')['questions']
            self.assertTrue(all('Answers should be given to three significant figures unless otherwise stated.' in q['contextHtml'] for q in payload), pid)
        combined = meta['edexcel-9ma0-03-sample']
        self.assertEqual((combined['paperCode'], combined['title'], combined['questionCount'], combined['totalMarks']),
                         ('9MA0/03', 'Statistics and Mechanics', 10, 100))
        books = [{s['bookId'] for s in q['skillMappings']} for q in combined['questions']]
        self.assertTrue(all(any('statistics' in b for b in bs) for bs in books[:5]))
        self.assertTrue(all(any('mechanics' in b for b in bs) for bs in books[5:]))
        payload = read('content/exams/edexcel-9ma0-03-sample.json')['questions']
        self.assertTrue(all('Section B: Mechanics' in q['contextHtml'] and '9.8' in q['contextHtml'] for q in payload[5:]))
        self.assertTrue(all('9.8' not in q['contextHtml'] for q in payload[:5]))
        self.assertIn('respectably', payload[0]['question'])
        table = read('content/exams/edexcel-9ma0-02-sample.json')['questions'][5]['question']
        self.assertIn('Always True', table)
        self.assertEqual(table.count('class="marks">(2)'), 3)
        self.assertTrue(all('Agrees with scheme.' in q['mathsCheckpoint'] for p in evidence['papers'] for q in p['questions']))

    def assert_session_evidence(self, path, session, strict_order=False, shared_boundary_pages=False, counts=(6, 59, 450),
                                codes=('9MA0/01', '9MA0/02', '9MA0/31', '9MA0/32', '9FM0/01', '9FM0/02')):
        import re
        evidence = read(path)
        meta = {p['id']: p for p in read('content/exams/pilot-metadata.json')['papers']}
        self.assertEqual((evidence['paperCount'], evidence['questionCount'], evidence['totalMarks']), counts)
        self.assertEqual([p['paperCode'] for p in evidence['papers']], list(codes))
        for record in evidence['papers']:
            paper = meta[record['paperId']]
            self.assertEqual(paper['session'], record.get('session', session))
            self.assertIn(paper['session'], [session] if isinstance(session, str) else session)
            self.assertEqual((paper['paperCode'], paper['title'], paper['examDate'], paper['questionCount'], paper['totalMarks']),
                             (record['paperCode'], record['title'], record['examDate'], record['questionCount'], record['totalMarks']))
            for key in ('questionPaperSha256', 'markSchemeSha256'):
                self.assertRegex(paper['source'][key], '^[0-9a-f]{64}$')
                self.assertEqual(paper['source'][key], record['sourceHashes'][key])
            payload = {q['id']: q for q in read(f"content/exams/{record['paperId']}.json")['questions']}
            self.assertEqual(list(payload), [q['id'] for q in paper['questions']])
            scheme_pages = []
            for row, q_record in zip(paper['questions'], record['questions']):
                q = payload[row['id']]
                self.assertEqual(q_record['id'], row['id'])
                self.assertEqual(sum(map(int, re.findall(r'class="marks">\((\d+)\)', q['question']))), row['marks'])
                sources = re.findall(r'src="([^"]+-ms-p(\d+)-\d+\.svg)"', ''.join(q['steps']))
                self.assertEqual(sorted({int(page) for _, page in sources}), q_record['markSchemePages'])
                self.assertTrue(all(f'/q{row["originalQuestionNumber"]:02d}-ms-' in src for src, _ in sources))
                scheme_pages += q_record['markSchemePages']
                for asset in q_record['assets']:
                    self.assertEqual(hashlib.sha256((ROOT / asset['asset']).read_bytes()).hexdigest(), asset['sha256'])
            if shared_boundary_pages:
                # A question may start mid-page: only the last page of one question may be the first page of the next.
                self.assertEqual(sorted(set(scheme_pages)), record['markSchemePagesUsed'])
                groups = [q['markSchemePages'] for q in record['questions']]
                for before, after in zip(groups, groups[1:]):
                    self.assertLessEqual(before[-1], after[0])
                    self.assertTrue(set(before).isdisjoint(after) or set(before) & set(after) == {after[0]})
            else:
                self.assertEqual(sorted(scheme_pages), record['markSchemePagesUsed'])
                self.assertEqual(len(set(scheme_pages)), len(scheme_pages))
            self.assertTrue(set(record.get('blankMarkSchemePages', [])).isdisjoint(scheme_pages))
            if strict_order:
                self.assertEqual(sorted(scheme_pages), scheme_pages)
        return evidence


if __name__ == '__main__':
    unittest.main()
