"""PAP-077-1 / PAP-077-2: the bank holds no duplicates, and the importers cannot add one.

The rule (standing from v0.77): an official past paper beats a PMT question, the earlier PMT question beats a later
one, and a second copy of the same official paper is skipped. scripts/duplicates.py finds candidates; every decision is
in docs/evidence/duplicate-decisions.json; scripts/luisa.py check (part of the gate) runs `duplicates.errors`.
"""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import duplicates  # noqa: E402


def read(path):
    return json.loads((ROOT / path).read_text())


def payload_question(qid):
    for name in ('exam-catalogue.json', 'pmt-catalogue.json'):
        for row in read(name)['questions']:
            if row['id'] == qid:
                return next(q for q in read(row['dataPath'])['questions'] if q['id'] == qid)
    raise KeyError(qid)


def scratch_repo():
    """A throwaway copy of the files `remove` writes; everything else is linked read-only from the repository."""
    tmp = Path(tempfile.mkdtemp())
    written = {'pmt-catalogue.json', 'exam-catalogue.json', 'content', 'docs', 'resources'}
    for item in ROOT.iterdir():
        if item.name not in written and item.name not in ('.git', 'dist'):
            (tmp / item.name).symlink_to(item)
    for name in ('pmt-catalogue.json', 'exam-catalogue.json'):
        shutil.copy(ROOT / name, tmp / name)
    (tmp / 'content').mkdir()
    for item in (ROOT / 'content').iterdir():
        if item.name in ('pmt', 'exams'):
            shutil.copytree(item, tmp / 'content' / item.name)
        else:
            (tmp / 'content' / item.name).symlink_to(item)
    (tmp / 'resources').mkdir()
    for item in (ROOT / 'resources').iterdir():
        if item.name == 'pmt':
            shutil.copytree(item, tmp / 'resources' / 'pmt')
        else:
            (tmp / 'resources' / item.name).symlink_to(item)
    (tmp / 'docs/evidence').mkdir(parents=True)
    shutil.copy(ROOT / duplicates.DECISIONS, tmp / duplicates.DECISIONS)
    return tmp


