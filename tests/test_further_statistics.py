"""Acceptance checks for the eight Further Statistics 1 Resources chapters."""
import hashlib
import json
import math
import re
import unittest
from pathlib import Path



ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / 'resources/teaching/v003/further-statistics-1'
MANIFEST = json.loads((ROOT / 'docs/evidence/further-statistics-1.json').read_text())


class FurtherStatistics(unittest.TestCase):
    def test_assigned_exercises_and_paired_booklets(self):
        assignments = set()
        total = 0
        for chapter in MANIFEST['chapters']:
            number = chapter['number']
            deck = json.loads((COURSE / f'chapter-{number:02}.json').read_text())
            slides = deck['slides']
            self.assertEqual(len(slides), chapter['slides'])
            for slide in slides:
                assignments.update(re.findall(r'Exercise (\d+[A-Z])', slide.get('sourceAssignment', '')))
            self.assertEqual(math.ceil(len(slides) / 2), chapter['sheetsPerBooklet'])
            exercises = [s for s in slides if 'singlePageExercise' in s]
            self.assertEqual(len(exercises), chapter['exercises'])
            for slide in exercises:
                self.assertIn(slide['title'].split(' · ')[0].removeprefix('Exercise '), assignments)
                parts = slide['singlePageExercise'].get('parts', [])
                if parts:
                    controls = [p['control'] for p in parts]
                    self.assertEqual(len(set(controls)), len(parts))
                    self.assertEqual(controls, slide['answerOrder'])
                    shapes = {shape['id']: shape for shape in slide['shapes']}
                    for part in parts:
                        self.assertEqual(shapes[part['work']]['answerFor'], part['control'])
                        answer = shapes[part['work']]['transcription']['tex']
                        self.assertTrue(answer.strip())
                        # A second source part in one row has lost its own control.
                        for field in (part['prompt'], answer):
                            self.assertNotRegex(field, r'\\par\s+\\textbf\{[a-z]+\}')
            total += len(exercises)
            for edition in ('booklets', 'solutions', 'textbook'):
                key = f'{edition}/chapter-{number:02}.pdf'
                path = COURSE / key
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), MANIFEST['files'][key])
        self.assertEqual(total, 131)
        self.assertEqual(len(assignments), 34)
