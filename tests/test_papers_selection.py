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
        self.page.route('**/papers-print.js', lambda route: route.fulfill(content_type='text/javascript', body='window.LUISA_PAPERS_PRINT={create:async (rows,opts)=>{window.testPaperSnapshot=rows;window.testPrintOptions=opts;return {warnings:[]}}};'))
        self.page.route('**/practice-catalogue.json', lambda route: route.fulfill(content_type='application/json', body=json.dumps({'version':1,'questions':[]})))
        self.page.route('**/exam-catalogue.json', lambda route: route.fulfill(content_type='application/json', body=json.dumps({'version':1,'questions':[]})))
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
                          board='Edexcel', bank='exam', examType='bronze', difficulty='easy', skillIds=['smq-1.01', 'smq-1.02'],
                          dataPath='content/practice/pure-year-1/chapter-01.json')
        question = dict(id=descriptor['id'], question='<p>Simplify the expression.</p>', contextHtml='<aside>Referenced model: x squared.</aside>',
                        steps=[] if incomplete else ['<p>Apply the index law.</p>'],
                        hints=['<p>Remember that powers add.</p>'])
        self.page.route('**/practice-catalogue.json', lambda route: route.fulfill(
            content_type='application/json', body=json.dumps({'version': 1, 'questions': [descriptor]})))
        self.page.route('**/content/practice/pure-year-1/chapter-01.json', lambda route: route.fulfill(
            content_type='application/json', body=json.dumps({'schemaVersion':1,'questions':[question]})))
        self.page.reload()
        self.page.wait_for_function("!document.querySelector('#papers-source-practice').disabled")
        return descriptor, question

    def test_practice_source_union_hints_and_restore(self):
        descriptor, question = self.practice_fixture()
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '1 questions in the selection')
        self.page.locator('#papers-topics input[value="maths-a-level/maths-pure-year-1/1"]').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '1 questions in the selection')
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
        self.page.locator('#papers-source-practice').check()
        self.page.locator('#papers-source-exam-style').uncheck()
        self.assertEqual(self.selection_ids(), [descriptor['id']])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertTrue(self.page.locator('#papers-source-practice').is_checked())
        self.assertFalse(self.page.locator('#papers-source-exam-style').is_checked())
        self.assertEqual(self.selection_ids(), [descriptor['id']])

    def test_incomplete_practice_solution_keeps_previous_paper(self):
        self.generate(1)
        previous = self.selection_ids()
        self.practice_fixture(incomplete=True)
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').check()
        self.page.locator('#papers-count').fill('1')
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('incomplete content')")
        self.assertEqual(self.selection_ids(), previous)

    def test_wide_practice_table_scrolls_inside_mobile_preview(self):
        descriptor, question = self.practice_fixture()
        question['question'] = '<table class="practice-table"><tr>' + ''.join(
            f'<td>{100000 + n}</td>' for n in range(12)) + '</tr></table>'
        self.page.route('**/content/practice/pure-year-1/chapter-01.json', lambda route: route.fulfill(
            content_type='application/json', body=json.dumps({'schemaVersion': 1, 'questions': [question]})))
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').check()
        self.generate(1)
        self.page.locator('#papers-selected summary').click()
        table = self.page.locator('#papers-selected .math-table')
        table.wait_for(state='visible')
        self.assertEqual(table.locator('td').count(), 12)
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.assertTrue(table.evaluate('n=>n.scrollWidth>n.clientWidth'))
        table.focus()
        table.press('ArrowRight')
        self.page.wait_for_function("document.querySelector('#papers-selected .math-table').scrollLeft > 0")

    def test_source_checkboxes_difficulty_and_empty_pool(self):
        descriptor, _ = self.practice_fixture()
        self.page.locator('#papers-source-practice').uncheck()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '1 questions in the selection')
        self.page.locator('#papers-difficulty').select_option('difficult')
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '0 questions in the selection')
        self.assertTrue(self.page.locator('#papers-generate').is_disabled())
        self.page.locator('#papers-difficulty').select_option('easy')
        self.generate(1)
        self.assertEqual(self.selection_ids(), [descriptor['id']])
        self.page.locator('#papers-source-exam-style').uncheck()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '0 questions in the selection')
        self.assertEqual(self.selection_ids(), [descriptor['id']])
        self.assertTrue(self.page.locator('#papers-generate').is_disabled())
        self.assertFalse(self.page.locator('#papers-print').is_disabled())

    def test_full_pool_regeneration_uses_new_order(self):
        self.page.locator('#papers-course').select_option('further-maths-a-level')
        self.page.locator('#papers-topics input[value="further-maths-a-level/pure-core-1/1"]').check()
        self.page.locator('#papers-order').select_option('selection')
        self.page.evaluate('Math.random=()=>0')
        count = int(self.page.locator('#papers-count').get_attribute('max'))
        self.generate(count)
        first = self.selection_ids()
        self.page.evaluate('Math.random=()=>0.999999')
        self.page.locator('#papers-regenerate').click()
        self.page.wait_for_function("document.querySelector('#papers-cancel').hidden")
        self.assertEqual(set(self.selection_ids()),set(first))
        self.assertNotEqual(self.selection_ids(),first)

    def test_print_options_persist_and_reach_snapshot(self):
        self.generate(2)
        self.page.locator('#papers-condensed').check()
        self.page.locator('#papers-answers').uncheck()
        self.page.locator('#papers-order').select_option('selection')
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertTrue(self.page.locator('#papers-condensed').is_checked())
        self.assertFalse(self.page.locator('#papers-answers').is_checked())
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'selection')
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPrintOptions)')
        self.assertEqual(self.page.evaluate('testPrintOptions'), {'layout':'condensed','includeAnswers':False})

    def test_default_and_migrated_two_per_page_use_one_question_per_page(self):
        self.assertFalse(self.page.get_by_role('checkbox', name='Condensed').is_checked())
        self.assertTrue(self.page.get_by_role('checkbox', name='Include worked solutions at the back').is_checked())
        self.generate(1)
        ids = self.selection_ids()
        self.page.evaluate('''() => {
          const key = 'luisa-papers-v1';
          const saved = JSON.parse(sessionStorage.getItem(key));
          saved.layout = 'two';
          sessionStorage.setItem(key, JSON.stringify(saved));
        }''')
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.selection_ids(), ids)
        self.assertFalse(self.page.get_by_role('checkbox', name='Condensed').is_checked())
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPrintOptions)')
        self.assertEqual(self.page.evaluate('testPrintOptions'), {'layout':'one','includeAnswers':True})
        self.assertEqual(self.page.locator('#papers-answers').evaluate("node=>node.parentElement.nextElementSibling.querySelector('input').id"),
                         'papers-condensed')

    def test_past_exam_loader_marks_timing_and_mixed_selection(self):
        q = dict(id='exam/test-paper/q1', sourceLabel='Source: Test paper · Q1',
                 board='Edexcel', status='checked', marks=7, difficulty='easy',
                 dataPath='content/exams/test-paper.json', paperId='test-paper', paperCode='9MA0/01', session='June 2025',
                 chapterKeys=['maths-a-level/maths-pure-year-1/1'],
                 skillMappings=[dict(courseId='maths-a-level',bookId='maths-pure-year-1',skillId='smq-1.01')])
        self.page.route('**/exam-catalogue.json', lambda route: route.fulfill(
            content_type='application/json',body=json.dumps({'version':1,'questions':[q]})))
        self.page.route('**/content/exams/test-paper.json', lambda route: route.fulfill(
            content_type='application/json',body=json.dumps({'schemaVersion':1,'questions':[
                dict(id=q['id'],question='<p>Evaluate 2 + 3.</p>',steps=['<p>5.</p>'])]})))
        self.page.reload()
        self.page.wait_for_function("!document.querySelector('#papers-source-past-papers').disabled")
        self.page.locator('#papers-source-practice').uncheck()
        self.generate(1)
        self.assertEqual(self.selection_ids(), [q['id']])
        self.assertEqual(self.page.locator('#papers-summary').inner_text(), '1 questions · 7 marks · Suggested practice time: 6 minutes')
        self.page.locator('#papers-source-past-papers').uncheck()
        self.page.locator('#papers-source-practice').check()
        self.page.locator('#papers-browse').click()
        self.page.locator('[data-add]').first.click()
        self.assertIn('7 known marks (1 of 2 questions)',self.page.locator('#papers-summary').inner_text())
        self.assertNotIn('time',self.page.locator('#papers-summary').inner_text())

    def test_all_actual_questions_reference_exclusion_and_qualified_ids(self):
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '6,147 questions in the selection')
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '3,353 questions in the selection')
        self.assertEqual(self.page.locator('#papers-skills').count(), 0)
        self.page.locator('#papers-course').select_option('further-maths-a-level')
        self.page.locator('#papers-book').select_option('further-maths-a-level/pure-core-2')
        self.page.locator('#papers-topics input[value="further-maths-a-level/pure-core-2/6"]').check()
        self.page.locator('#papers-browse').click()
        self.page.locator('[data-add]').first.wait_for()
        self.assertTrue(self.page.locator('[data-add]').evaluate_all(
            'nodes=>nodes.some(n=>n.dataset.add.includes("/pure-core-1/") && n.dataset.add.includes("/1.30/"))'))

    def test_live_catalogues_source_split_paper_filter_and_legacy_restore(self):
        self.page.unroute('**/practice-catalogue.json')
        self.page.unroute('**/exam-catalogue.json')
        gold = 'practice/maths-a-level/maths-mechanics-year-2/ch7/problem-b/qgold'
        self.page.evaluate('''id => sessionStorage.setItem('luisa-papers-v1', JSON.stringify({
          version:2, sources:{practice:false, exam:true}, selected:[id], order:'selection',
          layout:'condensed', includeAnswers:false, topics:['old-topic'], skills:['old-skill']
        }))''', gold)
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.selection_ids(), [gold])
        self.assertIn('reset', self.page.locator('#papers-selection-note').inner_text())
        self.assertIn('15 marks', self.page.locator('#papers-summary').inner_text())
        self.assertFalse(self.page.locator('#papers-source-practice').is_checked())
        self.assertTrue(self.page.locator('#papers-source-exam-style').is_checked())
        self.assertTrue(self.page.locator('#papers-source-past-papers').is_checked())
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '601 questions in the selection')
        self.page.locator('#papers-source-past-papers').uncheck()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '554 questions in the selection')
        self.assertTrue(self.page.locator('#papers-past-paper').is_disabled())
        self.page.locator('#papers-source-exam-style').uncheck()
        self.page.locator('#papers-source-past-papers').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '47 questions in the selection')
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-01-2025-june')
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '16 questions in the selection')
        self.page.locator('#papers-source-practice').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '8,084 questions in the selection')
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.page.locator('#papers-book').select_option('maths-a-level/maths-pure-year-1')
        for number in (2, 7):
            self.page.locator(f'#papers-topics input[value="maths-a-level/maths-pure-year-1/{number}"]').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '3 questions in the selection')
        self.page.locator('#papers-browse').click()
        self.page.wait_for_function("document.querySelectorAll('[data-add]').length === 3")
        browsed = self.page.locator('[data-add]').evaluate_all('nodes=>nodes.map(n=>n.dataset.add)')
        self.assertEqual(self.selection_ids(), [gold])
        self.generate(3)
        self.assertCountEqual(self.selection_ids(), browsed)
        self.page.locator('#papers-order').select_option('topic')
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        snapshot = self.page.evaluate('testPaperSnapshot')
        self.assertEqual([q['printChapter']['id'] for q in snapshot], ['2', '7', '7'])
        question = next(q for q in snapshot if q['id'].endswith('/q4'))
        path = ROOT / 'content/exams/edexcel-9ma0-01-2025-june.json'
        source = next(q for q in json.loads(path.read_text())['questions'] if q['id'] == question['id'])
        self.assertEqual(question['question'], source['question'])

    def test_practice_marks_include_all_labelled_table_parts(self):
        self.page.unroute('**/practice-catalogue.json')
        ident = 'practice/maths-a-level/maths-pure-year-1/ch11/11.3/q7'
        self.page.evaluate('''id => sessionStorage.setItem('luisa-papers-v1',
            JSON.stringify({version:3, selected:[id]}))''', ident)
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.selection_ids(), [ident])
        self.assertIn('6 marks', self.page.locator('#papers-summary').inner_text())
        payload_path = 'content/practice/pure-year-1/chapter-11.json'
        payload = json.loads((ROOT / payload_path).read_text())
        question = next(q for q in payload['questions'] if q['id'] == ident)
        question['question'] = question['question'].replace('<span class="marks">(1 mark)</span>', '')
        self.page.route('**/' + payload_path, lambda route: route.fulfill(json=payload))
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-summary').inner_text(), '1 questions')

    def test_edexcel_filter_excludes_ineligible_saved_questions(self):
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
        self.page.locator('#papers-order').select_option('selection')
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
        book = 'maths-pure-year-1'
        canonical = json.loads((ROOT / 'textbook-catalogue.json').read_text())
        labels = [f"{c['id']}. {c['title']}" for b in canonical['books'] if b['id'] == book for c in b['chapters']]
        self.assertEqual(len(labels), 14)
        self.assertEqual(self.page.locator('#papers-topics label > span').evaluate_all(
            'nodes=>nodes.map(n=>n.firstChild.textContent)'), labels)
        expected = {(q['skill'], q['question']) for q in canonical['questions']
                    if any('maths-a-level/' + t['book'] + '/' + t['chapter'] in topics for t in q['targets'])}
        self.assertEqual(self.page.locator('#filter-title').inner_text(), f'{len(expected):,} questions in the selection')
        self.assertEqual(self.page.locator('#papers-topics input:checked').count(), 2)
        self.generate(12)
        self.assertTrue(all((key.split('/')[-2], int(key.split('/')[-1][1:])) in expected for key in self.selection_ids()))
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
        self.page.locator('#papers-topics input[value="further-maths-a-level/pure-core-1/1"]').check()
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