class BankHasNoDuplicates(unittest.TestCase):
    def test_gate_check_passes_on_the_bank(self):
        self.assertEqual(duplicates.errors(ROOT), [])

    def test_counts_after_removal(self):
        items = duplicates.bank(ROOT)
        self.assertEqual(len([i for i in items if i['kind'] != 'madas']), 9149)
        self.assertEqual(sum(i['kind'] == 'madas' for i in items), 1018)
        pmt = [i for i in items if i['kind'] == 'pmt']
        self.assertEqual(len(pmt), 83)
        self.assertEqual(sum(i['id'].startswith('pmt/pure-core-1/') for i in pmt), 58)
        self.assertEqual(sum(i['id'].startswith('pmt/pure-core-2/') for i in pmt), 25)

    def test_no_row_carries_a_copy_link(self):
        for name in ('pmt-catalogue.json', 'exam-catalogue.json', 'practice-catalogue.json'):
            for row in read(name)['questions']:
                self.assertNotIn('duplicateOf', row, row['id'])

    def test_every_removal_is_recorded_and_migrated(self):
        decisions = read(duplicates.DECISIONS)['duplicates']
        self.assertEqual(len(decisions), 51)
        self.assertEqual(sum(d['retained'].startswith('exam/') for d in decisions), 47)
        self.assertEqual(sum(d['retained'].startswith('pmt/') for d in decisions), 4)
        self.assertEqual(read('pmt-catalogue.json')['migrations'], {d['removed']: d['retained'] for d in decisions})
        pmt_to_pmt = {d['removed']: d['retained'] for d in decisions if d['retained'].startswith('pmt/')}
        self.assertEqual(pmt_to_pmt, {'pmt/pure-core-1/ch8/q5': 'pmt/pure-core-1/ch3/q3',
                                      'pmt/pure-core-1/ch8/q8': 'pmt/pure-core-1/ch3/q6',
                                      'pmt/pure-core-2/ch1/q10': 'pmt/pure-core-1/ch2/q7',
                                      'pmt/pure-core-2/ch6/q1': 'pmt/pure-core-2/ch3/q3'})
        trace = read('docs/evidence/v077-duplicates-removed.json')
        self.assertEqual({(r['removed'], r['retained']) for r in trace['removed']},
                         {(d['removed'], d['retained']) for d in decisions})

    def test_no_removed_id_is_left_anywhere_in_shipped_data_or_tests(self):
        removed = [d['removed'] for d in read(duplicates.DECISIONS)['duplicates']]
        # Only the migration map (and the evidence) may name a removed ID.
        files = ['exam-catalogue.json', 'practice-catalogue.json', 'textbook-catalogue.json', 'content/exams/pilot-metadata.json',
                 *[str(p.relative_to(ROOT)) for p in (ROOT / 'content/pmt').glob('*.json')],
                 *[str(p.relative_to(ROOT)) for p in (ROOT / 'tests').glob('*.py') if p.name != 'test_duplicates.py']]
        for name in files:
            text = (ROOT / name).read_text()
            for qid in removed:
                self.assertIsNone(re.search(rf'{qid}(?![0-9])', text), f'{qid} in {name}')
        pmt = json.loads((ROOT / 'pmt-catalogue.json').read_text())
        text = json.dumps(pmt['questions'])
        for qid in removed:
            self.assertNotIn(f'"{qid}"', text)
        for qid in removed:
            sheet, q = qid.split('/')[1:3], int(qid.rsplit('/q', 1)[1])
            folder = ROOT / 'resources/pmt' / f'{sheet[0]}-{sheet[1]}'
            self.assertEqual(list(folder.glob(f'q{q:02}-*')), [], qid)

    def test_survivors_gained_the_copies_chapters_and_skills(self):
        rows = {r['id']: r for n in ('exam-catalogue.json', 'pmt-catalogue.json') for r in read(n)['questions']}
        self.assertIn('further-maths-a-level/pure-core-1/8', rows['pmt/pure-core-1/ch3/q3']['chapterKeys'])
        self.assertEqual(rows['pmt/pure-core-1/ch3/q3']['chapterKeys'][0], 'further-maths-a-level/pure-core-1/3')
        self.assertIn('further-maths-a-level/pure-core-2/2', rows['exam/edexcel-9fm0-01-sample/q1']['chapterKeys'])
        self.assertIn('1.43', [s['skillId'] for s in rows['exam/edexcel-9fm0-02-2019-june/q7']['skillMappings']])
        meta = {q['id']: q for p in read('content/exams/pilot-metadata.json')['papers'] for q in p['questions']}
        self.assertEqual(meta['exam/edexcel-9fm0-02-2019-june/q7']['skillMappings'], rows['exam/edexcel-9fm0-02-2019-june/q7']['skillMappings'])


class ImportersRefuseDuplicates(unittest.TestCase):
    def test_a_pmt_copy_of_an_official_question_is_skipped(self):
        original = payload_question('exam/edexcel-9fm0-01-2019-june/q1')
        skip, replace, decide = duplicates.incoming([dict(original, id='pmt/pure-core-1/ch2/q99')], ROOT)
        self.assertEqual([(s['new'], s['existing']) for s in skip], [('pmt/pure-core-1/ch2/q99', 'exam/edexcel-9fm0-01-2019-june/q1')])
        with self.assertRaises(SystemExit):
            duplicates.guard_import([dict(original, id='pmt/pure-core-1/ch2/q99')], ROOT)

    def test_a_later_pmt_copy_of_a_pmt_question_is_skipped(self):
        original = payload_question('pmt/pure-core-1/ch3/q3')
        skip, _, _ = duplicates.incoming([dict(original, id='pmt/pure-core-2/ch9/q1')], ROOT)
        self.assertEqual([s['existing'] for s in skip], ['pmt/pure-core-1/ch3/q3'])

    def test_an_official_paper_imported_twice_is_skipped(self):
        paper = read('content/exams/edexcel-9fm0-02-2021-november.json')['questions']
        second = [dict(q, id=q['id'].replace('2021-november', '2021-november-copy')) for q in paper]
        skip, replace, decide = duplicates.incoming(second, ROOT)
        self.assertGreaterEqual(len(skip), len(paper) - 1)
        self.assertEqual(replace, [])
        with self.assertRaises(SystemExit):
            duplicates.guard_import(second, ROOT)

    def test_a_new_official_question_replaces_a_pmt_copy(self):
        pmt = payload_question('pmt/pure-core-2/ch7/q1')
        skip, replace, decide = duplicates.incoming([dict(pmt, id='exam/edexcel-9fm0-01-2099-june/q1')], ROOT)
        self.assertEqual(skip, [])
        self.assertEqual([(r['new'], r['existing']) for r in replace], [('exam/edexcel-9fm0-01-2099-june/q1', 'pmt/pure-core-2/ch7/q1')])
        self.assertEqual(duplicates.guard_import([dict(pmt, id='exam/edexcel-9fm0-01-2099-june/q1')], ROOT), replace)

    def test_known_copies_score_above_the_threshold(self):
        # Each removed copy's retained question, re-imported under a PMT ID, is caught (recall on the 51 pairs).
        decisions = read(duplicates.DECISIONS)['duplicates']
        for d in decisions:
            self.assertGreaterEqual(d['similarity'], duplicates.IMPORTED, d['removed'])


