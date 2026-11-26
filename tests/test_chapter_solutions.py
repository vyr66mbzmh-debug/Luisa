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
        evidence = json.loads((ROOT / 'docs/evidence/v056-booklets.json').read_text())['chapters']
        # Retain the historical v0.56 acceptance record. Apply only independently
        # reviewed replacement PDFs. Check every current fingerprint, and the
        # historical fingerprint/page count for matched canonical chapter records.
        replacements = json.loads((ROOT / 'docs/evidence/v059-integration.json').read_text())['mathematics']['pdfs']
        replacements += json.loads((ROOT / 'docs/evidence/v083-teaching-pdfs.json').read_text())['pdfs']
        replacements += json.loads((ROOT / 'docs/evidence/v084-teaching-pdfs.json').read_text())['pdfs']
        latest = {}
        for replacement in replacements:
            path = replacement['path']
            if path in latest:
                self.assertEqual(latest[path], replacement['before'])
            latest[path] = replacement['after']
            for record in evidence.values():
                for kind in ('booklet', 'solutions'):
                    if record[kind]['file'] == replacement['path']:
                        self.assertEqual(record[kind]['sha256'], replacement['before'])
                        self.assertEqual(record[kind]['pages'], replacement['pages'])
                        record[kind]['sha256'] = replacement['after']
        self.assertEqual(sum(r['solutions']['pages'] for r in evidence.values()), 1507)
        # A teaching question can move to a new panel when its working is reunited.
        # Verify the old edition before accepting its newly paginated successor.
        revised = json.loads((ROOT / 'docs/evidence/v086-teaching-pdfs.json').read_text())['pdfs']
        current = {entry['path']: entry for entry in revised}
        self.assertEqual(len(current), len(revised))
        for entry in revised:
            path = entry['path']
            if path in latest:
                self.assertEqual(latest[path], entry['before'])
            latest[path] = entry['after']
            for record in evidence.values():
                for kind in ('booklet', 'solutions'):
                    prior = record[kind]
                    if prior['file'] == path:
                        self.assertEqual((prior['sha256'], prior['pages']),
                                         (entry['before'], entry['previousPages']))
                        prior.update(sha256=entry['after'], pages=entry['pages'])

        linked = set()
        for book in teaching.values():
            for chapter in book['chapters']:
                path = ROOT / chapter['booklet']
                deck = path.parent.parent / f"chapter-{chapter['number']:02}.json"
                total = len(json.loads(deck.read_text())['slides'])
                alias = path.with_name(f"chapter-{chapter['number']:02}.pdf").relative_to(ROOT).as_posix()
                if alias != chapter['booklet'] and alias in latest:
                    student = current[chapter['booklet']]
                    self.assertEqual(latest[alias], student['before'])
                    latest[alias] = student['after']
                for kind in ('booklet', 'solutions'):
                    url = chapter[kind]
                    linked.add(url)
                    self.assertEqual(current[url]['slides'], total)
                    self.assertEqual(current[url]['pages'], (total + 1) // 2)
        self.assertEqual(set(current), linked)
        for path, digest in latest.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
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
                    self.assertEqual(url, record['solutions']['file'])
                    self.assertTrue(url.endswith(' SOLUTIONS.pdf'))
                    self.assertNotIn(url, seen)
                    seen.add(url)
                    self.assertNotEqual(url, chapter['booklet'])
                    self.assertEqual(hashlib.sha256((ROOT / url).read_bytes()).hexdigest(), record['solutions']['sha256'])
                    self.assertEqual([r['url'] for r in topic['resources'] if r['type'] == 'solutions' and r['access'] == 'available'], [url])
                    pupil = ROOT / chapter['booklet']
                    self.assertEqual(hashlib.sha256(pupil.read_bytes()).hexdigest(), record['booklet']['sha256'])
                    alias = pupil.with_name(f"chapter-{chapter['number']:02}.pdf")
                    self.assertEqual(hashlib.sha256(alias.read_bytes()).hexdigest(), record['booklet']['sha256'])
                    self.assertEqual(progress.count(f'<a href="{url}">Solutions</a>'), 1)
        self.assertEqual(len(seen), 62)
