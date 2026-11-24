"""PAP-075 / PAP-076: PMT Core Pure topic-sheet questions, checked chapter by chapter.

Expected counts and marks come from the source inventory taken before import (question count and the printed
"(Total for question = N marks)" lines of each PDF); the evidence file records the SHA-256 and page count of each PDF.
"""
import collections
import html
import json
import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = json.loads((ROOT / 'pmt-catalogue.json').read_text())['questions']

# sheetId -> (questions, total marks) from the inventory of the source PDFs.
EXPECTED = {
    'pure-core-1-ch1': (7, 52), 'pure-core-1-ch2': (11, 89), 'pure-core-1-ch3': (6, 56), 'pure-core-1-ch4': (6, 35),
    'pure-core-1-ch5': (5, 53), 'pure-core-1-ch6': (8, 65), 'pure-core-1-ch7': (10, 81), 'pure-core-1-ch8': (9, 84),
    'pure-core-1-ch9': (11, 110), 'pure-core-2-ch1': (11, 92), 'pure-core-2-ch2': (11, 87),
    'pure-core-2-ch3': (7, 49), 'pure-core-2-ch4': (4, 36), 'pure-core-2-ch5': (6, 59), 'pure-core-2-ch6': (9, 67),
    'pure-core-2-ch7': (3, 30), 'pure-core-2-ch8': (10, 138),
}
SOURCE_SLIPS = {'pmt/pure-core-1/ch2/q7', 'pmt/pure-core-1/ch6/q2', 'pmt/pure-core-1/ch6/q3', 'pmt/pure-core-1/ch6/q6',
                'pmt/pure-core-1/ch9/q10', 'pmt/pure-core-2/ch1/q10', 'pmt/pure-core-2/ch3/q6'}
LEAKS = re.compile(r'PMT|PhysicsAndMathsTutor|Physics\s*&?\s*Maths\s*Tutor|Mark Scheme|Total for question|\bEdexcel\b|9FM0', re.I)


def skill_library():
    text = (ROOT / 'data.js').read_text()
    lib = json.loads(text[text.index('{'):text.rindex('}') + 1])
    return {(b['id'], t['id'], k['id']) for c in lib['courses'] for b in c['books'] for t in b['topics'] for k in t['skills']}


def png_size(path):
    with open(path, 'rb') as f:
        head = f.read(24)
    assert head[:8] == b'\x89PNG\r\n\x1a\n', path
    return struct.unpack('>II', head[16:24])


def payloads():
    out = {}
    for row in CATALOGUE:
        if row['dataPath'] not in out:
            out[row['dataPath']] = {q['id']: q for q in json.loads((ROOT / row['dataPath']).read_text())['questions']}
    return out


