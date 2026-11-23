"""OPS-064, OPS-066, OPS-067, OPS-068: release tooling is in Git, engine-neutral, pinned, and self-describing."""
import contextlib
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts' / 'release'))
import land  # noqa: E402
import doctor  # noqa: E402

TOOLING = ['scripts/release/' + n for n in ('private.py', 'report.py', 'ada.py', 'land_build.py', 'verify_owner.py', 'qa_live.py',
                                            'qa_offline.py', 'finish.py', 'tokens.py', 'docs.py', 'doctor.py', 'README.md')]
TOOLING += ['scripts/bootstrap.py', 'requirements-tools.txt', 'scripts/import/README.md', 'docs/agentic/RELEASE-RUNBOOK.md',
            'docs/agentic/review-record.schema.json', 'docs/security/private-hashes.json', 'docs/handoff/HISTORY.md']


def script_sources():
    for path in sorted((ROOT / 'scripts').rglob('*.py')):
        if '__pycache__' not in path.parts and 'work' not in path.parts:
            yield path, path.read_text()


class ReleaseToolingTests(unittest.TestCase):
    def test_release_tooling_is_tracked(self):
        tracked = set(subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard'], text=True).split('\n'))
        self.assertEqual([p for p in TOOLING if p not in tracked], [])

    def test_scripts_do_not_need_ripgrep_node_or_string_waits(self):
        for path, text in script_sources():
            with self.subTest(str(path.relative_to(ROOT))):
                for pattern, why in ((r"""['"]rg['"]|\brg -""", 'ripgrep is not part of the environment'),
                                     (r"""\[\s*['"](?:node|npx|npm)['"]""", 'Node is not assumed by tooling'),
                                     (r'wait_for_function\(\s*f?[\'"]', 'string-evaluated waits break under CSP; use locators')):
                    found = re.search(pattern, text)
                    self.assertIsNone(found, f'{why}: {found and text[max(0, found.start() - 40):found.end() + 20]!r}')

    def test_repository_code_has_no_personal_absolute_paths(self):
        for path, text in script_sources():
            with self.subTest(str(path.relative_to(ROOT))):
                self.assertNotRegex(text, r'(?:/Users|/home)/(?!runner/)[A-Za-z0-9._-]+/')
                self.assertNotIn('/tmp/luisa', text)

    def test_tool_requirements_are_exact_pins(self):
        lines = [l for l in (ROOT / 'requirements-tools.txt').read_text().splitlines() if l.strip() and not l.startswith('#')]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r'^[A-Za-z0-9_.-]+==[0-9][0-9A-Za-z.]*$')
        names = {l.split('==')[0].lower() for l in lines}
        self.assertLessEqual({'playwright', 'pymupdf', 'nodejs-wheel', 'sympy', 'flask'}, names)

    def test_review_record_schema_and_validator_agree(self):
        schema = json.loads((ROOT / 'docs/agentic/review-record.schema.json').read_text())
        self.assertEqual(set(schema['required']), {'head', 'base', 'verdict', 'findings', 'review'})
        good = {'head': 'a' * 40, 'base': 'b' * 40, 'verdict': 'ship', 'review': 'Checked the whole diff, tests and the built artifact.',
                'findings': [{'severity': 'low', 'where': 'scripts/x.py:1', 'issue': 'typo', 'resolution': 'fixed'}]}
        self.assertEqual(land.review_errors(good), [])
        for broken in ({**good, 'verdict': 'maybe'}, {**good, 'head': 'abc'}, {k: v for k, v in good.items() if k != 'findings'},
                       {**good, 'findings': [{'severity': 'urgent', 'where': 'x', 'issue': 'y'}]}, {**good, 'review': 'ok'}):
            self.assertTrue(land.review_errors(broken))

    def test_vendor_files_only_point_to_agents(self):
        for name in ('CLAUDE.md', 'GEMINI.md', '.github/copilot-instructions.md', '.cursorrules'):
            path = ROOT / name
            if path.exists():
                text = path.read_text()
                self.assertIn('AGENTS.md', text, name)
                self.assertLess(len(text.splitlines()), 6, f'{name} must stay a pointer, not a second rulebook')
        agents = (ROOT / 'AGENTS.md').read_text()
        self.assertIn('## Quick start for any AI agent', agents)
        self.assertIn('docs/agentic/RELEASE-RUNBOOK.md', agents)
        self.assertIn('docs/agentic/RELEASE-RUNBOOK.md', (ROOT / 'HANDOFF.md').read_text())
        self.assertIn('## Tooling, access and where everything lives', (ROOT / 'HANDOFF.md').read_text())

    def test_doctor_lines_name_status_and_action(self):
        doctor.RESULTS.clear()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            doctor.item('Thing', True, 'detail')
            doctor.item('Other thing', False, '', 'do this')
            doctor.item('Nice to have', False, '', 'maybe', optional=True)
        lines = out.getvalue().splitlines()
        self.assertEqual(lines[0], 'PASS     Thing — detail')
        self.assertEqual(lines[1:3], ['MISSING  Other thing', '         action: do this'])
        self.assertTrue(lines[3].startswith('OPTIONAL Nice to have'))
        self.assertEqual(doctor.RESULTS, ['PASS', 'MISSING', 'OPTIONAL'])
        doctor.RESULTS.clear()

    def test_runbook_covers_every_release_step(self):
        runbook = (ROOT / 'docs/agentic/RELEASE-RUNBOOK.md').read_text()
        for needle in ('bootstrap.py', 'luisa.py doctor', 'luisa.py gate', 'review-record.schema.json', 'land_build.py', 'verify_owner.py',
                       'ada.py stage', 'ada.py activate', 'ada.py rollback', 'qa_live.py ada', 'accounts-check', 'finish.py archive',
                       'finish.py report', 'finish.py complete', 'scripts/usage.py', 'tokens.py', 'PROGRESS.md', 'docs.py apply'):
            self.assertIn(needle, runbook, needle)
        steps = [int(n) for n in re.findall(r'^(\d+)\. ', runbook, re.M)]
        self.assertGreaterEqual(len(steps), 15)


if __name__ == '__main__':
    unittest.main()
