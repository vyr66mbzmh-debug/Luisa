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
        self.assertEqual(set(by_id), {q['id'] for q in originals})
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
            self.assertEqual(hashlib.sha256((ROOT / chapter['path']).read_bytes()).hexdigest(),
                             chapter['sha256'])


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
            'edexcel-9ma0-01-2019-june': ([3,5,5,6,10,8,7,10,5,6,7,10,11,7], (4,6,4)),
            'edexcel-9ma0-02-2019-june': ([3,4,3,6,3,10,7,6,9,6,11,7,10,15], (4,6,4)),
            'edexcel-9ma0-32-2019-june': ([6,8,12,11,13], (1,3,1)),
            'edexcel-9ma0-31-2019-june': ([8,11,9,9,13], (1,3,1)),
            'edexcel-9fm0-01-2019-june': ([9,7,10,5,13,6,7,18], (2,4,2)),
            'edexcel-9fm0-02-2019-june': ([10,8,6,8,12,9,11,11], (2,4,2)),
            'edexcel-9ma0-01-2018-june': ([3,7,4,4,5,10,7,5,10,8,10,10,7,10], (4,6,4)),
            'edexcel-9ma0-02-2018-june': ([6,5,5,7,6,6,9,7,5,8,7,9,10,10], (4,6,4)),
            'edexcel-9ma0-03-2018-june': ([5,7,11,13,14,6,8,8,13,15], (3,4,3)),
        }
        self.assertTrue(data['printable'])
        self.assertEqual([p['id'] for p in data['papers']], list(expected))
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
            for field in ('questionPaperUrl', 'markSchemeUrl'):
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
        self.assertEqual(len({q['id'] for q in all_rows}), 272)
        self.assertEqual(sum(q['marks'] for q in all_rows), data['totalMarks'])
        self.assertEqual(data['totalMarks'], 2100)


    def test_printable_payloads_and_assets_are_complete(self):
        import re
        catalogue = read('exam-catalogue.json')['questions']
        metadata = {q['id']: q for p in read('content/exams/pilot-metadata.json')['papers'] for q in p['questions']}
        self.assertEqual({q['id'] for q in catalogue}, set(metadata))
        self.assertEqual(len(catalogue), 272)
        self.assertEqual(sum(q['marks'] for q in catalogue), 2100)
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
