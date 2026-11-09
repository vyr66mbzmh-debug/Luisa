import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from luisa import catalogue
from offline_manifest import BOOK_ALIASES


class ChapterSolutions(unittest.TestCase):
    def test_chapters_use_accepted_solution_pdfs(self):
        teaching = catalogue()
        evidence = json.loads((ROOT / 'docs/evidence/v037-solutions.json').read_text())
        textbook = json.loads((ROOT / 'textbook-catalogue.json').read_text())
        progress = (ROOT / 'development-progress.html').read_text()
        seen = set()
        for book in textbook['books']:
            key = BOOK_ALIASES.get(book['id'], book['id'])
            chapters = {c['number']: c for c in teaching[key]['chapters']}
            for topic in book['chapters']:
                chapter = chapters[int(topic['id'])]
                url = chapter['solutions']
                record = evidence[f"{key}-{chapter['number']}"]
                with self.subTest(book=key, chapter=chapter['number']):
                    self.assertNotIn(url, seen)
                    seen.add(url)
                    self.assertNotEqual(url, chapter['booklet'])
                    self.assertEqual(hashlib.sha256((ROOT / url).read_bytes()).hexdigest(), record['sha256'])
                    self.assertEqual([r['url'] for r in topic['resources'] if r['type'] == 'solutions' and r['access'] == 'available'], [url])
                    self.assertEqual(progress.count(f'<a href="{url}">Solutions</a>'), 1)
        self.assertEqual(len(seen), 62)
        self.assertEqual(sum(r['pages'] for r in evidence.values()), 1496)
