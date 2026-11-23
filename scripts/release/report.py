#!/usr/bin/env python3
"""Build and check the Luisa release report (OPS-069, OPS-070).

The report exists in three forms: the website page (development-progress.html, copied to
release-report-<version>.html), a plain-text body and an HTML email body. Every form carries
exactly one handoff: the whole of HANDOFF.md, under the heading "Luisa v<version> handoff",
where <version> comes from release.json. HANDOFF.md must start its release block with the marker
<!-- LUISA-REPORT-HANDOFF v<version> --> for the same version.

Usage:
  python3 scripts/release/report.py build            # rewrite development-progress.html and release-report-<v>.html
  python3 scripts/release/report.py check            # check both pages (also run by the gate)
  python3 scripts/release/report.py email --revision <sha> --out <dir>   # write report.txt and report.html for SMTP
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = 'https://github.com/vyr66mbzmh-debug/Luisa'
MARKER = re.compile(r'<!-- LUISA-REPORT-HANDOFF v(\d+\.\d+) -->')
SECTION = re.compile(r'<!-- LUISA-FULL-HANDOFF v[^>]*-->\s*<section id="release-handoff">.*?</section>', re.S)
LEGACY_SECTION = re.compile(r'<!-- LUISA-FULL-HANDOFF v[^>]*-->\s*<section id="release-handoff">.*</pre>', re.S)
STATUS_STYLE = [('status-complete', '#dff2df'), ('status-progress', '#fff0c2'), ('status-not-started', '#f8dddd')]


def version(root=ROOT):
    return json.loads((root / 'release.json').read_text())['version']


def handoff_markdown(root=ROOT):
    return (root / 'HANDOFF.md').read_text()


def heading(v):
    return f'Luisa v{v} handoff'


def handoff_section(v, markdown):
    return (f'<!-- LUISA-FULL-HANDOFF v{v} --><section id="release-handoff"><h2>{heading(v)}</h2>'
            f'<pre style="white-space:pre-wrap">{html.escape(markdown.rstrip(chr(10)), quote=False)}</pre></section>')


def intro(root, v):
    history = json.loads((root / 'version-history.json').read_text())
    entry = next(r for r in history['releases'] if r['version'] == v)
    paragraphs = entry.get('reportIntro') or entry['changes'][:2]
    out = [f'<p>{html.escape(p, quote=False)}</p>' for p in paragraphs]
    links = ['<a href="./version-history.html">version history</a>']
    if entry.get('issue'):
        links.append(f'<a href="{REPOSITORY}/issues/{entry["issue"]}">implementation and release evidence</a>')
    reqs = entry.get('requirements') or []
    named = ('Requirements ' + ', '.join(f'<strong>{html.escape(r)}</strong>' for r in reqs) + '. ') if reqs else ''
    out.append(f'<p>{named}See {" and ".join(links)}.</p>')
    return out


def build(root=ROOT):
    """Rewrite development-progress.html and release-report-<version>.html from current sources."""
    v = version(root)
    markdown = handoff_markdown(root)
    errors = handoff_errors(markdown, v)
    if errors:
        raise SystemExit('HANDOFF.md is not ready for the report: ' + '; '.join(errors))
    page = (root / 'development-progress.html').read_text()
    head, rest = page.split('\n', 1)
    head = re.sub(r'Luisa v\d+\.\d+ (release report|development progress)', lambda m: f'Luisa v{v} {m[1]}', head)
    start = rest.index('<h2>')
    tables = rest[start:]
    tables = SECTION.sub('', tables)
    tables = LEGACY_SECTION.sub('', tables)
    tables = re.sub(r'<!-- LUISA-FULL-HANDOFF[^>]*-->', '', tables).rstrip('\n')
    if 'release-handoff' in tables or re.search(r'<h[1-6][^>]*>[^<]*handoff', tables, re.I):
        raise SystemExit('development-progress.html has an unexpected handoff fragment; fix the page source')
    text = '\n'.join([head] + intro(root, v) + [tables + handoff_section(v, markdown)]) + '\n'
    errs = page_errors(text, v, markdown)
    if errs:
        raise SystemExit('Built report failed its own check: ' + '; '.join(errs))
    (root / 'development-progress.html').write_text(text)
    (root / f'release-report-{v}.html').write_text(text)
    return text


def handoff_errors(markdown, v):
    errors = []
    markers = MARKER.findall(markdown)
    if markers != [v]:
        errors.append(f'HANDOFF.md must contain exactly one release marker for v{v} (found {markers or "none"})')
    if '[LUISA-HANDOFF' in markdown:
        errors.append('HANDOFF.md contains a separate [LUISA-HANDOFF ...] paragraph')
    if not markdown.startswith('# Current Luisa handoff'):
        errors.append('HANDOFF.md must start with "# Current Luisa handoff"')
    return errors


def page_errors(text, v, markdown):
    """Errors for one report page (website or email HTML). Empty list means exactly one correct handoff."""
    errors = []
    markers = re.findall(r'<!-- LUISA-FULL-HANDOFF v([^ ]+) -->', text)
    if markers != [v]:
        errors.append(f'expected one LUISA-FULL-HANDOFF marker for v{v}, found {markers}')
    if text.count('<section id="release-handoff">') != 1:
        errors.append('expected exactly one release-handoff section')
    heads = [re.sub(r'<[^>]+>', '', h).strip() for h in re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', text, re.S)]
    handoff_heads = [h for h in heads if 'handoff' in h.lower()]
    if handoff_heads != [heading(v)]:
        errors.append(f'expected the single heading "{heading(v)}", found {handoff_heads}')
    if '[LUISA-HANDOFF' in text:
        errors.append('report contains a separate [LUISA-HANDOFF ...] paragraph')
    body = html.escape(markdown.rstrip('\n'), quote=False)
    if text.count(body) != 1:
        errors.append('report must contain the whole of HANDOFF.md exactly once')
    inner = re.findall(r'&lt;!-- LUISA-REPORT-HANDOFF v([\d.]+) --&gt;', text)
    if inner != [v]:
        errors.append(f'handoff marker comment must show v{v}, found {inner}')
    if f'<title>Luisa v{v} release report</title>' not in text:
        errors.append(f'title must name v{v}')
    errors += [f'private-looking value in report: {kind}' for kind in private_patterns(text)]
    return errors


def text_errors(text, v, markdown):
    errors = []
    if text.count(heading(v)) != 1:
        errors.append(f'text report must contain the heading "{heading(v)}" exactly once')
    if text.count(markdown.rstrip('\n')) != 1:
        errors.append('text report must contain the whole of HANDOFF.md exactly once')
    if '[LUISA-HANDOFF' in text:
        errors.append('text report contains a separate [LUISA-HANDOFF ...] paragraph')
    if re.findall(r'<!-- LUISA-REPORT-HANDOFF v([\d.]+) -->', text) != [v]:
        errors.append(f'text report handoff marker must show v{v}')
    errors += [f'private-looking value in text report: {kind}' for kind in private_patterns(text)]
    return errors


def private_patterns(text):
    """Generic private-data patterns usable without the private config (CI-safe)."""
    found = []
    if re.search(r'(?:/Users|/home)/[A-Za-z0-9._-]+/', text):
        found.append('personal absolute path')
    if re.search(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b', re.sub(r'noreply@[\w.]+|[\w.+-]+@users\.noreply\.github\.com', '', text)):
        found.append('email address')
    if re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_\w{40,}', text):
        found.append('credential')
    return found


def check(root=ROOT):
    v = version(root)
    markdown = handoff_markdown(root)
    errors = handoff_errors(markdown, v)
    for name in ('development-progress.html', f'release-report-{v}.html'):
        path = root / name
        if not path.is_file():
            errors.append(f'{name} is missing')
            continue
        errors += [f'{name}: {e}' for e in page_errors(path.read_text(), v, markdown)]
    return errors


def email(root, revision, out_dir, owner_url, intro_text):
    """Write report.txt and report.html (absolute links, inline colours) for the SMTP adapter."""
    v = version(root)
    markdown = handoff_markdown(root)
    page = (root / f'release-report-{v}.html').read_text()
    body = re.sub(r'href="([^"]+)"', lambda m: 'href="' + html.escape(urljoin(owner_url, html.unescape(m[1])), quote=True) + '"', page)
    for cls, colour in STATUS_STYLE:
        body = body.replace(f'class="{cls}"', f'class="{cls}" style="background:{colour};padding:8px;border:1px solid #ccd5df"')
    links = [('Repository', f'{REPOSITORY}/tree/{revision}'), ('Handoff', f'{REPOSITORY}/blob/{revision}/HANDOFF.md'),
             ('Requirements', f'{REPOSITORY}/blob/{revision}/docs/requirements/register.json'),
             ('Release report', f'{owner_url}release-report-{v}.html')]
    facts = (f'<p>Production revision <code>{revision}</code>. '
             + ' · '.join(f'<a href="{u}">{n}</a>' for n, u in links) + '</p>')
    body = body.replace('<!-- LUISA-FULL-HANDOFF', facts + '<!-- LUISA-FULL-HANDOFF', 1)
    body = body.replace('<h1>', f'<p>{html.escape(intro_text, quote=False)}</p><h1>', 1)
    plain = '\n'.join([intro_text, '', f'Production revision {revision}.'] + [f'{n}: {u}' for n, u in links]
                      + ['', heading(v), '', markdown.rstrip('\n'), ''])
    errors = page_errors(body, v, markdown) + text_errors(plain, v, markdown)
    if errors:
        raise SystemExit('Email report failed the single-handoff check: ' + '; '.join(errors))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'report.html').write_text(body)
    (out / 'report.txt').write_text(plain)
    return out / 'report.txt', out / 'report.html'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['build', 'check', 'email'])
    parser.add_argument('--revision')
    parser.add_argument('--out')
    parser.add_argument('--intro', default='')
    args = parser.parse_args()
    if args.command == 'build':
        build()
        print(json.dumps({'event': 'report_built', 'version': version()}))
    elif args.command == 'check':
        errors = check()
        for e in errors:
            print(json.dumps({'event': 'report_failure', 'message': e}))
        if errors:
            raise SystemExit(1)
        print(json.dumps({'event': 'report_pass', 'version': version()}))
    else:
        owner = json.loads((ROOT / 'release.json').read_text())['publicBaseUrl'].rstrip('/') + '/'
        txt, page = email(ROOT, args.revision, args.out, owner, args.intro)
        print(json.dumps({'event': 'email_report_written', 'text': txt.name, 'html': page.name}))


if __name__ == '__main__':
    sys.exit(main())
