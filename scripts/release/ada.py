#!/usr/bin/env python3
"""Deploy the checked staff and pupil artifacts to ADA, and verify or roll back.

All host details and server paths come from WORKSPACE.json (see private.py); nothing private is
printed. The live release folder is detected on the server (the one whose `start` file equals the
active start script), so no previous revision is hard-coded.

Usage (run from the main checkout at the merged revision, after land_build.py):
  python3 scripts/release/ada.py status                  # live release folder name and service state
  python3 scripts/release/ada.py stage                   # upload dist-staff and dist-student into a new release folder
  python3 scripts/release/ada.py activate                # snapshot accounts privately, switch start script, restart
  python3 scripts/release/ada.py accounts-check [--allow-completed-first-signin]
  python3 scripts/release/ada.py rollback                # switch back to the previous release folder
  python3 scripts/release/ada.py cleanup                 # after verification: keep only the active release folder
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tarfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import private  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ACCOUNT_QUERIES = [
    'select school_number,password_hash,temporary_hash,active,force_change from accounts order by school_number',
    'select username,password_hash,temporary_hash,active,force_change from staff_accounts order by username',
    'select * from teacher_credential order by singleton',
    'select * from student_directory order by school_number',
    'select * from teacher_directory order by username',
]



def label(folder):
    """Printable name of a release folder: its revision part only (the folder prefix is private server layout)."""
    name, prefix = Path(folder).name, private.layout('releasePrefix')
    return 'release ' + name[len(prefix):] if name.startswith(prefix) else 'release (name withheld)'

def revision():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def version():
    return json.loads((ROOT / 'release.json').read_text())['version']


def folder(rev):
    return private.layout('releaseRoot') + '/' + private.layout('releasePrefix') + rev[:10]


def live_folder():
    """Return the release folder whose start file is byte-identical to the active start script."""
    script = f"""from pathlib import Path
root=Path({private.layout('releaseRoot')!r});start=Path({private.layout('startScript')!r}).read_bytes()
hits=[str(p) for p in sorted(root.glob({private.layout('releasePrefix')!r}+'*')) if (p/'start').is_file() and (p/'start').read_bytes()==start]
print('\\n'.join(hits))"""
    hits = private.remote_python(script).decode().split()
    if len(hits) != 1:
        raise SystemExit(f'Expected exactly one live ADA release folder, found {len(hits)}; inspect the host before deploying.')
    return hits[0]


def upload(dest, files):
    p = subprocess.Popen(private.ssh_command() + ['umask 077; tar xzf - -C ' + dest], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    errors = []
    reader = threading.Thread(target=lambda: errors.append(p.stderr.read()), daemon=True)  # drain stderr while streaming
    reader.start()
    try:
        with tarfile.open(fileobj=p.stdin, mode='w|gz', compresslevel=1) as archive:
            for name, path in files:
                archive.add(path, arcname=name, recursive=False)
    finally:
        p.stdin.close()
    code = p.wait()
    reader.join()
    error = b''.join(errors).decode(errors='replace')
    if code:
        raise private.RemoteError('Upload to ADA failed: ' + private.redact(error.strip())[-600:])


def stage():
    rev, v = revision(), version()
    old, new = live_folder(), folder(rev)
    if old == new:
        raise SystemExit('This revision is already the live ADA release.')
    lock = open(private.work_dir(v) / 'staging.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    private.remote('umask 077; mkdir -p ' + new + '/src ' + new + '/content ' + new + '/staff')
    for profile, dirname in [('student', 'content'), ('staff', 'staff')]:
        local = ROOT / ('dist-' + profile)
        dest = new + '/' + dirname
        m = json.loads((local / 'build-manifest.json').read_bytes())
        if not (m['revision'] == rev and m['edition'] == profile and m['version'] == v and not m['dirty']):
            raise SystemExit(f'dist-{profile} is not a clean {v} build of {rev[:10]}; run land_build.py first.')
        upload(dest, [('build-manifest.json', local / 'build-manifest.json')])
        common = f"""from pathlib import Path
import os,hashlib,json
d=Path({dest!r})
files=json.loads((d/'build-manifest.json').read_bytes())['files']
"""
        # Reuse identical files from the live release by hard link; upload only new content.
        raw = private.remote_python(common + f"""
index={{}}
for loc in [{(old + '/content')!r},{(old + '/staff')!r},{(new + '/content')!r}]:
 src=Path(loc)
 if not (src/'build-manifest.json').is_file():continue
 for n,e in json.loads((src/'build-manifest.json').read_bytes())['files'].items():
  p=src/n
  if p.is_file() and p.stat().st_size==e['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']:index[e['sha256']]=p
need=[]
for n,e in files.items():
 p=d/n;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  if p.stat().st_size==e['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']:continue
  p.unlink()
 src=index.get(e['sha256'])
 if src and src.exists():os.link(src,p)
 elif src is None:index[e['sha256']]=p;need.append(n)
