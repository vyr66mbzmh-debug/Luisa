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
            for kind in ('slides', 'booklet', 'solutions', 'pdf'):
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


def student_restricted_pdfs(root):
    """Return every textbook extract and byte-identical alias in the student edition."""
    urls = set()
    teaching = json.loads((root / 'teaching-catalogue.js').read_text().split('=', 1)[1].strip().rstrip(';'))
    for book in teaching.values():
        for chapter in book['chapters']:
            if chapter.get('pdf'):
                urls.add(urllib.parse.urlsplit(chapter['pdf']).path.lstrip('/'))
    textbook = json.loads((root / 'textbook-catalogue.json').read_text())
    for book in textbook['books']:
        for chapter in book['chapters']:
            for item in chapter.get('resources', []):
                if item.get('type') == 'pdf' and item.get('url'):
                    urls.add(urllib.parse.urlsplit(item['url']).path.lstrip('/'))
    data_text = (root / 'lesson-resources-data.js').read_text()
    # These paths are embedded in the generated skill toolbar catalogue.
    for path in re.findall(r"['\"]((?:resources/)[^'\"]+\.pdf)['\"]", data_text):
        if '/chapters/' in path or '/textbook/' in path:
            urls.add(path)
    hashes = set()
    for name in urls:
        path = root / name
        if path.is_file():
            hashes.add(digest(path))
    return urls, hashes


