"""Focused print acceptance; run explicitly with Playwright and Chrome installed.

One browser, one page at a time. No network services or new production dependencies.
"""
from datetime import datetime, timezone
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
        cls.context = cls.browser.new_context(timezone_id='Europe/London')

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
        self.assertEqual(preview.locator('.questions-page').count(), 4)
        self.assertGreater(preview.locator('.solutions-page').count(), 1)
        self.assertEqual(preview.locator('.print-page').evaluate_all("nodes=>nodes.map(n=>n.classList.contains('questions-page'))")[:4], [True] * 4)
        for index, item in enumerate(rows):
            selector = '[data-question-id="' + item['id'] + '"]'
            source = self.page.evaluate('html=>{const n=document.createElement("div");n.innerHTML=html;return [...n.querySelectorAll("[data-math]")].map(x=>x.dataset.math)}', ''.join(item['steps']))
            actual = preview.locator('.print-solution' + selector + ' [data-math]').evaluate_all('nodes=>nodes.map(n=>n.dataset.math)')
            self.assertEqual(actual, source)
            self.assertIn(f'Q{index + 1}', preview.locator('.print-solution' + selector).first.inner_text())
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
            self.assertIn('Worked solutions', pdf[4].get_text())
            pdf[1].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/luisa57-verified-diagram-page.png')
            pdf[0].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/luisa57-verified-question-page.png')
            pdf[4].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/luisa57-verified-solution-page.png')

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
        # Following ordinary questions return to one per sheet, preserving order.
        self.assertEqual([sheet.locator('.print-question h2').inner_text() for sheet in
                          preview.locator('.questions-page').all()[-2:]], ['Q3','Q4'])
        preview.pdf(path='/tmp/luisa57-long-question.pdf', prefer_css_page_size=True)

    def test_all_eligible_long_sources_preserve_content_and_fit(self):
        rejected = {r['id'] for r in json.loads((ROOT / 'docs/evidence/v057-papers-print.json').read_text())['promptAudit']['rejections']}
        allowed = {(r['skill'], r['question']) for r in json.loads((ROOT / 'textbook-catalogue.json').read_text())['questions']}
        rows = [row(skill, number) for skill, number in sorted(allowed) if row(skill, number)['id'] in rejected]
        self.assertEqual(len(rows), 271)
        for layout, offset in [(layout, offset) for layout in ('one', 'condensed') for offset in range(0, len(rows), 10)]:
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
        for layout, expected_pages in [('one', 4), ('condensed', 1)]:
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

    def test_past_exam_marks_and_timestamp_on_continuations(self):
        import fitz
        self.page.clock.set_fixed_time(datetime(2026, 11, 20, 18, 30, tzinfo=timezone.utc))
        rows = [dict(row('smq-1.53', 2), sourceKind='past-exam', sourceLabel='Source: Exam fixture A Q2', marks=7, difficulty='Hard'),
                dict(row('1.01', 1), sourceKind='past-exam', sourceLabel='Exam fixture B Q1', marks=6, difficulty='Easy')]
        rows[0]['question'] += '<p>Continuation geometry fixture.</p>' * 55
        for layout in ('one', 'condensed'):
            with self.subTest(layout=layout):
                preview, result = self.preview(rows, layout=layout, includeAnswers=False)
                self.assertTrue(result['ready'], result)
                self.assertGreater(preview.locator('.extended-page').count(), 1)
                self.assertEqual(preview.locator('.question-marks').all_text_contents(), ['[7 Marks]', '[6 Marks]'])
                self.assertEqual(preview.locator('.page-banner').all_text_contents(), ['Question paper'] * result['pageCount'])
                self.assertEqual(preview.locator('.page-footer time').all_text_contents(), ['20/11/26 6:30pm'] * result['pageCount'])
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
                    for sheet in pdf:
                        self.assertIn('20/11/26 6:30pm', sheet.get_text())
                        if layout == 'one':
                            rules = [path['rect'] for path in sheet.get_drawings()
                                     if path['rect'].y0 > sheet.rect.height - 58 and
                                        path['rect'].width > sheet.rect.width * .8 and path['rect'].height < 2]
                            self.assertEqual(len(rules), 1, rules)
                    pdf[-1].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(path + '.png')
                preview.close()

    def test_original_instructions_omitted_and_exam_solution_heading_matches(self):
        import fitz
        pure = json.loads((ROOT / 'content/exams/edexcel-9ma0-01-2025-june.json').read_text())
        core = json.loads((ROOT / 'content/exams/edexcel-9fm0-01-2025-june.json').read_text())
        exam = json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']
        descriptors = {item['id']: item for item in exam}
        rows = [dict(item, **{key: descriptors[item['id']][key] for key in ('marks', 'difficulty', 'sourceLabel')},
                     sourceKind='past-exam') for item in (pure['questions'][6], core['questions'][8])]
        preview, result = self.preview(rows)
        self.assertTrue(result['ready'], result)
        self.assertTrue(preview.locator('.page-banner').evaluate_all(
            "nodes=>nodes.every(n=>getComputedStyle(n).fontWeight==='700')"))
        self.assertEqual(preview.locator('.print-question .exam-instructions,.print-question .practice-context').count(), 0)
        for item in rows:
            selector = f'[data-question-id="{item["id"]}"] .compact-heading'
            question = preview.locator('.print-question' + selector)
            solution = preview.locator('.print-solution' + selector).first
            self.assertIn(item['sourceLabel'], question.inner_text())
            self.assertIn(f"[{item['marks']} Marks]", question.inner_text())
            self.assertEqual(solution.inner_text(), question.inner_text())
            self.assertTrue(solution.evaluate("n=>{const p=n.querySelector('.compact-provenance');return p.scrollWidth<=p.clientWidth+1}"))
        with fitz.open(stream=preview.pdf(prefer_css_page_size=True), filetype='pdf') as pdf:
            text = ''.join(sheet.get_text() for sheet in pdf)
            self.assertNotIn('Original paper instructions', text)
            self.assertNotIn('You should show sufficient working', text)
            self.assertNotIn('Page total:', text)
            self.assertIn('Worked solutions', text)
            pdf[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save('/tmp/luisa61-exam-question.png')
            pdf[len(rows)].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save('/tmp/luisa61-exam-solution.png')

    def exam_rows(self, paper, numbers):
        payload = {q['id']: q for q in json.loads((ROOT / f'content/exams/{paper}.json').read_text())['questions']}
        descriptors = {q['id']: q for q in json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']}
        return [dict(payload[f'exam/{paper}/q{n}'], **{key: descriptors[f'exam/{paper}/q{n}'][key] for key in
                     ('marks', 'difficulty', 'sourceLabel', 'questionNumber', 'paperCode')}, sourceKind='past-exam')
                for n in numbers]

    def assert_exam_print(self, preview, result, rows, answers):
        self.assertTrue(result['ready'], result)
        self.assertEqual(result['warnings'], [])
        ids = [r['id'] for r in rows]
        self.assertEqual(preview.locator('.questions-page .print-question').evaluate_all(
            'nodes=>[...new Set(nodes.map(n=>n.dataset.questionId))]'), ids)
        self.assertEqual(preview.locator('.questions-page .question-marks').all_text_contents(), [f"[{r['marks']} Marks]" for r in rows])
        self.assertEqual(preview.locator('.page-banner').all_text_contents()[:1], ['Question paper'])
        self.assertEqual(preview.locator('.print-question .exam-instructions').count(), 0)
        self.assertTrue(preview.locator('img').evaluate_all('nodes=>nodes.every(n=>n.complete&&n.naturalWidth>0)'))
        self.assertFalse(preview.locator('.page-content,.print-question').evaluate_all(
            'nodes=>nodes.some(n=>n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1)'))
        self.assertTrue(preview.locator('.print-question img').evaluate_all(
            'nodes=>nodes.every(img=>{const b=img.getBoundingClientRect(),line=parseFloat(getComputedStyle(img).lineHeight);'
            'return b.height<=8*line+1&&Math.abs(b.width/b.height-img.naturalWidth/img.naturalHeight)<.02})'))
        parse = ('html=>{const n=document.createElement("div");n.innerHTML=html;return [[...n.querySelectorAll("[data-math]")]'
                 '.map(x=>x.dataset.math),[...n.querySelectorAll("img")].map(x=>x.getAttribute("src"))]}')
        for item in rows:
            selector = f'[data-question-id="{item["id"]}"]'
            question = preview.locator('.print-question' + selector + ' .compact-heading').first.inner_text()
            self.assertIn(item['sourceLabel'], question)
            maths, images = self.page.evaluate(parse, item['question'])
            self.assertEqual(preview.locator('.print-question' + selector + ' [data-math]').evaluate_all('nodes=>nodes.map(n=>n.dataset.math)'), maths)
            self.assertEqual(preview.locator('.print-question' + selector + ' img').evaluate_all('nodes=>nodes.map(n=>n.getAttribute("src"))'), images)
            scheme = preview.locator('.print-solution' + selector + ' img').evaluate_all('nodes=>nodes.map(n=>n.getAttribute("src"))')
            if answers:
                self.assertEqual(scheme, self.page.evaluate(parse, ''.join(item['steps']))[1])
                self.assertEqual(preview.locator('.print-solution' + selector + ' .compact-heading').first.inner_text(), question)
            else:
                self.assertEqual(scheme, [])
        if not answers:
            self.assertEqual(preview.locator('.solutions-page,.print-solution').count(), 0)
            self.assertNotIn('-ms-p', preview.content())

    def test_pure_mathematics_2_complete_paper_and_mixed_overlap(self):
        import fitz
        self.page.clock.set_fixed_time(datetime(2026, 11, 21, 18, 30, tzinfo=timezone.utc))
        paper = self.exam_rows('edexcel-9ma0-02-2025-june', range(1, 16))
        self.assertEqual(sum(r['marks'] for r in paper), 100)
        for layout in ('one', 'condensed'):
            for answers in (False, True):
                with self.subTest(layout=layout, answers=answers):
                    preview, result = self.preview(paper, layout=layout, includeAnswers=answers)
                    self.assert_exam_print(preview, result, paper, answers)
                    text = ''.join(preview.locator('.questions-page').all_inner_texts())
                    self.assertIn('In this question you must show detailed reasoning.', text)
                    self.assertIn('Solutions relying entirely on calculator technology are not acceptable.', text)
                    if answers:
                        self.assertEqual(preview.locator('.print-solution img').count(), 70)
                    path = f'/tmp/luisa62-pure2-{layout}-{"solutions" if answers else "questions"}.pdf'
                    preview.pdf(path=path, prefer_css_page_size=True)
                    with fitz.open(path) as pdf:
                        self.assertEqual(len(pdf), result['pageCount'])
                        content = ''.join(sheet.get_text() for sheet in pdf)
                        self.assertNotIn('Original paper instructions', content)
                        self.assertNotIn('You should show sufficient working', content)
                        self.assertEqual('Worked solutions' in content, answers)
                        for index, sheet in enumerate(pdf):
                            self.assertIn(f'Page {index + 1} of {len(pdf)}', sheet.get_text())
                            self.assertIn('21/11/26 6:30pm', sheet.get_text())
                    preview.close()
        # Overlapping original numbers from two papers keep separate prompts and schemes.
        mixed = [row for pair in zip(self.exam_rows('edexcel-9ma0-01-2025-june', (1, 7)),
                                     self.exam_rows('edexcel-9ma0-02-2025-june', (1, 7))) for row in pair]
        for layout in ('one', 'condensed'):
            with self.subTest(mixed=layout):
                preview, result = self.preview(mixed, layout=layout, includeAnswers=True)
                self.assert_exam_print(preview, result, mixed, True)
                for item in mixed:
                    paper_id = item['id'].split('/')[1]
                    sources = preview.locator(f'.print-solution[data-question-id="{item["id"]}"] img').evaluate_all(
                        'nodes=>nodes.map(n=>n.getAttribute("src"))')
                    self.assertTrue(sources and all(f'/{paper_id}/q{item["questionNumber"]:02d}-ms-' in s for s in sources), sources)
                preview.pdf(path=f'/tmp/luisa62-mixed-{layout}.pdf', prefer_css_page_size=True)
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
            const line = parseFloat(getComputedStyle(img).lineHeight);
            return getComputedStyle(img).filter === 'grayscale(1)' && bounds.height > 6 * line && bounds.height <= 8 * line + 1 &&
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
            solution = preview.locator('.print-solution' + selector + ' .compact-provenance').first
            self.assertEqual(solution.inner_text(), provenance.inner_text())
            self.assertEqual(solution.get_attribute('title'), provenance.get_attribute('title'))
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
