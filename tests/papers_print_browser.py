"""Focused print acceptance; run explicitly with Playwright and Chrome installed.

One browser, one page at a time. No network services or new production dependencies.
"""
import functools
import http.server
import json
import pathlib
import tempfile
import threading
import unittest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]


class QuietServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        # Exercise the deployed ADA policy, including popup base and script URLs.
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; base-uri 'self'")
        super().end_headers()


def row(skill, number):
    question = next(q for q in json.loads((ROOT / 'content' / (skill + '.json')).read_text()) if q['number'] == number)
    return dict(question, skillCode=skill, courseTitle='Mathematics', bookTitle='Question library', topicTitle='Practice')


class PapersPrintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietServer, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel='chrome')
        cls.context = cls.browser.new_context()

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.page = self.context.new_page()
        # Avoid library/service worker side effects while retaining a real HTTP base.
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}/icon.svg')
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}/index.html')
        self.page.add_script_tag(url='/papers-print.js')

    def tearDown(self):
        for page in self.context.pages:
            page.close()

    def preview(self, rows):
        with self.page.expect_popup() as event:
            self.page.evaluate('rows => { window.resultPromise = LUISA_PAPERS_PRINT.create(rows).then(r => window.result = {ready:r.ready,warnings:r.warnings,pageCount:r.pageCount}); }', rows)
        preview = event.value
        self.page.evaluate('window.resultPromise')
        return preview, self.page.evaluate('window.result')

    def test_mixed_paper_pdf_has_complete_matching_solutions_at_back(self):
        rows = [row('1.01', 1), row('2.65', 1), row('1.01', 2), row('smq-2.30', 9)]
        preview, result = self.preview(rows)
        self.assertTrue(result['ready'], result)
        self.assertEqual(preview.title(), 'Maths Paper')
        self.assertTrue(preview.locator('.print-question img').evaluate_all('nodes=>nodes.length>0 && nodes.every(n=>n.complete&&n.naturalWidth>0)'))
        question_ids = preview.locator('.questions-page .print-question').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.questionId)')
        self.assertEqual(question_ids, [r['id'] for r in rows])
        self.assertEqual(preview.locator('.questions-page').count(), 2)
        self.assertGreater(preview.locator('.solutions-page').count(), 1)
        self.assertEqual(preview.locator('.print-page').evaluate_all("nodes=>nodes.map(n=>n.classList.contains('questions-page'))")[:2], [True, True])
        for index, item in enumerate(rows):
            selector = '[data-question-id="' + item['id'] + '"]'
            source = self.page.evaluate('html=>{const n=document.createElement("div");n.innerHTML=html;return [...n.querySelectorAll("[data-math]")].map(x=>x.dataset.math)}', ''.join(item['steps']))
            actual = preview.locator('.print-solution' + selector + ' [data-math]').evaluate_all('nodes=>nodes.map(n=>n.dataset.math)')
            self.assertEqual(actual, source)
            self.assertIn(f'Question {index + 1}', preview.locator('.print-solution' + selector).first.inner_text())
            self.assertIn(f'Source: Luisa {item["skillCode"]} Q{item["number"]}', preview.locator('.print-solution' + selector).first.inner_text())
        dimensions = preview.locator('.page-content,.print-question').evaluate_all('nodes=>nodes.map(n=>[n.scrollHeight-n.clientHeight,n.scrollWidth-n.clientWidth])')
        self.assertTrue(all(h <= 1 and w <= 1 for h, w in dimensions), dimensions)
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / 'Maths Paper.pdf'
            preview.pdf(path=str(path), prefer_css_page_size=True)
            import fitz
            pdf = fitz.open(path)
            self.assertEqual(len(pdf), result['pageCount'])
            for index, sheet in enumerate(pdf):
                self.assertAlmostEqual(sheet.rect.width, 595.28, delta=1)
                self.assertAlmostEqual(sheet.rect.height, 841.89, delta=1)
                self.assertIn(f'Page {index + 1} of {len(pdf)}', sheet.get_text())
            self.assertNotIn('Worked solutions', pdf[0].get_text())
            self.assertIn('Worked solutions', pdf[2].get_text())
            pdf[1].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/luisa57-verified-diagram-page.png')
            pdf[0].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/luisa57-verified-question-page.png')
            pdf[2].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/luisa57-verified-solution-page.png')

    def test_oversized_original_is_identified_and_never_clipped_into_pdf(self):
        preview, result = self.preview([row('smq-1.53', 2)])
        self.assertFalse(result['ready'])
        self.assertTrue(any('smq-1.53 Q2' in warning for warning in result['warnings']))
        self.assertTrue(preview.get_by_role('button', name='Print / Save PDF').is_disabled())
        self.assertEqual(preview.locator('.print-question img').count(), 21)

    def test_closed_loading_preview_releases_caller(self):
        self.context.route('**/papers-print.css', lambda route: None)
        try:
            with self.page.expect_popup() as event:
                self.page.evaluate('rows=>{window.resultPromise=LUISA_PAPERS_PRINT.create(rows).catch(e=>window.failure=e.message)}', [row('1.01',1)])
            event.value.close()
            self.page.evaluate('window.resultPromise')
            self.assertIn('closed', self.page.evaluate('window.failure'))
        finally:
            self.context.unroute('**/papers-print.css')


if __name__ == '__main__':
    unittest.main()