class GateFailsOnDuplicates(unittest.TestCase):
    def setUp(self):
        self.tmp = scratch_repo()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_a_copy_link_or_a_removed_question_fails_the_gate(self):
        path = self.tmp / 'pmt-catalogue.json'
        cat = json.loads(path.read_text())
        cat['questions'][0]['duplicateOf'] = 'exam/edexcel-9fm0-01-2019-june/q1'
        path.write_text(json.dumps(cat))
        self.assertTrue(any('is a copy of' in e for e in duplicates.errors(self.tmp)))

    def test_an_undecided_candidate_fails_the_gate(self):
        dec = json.loads((self.tmp / duplicates.DECISIONS).read_text())
        dec['notDuplicates'] = [d for d in dec['notDuplicates'] if d['id'] != 'pmt/pure-core-1/ch4/q3']
        (self.tmp / duplicates.DECISIONS).write_text(json.dumps(dec))
        errors = duplicates.errors(self.tmp)
        self.assertTrue(any('possible duplicate pmt/pure-core-1/ch4/q3' in e for e in errors), errors)

    def test_remove_carries_over_deletes_and_migrates(self):
        # As if a new official paper had copied PMT Core Pure 1 Ch.3 Q3 (itself the survivor of Ch.8 Q5).
        result = duplicates.remove(self.tmp, 'pmt/pure-core-1/ch3/q3', 'exam/edexcel-9fm0-02-2021-november/q4', 'test')
        self.assertIn('further-maths-a-level/pure-core-1/8', result['chapterKeysAdded'])
        self.assertGreater(result['filesDeleted'], 0)
        cat = json.loads((self.tmp / 'pmt-catalogue.json').read_text())
        self.assertNotIn('pmt/pure-core-1/ch3/q3', {r['id'] for r in cat['questions']})
        self.assertEqual(cat['migrations']['pmt/pure-core-1/ch3/q3'], 'exam/edexcel-9fm0-02-2021-november/q4')
        self.assertEqual(cat['migrations']['pmt/pure-core-1/ch8/q5'], 'exam/edexcel-9fm0-02-2021-november/q4')  # chain resolved
        self.assertFalse(list((self.tmp / 'resources/pmt/pure-core-1-ch3').glob('q03-*')))
        self.assertTrue(list((ROOT / 'resources/pmt/pure-core-1-ch3').glob('q03-*')), 'the repository is untouched')
        exam = {r['id']: r for r in json.loads((self.tmp / 'exam-catalogue.json').read_text())['questions']}
        self.assertIn('further-maths-a-level/pure-core-1/8', exam['exam/edexcel-9fm0-02-2021-november/q4']['chapterKeys'])
        errors = [e for e in duplicates.errors(self.tmp) if 'possible duplicate' not in e]
        self.assertEqual(errors, [])

    def test_the_earlier_pmt_question_is_kept(self):
        with self.assertRaises(SystemExit):
            duplicates.remove(self.tmp, 'pmt/pure-core-1/ch3/q3', 'pmt/pure-core-2/ch3/q3', 'test')
        with self.assertRaises(SystemExit):
            duplicates.remove(self.tmp, 'exam/edexcel-9fm0-02-2021-november/q4', 'pmt/pure-core-1/ch3/q3', 'test')


if __name__ == '__main__':
    unittest.main()
