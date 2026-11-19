"""Papers UI regressions. Run with a Python environment containing Playwright.

Uses one Chromium worker and a local static server. Printing is stubbed here so
selection invariants are independent from the measured PDF pagination tests.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import threading
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[1]


class BrowserTestServer(ThreadingHTTPServer):
    # Browser asset bursts plus Playwright routing can exceed Python's default
    # five-connection backlog and reset otherwise valid local requests on macOS.
    request_queue_size = 128


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@unittest.skipUnless(sync_playwright, 'Playwright is required for Papers UI checks')
class PapersSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = BrowserTestServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel=os.environ.get('LUISA_BROWSER_CHANNEL') or None)
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/papers.html'

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(service_workers='block')
        self.page = self.context.new_page()
        self.page.route('**/papers-print.js', lambda route: route.fulfill(content_type='text/javascript', body='window.LUISA_PAPERS_PRINT={create:async rows=>{window.testPaperSnapshot=rows;return {warnings:[]}}};'))
        self.page.route('**/practice-catalogue.json', lambda route: route.fulfill(content_type='application/json', body=json.dumps({'version':1,'questions':[]})))
        self.page.goto(self.url)
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('6,147')")

    def tearDown(self):
        self.context.close()

    def generate(self, count):
        self.page.locator('#papers-count').fill(str(count))
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function(f"document.querySelector('#papers-selected-count').textContent === '{count}' && document.querySelector('#papers-cancel').hidden")

    def selection_ids(self):
        return self.page.locator('[data-remove]').evaluate_all('(nodes)=>nodes.map(node=>node.dataset.remove)')

    def practice_fixture(self, incomplete=False):
        descriptor = dict(id='practice/maths-a-level/maths-pure-year-1/ch1/1.1/q1',
                          courseId='maths-a-level', bookId='maths-pure-year-1',
                          chapterId='ch1', chapterNumber=1, chapterTitle='Algebraic expressions',
                          subchapterId='1.1', subchapterTitle='1.1 Index laws', questionLabel='1',
                          board='Edexcel', skillIds=['smq-1.01', 'smq-1.02'],
                          dataPath='content/practice/pure-year-1/chapter-01.json')
        question = dict(id=descriptor['id'], question='<p>Simplify the expression.</p>', contextHtml='<aside>Referenced model: x squared.</aside>',
                        steps=[] if incomplete else ['<p>Apply the index law.</p>'],
                        hints=['<p>Remember that powers add.</p>'])
        self.page.route('**/practice-catalogue.json', lambda route: route.fulfill(
            content_type='application/json', body=json.dumps({'version': 1, 'questions': [descriptor]})))
        self.page.route('**/content/practice/pure-year-1/chapter-01.json', lambda route: route.fulfill(
            content_type='application/json', body=json.dumps({'schemaVersion':1,'questions':[question]})))
        self.page.reload()
        self.page.wait_for_function("!document.querySelector('#papers-source').disabled")
        return descriptor, question

    def test_practice_source_union_hints_and_restore(self):
        descriptor, question = self.practice_fixture()
        self.page.locator('#papers-source').select_option('practice-booklet')
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '1 questions in this pool')
        self.page.locator('#papers-skills input[value$="/smq-1.01"]').check()
        self.page.locator('#papers-skills input[value$="/smq-1.02"]').check()
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '1 questions in this pool')
        self.generate(1)
        self.page.locator('#papers-selected summary').click()
        self.assertNotIn('powers add', self.page.locator('#papers-selected').inner_text())
        self.assertIn('Practice Booklet · Chapter 1 · 1.1 Index laws · Q1', self.page.locator('#papers-selected').inner_text())
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        row = self.page.evaluate('testPaperSnapshot[0]')
        self.assertEqual(row['question'], question['question'])
        self.assertEqual(row['contextHtml'], question['contextHtml'])
        self.assertIn('Referenced model',self.page.locator('#papers-selected').inner_text())
        self.assertEqual(row['hints'], question['hints'])
        self.assertEqual(row['steps'], question['steps'])
        self.assertEqual(row['source']['practiceBookletQuestionId'], descriptor['id'])
        self.page.locator('#papers-source').select_option('luisa')
        self.assertEqual(self.selection_ids(), [descriptor['id']])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-source').input_value(), 'luisa')
        self.assertEqual(self.selection_ids(), [descriptor['id']])

    def test_incomplete_practice_solution_keeps_previous_paper(self):
        self.generate(1)
        previous = self.selection_ids()
        self.practice_fixture(incomplete=True)
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.page.locator('#papers-source').select_option('practice-booklet')
        self.page.locator('#papers-count').fill('1')
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('incomplete content')")
        self.assertEqual(self.selection_ids(), previous)

    def test_all_actual_questions_reference_exclusion_and_qualified_ids(self):
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '6,147 questions in this pool')
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '3,353 questions in this pool')
        self.assertEqual(self.page.locator('#papers-skills input[value$="/smq-2.48"]').count(), 0)
        self.page.locator('#papers-course').select_option('further-maths-a-level')
        self.page.locator('#papers-skills input[value$="/2.04"]').check()
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '34 questions in this pool')
        self.generate(34)
        ids = self.selection_ids()
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith('further-maths-a-level/pure-core-2/') for i in ids))
        self.assertTrue(any(i.endswith('/q34') for i in ids))

    def test_edexcel_filter_excludes_skills_topics_and_saved_questions(self):
        self.page.locator('#papers-course').select_option('further-maths-a-level')
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '2,794 questions in this pool')
        self.assertEqual(self.page.locator('#papers-skills input[value$="/1.16"]').count(), 0)
        self.assertEqual(self.page.locator('#papers-topics input[value$="/further-algebra"]').count(), 0)
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.assertEqual(self.page.locator('#papers-skills input[value$="/smq-1.59"]').count(), 0)
        self.page.locator('#papers-skills input[value$="/smq-1.51"]').check()
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), '2 questions in this pool')
        self.generate(2)
        self.assertEqual({i.rsplit('/', 1)[-1] for i in self.selection_ids()}, {'q1', 'q2'})
        self.page.evaluate("""() => sessionStorage.setItem('luisa-papers-v1', JSON.stringify({
            version:1, selected:[
                'further-maths-a-level/pure-core-1/further-algebra/1.16/q1',
                'maths-a-level/maths-statistics-year-1/sampling-and-data/smq-1.51/q3',
                'further-maths-a-level/pure-core-1/complex-numbers/1.01/q1'
            ]
        }))""")
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-selected-count').textContent==='1'")
        self.assertEqual(self.selection_ids(), ['further-maths-a-level/pure-core-1/complex-numbers/1.01/q1'])
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        self.assertEqual(self.page.evaluate('testPaperSnapshot.length'), 1)

    def test_catalogue_failure_keeps_generation_disabled(self):
        self.page.route('**/textbook-catalogue.json', lambda route: route.fulfill(status=503, body='Unavailable'))
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('could not be loaded')")
        for ident in ['papers-generate', 'papers-browse', 'papers-course', 'papers-book', 'papers-print']:
            self.assertTrue(self.page.locator('#' + ident).is_disabled())
        self.assertEqual(self.selection_ids(), [])

    def test_random_without_replacement_and_regeneration(self):
        self.generate(12)
        first = self.selection_ids()
        self.assertEqual(len(set(first)), 12)
        self.page.locator('#papers-regenerate').click()
        self.page.wait_for_function("document.querySelector('#papers-cancel').hidden")
        second = self.selection_ids()
        self.assertEqual(len(set(second)), 12)
        self.assertNotEqual(set(first), set(second))

    def test_manual_mixed_books_filter_retention_and_immutable_print(self):
        self.page.locator('#papers-browse').click()
        self.page.locator('[data-add]').first.wait_for()
        self.page.locator('[data-add]').first.click()
        first = self.selection_ids()[0]
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.page.locator('[data-add]').first.wait_for()
        self.page.locator('[data-add]').first.click()
        chosen = self.selection_ids()
        self.assertEqual(len(chosen), 2)
        self.assertEqual(chosen[0], first)
        self.assertTrue(chosen[1].startswith('maths-a-level/'))
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        snapshot = self.page.evaluate('''() => ({
          frozen: Object.isFrozen(testPaperSnapshot) && testPaperSnapshot.every(row => Object.isFrozen(row) && Object.isFrozen(row.steps) && Object.isFrozen(row.source)),
          rows: testPaperSnapshot
        })''')
        self.assertTrue(snapshot['frozen'])
        self.assertEqual([r['id'] for r in snapshot['rows']], chosen)
        for row in snapshot['rows']:
            content = json.loads((ROOT / 'content' / f"{row['skillId']}.json").read_text())
            original = next(q for q in content if q['number'] == row['number'])
            self.assertEqual(row['question'], original['question'])
            self.assertEqual(row['steps'], original['steps'])
            self.assertEqual(row['source']['questionId'], original['id'])
        self.page.locator('#papers-selected summary').first.click()
        self.page.locator('#papers-selected .katex').first.wait_for()
        self.page.set_viewport_size({'width': 1440, 'height': 1100})
        screenshot_dir = os.environ.get('LUISA_SCREENSHOT_DIR')
        if screenshot_dir:
            Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
            self.page.evaluate('scrollTo(0, 0)')
            self.page.screenshot(path=str(Path(screenshot_dir) / 'papers-desktop.png'))
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        if screenshot_dir:
            self.page.evaluate('scrollTo(0, 0)')
            self.page.screenshot(path=str(Path(screenshot_dir) / 'papers-mobile-top.png'))
            self.page.locator('#selection-title').scroll_into_view_if_needed()
            self.page.screenshot(path=str(Path(screenshot_dir) / 'papers-mobile-selection.png'))
        self.page.locator('[data-remove]').first.click()
        self.assertEqual(len(self.selection_ids()), 1)
        self.assertEqual(self.page.evaluate('testPaperSnapshot.length'), 2)
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.selection_ids(), chosen[1:])

    def test_multiple_topics_form_one_random_pool(self):
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.page.locator('#papers-book').select_option('maths-a-level/maths-pure-year-1')
        topics = self.page.locator('#papers-topics input').evaluate_all('(nodes) => nodes.slice(0, 2).map(node => node.value)')
        for topic in topics:
            self.page.locator(f'#papers-topics input[value="{topic}"]').check()
        expected = self.page.evaluate("""async topics => { const eligible = new Set((await (await fetch('textbook-catalogue.json')).json()).questions.map(q => `${q.skill}/${q.question}`)); return FMQ_LIBRARY.courses.flatMap(c => c.books.flatMap(b => b.topics.filter(t => topics.includes(`${c.id}/${b.id}/${t.id}`)).flatMap(t => t.skills.flatMap(s => s.questions.filter(q => !q.reference && eligible.has(`${s.id}/${q.number}`)))))).length; }""", topics)
        self.assertEqual(self.page.locator('#papers-pool-count').inner_text(), f'{expected:,} questions in this pool')
        self.assertEqual(self.page.locator('#papers-topics input:checked').count(), 2)
        self.generate(12)
        self.assertTrue(all(any(question.startswith(topic + '/') for topic in topics) for question in self.selection_ids()))
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-topics input:checked').count(), 2)

    def test_invalid_counts_keep_previous_paper(self):
        self.generate(2)
        before = self.selection_ids()
        for value in ['0', '-1', '2.5', '99999']:
            self.page.locator('#papers-count').fill(value)
            self.page.locator('#papers-regenerate').click()
            self.assertIn('Choose a whole number', self.page.locator('#papers-status').inner_text())
            self.assertEqual(self.selection_ids(), before)

    def test_loading_failure_and_cancellation_keep_previous_selection(self):
        self.page.locator('#papers-course').select_option('further-maths-a-level')
        self.page.locator('#papers-skills input[value$="/1.01"]').check()
        self.generate(1)
        before = self.selection_ids()
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.page.route('**/content/*.json', lambda route: route.abort())
        self.page.locator('#papers-count').fill('1')
        self.page.locator('#papers-regenerate').click()
        self.page.wait_for_function("document.querySelector('#papers-status').classList.contains('error')")
        self.assertEqual(self.selection_ids(), before)
        self.page.unroute('**/content/*.json')
        self.page.evaluate("() => { window.fetch = (_url, options) => new Promise((_resolve, reject) => options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))); }")
        self.page.locator('#papers-regenerate').click()
        self.page.locator('#papers-cancel').click()
        self.assertIn('cancelled', self.page.locator('#papers-status').inner_text())
        self.assertEqual(self.selection_ids(), before)


if __name__ == '__main__':
    unittest.main()
