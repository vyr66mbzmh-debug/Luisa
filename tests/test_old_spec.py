import json
from pathlib import Path
import re
import unittest
from collections import Counter


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text())


class OldSpecRevision(unittest.TestCase):
    def test_collection_mapping_and_marking_materials(self):
        catalogue = read('old-spec-catalogue.json')
        self.assertEqual(catalogue['group'], 'old spec revision questions')
        rows = catalogue['questions']
        self.assertEqual(len({row['id'] for row in rows}), 244)
        self.assertEqual(sum(row['marks'] for row in rows), 2218)
        self.assertEqual(sum(row['edited'] for row in rows), 15)
        positions = [p for row in rows for p in row['packs']]
        self.assertEqual(len(positions), len(set(positions)))
        self.assertEqual(len(positions), 264)
        self.assertEqual(len({p.split('-')[0] for p in positions}), 22)
        self.assertEqual(Counter(r['difficulty'] for r in rows), {'easy':33, 'medium':124, 'difficult':87})
        self.assertEqual(Counter(r['markScheme'] for r in rows), {'source':227, 'editorial':17})
        existing = {q['id'] for name in ('exam','pmt') for q in read(name+'-catalogue.json')['questions']}
        aliases = [r['canonicalId'] for r in rows if 'canonicalId' in r]
        self.assertEqual(len(set(aliases)), 23)
        self.assertTrue(set(aliases) <= existing)
        keys = {f"{b['course']}/{b['id']}/{c['id']}" for b in read('textbook-catalogue.json')['books'] for c in b['chapters']}
        payloads = {name:{q['id']:q for q in read(name)} for name in {r['dataPath'] for r in rows}}
        for row in rows:
            with self.subTest(id=row['id']):
                self.assertTrue(row['chapterKeys'] and set(row['chapterKeys']) <= keys)
                self.assertEqual('edited' in row['sourceLabel'].lower(), row['edited'])
                q = payloads[row['dataPath']][row['id']]
                self.assertTrue(q['question'] and q['steps'] and q['markSchemeSteps'])
                self.assertNotEqual(q['steps'], q['markSchemeSteps'])
                scheme = ''.join(q['markSchemeSteps'])
                if row['markScheme'] == 'editorial':
                    self.assertIn('Suggested marking guide', scheme)
                    self.assertEqual(sum(map(int,re.findall(r'<p>\[(\d+)\]',scheme))),row['marks'])
                else:
                    self.assertIn('Source marking table',scheme)
                for path in re.findall(r'<img src="([^"]+)"',q['question']+''.join(q['steps'])+scheme):
                    self.assertTrue((ROOT/path).is_file(),path)
