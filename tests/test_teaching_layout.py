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
