"""ADA student content gateway. All durable state is private SQLite data."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
from html import escape
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from zoneinfo import ZoneInfo

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from flask import Flask, abort, g, make_response, redirect, render_template_string, request, send_from_directory, url_for
import pyotp


_PH = PasswordHasher()
_DUMMY_PASSWORD_HASH = _PH.hash(secrets.token_urlsafe(32))
_SCHOOL_NUMBER = re.compile(r"[0-9]{5}\Z", re.ASCII)
_SIGN_IN = re.compile(r"[0-9]{5}@marlboroughcollege\.org\Z", re.ASCII | re.IGNORECASE)
_UTC = timezone.utc
_UK = ZoneInfo('Europe/London')

PDF_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{{ title }}</title><style>body{margin:0;height:100dvh;display:flex;flex-direction:column;font:16px system-ui}
nav{display:flex;align-items:center;justify-content:space-between;padding:.6rem 1rem;background:#183957}a{color:white}
iframe{width:100%;border:0;flex:1}</style><nav><a href="{{ file }}?download=1" download>Download PDF</a>
<a href="{{ url_for('confirm_logout') }}" target=_top>Sign out</a></nav><iframe src="{{ file }}?inline=1" title="{{ title }}"></iframe></html>"""
LOGIN_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Luisa sign in</title><style>body{font:17px system-ui;max-width:32rem;margin:8vh auto;padding:1.5rem;color:#183957}label,input,button{display:block;width:100%;box-sizing:border-box;margin:.5rem 0 1rem}input,button{font:inherit;padding:.7rem}button{background:#183957;color:white;border:0;border-radius:.3rem}.error{color:#8b2020}</style><h1>Luisa sign in</h1>{% if error %}<p class=error role=alert>{{ error }}</p>{% endif %}<form method=post><input type=hidden name=_csrf value='{{ csrf }}'><label>School email or staff username<input name=email type=text autocomplete=username required maxlength=64></label><label>Luisa password<input name=password type=password autocomplete=current-password required maxlength=1024></label><button>Sign in</button></form><p><a href="{{ url_for('admin_login') }}">Admin sign in</a></p></html>"""
ADMIN_LOGIN_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Luisa administration sign in</title><style>body{font:17px system-ui;max-width:32rem;margin:8vh auto;padding:1.5rem;color:#183957}label,input,button{display:block;width:100%;box-sizing:border-box;margin:.5rem 0 1rem}input,button{font:inherit;padding:.7rem}button{background:#183957;color:white;border:0;border-radius:.3rem}.error{color:#8b2020}</style><h1>Teacher sign in</h1>{% if error %}<p class=error role=alert>{{ error }}</p>{% endif %}<form method=post><input type=hidden name=_csrf value='{{ csrf }}'><label>Username<input name=username value=admin autocomplete=username required></label><label>Teacher password<input name=password type=password autocomplete=current-password required maxlength=1024></label>{% if config.ADMIN_AUTH_MODE == "totp" %}<label>Authenticator code<input name=totp inputmode=numeric autocomplete=one-time-code required pattern='[0-9]{6}'></label>{% endif %}<button>Sign in</button></form></html>"""
CHANGE_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Change Luisa password</title><style>body{font:17px system-ui;max-width:32rem;margin:8vh auto;padding:1.5rem;color:#183957}label,input,button{display:block;width:100%;box-sizing:border-box;margin:.5rem 0 1rem}input,button{font:inherit;padding:.7rem}button{background:#183957;color:white;border:0;border-radius:.3rem}.error{color:#8b2020}</style><p style="text-align:right"><a href="{{ url_for('confirm_logout') }}">Sign out</a></p><h1>Choose a new Luisa password</h1><p>Change your temporary password before opening course content.</p>{% if error %}<p class=error role=alert>{{ error }}</p>{% endif %}<form method=post><input type=hidden name=_csrf value='{{ csrf }}'><label>New password<input name=password type=password autocomplete=new-password required minlength=8 maxlength=1024></label><label>Repeat new password<input name=confirm type=password autocomplete=new-password required minlength=8 maxlength=1024></label><button>Save password</button></form></html>"""
TEACHER_PASSWORD_PAGE = """<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Change teacher password · Luisa</title>
<style>body{font:17px/1.5 system-ui;color:#183957;max-width:32rem;margin:6vh auto;padding:1.5rem}
label,input,button{display:block}input,button{box-sizing:border-box;width:100%;padding:.7rem;font:inherit}
label{margin:1rem 0}button{background:#183957;color:white;border:0;border-radius:.3rem}[role=alert]{color:#8b2020}</style>
<a href="{{ url_for('admin_home') }}">Back to student accounts</a> · <a href="{{ url_for('confirm_logout') }}">Sign out</a><h1>Change teacher password</h1>
{% if error %}<p role=alert>{{ error }}</p>{% endif %}
<form method=post><input type=hidden name=_csrf value='{{ csrf }}'>
<label>Current teacher password<input name=current type=password autocomplete=current-password required maxlength=1024></label>
<label>New teacher password (at least 8 characters)<input name=password type=password autocomplete=new-password required minlength=8 maxlength=1024></label>
<label>Repeat new password<input name=confirm type=password autocomplete=new-password required maxlength=1024></label>
<button>Save password</button></form></html>"""

SLIPS_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Luisa password slips</title><style>@page{size:A4;margin:12mm}body{font:16px/1.45 system-ui;color:#183957}
main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}article{border:1px dashed #778;padding:5mm;break-inside:avoid;overflow-wrap:anywhere}
h2,p{margin:.4em 0}code{font-size:1.1em}nav{margin:1em}button{font:inherit}@media print{nav{display:none}main{display:block}article{display:inline-block;vertical-align:top;width:49%;box-sizing:border-box}}</style>
<nav><button onclick="window.print()">Print slips</button> <a href="{{ url_for('admin_home') }}">Back to student accounts</a> · <a href="{{ url_for('confirm_logout') }}">Sign out</a></nav>
<main>{% for row, password in slips %}<article><h2>Luisa · {{ row.school_number }}</h2><p>{{ link }}</p>
<p>School email<br>{{ row.school_number }}@marlboroughcollege.org</p><p>First password<br><code>{{ password }}</code></p>
<p>Sign in once, then choose your own Luisa password.</p></article>{% endfor %}</main></html>"""

ADMIN_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Luisa account administration</title><style>body{font:16px/1.5 system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#183957}table{border-collapse:collapse;width:100%;margin:1.5rem 0}td,th{border:1px solid #ccd5df;padding:.5rem;text-align:left}button,input,textarea{font:inherit;padding:.45rem;margin:.2rem}form{display:inline}section{padding:1rem;border:1px solid #ccd5df;margin:1rem 0}.notice{background:#edf5fb;padding:.8rem}.secret{font:1.15rem monospace;overflow-wrap:anywhere}small{color:#526575}</style><h1>Luisa student accounts</h1><p><a href='{{ url_for("teacher_password") }}'>Change teacher password</a> · <a href='{{ url_for("logout") }}' onclick="event.preventDefault();document.getElementById('logout').submit()">Sign out</a><form id=logout method=post action='{{ url_for("logout") }}'><input type=hidden name=_csrf value='{{ csrf }}'></form></p>{% if notice %}<p class=notice role=status>{{ notice }}</p>{% endif %}{% if temp_password %}<section><b>Give this temporary password to pupil {{ temp_school_number }} privately. It works until the first successful sign-in or until you replace it.</b><p class=secret>{{ temp_password }}</p></section>{% endif %}<section><h2>Staff accounts</h2><table><tr><th>Username</th><th>Access</th></tr>{% for member in staff %}<tr><td>{{ member.username }}</td><td>{{ 'Active' if member.active else 'Suspended' }}</td></tr>{% endfor %}</table></section><section><h2>Class password slips</h2><form method=post action='{{ url_for("issue_slips") }}'><input type=hidden name=_csrf value='{{ csrf }}'><label>Class <select name=class_code><option value="">All classes</option>{% for code in classes %}<option>{{ code }}</option>{% endfor %}</select></label><button>Create printable slips</button></form><p>Creates one slip for each active pupil who has never been issued a password. Print the sheet before closing it. To replace a lost slip, issue a new password on the pupil’s row.</p></section><section><h2>Add school numbers</h2><form method=post action='{{ url_for("add_roster") }}'><input type=hidden name=_csrf value='{{ csrf }}'><label>Class (optional) <input name=class_code maxlength=12></label><label>One per line; leading zeroes are preserved<br><textarea name=numbers rows=5 cols=24 required></textarea></label><button>Add roster entries</button></form></section><table><thead><tr><th>Class</th><th>School number</th><th>Cohort</th><th>Access</th><th>Latest successful sign-in</th><th>Account controls</th></tr></thead><tbody>{% for row in rows %}<tr><td>{{ row.class_code }}</td><td>{{ row.number }}</td><td>{{ row.cohort }}</td><td>{{ 'Active' if row.active else 'Suspended' }}{% if row.force_change %} · password change required{% endif %}</td><td>{{ row.last_sign_in }}</td><td><form method=post action='{{ url_for("account_action") }}'><input type=hidden name=_csrf value='{{ csrf }}'><input type=hidden name=school_number value='{{ row.number }}'><select name=action><option value=reset>Issue temporary password</option><option value=force>Force password change</option><option value=suspend>Suspend</option><option value=reactivate>Reactivate</option><option value=revoke>Revoke sessions</option></select><label>Optional temporary password <input name=chosen_password type=password minlength=8 maxlength=128 autocomplete=off></label><button>Apply</button></form></td></tr>{% endfor %}</tbody></table><p><small>Only the latest successful student sign-in is displayed. UK local time. Student names and dates of birth are not collected.</small></p></html>"""


class LoginLimiter:
    """Short-lived in-process throttle counters keyed by identifier digest, never IP."""
    def __init__(self, limit=8, window_seconds=900):
        self.limit = limit
        self.window = window_seconds
        self.entries: dict[str, tuple[float, int]] = {}
        self.lock = threading.Lock()

    def allowed(self, key: str) -> bool:
        now = time.monotonic()
        with self.lock:
            start, failures = self.entries.get(key, (now, 0))
            if now - start >= self.window:
                self.entries[key] = (now, 0)
                return True
            return failures < self.limit

    def failed(self, key: str) -> None:
        now = time.monotonic()
        with self.lock:
            start, failures = self.entries.get(key, (now, 0))
            if now - start >= self.window:
                self.entries[key] = (now, 1)
            else:
                self.entries[key] = (start, failures + 1)

    def succeeded(self, key: str) -> None:
        with self.lock:
            self.entries.pop(key, None)


def utc_now() -> datetime:
    return datetime.now(_UTC)


def utc_text(value: datetime | None = None) -> str:
    return (value or utc_now()).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def digest_session(value: str) -> str:
    return sha256(value.encode('ascii')).hexdigest()


def email_key(value: str, key: bytes) -> str:
    return hmac.new(key, value[:120].encode('utf-8', 'ignore'), sha256).hexdigest()


def password_ok(encoded: str | None, candidate: str) -> bool:
    if not encoded:
        return False
    try:
        return _PH.verify(encoded, candidate)
    except (VerifyMismatchError, VerificationError, InvalidHashError, ValueError):
        return False


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        STUDENT_BUILD_DIR=os.environ.get('LUISA_STUDENT_BUILD_DIR', ''),
        DATABASE_PATH=os.environ.get('LUISA_STUDENT_DATABASE', ''),
        ADMIN_PASSWORD_HASH=os.environ.get('LUISA_ADMIN_PASSWORD_HASH', ''),
        TEACHER_SETUP=os.environ.get('LUISA_TEACHER_SETUP') == '1',
        PUBLIC_ORIGIN=os.environ.get('LUISA_PUBLIC_ORIGIN', 'https://adazmq.marlboroughcollege.org'),
        ADMIN_AUTH_MODE=os.environ.get('LUISA_ADMIN_AUTH_MODE', 'totp'),
        ADMIN_TOTP_SECRET=os.environ.get('LUISA_ADMIN_TOTP_SECRET', ''),
        SCHOOL_YEAR=os.environ.get('LUISA_SCHOOL_YEAR', '2026-27'),
        SESSION_COOKIE='__Secure-LuisaSession',
        LOGIN_CSRF_COOKIE='__Secure-LuisaLoginCSRF',
        SESSION_COOKIE_PATH=os.environ.get('LUISA_COOKIE_PATH', os.environ.get('LUISA_URL_PREFIX', '/') or '/'),
        SESSION_SECONDS=3600,
        SESSION_ABSOLUTE_SECONDS=12 * 3600,
        MAX_CONTENT_LENGTH=16 * 1024,
        COOKIE_SECURE=True,
    )
    if overrides:
        app.config.update(overrides)
    prefix = app.config['SESSION_COOKIE_PATH']
    if prefix != '/' and (not prefix.startswith('/') or prefix.endswith('/') or '..' in prefix.split('/')):
        raise RuntimeError('Cookie path must be / or a normalized absolute URL prefix such as /AL')
    if not app.config['STUDENT_BUILD_DIR'] or not app.config['DATABASE_PATH']:
        raise RuntimeError('Student build directory and private database path must be configured')
    build_dir = Path(app.config['STUDENT_BUILD_DIR']).resolve()
    db_path = Path(app.config['DATABASE_PATH']).resolve()
    source_root = Path(__file__).resolve().parents[1]
    mode = app.config['ADMIN_AUTH_MODE']
    if mode not in {'password', 'totp'} or not app.config['ADMIN_PASSWORD_HASH']:
        raise RuntimeError('A supported teacher sign-in mode and password hash are required')
    if mode == 'totp' and not app.config['ADMIN_TOTP_SECRET']:
        raise RuntimeError('Teacher authenticator secret is missing for TOTP mode')
    if not build_dir.is_dir() or db_path.is_relative_to(build_dir) or db_path.is_relative_to(source_root):
        raise RuntimeError('Student artifact must exist and authentication storage must be outside public and source trees')
    build_manifest = build_dir / 'build-manifest.json'
    if not build_manifest.is_file():
        raise RuntimeError('Student artifact is missing build-manifest.json')
    manifest = json.loads(build_manifest.read_text())
    asset_paths = frozenset(manifest.get('files', {}))
    if manifest.get('edition') != 'student':
        raise RuntimeError('Refusing to serve a non-student artifact')

    app.logger.disabled = True
    limiter = LoginLimiter()
    app.extensions['luisa_login_limiter'] = limiter
    rate_key = secrets.token_bytes(32)

    def connect_db():
        conn = sqlite3.connect(str(db_path), timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=10000')
        return conn

    def db():
        if 'luisa_db' not in g:
            g.luisa_db = connect_db()
        return g.luisa_db

    @app.teardown_appcontext
    def close_db(_error=None):
        conn = g.pop('luisa_db', None)
        if conn is not None:
            conn.close()

    def init_db():
        db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            os.chmod(db_path.parent, 0o700)
        except OSError:
            pass
        conn = connect_db()
        try:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS accounts (
                    school_number TEXT PRIMARY KEY CHECK(length(school_number)=5 AND school_number NOT GLOB '*[^0-9]*'),
                    password_hash TEXT,
                    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
                    force_change INTEGER NOT NULL DEFAULT 0 CHECK(force_change IN (0,1)),
                    temporary_hash TEXT,
                    temporary_expires_utc TEXT,
                    last_sign_in_utc TEXT
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    session_hash TEXT PRIMARY KEY,
                    school_number TEXT REFERENCES accounts(school_number) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK(role IN ('student','admin')),
                    must_change INTEGER NOT NULL DEFAULT 0 CHECK(must_change IN (0,1)),
                    csrf_token TEXT NOT NULL,
                    created_utc TEXT NOT NULL,
                    expires_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS staff_accounts (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    temporary_hash TEXT,
                    temporary_available INTEGER NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1,
                    force_change INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS teacher_credential (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    password_hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS admin_mfa_state (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    last_accepted_step INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO admin_mfa_state(singleton,last_accepted_step) VALUES(1,-1);
            ''')
            conn.execute('BEGIN IMMEDIATE')
            if 'staff_username' not in {row['name'] for row in conn.execute('PRAGMA table_info(sessions)')}:
                conn.execute('ALTER TABLE sessions RENAME TO old_sessions')
                conn.execute("""CREATE TABLE sessions (
                    session_hash TEXT PRIMARY KEY,
                    school_number TEXT REFERENCES accounts(school_number) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK(role IN ('student','staff','admin')),
                    must_change INTEGER NOT NULL DEFAULT 0 CHECK(must_change IN (0,1)),
                    csrf_token TEXT NOT NULL, created_utc TEXT NOT NULL, expires_utc TEXT NOT NULL,
                    staff_username TEXT REFERENCES staff_accounts(username) ON DELETE CASCADE,
                    CHECK ((role='staff')=(staff_username IS NOT NULL)),
                    CHECK ((role='student')=(school_number IS NOT NULL))
                )""")
                conn.execute("""INSERT INTO sessions(session_hash,school_number,role,must_change,csrf_token,created_utc,expires_utc)
                    SELECT session_hash,school_number,role,must_change,csrf_token,created_utc,expires_utc FROM old_sessions""")
                conn.execute('DROP TABLE old_sessions')
            columns = {row['name'] for row in conn.execute('PRAGMA table_info(accounts)')}
            if 'class_code' not in columns:
                conn.execute("ALTER TABLE accounts ADD COLUMN class_code TEXT NOT NULL DEFAULT ''")
            if 'temporary_available' not in columns:
                conn.execute('ALTER TABLE accounts ADD COLUMN temporary_available INTEGER NOT NULL DEFAULT 0')
                conn.execute('UPDATE accounts SET temporary_available=1 WHERE temporary_expires_utc IS NOT NULL')
            conn.execute("""DELETE FROM sessions WHERE role='student' AND rowid IN (
                SELECT id FROM (SELECT rowid AS id, ROW_NUMBER() OVER (
                    PARTITION BY school_number ORDER BY created_utc DESC, rowid DESC) AS n FROM sessions WHERE role='student')
                WHERE n>1)""")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS single_pupil_session ON sessions(school_number) WHERE role='student'")
            conn.execute('INSERT OR IGNORE INTO teacher_credential VALUES(1, ?)', (app.config['ADMIN_PASSWORD_HASH'],))
            conn.commit()
            conn.execute('PRAGMA journal_mode=WAL')
        finally:
            conn.close()
        try:
            os.chmod(db_path, 0o600)
            if Path(str(db_path) + '-wal').exists(): os.chmod(str(db_path) + '-wal', 0o600)
            if Path(str(db_path) + '-shm').exists(): os.chmod(str(db_path) + '-shm', 0o600)
        except OSError:
            pass

    app.extensions['luisa_init_db'] = init_db

    @app.cli.command('init-db')
    def init_db_command():
        init_db()
        print('Private Luisa account database initialized.')

    def new_session(role: str, identity: str | None = None, must_change: bool = False):
        if role == 'student':
            db().execute("DELETE FROM sessions WHERE school_number=? AND role='student'", (identity,))
        token = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        created = utc_now()
        expiry = utc_text(created + timedelta(seconds=app.config['SESSION_SECONDS']))
        db().execute('INSERT INTO sessions(session_hash,school_number,role,must_change,csrf_token,created_utc,expires_utc,staff_username) VALUES(?,?,?,?,?,?,?,?)',
                     (digest_session(token), identity if role == 'student' else None, role, int(must_change), csrf, utc_text(created), expiry, identity if role == 'staff' else None))
        return token

    def establish(token: str):
        response = redirect(url_for('change_password') if g.luisa_session['must_change'] else url_for('index'))
        response.set_cookie(app.config['SESSION_COOKIE'], token, max_age=app.config['SESSION_SECONDS'],
                            secure=True, httponly=True, samesite='Lax', path=app.config['SESSION_COOKIE_PATH'])
        return response

    def csrf_ok() -> bool:
        session = getattr(g, 'luisa_session', None)
        candidate = request.form.get('_csrf', '')
        return bool(session and candidate and hmac.compare_digest(session['csrf_token'], candidate))

    def require_csrf():
        if not csrf_ok():
            abort(400)

    @app.before_request
    def load_private_session():
        g.luisa_session = None
        if not request.is_secure and not app.testing and request.endpoint != 'health':
            abort(400)
        if request.path in {'/login', '/admin/login'} or request.path.endswith('/sw.js') or request.path == '/healthz':
            return None
        token = request.cookies.get(app.config['SESSION_COOKIE'], '')
        if token:
            session_hash = digest_session(token)
            now = utc_now()
            row = db().execute('SELECT * FROM sessions WHERE session_hash=? AND expires_utc>? AND created_utc>?',
                               (session_hash, utc_text(now), utc_text(now - timedelta(seconds=app.config['SESSION_ABSOLUTE_SECONDS'])))).fetchone()
            if not row:
                db().execute('DELETE FROM sessions WHERE session_hash=?', (session_hash,))
            if row:
                if row['role'] in {'student', 'staff'}:
                    if row['role'] == 'staff':
                        account = db().execute('SELECT active,force_change FROM staff_accounts WHERE username=?', (row['staff_username'],)).fetchone()
                    else:
                        account = db().execute('SELECT active,force_change FROM accounts WHERE school_number=?', (row['school_number'],)).fetchone()
                    if not account or not account['active']:
                        db().execute('DELETE FROM sessions WHERE session_hash=?', (row['session_hash'],))
                        row = None
                    elif account['force_change'] and not row['must_change']:
                        db().execute('UPDATE sessions SET must_change=1 WHERE session_hash=?', (row['session_hash'],))
                        row = dict(row); row['must_change'] = 1
                if row:
                    db().execute('UPDATE sessions SET expires_utc=? WHERE session_hash=?',
                                 (utc_text(utc_now() + timedelta(seconds=app.config['SESSION_SECONDS'])), row['session_hash']))
                    g.luisa_session = dict(row)
        public = {'login', 'admin_login', 'service_worker', 'health'}
        endpoint = request.endpoint
        if endpoint not in public and g.luisa_session is None:
            if request.path.startswith('/admin'):
                return redirect(url_for('admin_login'))
            return redirect(url_for('login'))
        if (app.config['TEACHER_SETUP'] and g.luisa_session and g.luisa_session['role'] == 'admin'
                and endpoint not in {'teacher_password', 'confirm_logout', 'logout'} and teacher_hash() == app.config['ADMIN_PASSWORD_HASH']):
            return redirect(url_for('teacher_password'))
        if endpoint in {'change_password', 'change_password_post'} and g.luisa_session and g.luisa_session['role'] in {'student', 'staff'}:
            return None
        if g.luisa_session and g.luisa_session['role'] in {'student', 'staff'} and g.luisa_session['must_change'] and endpoint not in {'change_password', 'change_password_post', 'confirm_logout', 'logout'}:
            return redirect(url_for('change_password'))
        return None

    @app.after_request
    def private_headers(response):
        response.headers['Cache-Control'] = 'private, no-store, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        embedded = request.endpoint == 'private_asset'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN' if embedded else 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors " + ("'self'" if embedded else "'none'")
        token = request.cookies.get(app.config['SESSION_COOKIE'])
        if token and getattr(g, 'luisa_session', None) and g.luisa_session.get('session_hash') == digest_session(token):
            response.set_cookie(app.config['SESSION_COOKIE'], token, max_age=app.config['SESSION_SECONDS'],
                                secure=True, httponly=True, samesite='Lax', path=app.config['SESSION_COOKIE_PATH'])
        return response

    def base_context():
        session = getattr(g, 'luisa_session', None)
        return session['csrf_token'] if session else ''

    def render_login(template, error=None):
        token = secrets.token_urlsafe(32)
        response = make_response(render_template_string(template, csrf=token, error=error))
        response.set_cookie(app.config['LOGIN_CSRF_COOKIE'], token, max_age=600, secure=True,
                            httponly=True, samesite='Lax', path=app.config['SESSION_COOKIE_PATH'])
        return response

    def login_csrf_ok() -> bool:
        cookie = request.cookies.get(app.config['LOGIN_CSRF_COOKIE'], '')
        candidate = request.form.get('_csrf', '')
        return bool(cookie and candidate and hmac.compare_digest(cookie, candidate))

    def consume_admin_totp(code: str) -> bool:
        if not re.fullmatch(r'[0-9]{6}', code, re.ASCII):
            return False
        totp = pyotp.TOTP(app.config['ADMIN_TOTP_SECRET'])
        current_step = int(time.time() // totp.interval)
        matching = [step for step in (current_step - 1, current_step, current_step + 1)
                    if step >= 0 and totp.verify(code, for_time=step * totp.interval, valid_window=0)]
        if not matching:
            return False
        latest = max(matching)
        result = db().execute('UPDATE admin_mfa_state SET last_accepted_step=? WHERE singleton=1 AND last_accepted_step<?',
                              (latest, latest))
        return result.rowcount == 1

    @app.get('/login')
    def login():
        return render_login(LOGIN_PAGE)

    @app.post('/login')
    def student_login():
        if not login_csrf_ok():
            abort(400)
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        username = email.lower().removesuffix('@marlboroughcollege.org')
        is_staff = email.isascii() and re.fullmatch(r'[a-z][a-z0-9._-]{0,31}', username) and username != 'admin'
        key = email_key(username if is_staff else email.casefold(), rate_key)
        if not limiter.allowed(key):
            return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details or contact your teacher.'), 429
        if is_staff:
            return staff_login(username, password, key)
        school_number = email[:5] if _SIGN_IN.fullmatch(email) else ''
        account = db().execute('SELECT * FROM accounts WHERE school_number=? AND active=1', (school_number,)).fetchone() if school_number else None
        temp_is_valid = bool(account and account['temporary_hash'] and account['temporary_available'] and (not account['temporary_expires_utc'] or account['temporary_expires_utc'] > utc_text()))
        permanent_hash = account['password_hash'] if account and account['password_hash'] else _DUMMY_PASSWORD_HASH
        temporary_hash = account['temporary_hash'] if temp_is_valid else _DUMMY_PASSWORD_HASH
        if len(password) <= 1024:
            permanent_ok = password_ok(permanent_hash, password)
            temporary_ok = password_ok(temporary_hash, password)
        else:
            permanent_ok = temporary_ok = False
        using_temporary = bool(temp_is_valid and temporary_ok and not permanent_ok)
        ok = permanent_ok or using_temporary
        needs_change = using_temporary
        if not ok:
            limiter.failed(key)
            return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details or contact your teacher.'), 401
        db().execute('BEGIN IMMEDIATE')
        if using_temporary:
            consumed = db().execute('UPDATE accounts SET temporary_available=0,temporary_expires_utc=NULL,force_change=1,last_sign_in_utc=? WHERE school_number=? AND active=1 AND temporary_hash=? AND temporary_available=1 AND (temporary_expires_utc IS NULL OR temporary_expires_utc>?)',
                                    (utc_text(), school_number, account['temporary_hash'], utc_text()))
            if consumed.rowcount != 1:
                limiter.failed(key)
                return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details or contact your teacher.'), 401
        elif account['force_change']:
            still_valid = db().execute('UPDATE accounts SET last_sign_in_utc=? WHERE school_number=? AND active=1 AND force_change=1 AND password_hash=?',
                                       (utc_text(), school_number, account['password_hash']))
            if still_valid.rowcount != 1:
                limiter.failed(key)
                return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details or contact your teacher.'), 401
            needs_change = True
        else:
            signed_in = db().execute('UPDATE accounts SET last_sign_in_utc=? WHERE school_number=? AND active=1 AND force_change=0 AND password_hash=?',
                                     (utc_text(), school_number, account['password_hash']))
            if signed_in.rowcount != 1:
                limiter.failed(key)
                return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details or contact your teacher.'), 401
        limiter.succeeded(key)
        token = new_session('student', school_number, needs_change)
        db().execute('COMMIT')
        g.luisa_session = {'must_change': int(needs_change)}
        response = redirect(url_for('change_password') if needs_change else url_for('index'))
        response.set_cookie(app.config['SESSION_COOKIE'], token, max_age=app.config['SESSION_SECONDS'], secure=True,
                            httponly=True, samesite='Lax', path=app.config['SESSION_COOKIE_PATH'])
        return response

    def staff_login(username, password, key):
        account = db().execute('SELECT * FROM staff_accounts WHERE username=? AND active=1', (username,)).fetchone()
        first = bool(account and account['temporary_available'])
        encoded = (account['temporary_hash'] if first else account['password_hash']) if account else None
        if len(password) <= 1024 and password_ok(encoded or _DUMMY_PASSWORD_HASH, password) and encoded:
            db().execute('BEGIN IMMEDIATE')
            if first:
                valid = db().execute("""UPDATE staff_accounts SET temporary_available=0 WHERE username=? AND active=1
                    AND temporary_available=1 AND temporary_hash=?""", (username, encoded)).rowcount
            else:
                valid = db().execute("SELECT 1 FROM staff_accounts WHERE username=? AND active=1 AND password_hash=?",
                                     (username, encoded)).fetchone()
            if valid:
                token = new_session('staff', username, first)
                db().commit()
                limiter.succeeded(key)
                g.luisa_session = {'must_change': first}
                return establish(token)
            db().rollback()
        limiter.failed(key)
        return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details.'), 401

    def teacher_hash():
        return db().execute('SELECT password_hash FROM teacher_credential WHERE singleton=1').fetchone()[0]

    @app.get('/admin/login')
    def admin_login():
        return render_login(ADMIN_LOGIN_PAGE)

    @app.post('/admin/login')
    def admin_login_post():
        if not login_csrf_ok():
            abort(400)
        password = request.form.get('password', '')
        code = request.form.get('totp', '')
        key = email_key('teacher-admin', rate_key)
        if not limiter.allowed(key):
            return render_login(ADMIN_LOGIN_PAGE, 'Sign-in failed.'), 429
        verified_hash = teacher_hash()
        if request.form.get('username') != 'admin' or len(password) > 1024 or not password_ok(verified_hash, password):
            limiter.failed(key)
            return render_login(ADMIN_LOGIN_PAGE, 'Sign-in failed.'), 401
        db().execute('BEGIN IMMEDIATE')
        if verified_hash != teacher_hash() or (mode == 'totp' and not consume_admin_totp(code)):
            db().rollback()
            limiter.failed(key)
            return render_login(ADMIN_LOGIN_PAGE, 'Sign-in failed.'), 401
        limiter.succeeded(key)
        token = new_session('admin')
        db().commit()
        g.luisa_session = {'csrf_token': '', 'must_change': 0}
        setup = app.config['TEACHER_SETUP'] and verified_hash == app.config['ADMIN_PASSWORD_HASH']
        response = redirect(url_for('teacher_password' if setup else 'admin_home'))
        response.set_cookie(app.config['SESSION_COOKIE'], token, max_age=app.config['SESSION_SECONDS'], secure=True,
                            httponly=True, samesite='Lax', path=app.config['SESSION_COOKIE_PATH'])
        return response

    @app.get('/logout')
    def confirm_logout():
        return render_template_string(
            """<!doctype html><meta name=viewport content="width=device-width"><title>Luisa sign out</title>
            <main><h1>Sign out of Luisa</h1><form method=post>
            <input type=hidden name=_csrf value="{{ csrf }}"><button>Sign out</button></form></main>""",
            csrf=base_context())

    @app.post('/logout')
    def logout():
        require_csrf()
        token = request.cookies.get(app.config['SESSION_COOKIE'], '')
        if token:
            db().execute('DELETE FROM sessions WHERE session_hash=?', (digest_session(token),))
        destination = 'admin_login' if g.luisa_session['role'] == 'admin' else 'login'
        g.luisa_session = None
        response = redirect(url_for(destination))
        response.delete_cookie(app.config['SESSION_COOKIE'], path=app.config['SESSION_COOKIE_PATH'], secure=True, httponly=True, samesite='Lax')
        return response

    @app.get('/change-password')
    def change_password():
        if not g.luisa_session or g.luisa_session['role'] not in {'student', 'staff'}:
            return redirect(url_for('login'))
        return render_template_string(CHANGE_PAGE, csrf=base_context(), error=None)

    @app.post('/change-password')
    def change_password_post():
        require_csrf()
        if not g.luisa_session or g.luisa_session['role'] not in {'student', 'staff'} or not g.luisa_session['must_change']:
            abort(403)
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if len(password) < 8 or len(password) > 1024 or password != confirm:
            return render_template_string(CHANGE_PAGE, csrf=base_context(), error='Use at least 8 characters and enter the same password twice.'), 400
        is_staff = g.luisa_session['role'] == 'staff'
        table, column, session_column = ('staff_accounts', 'username', 'staff_username') if is_staff else ('accounts', 'school_number', 'school_number')
        number = g.luisa_session[session_column]
        if password in {number, number + '@marlboroughcollege.org'}:
            return render_template_string(CHANGE_PAGE, csrf=base_context(), error='Choose a password independent of your school number and email.'), 400
        old = db().execute(f'SELECT password_hash,temporary_hash FROM {table} WHERE {column}=? AND active=1', (number,)).fetchone()
        if old is None:
            abort(403)
        if any(password_ok(value, password) for value in old if value):
            return render_template_string(CHANGE_PAGE, csrf=base_context(), error='Choose a different Luisa password.'), 400
        new_hash = _PH.hash(password)
        db().execute('BEGIN IMMEDIATE')
        if not db().execute('SELECT 1 FROM sessions WHERE session_hash=? AND must_change=1', (g.luisa_session['session_hash'],)).fetchone():
            db().execute('ROLLBACK')
            abort(403)
        changed = db().execute(f'UPDATE {table} SET password_hash=?,force_change=0,temporary_hash=NULL,temporary_available=0 WHERE {column}=? AND active=1', (new_hash, number))
        if changed.rowcount != 1:
            abort(403)
        db().execute(f'DELETE FROM sessions WHERE {session_column}=?', (number,))
        token = new_session(g.luisa_session['role'], number, False)
        db().execute('COMMIT')
        g.luisa_session = {'must_change': 0}
        response = redirect(url_for('index'))
        response.set_cookie(app.config['SESSION_COOKIE'], token, max_age=app.config['SESSION_SECONDS'], secure=True,
                            httponly=True, samesite='Lax', path=app.config['SESSION_COOKIE_PATH'])
        return response

    def admin_only(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not g.luisa_session or g.luisa_session.get('role') != 'admin':
                abort(403)
            return fn(*args, **kwargs)
        return wrapped

    def temporary_password(number: str, chosen: str):
        candidate = chosen or secrets.token_urlsafe(18)
        if len(candidate) < 8 or len(candidate) > 128:
            raise ValueError('Temporary passwords must be 8 to 128 characters.')
        if candidate in {number, number + '@marlboroughcollege.org'}:
            raise ValueError('Temporary passwords must be independent of the school number and email.')
        candidate_hash = _PH.hash(candidate)
        now = utc_text()
        db().execute('BEGIN IMMEDIATE')
        try:
            db().execute('UPDATE accounts SET temporary_hash=NULL,temporary_expires_utc=NULL WHERE temporary_expires_utc IS NOT NULL AND temporary_expires_utc<=?', (now,))
            other_hashes = db().execute('SELECT temporary_hash FROM accounts WHERE school_number<>? AND temporary_available=1 AND temporary_hash IS NOT NULL AND (temporary_expires_utc IS NULL OR temporary_expires_utc>?)', (number, now)).fetchall()
            if any(password_ok(row['temporary_hash'], candidate) for row in other_hashes):
                raise ValueError('That password is already active for another pupil. Choose or generate another.')
            updated = db().execute('UPDATE accounts SET password_hash=NULL,force_change=1,temporary_hash=?,temporary_available=1,temporary_expires_utc=NULL WHERE school_number=? AND active=1',
                         (candidate_hash, number))
            if updated.rowcount != 1:
                raise ValueError('Reactivate this account before issuing a password.')
            db().execute('DELETE FROM sessions WHERE school_number=?', (number,))
            db().execute('COMMIT')
        except Exception:
            db().execute('ROLLBACK')
            raise
        return candidate

    def render_admin(notice=None, temp_password=None, temp_school_number=None, status=200):
        rows = []
        labels = {'2026-27': {'23': 'Lower Sixth', '22': 'Upper Sixth'}}
        mapping = labels.get(app.config['SCHOOL_YEAR'], {})
        for account in db().execute('SELECT * FROM accounts ORDER BY class_code,school_number'):
            sign_in = 'Never signed in'
            if account['last_sign_in_utc']:
                value = datetime.fromisoformat(account['last_sign_in_utc'].replace('Z', '+00:00')).astimezone(_UK)
                sign_in = value.strftime('%d %B %Y, %H:%M %Z')
            rows.append({'class_code': account['class_code'], 'number': account['school_number'], 'cohort': mapping.get(account['school_number'][:2], '—'),
                         'active': bool(account['active']), 'force_change': bool(account['force_change']), 'last_sign_in': sign_in})
        staff = db().execute('SELECT username,active FROM staff_accounts ORDER BY username').fetchall()
        return render_template_string(ADMIN_PAGE, staff=staff, rows=rows, csrf=base_context(), notice=notice,
                                      temp_password=temp_password, temp_school_number=temp_school_number,
                                      classes=sorted({row['class_code'] for row in rows if row['class_code']})), status

    @app.get('/admin')
    @admin_only
    def admin_home():
        return render_admin('Teacher password changed.' if request.args.get('password_changed') == '1' else None)

    @app.route('/admin/password', methods=['GET', 'POST'])
    @admin_only
    def teacher_password():
        def form(error=None, status=200):
            return render_template_string(TEACHER_PASSWORD_PAGE, csrf=base_context(), error=error), status

        if request.method == 'GET':
            return form()
        require_csrf()
        current = request.form.get('current', '')
        new = request.form.get('password', '')
        verified_hash = teacher_hash()
        if len(current) > 1024 or not password_ok(verified_hash, current):
            return form('The current teacher password is incorrect.', 400)
        if not 8 <= len(new) <= 1024 or new != request.form.get('confirm'):
            return form('Enter the same new password twice, using at least 8 characters.', 400)
        if new == current:
            return form('Choose a different teacher password.', 400)
        replacement = _PH.hash(new)
        session_hash = g.luisa_session['session_hash']
        db().execute('BEGIN IMMEDIATE')
        changed = db().execute(
            """UPDATE teacher_credential SET password_hash=? WHERE singleton=1 AND password_hash=?
               AND EXISTS (SELECT 1 FROM sessions WHERE session_hash=? AND role='admin' AND expires_utc>?)""",
            (replacement, verified_hash, session_hash, utc_text()))
        if not changed.rowcount:
            db().rollback()
            return redirect(url_for('admin_login'))
        db().execute("DELETE FROM sessions WHERE role='admin' AND session_hash<>?", (session_hash,))
        db().commit()
        return redirect(url_for('admin_home', password_changed=1))

    @app.post('/admin/roster')
    @admin_only
    def add_roster():
        require_csrf()
        class_code = request.form.get('class_code', '').strip().upper()
        if class_code and not re.fullmatch(r'[A-Z0-9-]{1,12}', class_code):
            return render_admin('Use letters, digits or hyphens for the class.', status=400)
        raw = request.form.get('numbers', '')
        candidates = [piece for piece in re.split(r'[\s,;]+', raw.strip()) if piece]
        invalid = False
        db().execute('BEGIN IMMEDIATE')
        for candidate in candidates:
            if not _SCHOOL_NUMBER.fullmatch(candidate):
                invalid = True
                continue
            db().execute('INSERT OR IGNORE INTO accounts(school_number,active,class_code) VALUES(?,1,?)', (candidate, class_code))
        db().execute('COMMIT')
        return render_admin('Roster update complete. Check that every roster entry is exactly five ASCII digits.' if invalid else 'Roster update complete.')

    @app.post('/admin/slips')
    @admin_only
    def issue_slips():
        require_csrf()
        code = request.form.get('class_code', '')
        conn = db()
        conn.execute('BEGIN IMMEDIATE')
        rows = conn.execute("""SELECT school_number FROM accounts
            WHERE active=1 AND password_hash IS NULL AND temporary_hash IS NULL AND force_change=0
            AND last_sign_in_utc IS NULL AND (?='' OR class_code=?) ORDER BY class_code,school_number""", (code, code)).fetchall()
        slips = []
        for row in rows:
            password = secrets.token_urlsafe(15)
            conn.execute("""UPDATE accounts SET temporary_hash=?, temporary_available=1, force_change=1
                WHERE school_number=?""", (_PH.hash(password), row['school_number']))
            slips.append((row, password))
        if slips:
            page = render_template_string(SLIPS_PAGE, slips=slips, link=app.config['PUBLIC_ORIGIN'].rstrip('/') + url_for('login'))
            conn.commit()
            return page
        conn.rollback()
        return render_admin('All active pupils in this selection have already been issued a password, or the selection is empty.')

    @app.post('/admin/account')
    @admin_only
    def account_action():
        require_csrf()
        number = request.form.get('school_number', '')
        action = request.form.get('action', '')
        if not _SCHOOL_NUMBER.fullmatch(number):
            abort(400)
        account = db().execute('SELECT * FROM accounts WHERE school_number=?', (number,)).fetchone()
        if not account:
            abort(404)
        if action == 'reset':
            if not account['active']:
                return render_admin('Reactivate this account before issuing a temporary password.', status=400)
            chosen = request.form.get('chosen_password', '')
            try:
                temp = temporary_password(number, chosen)
            except ValueError as error:
                return render_admin(str(error), status=400)
            return render_admin('Temporary password issued. It will not be shown again after this response.', temp, number)
        if action == 'force':
            db().execute('UPDATE accounts SET force_change=1 WHERE school_number=?', (number,))
            db().execute('DELETE FROM sessions WHERE school_number=?', (number,))
            notice = 'Password change required at next sign-in.'
        elif action == 'suspend':
            db().execute('UPDATE accounts SET active=0 WHERE school_number=?', (number,))
            db().execute('DELETE FROM sessions WHERE school_number=?', (number,))
            notice = 'Access suspended and sessions revoked.'
        elif action == 'reactivate':
            db().execute('UPDATE accounts SET active=1 WHERE school_number=?', (number,))
            notice = 'Access reactivated.'
        elif action == 'revoke':
            db().execute('DELETE FROM sessions WHERE school_number=?', (number,))
            notice = 'Student sessions revoked.'
        else:
            abort(400)
        return render_admin(notice)

    @app.get('/sw.js')
    def service_worker():
        # Migration-only service worker; it contains no offline fetch handler or pack data.
        response = send_from_directory(str(build_dir), 'sw.js')
        response.headers['Service-Worker-Allowed'] = app.config['SESSION_COOKIE_PATH']
        return response

    @app.get('/healthz')
    def health():
        return 'ok', 200, {'Content-Type': 'text/plain'}

    @app.get('/')
    def index():
        if not g.luisa_session or g.luisa_session['role'] not in {'student', 'staff'} or g.luisa_session['must_change']:
            return redirect(url_for('login'))
        return course_page(build_dir / 'index.html')

    def course_page(target):
        page = target.read_text(encoding='utf-8')
        identity = g.luisa_session['school_number'] or g.luisa_session['staff_username']
        return page.replace('<!--luisa-account-name-->', escape(identity) + ' · ')

    @app.get('/<path:asset>')
    def private_asset(asset: str):
        if not g.luisa_session or g.luisa_session['role'] not in {'student', 'staff'} or g.luisa_session['must_change']:
            return redirect(url_for('login'))
        if asset == 'index.html':
            return index()
        if asset not in asset_paths:
            abort(404)
        target = (build_dir / asset).resolve()
        if not target.is_relative_to(build_dir) or not target.is_file():
            abort(404)
        if target.suffix.lower() == '.html':
            return course_page(target)
        if target.suffix.lower() == '.pdf' and request.headers.get('Sec-Fetch-Dest') == 'document' and 'download' not in request.args:
            return render_template_string(PDF_PAGE, title=target.stem, file=url_for('private_asset', asset=asset))
        return send_from_directory(str(build_dir), asset, conditional=False, etag=False, max_age=0,
                                   as_attachment=target.suffix.lower() == '.pdf' and 'download' in request.args)

    return app


def backup_database(source: str | Path, destination: str | Path, public_root: str | Path,
                    source_root: str | Path | None = None) -> None:
    """Create a consistent SQLite backup outside the public artifact tree."""
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    public_root = Path(public_root).resolve()
    source_root = Path(source_root or Path(__file__).resolve().parents[1]).resolve()
    if (source == destination or source.is_relative_to(public_root) or destination.is_relative_to(public_root)
            or source.is_relative_to(source_root) or destination.is_relative_to(source_root)):
        raise ValueError('Database and backup must both remain outside public and source trees')
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    src = sqlite3.connect(str(source))
    dst = sqlite3.connect(str(destination))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    os.chmod(destination, 0o600)
