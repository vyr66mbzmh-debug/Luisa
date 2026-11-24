"""PAP-075 / PAP-076 / PAP-077: PMT Core Pure topic-sheet questions, checked chapter by chapter.

Expected counts and marks come from the source inventory taken before import (question count and the printed
"(Total for question = N marks)" lines of each PDF); the evidence file records the SHA-256 and page count of each PDF.
Since v0.77 the 51 questions that copied an official past paper or an earlier PMT question are removed (PAP-077-1);
each sheet's inventory equals the questions kept plus the questions removed.
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
REMOVED = {d['removed']: d for d in json.loads((ROOT / 'docs/evidence/v077-duplicates-removed.json').read_text())['removed']}

AS_REMOVALS = json.loads((ROOT / 'docs/evidence/v079-pmt-duplicates.json').read_text())['removed']
REMOVED.update({entry['removed']: entry for entry in AS_REMOVALS})

# sheetId -> (questions, total marks) from the inventory of the source PDFs.
EXPECTED = {
    'pure-core-1-ch1': (7, 52), 'pure-core-1-ch2': (11, 89), 'pure-core-1-ch3': (6, 56), 'pure-core-1-ch4': (6, 35),
    'pure-core-1-ch5': (5, 53), 'pure-core-1-ch6': (8, 65), 'pure-core-1-ch7': (10, 81), 'pure-core-1-ch8': (9, 84),
    'pure-core-1-ch9': (11, 110), 'pure-core-2-ch1': (11, 92), 'pure-core-2-ch2': (11, 87),
    'pure-core-2-ch3': (7, 49), 'pure-core-2-ch4': (4, 36), 'pure-core-2-ch5': (6, 59), 'pure-core-2-ch6': (9, 67),
    'pure-core-2-ch7': (3, 30), 'pure-core-2-ch8': (10, 138),
}
# Source slips kept as printed, on questions still in the bank (two more were on removed copies).
SOURCE_SLIPS = {'pmt/pure-core-1/ch2/q7', 'pmt/pure-core-1/ch6/q2', 'pmt/pure-core-1/ch6/q6'}
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

    def test_counts_after_duplicate_removal(self):
        self.assertEqual(len(CATALOGUE) + len(AS_REMOVALS), 83)
        for book, expected in [('pure-core-1', 58), ('pure-core-2', 25)]:
            count = sum(book in r['id'] for r in CATALOGUE) + sum(book in r['removed'] for r in AS_REMOVALS)
            self.assertEqual(count, expected)
        self.assertEqual(sum(r['marks'] for r in CATALOGUE + AS_REMOVALS), 704)
        self.assertEqual(collections.Counter(r['difficulty'] for r in CATALOGUE + AS_REMOVALS), {'easy': 29, 'medium': 42, 'difficult': 12})
        self.assertEqual(len(REMOVED), 51 + len(AS_REMOVALS))

    def test_original_exams_are_recorded_only_when_confirmed_PAP_077_5(self):
        # Every survivor is listed; a confirmed original names a paper, series and question; the rest are 'unknown'.
        evidence = json.loads((ROOT / 'docs/evidence/v077-pmt-original-exams.json').read_text())
        listed = {r['id']: r for r in evidence['questions']}
        self.assertEqual(set(listed), {r['id'] for r in CATALOGUE} | {r['removed'] for r in AS_REMOVALS})
        confirmed = {i: r for i, r in listed.items() if r['originalExam'] != 'unknown'}
        self.assertEqual((evidence['summary']['confirmed'], evidence['summary']['unknown']), (len(confirmed), len(listed) - len(confirmed)))
        self.assertEqual(len(confirmed), 56)
        for row in CATALOGUE:
            with self.subTest(row['id']):
                record = listed[row['id']]
                self.assertEqual(row.get('originalExam'), confirmed.get(row['id'], {}).get('originalExam'))
                if row['id'] in confirmed:
                    self.assertRegex(record['originalExam'], r'^Edexcel [89]FM0/0[12] .+ Q\d+$')
                    self.assertEqual(record['originalExam'], f"Edexcel {record['paper']} {record['series']} Q{record['questionNumber']}")
                    self.assertTrue(record['dateEvidence'] and record['comparedWith'] and record['method'])

    def test_every_imported_chapter_is_complete_with_its_printed_marks(self):
        imported = set(self.rows)
        self.assertTrue(imported, 'no PMT chapters imported')
        self.assertLessEqual(imported, set(EXPECTED), 'a chapter without an inventory entry')
        for sheet in sorted(EXPECTED):
            with self.subTest(sheet=sheet):
                book, chapter = sheet.rsplit('-ch', 1)
                kept = {r['questionNumber']: r['marks'] for r in self.rows[sheet]}
                gone = {int(i.rsplit('/q', 1)[1]): d['marks'] for i, d in REMOVED.items() if i.startswith(f'pmt/{book}/ch{chapter}/')}
                count, marks = EXPECTED[sheet]
                self.assertFalse(set(kept) & set(gone))
                self.assertEqual(sorted(kept | gone), list(range(1, count + 1)))
                self.assertEqual(sum(kept.values()) + sum(gone.values()), marks)

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

    def test_no_duplicates_remain_and_removed_ids_migrate(self):
        exam_ids = {r['id'] for r in json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']}
        pmt_ids = {r['id'] for r in CATALOGUE}
        migrations = json.loads((ROOT / 'pmt-catalogue.json').read_text())['migrations']
        for row in CATALOGUE:
            self.assertNotIn('duplicateOf', row)
        self.assertEqual(set(migrations), set(REMOVED))
        for old, new in migrations.items():
            with self.subTest(id=old):
                self.assertNotIn(old, pmt_ids)
                self.assertIn(new, exam_ids | pmt_ids)
                retained = REMOVED[old]['retained']
                self.assertEqual(migrations.get(retained, retained), new)
                self.assertTrue(new.startswith('exam/') or new in pmt_ids)
        # Spot checks confirmed against the rendered pages (v0.75): an official original, and an earlier PMT original.
        by_label = {d['removedLabel']: d['retained'] for d in REMOVED.values()}
        self.assertEqual(by_label['PMT Core Pure 1 Ch.2 Argand Diagrams Q9'], 'exam/edexcel-9fm0-01-2019-june/q1')
        self.assertEqual(by_label['PMT Core Pure 1 Ch.8 Proof by Induction Q5'], 'pmt/pure-core-1/ch3/q3')

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
