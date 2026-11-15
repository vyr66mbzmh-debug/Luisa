import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TeachingLayoutTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js is required for the lesson renderer")
    def test_question_layout_and_table_classification(self):
        subprocess.run(
            ["node", "--test", str(ROOT / "tests" / "teaching-layout.test.cjs")],
            cwd=ROOT,
            check=True,
        )

    def test_line_equation_exercises_preserve_the_original_givens(self):
        chapter = ROOT / "resources" / "pure-year-1"
        source = json.loads((chapter / "native" / "chapter-05.json").read_text())
        live = json.loads((chapter / "v11" / "chapter-05.json").read_text())
        originals = {
            shape["id"]: shape.get("transcription", {}).get("tex")
            for shape in source["slides"][26]["shapes"]
        }
        prompts = [shape for shape in live["slides"][26]["shapes"] if shape.get("sourceQuestionShape")]
        self.assertEqual(len(prompts), 2)
        for prompt in prompts:
            self.assertEqual(prompt["transcription"]["tex"], originals[prompt["sourceQuestionShape"]])
