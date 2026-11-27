#!/usr/bin/env python3
"""Disconnected-use verification of the owner edition (PWA offline packs, Papers and print offline).

Usage (from the main checkout at the merged revision):
  python3 scripts/release/qa_offline.py [--url https://<owner-site>/]   # default: release.json publicBaseUrl
  python3 scripts/release/qa_offline.py --local                         # dry run against dist/ on a local server

Downloads two chapter packs (Core Pure 2 chapter 6, Pure Year 2 chapter 11), goes offline, and checks:
the Papers totals (read from the local build), the Course/Book-filtered dropdown (derived from the
catalogue), printing every Further Maths paper's Core Pure 2 chapter 6 questions with their own schemes,
the teacher exam paper (questions only; questions and mark scheme) with its bundled fonts, and In paper
order printing. Results go to the private release work folder (qa-offline.json); finish.py requires it.
"""
import argparse
import functools
import http.server
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402
from qa_live import local_totals, dropdown_order, metadata  # noqa: E402
from playwright.sync_api import sync_playwright, expect  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PASSED = []
CP2_6 = 'further-maths-a-level/pure-core-2/6'


def ok(message):
    PASSED.append(message)
    print(message, flush=True)


def clear(p):
    """Clear the current paper selection (the button is disabled when nothing is selected)."""
    if p.locator('#papers-clear').is_enabled():
        p.locator('#papers-clear').click()


def printed(p, out, name, check=None):
    with p.expect_popup() as pop:
        p.locator('#papers-print').click()
    q = pop.value
    expect(q.get_by_role('button', name='Print / Save PDF')).to_be_enabled(timeout=60000)
    assert not q.locator('.print-errors').count()
    if check:
        check(q)
    assert q.locator('img').evaluate_all('ns=>ns.every(n=>n.complete&&n.naturalWidth>0)')
    q.pdf(path=str(out / f'offline-{name}.pdf'), prefer_css_page_size=True)
    q.close()


