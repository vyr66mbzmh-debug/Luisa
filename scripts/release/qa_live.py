#!/usr/bin/env python3
"""Live verification of the Papers page and print on a deployed edition (owner, ADA staff, ADA pupil).

Usage (from the main checkout at the merged revision, after the editions are built):
  python3 scripts/release/qa_live.py owner [--url URL] [--papers id,id]
  python3 scripts/release/qa_live.py ada   [--papers id,id]

Expectations are derived, not hard-coded: question totals are read from the locally built owner
artifact (dist/); the past-paper dropdown order, labels and course/book lists come from
content/exams/pilot-metadata.json and exam-catalogue.json. The papers exercised in depth default to
those in the newest docs/evidence/v*-import-*.json. The ADA run creates one temporary staff and one
temporary pupil account through the server's own database (removed afterwards) and never prints
credentials. Results and printed PDFs go to the private release work folder; a results file
qa-<target>.json lists every passed check, and finish.py requires it.
Waits use Playwright locators only (no string-evaluated waits), so ADA's CSP is respected.
"""
import argparse
import functools
import glob
import hashlib
import http.server
import json
import os
import re
import secrets
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402
import ada as ada_tool  # noqa: E402
from playwright.sync_api import sync_playwright, expect  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
expect.set_options(timeout=45000)
PASSED = []


def ok(message):
    PASSED.append(message)
    print(message, flush=True)


def metadata():
    meta = json.loads((ROOT / 'content/exams/pilot-metadata.json').read_text())['papers']
    cat = json.loads((ROOT / 'exam-catalogue.json').read_text())['questions']
    return meta, cat


def dropdown_order(meta):
    """Newest first by exam or series date, then by paper code; undated papers last (papers.js)."""
    by_code = sorted(meta, key=lambda p: p['paperCode'])
    return sorted(by_code, key=lambda p: p.get('examDate') or p.get('seriesDate') or '', reverse=True)


def default_qa_papers():
    files = sorted(glob.glob(str(ROOT / 'docs/evidence/v*-import-*.json')), key=lambda f: [int(x) for x in re.findall(r'v(\d+)', Path(f).name)[:1]])
    return [p['paperId'] for p in json.loads(Path(files[-1]).read_text())['papers']]


def local_totals(browser):
    """Read the question totals the built owner artifact shows (all sources, and without past papers)."""
    handler = functools.partial(type('H', (http.server.SimpleHTTPRequestHandler,), {'log_message': lambda *a: None}), directory=str(ROOT / 'dist'))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        context = browser.new_context(service_workers='block')
        page = context.new_page()
        page.goto(f'http://127.0.0.1:{server.server_port}/papers.html')
        expect(page.locator('#papers-generate')).to_be_enabled(timeout=90000)
        total = page.locator('#filter-title').inner_text()
        page.locator('#papers-source-past-papers').uncheck()
        expect(page.locator('#filter-title')).not_to_have_text(total)
        no_past = page.locator('#filter-title').inner_text()
        context.close()
        return total, no_past
    finally:
        server.shutdown()


def live_get(p, url, **options):
    for attempt in range(4):
        try:
            return p.request.get(url, timeout=9000, max_retries=1, **options)
        except Exception:
            if attempt == 3:
                raise