def student_content(name, content, restricted_urls, restricted_hashes, root):
    """Apply student-only interface and catalogue changes to a copied source blob."""
    path = Path(name)
    if path.name in {'teaching-catalogue.js', 'lesson-resources-data.js'}:
        text = content.decode('utf-8')
        if path.name == 'teaching-catalogue.js':
            data = json.loads(text.split('=', 1)[1].strip().rstrip(';'))
            for book in data.values():
                for chapter in book['chapters']:
                    chapter.pop('pdf', None)
            text = 'const LUISA_TEACHING=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
        else:
            # Remove source PDF destinations from the toolbar mapping while preserving skill/chapter mappings.
            text = re.sub(r"pdf\s*:\s*(['\"])[^'\"]+\1\s*,?", '', text)
            text = re.sub(r"['\"]pdf['\"]\s*:\s*(['\"])[^'\"]+\1\s*,?", '', text)
        return text.encode('utf-8')
    if path.name == 'textbook-catalogue.json':
        data = json.loads(content)
        for book in data['books']:
            for chapter in book['chapters']:
                chapter['resources'] = [r for r in chapter.get('resources', []) if r.get('type') != 'pdf']
        return (json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    if path.name == 'teaching-chapters.html':
        text = content.decode('utf-8').replace(",['Book chapter','pdf']", '')
        content = text.encode('utf-8')
    if path.name == 'textbook-view.js':
        text = content.decode('utf-8').replace('Available teaching slides, book chapters and handouts remain accessible above.', 'Available teaching slides and handouts remain accessible above.')
        content = text.encode('utf-8')
    if path.name == 'index.html':
        text = content.decode('utf-8')
        text = re.sub(r'<a\b(?=[^>]*id=["\']book-chapter["\'])[^>]*>.*?</a\s*>', '', text, flags=re.I|re.S)
        content = text.encode('utf-8')
    if path.name == 'lesson-resources.js':
        text = content.decode('utf-8')
        text = text.replace("book.onclick=e=>choose(e,bookKey);", "if(book)book.onclick=e=>choose(e,bookKey);")
        text = text.replace("setLink(book,bookKey);", "if(book)setLink(book,bookKey);")
        return text.encode('utf-8')
    if path.name == 'release.json':
        data = json.loads(content)
        data['edition'] = 'student'
        data['version'] = '0.40'
        data['publicBaseUrl'] = ''
        data.pop('repository', None)
        data['note'] = 'Online student edition; content requires authenticated server delivery.'
        return (json.dumps(data, indent=2) + '\n').encode()
    if path.suffix == '.json':
        try:
            data = json.loads(content)
        except (UnicodeError, json.JSONDecodeError):
            return content
        def restricted(value):
            url = urllib.parse.urlsplit(value)
            target = root / url.path.lstrip('/')
            return url.path.lstrip('/') in restricted_urls or (target.is_file() and digest(target) in restricted_hashes)
        def scrub(value):
            if isinstance(value, dict):
                for key in list(value):
                    item = value[key]
                    if isinstance(item, str) and (item.startswith('https://github.com/vyr66mbzmh-debug/Luisa') or
                                                  item.startswith('https://fmq-6d9.pages.dev') or
                                                  item.startswith('https://adazmq.marlboroughcollege.org')):
                        del value[key]
                    elif isinstance(item, str) and item.lower().split('?', 1)[0].split('#', 1)[0].endswith('.pdf') and restricted(item):
                        del value[key]
                    else:
                        scrub(item)
            elif isinstance(value, list):
                for i in range(len(value) - 1, -1, -1):
                    item = value[i]
                    if isinstance(item, str) and (item.startswith('https://github.com/vyr66mbzmh-debug/Luisa') or
                                                  item.startswith('https://fmq-6d9.pages.dev') or
                                                  item.startswith('https://adazmq.marlboroughcollege.org')):
                        del value[i]
                    elif isinstance(item, str) and item.lower().split('?', 1)[0].split('#', 1)[0].endswith('.pdf') and restricted(item):
                        del value[i]
                    else:
                        scrub(item)
        scrub(data)
        return (json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    if path.name == 'sw.js':
        # One-time migration worker: remove old Luisa offline packs then unregister itself.
        return ("self.addEventListener('install',e=>e.waitUntil(self.skipWaiting()));\n"
                "self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith('luisa-offline-v1-'+encodeURIComponent(new URL(self.registration.scope).pathname)+'-'))await caches.delete(k);await self.clients.claim();await self.registration.unregister();})()));\n").encode()
    if path.suffix in {'.html', '.js', '.json', '.webmanifest'}:
        try:
            text = content.decode('utf-8')
        except UnicodeError:
            return content
        if path.suffix == '.html':
            text = re.sub(r'<script\b[^>]*offline-register\.js[^>]*>\s*</script\s*>', '', text, flags=re.I)
            text = re.sub(r'<link\b[^>]*rel=["\']manifest["\'][^>]*>', '', text, flags=re.I)
            text = re.sub(r'<a\b(?=[^>]*href=["\'][^"\']*offline\.html[^"\']*["\'])[^>]*>.*?</a\s*>', '', text, flags=re.I|re.S)
            text = re.sub(r'<a\b(?=[^>]*href=["\']https://(?:fmq-6d9\.pages\.dev|adazmq\.marlboroughcollege\.org)[^"\']*["\'])[^>]*>.*?</a\s*>', '', text, flags=re.I|re.S)
            text = re.sub(r'<a\b(?=[^>]*href=["\']https://github\.com/vyr66mbzmh-debug/Luisa[^"\']*["\'])[^>]*>.*?</a\s*>', '', text, flags=re.I|re.S)
            text = re.sub(r'<a\b(?=[^>]*href=["\']https://classpad\.net/note/[^"\']*["\'])[^>]*>.*?</a\s*>', '', text, flags=re.I|re.S)
            def remove_restricted_anchor(match):
                href = re.search(r'href=["\']([^"\']+)', match.group(0), flags=re.I)
                if not href:
                    return match.group(0)
                value = href.group(1)
                url = urllib.parse.urlsplit(value)
                target_name = url.path.lstrip('/')
                target = root / target_name
                if target_name in restricted_urls or (target.is_file() and digest(target) in restricted_hashes):
                    return ''
                return match.group(0)
            text = re.sub(r'<a\b[^>]*>.*?</a\s*>', remove_restricted_anchor, text, flags=re.I|re.S)
            text = re.sub(r'(<html\b[^>]*)(>)', r'\1 data-luisa-edition="student"\2', text, count=1, flags=re.I)
            text = re.sub(r"""<a\b[^>]*href=["'][^"']*development-progress\.html(?:[?#][^"']*)?["'][^>]*>.*?</a>""", '', text, flags=re.I|re.S)
            logout = '../' * (len(path.parts) - 1) + 'logout'
            account_link = f'<a class="luisa-signout" target="_top" href="{logout}" style="color:inherit;white-space:nowrap;margin-left:auto"><!--luisa-account-name-->Sign out</a>'
            if '</header>' in text:
                end = text.index('</header>')
                if path == Path('index.html'):
                    end = text.rindex('</div>', 0, end)
                text = text[:end] + account_link + text[end:]
            else:
                nav = '<nav style="text-align:right;padding:.5rem 1rem">' + account_link + '</nav>'
                text, count = re.subn(r'<body\b[^>]*>', lambda m: m[0] + nav, text, count=1, flags=re.I)
                if not count:
                    text = text.replace('</head>', '</head>' + nav, 1) if '</head>' in text else nav + text
        if path.name == 'app.js':
            registration = "if('serviceWorker' in navigator&&location.protocol!=='file:')navigator.serviceWorker.register('sw.js').catch(()=>{});"
            cleanup = """if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  const scope = new URL('./', location.href);
  const cachePrefix = 'luisa-offline-v1-' + encodeURIComponent(scope.pathname) + '-';
  navigator.serviceWorker.getRegistrations().then(registrations => {
    for (const registration of registrations) {
      const worker = registration.active || registration.waiting || registration.installing;
      if (registration.scope === scope.href && worker?.scriptURL === new URL('sw.js', scope).href) registration.unregister();
    }
  }).catch(() => {});
  caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith(cachePrefix)).map(key => caches.delete(key)))).catch(() => {});
}"""
            text = text.replace(registration, cleanup)
        if path.name == 'manifest.webmanifest':
            return b'{}\n'
        return text.encode('utf-8')
    return content


def build(root=ROOT, output=None, profile='owner'):
    if profile not in {'owner', 'student'}:
        raise ValueError('Build profile must be owner or student')
    output = Path(output or os.environ.get('LUISA_BUILD_DIR', root / ('dist-student' if profile == 'student' else 'dist'))).resolve()
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
    restricted_urls, restricted_hashes = student_restricted_pdfs(root) if profile == 'student' else (set(), set())
    # Validate filesystem symlinks, but retrieve unchanged bytes from the Git object store.
    list(public_files(root))
    for name, content in source_files(root):
        if not is_public(name):
            continue
        if profile == 'student':
            path = Path(name)
            if name in restricted_urls or (path.suffix.lower() == '.pdf' and hashlib.sha256(content).hexdigest() in restricted_hashes):
                continue
            if path.name == 'offline.html' or path.name.startswith('offline') or path.name == 'manifest.webmanifest':
                continue
            content = student_content(name, content, restricted_urls, restricted_hashes, root)
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        entries[name] = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    from print_downloads import prepare_print_downloads
    prepare_print_downloads(output, entries)
    if profile == 'owner':
        from offline_manifest import generate
        generate(output, entries, json.loads((root / 'release.json').read_text())['version'])
    revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip())
    release_file = output / 'release.json'
    manifest = {'schemaVersion': 1, 'revision': revision, 'dirty': dirty, 'edition': profile, 'version': json.loads(release_file.read_text())['version'], 'files': entries}
    (output / 'build-manifest.json').write_text(json.dumps(manifest, sort_keys=True, separators=(',', ':')) + '\n')
    emit('build_pass', files=len(entries), revision=revision, dirty=dirty, edition=profile)
    return output


def check_artifact(directory, profile, root=ROOT):
    directory = Path(directory).resolve()
    manifest_path = directory / 'build-manifest.json'
    if not manifest_path.is_file():
        raise ValueError('Artifact is missing build-manifest.json')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('edition') != profile:
        raise ValueError(f'Expected {profile} artifact, got {manifest.get("edition")}')
    files = set(manifest.get('files', {}))
    library = json.loads((directory / 'data.js').read_text().split('=', 1)[1].strip().rstrip(';'))
    downloads = library['printDownloads']
    if not downloads or len(downloads) != len(set(downloads.values())):
        raise ValueError('Missing or ambiguous named print downloads')
    for source, alias in downloads.items():
        if source not in files or alias not in files or manifest['files'][source] != manifest['files'][alias]:
            raise ValueError('Named PDF differs from its original: ' + alias)
    if profile == 'student':
        restricted_urls, restricted_hashes = student_restricted_pdfs(root)
        forbidden_names = [n for n in files if n in restricted_urls]
        forbidden_hashes = [n for n in files if Path(n).suffix.lower() == '.pdf' and (directory / n).is_file() and digest(directory / n) in restricted_hashes]
        if forbidden_names or forbidden_hashes:
            raise ValueError('Student artifact contains textbook chapter PDF files')
        if any(Path(n).name == 'offline.html' or Path(n).name.startswith('offline') or Path(n).name == 'manifest.webmanifest' for n in files):
            raise ValueError('Student artifact contains offline pack files')
        student_release = json.loads((directory / 'release.json').read_text())
        if student_release.get('edition') != 'student' or student_release.get('version') != '0.40' or student_release.get('publicBaseUrl') or 'repository' in student_release:
            raise ValueError('Student release metadata exposes an owner edition route or incorrect profile version')
        for name in files:
            path = directory / name
            if path.suffix.lower() in {'.html', '.json', '.js'}:
                text = path.read_text(errors='ignore')
                if path.suffix == '.html' and (text.count('class="luisa-signout"') != 1 or
                        re.search(r'''href=["'][^"']*development-progress\.html''', text, re.I)):
                    raise ValueError('Student navigation is missing sign-out or exposes the development report: ' + name)
                if re.search(r'(?:fmq-6d9\.pages\.dev|adazmq\.marlboroughcollege\.org|github\.com/vyr66mbzmh-debug/Luisa|classpad\.net/note/)', text, re.I):
                    raise ValueError('Student artifact contains a direct owner/CG100 link: ' + name)
                if re.search(r'href=["\'][^"\']*offline\.html', text, re.I):
                    raise ValueError('Student artifact contains an offline page link: ' + name)
                for match in re.finditer(r'(?:(?:resources|printouts)/)[A-Za-z0-9._/-]+\.pdf', text, re.I):
                    source = root / match.group(0)
                    if source.is_file() and digest(source) in restricted_hashes:
                        raise ValueError('Student artifact references a textbook chapter PDF: ' + name)
                if re.search(r'navigator\.serviceWorker\.register\s*\(', text):
                    raise ValueError('Student artifact registers an offline service worker: ' + name)
        for name in ('index.html', 'teaching-chapters.html'):
            text = (directory / name).read_text()
            if 'id="book-chapter"' in text or "['Book chapter','pdf']" in text:
                raise ValueError('Student interface exposes a textbook chapter control: ' + name)
        index = (directory / 'index.html').read_text()
        for control in ('id="textbook-view-link"', 'id="print-topic"', 'id="print-skill"', 'id="skill-solutions"'):
            if control not in index:
                raise ValueError('Student interface is missing a retained control: ' + control)
        source_textbook = json.loads((root / 'textbook-catalogue.json').read_text())
        expected_textbook = json.loads(json.dumps(source_textbook))
        for book in expected_textbook['books']:
            for chapter in book['chapters']:
                chapter['resources'] = [r for r in chapter.get('resources', []) if r.get('type') != 'pdf']
        student_textbook = json.loads((directory / 'textbook-catalogue.json').read_text())
        if student_textbook != expected_textbook:
            raise ValueError('Student textbook profile changed retained exercise or Luisa resource catalogue data')
        source_teaching = json.loads((root / 'teaching-catalogue.js').read_text().split('=', 1)[1].strip().rstrip(';'))
        expected_teaching = json.loads(json.dumps(source_teaching))
        for book in expected_teaching.values():
            for chapter in book['chapters']:
                chapter.pop('pdf', None)
        student_teaching = json.loads((directory / 'teaching-catalogue.js').read_text().split('=', 1)[1].strip().rstrip(';'))
        if student_teaching != expected_teaching:
            raise ValueError('Student teaching catalogue changed retained Luisa resources')
        source_lesson = json.loads((root / 'lesson-resources-data.js').read_text().split('=', 1)[1].strip().rstrip(';'))
        def strip_pdf_fields(value):
            if isinstance(value, dict):
                return {k: strip_pdf_fields(v) for k, v in value.items() if k != 'pdf'}
            if isinstance(value, list):
                return [strip_pdf_fields(v) for v in value]
            return value
        student_lesson = json.loads((directory / 'lesson-resources-data.js').read_text().split('=', 1)[1].strip().rstrip(';'))
        if student_lesson != strip_pdf_fields(source_lesson):
            raise ValueError('Student skill toolbar changed retained chapter/resource mappings')
        book_data = json.loads((directory / 'textbook-catalogue.json').read_text())
        retained = {'slides': 0, 'booklet': 0, 'solutions': 0, 'practice': 0}
        for book in book_data['books']:
            for chapter in book['chapters']:
                for resource in chapter.get('resources', []):
                    if resource.get('type') in retained and resource.get('access') == 'available' and resource.get('url'):
                        target = resolve_local(directory, resource['url'])
                        if target and target.is_file():
                            retained[resource['type']] += 1
        missing = [kind for kind, count in retained.items() if not count]
        if missing:
            raise ValueError('Student artifact lacks retained teaching/practice routes: ' + ', '.join(missing))
        if not any((directory / 'printouts').rglob('*.pdf')):
            raise ValueError('Student artifact is missing Print topic/skill PDF routes')
    return manifest


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
    parser.add_argument('command', choices=['requirements', 'check', 'build', 'check-artifact', 'test', 'scan', 'gate', 'serve'])
    parser.add_argument('--output')
    parser.add_argument('--profile', choices=['owner', 'student'], default='owner')
    parser.add_argument('--directory', default='dist')
    parser.add_argument('--host-profile', choices=['owner', 'student'])
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
        build(output=args.output, profile=args.profile)
    if args.command == 'serve':
        serve(args.directory, args.port)
    if args.command == 'check-artifact':
        manifest = check_artifact(args.directory, args.host_profile or args.profile)
        emit('artifact_check_pass', edition=manifest['edition'], version=manifest['version'], revision=manifest['revision'])


if __name__ == '__main__':
    main()
