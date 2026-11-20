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


class BrowserTestServer(http.server.ThreadingHTTPServer):
    request_queue_size = 128


class QuietServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        # Exercise the deployed ADA policy, including popup base and script URLs.
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; base-uri 'self'")
        super().end_headers()


CATALOGUE = json.loads((ROOT / 'data.js').read_text().split('=', 1)[1].rstrip(';\n'))
METADATA = {s['id']: dict(skillCode=s['code'], courseTitle=c['title'], bookTitle=b['title'], topicTitle=t['title'])
            for c in CATALOGUE['courses'] for b in c['books'] for t in b['topics'] for s in t['skills']}


def row(skill, number):
    question = next(q for q in json.loads((ROOT / 'content' / (skill + '.json')).read_text()) if q['number'] == number)
    return dict(question, **METADATA[skill])


def practice_row(family, chapter, suffix):
    document = json.loads((ROOT / f'content/practice/{family}/chapter-{chapter:02}.json').read_text())
    question = next(q for q in document['questions'] if q['id'].endswith('/' + suffix))
    return dict(question, sourceKind='practice-booklet', courseTitle='Mathematics A level',
                bookTitle=family, topicTitle=question['chapterTitle'])


class PapersPrintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = BrowserTestServer(('127.0.0.1', 0), functools.partial(QuietServer, directory=str(ROOT)))
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

    def preview(self, rows, **options):
        with self.page.expect_popup() as event:
            self.page.evaluate('input => { window.resultPromise = LUISA_PAPERS_PRINT.create(input.rows,input.options).then(r => window.result = {ready:r.ready,warnings:r.warnings,pageCount:r.pageCount}); }', dict(rows=rows, options=options))
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

    def test_long_original_continues_without_losing_any_diagrams(self):
        item = row('smq-1.53', 2)
        preview, result = self.preview([row('1.01', 1), item, row('1.01', 2), row('1.01', 3)])
        self.assertTrue(result['ready'], result)
        self.assertTrue(preview.get_by_role('button', name='Print / Save PDF').is_enabled())
        selector = '.print-question[data-question-id="' + item['id'] + '"]'
        images = preview.locator(selector + ' img').evaluate_all('nodes=>nodes.map(n=>n.getAttribute("src"))')
        expected = self.page.evaluate('html=>{const n=document.createElement("div");n.innerHTML=html;return [...n.querySelectorAll("img")].map(x=>x.getAttribute("src"))}', item['question'])
        self.assertEqual(images, expected)
        self.assertEqual(len(images), 21)
        self.assertTrue(all(value <= 1 for value in preview.locator('.page-content,.print-question').evaluate_all('nodes=>nodes.flatMap(n=>[n.scrollHeight-n.clientHeight,n.scrollWidth-n.clientWidth])')))
        # Following ordinary questions return to two per sheet, preserving order.
        self.assertEqual(preview.locator('.questions-page').last.locator('.print-question h2').all_text_contents(), ['Q3','Q4'])
        preview.pdf(path='/tmp/luisa57-long-question.pdf', prefer_css_page_size=True)

    def test_all_eligible_long_sources_preserve_content_and_fit(self):
        rejected = {r['id'] for r in json.loads((ROOT / 'docs/evidence/v057-papers-print.json').read_text())['promptAudit']['rejections']}
        allowed = {(r['skill'], r['question']) for r in json.loads((ROOT / 'textbook-catalogue.json').read_text())['questions']}
        rows = [row(skill, number) for skill, number in sorted(allowed) if row(skill, number)['id'] in rejected]
        self.assertEqual(len(rows), 271)
        for layout, offset in [(layout, offset) for layout in ('two', 'one', 'condensed') for offset in range(0, len(rows), 10)]:
            batch = rows[offset:offset + 10]
            preview, result = self.preview(batch, layout=layout)
            self.assertTrue(result['ready'], result)
            self.assertFalse(preview.locator('.page-content,.print-question').evaluate_all('nodes=>nodes.some(n=>n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1)'))
            identities = preview.evaluate(r'''rows=>{
              function identity(nodes){
                const parent=document.createElement('div');
                for(const node of nodes)parent.append(node.cloneNode(true));
                const maths=[...parent.querySelectorAll('[data-math]')].map(n=>n.dataset.math);
                const images=[...parent.querySelectorAll('img')].map(n=>n.getAttribute('src'));
                const parts=[...parent.querySelectorAll('ol>li')].map(n=>Number(n.getAttribute('value'))||(Number(n.parentElement.getAttribute('start'))||1)+[...n.parentElement.children].indexOf(n));
                parent.querySelectorAll('[data-math]').forEach(n=>n.remove());
                return {maths,images,parts,text:parent.textContent.replace(/\s+/g,' ').trim()};
              }
              return rows.map(row=>{
                const question=document.createElement('div');question.innerHTML=row.question;
                const solution=document.createElement('div');solution.innerHTML=row.steps.join('');
                const actualQuestion=identity(document.querySelectorAll('.print-question[data-question-id="'+row.id+'"]>.math-content'));
                const actualSolution=identity(document.querySelectorAll('.print-solution[data-question-id="'+row.id+'"]>.solution-step'));
                return {id:row.id,question:JSON.stringify(identity([question]))===JSON.stringify(actualQuestion),solution:JSON.stringify(identity([solution]))===JSON.stringify(actualSolution),imagesLoaded:[...document.querySelectorAll('[data-question-id="'+row.id+'"] img')].every(n=>n.complete&&n.naturalWidth>0)};
              });
            }''', batch)
            self.assertTrue(all(item['question'] and item['solution'] and item['imagesLoaded'] for item in identities), identities)
            preview.close()

    def test_layouts_and_optional_answers_are_complete_in_dom_and_pdf(self):
        import fitz
        rows = [dict(row('1.01', number), steps=['<p>ANSWER_SECRET_%s</p>' % number],
                     hints=['<p>HINT_SECRET_%s</p>' % number]) for number in (1, 2, 3, 4)]
        for layout, expected_pages in [('one', 4), ('two', 2), ('condensed', 1)]:
            for include_answers in (False, True):
                with self.subTest(layout=layout, include_answers=include_answers):
                    preview, result = self.preview(rows, layout=layout, includeAnswers=include_answers)
                    self.assertTrue(result['ready'], result)
                    self.assertEqual(preview.locator('.questions-page').count(), expected_pages)
                    self.assertEqual(preview.locator('.questions-page .print-question h2').all_text_contents(),
                                     ['Q1', 'Q2', 'Q3', 'Q4'])
                    self.assertFalse(preview.locator('.page-content,.print-question').evaluate_all(
                        'nodes=>nodes.some(n=>n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1)'))
                    if layout == 'condensed':
                        self.assertEqual(preview.locator('.working-space').count(), 0)
                    pdf_path = '/tmp/luisa59-print-%s-%s.pdf' % (layout, 'answers' if include_answers else 'questions')
                    preview.pdf(path=pdf_path, prefer_css_page_size=True)
                    with fitz.open(pdf_path) as pdf:
                        self.assertEqual(len(pdf), result['pageCount'])
                        pdf_text = ''.join(sheet.get_text() for sheet in pdf)
                        pdf[0].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(pdf_path + '.png')
                    for item in rows:
                        for secret in ('ANSWER_SECRET_', 'HINT_SECRET_'):
                            marker = secret + str(item['number'])
                            self.assertEqual(marker in preview.content(), include_answers)
                            self.assertEqual(marker in pdf_text, include_answers)
                    self.assertEqual(preview.locator('.solutions-page').count() > 0, include_answers)
                    preview.close()

    def test_excluded_answers_are_never_prepared_or_loaded(self):
        item = dict(row('1.01', 1), steps=['<p data-math="\\invalidAnswerCommand">UNAVAILABLE_ANSWER</p><img src="/missing-answer.png">'],
                    hints=['<img src="/missing-hint.png">UNAVAILABLE_HINT'])
        preview, result = self.preview([item], includeAnswers=False)
        self.assertTrue(result['ready'], result)
        self.assertNotIn('UNAVAILABLE_', preview.content())
        self.assertEqual(preview.locator('img,.solution-step,.solution-hints').count(), 0)

    def test_past_exam_marks_totals_time_and_continuations(self):
        import fitz
        rows = [dict(row('smq-1.53', 2), sourceKind='past-exam', sourceLabel='Source: Exam fixture A Q2', marks=7, difficulty='Hard'),
                dict(row('1.01', 1), sourceKind='past-exam', sourceLabel='Exam fixture B Q1', marks=6, difficulty='Easy')]
        rows[0]['question'] += '<p>Continuation geometry fixture.</p>' * 55
        for layout in ('one', 'two', 'condensed'):
            with self.subTest(layout=layout):
                preview, result = self.preview(rows, layout=layout, includeAnswers=False)
                self.assertTrue(result['ready'], result)
                self.assertGreater(preview.locator('.extended-page').count(), 1)
                self.assertTrue(all('Total: 13 marks' in t and 'Estimated time: 11 min' in t
                                    for t in preview.locator('.paper-marks').all_text_contents()))
                allocated = preview.locator('[data-allocated-marks]').evaluate_all(
                    'nodes=>nodes.map(n=>({id:n.dataset.questionId,marks:Number(n.dataset.allocatedMarks),last:![...n.ownerDocument.querySelectorAll(".print-question")].some(x=>x.dataset.questionId===n.dataset.questionId&&(n.compareDocumentPosition(x)&Node.DOCUMENT_POSITION_FOLLOWING))}))')
                self.assertEqual(sum(item['marks'] for item in allocated), 13)
                self.assertEqual(len(allocated), 2)
                self.assertTrue(all(item['last'] for item in allocated), allocated)
                totals = preview.locator('.questions-page .page-footer>span:first-child').all_text_contents()
                self.assertEqual(sum(int(text.split(': ')[1].split(' ')[0]) for text in totals), 13)
                self.assertTrue(all('final page' in text for text in preview.locator('.marks-policy').all_text_contents()))
                self.assertIn('Exam fixture A Q2', preview.locator('.questions-page').first.inner_text())
                self.assertNotIn('Source: Source:', preview.locator('body').inner_text())
                self.assertIn('Hard', preview.locator('.questions-page').first.inner_text())
                self.assertEqual(preview.locator('.print-question img').count(), 21)
                self.assertFalse(preview.locator('.page-content,.print-question').evaluate_all(
                    'nodes=>nodes.some(n=>n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1)'))
                path = '/tmp/luisa59-print-marks-%s.pdf' % layout
                preview.pdf(path=path, prefer_css_page_size=True)
                with fitz.open(path) as pdf:
                    self.assertEqual(len(pdf), result['pageCount'])
                    pdf[-1].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(path + '.png')
                preview.close()

    def test_incomplete_or_mixed_metadata_never_invents_totals(self):
        known = dict(row('1.01', 1), sourceKind='past-exam', sourceLabel='Exam fixture', marks=6)
        for unknown in (row('1.01', 2), dict(row('1.01', 2), sourceKind='past-exam'),
                        dict(row('1.01', 2), sourceKind='past-exam', marks='5'),
                        dict(row('1.01', 2), sourceKind='past-exam', marks=2.5)):
            preview, result = self.preview([known, unknown], includeAnswers=False)
            self.assertTrue(result['ready'], result)
            self.assertEqual(preview.locator('.paper-marks,.marks-policy,[data-allocated-marks]').count(), 0)
            self.assertNotIn('Estimated time:', preview.locator('.print-pages').inner_text())
            self.assertNotIn('Page total:', preview.locator('.print-pages').inner_text())
            self.assertEqual(preview.locator('.question-marks').all_text_contents(), ['[6 Marks]'])
            preview.close()

    def test_gold_header_and_question_image_height(self):
        item = practice_row('applied-year-2', 7, 'qgold')
        if not item['id'].endswith('/problem-b/qgold'):
            rows = json.loads((ROOT / 'content/practice/applied-year-2/chapter-07.json').read_text())['questions']
            item = next(row for row in rows if row['id'].endswith('/problem-b/qgold'))
        item.update(sourceKind='practice-booklet', courseTitle='Maths A Level', bookTitle='Mechanics Year 2',
                    difficulty='difficult', marks=15)
        preview, result = self.preview([item], layout='condensed', includeAnswers=False)
        self.assertTrue(result['ready'], result)
        heading = preview.locator('.print-question header')
        self.assertEqual(heading.inner_text().splitlines(), [
            'Q1', '(A Level Y2 Mech Ch7 Forces - Practice B Gold - Difficult)', '[15 Marks]'])
        self.assertTrue(heading.evaluate('''head => {
            const [number, source, marks] = head.children;
            return number.getBoundingClientRect().top === marks.getBoundingClientRect().top &&
                   getComputedStyle(number).fontWeight === '700' && getComputedStyle(marks).fontWeight === '700' &&
                   source.scrollWidth <= source.clientWidth + 1 &&
                   marks.getBoundingClientRect().right === head.getBoundingClientRect().right;
        }'''))
        image = preview.locator('.print-question img')
        self.assertTrue(image.evaluate('''img => {
            const bounds = img.getBoundingClientRect();
            return getComputedStyle(img).filter === 'grayscale(1)' && bounds.height > 0 && bounds.height <= 6 * parseFloat(getComputedStyle(img).lineHeight) + 1 &&
                   Math.abs(bounds.width / bounds.height - img.naturalWidth / img.naturalHeight) < .01;
        }'''))
        preview.pdf(path='/tmp/luisa103-gold.pdf', prefer_css_page_size=True)

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

    def test_unavailable_preview_shell_does_not_overwrite_sign_in(self):
        self.context.route('**/paper-preview.html', lambda route: route.fulfill(
            content_type='text/html', body='<h1>Sign in</h1><p>Session expired.</p>'))
        try:
            with self.page.expect_popup() as event:
                self.page.evaluate('rows=>{window.resultPromise=LUISA_PAPERS_PRINT.create(rows).catch(e=>window.failure=e.message)}', [row('1.01', 1)])
            self.page.evaluate('window.resultPromise')
            self.assertIn('Sign in or reconnect', self.page.evaluate('window.failure'))
            self.assertEqual(event.value.locator('h1').inner_text(), 'Sign in')
            self.assertEqual(event.value.locator('.print-question').count(), 0)
        finally:
            self.context.unroute('**/paper-preview.html')

    def test_practice_context_hints_portrait_and_part_labels_survive_print(self):
        rows = [practice_row('pure-year-1', 9, '9.5/q4'),
                practice_row('applied-year-2', 3, 'problem-a/qgold'),
                practice_row('applied-year-2', 2, '2.2/q3'),
                practice_row('pure-year-2', 10, '10.1/q6')]
        preview, result = self.preview(rows)
        self.assertTrue(result['ready'], result)
        self.assertEqual(result['warnings'], [])
        self.assertGreater(preview.locator('.practice-context').count(), 0)
        self.assertEqual(preview.locator('.questions-page .solution-hints').count(), 0)
        self.assertTrue(all(value <= 1 for value in preview.locator('.page-content,.print-question').evaluate_all(
            'nodes=>nodes.flatMap(n=>[n.scrollHeight-n.clientHeight,n.scrollWidth-n.clientWidth])')))
        for item in rows:
            selector = '[data-question-id="' + item['id'] + '"]'
            provenance = preview.locator('.print-question' + selector + ' .compact-provenance').first
            self.assertIn('Practice', provenance.inner_text())
            self.assertIn('Source: Practice Booklet · Chapter', provenance.get_attribute('title'))
            self.assertIn('Source: Practice Booklet', preview.locator('.print-solution' + selector).first.inner_text())
            self.assertTrue(preview.locator(selector + ' img').evaluate_all(
                'nodes=>nodes.every(n=>n.complete&&n.naturalWidth>0)'))
            expected = self.page.evaluate('html=>{const n=document.createElement("div");n.innerHTML=html;return [...n.querySelectorAll("[data-math]")].map(x=>x.dataset.math)}', ''.join(item['steps']))
            actual = preview.locator('.print-solution' + selector + ' .solution-step [data-math]').evaluate_all(
                'nodes=>nodes.map(n=>n.dataset.math)')
            self.assertEqual(actual, expected)
            if item.get('hints'):
                self.assertGreater(preview.locator('.print-solution' + selector + ' .solution-hints').count(), 0)
        # The tall photograph remains proportional and fits a readable full sheet.
        self.assertTrue(preview.locator('.print-page img.practice-figure').evaluate_all(
            'nodes=>nodes.every(n=>Math.abs(n.clientWidth/n.clientHeight-n.naturalWidth/n.naturalHeight)<.02)'))
        # A multiline equation must align its part letter with the first line.
        self.assertTrue(preview.locator('.print-solution li>.equation:first-child').evaluate_all(
            'nodes=>nodes.length>0&&nodes.every(n=>getComputedStyle(n).verticalAlign==="top")'))


if __name__ == '__main__':
    unittest.main()