def paper(p, url, role, totals, qa_papers, out, rev, version):
    meta, cat = metadata()
    marks_of = {q['id']: q['marks'] for q in cat}
    order = dropdown_order(meta)
    total_text, no_past_text = totals
    print(role, 'begin live verification', flush=True)

    def failed(request):
        path = urlsplit(request.url).path
        if path.startswith(urlsplit(url).path) and request.failure != 'net::ERR_ABORTED':
            print(role, 'request failure', path, request.failure, flush=True)
    p.context.on('requestfailed', failed)
    if role != 'owner':
        def serve_via_live_request(route):
            if route.request.method != 'GET':
                return route.continue_()
            for timeout in (9000, 12000, 16000):
                try:
                    return route.fulfill(response=route.fetch(timeout=timeout, max_redirects=0, max_retries=1))
                except Exception:
                    continue
            print(role, 'authenticated endpoint timed out', urlsplit(route.request.url).path, flush=True)
            route.abort('timedout')
        p.context.route(url + '**', serve_via_live_request)
    if role == 'owner':
        for name in ('', 'textbook-view.html', 'teaching-chapters.html'):
            p.goto(url + name, wait_until='domcontentloaded', timeout=90000)
            expect(p.locator('a[href$="papers.html"]')).to_have_count(1)
    p.goto(url + 'papers.html', wait_until='commit', timeout=90000)
    expect(p.locator('a[href$="papers.html"]')).to_have_count(1)
    try:
        expect(p.locator('#filter-title')).to_have_text(total_text, timeout=25000)
    except AssertionError:
        print(role, 'retrying Papers startup', flush=True)
        p.reload(wait_until='commit', timeout=90000)
        expect(p.locator('#filter-title')).to_have_text(total_text, timeout=70000)
    if role == 'student':
        assert not p.locator('a[href$="offline.html"],a[href$="development-progress.html"],a[href*="classpad.net"]').count()
    if role != 'owner':
        expect(p.locator('.luisa-signout')).to_have_count(1)
    # PAP-068: the paper dropdown follows Course/Book; active and disabled styles.
    panel = p.locator('.filter-panel')
    shot = lambda name: panel.screenshot(path=str(out / f'shot-{role}-{name}.png'))
    opts = lambda: p.locator('#papers-past-paper option').evaluate_all('ns=>ns.map(n=>n.value)')
    look = lambda i: p.locator(i).evaluate('n=>[n.classList.contains("filter-active"),n.disabled,getComputedStyle(n).backgroundColor,getComputedStyle(n).borderTopColor]')
    white = [False, False, 'rgb(255, 255, 255)', 'rgb(170, 185, 196)']
    assert opts() == [''] + [x['id'] for x in order], opts()
    for i in ('#papers-past-paper', '#papers-difficulty', '#papers-course', '#papers-book'):
        assert look(i) == white, (i, look(i))
    shot('all')
    maths = [x['id'] for x in order if x['paperCode'].startswith('9MA')]
    p.locator('#papers-course').select_option('maths-a-level')
    assert opts() == [''] + maths, opts()
    assert look('#papers-course') == [True, False, 'rgb(237, 243, 247)', 'rgb(21, 59, 87)'], look('#papers-course')
    mech = [x['id'] for x in order if any(k.startswith('maths-a-level/maths-mechanics-year-2/') for q in cat if q['paperId'] == x['id'] for k in q['chapterKeys'])]
    p.locator('#papers-book').select_option('maths-a-level/maths-mechanics-year-2')
    assert opts() == [''] + mech, opts()
    p.locator('#papers-past-paper').select_option(mech[1])
    assert look('#papers-past-paper')[0]
    p.locator('#papers-difficulty').select_option('medium')
    assert look('#papers-difficulty')[0]
    shot('active')
    p.locator('#papers-difficulty').select_option('')
    assert look('#papers-difficulty') == white
    p.locator('#papers-book').select_option('maths-a-level/maths-pure-year-2')
    assert p.locator('#papers-past-paper').input_value() == '' and look('#papers-past-paper') == white
    p.locator('#papers-book').select_option('')
    p.locator('#papers-course').select_option('')
    assert len(opts()) == len(order) + 1 and look('#papers-course') == white and look('#papers-book') == white
    p.locator('#papers-past-paper').select_option('edexcel-9fm0-01-2024-june')
    p.locator('#papers-source-past-papers').uncheck()
    g = look('#papers-past-paper')
    assert g[:3] == [False, True, 'rgb(236, 238, 239)'] and p.locator('#papers-past-paper').input_value() == '', g
    expect(p.locator('#filter-title')).to_have_text(no_past_text)
    shot('disabled')
    p.locator('#papers-source-past-papers').check()
    assert look('#papers-past-paper') == white
    expect(p.locator('#filter-title')).to_have_text(total_text)
    ok(f'{role} PAP-068 dropdown order, Course/Book filtering, active, disabled and reset passed')
    p.locator('#papers-course').select_option('maths-a-level')
    p.locator('#papers-book').select_option('maths-a-level/maths-pure-year-1')
    expect(p.locator('#papers-topics input')).to_have_count(14)
    topics = p.locator('#papers-topics label > span').evaluate_all('ns=>ns.map(n=>n.firstChild.textContent)')
    assert (topics[0], topics[-1]) == ('1. Algebraic expressions', '14. Exponentials and logarithms')

    def print_paper(label, layout, answers, marks, expected_order=None):
        p.locator('#papers-condensed').set_checked(layout == 'condensed')
        p.locator('#papers-answers').set_checked(answers)
        with p.expect_popup() as event:
            p.locator('#papers-print').click()
        preview = event.value
        preview.locator('body.not-ready, .print-toolbar button:not(.secondary):enabled').wait_for(state='attached', timeout=140000)
        if preview.locator('body.not-ready').count():
            raise AssertionError(preview.locator('.print-status').inner_text() + ' ' + ' '.join(preview.locator('.print-errors li').all_text_contents()))
        expect(preview.get_by_role('button', name='Print / Save PDF')).to_be_enabled()
        assert not preview.locator('.print-errors').count()
        assert bool(preview.locator('.solutions-page').count()) == answers
        assert preview.locator('img').evaluate_all('ns=>ns.every(n=>n.complete&&n.naturalWidth>0)')
        expect(preview.locator('.questions-page .question-marks').first).to_have_text(marks)
        assert preview.locator('.print-question .marks').evaluate_all("ns=>ns.every(n=>getComputedStyle(n).fontWeight==='700'&&/^\\(\\d+\\)$/.test(n.textContent)&&getComputedStyle(n).position==='absolute')")
        expect(preview.locator('.questions-page .page-banner').first).to_have_text('Question paper')
        assert not preview.locator('.print-question .exam-instructions').count()
        assert 'Original paper instructions' not in preview.locator('.print-pages').inner_text()
        stamps = preview.locator('.page-footer time').all_text_contents()
        assert len(set(stamps)) == 1 and re.fullmatch(r'\d{2}/\d{2}/\d{2} \d{1,2}:\d{2}[ap]m', stamps[0])
        if expected_order:
            assert preview.locator('.questions-page .print-question').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]') == expected_order
        if answers:
            assert preview.locator('.solutions-page img').count() > 0
            for qid in preview.locator('.print-solution').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]'):
                if qid.startswith('exam/'):
                    pid, number = qid.split('/')[1], int(qid.rsplit('/q', 1)[1])
                    srcs = preview.locator(f'.print-solution[data-question-id="{qid}"] img').evaluate_all('ns=>ns.map(n=>n.getAttribute("src"))')
                    assert srcs and all(f'{pid}/q{number:02d}-ms-' in x for x in srcs), (qid, srcs)
        if layout == 'condensed':
            assert preview.locator('.working-space').count() == 0
            if label == 'gold':
                assert preview.locator('.print-question img').evaluate("img=>getComputedStyle(img).filter === 'grayscale(1)'")
        preview.pdf(path=str(out / f'live-{role}-{label}.pdf'), prefer_css_page_size=True)
        preview.close()
        print(role, label, 'print passed', flush=True)

    def select_whole(pid):
        n = sum(1 for q in cat if q['paperId'] == pid)
        marks = sum(q['marks'] for q in cat if q['paperId'] == pid)
        p.locator('#papers-clear').click()
        p.locator('#papers-past-paper').select_option(pid)
        expect(p.locator('#filter-title')).to_have_text(f'{n} questions in the selection')
        p.locator('#papers-count').fill(str(n))
        p.locator('#papers-generate').click()
        expect(p.locator('#papers-cancel')).to_be_hidden(timeout=90000)
        expect(p.locator('#papers-selected-count')).to_have_text(str(n))
        expect(p.locator('#papers-summary')).to_contain_text(f'{marks} marks')
        p.locator('#papers-order').select_option('paper')
        exp = [f'exam/{pid}/q{i}' for i in range(1, n + 1)]
        assert p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)') == exp
        return exp

    p.locator('#papers-course').select_option('')
    p.locator('#papers-source-practice').uncheck()
    p.locator('#papers-source-exam-style').uncheck()
    expect(p.locator('#filter-title')).to_have_text(f'{len(cat):,} questions in the selection')
    options = p.locator('#papers-past-paper option').evaluate_all('ns=>ns.map(n=>[n.value,n.textContent])')
    for (value, label), x in zip(options[1:], order):
        assert value == x['id'] and x['paperCode'] in label and x['session'] in label, (value, label)
    ok(f'{role} every past paper listed in date order with its session and code ({len(order)} papers)')
    # Stable regression: a whole June 2025 paper selected by browsing, then generated in paper order.
    p.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
    expect(p.locator('#filter-title')).to_have_text('15 questions in the selection')
    p.locator('#papers-browse').click()
    for first, count in ((1, 8), (9, 7)):
        expect(p.locator('[data-add]')).to_have_count(count, timeout=90000)
        expect(p.locator('[data-add]').first).to_have_attribute('data-add', re.compile(f'/q{first}$'), timeout=90000)
        for ident in p.locator('[data-add]').evaluate_all('ns=>ns.map(n=>n.dataset.add)'):
            p.locator(f'[data-add="{ident}"]').click()
        if count == 8:
            p.locator('#papers-next').click()
    p.locator('#papers-order').select_option('selection')
    expect(p.locator('#papers-selected-count')).to_have_text('15')
    expect(p.locator('#papers-summary')).to_contain_text('100 marks')
    expected = [f'exam/edexcel-9ma0-02-2025-june/q{n}' for n in range(1, 16)]
    assert p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)') == expected
    print_paper('pure2-whole', 'one', True, '[3 Marks]', expected)
    order_opts = lambda: p.locator('#papers-order option').evaluate_all('ns=>ns.map(n=>[n.value,n.textContent])')
    assert order_opts() == [['topic', 'Group by topic'], ['selection', 'As selected'], ['paper', 'In paper order']], order_opts()
    p.locator('#papers-count').fill('15')
    p.locator('#papers-generate').click()
    expect(p.locator('#papers-cancel')).to_be_hidden(timeout=90000)
    expect(p.locator('#papers-selected-count')).to_have_text('15')
    p.locator('#papers-order').select_option('paper')
    assert p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)') == expected
    print_paper('pure2-paper-order', 'condensed', False, '[3 Marks]', expected)
    p.reload(wait_until='commit', timeout=90000)
    expect(p.locator('#papers-status')).to_contain_text('restored', timeout=90000)
    assert p.locator('#papers-order').input_value() == 'paper'
    assert p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)') == expected
    ok(f'{role} In paper order option, order and reload passed')
    # The release's papers: selectable by name, own questions only, paper order, prints with own schemes, reload.
    modes = [('one', True), ('condensed', True), ('condensed', False)]
    for i, pid in enumerate(qa_papers):
        exp = select_whole(pid)
        if i < len(modes):
            layout, answers = modes[i]
            print_paper(f'{pid}-{layout}-{int(answers)}', layout, answers, f'[{marks_of[exp[0]]} Marks]', exp)
    p.reload(wait_until='commit', timeout=90000)
    expect(p.locator('#papers-status')).to_contain_text('restored', timeout=90000)
    last = qa_papers[-1]
    assert p.locator('#papers-past-paper').input_value() == last and p.locator('#papers-order').input_value() == 'paper'
    assert p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)') == [q['id'] for q in cat if q['paperId'] == last]
    # Mixed selection: add another paper's last question; both keep their own schemes.
    other = next(x['id'] for x in order if x['id'] != last)
    other_last = [q['id'] for q in cat if q['paperId'] == other][-1]
    p.locator('#papers-past-paper').select_option(other)
    p.locator('#papers-browse').click()
    while not p.locator(f'[data-add="{other_last}"]').count():
        p.locator('#papers-next').click()
    p.locator(f'[data-add="{other_last}"]').click()
    p.locator('#papers-order').select_option('selection')
    mixed = p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)')
    assert sorted(mixed) == sorted([q['id'] for q in cat if q['paperId'] == last] + [other_last]), mixed
    print_paper('release-mixed', 'one', True, f'[{marks_of[mixed[0]]} Marks]', mixed)
    ok(f'{role} release papers selectable by name, own questions, paper order, reload, mixed and scheme print passed ({", ".join(qa_papers)})')
    # Stable regression: June 2024 Core Pure 2 in paper order, then the teacher exam paper (owner, staff) or its absence (pupil).
    expected24 = select_whole('edexcel-9fm0-02-2024-june')
    print_paper('june2024-cp2-paper-order', 'condensed', True, '[7 Marks]', expected24)
    expect(p.locator('#papers-summary')).to_contain_text('75 marks · Time: 90 minutes')
    if role == 'student':
        assert p.locator('#papers-exam, #papers-exam-print, #papers-exam-minutes, #papers-exam-generate, [data-exam-preset], script[src$="papers-exam.js"]').count() == 0
        assert p.evaluate('typeof window.LUISA_PAPERS_EXAM') == 'undefined'
        for name in ('papers-exam.js', 'papers-exam.css'):
            assert live_get(p, url + name, max_redirects=0).status == 404, name
        ok(f'{role} exam paper absent and directly denied')
    else:
        exam_checks(p, role, out, expected24)
    p.locator('#papers-clear').click()
    p.locator('#papers-order').select_option('topic')
    p.locator('#papers-past-paper').select_option('edexcel-9ma0-01-2025-june')
    expect(p.locator('#filter-title')).to_have_text('16 questions in the selection')
    p.locator('#papers-browse').click()
    p.locator('[data-add$="/q7"]').click()
    p.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
    p.locator('#papers-browse').click()
    p.locator('[data-add="exam/edexcel-9ma0-02-2025-june/q7"]').click()
    expect(p.locator('#papers-selected-count')).to_have_text('2')
    print_paper('mixed', 'one', True, '[7 Marks]')
    p.locator('#papers-clear').click()
    p.locator('#papers-past-paper').select_option('')
    assert len(order_opts()) == 2 and p.locator('#papers-order').input_value() == 'topic'
    p.locator('#papers-source-past-papers').uncheck()
    p.locator('#papers-source-exam-style').check()
    p.locator('#papers-difficulty').select_option('difficult')
    p.locator('#papers-course').select_option('maths-a-level')
    p.locator('#papers-book').select_option('maths-a-level/maths-mechanics-year-2')
    p.locator('#papers-topics input[value="maths-a-level/maths-mechanics-year-2/7"]').check()
    p.locator('[data-add$="/problem-b/qgold"]').click()
    expect(p.locator('#papers-summary')).to_contain_text('15 marks')
    p.set_viewport_size({'width': 390, 'height': 844})
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
    print_paper('gold', 'condensed', False, '[15 Marks]')
    assert p.evaluate("JSON.parse(sessionStorage.getItem('luisa-papers-v1')).selected.length") == 1
    p.reload(wait_until='commit', timeout=90000)
    expect(p.locator('#papers-status')).to_contain_text('restored')
    expect(p.locator('#papers-selected-count')).to_have_text('1')
    assert p.locator('#papers-condensed').is_checked() and not p.locator('#papers-answers').is_checked()
    p.evaluate('''() => {
     const key='luisa-papers-v1';
     const saved=JSON.parse(sessionStorage.getItem(key));
     saved.selected=['practice/maths-a-level/maths-pure-year-1/ch11/11.3/q7'];
     sessionStorage.setItem(key,JSON.stringify(saved));
    }''')
    p.reload(wait_until='commit', timeout=90000)
    expect(p.locator('#papers-summary')).to_contain_text('6 marks')
    print_paper('labelled-table', 'one', False, '[6 Marks]')
    manifest_checks(p, url, role, rev, version)
    ok(f'{role} live manifest, assets, textbook topics, mobile, marks, mixed and condensed print, restore passed')


