"""Cold-start check (OPS-068): is everything a fresh agent needs present? Read-only; never prints private values.

Run as `python3 scripts/luisa.py doctor` with the bootstrapped interpreter (<state>/env/bin/python).
Each item prints PASS, MISSING (with the exact human action) or OPTIONAL (useful, not required).
Exit status 1 when anything is MISSING.
"""
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPO = 'vyr66mbzmh-debug/Luisa'
RESULTS = []


def item(name, ok, detail='', action='', optional=False):
    status = 'PASS' if ok else ('OPTIONAL' if optional else 'MISSING')
    RESULTS.append(status)
    line = f'{status:8} {name}'
    if detail:
        line += f' — {detail}'
    if not ok and action:
        line += f'\n         action: {action}'
    print(line, flush=True)


def quiet(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 127, ''


def pins():
    out = {}
    for line in (ROOT / 'requirements-tools.txt').read_text().splitlines():
        if '==' in line and not line.startswith('#'):
            name, version = line.split('==')
            out[name.strip()] = version.strip()
    return out


def run():
    bootstrap = 'run: python3 scripts/bootstrap.py, then use <state>/env/bin/python'
    v = sys.version_info
    item('Python 3.12+', v >= (3, 12), f'{v.major}.{v.minor}.{v.micro}', bootstrap)
    wrong = []
    for name, want in pins().items():
        try:
            have = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            have = None
        if have != want:
            wrong.append(f'{name} {have or "absent"} (pinned {want})')
    item('Pinned Python packages (requirements-tools.txt)', not wrong, f'{len(pins())} pinned' if not wrong else '; '.join(wrong[:4]), bootstrap)
    node = shutil.which('node')  # presence check only; tooling never depends on Node
    code, out = quiet([node, '--version']) if node else (127, '')
    item('Node.js for the lesson renderer test', code == 0, out, bootstrap + ' (it provides node in env/bin); put env/bin first on PATH')
    env_record = private.state_dir() / 'env' / 'luisa-env.json'
    channel = os.environ.get('LUISA_BROWSER_CHANNEL') or (json.loads(env_record.read_text())['browserChannel'] if env_record.exists() else 'chromium')
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch(channel=None if channel == 'chromium' else channel).close()
        item('Browser for Playwright', True, f'channel {channel}')
    except Exception:
        item('Browser for Playwright', False, f'channel {channel}', 'install Google Chrome, or run: python3 scripts/bootstrap.py --browser chromium')
    code, out = quiet(['git', '-C', str(ROOT), 'remote', 'get-url', 'origin'])
    item('Git checkout of the Luisa repository', code == 0 and REPO in out, '', 'clone https://github.com/' + REPO)
    code, _ = quiet(['gh', 'auth', 'status'])
    item('GitHub CLI login', code == 0, '', 'install GitHub CLI and run: gh auth login (owner or an account with write access)')
    code, _ = quiet(['gh', 'repo', 'view', REPO, '--json', 'viewerPermission', '--jq', '.viewerPermission'])
    item('GitHub repository access', code == 0, '', 'ask the owner for write access to ' + REPO)
    code, out = quiet(['gh', 'api', f'repos/{REPO}/commits/main/check-runs', '--jq', '[.check_runs[].name]'])
    names = json.loads(out) if code == 0 and out.startswith('[') else []
    code_s, statuses = quiet(['gh', 'api', f'repos/{REPO}/commits/main/status', '--jq', '[.statuses[].context]'])
    names += json.loads(statuses) if code_s == 0 and statuses.startswith('[') else []
    item('Cloudflare Pages integration on main', any('Cloudflare Pages' in n for n in names), '',
         'the owner must reconnect the Cloudflare Pages project to the GitHub repository (Cloudflare dashboard)')
    release = json.loads((ROOT / 'release.json').read_text())
    try:
        m = json.loads(urllib.request.urlopen(urllib.request.Request(release['publicBaseUrl'].rstrip('/') + '/build-manifest.json',
                                                                     headers={'User-Agent': 'luisa-doctor'}), timeout=15).read())
        item('Live owner site', True, f"serving v{m['version']} ({m['revision'][:7]})")
    except Exception:
        item('Live owner site', False, '', 'check the Cloudflare Pages project and the network')
    state = private.state_dir()
    item('Private state folder', (state / 'WORKSPACE.json').is_file(), '(location not shown)',
         'ask the owner for the private state folder with WORKSPACE.json; set LUISA_STATE_DIR if it is not in the default place')
    missing = private.missing_keys()
    item('Private configuration keys', not missing, f'{len(private.REQUIRED_KEYS)} keys present' if not missing else 'missing: ' + ', '.join(missing),
         'ask the owner to add the missing keys to WORKSPACE.json (names in scripts/release/private.py)')
    if missing:
        return
    code = subprocess.run(private.ssh_command() + ['test -f ' + private.layout('startScript')], capture_output=True, timeout=40).returncode
    item('ADA SSH access', code == 0, '', 'ask the owner to authorise this machine\'s SSH key for the ADA host (and accept its host key)')
    try:  # Playwright's HTTP stack, as used by the live QA (some Python OpenSSL builds cannot negotiate with this host)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            request = p.request.new_context()
            status = request.get(private.get('ada.url').rstrip('/') + '/login', timeout=20000, max_redirects=0).status
            request.dispose()
        item('ADA website', status == 200, '')
    except Exception:
        item('ADA website', False, '', 'check the ADA host is up (owner)')
    backups = Path(private.get('master')) / 'backups'
    item('Recovery storage', backups.is_dir() and os.access(backups, os.W_OK), '', 'ask the owner to make the master folder (key "master") with backups/ available and writable')
    sender = Path(private.get('mailSender'))
    readable = sender.is_file() and os.access(sender, os.R_OK)
    if readable:
        try:
            compile(sender.read_text(), 'mail adapter', 'exec')
        except SyntaxError:
            readable = False
    item('Mail adapter (owner report)', readable, '', 'ask the owner to provision the SMTP adapter (key "mailSender"); never recreate credentials yourself')
    source = Path(private.get('pastPaperSource')).expanduser()
    if source.is_dir() and os.access(source, os.R_OK):
        pdfs = sum(1 for _ in source.rglob('*.pdf'))
        item('Past-paper source folder', True, f'readable; {pdfs} PDFs present' + ('' if pdfs else ' (the owner supplies papers before an import)'))
    else:
        item('Past-paper source folder', False, '', 'create the folder named by "pastPaperSource" (default <state>/past-paper-source) or point the key at the folder of new papers; macOS may need Files and Folders permission for the terminal')
    item('Tesseract OCR (import aid only)', bool(shutil.which('tesseract')), '', 'optional: brew install tesseract', optional=True)


def main():
    print('Luisa doctor (read-only; private values are never printed)', flush=True)
    run()
    missing = RESULTS.count('MISSING')
    print(json.dumps({'event': 'doctor', 'pass': RESULTS.count('PASS'), 'missing': missing, 'optional': RESULTS.count('OPTIONAL')}))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