def run(url, out, channel):
    meta, cat = metadata()
    order = dropdown_order(meta)
    with sync_playwright() as w:
        b = w.chromium.launch(channel=None if channel == 'chromium' else channel)
        total_text, _ = local_totals(b)
        c = b.new_context()
        p = c.new_page()
        p.goto(url + 'offline.html')
        expect(p.locator('#status')).to_contain_text('Choose chapters below', timeout=60000)
        for book, chapter in (('pure-core-2', 6), ('maths-pure-year-2', 11)):
            p.locator('#book').select_option(book)
            card = p.locator('.chapter').filter(has=p.locator(f'input[aria-label$="chapter {chapter}"]'))
            card.locator('input').check()
            p.locator('#download').click()
            expect(p.locator('#status')).to_contain_text('Download complete', timeout=2400000)
            expect(card.locator('.ready')).to_contain_text('Ready offline')
        c.set_offline(True)
        p.goto(url + 'papers.html')
        expect(p.locator('#filter-title')).to_have_text(total_text)
        p.locator('#papers-source-practice').uncheck()
        p.locator('#papers-source-exam-style').uncheck()
        p.locator('#papers-course').select_option('further-maths-a-level')
        p.locator('#papers-book').select_option('further-maths-a-level/pure-core-2')
        p.locator(f'#papers-topics input[value="{CP2_6}"]').check()
        cp2 = [x['id'] for x in order if any(k.startswith('further-maths-a-level/pure-core-2/') for q in cat if q['paperId'] == x['id'] for k in q['chapterKeys'])]
        options = p.locator('#papers-past-paper option').evaluate_all('ns=>ns.map(n=>n.value)')
        assert options == [''] + cp2, options
        assert p.locator('#papers-course').evaluate('n=>n.classList.contains("filter-active")')
        ok('Offline PAP-068 paper dropdown follows Course and Book')
        for pid in cp2:
            ids = [q['id'] for q in cat if q['paperId'] == pid and CP2_6 in q['chapterKeys']]
            if not ids:
                continue
            clear(p)
            p.locator('#papers-past-paper').select_option(pid)
            expect(p.locator('#filter-title')).to_have_text(f'{len(ids)} questions in the selection')
            p.locator('#papers-browse').click()
            expect(p.locator('[data-add]')).to_have_count(min(len(ids), 8))
            expect(p.locator('[data-add]').first).to_have_attribute('data-add', ids[0])
            shown = p.locator('[data-add]').evaluate_all('ns=>ns.map(n=>n.dataset.add)')
            assert shown == ids[:8], (pid, shown)
            for x in shown:
                p.locator(f'[data-add="{x}"]').click()
            expect(p.locator('#papers-selected-count')).to_have_text(str(len(shown)))
            prefixes = tuple(f'{pid}/q{z}{int(x.rsplit("/q", 1)[1])}-ms-' for x in shown for z in ('', '0'))  # q6-ms- (older) or q06-ms-

            def own_schemes(q, prefixes=prefixes, pid=pid):
                srcs = q.locator('.solutions-page img').evaluate_all('ns=>ns.map(n=>n.getAttribute("src"))')
                assert srcs and all(any(x in s for x in prefixes) for s in srcs), (pid, srcs[:3])
            printed(p, out, pid, own_schemes)
            ok(f'Offline {pid} Core Pure 2 chapter 6 print with its own schemes passed')
        # Teacher exam paper offline (questions only; then questions and mark scheme).
        clear(p)
        p.locator('#papers-past-paper').select_option('edexcel-9fm0-02-2024-june')
        p.locator('#papers-browse').click()
        p.locator('[data-add="exam/edexcel-9fm0-02-2024-june/q1"]').click()
        expect(p.locator('#papers-selected-count')).to_have_text('1')
        p.locator('#papers-exam summary').click()
        p.locator('#papers-exam-title').fill('Offline Check')
        with p.expect_popup() as pop:
            p.locator('#papers-exam-print').click()
        q = pop.value
        expect(q.get_by_role('button', name='Print / Save PDF')).to_be_enabled(timeout=60000)
        assert not q.locator('.print-errors').count()
        assert q.locator('.exam-page').count() == 2 and q.locator('.exam-page .page-footer').all_text_contents() == ['Page 1 of 2', 'Page 2 of 2']
        expect(q.locator('.paper-total')).to_have_text('TOTAL FOR PAPER IS 7 MARKS')
        assert q.locator('.exam-heading h2').first.inner_text() == 'Question 1' and q.locator('.exam-course-map').count() == 0
        assert q.evaluate("document.fonts.check('bold 22pt KaTeX_Main') && document.fonts.check('11pt KaTeX_Main')"), 'bundled front-page font not loaded offline'
        q.pdf(path=str(out / 'offline-exam-paper.pdf'), prefer_css_page_size=True)
        q.close()
        p.locator('input[name="papers-exam-content"][value="both"]').check()
        with p.expect_popup() as pop:
            p.locator('#papers-exam-print').click()
        q = pop.value
        expect(q.get_by_role('button', name='Print / Save PDF')).to_be_enabled(timeout=60000)
        s = q.locator('.exam-scheme-page').count()
        assert s > 0 and q.locator('.exam-page').count() == 2
        assert q.locator('.exam-scheme-page .page-footer').all_text_contents() == [f'Mark scheme page {i} of {s}' for i in range(1, s + 1)]
        q.pdf(path=str(out / 'offline-exam-scheme.pdf'), prefer_css_page_size=True)
        q.close()
        ok('Offline teacher exam paper print passed (questions only, and questions and mark scheme)')
        # Cross-book pack: Pure Year 2 chapter 11, In paper order.
        clear(p)
        p.locator(f'#papers-topics input[value="{CP2_6}"]').uncheck()
        p.locator('#papers-course').select_option('maths-a-level')
        p.locator('#papers-book').select_option('maths-a-level/maths-pure-year-2')
        p.locator('#papers-topics input[value="maths-a-level/maths-pure-year-2/11"]').check()
        p.locator('#papers-past-paper').select_option('edexcel-9ma0-02-2025-june')
        expect(p.locator('#filter-title')).to_have_text('2 questions in the selection')
        p.locator('#papers-browse').click()
        p.locator('[data-add$="9ma0-02-2025-june/q15"]').click()
        def q15_images(q):
            assert q.locator('.solutions-page img').count() == 9 and q.locator('.print-question img').count() == 1
        printed(p, out, 'pure2-q15', q15_images)
        p.locator('[data-add$="9ma0-02-2025-june/q10"]').click()
        expect(p.locator('#papers-selected-count')).to_have_text('2')
        p.locator('#papers-order').select_option('selection')
        p.locator('#papers-order').select_option('paper')
        want = ['exam/edexcel-9ma0-02-2025-june/q10', 'exam/edexcel-9ma0-02-2025-june/q15']
        assert p.locator('[data-remove]').evaluate_all('ns=>ns.map(n=>n.dataset.remove)') == want
        def paper_order(q):
            assert q.locator('.questions-page .print-question').evaluate_all('ns=>[...new Set(ns.map(n=>n.dataset.questionId))]') == want
        printed(p, out, 'paper-order', paper_order)
        ok('Offline In paper order print passed')
        p.reload()
        expect(p.locator('#papers-selected-count')).to_have_text('2')
        ok('Offline selection survives reload')
        # NAV-091: the teacher exam mode opened above is restored after the reload; close it to return to the practice draft.
        expect(p.locator('#papers-exam')).to_have_js_property('open', True)
        p.locator('#papers-exam summary').click()
        expect(p.locator('#papers-exam')).to_have_js_property('open', False)
        ok('Offline exam mode restored after reload and closed to the practice draft')
        clear(p)
        p.locator('#papers-source-past-papers').uncheck()
        p.locator('#papers-source-madas').check()
        p.locator('#papers-browse').click()
        button = p.locator('[data-add^="madas/"]').first
        expect(button).to_be_visible()
        button.click()
        expect(p.locator('#papers-selected-count')).to_have_text('1')
        def madas_print(preview):
            expect(preview.locator('.solutions-page .scheme-credit').first).to_contain_text('Adapted MADAS')
            assert preview.locator('.madas-excerpt img').evaluate_all('ns=>ns.length>0&&ns.every(n=>n.complete&&n.naturalWidth)')
        printed(p, out, 'madas', madas_print)
        ok('Offline MADAS question and adapted scheme print from the downloaded chapter pack')
        b.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--url')
    parser.add_argument('--local', action='store_true')
    parser.add_argument('--channel', default=os.environ.get('LUISA_BROWSER_CHANNEL') or 'chromium')
    args = parser.parse_args()
    release = json.loads((ROOT / 'release.json').read_text())
    out = private.work_dir(release['version'])
    server = None
    if args.local:
        handler = functools.partial(type('H', (http.server.SimpleHTTPRequestHandler,), {'log_message': lambda *a: None}), directory=str(ROOT / 'dist'))
        server = type('S', (http.server.ThreadingHTTPServer,), {'request_queue_size': 128})(('127.0.0.1', 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/'
    else:
        url = (args.url or release['publicBaseUrl']).rstrip('/') + '/'
    try:
        run(url, out, args.channel)
    finally:
        if server:
            server.shutdown()
    rev = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    name = 'qa-offline-dry-run.json' if args.local else 'qa-offline.json'
    (out / name).write_text(json.dumps({'revision': rev, 'version': release['version'], 'passed': PASSED}, indent=1))
    print(json.dumps({'event': 'offline_qa_pass', 'checks': len(PASSED)}))


if __name__ == '__main__':
    main()
