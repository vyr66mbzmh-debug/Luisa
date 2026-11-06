#!/usr/bin/env python3
"""Portable static packaging and evidence gates. Python stdlib only."""
import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import tarfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = {'assets', 'content', 'printouts', 'resources', 'vendor'}
PUBLIC_SUFFIXES = {'.html', '.js', '.css', '.svg', '.webmanifest'}
PUBLIC_JSON = {'textbook-catalogue.json', 'version-history.json', 'release.json'}


def emit(event, **data):
    print(json.dumps({'event': event, **data}, ensure_ascii=False), flush=True)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def catalogue(root=ROOT):
    text = (root / 'teaching-catalogue.js').read_text()
    return json.loads(text.split('=', 1)[1].strip().rstrip(';'))


def resolve_local(root, url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    decoded = urllib.parse.unquote(parts.path)
    path = (root / decoded.lstrip('/')).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes website root')
    if path.is_dir():
        path = path / 'index.html'
    if not path.exists() and not path.suffix:
        path = path.with_suffix('.html')
    return path


def public_files(root=ROOT):
    for p in sorted(root.iterdir()):
        if p.is_symlink():
            raise ValueError('Symlink in website root: ' + p.name)
        if p.is_file() and (p.suffix in PUBLIC_SUFFIXES or p.name in PUBLIC_JSON or p.name in {'_headers', '_redirects'}):
            yield p
        elif p.is_dir() and p.name in PUBLIC_DIRS:
            for f in sorted(p.rglob('*')):
                if f.is_symlink():
                    raise ValueError('Symlink in public input: ' + str(f.relative_to(root)))
                if f.is_file() and not any(x.startswith('.') for x in f.relative_to(root).parts):
                    yield f


TEXT_SUFFIXES = {'.py', '.md', '.txt', '.json', '.js', '.css', '.html', '.svg', '.yml', '.yaml', '.webmanifest', '.toml'}


def source_files(root=ROOT, text_only=False):
    """Read committed blobs without hydrating cloud placeholders, then overlay edits."""
    changed = set(filter(None, subprocess.check_output(['git', '-C', str(root), 'diff', '--name-only', 'HEAD', '-z']).decode().split('\0')))
    changed.update(filter(None, subprocess.check_output(['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard', '-z']).decode().split('\0')))
    proc = subprocess.Popen(['git', '-C', str(root), 'archive', '--format=tar', 'HEAD'], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
            for member in archive:
                name = member.name
                if name in changed or not member.isfile() or (text_only and Path(name).suffix not in TEXT_SUFFIXES and not Path(name).name.startswith('.env') and Path(name).suffix not in {'.key', '.pem'}):
                    continue
                if Path(name).is_absolute() or '..' in Path(name).parts:
                    raise ValueError('Unsafe Git archive path')
                with archive.extractfile(member) as f:
                    yield name, f.read()
        if proc.wait() != 0:
            raise ValueError('Git archive failed')
    finally:
        if proc.poll() is None:
            proc.terminate()
        proc.wait()
        proc.stdout.close()
    for name in sorted(changed):
        path = root / name
        if not path.exists():
            continue
        if path.is_symlink():
            raise ValueError('Symlink in changed input: ' + name)
        if path.is_file() and (not text_only or path.suffix in TEXT_SUFFIXES or path.name.startswith('.env') or path.suffix in {'.key', '.pem'}):
            yield name, path.read_bytes()


def is_public(name):
    p = Path(name)
    return not any(x.startswith('.') for x in p.parts) and ((len(p.parts) == 1 and (p.suffix in PUBLIC_SUFFIXES or p.name in PUBLIC_JSON or p.name in {'_headers', '_redirects'})) or (len(p.parts) > 1 and p.parts[0] in PUBLIC_DIRS))


def render_requirements(root=ROOT):
    data = json.loads((root / 'docs/requirements/register.json').read_text())
    lines = ['# Luisa requirements and acceptance', '', 'Generated from register.json; edit the register, then run `python3 scripts/luisa.py requirements`.', '', 'Historical assertions are not current verification. See README.md in this folder for status definitions.', '', '| ID | Requirement | Scope | Implementation | Verification |', '|---|---|---|---|---|']
    for r in data['requirements']:
        def cell(v):
            return (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)).replace('|', '\\|').replace('\n', ' ')
        lines.append('| ' + ' | '.join((f"<a name='req-{r[k].lower()}'></a>" if k == 'id' else '') + cell(r[k]) for k in ('id', 'requirement', 'scope', 'implementation', 'verification')) + ' |')
    return '\n'.join(lines) + '\n'


def check(root=ROOT):
    errors = []
    data = json.loads((root / 'docs/requirements/register.json').read_text())
    seen = set()
    for r in data['requirements']:
        if r['id'] in seen:
            errors.append('Duplicate requirement: ' + r['id'])
        seen.add(r['id'])
        for k in ('id', 'requirement', 'scope', 'implementation', 'verification', 'acceptance', 'origin', 'evidence'):
            if k not in r:
                errors.append('Missing requirement field: ' + r['id'] + ':' + k)
        if r.get('verification') == 'verified' and not r.get('evidence'):
            errors.append('Verified requirement lacks evidence: ' + r['id'])
    if (root / 'docs/requirements/REQUIREMENTS.md').read_text() != render_requirements(root):
        errors.append('Generated requirements table is stale')
    destinations = []
    for book in catalogue(root).values():
        for chapter in book['chapters']:
            for kind in ('slides', 'booklet', 'pdf'):
                if chapter.get(kind):
                    destinations.append(chapter[kind])
    for book in json.loads((root / 'textbook-catalogue.json').read_text())['books']:
        for chapter in book['chapters']:
            for resource in chapter.get('resources', []):
                if resource.get('access') == 'available' and resource.get('url'):
                    destinations.append(resource['url'])
    for url in sorted(set(destinations)):
        try:
            p = resolve_local(root, url)
            if p is None:
                continue
            if not p.is_file():
                errors.append('Missing catalogue destination: ' + url)
            elif p.suffix.lower() == '.pdf':
                with p.open('rb') as f:
                    if f.read(5) != b'%PDF-':
                        errors.append('PDF destination is not PDF: ' + url)
        except ValueError:
            errors.append('Unsafe catalogue destination: ' + url)
    for path in public_files(root):
        if path.stat().st_size > 25 * 1024 * 1024:
            errors.append('Cloudflare file exceeds 25MiB: ' + str(path.relative_to(root)))
    if errors:
        for error in errors:
            emit('check_failure', message=error)
        raise SystemExit(1)
    emit('check_pass', requirements=len(seen), catalogue_destinations=len(set(destinations)))


def build(root=ROOT, output=None):
    output = Path(output or os.environ.get('LUISA_BUILD_DIR', root / 'dist')).resolve()
    # Only rebuild a marked dedicated output; never recursively remove an arbitrary path.
    if output == root.resolve() or root.resolve().is_relative_to(output) or output.is_symlink():
        raise ValueError('Unsafe build output')
    if output.exists() and any(output.iterdir()):
        if not (output / '.luisa-build').is_file():
            raise ValueError('Refusing to replace an unmarked output directory')
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / '.luisa-build').write_text('Generated static artifact; safe to rebuild.\n')
    entries = {}
    # Validate filesystem symlinks, but retrieve unchanged bytes from the Git object store.
    list(public_files(root))
    for name, content in source_files(root):
        if not is_public(name):
            continue
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        entries[name] = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    from offline_manifest import generate
    generate(output, entries, json.loads((root / 'release.json').read_text())['version'])
    revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip())
    manifest = {'schemaVersion': 1, 'revision': revision, 'dirty': dirty, 'version': json.loads((root / 'release.json').read_text())['version'], 'files': entries}
    (output / 'build-manifest.json').write_text(json.dumps(manifest, sort_keys=True, separators=(',', ':')) + '\n')
    emit('build_pass', files=len(entries), revision=revision, dirty=dirty)
    return output