def exam_checks(p, role, out, expected24):
    """Teacher-only exam paper (owner and staff): defaults, questions only, scheme only, timed paper."""
    import datetime
    import zoneinfo
    p.locator('#papers-exam summary').click()
    assert p.locator('input[name="papers-exam-content"]').evaluate_all('ns=>ns.map(n=>[n.value,n.checked])') == [['questions', True], ['scheme', False], ['both', False]]
    panel = p.locator('#papers-exam').inner_text()
    for gone in ('no solutions', 'is added automatically when any question comes from Mechanics', 'g = 9.8', 'Prints the paper above'):
        assert gone not in panel, gone
    assert p.locator('#papers-exam-instructions').input_value() == (
        'Calculators may be used and a formulae booklet is provided. Where specified, answers relying solely on technology will not receive credit.\n\n'
        'Give exact answers where requested and approximate numerical answers to three significant figures unless otherwise stated.\n\n'
        'Clearly label all answers, including those on additional paper, with the question number and part.')
    now = datetime.datetime.now(zoneinfo.ZoneInfo('Europe/London'))
    suffix = 'th' if 11 <= now.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(now.day % 10, 'th')
    assert p.locator('#papers-exam-date').input_value() == f'{now:%A} {now.day}{suffix} {now:%B}'
    ok(f'{role} exam defaults and removed texts passed')
    p.locator('#papers-exam-year').fill('L6')
    p.locator('#papers-exam-title').fill('Further Maths Assessment 1')
    expect(p.locator('#papers-exam-summary')).to_have_text('9 questions · 75 marks · Time: 90 minutes (+23 minutes extra time)')

    def popup():
        with p.expect_popup() as event:
            p.locator('#papers-exam-print').click()
        ex = event.value
        ex.locator('body.not-ready, .print-toolbar button:not(.secondary):enabled').wait_for(state='attached', timeout=140000)
        assert not ex.locator('body.not-ready, .print-errors').count(), ex.locator('.print-status').inner_text()
        return ex
    ex = popup()
    expect(ex.locator('.exam-title')).to_have_text('L6 Further Maths Assessment 1')
    expect(ex.locator('.exam-time')).to_have_text('Time: 90 minutes (+23 minutes extra time)')
    expect(ex.locator('.exam-marks-available')).to_have_text('Total marks available: 75')
    n = ex.locator('.exam-page').count()
    assert n >= 18 and n % 2 == 0, n
    assert ex.locator('.exam-page .page-footer').all_text_contents() == [f'Page {i} of {n}' for i in range(1, n + 1)]
    assert ex.locator('.exam-front-page .page-footer, .page-banner, .solutions-page, .print-solution').count() == 0
    assert ex.locator('.exam-page .exam-question').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]') == expected24
    assert ex.locator('.question-total').all_text_contents() == [f'(Total for Question {i} is {m} marks)' for i, m in enumerate([7, 8, 5, 6, 9, 14, 9, 7, 10], 1)]
    expect(ex.locator('.paper-total')).to_have_text('TOTAL FOR PAPER IS 75 MARKS')
    ys = ex.locator('.answer-rules').first.locator('.answer-line').evaluate_all('ns=>ns.map(n=>n.y1.baseVal.value)')
    assert all(abs(b - a - 8 / 25.4 * 96) < .01 for a, b in zip(ys, ys[1:])), ys
    assert ex.locator('.exam-course-map').count() == 0
    assert ex.locator('.exam-heading h2').first.inner_text() == 'Question 1'
    assert ex.locator('.exam-date sup').count() == 1 and ex.locator('.exam-scheme-page').count() == 0
    ex.pdf(path=str(out / f'live-{role}-exam.pdf'), prefer_css_page_size=True)
    ex.close()
    ok(f'{role} teacher exam paper passed')
    p.locator('input[name="papers-exam-content"][value="scheme"]').check()
    ex = popup()
    assert ex.locator('.exam-front-page, .exam-page, .answer-lines').count() == 0
    s = ex.locator('.exam-scheme-page').count()
    assert s > 0
    assert ex.locator('.exam-scheme-page .page-footer').all_text_contents() == [f'Mark scheme page {i} of {s}' for i in range(1, s + 1)]
    assert ex.locator('.exam-scheme').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]') == expected24
    srcs = ex.locator('.exam-scheme img').evaluate_all('ns=>ns.map(n=>n.getAttribute("src"))')
    assert srcs and all('/edexcel-9fm0-02-2024-june/' in x and '-ms-' in x for x in srcs)
    ex.pdf(path=str(out / f'live-{role}-scheme.pdf'), prefer_css_page_size=True)
    ex.close()
    ok(f'{role} mark scheme only passed')
    p.locator('input[name="papers-exam-content"][value="both"]').check()
    p.locator('#papers-past-paper').select_option('')
    p.locator('[data-exam-preset="60"]').click()
    p.locator('#papers-exam-generate').click()
    expect(p.locator('#papers-exam-target-report')).to_contain_text('Target 60 minutes met:', timeout=120000)
    m = re.search(r'(\d+) marks · Time: (\d+) minutes \(\+(\d+) minutes extra time\)', p.locator('#papers-exam-summary').inner_text())
    marks, minutes, extra = map(int, m.groups())
    assert abs(minutes - 60) <= 2 and minutes == marks * 6 // 5 and extra == int(minutes * .25 + .5), m.groups()
    diffs = p.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(r=>r.difficulty)')
    assert diffs[0] == 'easy' and diffs[-1] == 'difficult', diffs
    ex = popup()
    expect(ex.locator('.exam-time')).to_have_text(f'Time: {minutes} minutes (+{extra} minutes extra time)')
    expect(ex.locator('.paper-total')).to_have_text(f'TOTAL FOR PAPER IS {marks} MARKS')
    pages = ''.join(ex.locator('.print-page').evaluate_all('ns=>ns.map(n=>n.classList.contains("exam-scheme-page")?"s":n.classList.contains("exam-page")?"q":"f")'))
    assert re.fullmatch(r'fq+s+', pages), pages
    ids = p.evaluate('LUISA_PAPERS_BUILDER.snapshot().map(r=>r.id)')
    assert ex.locator('.exam-scheme').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]') == ids
    ex.pdf(path=str(out / f'live-{role}-timed.pdf'), prefer_css_page_size=True)
    ex.close()
    ok(f'{role} timed exam paper with mark scheme passed ({len(diffs)} questions, {marks} marks, {minutes} minutes)')


