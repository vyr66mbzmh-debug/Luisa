"""Read Luisa's private configuration at run time. Never print values from it.

The private state folder defaults to ~/.local/share/luisa-agent-state and can be moved with
LUISA_STATE_DIR. It holds WORKSPACE.json (keys below), the bootstrapped environment (env/),
release work folders (releases/<version>/) and private evidence (reports/). None of it is in Git.

WORKSPACE.json keys used by the tooling (names only; values stay private):
  master                      folder holding backups/ (recovery ZIPs, latest five kept)
  mailSender                  path of the private SMTP adapter script (owner report)
  pastPaperSource             folder holding owner-supplied past-paper PDFs (read-only)
  ada.sshHost, ada.sshPort    SSH target for the ADA host
  ada.url                     ADA website prefix used for live verification
  ada.pupilEmailDomain        domain of pupil sign-in identities (QA fixture accounts)
  ada.layout.releaseRoot, .releasePrefix, .startScript, .dataDir, .runtimePython,
  ada.layout.supervisorCommand, .serviceName, .nginx   server-internal paths and commands
"""
import json
import re
import os
import subprocess
from pathlib import Path

REQUIRED_KEYS = ['master', 'mailSender', 'pastPaperSource', 'ada.sshHost', 'ada.sshPort', 'ada.url',
                 'ada.pupilEmailDomain', 'ada.layout.releaseRoot', 'ada.layout.releasePrefix',
                 'ada.layout.startScript', 'ada.layout.dataDir', 'ada.layout.runtimePython',
                 'ada.layout.supervisorCommand', 'ada.layout.serviceName', 'ada.layout.nginx']


class MissingPrivateConfig(RuntimeError):
    """Raised with a human action; the message never contains a private value."""


def state_dir():
    return Path(os.environ.get('LUISA_STATE_DIR') or Path.home() / '.local/share/luisa-agent-state')


def workspace():
    path = state_dir() / 'WORKSPACE.json'
    if not path.is_file():
        raise MissingPrivateConfig(f'Private configuration missing: create WORKSPACE.json in the private state folder '
                                   f'(LUISA_STATE_DIR) with the keys listed in scripts/release/private.py.')
    return json.loads(path.read_text())


def get(key, data=None):
    """Return the value at a dotted key such as 'ada.layout.dataDir'."""
    value = workspace() if data is None else data
    for part in key.split('.'):
        if not isinstance(value, dict) or part not in value:
            raise MissingPrivateConfig(f'Private configuration key "{key}" is missing from WORKSPACE.json; '
                                       'ask the owner to provide it (see scripts/release/private.py).')
        value = value[part]
    return value


def missing_keys():
    try:
        data = workspace()
    except MissingPrivateConfig:
        return list(REQUIRED_KEYS)
    out = []
    for key in REQUIRED_KEYS:
        try:
            get(key, data)
        except MissingPrivateConfig:
            out.append(key)
    return out


PUBLIC_KEYS = {'ada.url', 'ada.pupilEmailDomain'}  # already published by the site and the auth app


def private_values(data=None):
    """Identifying WORKSPACE.json values for leak checks: addresses, host names and absolute paths, plus the
    home path. Public keys (PUBLIC_KEYS), plain words and bare file names are not identifying and are skipped."""
    found = set()
    def walk(v, key=''):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f'{key}.{k}' if key else k)
        elif isinstance(v, list):
            for x in v:
                walk(x, key)
        elif isinstance(v, str) and key not in PUBLIC_KEYS:
            path = v.startswith(('/', '~')) and len(v) >= 12 and not v.startswith(('/workspace', '/usr/', '/etc/', '/tmp/'))
            host = re.fullmatch(r'(?:[\w.+-]+@)?(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}', v) and not re.search(r'\.(?:py|json|md|txt|sh|sqlite|conf|tex|pdf)$', v)
            if path or host or '@' in v:
                found.add(v)
    walk(workspace() if data is None else data)
    home = str(Path.home())
    if len(home) > 6:
        found.add(home)
    return found


def assert_no_private_values(text, label):
    """Raise (without echoing the value) if any private value appears in text."""
    try:
        values = private_values()
    except MissingPrivateConfig:
        values = {str(Path.home())}
    for value in values:
        if value in text:
            raise RuntimeError(f'{label} contains a private value; it was not written or sent.')


def work_dir(version):
    """Private per-release work folder, replacing ad hoc /tmp folders."""
    path = state_dir() / 'releases' / f'v{version}'
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path


def ssh_command():
    ada = get('ada')
    return ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12',
            '-p', str(ada['sshPort']), ada['sshHost']]


def remote(command, data=None, check=True):
    """Run a shell command on the ADA host and return stdout bytes."""
    result = subprocess.run(ssh_command() + [command], input=data, stdout=subprocess.PIPE, check=check)
    return result.stdout


def remote_python(script):
    return remote('python3 -', script.encode())


def layout(name):
    return get('ada.layout.' + name)
