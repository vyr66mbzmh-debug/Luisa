"""Coverage, marks, attribution, and internal-only chapter metadata for the MADAS bank."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))


class MadasCollection(unittest.TestCase):
    def test_every_paper_reference_has_its_own_prompt_and_adapted_mark_scheme(self):
        collection = json.loads((ROOT/'madas-catalogue.json').read_text())
        textbook = json.loads((ROOT/'textbook-catalogue.json').read_text())
        chapters = {f"{b['course']}/{b['id']}/{ch['id']}" for b in textbook['books'] for ch in b['chapters']}
        counts = Counter()
        seen = set()
        assets = set()
        cache = {}
        for primary in collection['questions']:
            for row in [primary, *primary.get('editions', [])]:
                slug = row['paperId']
                letter = slug[-1].upper()
                group = slug[:-2]
                counts[group] += 1
                self.assertNotIn(row['id'], seen)
                seen.add(row['id'])
                self.assertEqual(row['difficulty'], 'standard' if letter < 'J' else 'hard' if letter < 'S' else 'very-hard')
                self.assertEqual(row['markScheme'], 'worked')
                self.assertTrue(set(row['chapterKeys']) <= chapters and row['chapterKeys'])
                if group == 'as-pure':
                    self.assertTrue(all('/maths-pure-year-1/' in key for key in row['chapterKeys']))
                qualification = {'alevel-pure':'A-level Pure','as-pure':'AS Pure','alevel-applied':'A-level Applied'}[group]
                self.assertEqual(row['sourceLabel'], f"MADAS {qualification} Paper {letter} Q{row['questionNumber']}")
                path = row['dataPath']
                if path not in cache:
                    cache[path] = {q['id']:q for q in json.loads((ROOT/path).read_text())}
                q = cache[path][row['id']]
                self.assertRegex(q['promptText'], r'[A-Za-z]{3}')
                self.assertNotRegex(q['question'] + ''.join(q['steps']), r'(?:Pure|Mechanics|Statistics) Year [12], Ch\.')
                self.assertEqual(q['steps'][-1], f"<p class=\"madas-total\">Total mark for question {row['questionNumber']} is {row['marks']} marks.</p>")
                self.assertEqual(len(re.findall(r'\[\s*[MAB]\s*1\s*\]', ''.join(q['steps']))), row['marks'], row['id'])
                for kind,markup in [('question',q['question']),('solution',''.join(q['steps']))]:
                    parser = Images()
                    parser.feed(markup)
                    self.assertTrue(parser.images, row['id'])
                    for i,img in enumerate(parser.images, 1):
                        self.assertEqual(img['src'], f"resources/madas/{slug}/q{row['questionNumber']}-{kind}-{i}.svg")
                        self.assertTrue(img['alt'])
                        self.assertTrue((ROOT/img['src']).is_file())
                        assets.add(img['src'])
        self.assertEqual(counts, {'alevel-pure':337,'as-pure':323,'alevel-applied':361})
        self.assertEqual(len(cache), 75)
        self.assertEqual(len(seen), 1021)
        self.assertEqual(assets, {p.relative_to(ROOT).as_posix() for p in (ROOT/'resources/madas').rglob('*.svg')})
