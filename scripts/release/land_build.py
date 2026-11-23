#!/usr/bin/env python3
"""Land one reviewed PR on green exact-head CI, then build and check all three editions from main.

Usage (from the PR's worktree, clean, at the reviewed head):
  python3 scripts/release/land_build.py --pr 131 --review-record <review.json>

Steps: the worktree HEAD, the PR head and the review record's head must all agree; wait for every PR
check at that head (`gh pr checks --watch`); land with scripts/land.py (squash, no force); fast-forward
the main checkout; prove the merge tree equals the reviewed tree; build owner, staff and student
editions and run check-artifact on each. The merged revision is written to the private release
work folder (releases/v<version>/merged-revision).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402

HERE = Path(__file__).resolve().parents[2]


def run(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, **kw)


def out(cmd, cwd):
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def main_checkout():
    """The worktree that has main checked out (the release builds from it)."""
    block = {}
    for line in out(['git', 'worktree', 'list', '--porcelain'], HERE).splitlines() + ['']:
        if not line:
            if block.get('branch') == 'refs/heads/main':
                return Path(block['worktree'])
            block = {}
            continue
        key, _, value = line.partition(' ')
        block[key] = value
    raise SystemExit('No worktree has main checked out; create one (git worktree add <dir> main).')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pr', required=True, type=int)
    parser.add_argument('--review-record', required=True, type=Path)
    parser.add_argument('--skip-land', action='store_true', help='PR already merged: only verify main and build')
    args = parser.parse_args()
    review = json.loads(args.review_record.read_text())
    head = review['head']
    pr = json.loads(out(['gh', 'pr', 'view', str(args.pr), '--json', 'headRefOid,baseRefOid,state,mergeCommit'], HERE))
    if not args.skip_land:
        if out(['git', 'rev-parse', 'HEAD'], HERE) != head or out(['git', 'status', '--porcelain'], HERE):
            raise SystemExit('Run from the clean PR worktree at the reviewed head.')
        if pr['headRefOid'] != head:
            raise SystemExit('The PR head is not the reviewed head; review the new head first.')
        run(['gh', 'pr', 'checks', str(args.pr), '--watch', '--interval', '12'], HERE)
        if out(['gh', 'pr', 'view', str(args.pr), '--json', 'headRefOid', '--jq', '.headRefOid'], HERE) != head:
            raise SystemExit('The PR head moved while checks ran.')
        run([sys.executable, 'scripts/land.py', str(args.pr), '--review-record', str(args.review_record.resolve())], HERE)
    main_dir = main_checkout()
    run(['git', 'fetch', 'origin', 'main'], main_dir)
    merge = out(['gh', 'pr', 'view', str(args.pr), '--json', 'state,mergeCommit', '--jq', 'select(.state == "MERGED") | .mergeCommit.oid'], HERE)
    if not merge or out(['git', 'rev-parse', 'origin/main'], main_dir) != merge:
        raise SystemExit('origin/main is not the PR merge commit; inspect before building.')
    if out(['git', 'rev-parse', merge + '^{tree}'], main_dir) != out(['git', 'rev-parse', head + '^{tree}'], main_dir):
        raise SystemExit('The merged tree differs from the reviewed tree.')
    if out(['git', 'branch', '--show-current'], main_dir) != 'main' or out(['git', 'status', '--porcelain'], main_dir):
        raise SystemExit('The main checkout must be clean and on main.')
    run(['git', 'merge', '--ff-only', 'origin/main'], main_dir)
    version = json.loads((main_dir / 'release.json').read_text())['version']
    record = private.work_dir(version) / 'merged-revision'
    if record.exists() and record.read_text().strip() != merge:
        # A later landing for an already-released version (a docs-only follow-up): keep the release revision.
        (private.work_dir(version) / 'followup-revision').write_text(merge + '\n')
        print('Release revision kept; follow-up merge recorded separately.', flush=True)
    else:
        record.write_text(merge + '\n')
    for profile in ('owner', 'staff', 'student'):
        run([sys.executable, 'scripts/luisa.py', 'build', '--profile', profile], main_dir)
        directory = 'dist' if profile == 'owner' else 'dist-' + profile
        run([sys.executable, 'scripts/luisa.py', 'check-artifact', '--directory', directory, '--host-profile', profile], main_dir)
    print(json.dumps({'event': 'landed_and_built', 'version': version, 'revision': merge, 'mainCheckout': main_dir.name}))


if __name__ == '__main__':
    main()
