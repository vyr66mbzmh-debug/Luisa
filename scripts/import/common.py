"""Shared paths and source checks for the past-paper import pipeline (see README.md).

An import set is a folder under scripts/import/sets/<name>/ holding the per-release inputs:
papers.py (PAPERS, ORDER), maps.py (MAPS), prompts/<paperId>.py, maths/<paperId>.py and the JSON
inputs figs.json, marks.json, qpends.json and checks.json. Source PDFs live outside Git in the folder
named by the private key `pastPaperSource` (or --source); work files go to <state>/import/<name>/.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts' / 'release'))
import private  # noqa: E402


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parser(doc, paper=True):
    p = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--set', required=True, help='import set name (folder in scripts/import/sets)')
    p.add_argument('--source', help='folder holding the source PDFs (default: private key pastPaperSource)')
    p.add_argument('--repo', default=str(ROOT), help='repository root to write into (default: this checkout)')
    if paper:
        p.add_argument('paper', help='paper id, e.g. edexcel-9ma0-01-sample')
    return p


class ImportSet:
    def __init__(self, args):
        self.name = args.set
        self.dir = HERE / 'sets' / args.set
        if not (self.dir / 'papers.py').is_file():
            raise SystemExit(f'No import set {args.set!r} (expected {self.dir.relative_to(ROOT)}/papers.py)')
        self.repo = Path(args.repo).resolve()
        mod = module(self.dir / 'papers.py', f'luisa_import_{self.name.replace("-", "_")}_papers')
        self.papers = mod.PAPERS
        self.order = getattr(mod, 'ORDER', None)
        self._source = args.source
        self.work = private.state_dir() / 'import' / self.name
        self.work.mkdir(parents=True, exist_ok=True)

    @property
    def source(self):
        return Path(self._source or private.get('pastPaperSource')).expanduser()

    def data(self, name):
        return json.loads((self.dir / name).read_text())

    def maps(self):
        return module(self.dir / 'maps.py', 'luisa_import_maps').MAPS

    def prompts(self, pid):
        return module(self.dir / 'prompts' / f'{pid}.py', 'luisa_import_prompts_' + pid.replace('-', '_'))

    def pdf(self, pid, kind):
        """Path of the owner source PDF (kind 'qp' or 'ms'), refused unless its SHA-256 is the recorded one."""
        path = self.source / self.papers[pid][kind]
        if not path.is_file():
            raise SystemExit(f'{pid} {kind.upper()} not found in the source folder (file {self.papers[pid][kind]!r})')
        if hashlib.sha256(path.read_bytes()).hexdigest() != self.papers[pid][kind + 'sha']:
            raise SystemExit(f'{pid} {kind.upper()} does not match its recorded SHA-256; never import an unverified copy')
        return path

    def assets_path(self, pid):
        return self.work / 'assets' / f'{pid}.json'