print(json.dumps(need))
""")
        names = json.loads(raw)
        print(profile, 'new files', len(names), flush=True)
        if names:
            upload(dest, [(n, local / n) for n in names])
        private.remote_python(common + """
index={e['sha256']:d/n for n,e in files.items() if (d/n).is_file()}
for n,e in files.items():
 p=d/n
 if not p.exists():os.link(index[e['sha256']],p)
 assert p.stat().st_size==e['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],n
assert {str(p.relative_to(d)) for p in d.rglob('*') if p.is_file()}==set(files)|{'build-manifest.json'}
""")
    upload(new + '/src', [(str(p.relative_to(ROOT)), p) for p in sorted((ROOT / 'student_server').glob('*.py'))]
           + [('tests/test_student_auth.py', ROOT / 'tests/test_student_auth.py')])
    private.remote_python(f"""from pathlib import Path
for n in ['launch','start','nginx.conf']:
 a=Path({old!r})/n;b=Path({new!r})/n;b.write_bytes(a.read_bytes().replace({old.encode()!r},{new.encode()!r}));b.chmod(a.stat().st_mode&0o777)
""")
    private.remote(private.layout('nginx') + ' -t -c ' + new + '/nginx.conf')
    (private.work_dir(v) / 'ada-previous-folder').write_text(old)
    print('Staged ADA', label(new), 'beside the live', label(old), flush=True)


def snapshot_path(rev):
    p = private.state_dir() / 'ada-student'
    p.mkdir(exist_ok=True)
    return p / ('accounts-before-' + rev[:10] + '.sqlite')


def activate(allow_server_change=False):
    rev = revision()
    if subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=ROOT, text=True).split()[0] != rev:
        raise SystemExit('Activate only the revision at the tip of origin/main.')
    old, new = live_folder(), folder(rev)
    live_rev = json.loads(private.remote('cat ' + old + '/staff/build-manifest.json'))['revision']
    changed = subprocess.check_output(['git', 'diff', '--name-only', f'{live_rev}..{rev}', '--', 'student_server', 'requirements-auth.txt'],
                                      cwd=ROOT, text=True).strip()
    if changed and not allow_server_change:
        raise SystemExit('The ADA server code changed since the live release; review it and rerun with --allow-server-change.')
    data = private.layout('dataDir')
    back = data + '/backup-' + rev[:10] + '.sqlite'
    private.remote_python(f"""import sqlite3,os
os.umask(0o077)
src=sqlite3.connect({data + '/accounts.sqlite'!r});dst=sqlite3.connect({back!r});src.backup(dst);assert dst.execute('pragma integrity_check').fetchone()==('ok',);dst.close()
""")
    target = snapshot_path(rev)
    with open(target, 'wb', opener=lambda p, f: os.open(p, f, 0o600)) as f:
        f.write(private.remote('cat ' + back))
    if sqlite3.connect(target).execute('pragma integrity_check').fetchone() != ('ok',):
        raise SystemExit('Private account snapshot failed its integrity check.')
    private.remote('rm ' + back)
    start = private.layout('startScript')
    restart = private.layout('supervisorCommand') + ' restart ' + private.layout('serviceName')
    private.remote(f'cmp {start} {old}/start && install -m 700 {new}/start {start}.luisa-next && mv {start}.luisa-next {start} && {restart}')
    print('Activated ADA', label(new), '(account snapshot kept privately)', flush=True)


def rollback():
    v = version()
    previous = (private.work_dir(v) / 'ada-previous-folder').read_text().strip()
    new = folder(revision())
    start = private.layout('startScript')
    restart = private.layout('supervisorCommand') + ' restart ' + private.layout('serviceName')
    private.remote(f'cmp {start} {new}/start && install -m 700 {previous}/start {start}.luisa-rollback && mv {start}.luisa-rollback {start} && {restart}')
    print('Rolled ADA back to', label(previous), flush=True)


def accounts_check(allow_first_signin=False):
    rev = revision()
    p = snapshot_path(rev)
    db = private.layout('dataDir') + '/accounts.sqlite'
    if not allow_first_signin:
        c = sqlite3.connect(p)
        expected = hashlib.sha256(json.dumps([c.execute(q).fetchall() for q in ACCOUNT_QUERIES]).encode()).hexdigest()
        actual = private.remote_python(f"import sqlite3,hashlib,json\nc=sqlite3.connect({db!r})\nqueries={ACCOUNT_QUERIES!r}\n"
                                       "print(hashlib.sha256(json.dumps([c.execute(q).fetchall() for q in queries]).encode()).hexdigest())").decode().strip()
        if actual != expected:
            raise SystemExit('Account directory/credential state changed; investigate before cleanup. '
                             'If real users completed a first sign-in during the deploy, rerun with --allow-completed-first-signin.')
        print('Existing student, staff and admin credentials and name directories preserved exactly.')
        return
    # Strict variant: a row may differ only by a forced-change first sign-in completed after the snapshot.
    snap = datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    same = ['select * from teacher_credential order by singleton', 'select * from student_directory order by school_number',
            'select * from teacher_directory order by username']
    staff = 'select username,password_hash,temporary_hash,active,force_change,last_sign_in_utc,signins from staff_accounts order by username'
    pupil = 'select school_number,password_hash,temporary_hash,active,force_change,last_sign_in_utc,signins from accounts order by school_number'
    c = sqlite3.connect(p)
    live = json.loads(private.remote_python(f"import sqlite3,json\nc=sqlite3.connect({db!r})\nprint(json.dumps([c.execute(q).fetchall() for q in {same + [staff, pupil]!r}]))").decode())
    for q, rows in zip(same, live):
        if json.loads(json.dumps(c.execute(q).fetchall())) != rows:
            raise SystemExit('changed: ' + q.split(' from ')[1].split()[0])
    counts = {}
    for name, q, rows in (('staff', staff, live[-2]), ('pupil', pupil, live[-1])):
        before = {r[0]: r for r in json.loads(json.dumps(c.execute(q).fetchall()))}
        after = {r[0]: r for r in rows}
        if set(before) != set(after):
            raise SystemExit(name + ' accounts added or removed')
        counts[name] = 0
        for user, a in after.items():
            b = before[user]
            if b[1:5] == a[1:5]:
                continue
            if not (b[2] is not None and a[2] is None and b[4] == 1 and a[4] == 0 and b[3] == a[3]
                    and a[6] == (b[6] or 0) + 1 and a[5] and a[5] > snap):
                raise SystemExit('unexplained ' + name + ' credential change')
            counts[name] += 1
    print(f"Existing student, staff and admin credentials and name directories preserved exactly, apart from first sign-ins "
          f"completed through the forced-change flow after the {snap} snapshot (staff {counts['staff']}, pupils {counts['pupil']}).")


def cleanup():
    v = version()
    current = folder(revision())
    if live_folder() != current:
        raise SystemExit('The merged revision is not the live ADA release; nothing was removed.')
    previous_path = private.work_dir(v) / 'ada-previous-folder'
    previous = previous_path.read_text().strip() if previous_path.exists() else None
    if previous:
        saved = private.state_dir() / 'ada-student' / f'gateway-{Path(previous).name}-before-v{v}.tar.gz'
        saved.write_bytes(private.remote(f'tar czf - -C {previous} launch start nginx.conf src content/build-manifest.json staff/build-manifest.json'))
        with tarfile.open(saved) as tf:
            assert 'start' in tf.getnames()
    data = private.layout('dataDir')
    private.remote_python(f"""from pathlib import Path
import shutil,re
current=Path({current!r});assert Path({private.layout('startScript')!r}).read_bytes()==(current/'start').read_bytes()
env=Path({data + '/gateway.env'!r});lines=env.read_bytes().splitlines(keepends=True)
pattern=re.escape({(private.layout('releaseRoot') + '/' + private.layout('releasePrefix')).encode()!r})+rb'[0-9a-f]+'
for i,line in enumerate(lines):
 if b'LUISA_STUDENT_BUILD_DIR=' in line or b'LUISA_STAFF_BUILD_DIR=' in line:lines[i]=re.sub(pattern,str(current).encode(),line)
temp=env.with_suffix('.next');temp.write_bytes(b''.join(lines));temp.chmod(0o600);temp.replace(env)
root=Path({private.layout('releaseRoot')!r})
for p in root.glob({private.layout('releasePrefix')!r}+'*'):
 if p.is_dir() and p!=current:shutil.rmtree(p)
for p in root.glob('.stage-*'):
 if p.is_dir():shutil.rmtree(p)
""")
    print('ADA keeps only the verified release folder; the previous gateway files are saved privately.', flush=True)


def status():
    old = live_folder()
    restart = private.layout('supervisorCommand') + ' status ' + private.layout('serviceName')
    state = private.remote(restart, check=False).decode()
    m = json.loads(private.remote('cat ' + old + '/staff/build-manifest.json'))
    print(json.dumps({'liveFolder': label(old), 'revision': m['revision'], 'version': m['version'],
                      'running': 'RUNNING' in state}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['status', 'stage', 'activate', 'accounts-check', 'rollback', 'cleanup'])
    parser.add_argument('--allow-server-change', action='store_true')
    parser.add_argument('--allow-completed-first-signin', action='store_true')
    args = parser.parse_args()
    os.umask(0o077)
    if args.command == 'stage':
        stage()
    elif args.command == 'activate':
        activate(args.allow_server_change)
    elif args.command == 'accounts-check':
        accounts_check(args.allow_completed_first_signin)
    else:
        {'status': status, 'rollback': rollback, 'cleanup': cleanup}[args.command]()


if __name__ == '__main__':
    main()
