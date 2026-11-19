"""Boundary regressions for native Practice Booklet extraction."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/practice'))
from extract import extract_native,split_items
from render import Renderer

class ExtractionTests(unittest.TestCase):
    def test_nested_parts_are_not_questions(self):
        rows=split_items(r'\item First\begin{parts}\item a\item b\end{parts}\item Second')
        self.assertEqual([n for n,_ in rows],['1','2'])
        self.assertIn(r'\item b',rows[0][1])

    def test_counter_continuation_is_original_number(self):
        self.assertEqual(split_items(r'\setcounter{enumi}{7}\item Next')[0][0],'8')
        self.assertEqual(split_items(r'\setcounter{enumii}{1}\item Next')[0][0],'2')

    def test_hint_separated_without_changing_prompt(self):
        text=r'\begin{document}\chaptersection{s11}{1.1 Algebra}{1}\begin{questions}\item Show $x=2$.\begin{hintbox}Try substitution.\end{hintbox}\end{questions}\hypertarget{answers}{}'
        rows=extract_native(text)
        self.assertEqual(rows[0]['questionLatex'],r'Show $x=2$.')
        self.assertEqual(rows[0]['hintsLatex'],['Try substitution.'])

    def test_native_vector_macros_preserve_arrow_and_column(self):
        result=Renderer('.','.','assets').render(r'$\vv{AB}=\cv3{-2}$')
        self.assertIn(r'\overrightarrow{AB}',result)
        self.assertIn(r'\begin{pmatrix}3\\-2\end{pmatrix}',result)

    def test_unsupported_content_fails(self):
        with self.assertRaisesRegex(ValueError,'Unknown command'):
            Renderer('.','.','assets').render(r'\unknown{meaningful content}')

    def test_layout_table_does_not_gain_data_borders(self):
        result=Renderer('.','.','assets').render(r'\begin{tabular}{ll}$a$&$b$\end{tabular}')
        self.assertIn('practice-layout-table',result)

    def test_table_math_after_rule_and_rowbreak(self):
        result=Renderer('.','.','assets').render(r'\begin{tabular}{|ccc|}$x$&2&4\\\hline$f$&4&8\\$y$&1&3\end{tabular}')
        self.assertEqual(result.count('<tr>'),3)
        self.assertEqual(result.count('<td>'),9)
        self.assertIn('data-math="f"',result)
        self.assertNotIn('&amp;',result)

    def test_table_optional_spacing_and_nested_math(self):
        result=Renderer('.','.','assets').render(r'\begin{tabular}{ll}$\begin{matrix}1&2\\3&4\end{matrix}$&A\&B\\[3pt]$c$&d\\ [-2mm]$e$&f\end{tabular}')
        self.assertEqual(result.count('<tr>'),3)
        self.assertEqual(result.count('<td>'),6)
        self.assertIn('A&amp;B',result)
        self.assertNotIn('[3pt]',result)
        self.assertNotIn('[-2mm]',result)
        self.assertIn(r'1&amp;2\\3&amp;4',result)

if __name__=='__main__':unittest.main()
