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
        original = next(slide for slide in source["slides"] if slide["id"] == "p1-c05-s027")
        for shape_id, question, board_id in [("5", "14", "p1-c05-s027"), ("6", "16", "p1-c05-s027-item-2")]:
            with self.subTest(question=question):
                supplied = next(shape for shape in original["shapes"] if shape["id"] == shape_id)
                board = next(slide for slide in live["slides"] if slide["id"] == board_id)
                texts = {shape["id"]: shape["transcription"]["tex"] for shape in board["shapes"]
                         if "transcription" in shape}
                self.assertEqual(texts["number"], f"Question {question}")
                self.assertEqual(f"{question} " + texts["question"], supplied["transcription"]["tex"])
