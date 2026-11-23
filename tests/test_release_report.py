"""OPS-069: every report form carries exactly one handoff, headed with the release.json version."""
import html
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'release'))
import report  # noqa: E402

HANDOFF = '''# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v9.02 -->
**Release 9.02 · GitHub #900.** Fixture release block.
<!-- END LUISA-RELEASE-BLOCK -->

## Tooling, access and where everything lives
Fixture standing section with <angle> & ampersand.
'''
# The pre-v0.73 page shape: a stale marker, two handoff headings, and only the release block.
LEGACY_PAGE = ('<!doctype html><html><head><title>Luisa v9.01 release report</title></head><body><h1>Luisa v9.01 release report</h1>\n'
               '<p>old intro</p>\n'
               '<h2>Chapters</h2><table><tr><td>row</td></tr></table>'
               '<!-- LUISA-FULL-HANDOFF v8.59 --><section id="release-handoff"><h2>Version 8.59 handoff</h2><h2>Handoff</h2>'
               '<pre>&lt;!-- LUISA-REPORT-HANDOFF v9.01 --&gt;old</pre></section></body></html>\n')


class ReleaseReportTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / 'release.json').write_text(json.dumps({'version': '9.02', 'publicBaseUrl': 'https://owner.example.org'}))
        (self.root / 'version-history.json').write_text(json.dumps({'current': '9.02', 'releases': [
            {'version': '9.02', 'previous': '9.01', 'issue': 900, 'changes': ['Fixture change.'], 'requirements': ['OPS-069']}]}))
        (self.root / 'HANDOFF.md').write_text(HANDOFF)
        (self.root / 'development-progress.html').write_text(LEGACY_PAGE)

    def test_build_replaces_legacy_handoff_with_exactly_one_correct_block(self):
        text = report.build(self.root)
        self.assertEqual(report.check(self.root), [])
        self.assertEqual(text, (self.root / 'release-report-9.02.html').read_text())
        self.assertEqual(text.count('<section id="release-handoff">'), 1)
        self.assertEqual(re.findall(r'<h2>([^<]*[Hh]andoff[^<]*)</h2>', text), ['Luisa v9.02 handoff'])
        self.assertEqual(text.count(html.escape(HANDOFF.rstrip('\n'), quote=False)), 1)
        self.assertNotIn('8.59', text)
        self.assertNotIn('[LUISA-HANDOFF', text)
        self.assertIn('<title>Luisa v9.02 release report</title>', text)
        self.assertIn('/issues/900', text)

    def test_rebuild_is_idempotent(self):
        first = report.build(self.root)
        self.assertEqual(report.build(self.root), first)

    def test_student_edition_strip_removes_the_whole_handoff(self):
        text = report.build(self.root)
        stripped = re.sub(r'<section id="release-handoff">.*?</section>', '', text, flags=re.S)  # scripts/luisa.py build
        self.assertNotIn('LUISA-REPORT-HANDOFF', stripped)
        self.assertNotIn('Tooling, access', stripped)

    def test_defects_are_detected(self):
        good = report.build(self.root)
        cases = {
            'second heading': good.replace('<h2>Luisa v9.02 handoff</h2>', '<h2>Luisa v9.02 handoff</h2><h2>Handoff</h2>'),
            'stray paragraph': good.replace('<h2>Chapters</h2>', '<p>[LUISA-HANDOFF v9.02] see below</p><h2>Chapters</h2>'),
            'wrong marker': good.replace('<!-- LUISA-FULL-HANDOFF v9.02 -->', '<!-- LUISA-FULL-HANDOFF v8.59 -->'),
            'two sections': good + report.handoff_section('9.02', HANDOFF),
            'stale inner marker': good.replace('&lt;!-- LUISA-REPORT-HANDOFF v9.02 --&gt;', '&lt;!-- LUISA-REPORT-HANDOFF v9.01 --&gt;'),
            'private path': good.replace('Fixture change.', '/' + 'Users/someone/Library/x'),
            'email address': good.replace('Fixture change.', 'mail owner' + '@school.org.uk'),
        }
        for name, page in cases.items():
            with self.subTest(name):
                self.assertTrue(report.page_errors(page, '9.02', HANDOFF), name)

    def test_handoff_must_carry_one_marker_for_the_release_version(self):
        self.assertEqual(report.handoff_errors(HANDOFF, '9.02'), [])
        self.assertTrue(report.handoff_errors(HANDOFF, '9.03'))
        self.assertTrue(report.handoff_errors(HANDOFF + '<!-- LUISA-REPORT-HANDOFF v9.01 -->\n', '9.02'))
        self.assertTrue(report.handoff_errors(HANDOFF.replace('Fixture release', '[LUISA-HANDOFF v9.02] Fixture release'), '9.02'))
        with self.assertRaises(SystemExit):
            (self.root / 'HANDOFF.md').write_text(HANDOFF.replace('v9.02', 'v9.01'))
            report.build(self.root)

    def test_email_forms_have_one_handoff_and_absolute_links(self):
        report.build(self.root)
        out = self.root / 'out'
        out.mkdir()
        text_path, html_path = report.email(self.root, 'a' * 40, out, 'https://owner.example.org/', 'Owner intro paragraph for the fixture release.')
        body, page = text_path.read_text(), html_path.read_text()
        self.assertEqual(report.text_errors(body, '9.02', HANDOFF), [])
        self.assertEqual(report.page_errors(page, '9.02', HANDOFF), [])
        self.assertEqual(body.count('Luisa v9.02 handoff'), 1)
        self.assertNotIn('href="./', page)

    def test_repository_report_is_consistent(self):
        self.assertEqual(report.check(ROOT), [])


if __name__ == '__main__':
    unittest.main()
