#!/usr/bin/env python3
"""Wait until Cloudflare serves the merged revision, then verify the owner edition live and offline.

Usage (from the main checkout at the merged revision):
  python3 scripts/release/verify_owner.py [--timeout-minutes 12]

Cloudflare Pages deploys main automatically. This polls <publicBaseUrl>/build-manifest.json until its
revision, version and edition match, saves the manifest to the private release work folder, then runs
qa_live.py owner and qa_offline.py against the live site.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--timeout-minutes', type=float, default=12)
    parser.add_argument('--channel', default=os.environ.get('LUISA_BROWSER_CHANNEL') or 'chromium')
    args = parser.parse_args()
    release = json.loads((ROOT / 'release.json').read_text())
    version, base = release['version'], release['publicBaseUrl'].rstrip('/') + '/'
    rev = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out = private.work_dir(version)
    deadline = time.time() + args.timeout_minutes * 60
    while True:
        try:
            req = urllib.request.Request(f'{base}build-manifest.json?revision={rev}', headers={'Cache-Control': 'no-cache', 'User-Agent': 'luisa-release'})
            data = urllib.request.urlopen(req, timeout=10).read()
            m = json.loads(data)
            if (m['revision'], m['version'], m['edition']) == (rev, version, 'owner'):
                (out / 'live-owner-manifest.json').write_bytes(data)
                print(f'Cloudflare production manifest matches {rev}', flush=True)
                break
        except Exception:
            pass
        if time.time() > deadline:
            raise SystemExit('Cloudflare did not publish the expected revision in time; check the Cloudflare Pages build for this commit.')
        time.sleep(12)
    subprocess.run([sys.executable, str(ROOT / 'scripts/release/qa_live.py'), 'owner', '--channel', args.channel], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/release/qa_offline.py'), '--url', base, '--channel', args.channel], cwd=ROOT, check=True)
    print(json.dumps({'event': 'owner_verified', 'version': version, 'revision': rev}))


if __name__ == '__main__':
    main()
