#!/usr/bin/env python3
"""Create Luisa's pinned working environment in the private state folder (OPS-067).

Usage:
  python3 scripts/bootstrap.py [--python /path/to/python3.12+] [--browser auto|chrome|chromium] [--recreate]

Creates <state>/env (state = $LUISA_STATE_DIR or ~/.local/share/luisa-agent-state), a Python virtual
environment with requirements-dev.txt (Flask, argon2, PyOTP, gunicorn for the auth tests) and the exact
pins in requirements-tools.txt (Playwright, PyMuPDF, SymPy, Pillow, and Node.js via nodejs-wheel, which
puts a `node` command in env/bin for the lesson renderer test). Browser: the installed Google Chrome is
used when present (channel "chrome"); otherwise Playwright's pinned Chromium is installed ("chromium").
The choice is written to <state>/env/luisa-env.json and printed as the two environment lines to use:
  export PATH="<state>/env/bin:$PATH"
  export LUISA_BROWSER_CHANNEL=<chrome|chromium>
Nothing is written to /tmp or to the repository. Re-running is safe; --recreate rebuilds from scratch.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def state_dir():
    return Path(os.environ.get('LUISA_STATE_DIR') or Path.home() / '.local/share/luisa-agent-state')


def chrome_works(python):
    probe = ('from playwright.sync_api import sync_playwright\n'
             'with sync_playwright() as p:\n b=p.chromium.launch(channel="chrome"); b.close()\n')
    return subprocess.run([python, '-c', probe], capture_output=True).returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--browser', choices=['auto', 'chrome', 'chromium'], default='auto')
    parser.add_argument('--recreate', action='store_true')
    args = parser.parse_args()
    version = subprocess.check_output([args.python, '-c', 'import sys;print("%d.%d"%sys.version_info[:2])'], text=True).strip()
    if tuple(map(int, version.split('.'))) < (3, 12):
        raise SystemExit(f'Python 3.12 or newer is required (found {version}); pass --python.')
    env = state_dir() / 'env'
    if args.recreate and env.exists():
        shutil.rmtree(env)
    state_dir().mkdir(parents=True, exist_ok=True)
    os.chmod(state_dir(), 0o700)
    if not (env / 'bin' / 'python').exists():
        subprocess.run([args.python, '-m', 'venv', str(env)], check=True)
    python = str(env / 'bin' / 'python')
    pip = [python, '-m', 'pip', 'install', '--disable-pip-version-check', '--quiet']
    subprocess.run(pip + ['-r', str(ROOT / 'requirements-dev.txt'), '-r', str(ROOT / 'requirements-tools.txt')], check=True)
    subprocess.run([python, '-m', 'pip', 'check'], check=True)
    browser = args.browser
    if browser == 'auto':
        browser = 'chrome' if chrome_works(python) else 'chromium'
    if browser == 'chromium':
        subprocess.run([python, '-m', 'playwright', 'install', 'chromium'], check=True)
    elif not chrome_works(python):
        raise SystemExit('Google Chrome is not usable by Playwright; install Chrome or rerun with --browser chromium.')
    node = subprocess.check_output([str(env / 'bin' / 'node'), '--version'], text=True).strip()
    record = {'python': version, 'browserChannel': browser, 'node': node,
              'requirements': ['requirements-dev.txt', 'requirements-tools.txt']}
    (env / 'luisa-env.json').write_text(json.dumps(record, indent=1) + '\n')
    print(json.dumps({'event': 'environment_ready', **record}))
    shown = str(env).replace(str(Path.home()), '$HOME', 1)  # never print a personal absolute path
    print(f'export PATH="{shown}/bin:$PATH"')
    print(f'export LUISA_BROWSER_CHANNEL={browser}')


if __name__ == '__main__':
    main()
