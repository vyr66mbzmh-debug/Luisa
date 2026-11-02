#!/usr/bin/env python3
"""Gate one reviewed PR; never force-push or bypass missing checks."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pr', type=int)
    parser.add_argument('--review-record', required=True, type=Path)
    args = parser.parse_args()
    review = json.loads(args.review_record.read_text())
    head = run('git', 'rev-parse', 'HEAD')
    if review.get('head') != head or review.get('verdict') != 'ship':
        raise SystemExit('A ship verdict for the current HEAD is required')
    if run('git', 'status', '--porcelain'):
        raise SystemExit('Commit/preserve the working tree before landing')
    if run('git', 'branch', '--show-current') == 'main':
        raise SystemExit('Land from the reviewed task branch, not main')
    subprocess.run([sys.executable, 'scripts/luisa.py', 'gate'], cwd=ROOT, check=True)
    pr = json.loads(run('gh', 'pr', 'view', str(args.pr), '--json', 'headRefOid,baseRefName,isDraft'))
    if pr['headRefOid'] != head or pr['baseRefName'] != 'main' or pr['isDraft']:
        raise SystemExit('PR head/base/draft differs from reviewed task')
    checks = json.loads(run('gh', 'pr', 'checks', str(args.pr), '--json', 'name,bucket'))
    byname = {x['name']: x['bucket'] for x in checks}
    if any(byname.get(name) != 'pass' for name in ('build', 'test', 'scan')) or any(x['bucket'] != 'pass' for x in checks):
        raise SystemExit('All checks, including build/test/scan, must exist and pass')
    subprocess.run(['gh', 'pr', 'merge', str(args.pr), '--squash', '--match-head-commit', head], cwd=ROOT, check=True)
    print('Merged reviewed head; verify deployment and update HANDOFF before claiming publication.')

if __name__ == '__main__':
    main()
