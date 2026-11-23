#!/usr/bin/env python3
"""Apply a release's documentation from its committed spec, then rebuild the release report.

Usage (in the release branch):
  python3 scripts/release/docs.py apply docs/releases/v0.73.json --tokens "<token sentence>"

The spec (JSON) has: version, previous, date, issue, note (release.json), changes and requirements
(version-history.json), reportIntro (report paragraphs), changelog (bullets), roadmapHeading and
roadmap (one paragraph), and handoff (path of the release block in Markdown; "{TOKENS}" is replaced by
--tokens). Applying is idempotent: re-running replaces this version's entries. When HANDOFF.md still
carries the previous version's release block, that block is moved verbatim to the top of
docs/handoff/HISTORY.md, so HANDOFF.md always holds exactly one current release block.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
START = re.compile(r'<!-- LUISA-REPORT-HANDOFF v(\d+\.\d+) -->\n')
END = '<!-- END LUISA-RELEASE-BLOCK -->'
HISTORY_HEAD = '# Earlier Luisa handoffs\n'


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def section(text, heading, body, before):
    """Insert or replace a Markdown section '## heading' placed before the first line matching `before`."""
    block = f'## {heading}\n\n{body.rstrip()}\n\n'
    pattern = re.compile(rf'^## {re.escape(heading)}\n.*?(?=^## |\Z)', re.S | re.M)
    if pattern.search(text):
        return pattern.sub(lambda m: block, text, count=1)
    at = re.search(before, text, re.M)
    if not at:
        raise SystemExit(f'Cannot place section "{heading}"')
    return text[:at.start()] + block + text[at.start():]


def apply(spec_path, tokens):
    spec = json.loads(Path(spec_path).read_text())
    v, prev = spec['version'], spec['previous']
    release = json.loads((ROOT / 'release.json').read_text())
    if release['version'] not in (v, prev):
        raise SystemExit(f'release.json is {release["version"]}; expected {prev} or {v}')
    release.update(version=v, note=spec['note'])
    write_json(ROOT / 'release.json', release)
    history = json.loads((ROOT / 'version-history.json').read_text())
    history['current'] = v
    history['releases'] = [r for r in history['releases'] if r['version'] != v]
    if history['releases'][0]['version'] != prev:
        raise SystemExit('version-history.json does not start with the previous release')
    history['releases'].insert(0, {'version': v, 'previous': prev, 'date': spec['date'], 'issue': spec['issue'],
                                   'changes': spec['changes'], 'reportIntro': spec['reportIntro'],
                                   'requirements': spec['requirements']})
    write_json(ROOT / 'version-history.json', history)
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    changelog = section(changelog, f'Luisa v{v}', '\n'.join('- ' + b for b in spec['changelog']), rf'^## Luisa v{re.escape(prev)}$')
    (ROOT / 'CHANGELOG.md').write_text(changelog)
    roadmap = (ROOT / 'docs/ROADMAP.md').read_text()
    roadmap = section(roadmap, spec['roadmapHeading'], spec['roadmap'], r'^## ')
    (ROOT / 'docs/ROADMAP.md').write_text(roadmap)
    block = (ROOT / spec['handoff']).read_text().replace('{TOKENS}', tokens).rstrip('\n')
    handoff = (ROOT / 'HANDOFF.md').read_text()
    m = START.search(handoff)
    end = handoff.index(END)
    if not m or m.start() > end:
        raise SystemExit('HANDOFF.md has no current release block')
    if m.group(1) == prev:
        history_path = ROOT / 'docs/handoff/HISTORY.md'
        old = handoff[m.start():end].rstrip('\n') + '\n\n'
        text = history_path.read_text()
        if not text.startswith(HISTORY_HEAD):
            raise SystemExit('docs/handoff/HISTORY.md must start with "' + HISTORY_HEAD.strip() + '"')
        head_end = text.index('\n\n', len(HISTORY_HEAD)) + 2
        history_path.write_text(text[:head_end] + old + text[head_end:])
    elif m.group(1) != v:
        raise SystemExit(f'HANDOFF.md release block is v{m.group(1)}; expected v{prev} or v{v}')
    handoff = handoff[:m.start()] + f'<!-- LUISA-REPORT-HANDOFF v{v} -->\n' + block + '\n' + handoff[end:]
    (ROOT / 'HANDOFF.md').write_text(handoff)
    report.build(ROOT)
    print(json.dumps({'event': 'release_docs_applied', 'version': v}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['apply'])
    parser.add_argument('spec')
    parser.add_argument('--tokens', required=True, help='token sentence for the handoff Usage line (say "unavailable" if so)')
    args = parser.parse_args()
    apply(args.spec, args.tokens)


if __name__ == '__main__':
    main()
