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

    def test_displayed_mathematical_svgs_have_no_embedded_raster(self):
        import xml.etree.ElementTree as ET

        teaching = json.loads((ROOT / "teaching-catalogue.js").read_text().split("=", 1)[1].strip().rstrip(";"))
        assets = set()

        def collect(shapes, directory):
            for shape in shapes:
                asset = shape.get("asset", "")
                if asset.endswith(".svg"):
                    assets.add(directory / asset)
                collect(shape.get("children", []), directory)

        for book in teaching.values():
            for chapter in book["chapters"]:
                directory = (ROOT / chapter["booklet"]).parent.parent
                deck = json.loads((directory / f"chapter-{chapter['number']:02}.json").read_text())
                # The Pure 1 viewer reads its v11 deck with the native artwork base.
                asset_dir = directory.parent / "native" if directory == ROOT / "resources/pure-year-1/v11" else directory
                for slide in deck["slides"]:
                    collect(slide.get("shapes", []), asset_dir)
        for asset in sorted(assets):
            # Most formula and graph SVGs contain only paths. Parse the few with image tags.
            source = asset.read_bytes()
            if b"image" in source:
                for node in ET.fromstring(source).iter():
                    if node.tag.rsplit("}", 1)[-1] == "image":
                        href = node.get("href") or node.get("{http://www.w3.org/1999/xlink}href") or ""
                        self.assertFalse(href.startswith("data:image/") or href.lower().endswith(
                            (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")), asset)
