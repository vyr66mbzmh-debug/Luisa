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
            '9MA0/01': ([4,5,5,5,3,7,7,5,9,6,8,8,5,7,9,7], (5,6,5)),
            '9MA0/02': ([3,4,2,5,7,6,4,9,8,9,11,8,3,8,13], (5,5,5)),
            '9MA0/32': ([4,10,8,9,8,11], (2,2,2)),
            '9MA0/31': ([9,5,6,9,10,11], (2,2,2)),
            '9FM0/01': ([6,5,5,8,5,5,8,12,9,12], (3,4,3)),
            '9FM0/02': ([6,8,12,10,4,8,12,8,7], (3,3,3)),
        }
        self.assertTrue(data['printable'])
        self.assertEqual({p['paperCode'] for p in data['papers']}, set(expected))
        all_rows = []
        for paper in data['papers']:
            rows = paper['questions']; marks, bands = expected[paper['paperCode']]
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
        self.assertEqual(len({q['id'] for q in all_rows}), 62)
        self.assertEqual(sum(q['marks'] for q in all_rows), data['totalMarks'])
        self.assertEqual(data['totalMarks'], 450)


    def test_printable_payloads_and_assets_are_complete(self):
        import re
        catalogue = read('exam-catalogue.json')['questions']
        metadata = {q['id']: q for p in read('content/exams/pilot-metadata.json')['papers'] for q in p['questions']}
        self.assertEqual({q['id'] for q in catalogue}, set(metadata))
        self.assertEqual(len(catalogue), 62)
        self.assertEqual(sum(q['marks'] for q in catalogue), 450)
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
        paper = next(p for p in read('content/exams/pilot-metadata.json')['papers'] if p['paperCode'] == '9MA0/02')
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


if __name__ == '__main__':
    unittest.main()