class PmtChapters(unittest.TestCase):
    def setUp(self):
        self.rows = collections.defaultdict(list)
        for row in CATALOGUE:
            self.rows[row['sheetId']].append(row)
        self.payloads = payloads()

    def test_every_imported_chapter_is_complete_with_its_printed_marks(self):
        imported = set(self.rows)
        self.assertTrue(imported, 'no PMT chapters imported')
        self.assertLessEqual(imported, set(EXPECTED), 'a chapter without an inventory entry')
        for sheet in sorted(imported):
            with self.subTest(sheet=sheet):
                rows = self.rows[sheet]
                count, marks = EXPECTED[sheet]
                self.assertEqual([r['questionNumber'] for r in rows], list(range(1, count + 1)))
                self.assertEqual(sum(r['marks'] for r in rows), marks)

    def test_rows_carry_the_source_scheme_flag_difficulty_and_source(self):
        library = skill_library()
        for sheet, rows in sorted(self.rows.items()):
            for row in rows:
                with self.subTest(id=row['id']):
                    self.assertEqual(row['markScheme'], 'source')
                    self.assertEqual(row['board'], 'PMT')
                    self.assertEqual(row['status'], 'checked')
                    self.assertIn(row['difficulty'], ('easy', 'medium', 'difficult'))
                    self.assertTrue(row['difficultyReason'].strip() and '\n' not in row['difficultyReason'])
                    self.assertRegex(row['sourceLabel'], rf'^PMT Core Pure [12] Ch\.\d+ .+ Q{row["questionNumber"]}$')
                    self.assertRegex(row['sourceSha256'], r'^[0-9a-f]{64}$')
                    self.assertTrue(row['skillMappings'])
                    for s in row['skillMappings']:
                        self.assertIn((s['bookId'], s['topicId'], s['skillId']), library)
                    self.assertEqual(row['chapterKeys'][0], f'further-maths-a-level/{sheet.rsplit("-ch", 1)[0]}/{sheet.rsplit("-ch", 1)[1]}')
                    self.assertEqual(bool(row['sourceNote']), row['id'] in SOURCE_SLIPS)

    def test_each_question_has_its_own_source_scheme_crops_and_figures(self):
        for row in CATALOGUE:
            q = self.payloads[row['dataPath']][row['id']]
            with self.subTest(id=row['id']):
                self.assertEqual(q['sourceScheme']['kind'], 'source')
                self.assertEqual(q['sourceScheme']['page'], row['schemePages'])
                self.assertTrue(q['steps'])
                for step in q['steps']:
                    src = re.fullmatch(r'<figure class="exam-solution-source"[^>]*><img src="(resources/pmt/[a-z0-9-]+/q(\d+)-ms-(?:from-[a-z0-9-]+-)?p\d+-\d+\.png)"[^>]*alt="PMT mark scheme for [^"]+"[^>]*></figure>', step)
                    self.assertIsNotNone(src, step[:120])
                    self.assertEqual(int(src.group(2)), row['questionNumber'])
                    w, h = png_size(ROOT / src.group(1))
                    self.assertGreater(w, 400)
                    self.assertGreater(h, 20)
                    self.assertLessEqual(h, w * 1.01, 'a scheme crop must fit one printed page (split at blank rows)')
                for img in re.findall(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', q['question']):
                    self.assertTrue((ROOT / img[0]).is_file(), img[0])
                    self.assertGreater(len(img[1]), 20, 'figure needs a real description')

    def test_question_text_names_no_source(self):
        for row in CATALOGUE:
            q = self.payloads[row['dataPath']][row['id']]
            with self.subTest(id=row['id']):
                text = html.unescape(re.sub(r'<[^>]+>', ' ', q['question'] + (q.get('contextHtml') or '')))
                self.assertIsNone(LEAKS.search(text))
                self.assertFalse(q.get('contextHtml'))

    def test_printed_part_marks_add_up_to_the_question_total(self):
        for row in CATALOGUE:
            q = self.payloads[row['dataPath']][row['id']]
            parts = [int(n) for n in re.findall(r'<span class="marks">\((\d+)\)</span>', q['question'])]
            with self.subTest(id=row['id']):
                if parts:  # a few sheets print only the question total
                    self.assertEqual(sum(parts), row['marks'])

    def test_duplicates_are_marked_and_point_at_a_real_question(self):
        exam_ids = {r['id'] for r in json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']}
        pmt_ids = {r['id'] for r in CATALOGUE}
        for row in CATALOGUE:
            if row['duplicateOf']:
                with self.subTest(id=row['id']):
                    self.assertNotEqual(row['duplicateOf'], row['id'])
                    self.assertIn(row['duplicateOf'], exam_ids | pmt_ids)
                    original = next((r for r in CATALOGUE if r['id'] == row['duplicateOf']), None)
                    self.assertTrue(original is None or not original['duplicateOf'], 'a copy must point at the original')
        # Spot checks confirmed against the rendered pages.
        dup = {r['id']: r['duplicateOf'] for r in CATALOGUE}
        if 'pmt/pure-core-1/ch2/q9' in dup:
            self.assertEqual(dup['pmt/pure-core-1/ch2/q9'], 'exam/edexcel-9fm0-01-2019-june/q1')
        if 'pmt/pure-core-1/ch8/q5' in dup:
            self.assertEqual(dup['pmt/pure-core-1/ch8/q5'], 'pmt/pure-core-1/ch3/q3')

    def test_offline_packs_carry_every_pmt_question(self):
        # Run the real offline generator over a symlinked copy, so the repository itself is not written to.
        import shutil
        import sys
        import tempfile
        sys.path.insert(0, str(ROOT / 'scripts'))
        import luisa  # noqa: E402
        import offline_manifest  # noqa: E402
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        for item in ROOT.iterdir():
            if item.name not in ('.git', 'dist', 'offline-catalogue.json'):
                (tmp / item.name).symlink_to(item)
        entries = {str(name.relative_to(ROOT)): {'sha256': '0' * 64, 'bytes': 1} for name in luisa.public_files(ROOT)}
        result = offline_manifest.generate(tmp, entries, 'test')
        shared = set(result['shared'])
        self.assertIn('pmt-catalogue.json', shared)
        packs = {p['id']: set(p['files']) | shared for p in result['packs']}
        for row in CATALOGUE:
            book, chapter = row['chapterKeys'][0].split('/')[1:]
            files = packs[f'{book}:{chapter}']
            q = self.payloads[row['dataPath']][row['id']]
            with self.subTest(id=row['id']):
                self.assertIn(row['dataPath'], files)
                for src in re.findall(r'src="(resources/pmt/[^"]+)"', q['question'] + ''.join(q['steps'])):
                    self.assertIn(src, files)

if __name__ == '__main__':
    unittest.main()
