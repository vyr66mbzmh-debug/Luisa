"""PAP-074-1: the mark-scheme flag is derived from the payloads for every question in the Papers bank."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import mark_schemes  # noqa: E402


class MarkSchemeFlagTests(unittest.TestCase):
    def test_every_question_has_its_derived_flag(self):
        self.assertEqual(mark_schemes.errors(ROOT), [])
        derived = mark_schemes.derive(ROOT)
        self.assertEqual({name: len(rows) for name, rows in derived.items()},
                         {'textbook-catalogue.json': 6147, 'practice-catalogue.json': 2475, 'exam-catalogue.json': 444,
                          'pmt-catalogue.json': 134})

    def test_counts_per_source(self):
        counts = {f'{source}|{value}': n for (source, value), n in mark_schemes.counts(ROOT).items()}
        self.assertEqual(counts, {
            'Past Papers|official': 444,                               # paired official Edexcel schemes
            'Exam style (Practice Booklet)|worked': 554,               # Luisa worked solutions only
            'Practice questions (Practice Booklet)|worked': 1921,
            'Practice questions (Luisa skill questions)|worked': 6147,
            'PMT (pure-core-1)|source': 73,                            # PMT topic sheets with their source mark schemes
            'PMT (pure-core-2)|source': 61,
        })

    def test_past_paper_official_only_when_every_step_is_an_official_crop_of_that_paper(self):
        catalogue = json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']
        q = next(x for x in catalogue if x['id'] == 'exam/edexcel-9fm0-01-2019-june/q1')
        payload = next(x for x in json.loads((ROOT / q['dataPath']).read_text())['questions'] if x['id'] == q['id'])
        self.assertEqual(mark_schemes.exam_kind(payload), 'official')
        for broken in (dict(payload, steps=[]),
                       dict(payload, steps=payload['steps'] + ['<p>Luisa worked solution.</p>']),
                       dict(payload, steps=[payload['steps'][0].replace('edexcel-9fm0-01-2019-june/', 'edexcel-9fm0-02-2019-june/')]),
                       dict(payload, steps=[payload['steps'][0].replace('-ms-', '-fig-')])):
            with self.subTest(steps=broken['steps'][:1]), self.assertRaises(ValueError):
                mark_schemes.exam_kind(broken)

    def test_worked_solutions_are_never_a_mark_scheme(self):
        self.assertEqual(mark_schemes.source_kind({'id': 'x', 'steps': ['<p>Worked.</p>']}), 'worked')
        self.assertEqual(mark_schemes.source_kind({'id': 'x', 'steps': []}), 'none')
        self.assertEqual(mark_schemes.source_kind({'id': 'x', 'steps': ['  ']}), 'none')
        # A source's own marking scheme counts only with its kind and source page recorded.
        self.assertEqual(mark_schemes.source_kind({'id': 'x', 'steps': ['<p>M1</p>'], 'sourceScheme': {'kind': 'official', 'page': 4}}), 'official')
        with self.assertRaises(ValueError):
            mark_schemes.source_kind({'id': 'x', 'steps': ['<p>M1</p>'], 'sourceScheme': {'kind': 'worked', 'page': 4}})
        with self.assertRaises(ValueError):
            mark_schemes.source_kind({'id': 'x', 'steps': ['<p>M1</p>'], 'sourceScheme': {'kind': 'official'}})
        # A PMT row counts only when every step is a crop of its own question's scheme (v0.75 review).
        own = '<figure class="exam-solution-source"><img src="resources/pmt/pure-core-1-ch2/q07-ms-p19-1.png" alt="x"></figure>'
        pmt = {'id': 'pmt/pure-core-1/ch2/q7', 'sourceScheme': {'kind': 'source', 'page': [19]}}
        self.assertEqual(mark_schemes.source_kind(dict(pmt, steps=[own])), 'source')
        missing = own.replace('p19-1.png', 'p19-9.png')  # well formed, but no such crop file
        for steps in ([], ['<p>M1 typed scheme</p>'], [own.replace('q07', 'q08')], [own, '<p>extra</p>'], [own + '<p>extra</p>'], [missing]):
            with self.assertRaises(ValueError):
                mark_schemes.source_kind(dict(pmt, steps=steps))

    def test_check_detects_a_hand_edited_or_missing_flag(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        for name in ('textbook-catalogue.json', 'practice-catalogue.json', 'exam-catalogue.json', 'pmt-catalogue.json'):
            shutil.copy(ROOT / name, root / name)
        (root / 'content').symlink_to(ROOT / 'content')
        (root / 'resources').symlink_to(ROOT / 'resources')
        self.assertEqual(mark_schemes.errors(root), [])
        practice = json.loads((root / 'practice-catalogue.json').read_text())
        tampered = copy.deepcopy(practice)
        tampered['questions'][0]['markScheme'] = 'official'
        del tampered['questions'][1]['markScheme']
        (root / 'practice-catalogue.json').write_text(json.dumps(tampered))
        found = mark_schemes.errors(root)
        self.assertEqual(len(found), 2, found)
        self.assertIn('markScheme official but the payload gives worked', found[0])
        self.assertIn('has no valid markScheme', found[1])

    def test_ids_and_order_unchanged_by_the_flag(self):
        # Saved selections and saved papers refer to row IDs: the flag sits after the id and changes no ID or order.
        for name in ('practice-catalogue.json', 'exam-catalogue.json'):
            rows = json.loads((ROOT / name).read_text())['questions']
            self.assertEqual([list(r)[:2] for r in rows[:3]], [['id', 'markScheme']] * 3)
            self.assertEqual(len({r['id'] for r in rows}), len(rows))


if __name__ == '__main__':
    unittest.main()
