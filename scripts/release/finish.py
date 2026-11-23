#!/usr/bin/env python3
"""Finish a verified release: recovery archive, ADA cleanup, published-report check, owner report, completion.

Usage (from the main checkout at the merged revision, after verify_owner.py, ada.py and qa_live.py ada):
  python3 scripts/release/finish.py archive            # recovery ZIP in <master>/backups, newest five kept
  python3 scripts/release/finish.py cleanup            # ADA keeps only the verified release folder
  python3 scripts/release/finish.py check-published    # live release report = manifest, exactly one handoff
  python3 scripts/release/finish.py report --intro "<one paragraph for the owner>"   # SMTP owner report
  python3 scripts/release/finish.py complete           # OPS-070: refuse unless every closing record exists

`report` refuses to send unless every QA results file names the merged revision, the published report
passes the single-handoff check, and HANDOFF.md and the register are current. The prepared report is
checked for private values and kept privately (reports/v<version>/). A second send is refused.
`complete` checks HANDOFF.md, the register, the issue's evidence and token-log comments, and the SMTP
record; it is the last command of a release.
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402
import report as report_tool  # noqa: E402
import ada as ada_tool  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = re.compile(r'(?:Luisa-|luisa-)?v\d+\.\d+-[0-9a-f]{7,40}-website\.zip')


DOCS_ONLY = re.compile(r'(?:HANDOFF\.md|CHANGELOG\.md|docs/.*|development-progress\.html|release-report-[\d.]+\.html)')


def context(allow_docs_followup=False):
    """Release facts. Normally HEAD must be the merged release revision recorded by land_build.py. With
    allow_docs_followup (finish.py complete), HEAD may also be a later main commit that changes only documentation."""
    release = json.loads((ROOT / 'release.json').read_text())
    version = release['version']
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    work = private.work_dir(version)
    merged = (work / 'merged-revision').read_text().strip() if (work / 'merged-revision').exists() else None
    rev = merged
    if merged != head:
        ok = allow_docs_followup and merged and subprocess.run(['git', 'merge-base', '--is-ancestor', merged, head], cwd=ROOT).returncode == 0
        changed = subprocess.check_output(['git', 'diff', '--name-only', merged, head], cwd=ROOT, text=True).split() if ok else []
        if not ok or not all(DOCS_ONLY.fullmatch(f) for f in changed):
            raise SystemExit('Run from the main checkout at the merged revision recorded by land_build.py'
                             + (' (or a later main commit that changes documentation only).' if allow_docs_followup else '.'))
    history = json.loads((ROOT / 'version-history.json').read_text())
    entry = next(r for r in history['releases'] if r['version'] == version)
    return release, version, rev, work, entry


def archive():
    release, version, rev, work, _ = context()
    backups = Path(private.get('master')) / 'backups'
    subprocess.run([sys.executable, 'scripts/archive_release.py', str(backups)], cwd=ROOT, check=True)
    path = backups / f'v{version}-{rev[:12]}-website.zip'
    assert path.is_file() and path.with_suffix('.zip.sha256').is_file()
    kept = [p for p in backups.iterdir() if p.is_file() and ARCHIVE.fullmatch(p.name)]
    if len(kept) > 5:
        raise SystemExit('Recovery retention failed: more than five archives remain.')
    print(f'Recovery ZIP {path.name} written and verified; {len(kept)} archives retained (latest five).')


def check_published(quiet=False):
    release, version, rev, work, _ = context(allow_docs_followup=True)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    base = release['publicBaseUrl'].rstrip('/') + '/'
    fetch = lambda path: urllib.request.urlopen(urllib.request.Request(base + path, headers={'Cache-Control': 'no-cache', 'User-Agent': 'luisa-release'}), timeout=15).read()
    manifest = json.loads(fetch(f'build-manifest.json?revision={head}'))
    data = fetch(f'release-report-{version}.html?revision={head}')
    if manifest['revision'] != head:
        raise SystemExit('Cloudflare is not serving this checkout\'s revision yet; wait for its deployment and retry.')
    if hashlib.sha256(data).hexdigest() != manifest['files'][f'release-report-{version}.html']['sha256']:
        raise SystemExit('The published release report does not match the live owner manifest.')
    errors = report_tool.page_errors(data.decode(), version, (ROOT / 'HANDOFF.md').read_text())
    if errors:
        raise SystemExit('Published report fails the single-handoff check: ' + '; '.join(errors))
    if not quiet:
        print(f'Published release report matches the owner manifest and has exactly one "{report_tool.heading(version)}".')


def closing_errors(version, entry):
    """Errors that block completion (OPS-070)."""
    errors = report_tool.handoff_errors((ROOT / 'HANDOFF.md').read_text(), version)
    errors += report_tool.check(ROOT)
    issue = entry.get('issue')
    if not issue:
        errors.append('version-history.json has no issue number for this release')
    register = json.loads((ROOT / 'docs/requirements/register.json').read_text())['requirements']
    named = [r['id'] for r in register if f'#{issue}' in r.get('origin', '') or f'GitHub issue #{issue}' in r.get('evidence', [])]
    if not named or not set(entry.get('requirements', [])) <= {r['id'] for r in register}:
        errors.append(f'the register has no requirement entries for issue #{issue} matching version-history')
    return errors


def report(intro):
    release, version, rev, work, entry = context()
    for name in ('qa-owner.json', 'qa-offline.json', 'qa-ada.json'):
        path = work / name
        if not path.exists() or json.loads(path.read_text())['revision'] != rev:
            raise SystemExit(f'{name} is missing or not for this revision; run the live verification first.')
    check_published(quiet=True)
    errors = closing_errors(version, entry)
    if errors:
        raise SystemExit('Not ready to report: ' + '; '.join(errors))
    if not intro or len(intro) < 80:
        raise SystemExit('Give a one-paragraph --intro for the owner (what is live, what changed, decisions applied).')
    folder = private.state_dir() / 'reports' / f'v{version}'
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / 'smtp-accepted.json').exists():
        raise SystemExit('Report already submitted for this version; duplicate suppressed.')
    owner = release['publicBaseUrl'].rstrip('/') + '/'
    text_path, html_path = report_tool.email(ROOT, rev, folder, owner, intro)
    for path in (text_path, html_path):
        private.assert_no_private_values(path.read_text(), path.name)
    result = subprocess.run([sys.executable, private.get('mailSender'), '--subject', f'Luisa v{version} report',
                             '--body-file', str(text_path), '--html-file', str(html_path)], capture_output=True)
    if result.returncode:
        (folder / 'smtp-failed.json').write_text(json.dumps({'version': version, 'returncode': result.returncode,
                                                             'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}))
        raise SystemExit('Owner email adapter failed; the prepared report is kept privately. Record "notification pending".')
    (folder / 'smtp-accepted.json').write_text(json.dumps({'version': version, 'revision': rev, 'accepted': True, 'returncode': 0,
                                                           'recipient': 'configured owner only',
                                                           'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}))
    print('Owner report accepted by the configured SMTP server (exactly one handoff; no private values).', flush=True)


def complete():
    release, version, rev, work, entry = context(allow_docs_followup=True)
    errors = closing_errors(version, entry)
    if not (private.state_dir() / 'reports' / f'v{version}' / 'smtp-accepted.json').exists():
        errors.append('no SMTP acceptance record for this version (finish.py report)')
    issue = entry.get('issue')
    if issue:
        comments = json.loads(subprocess.check_output(['gh', 'issue', 'view', str(issue), '--json', 'comments'], cwd=ROOT, text=True))['comments']
        bodies = [c['body'] for c in comments]
        if not any(rev in b for b in bodies):
            errors.append(f'issue #{issue} has no evidence comment naming the merged revision')
        if not any(re.search(r'\btokens?\b', b, re.I) and re.search(r'\bsource\b', b, re.I) for b in bodies):
            errors.append(f'issue #{issue} has no token-log comment stating its source')
    if errors:
        raise SystemExit('Release not complete: ' + '; '.join(errors))
    print(f'Release v{version} complete: HANDOFF.md, register, issue #{issue} evidence and token log, report and SMTP record all present.')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['archive', 'cleanup', 'check-published', 'report', 'complete'])
    parser.add_argument('--intro', default='')
    args = parser.parse_args()
    if args.command == 'archive':
        archive()
    elif args.command == 'cleanup':
        context()
        ada_tool.cleanup()
    elif args.command == 'check-published':
        check_published()
    elif args.command == 'report':
        report(args.intro)
    else:
        complete()


if __name__ == '__main__':
    main()
