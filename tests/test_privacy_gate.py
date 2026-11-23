"""OPS-065: the privacy gate blocks personal paths, private hosts/addresses, stray emails and owner source PDFs."""
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts' / 'release'))
import luisa  # noqa: E402
import private  # noqa: E402

SECRET_HOST = 'private-host.internal.example.net'
SOURCE_PDF = b'%PDF-1.4 fixture owner source paper'


class PrivacyGateTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / 'docs/security').mkdir(parents=True)
        (self.root / 'docs/security/private-hashes.json').write_text(json.dumps({'sha256': [hashlib.sha256(SECRET_HOST.encode()).hexdigest()]}))
        (self.root / 'content/exams').mkdir(parents=True)
        (self.root / 'content/exams/pilot-metadata.json').write_text(json.dumps({'papers': [
            {'source': {'questionPaperSha256': hashlib.sha256(SOURCE_PDF).hexdigest()}}]}))
        (self.root / 'README.md').write_text('Clean fixture. Contact noreply@anthropic.com. Site https://owner.example.org/.\n')
        self.git('init', '-q')
        self.commit()

    def git(self, *args):
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=t', '-c', 'user.email=t@example.com', *args], check=True, capture_output=True)

    def commit(self):
        self.git('add', '-A')
        self.git('commit', '-qm', 'fixture', '--allow-empty')

    def gate(self, values=()):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            try:
                luisa.privacy(self.root, workspace_values=set(values))
                return True, out.getvalue()
            except SystemExit:
                return False, out.getvalue()

    def test_clean_repository_passes(self):
        self.assertEqual(self.gate()[0], True)

    def test_blocked_content(self):
        cases = {
            'personal path': ('notes.md', 'see /' + 'Users/someone/Library/CloudStorage/file.pptx'),
            'windows path': ('notes.md', 'C:\\\\' + 'Users\\\\someone\\\\file'),
            'hashed private host': ('scripts/x.py', f'HOST = "{SECRET_HOST.upper()}"'),
            'email in docs': ('docs/notes.md', 'write to owner' + '@school.org.uk'),
            'local private value': ('data.json', '{"x": "an-exact-private-value"}'),
            'subdomain of a hashed host': ('index.html', f'<a href="https://ada.{SECRET_HOST}/">x</a>'),
            'email at a hashed host in shipped js': ('app.js', f'const to = "owner@{SECRET_HOST}";'),
            'hashed host in a .cjs file': ('x.cjs', f'module.exports = "{SECRET_HOST}";'),
            'hashed host in a shell script': ('run.sh', f'ssh {SECRET_HOST}'),
            'hashed host in .gitignore': ('.gitignore', f'{SECRET_HOST}/'),
            'personal path in an extensionless file': ('Makefile', 'cd /' + 'Users/someone/x'),
            'bare home path': ('notes.md', 'cd /' + 'Users/someone'),
        }
        for name, (path, text) in cases.items():
            with self.subTest(name):
                target = self.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
                passed, output = self.gate({'an-exact-private-value'})
                self.assertFalse(passed, name)
                self.assertIn('value withheld', output)
                self.assertNotIn(SECRET_HOST, output)
                self.assertNotIn('an-exact-private-value', output)
                target.unlink()
        self.assertTrue(self.gate({'an-exact-private-value'})[0])

    def test_unreadable_private_configuration_fails_instead_of_passing(self):
        import os
        state = self.root / 'state'
        state.mkdir()
        (state / 'WORKSPACE.json').write_text('{not json')
        old = os.environ.get('LUISA_STATE_DIR')
        os.environ['LUISA_STATE_DIR'] = str(state)
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit):
                luisa.privacy(self.root)
            self.assertIn('private configuration unreadable', out.getvalue())
        finally:
            if old is None:
                os.environ.pop('LUISA_STATE_DIR')
            else:
                os.environ['LUISA_STATE_DIR'] = old

    def test_committed_and_untracked_source_pdfs_are_blocked(self):
        (self.root / 'docs').mkdir(exist_ok=True)
        (self.root / 'docs/paper.pdf').write_bytes(SOURCE_PDF)
        self.assertFalse(self.gate()[0])
        self.commit()
        self.assertFalse(self.gate()[0])

    def test_pdfs_in_past_paper_content_are_blocked(self):
        (self.root / 'resources/exams/x').mkdir(parents=True)
        (self.root / 'resources/exams/x/q01.pdf').write_bytes(b'%PDF-1.4 other')
        self.assertFalse(self.gate()[0])

    def test_test_fixture_emails_are_outside_the_email_scope(self):
        (self.root / 'tests').mkdir()
        (self.root / 'tests/test_auth.py').write_text('EMAIL = "01234@school.example.org"\n')
        self.assertTrue(self.gate()[0])

    def test_private_values_skip_public_and_generic_values(self):
        data = {'ada': {'url': 'https://public.example.org', 'pupilEmailDomain': 'school.example.org', 'serviceName': 'student',
                        'sshHost': 'user@ssh.private.example.net', 'layout': {'releaseRoot': '/srv/apps/private/releases'}},
                'mailSender': 'send_report.py', 'note': 'plain words only'}
        values = private.private_values(data)
        self.assertIn('user@ssh.private.example.net', values)
        self.assertIn('/srv/apps/private/releases', values)
        for public in ('https://public.example.org', 'school.example.org', 'student', 'send_report.py', 'plain words only'):
            self.assertNotIn(public, values)

    def test_repository_passes_the_privacy_gate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            luisa.privacy(ROOT, workspace_values=set())


if __name__ == '__main__':
    unittest.main()
