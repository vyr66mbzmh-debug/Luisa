"""Source-label regressions for practice solutions shown in mixed Papers."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('practice_catalogue',Path(__file__).resolve().parents[1]/'scripts/build_practice_catalogue.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SolutionPartLabels(unittest.TestCase):
    def test_gapped_source_labels(self):
        source='<ol type="a"><li>A</li><li>B</li><li value="5">E</li></ol>'
        solution='<ol type="a"><li>one</li><li>two</li><li>five</li></ol>'
        result=module.align_solution_parts(source,solution)
        self.assertIn('<li value="5">five',result)
        self.assertEqual(module.align_solution_parts(source,result),result)

    def test_continuation_and_nested_roman(self):
        source='<ol type="a"><li>A<ol type="i"><li>i</li><li>ii</li></ol></li></ol><p>More</p><ol type="a"><li value="3">C</li></ol>'
        solution='<ol type="a"><li>first<ol type="i"><li>nested</li></ol></li><li>third</li></ol>'
        result=module.align_solution_parts(source,solution)
        self.assertIn('<li value="3">third',result)
        self.assertIn('<li>nested',result)

    def test_unlabelled_diagram_retains_authored_labels(self):
        solution='<ol type="a"><li>Diagram a</li><li>Diagram b</li></ol>'
        self.assertEqual(module.align_solution_parts('<img src="diagram.png">',solution),solution)

if __name__=='__main__':unittest.main()