def scan(root=ROOT):
    patterns = [re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'), re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'), re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}\b'), re.compile(r'\bAKIA[A-Z0-9]{16}\b')]
    errors = []
    count = 0
    for name, content in source_files(root, text_only=True):
        count += 1
        path = Path(name)
        if path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example') or path.suffix in {'.pem', '.key'}:
            errors.append(name)
        try:
            text = content.decode('utf-8')
        except UnicodeError:
            continue
        if any(p.search(text) for p in patterns):
            errors.append(name)
    if errors:
        for name in sorted(set(errors)):
            emit('scan_failure', file=name, message='Potential credential; value withheld')
        raise SystemExit(1)
    emit('scan_pass', files=count, limitation='Pattern scan only; full-history GitHub secret scanning is separate')


def serve(directory, port):
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise ValueError('Build or choose a valid static directory first')
    # SimpleHTTPRequestHandler follows symlinks; reject them before exposing files.
    if any(p.is_symlink() for p in directory.rglob('*')):
        raise ValueError('Refusing to serve a directory containing symlinks')
    import functools
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as server:
        signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=server.shutdown, daemon=True).start())
        emit('serving', host='127.0.0.1', port=port)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['requirements', 'check', 'build', 'test', 'scan', 'gate', 'serve'])
    parser.add_argument('--output')
    parser.add_argument('--directory', default='dist')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8778')))
    args = parser.parse_args()
    if args.command == 'requirements':
        (ROOT / 'docs/requirements/REQUIREMENTS.md').write_text(render_requirements())
        emit('requirements_generated')
    if args.command in ('check', 'gate'):
        check()
    if args.command in ('test', 'gate'):
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, check=True)
    if args.command in ('scan', 'gate'):
        scan()
    if args.command in ('build', 'gate'):
        build(output=args.output)
    if args.command == 'serve':
        serve(args.directory, args.port)


if __name__ == '__main__':
    main()