def manifest_checks(p, url, role, rev, version):
    local = json.loads((ROOT / {'owner': 'dist', 'staff': 'dist-staff', 'student': 'dist-student'}[role] / 'build-manifest.json').read_text())
    response = live_get(p, url + 'build-manifest.json')
    if role == 'owner':
        assert response.ok
        manifest = response.json()
    else:
        assert response.status == 404
        directory = ada_tool.folder(rev)
        assert ada_tool.live_folder() == directory
        manifest = json.loads(private.remote('cat ' + directory + '/' + {'staff': 'staff', 'student': 'content'}[role] + '/build-manifest.json'))
    assert (manifest['revision'], manifest['edition'], manifest['version'], manifest['dirty']) == (rev, role, version, False)
    paths = ['release.json', 'papers.html', 'papers.js', 'papers.css', 'paper-preview.html', 'papers-print.js', 'papers-print.css',
             'exam-catalogue.json', 'practice-catalogue.json', 'textbook-catalogue.json']
    paths += [path for path in local['files'] if path.startswith('content/exams/')]
    if role == 'owner':
        paths += ['development-progress.html', f'release-report-{version}.html']
    else:
        paths = ['papers.html', 'paper-preview.html', 'papers.js', 'papers-print.js', 'papers-print.css', 'exam-catalogue.json']
    for path in paths:
        res = live_get(p, url + path)
        assert res.ok, (path, res.status)
        assert local['files'][path]['sha256'] == manifest['files'][path]['sha256'], path
        if role == 'owner' or not path.endswith('.html'):
            assert hashlib.sha256(res.body()).hexdigest() == manifest['files'][path]['sha256'], path
        else:
            assert 'text/html' in res.headers.get('content-type', '')
            marker = {'papers.html': 'id="papers-main"', 'paper-preview.html': 'name="luisa-paper-preview"'}[path]
            assert marker in res.text(), path
        if role != 'owner':
            assert 'no-store' in res.headers.get('cache-control', '')
    if role == 'owner':
        import report
        page = live_get(p, url + f'release-report-{version}.html').text()
        errors = report.page_errors(page, version, (ROOT / 'HANDOFF.md').read_text())
        assert not errors, errors
        ok('owner published release report has exactly one correctly titled handoff')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('target', choices=['owner', 'ada'])
    parser.add_argument('--url', help='owner edition URL (default: release.json publicBaseUrl); a local server URL for a dry run')
    parser.add_argument('--papers', help='comma-separated paper ids to exercise in depth')
    parser.add_argument('--channel', default=os.environ.get('LUISA_BROWSER_CHANNEL') or 'chromium', help='Playwright browser channel (chrome, or chromium for the bundled browser)')
    args = parser.parse_args()
    release = json.loads((ROOT / 'release.json').read_text())
    version = release['version']
    rev = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out = private.work_dir(version)
    qa_papers = args.papers.split(',') if args.papers else default_qa_papers()
    with sync_playwright() as w:
        browser = w.chromium.launch(channel=None if args.channel == 'chromium' else args.channel, args=['--disable-http2', '--disable-quic'])
        totals = local_totals(browser)
        if args.target == 'owner':
            url = (args.url or release['publicBaseUrl']).rstrip('/') + '/'
            c = browser.new_context(service_workers='block', viewport={'width': 1440, 'height': 1000})
            paper(c.new_page(), url, 'owner', totals, qa_papers, out, rev, version)
        else:
            url = private.get('ada.url').rstrip('/') + '/'
            staff = 'qa' + secrets.token_hex(5)
            pupil = '0' + str(secrets.randbelow(10000)).zfill(4)
            pw = secrets.token_urlsafe(24)
            db = private.layout('dataDir') + '/accounts.sqlite'
            fixture = lambda script: private.remote(private.layout('runtimePython') + ' -', (
                f"import sqlite3\nfrom argon2 import PasswordHasher\nc=sqlite3.connect({db!r});c.execute('pragma foreign_keys=on')\n" + script).encode())
            fixture(f"h=PasswordHasher().hash({pw!r});c.execute('insert into staff_accounts(username,password_hash,force_change)values(?,?,0)',({staff!r},h));"
                    f"c.execute('insert into accounts(school_number,password_hash)values(?,?)',({pupil!r},h));c.commit()")
            try:
                for role, ident in [('student', pupil + '@' + private.get('ada.pupilEmailDomain')), ('staff', staff)]:
                    c = browser.new_context(service_workers='block', viewport={'width': 1440, 'height': 1000})
                    p = c.new_page()
                    p.goto(url + 'login')
                    p.locator('[name=email]').fill(ident)
                    p.locator('[name=password]').fill(pw)
                    p.locator('button[type=submit],button').first.click()
                    expect(p).not_to_have_url(re.compile(r'/login'))
                    paper(p, url, role, totals, qa_papers, out, rev, version)
                    p.locator('.luisa-signout').click()
                    expect(p).to_have_url(url + 'login')
                    assert live_get(p, url + 'papers.js', max_redirects=0).status == 302
                    c.close()
                guest = browser.new_context().new_page()
                for path in ['papers.html', 'papers.js', 'exam-catalogue.json', 'content/exams/edexcel-9ma0-01-2025-june.json',
                             'resources/exams/edexcel-9ma0-01-2025-june/q07-figure.svg', 'content/exams/edexcel-9fm0-02-2024-june.json']:
                    assert live_get(guest, url + path, max_redirects=0).status == 302, path
                assert live_get(guest, url + 'admin', max_redirects=0).status in (302, 403)
                ok('ada signed-out guests are redirected from Papers and exam assets')
            finally:
                fixture(f"c.execute('delete from sessions where staff_username=? or school_number=?',({staff!r},{pupil!r}));"
                        f"c.execute('delete from staff_accounts where username=?',({staff!r},));c.execute('delete from accounts where school_number=?',({pupil!r},));c.commit()")
        browser.close()
    target = 'owner' if args.target == 'owner' and not args.url else ('dry-run' if args.url else 'ada')
    (out / f'qa-{target}.json').write_text(json.dumps({'revision': rev, 'version': version, 'papers': qa_papers, 'passed': PASSED}, indent=1))
    print(json.dumps({'event': 'qa_pass', 'target': target, 'checks': len(PASSED)}))


if __name__ == '__main__':
    main()
