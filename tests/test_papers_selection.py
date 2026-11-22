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
        self.assertEqual(self.page.locator('#papers-summary').inner_text(), '1 questions · 7 marks · Time: 8 minutes')
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
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '826 questions in the selection')
        self.page.locator('#papers-source-past-papers').uncheck()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '554 questions in the selection')
        self.assertTrue(self.page.locator('#papers-past-paper').is_disabled())
        self.page.locator('#papers-source-exam-style').uncheck()
        self.page.locator('#papers-source-past-papers').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '272 questions in the selection')
        options = self.page.locator('#papers-past-paper option').evaluate_all('nodes=>nodes.map(n=>[n.value,n.textContent])')
        self.assertEqual(len(options), 28)
        self.assertIn(['edexcel-9ma0-02-2025-june', 'June 2025 Paper 2 (Maths · 9MA0/02)'], options)
        self.assertEqual(options[7:13], [
            ['edexcel-9ma0-31-2024-june', 'June 2024 Paper 3 Statistics (Maths · 9MA0/31)'],
            ['edexcel-9ma0-32-2024-june', 'June 2024 Paper 3 Mechanics (Maths · 9MA0/32)'],
            ['edexcel-9ma0-02-2024-june', 'June 2024 Paper 2 (Maths · 9MA0/02)'],
            ['edexcel-9ma0-01-2024-june', 'June 2024 Paper 1 (Maths · 9MA0/01)'],
            ['edexcel-9fm0-02-2024-june', 'June 2024 Paper 2 (Further Maths · 9FM0/02)'],
            ['edexcel-9fm0-01-2024-june', 'June 2024 Paper 1 (Further Maths · 9FM0/01)']])
        self.assertEqual(options[13:], [
            ['edexcel-9ma0-31-2023-june', 'June 2023 Paper 3 Statistics (Maths · 9MA0/31)'],
            ['edexcel-9ma0-32-2023-june', 'June 2023 Paper 3 Mechanics (Maths · 9MA0/32)'],
            ['edexcel-9ma0-02-2023-june', 'June 2023 Paper 2 (Maths · 9MA0/02)'],
            ['edexcel-9ma0-01-2023-june', 'June 2023 Paper 1 (Maths · 9MA0/01)'],
            ['edexcel-9fm0-02-2023-june', 'June 2023 Paper 2 (Further Maths · 9FM0/02)'],
            ['edexcel-9fm0-01-2023-june', 'June 2023 Paper 1 (Further Maths · 9FM0/01)'],
            # PAP-070: newest exam date first, so the June 2019 Further Maths papers sit between Maths papers.
            ['edexcel-9ma0-31-2019-june', 'June 2019 Paper 3 Statistics (Maths · 9MA0/31)'],
            ['edexcel-9ma0-32-2019-june', 'June 2019 Paper 3 Mechanics (Maths · 9MA0/32)'],
            ['edexcel-9ma0-02-2019-june', 'June 2019 Paper 2 (Maths · 9MA0/02)'],
            ['edexcel-9fm0-02-2019-june', 'June 2019 Paper 2 (Further Maths · 9FM0/02)'],
            ['edexcel-9ma0-01-2019-june', 'June 2019 Paper 1 (Maths · 9MA0/01)'],
            ['edexcel-9fm0-01-2019-june', 'June 2019 Paper 1 (Further Maths · 9FM0/01)'],
            ['edexcel-9ma0-03-2018-june', 'June 2018 Paper 3 (Maths · 9MA0/03)'],
            ['edexcel-9ma0-02-2018-june', 'June 2018 Paper 2 (Maths · 9MA0/02)'],
            ['edexcel-9ma0-01-2018-june', 'June 2018 Paper 1 (Maths · 9MA0/01)']])
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '15 questions in the selection')
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.page.locator('#papers-book').select_option('maths-a-level/maths-pure-year-2')
        self.page.locator('#papers-topics input[value="maths-a-level/maths-pure-year-2/11"]').check()
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '2 questions in the selection')
        self.page.locator('#papers-browse').click()
        self.page.wait_for_function("document.querySelectorAll('[data-add]').length === 2")
        self.assertEqual(self.page.locator('[data-add]').evaluate_all('nodes=>nodes.map(n=>n.dataset.add)'),
                         ['exam/edexcel-9ma0-02-2025-june/q10', 'exam/edexcel-9ma0-02-2025-june/q15'])
        self.page.locator('#papers-topics input[value="maths-a-level/maths-pure-year-2/11"]').uncheck()
        self.page.locator('#papers-course').select_option('')
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

    def test_whole_pure_mathematics_2_paper_in_source_order_survives_reload(self):
        self.page.unroute('**/exam-catalogue.json')
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').uncheck()
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '15 questions in the selection')
        expected = [f'exam/edexcel-9ma0-02-2025-june/q{n}' for n in range(1, 16)]
        self.page.locator('#papers-browse').click()
        for first, count in ((1, 8), (9, 7)):
            self.page.wait_for_function(f"document.querySelectorAll('[data-add]').length === {count} && "
                                        f"document.querySelector('[data-add]').dataset.add.endsWith('/q{first}')")
            for ident in self.page.locator('[data-add]').evaluate_all('nodes=>nodes.map(n=>n.dataset.add)'):
                self.page.locator(f'[data-add="{ident}"]').click()
            if count == 8:
                self.page.locator('#papers-next').click()
        self.page.locator('#papers-order').select_option('selection')
        self.assertEqual(self.selection_ids(), expected)
        summary = self.page.locator('#papers-summary').inner_text()
        self.assertIn('100 marks', summary)
        self.assertIn('Time: 120 minutes', summary)
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        snapshot = self.page.evaluate('testPaperSnapshot')
        self.assertEqual([q['id'] for q in snapshot], expected)
        self.assertEqual([q['marks'] for q in snapshot], [3, 4, 2, 5, 7, 6, 4, 9, 8, 9, 11, 8, 3, 8, 13])
        payload = {q['id']: q for q in json.loads((ROOT / 'content/exams/edexcel-9ma0-02-2025-june.json').read_text())['questions']}
        for item in snapshot:
            self.assertEqual(item['question'], payload[item['id']]['question'])
            self.assertEqual(item['steps'], payload[item['id']]['steps'])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.selection_ids(), expected)
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), 'edexcel-9ma0-02-2025-june')
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'selection')

    def test_june_2018_and_2019_papers_select_only_their_own_questions_PAP_070(self):
        self.page.unroute('**/exam-catalogue.json')
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').uncheck()
        papers = {'edexcel-9ma0-31-2019-june': 5, 'edexcel-9ma0-32-2019-june': 5, 'edexcel-9ma0-02-2019-june': 14,
                  'edexcel-9fm0-02-2019-june': 8, 'edexcel-9ma0-01-2019-june': 14, 'edexcel-9fm0-01-2019-june': 8,
                  'edexcel-9ma0-03-2018-june': 10, 'edexcel-9ma0-02-2018-june': 14, 'edexcel-9ma0-01-2018-june': 14}
        for paper, count in papers.items():
            self.page.locator('#papers-past-paper').select_option(paper)
            self.assertEqual(self.page.locator('#filter-title').inner_text(), f'{count} questions in the selection')
            self.page.locator('#papers-browse').click()
            self.page.wait_for_function(f"document.querySelectorAll('[data-add]').length === {min(count, 8)} && "
                                        f"document.querySelector('[data-add]').dataset.add === 'exam/{paper}/q1'")
            shown = self.page.locator('[data-add]').evaluate_all('nodes=>nodes.map(n=>n.dataset.add)')
            self.assertEqual(shown, [f'exam/{paper}/q{n}' for n in range(1, min(count, 8) + 1)])
        # A whole combined Statistics and Mechanics paper keeps its original numbering and source order.
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-03-2018-june')
        self.generate(10)
        expected = [f'exam/edexcel-9ma0-03-2018-june/q{n}' for n in range(1, 11)]
        self.assertCountEqual(self.selection_ids(), expected)
        self.page.locator('#papers-order').select_option('paper')
        self.assertIn('100 marks', self.page.locator('#papers-summary').inner_text())
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        snapshot = self.page.evaluate('testPaperSnapshot')
        self.assertEqual([q['id'] for q in snapshot], expected)
        self.assertEqual([q['marks'] for q in snapshot], [5, 7, 11, 13, 14, 6, 8, 8, 13, 15])
        payload = {q['id']: q for q in json.loads((ROOT / 'content/exams/edexcel-9ma0-03-2018-june.json').read_text())['questions']}
        for item in snapshot:
            self.assertEqual(item['question'], payload[item['id']]['question'])
            self.assertEqual(item['steps'], payload[item['id']]['steps'])
        # A mixed selection adds a June 2019 Further Maths question and keeps both after reload.
        self.page.locator('#papers-past-paper').select_option('edexcel-9fm0-01-2019-june')
        self.page.locator('#papers-browse').click()
        self.page.wait_for_function("document.querySelector('[data-add]')?.dataset.add === 'exam/edexcel-9fm0-01-2019-june/q1'")
        self.page.locator('[data-add="exam/edexcel-9fm0-01-2019-june/q1"]').click()
        self.assertCountEqual(self.selection_ids(), expected + ['exam/edexcel-9fm0-01-2019-june/q1'])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertCountEqual(self.selection_ids(), expected + ['exam/edexcel-9fm0-01-2019-june/q1'])
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), 'edexcel-9fm0-01-2019-june')

    def test_teacher_exam_paper_uses_builder_selection_and_defaults_PAP_065C(self):
        self.page.unroute('**/papers-print.js')
        self.page.unroute('**/exam-catalogue.json')
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        panel = self.page.locator('#papers-exam')
        self.assertIn('Teachers only', panel.locator('summary').inner_text())
        panel.locator('summary').click()
        self.assertEqual(self.page.locator('#papers-exam-title').input_value(), 'Maths Assessment')
        self.assertRegex(self.page.locator('#papers-exam-month').input_value(), r'^[A-Z][a-z]+ \d{4}$')
        # PAP-067-3: three default paragraphs separated by blank lines, still editable.
        self.assertEqual(self.page.locator('#papers-exam-instructions').input_value(), '\n\n'.join(['Calculators may be used and a formulae booklet is provided. Where specified, answers relying solely on technology will not receive credit.', 'Give exact answers where requested and approximate numerical answers to three significant figures unless otherwise stated.', 'Clearly label all answers, including those on additional paper, with the question number and part.']))
        # PAP-067-8: Date defaults to today (Europe/London) in the template style.
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo('Europe/London'))
        suffix = 'th' if 11 <= now.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(now.day % 10, 'th')
        self.assertEqual(self.page.locator('#papers-exam-date').input_value(), f"{now:%A} {now.day}{suffix} {now:%B}")
        # A stored automatic date (or a v0.66 session's empty date) never goes stale: only a typed or cleared value is kept.
        self.page.evaluate("sessionStorage.setItem('luisa-papers-exam-v1', JSON.stringify({title: 'Maths Assessment', date: 'Friday 20th November'}))")
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        self.assertEqual(self.page.locator('#papers-exam-date').input_value(), f"{now:%A} {now.day}{suffix} {now:%B}")
        self.page.evaluate("sessionStorage.removeItem('luisa-papers-exam-v1')")
        panel.locator('summary').click()
        # PAP-067-2: one print choice, Questions only by default.
        radios = self.page.locator('input[name="papers-exam-content"]')
        self.assertEqual(radios.evaluate_all('ns=>ns.map(n=>[n.value,n.parentElement.textContent.trim(),n.checked,n.type])'),
                         [['questions', 'Questions only', True, 'radio'], ['scheme', 'Mark scheme only', False, 'radio'], ['both', 'Questions and mark scheme', False, 'radio']])
        # PAP-067-4/5: helper texts removed.
        text = panel.inner_text()
        for gone in ('Prints the paper above as a lined exam paper', 'no solutions', 'is added automatically when any question comes from Mechanics', 'g = 9.8'):
            self.assertNotIn(gone, text)
        self.assertTrue(self.page.locator('#papers-exam-print').is_disabled())
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').uncheck()
        # PAP-067-7: no g status text without a mechanics question.
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-31-2024-june')
        self.page.locator('#papers-browse').click()
        self.page.wait_for_function("document.querySelectorAll('[data-add]').length >= 1")
        self.page.locator('[data-add="exam/edexcel-9ma0-31-2024-june/q1"]').click()
        self.assertNotIn('g = 9.8', self.page.locator('#papers-exam-summary').inner_text())
        self.assertNotIn('g = 9.8', panel.inner_text())
        self.page.locator('[data-remove]').first.click()
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-32-2024-june')
        self.page.wait_for_function("document.querySelectorAll('[data-add]').length === 6")
        for n in (1, 2):
            self.page.locator(f'[data-add="exam/edexcel-9ma0-32-2024-june/q{n}"]').click()
        self.page.locator('#papers-past-paper').select_option('edexcel-9fm0-01-2024-june')
        self.page.wait_for_function("document.querySelectorAll('[data-add]').length === 8")
        self.page.locator('[data-add="exam/edexcel-9fm0-01-2024-june/q1"]').click()
        self.page.locator('#papers-order').select_option('selection')
        self.assertEqual(self.page.locator('#papers-summary').inner_text(), '3 questions · 20 marks · Time: 24 minutes')
        # PAP-067-7: with a mechanics question the status still has no g text.
        self.assertEqual(self.page.locator('#papers-exam-summary').inner_text(), '3 questions · 20 marks · Time: 24 minutes (+6 minutes extra time)')
        self.assertNotIn('g = 9.8', panel.inner_text())
        # PAP-066-2/3: no course map field and no Regenerate control.
        self.assertEqual(self.page.locator('#papers-exam-map, #papers-exam-map-reset').count(), 0)
        self.assertNotIn('course map', panel.inner_text().lower())
        self.page.locator('#papers-exam-year').fill('L6')
        self.page.locator('#papers-exam-date').fill('Friday 20th November P4 & P5')
        self.page.locator('input[name="papers-exam-content"][value="both"]').check()
        self.assertTrue(self.page.locator('#papers-exam-print').is_enabled())
        with self.page.expect_popup() as event:
            self.page.locator('#papers-exam-print').click()
        preview = event.value
        preview.wait_for_function("document.querySelector('.print-status')?.textContent.includes('A4 pages')", timeout=60000)
        # The chosen print option reaches the paper: the scheme follows the questions.
        self.assertEqual(preview.locator('.exam-scheme').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]'),
                         ['exam/edexcel-9ma0-32-2024-june/q1', 'exam/edexcel-9ma0-32-2024-june/q2', 'exam/edexcel-9fm0-01-2024-june/q1'])
        self.assertEqual(preview.locator('.exam-date sup').all_inner_texts(), ['th'])
        self.assertEqual(preview.locator('.exam-title').inner_text(), 'L6 Maths Assessment')
        self.assertEqual(preview.locator('.exam-page .exam-question').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]'),
                         ['exam/edexcel-9ma0-32-2024-june/q1', 'exam/edexcel-9ma0-32-2024-june/q2', 'exam/edexcel-9fm0-01-2024-june/q1'])
        self.assertEqual(preview.locator('.paper-total').inner_text(), 'TOTAL FOR PAPER IS 20 MARKS')
        self.assertEqual(preview.locator('.exam-gravity').count(), 1)
        preview.close()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('Exam paper and mark scheme ready')")
        # Front-page fields, the print option and the selection are kept for the session.
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-exam-year').input_value(), 'L6')
        self.assertEqual(self.page.locator('#papers-exam-date').input_value(), 'Friday 20th November P4 & P5')
        self.assertTrue(self.page.locator('input[name="papers-exam-content"][value="both"]').is_checked())
        # The Date field can be cleared; it stays empty and prints no date line.
        self.page.locator('#papers-exam summary').click()
        self.page.locator('#papers-exam-date').fill('')
        self.page.locator('input[name="papers-exam-content"][value="scheme"]').check()
        with self.page.expect_popup() as event:
            self.page.locator('#papers-exam-print').click()
        preview = event.value
        preview.wait_for_function("document.querySelector('.print-status')?.textContent.includes('A4 pages')", timeout=60000)
        self.assertEqual(preview.locator('.exam-front-page, .exam-page, .exam-date').count(), 0)
        self.assertGreater(preview.locator('.exam-scheme-page').count(), 0)
        preview.close()
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-exam-date').input_value(), '')
        self.assertEqual(self.selection_ids(), ['exam/edexcel-9ma0-32-2024-june/q1', 'exam/edexcel-9ma0-32-2024-june/q2', 'exam/edexcel-9fm0-01-2024-june/q1'])

    def exam_summary_minutes(self):
        import re
        text = self.page.locator('#papers-exam-summary').inner_text()
        match = re.search(r'(\d+) marks · Time: (\d+) minutes \(\+(\d+) minutes extra time\)', text)
        self.assertTrue(match, text)
        return tuple(map(int, match.groups()))

    def timed(self, preset=None, minutes=None):
        if preset: self.page.locator(f'[data-exam-preset="{preset}"]').click()
        else: self.page.locator('#papers-exam-minutes').fill(str(minutes))
        self.page.locator('#papers-exam-generate').click()
        self.page.wait_for_function("(() => { const r = document.querySelector('#papers-exam-target-report'); return !r.hidden && !r.textContent.startsWith('Loading'); })()", timeout=60000)
        return self.page.locator('#papers-exam-target-report').inner_text()

    def test_timed_exam_paper_from_chosen_topics_PAP_066(self):
        self.page.unroute('**/papers-print.js')
        self.page.unroute('**/exam-catalogue.json')
        self.page.unroute('**/practice-catalogue.json')
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        self.page.locator('#papers-exam summary').click()
        self.assertEqual(self.page.locator('[data-exam-preset]').all_inner_texts(), ['1 period · 32 minutes (+8)', '2 periods · 60 minutes (+15)'])
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').uncheck()
        for preset in (32, 60):
            with self.subTest(preset=preset):
                report = self.timed(preset)
                self.assertEqual(self.page.locator('#papers-exam-minutes').input_value(), str(preset))
                self.assertIn(f'Target {preset} minutes met', report)
                marks, minutes, extra = self.exam_summary_minutes()
                self.assertLessEqual(abs(minutes - preset), 2)  # PAP-067-1
                # PAP-067-6/7: no "without marks" note and no g status text after generating.
                self.assertNotIn('without marks', report)
                self.assertNotIn('left out', report)
                self.assertNotIn('g = 9.8', self.page.locator('#papers-exam').inner_text())
                # Questions without marks are still excluded from timed generation.
                kinds = self.page.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(r => [r.sourceKind, Number.isInteger(r.marks) && r.marks > 0])')
                self.assertTrue(all(kind in ('practice-booklet', 'past-exam') and marked for kind, marked in kinds), kinds)
                self.assertEqual((minutes, extra), (marks * 6 // 5, int(minutes * 0.25 + 0.5)))
                self.assertEqual(self.page.locator('#papers-order').input_value(), 'selection')
                self.assertTrue(self.page.locator('#papers-exam-order-warning').is_hidden())
                snapshot = self.page.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(r => r.difficulty)')
                self.assertEqual((snapshot[0], snapshot[-1]), ('easy', 'difficult'))
                self.assertIn(f'{marks} marks · Time: {minutes} minutes', self.page.locator('#papers-summary').inner_text())
        # Manual edits: reorder and remove update the time live; a rule-breaking order is flagged.
        ids = self.selection_ids()
        self.page.locator('#papers-selected > li').last.locator('[data-exam-move="-1"]').click()
        self.assertEqual(self.selection_ids(), ids[:-2] + [ids[-1], ids[-2]])
        problems = self.page.evaluate('LUISA_PAPERS_EXAM.orderProblems(LUISA_PAPERS_BUILDER.snapshot())')
        self.assertEqual(self.page.locator('#papers-exam-order-warning').is_visible(), bool(problems))
        self.page.locator('#papers-selected > li').first.locator('[data-exam-move="1"]').click()
        self.page.locator('#papers-selected > li').first.locator('[data-exam-move="1"]').click()
        self.page.locator('#papers-selected > li').first.locator('[data-exam-move="1"]').click()
        if self.page.evaluate('LUISA_PAPERS_EXAM.orderProblems(LUISA_PAPERS_BUILDER.snapshot()).length'):
            self.assertIn('does not follow the exam difficulty order', self.page.locator('#papers-exam-order-warning').inner_text())
        self.page.locator('#papers-exam-order').click()
        self.assertTrue(self.page.locator('#papers-exam-order-warning').is_hidden())
        before = self.exam_summary_minutes()
        self.page.locator('[data-remove]').first.click()
        self.assertLess(self.exam_summary_minutes()[0], before[0])
        # While a timed paper loads, the builder is locked; a busy builder is reported, never silently ignored.
        locked = self.page.evaluate("""async () => { let during; const r = await LUISA_PAPERS_BUILDER.exclusive(async () => { during = [LUISA_PAPERS_BUILDER.busy(), document.querySelector('#papers-generate').disabled, document.querySelector('[data-remove]').disabled, await LUISA_PAPERS_BUILDER.exclusive(async () => 'nested')]; return 'done'; }); return [r, during, LUISA_PAPERS_BUILDER.busy()]; }""")
        self.assertEqual(locked, ['done', [True, True, True, None], False])
        # A target the chosen topics cannot reach is reported with the closest paper, which the teacher may accept.
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-31-2024-june')
        report = self.timed(minutes=120)
        self.assertIn('Target 120 minutes cannot be met exactly', report)
        self.assertIn('which is only 60 minutes', report)
        self.assertTrue(self.page.locator('#papers-exam-accept').is_visible())
        self.page.locator('#papers-exam-accept').click()
        self.assertEqual(self.exam_summary_minutes()[:2], (50, 60))
        self.assertTrue(self.page.locator('#papers-exam-accept').is_hidden())
        # Realistic Practice Booklet exam-style topics (marks read from the questions) also meet 32 minutes.
        self.page.locator('#papers-past-paper').select_option('')
        self.page.locator('#papers-source-past-papers').uncheck()
        self.page.locator('#papers-source-exam-style').check()
        report = self.timed(32)
        self.assertIn('Target 32 minutes met:', report)
        self.assertLessEqual(abs(self.exam_summary_minutes()[1] - 32), 2)
        # Practice questions carry no difficulty labels, so the time is met and the missing bands are reported.
        self.page.locator('#papers-source-practice').check()
        self.page.locator('#papers-source-exam-style').uncheck()
        # Practice questions include thousands of skill questions without marks: they are excluded, and no note is shown.
        self.assertGreater(self.page.evaluate("LUISA_PAPERS_BUILDER.pool().filter(r => !['practice-booklet', 'past-exam'].includes(r.sourceKind)).length"), 1000)
        report = self.timed(32)
        self.assertNotIn('without marks', report)
        self.assertNotIn('were left out', report)
        self.assertIn('Target 32 minutes met, but not every exam rule.', report)
        self.assertIn('0 easy questions (0 marks) and 0 difficult questions', report)
        self.page.locator('#papers-exam-accept').click()
        self.assertLessEqual(abs(self.exam_summary_minutes()[1] - 32), 2)
        kinds = self.page.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(r => [r.sourceKind, Number.isInteger(r.marks) && r.marks > 0])')
        self.assertTrue(all(kind in ('practice-booklet', 'past-exam') and marked for kind, marked in kinds), kinds)
        self.assertTrue(self.page.locator('#papers-exam-order-warning').is_visible())
        # The target survives a reload with the other exam fields.
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-exam-minutes').input_value(), '32')

    def test_in_paper_order_only_for_one_past_paper_and_survives_reload(self):
        self.page.unroute('**/exam-catalogue.json')
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        order_options = lambda: self.page.locator('#papers-order option').evaluate_all('nodes=>nodes.map(n=>[n.value,n.textContent])')
        self.assertEqual(order_options(), [['topic', 'Group by topic'], ['selection', 'As selected']])
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-source-exam-style').uncheck()
        p1, p2 = 'exam/edexcel-9ma0-01-2025-june/', 'exam/edexcel-9ma0-02-2025-june/'
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
        self.assertEqual(order_options(), [['topic', 'Group by topic'], ['selection', 'As selected'], ['paper', 'In paper order']])
        self.page.locator('#papers-order').select_option('selection')
        self.generate(15)
        shuffled = self.selection_ids()
        expected = [f'{p2}q{n}' for n in range(1, 16)]
        self.assertCountEqual(shuffled, expected)
        # Add one Paper 1 question after a randomly ordered Paper 2.
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-01-2025-june')
        self.page.locator('#papers-browse').click()
        self.page.wait_for_function(f"document.querySelector('[data-add=\"{p1}q3\"]')")
        self.page.locator(f'[data-add="{p1}q3"]').click()
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
        self.assertEqual(self.selection_ids(), shuffled + [f'{p1}q3'])
        self.page.locator('#papers-order').select_option('paper')
        self.assertEqual(self.selection_ids(), expected + [f'{p1}q3'])
        self.page.locator('#papers-print').click()
        self.page.wait_for_function('Boolean(window.testPaperSnapshot)')
        snapshot = self.page.evaluate('testPaperSnapshot')
        self.assertEqual([q['id'] for q in snapshot], expected + [f'{p1}q3'])
        self.assertEqual([q['marks'] for q in snapshot][:15], [3, 4, 2, 5, 7, 6, 4, 9, 8, 9, 11, 8, 3, 8, 13])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'paper')
        self.assertEqual(self.selection_ids(), expected + [f'{p1}q3'])
        # Another single paper puts its own questions first; the rest keep the order they were added.
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-01-2025-june')
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'paper')
        self.assertEqual(self.selection_ids(), [f'{p1}q3'] + shuffled)
        self.page.locator('#papers-order').select_option('selection')
        self.assertEqual(self.selection_ids(), shuffled + [f'{p1}q3'])
        self.page.locator('#papers-order').select_option('paper')
        # All past papers removes the option and returns to the default order.
        self.page.locator('#papers-past-paper').select_option('')
        self.assertEqual(order_options(), [['topic', 'Group by topic'], ['selection', 'As selected']])
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'topic')
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#papers-status').textContent.includes('restored')")
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'topic')
        self.assertEqual(len(order_options()), 2)

    def paper_options(self):
        return self.page.locator('#papers-past-paper option').evaluate_all('nodes=>nodes.map(n=>n.value)')

    def select_style(self, ident):
        return self.page.locator(ident).evaluate("""node => { const s = getComputedStyle(node);
          return {active: node.classList.contains('filter-active'), disabled: node.disabled, border: s.borderTopColor,
                  background: s.backgroundColor, color: s.color, weight: s.fontWeight, shadow: s.boxShadow}; }""")

    @staticmethod
    def contrast(a, b):
        def luminance(css):
            channels = [int(v) / 255 for v in css[css.index('(') + 1:css.index(')')].split(',')[:3]]
            lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
            return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
        hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    def test_paper_dropdown_follows_course_book_tickbox_and_active_style_PAP_068(self):
        self.page.unroute('**/practice-catalogue.json')
        self.page.unroute('**/exam-catalogue.json')
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28")
        filters = ['#papers-past-paper', '#papers-difficulty', '#papers-course', '#papers-book']
        everything = self.paper_options()
        self.assertEqual(len(everything), 28)
        plain = {ident: self.select_style(ident) for ident in filters}
        for ident in filters:
            self.assertFalse(plain[ident]['active'], ident)
            self.assertFalse(plain[ident]['disabled'], ident)
            self.assertEqual(plain[ident]['background'], 'rgb(255, 255, 255)', ident)
        # PAP-068-1: Maths A level hides every Further Maths paper; All shows all papers again.
        self.page.locator('#papers-course').select_option('maths-a-level')
        maths = self.paper_options()
        self.assertEqual(len(maths), 20)
        self.assertFalse([value for value in maths if '9fm0' in value])
        self.assertIn('edexcel-9ma0-31-2024-june', maths)
        # PAP-068-2: the active style is clearly different, readable and not the disabled look.
        active = self.select_style('#papers-course')
        self.assertTrue(active['active'])
        self.assertEqual(active['border'], 'rgb(21, 59, 87)')
        self.assertEqual(active['background'], 'rgb(237, 243, 247)')
        self.assertNotEqual(active['background'], plain['#papers-course']['background'])
        self.assertGreaterEqual(self.contrast(active['color'], active['background']), 4.5)
        self.assertGreaterEqual(self.contrast(active['border'], 'rgb(255, 255, 255)'), 3)
        self.assertFalse(self.select_style('#papers-book')['active'])
        self.page.locator('#papers-book').select_option('maths-a-level/maths-mechanics-year-2')
        self.assertEqual(self.paper_options(), ['', 'edexcel-9ma0-32-2025-june', 'edexcel-9ma0-32-2024-june', 'edexcel-9ma0-32-2023-june',
                                                'edexcel-9ma0-32-2019-june', 'edexcel-9ma0-03-2018-june'])
        self.assertTrue(self.select_style('#papers-book')['active'])
        self.page.locator('#papers-past-paper').select_option('edexcel-9ma0-32-2024-june')
        self.assertTrue(self.select_style('#papers-past-paper')['active'])
        self.assertIn(['paper', 'In paper order'], self.page.locator('#papers-order option').evaluate_all('n=>n.map(o=>[o.value,o.textContent])'))
        # A chosen paper with no question in the new book is reset to All.
        self.page.locator('#papers-book').select_option('maths-a-level/maths-pure-year-2')
        self.assertEqual(self.paper_options(), ['', 'edexcel-9ma0-31-2025-june', 'edexcel-9ma0-02-2025-june', 'edexcel-9ma0-01-2025-june',
                                                'edexcel-9ma0-02-2024-june', 'edexcel-9ma0-01-2024-june',
                                                'edexcel-9ma0-31-2023-june', 'edexcel-9ma0-02-2023-june', 'edexcel-9ma0-01-2023-june',
                                                'edexcel-9ma0-02-2019-june', 'edexcel-9ma0-01-2019-june', 'edexcel-9ma0-02-2018-june', 'edexcel-9ma0-01-2018-june'])
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), '')
        self.assertFalse(self.select_style('#papers-past-paper')['active'])
        self.assertNotIn('paper', self.page.locator('#papers-order option').evaluate_all('n=>n.map(o=>o.value)'))
        self.page.locator('#papers-book').select_option('')
        self.assertFalse(self.select_style('#papers-book')['active'])
        self.assertEqual(len(self.paper_options()), 20)
        self.page.locator('#papers-course').select_option('further-maths-a-level')
        self.assertEqual(self.paper_options(), ['', 'edexcel-9fm0-02-2025-june', 'edexcel-9fm0-01-2025-june',
                                                'edexcel-9fm0-02-2024-june', 'edexcel-9fm0-01-2024-june',
                                                'edexcel-9fm0-02-2023-june', 'edexcel-9fm0-01-2023-june',
                                                'edexcel-9fm0-02-2019-june', 'edexcel-9fm0-01-2019-june'])
        self.page.locator('#papers-difficulty').select_option('medium')
        self.assertTrue(self.select_style('#papers-difficulty')['active'])
        self.page.locator('#papers-difficulty').select_option('')
        self.assertFalse(self.select_style('#papers-difficulty')['active'])
        self.page.locator('#papers-course').select_option('')
        self.assertEqual(self.paper_options(), everything)
        for ident in filters:
            self.assertEqual(self.select_style(ident), plain[ident], ident)
        # PAP-068-3: unticking resets a chosen paper, disables and greys the dropdown, and it filters nothing.
        self.page.locator('#papers-source-practice').uncheck()
        self.page.locator('#papers-past-paper').select_option('edexcel-9fm0-01-2024-june')
        self.page.locator('#papers-source-past-papers').uncheck()
        grey = self.select_style('#papers-past-paper')
        self.assertTrue(grey['disabled'])
        self.assertFalse(grey['active'])
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), '')
        self.assertEqual(grey['background'], 'rgb(236, 238, 239)')
        self.assertEqual(grey['color'], 'rgb(95, 107, 117)')
        self.assertNotEqual(grey['background'], active['background'])
        self.assertNotEqual(grey['border'], active['border'])
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '554 questions in the selection')
        self.page.evaluate("""() => { const s = document.querySelector('#papers-past-paper');
          s.append(new Option('x', 'edexcel-9ma0-01-2025-june')); s.value = 'edexcel-9ma0-01-2025-june'; }""")
        self.page.locator('#papers-difficulty').select_option('medium')
        self.page.locator('#papers-difficulty').select_option('')
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '554 questions in the selection')
        self.assertNotIn('paper', self.page.locator('#papers-order option').evaluate_all('n=>n.map(o=>o.value)'))
        self.page.locator('#papers-source-past-papers').check()
        self.assertFalse(self.page.locator('#papers-past-paper').is_disabled())
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), '')
        self.assertEqual(self.paper_options(), everything)
        self.assertEqual(self.page.locator('#filter-title').inner_text(), '826 questions in the selection')
        # Restore: a paper saved with the tickbox unticked comes back on All and disabled.
        saved = {'version': 3, 'sources': {'practice': False, 'exam-style': True, 'past-papers': False},
                 'pastPaper': 'edexcel-9fm0-01-2024-june', 'selected': [], 'selectionOrder': [], 'course': '', 'book': '', 'chapters': []}
        self.page.evaluate("s => sessionStorage.setItem('luisa-papers-v1', JSON.stringify(s))", saved)
        self.page.reload()
        self.page.wait_for_function("document.querySelectorAll('#papers-past-paper option').length === 28 && !document.querySelector('#papers-course').disabled")
        restored = self.select_style('#papers-past-paper')
        self.assertTrue(restored['disabled'])
        self.assertFalse(restored['active'])
        self.assertEqual(restored['background'], 'rgb(236, 238, 239)')
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), '')
        # A ticked saved paper inside the saved course is restored with the active style on every chosen filter.
        saved.update(sources={'practice': False, 'exam-style': False, 'past-papers': True}, course='maths-a-level',
                     difficulty='easy', pastPaper='edexcel-9ma0-01-2025-june', order='paper')
        self.page.evaluate("s => sessionStorage.setItem('luisa-papers-v1', JSON.stringify(s))", saved)
        self.page.reload()
        self.page.wait_for_function("!document.querySelector('#papers-course').disabled")
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), 'edexcel-9ma0-01-2025-june')
        self.assertEqual(self.page.locator('#papers-order').input_value(), 'paper')
        self.assertEqual(len(self.paper_options()), 20)
        for ident in ('#papers-past-paper', '#papers-difficulty', '#papers-course'):
            self.assertTrue(self.select_style(ident)['active'], ident)
        self.assertFalse(self.select_style('#papers-book')['active'])
        # A saved paper outside the saved course is reset to All.
        saved.update(pastPaper='edexcel-9fm0-01-2024-june', order='topic')
        self.page.evaluate("s => sessionStorage.setItem('luisa-papers-v1', JSON.stringify(s))", saved)
        self.page.reload()
        self.page.wait_for_function("!document.querySelector('#papers-course').disabled")
        self.assertEqual(self.page.locator('#papers-past-paper').input_value(), '')
        self.assertFalse(self.select_style('#papers-past-paper')['active'])

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
