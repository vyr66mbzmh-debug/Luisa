"""PAP-091/PAP-092/NAV-091 browser checks on the owner edition source.

Uses one Chromium worker and a local static server. Printing is stubbed where the
measured layout is not under test; tests/papers_print_browser.py covers pagination.
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
WORKED_ONLY = 'practice/maths-a-level/maths-mechanics-year-1/ch10/10.2/q7'
CHAPTER = 'maths-a-level/maths-mechanics-year-1/10'


class Server(ThreadingHTTPServer):
    request_queue_size = 128


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@unittest.skipUnless(sync_playwright, 'Playwright is required for timed paper checks')
class TimedPapers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel=os.environ.get('LUISA_BROWSER_CHANNEL') or None)
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(service_workers='block')
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.open_papers()

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open_papers(self, page=None):
        page = page or self.page
        page.goto(self.base + 'papers.html')
        page.wait_for_function("!document.querySelector('#papers-generate').disabled && !document.querySelector('#papers-reset').disabled", timeout=90000)

    def time_mode(self):
        self.page.locator('label.mode-choice:has-text("By time")').click()

    def only(self, sources, chapter=None, difficulty=''):
        for source in ('practice', 'exam-style', 'madas', 'past-papers', 'old-spec'):
            self.page.locator('#papers-source-' + source).set_checked(source in sources)
        self.page.locator('#papers-difficulty').select_option(difficulty)
        if chapter:
            self.page.locator(f'#papers-topics input[value="{chapter}"]').check()

    def generate(self):
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function("(() => { const r = document.querySelector('#papers-time-report'); return !r.hidden && !/^Checking/.test(r.textContent); })()", timeout=180000)
        return self.page.locator('#papers-time-report').inner_text()

    def paper(self):
        return self.page.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(q => [q.id, q.marks])')

    def test_marks_formula_presets_and_verified_layouts(self):
        values = self.page.evaluate("""() => ({
          ten: LUISA_PAPERS_PRINT.paperMinutes(10), fives: LUISA_PAPERS_PRINT.paperMinutes(5 + 5),
          exact: LUISA_PAPERS_TIMING.presets.map(m => LUISA_PAPERS_TIMING.targetMarks(m)[0]),
          presets: [...document.querySelectorAll('[data-minutes]')].map(b => b.dataset.minutes)})""")
        self.assertEqual((values['ten'], values['fives']), (12, 12))
        self.assertEqual(values['exact'], [25, 38, 50, 75, 100])
        self.assertEqual(values['presets'], ['30', '45', '60', '90', '120'])
        cases = {
            # The two verified Pearson layouts.
            'combined': '<ol type="a"><li>A <span class="marks">(3 marks)</span></li><li>B<ol type="i"><li>i</li><li>ii <span class="marks">(4 marks)</span></li></ol></li></ol>',
            'prose': 'Intro <ol type="a"><li>A <span class="marks">(3 marks)</span></li></ol> The force is removed. <span class="marks">(2 marks)</span>\n<ol type="a"><li>B</li><li>C <span class="marks">(3 marks)</span></li></ol>',
            # Incomplete or ambiguous allocations are never summed.
            'first-only': '<ol type="a"><li>A<ol type="i"><li>i <span class="marks">(2 marks)</span></li><li>ii</li></ol></li></ol>',
            'missing-part': '<ol type="a"><li>A <span class="marks">(3 marks)</span></li><li>B</li></ol>',
            'parent-and-child': '<ol type="a"><li>A <span class="marks">(5 marks)</span><ol type="i"><li>i <span class="marks">(2 marks)</span></li><li>ii <span class="marks">(3 marks)</span></li></ol></li></ol>',
            'label-only': '<span class="practice-tag">E/P</span> Show that x = 2.',
        }
        totals = self.page.evaluate('cases => Object.fromEntries(Object.entries(cases).map(([k, h]) => [k, LUISA_PAPERS_BUILDER.practiceMarks(h) ?? null]))', cases)
        self.assertEqual(totals, {'combined': 7, 'prose': 8, 'first-only': None, 'missing-part': None, 'parent-and-child': None, 'label-only': None})

    def test_mode_switch_keyboard_presets_and_custom_target(self):
        self.assertTrue(self.page.locator('input[name="papers-generate-mode"][value="count"]').is_checked())
        self.assertEqual(self.page.locator('#generate-title').inner_text(), 'Generate a paper')
        self.assertTrue(self.page.locator('#papers-time-fields').is_hidden())
        self.page.locator('input[name="papers-generate-mode"][value="count"]').focus()
        self.page.keyboard.press('ArrowRight')
        self.assertTrue(self.page.locator('input[name="papers-generate-mode"][value="time"]').is_checked())
        self.assertEqual(self.page.locator('#papers-minutes').input_value(), '30')
        self.assertEqual(self.page.locator('[aria-pressed="true"][data-minutes]').inner_text(), '30 min')
        self.assertEqual(self.page.locator('#papers-generate').inner_text(), 'Generate timed paper')
        self.assertEqual(self.page.get_by_label('Custom minutes').count(), 1)
        self.page.locator('[data-minutes="90"]').focus()
        self.page.keyboard.press('Enter')
        self.assertEqual(self.page.locator('#papers-minutes').input_value(), '90')
        self.page.locator('#papers-minutes').fill('37')
        self.assertEqual(self.page.locator('[aria-pressed="true"][data-minutes]').count(), 0)
        self.page.locator('#papers-minutes').fill('601')
        self.assertIn('2 to 600', self.generate())
        # Each preset and a custom target produce a paper within ±2 minutes, in its generated order.
        self.only({'practice', 'exam-style', 'past-papers'})
        for minutes in ('30', '45', '60', '90', '120', '37'):
            if minutes == '37': self.page.locator('#papers-minutes').fill(minutes)
            else: self.page.locator(f'[data-minutes="{minutes}"]').click()
            report = self.generate()
            marks = sum(m for _, m in self.paper())
            self.assertLessEqual(abs(int(marks * 6 / 5) - int(minutes)), 2, report)
            self.assertIn(f'{marks} marks · estimated time {int(marks * 6 / 5)} minutes', report)
            self.assertEqual(self.page.locator('#papers-order').input_value(), 'selection')
            self.assertIn(f'Time: {int(marks * 6 / 5)} minutes', self.page.locator('#papers-summary').inner_text())
        # Count mode still works after switching back.
        self.page.locator('label.mode-choice:has-text("By number of questions")').click()
        self.page.locator('#papers-count').fill('4')
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function("LUISA_PAPERS_BUILDER.snapshot().length === 4")
        self.assertTrue(self.page.locator('#papers-time-report').is_hidden())

    def test_worked_only_pearson_question_is_student_eligible_but_not_exam(self):
        self.time_mode()
        self.only({'practice'}, CHAPTER)
        self.page.locator('#papers-minutes').fill('10')
        self.generate()
        rows = self.paper()
        self.assertTrue(rows and all(isinstance(m, int) and m > 0 for _, m in rows))
        self.assertLessEqual(abs(int(sum(m for _, m in rows) * 6 / 5) - 10), 2)
        verdict = self.page.evaluate("""async id => {
          const [row] = await LUISA_PAPERS_BUILDER.load(LUISA_PAPERS_BUILDER.pool().filter(q => q.id === id));
          return [row.marks, row.markScheme, LUISA_PAPERS_EXAM.hasMarkScheme(row), (row.markSchemeSteps || []).length, row.steps.length > 0];
        }""", WORKED_ONLY)
        self.assertEqual(verdict, [8, 'worked', False, 0, True])
        # The teacher exam generator never uses it: its pool is questions with a scheme.
        self.page.locator('#papers-exam > summary').click()
        self.page.wait_for_function("LUISA_PAPERS_BUILDER.mode() === 'exam'")
        self.assertRegex(self.page.locator('#papers-exam-eligible').inner_text(), r'^0 of [\d,]+ questions .* mark scheme')
        self.assertTrue(self.page.locator('#papers-exam-generate').is_disabled())
        # The exam browser and generators no longer offer it.
        self.assertNotIn(WORKED_ONLY, self.page.evaluate("LUISA_PAPERS_BUILDER.snapshot().map(q => q.id)"))
        # Its exam draft omits the worked-only question; the practice paper keeps it.
        self.page.locator('#papers-exam > summary').click()
        self.page.wait_for_function("LUISA_PAPERS_BUILDER.mode() === 'practice'")
        self.assertEqual(self.paper(), rows)

    def test_easy_only_offers_alternative_and_changing_filters_withdraws_it(self):
        self.time_mode()
        self.only({'exam-style'}, 'maths-a-level/maths-pure-year-2/8', 'easy')
        self.page.locator('[data-minutes="120"]').click()
        report = self.generate()
        offer = self.page.locator('#papers-time-accept')
        self.assertTrue(offer.is_visible(), report)
        self.assertRegex(offer.inner_text(), r'^Use \d+-minute paper$')
        self.assertIn('unchanged', report)
        self.assertEqual(self.paper(), [])
        # Changing the filters (or the target) withdraws the offer.
        self.page.locator('#papers-difficulty').select_option('')
        self.assertTrue(offer.is_hidden())
        self.page.locator('#papers-difficulty').select_option('easy')
        self.generate()
        minutes = int(offer.inner_text().split()[1].split('-')[0])
        offer.click()
        self.page.wait_for_function("document.querySelector('#papers-time-accept').hidden && /Using the/.test(document.querySelector('#papers-time-report').textContent)")
        self.assertEqual(int(sum(m for _, m in self.paper()) * 6 / 5), minutes)
        # An Easy-only paper that meets its time is a valid student result.
        self.page.locator('#papers-minutes').fill(str(minutes))
        report = self.generate()
        self.assertIn(f'Target {minutes} minutes', report)
        self.assertTrue(offer.is_hidden())
        self.assertEqual(set(self.page.evaluate("LUISA_PAPERS_BUILDER.snapshot().map(q => q.difficulty)")), {'easy'})

    def test_no_known_totals_and_cancelling_by_changing_filters(self):
        self.time_mode()
        self.page.route('**/content/practice/**', lambda route: route.abort())
        self.only({'practice'}, 'maths-a-level/maths-pure-year-1/2')
        self.assertIn('no questions with a known mark total', self.generate().lower())
        self.page.unroute('**/content/practice/**')
        # A by-count paper, then a timed run whose Pearson content is held while the filters change.
        self.page.locator('label.mode-choice:has-text("By number of questions")').click()
        self.only({'past-papers'})
        self.page.locator('#papers-count').fill('3')
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function("LUISA_PAPERS_BUILDER.snapshot().length === 3")
        kept = self.paper()
        held = []
        self.page.route('**/content/practice/**', lambda route: held.append(route))
        self.time_mode()
        self.only({'practice', 'past-papers'})
        self.page.locator('#papers-generate').click()
        self.page.wait_for_function("!document.querySelector('#papers-cancel').hidden")
        self.page.locator('#papers-source-past-papers').uncheck()
        self.page.wait_for_function("document.querySelector('#papers-cancel').hidden")
        self.assertIn('Loading cancelled', self.page.locator('#papers-status').inner_text())
        self.assertEqual(self.paper(), kept)
        for route in held:
            route.abort()

    def test_reset_keeps_draft_settings_and_owner_course(self):
        self.page.locator('#papers-course').select_option('maths-a-level')
        self.page.locator('#papers-book').select_option('maths-a-level/maths-pure-year-1')
        self.page.locator('#papers-topics input').first.check()
        self.page.locator('#papers-source-madas').check(); self.page.locator('#papers-source-old-spec').check()
        self.page.locator('#papers-difficulty').select_option('medium')
        self.page.locator('#papers-past-paper').select_option(index=1)
        self.time_mode(); self.page.locator('[data-minutes="45"]').click()
        self.page.locator('#papers-answers').uncheck()
        self.generate()
        draft = self.paper()
        reset = self.page.get_by_role('button', name='Reset question filters')
        self.assertEqual((reset.inner_text(), reset.get_attribute('type')), ('Reset', 'button'))
        # Immediately to the right of the Question sources legend.
        box, legend = reset.bounding_box(), self.page.locator('.source-fieldset > legend').bounding_box()
        self.assertGreater(box['x'], legend['x'] + legend['width'] - 1)
        self.assertLess(abs((box['y'] + box['height'] / 2) - (legend['y'] + legend['height'] / 2)), 12)
        reset.press('Enter')
        state = self.page.evaluate("""() => ({sources: ['practice','exam-style','madas','past-papers','old-spec'].map(s => document.querySelector('#papers-source-' + s).checked),
          course: document.querySelector('#papers-course').value, book: document.querySelector('#papers-book').value,
          topics: document.querySelectorAll('#papers-topics input:checked').length, difficulty: document.querySelector('#papers-difficulty').value,
          paper: document.querySelector('#papers-past-paper').value, minutes: document.querySelector('#papers-minutes').value,
          mode: document.querySelector('input[name="papers-generate-mode"]:checked').value, answers: document.querySelector('#papers-answers').checked,
          offer: document.querySelector('#papers-time-accept').hidden})""")
        self.assertEqual(state, {'sources': [True, True, False, True, False], 'course': 'maths-a-level', 'book': '', 'topics': 0,
                                 'difficulty': '', 'paper': '', 'minutes': '45', 'mode': 'time', 'answers': False, 'offer': True})
        self.assertEqual(self.paper(), draft)
        self.assertIn('questions in the selection', self.page.locator('#filter-title').inner_text())
        stored = self.page.evaluate("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).modules.papers")
        self.assertEqual((stored['course'], stored['chapters'], stored['sources']['old-spec'], stored['selected']), ('maths-a-level', [], False, [i for i, _ in draft]))

    def test_new_tab_restores_draft_without_generating_and_explicit_clear(self):
        self.page.locator('#papers-topics input[value="maths-a-level/maths-pure-year-1/2"]').check()
        self.page.locator('#papers-topics input[value="maths-a-level/maths-pure-year-1/3"]').check()
        self.page.locator('#papers-source-old-spec').check()
        self.time_mode(); self.page.locator('[data-minutes="45"]').click()
        self.only({'practice', 'exam-style', 'past-papers', 'old-spec'})
        self.generate()
        draft = self.paper()
        # A new tab in the same profile is an ordinary reopening: same draft and settings, no generation.
        other = self.context.new_page()
        self.open_papers(other)
        other.wait_for_function("/restored/.test(document.querySelector('#papers-status').textContent)")
        self.assertEqual(other.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(q => [q.id, q.marks])'), draft)
        self.assertEqual(other.evaluate("[document.querySelector('#papers-minutes').value, document.querySelector('input[name=\"papers-generate-mode\"]:checked').value, document.querySelector('#papers-source-old-spec').checked, document.querySelector('#papers-time-report').hidden]"), ['45', 'time', True, True])
        other.locator('#papers-clear').click()
        third = self.context.new_page()
        self.open_papers(third)
        self.assertEqual(third.evaluate('LUISA_PAPERS_BUILDER.snapshot().length'), 0)

    def test_owner_launch_returns_to_last_page_but_tabs_and_home_do_not_bounce(self):
        self.page.locator('#papers-source-madas').check()
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).last"), 'papers')
        launch = self.context.new_page()
        launch.goto(self.base)
        launch.wait_for_url('**/papers.html')
        # The By skill tab is a deliberate destination.
        launch.locator('nav.view-tabs a', has_text='By skill').click()
        launch.wait_for_function("document.querySelector('#skilltitle')?.textContent.trim().length > 0")
        self.assertTrue(launch.url.startswith(self.base + '#'))
        launch.locator('#course').select_option('maths-a-level')
        launch.wait_for_function("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).modules.skill?.course === 'maths-a-level'")
        launch.locator('nav.view-tabs a', has_text='By textbook').click()
        launch.wait_for_function("document.querySelector('#chapter-title')?.textContent.startsWith('Chapter')")
        launch.locator('#chapter').select_option('3')
        launch.wait_for_function("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).modules.textbook?.chapter === '3'")
        # Browser Back returns through the in-page chapter change to By skill, which stays put.
        launch.go_back()
        launch.wait_for_function("location.hash.includes('chapter=1')")
        launch.go_back()
        launch.wait_for_function("!location.pathname.includes('textbook-view')")
        launch.wait_for_function("document.querySelector('#skilltitle')?.textContent.trim().length > 0")
        launch.wait_for_timeout(500)
        self.assertNotIn('textbook-view', launch.url)
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).last"), 'skill')
        # The main tab reopens By textbook with its own saved selection.
        # Back re-showed chapter 1, so that is now the latest By textbook selection; the tab reopens it.
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).modules.textbook.chapter"), '1')
        launch.locator('#course').select_option('maths-a-level')
        launch.locator('nav.view-tabs a', has_text='By textbook').click()
        launch.wait_for_function("document.querySelector('#chapter-title')?.textContent.startsWith('Chapter 1')")
        launch.locator('#chapter').select_option('3')
        launch.wait_for_function("JSON.parse(localStorage.getItem('luisa-preferences-v1:/')).modules.textbook?.chapter === '3'")
        self.assertIn('course=maths-a-level', launch.url)
        # A fresh launch now reopens By textbook with its chapter; a retired chapter falls back to its book.
        fresh = self.context.new_page(); fresh.goto(self.base)
        fresh.wait_for_url('**/textbook-view.html#*')
        self.assertIn('chapter=3', fresh.url)
        fresh.evaluate("""() => { const k = 'luisa-preferences-v1:/', s = JSON.parse(localStorage.getItem(k)); s.modules.textbook.chapter = '99'; s.modules.textbook.entry = 'retired'; localStorage.setItem(k, JSON.stringify(s)); }""")
        retired = self.context.new_page(); retired.goto(self.base)
        retired.wait_for_function("document.querySelector('#chapter-title')?.textContent.startsWith('Chapter')")
        self.assertIn('book=', retired.url)
        self.assertIn('Chapter 1:', retired.locator('#chapter-title').inner_text())
        # An explicit By skill link opens exactly that destination.
        link = self.context.new_page(); link.goto(self.base + '#course=maths-a-level&book=maths-pure-year-1')
        link.wait_for_function("document.querySelector('#skilltitle')?.textContent.trim().length > 0")
        self.assertTrue(link.url.startswith(self.base + '#course=maths-a-level'))
        # Resources keeps the resource last opened.
        res = self.context.new_page(); res.goto(self.base + 'teaching-chapters.html')
        first = res.locator('#catalogue a[data-resource]').nth(3)
        key = first.evaluate('a => [a.dataset.book, a.dataset.chapter, a.dataset.resource]')
        res.evaluate("a => a.addEventListener('click', e => e.preventDefault(), {once: true})", first.element_handle())
        first.click()
        again = self.context.new_page(); again.goto(self.base + 'teaching-chapters.html')
        self.assertEqual(again.locator('.resume-current').evaluate('a => [a.dataset.book, a.dataset.chapter, a.dataset.resource]'), key)


if __name__ == '__main__':
    unittest.main()
