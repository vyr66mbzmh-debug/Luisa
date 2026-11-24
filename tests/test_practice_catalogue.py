"""Source-label regressions for practice solutions shown in mixed Papers."""
import importlib.util
import hashlib
import json
from collections import Counter
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

class SourceContext(unittest.TestCase):
    def test_mathematical_title_labels_remain_readable(self):
        self.assertEqual(module.title_label(r'14.2 $y=e^x$'), '14.2 y=eˣ')
        self.assertEqual(module.title_label(r'3.5 Finding $\mu$ and $\sigma$'), '3.5 Finding μ and σ')
        self.assertEqual(module.title_label(r'6.2 Graphs of $\sec x$, $\operatorname{cosec}x$ and $\cot x$'),
                         '6.2 Graphs of sec x, cosec x and cot x')
        with self.assertRaises(ValueError):module.title_label(r'$\unsupported{x}$')

    def test_reference_uses_only_original_prompt(self):
        key='practice/maths-a-level/maths-mechanics-year-1/ch8/8.1/'
        original={'id':key+'q1','question':'<p>Original model.</p>','steps':['SECRET ANSWER'],
                  'hints':['SECRET HINT'],'subchapterId':'8.1','questionLabel':'1'}
        selected={'id':key+'q5','question':'<p>Find its domain.</p>'}
        result=module.source_context(selected,{key+'q1':original})
        self.assertIn('Reference from 8.1 Q1',result)
        self.assertIn(original['question'],result)
        self.assertNotIn('SECRET',result)
        self.assertEqual(selected['question'],'<p>Find its domain.</p>')


class CompletePracticeBank(unittest.TestCase):
    def test_all_source_questions_have_matching_working_and_original_pdf(self):
        root=Path(__file__).resolve().parents[1]
        index=json.loads((root/'practice-catalogue.json').read_text())
        descriptors={q['id']:q for q in index['questions']}
        removed=index.get('migrations', {})
        self.assertFalse(set(removed) & set(descriptors))
        self.assertEqual(len(descriptors)+len(removed),2475)
        self.assertEqual(len(index['questions'])+len(removed),2475)
        counts=Counter();seen=set();chapters=list((root/'content/practice').glob('*/chapter-*.json'))
        self.assertEqual(len(chapters),45)
        for path in chapters:
            doc=json.loads(path.read_text())
            authored=json.loads((root/'resources/practice-solutions'/path.parent.name/path.name).read_text())
            working={q['id']:q for q in authored['solutions']}
            self.assertEqual(len(working),len(authored['solutions']))
            self.assertEqual(set(working)-removed.keys(),{q['id'] for q in doc['questions']})
            counts[doc['sourceFamily']]+=len(set(working) & removed.keys())
            pdf_hash=hashlib.sha256((root/doc['sourcePdf']).read_bytes()).hexdigest()
            for q in doc['questions']:
                self.assertNotIn(q['id'],seen);seen.add(q['id']);counts[doc['sourceFamily']]+=1
                self.assertEqual(q['source']['pdfSha256'],pdf_hash)
                self.assertEqual(q['solutionStatus'],'worked')
                self.assertEqual(q['steps'],[module.align_solution_parts(q['question'],working[q['id']]['solutionHtml'])])
                self.assertEqual(descriptors[q['id']]['board'],'Edexcel')
                self.assertEqual(descriptors[q['id']]['dataPath'],path.relative_to(root).as_posix())
                self.assertTrue(q['skillIds'])
                self.assertEqual(q['subchapterLabel'],module.title_label(q['subchapterTitle']))
        self.assertEqual(seen,set(descriptors))
        self.assertEqual(counts,{'pure-year-1':874,'pure-year-2':738,'applied-year-1':459,'applied-year-2':404})

if __name__=='__main__':unittest.main()
