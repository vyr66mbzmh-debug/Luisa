import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

app = load('luisa')
usage = load('usage')

class ToolingAcceptance(unittest.TestCase):
    def test_public_boundary_excludes_docs_secrets_and_private_materials_DEV_006(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ['index.html', '.env', 'AGENTS.md', 'README.md', 'release.json']:
                (root / name).write_text('x')
            (root / 'materials').mkdir()
            (root / 'materials/source.pdf').write_bytes(b'%PDF-')
            (root / 'assets').mkdir()
            (root / 'assets/logo.svg').write_text('<svg/>')
            names = {p.relative_to(root).as_posix() for p in app.public_files(root)}
            self.assertEqual(names, {'index.html', 'release.json', 'assets/logo.svg'})

    def test_symlink_input_is_rejected_OPS_007(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'index.html').symlink_to('/etc/hosts')
            with self.assertRaises(ValueError):
                list(app.public_files(root))

    def test_path_escape_and_fallback_destinations_FR_006(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ((root / 'teaching-chapters.html').resolve()).write_text('hello')
            self.assertEqual(app.resolve_local(root, 'teaching-chapters#x'), (root / 'teaching-chapters.html').resolve())
            self.assertIsNone(app.resolve_local(root, 'https://example.com/chapter.pdf'))
            for value in ['../private.pdf', '%2e%2e/private.pdf']:
                with self.assertRaises(ValueError):
                    app.resolve_local(root, value)

    def test_hash_detects_actual_content_change_OPS_007(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'chapter.pdf'
            p.write_bytes(b'%PDF-one')
            first = app.digest(p)
            self.assertEqual(first, hashlib.sha256(b'%PDF-one').hexdigest())
            p.write_bytes(b'%PDF-two')
            self.assertNotEqual(app.digest(p), first)

    def test_rebuild_refuses_owner_directory_OPS_007(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output = root / 'owner'
            output.mkdir()
            (output / 'keep.txt').write_text('preserve')
            with self.assertRaises(ValueError):
                app.build(root=root, output=output)
            self.assertEqual((output / 'keep.txt').read_text(), 'preserve')

    def test_generated_requirements_are_deterministic_DEV_001(self):
        self.assertEqual(app.render_requirements(), (ROOT / 'docs/requirements/REQUIREMENTS.md').read_text())
        data = json.loads((ROOT / 'docs/requirements/register.json').read_text())
        ids = [r['id'] for r in data['requirements']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn('B03', ids)
        self.assertIn('FR-012', ids)

    def test_git_source_overlay_preserves_edits_and_deletions_OPS_007(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'index.html').write_text('old')
            (root / 'gone.css').write_text('old')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Tooling', '-c', 'user.email=tooling@users.noreply.github.com', 'commit', '-qm', 'fixture'], check=True)
            (root / 'index.html').write_text('new')
            (root / 'gone.css').unlink()
            (root / 'release.json').write_text('{}')
            values = dict(app.source_files(root))
            self.assertEqual(values['index.html'], b'new')
            self.assertNotIn('gone.css', values)
            self.assertIn('release.json', values)

    def test_usage_does_not_invent_task_cost_DEV_005(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)
            args = dict(task='test-task', provider='example', model='unknown', remaining=80.0, reset_at='window1', tokens=None, artifacts=None, rework=None)
            usage.record(argparse.Namespace(action='start', **args), state)
            args.update(remaining=95.0, reset_at='window2')
            row = usage.record(argparse.Namespace(action='end', **args), state)
            self.assertIsNone(row['accountObservedDeltaPP'])
            self.assertIsNone(row['reportedTaskTokens'])
            self.assertGreaterEqual(row['elapsedSeconds'], 0)
            self.assertEqual(len((state / 'usage.jsonl').read_text().splitlines()), 2)

    def test_usage_preserves_same_window_observation_DEV_005(self):
        with tempfile.TemporaryDirectory() as d:
            args = dict(task='test-task', provider='example', model='unknown', remaining=80.0, reset_at='window1', tokens=None, artifacts=None, rework=None)
            usage.record(argparse.Namespace(action='start', **args), Path(d))
            args['remaining'] = 79
            row = usage.record(argparse.Namespace(action='end', **args), Path(d))
            self.assertEqual(row['accountObservedDeltaPP'], 1.0)
            self.assertIn('not exact', row['attribution'])

if __name__ == '__main__':
    unittest.main()
