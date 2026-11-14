"""ADA student content gateway. All durable state is private SQLite data."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
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

LOGIN_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Luisa sign in</title><style>body{font:17px system-ui;max-width:32rem;margin:8vh auto;padding:1.5rem;color:#183957}label,input,button{display:block;width:100%;box-sizing:border-box;margin:.5rem 0 1rem}input,button{font:inherit;padding:.7rem}button{background:#183957;color:white;border:0;border-radius:.3rem}.error{color:#8b2020}</style><h1>Luisa sign in</h1>{% if error %}<p class=error role=alert>{{ error }}</p>{% endif %}<form method=post><input type=hidden name=_csrf value='{{ csrf }}'><label>School email<input name=email type=email autocomplete=username required maxlength=64></label><label>Luisa password<input name=password type=password autocomplete=current-password required maxlength=1024></label><button>Sign in</button></form></html>"""
ADMIN_LOGIN_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Luisa administration sign in</title><style>body{font:17px system-ui;max-width:32rem;margin:8vh auto;padding:1.5rem;color:#183957}label,input,button{display:block;width:100%;box-sizing:border-box;margin:.5rem 0 1rem}input,button{font:inherit;padding:.7rem}button{background:#183957;color:white;border:0;border-radius:.3rem}.error{color:#8b2020}</style><h1>Teacher sign in</h1>{% if error %}<p class=error role=alert>{{ error }}</p>{% endif %}<form method=post><input type=hidden name=_csrf value='{{ csrf }}'><label>Teacher password<input name=password type=password autocomplete=current-password required maxlength=1024></label><label>Authenticator code<input name=totp inputmode=numeric autocomplete=one-time-code required pattern='[0-9]{6}'></label><button>Sign in</button></form></html>"""
CHANGE_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Change Luisa password</title><style>body{font:17px system-ui;max-width:32rem;margin:8vh auto;padding:1.5rem;color:#183957}label,input,button{display:block;width:100%;box-sizing:border-box;margin:.5rem 0 1rem}input,button{font:inherit;padding:.7rem}button{background:#183957;color:white;border:0;border-radius:.3rem}.error{color:#8b2020}</style><h1>Choose a new Luisa password</h1><p>Change your temporary password before opening course content.</p>{% if error %}<p class=error role=alert>{{ error }}</p>{% endif %}<form method=post><input type=hidden name=_csrf value='{{ csrf }}'><label>New password<input name=password type=password autocomplete=new-password required minlength=12 maxlength=1024></label><label>Repeat new password<input name=confirm type=password autocomplete=new-password required minlength=12 maxlength=1024></label><button>Save password</button></form></html>"""
ADMIN_PAGE = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Luisa account administration</title><style>body{font:16px/1.5 system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#183957}table{border-collapse:collapse;width:100%;margin:1.5rem 0}td,th{border:1px solid #ccd5df;padding:.5rem;text-align:left}button,input,textarea{font:inherit;padding:.45rem;margin:.2rem}form{display:inline}section{padding:1rem;border:1px solid #ccd5df;margin:1rem 0}.notice{background:#edf5fb;padding:.8rem}.secret{font:1.15rem monospace;overflow-wrap:anywhere}small{color:#526575}</style><h1>Luisa student accounts</h1><p><a href='{{ url_for("logout") }}' onclick="event.preventDefault();document.getElementById('logout').submit()">Sign out</a><form id=logout method=post action='{{ url_for("logout") }}'><input type=hidden name=_csrf value='{{ csrf }}'></form></p>{% if notice %}<p class=notice role=status>{{ notice }}</p>{% endif %}{% if temp_password %}<section><b>Give this temporary password to pupil {{ temp_school_number }} privately. It expires in {{ temp_hours }} hour(s) and can be used once.</b><p class=secret>{{ temp_password }}</p></section>{% endif %}<section><h2>Add school numbers</h2><form method=post action='{{ url_for("add_roster") }}'><input type=hidden name=_csrf value='{{ csrf }}'><label>One per line; leading zeroes are preserved<br><textarea name=numbers rows=5 cols=24 required></textarea></label><button>Add roster entries</button></form></section><table><thead><tr><th>School number</th><th>Cohort</th><th>Access</th><th>Latest successful sign-in</th><th>Account controls</th></tr></thead><tbody>{% for row in rows %}<tr><td>{{ row.number }}</td><td>{{ row.cohort }}</td><td>{{ 'Active' if row.active else 'Suspended' }}{% if row.force_change %} · password change required{% endif %}</td><td>{{ row.last_sign_in }}</td><td><form method=post action='{{ url_for("account_action") }}'><input type=hidden name=_csrf value='{{ csrf }}'><input type=hidden name=school_number value='{{ row.number }}'><select name=action><option value=reset>Issue temporary password</option><option value=force>Force password change</option><option value=suspend>Suspend</option><option value=reactivate>Reactivate</option><option value=revoke>Revoke sessions</option></select><label>Optional temporary password <input name=chosen_password type=password minlength=12 maxlength=128 autocomplete=off></label><label>Expiry hours <input name=hours type=number min=1 max=24 value=24></label><button>Apply</button></form></td></tr>{% endfor %}</tbody></table><p><small>Only the latest successful student sign-in is displayed. UK local time. Student names and dates of birth are not collected.</small></p></html>"""


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
    if not app.config['ADMIN_PASSWORD_HASH'] or not app.config['ADMIN_TOTP_SECRET']:
        raise RuntimeError('Teacher password hash and MFA secret must be configured before startup')
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
                CREATE TABLE IF NOT EXISTS admin_mfa_state (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    last_accepted_step INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO admin_mfa_state(singleton,last_accepted_step) VALUES(1,-1);
            ''')
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

    def new_session(role: str, school_number: str | None = None, must_change: bool = False):
        token = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        created = utc_now()
        expiry = utc_text(created + timedelta(seconds=app.config['SESSION_SECONDS']))
        db().execute('INSERT INTO sessions(session_hash,school_number,role,must_change,csrf_token,created_utc,expires_utc) VALUES(?,?,?,?,?,?,?)',
                     (digest_session(token), school_number, role, int(must_change), csrf, utc_text(created), expiry))
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
                if row['role'] == 'student':
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
        if endpoint in {'change_password', 'change_password_post'} and g.luisa_session and g.luisa_session['role'] == 'student':
            return None
        if g.luisa_session and g.luisa_session['role'] == 'student' and g.luisa_session['must_change'] and endpoint not in {'change_password', 'change_password_post', 'logout'}:
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
        key = email_key(email.casefold(), rate_key)
        if not limiter.allowed(key):
            return render_login(LOGIN_PAGE, 'Sign-in failed. Check your details or contact your teacher.'), 429
        school_number = email[:5] if _SIGN_IN.fullmatch(email) else ''
        account = db().execute('SELECT * FROM accounts WHERE school_number=? AND active=1', (school_number,)).fetchone() if school_number else None
        temp_is_valid = bool(account and account['temporary_hash'] and account['temporary_expires_utc'] and account['temporary_expires_utc'] > utc_text())
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
            consumed = db().execute('UPDATE accounts SET temporary_expires_utc=NULL,force_change=1,last_sign_in_utc=? WHERE school_number=? AND active=1 AND temporary_hash=? AND temporary_expires_utc>?',
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
        pass_ok = password_ok(app.config['ADMIN_PASSWORD_HASH'], password) if len(password) <= 1024 else False
        totp_ok = consume_admin_totp(code)
        if not (pass_ok and totp_ok):
            limiter.failed(key)
            return render_login(ADMIN_LOGIN_PAGE, 'Sign-in failed.'), 401
        limiter.succeeded(key)
        token = new_session('admin')
        g.luisa_session = {'csrf_token': '', 'must_change': 0}
        response = redirect(url_for('admin_home'))
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
        g.luisa_session = None
        response = redirect(url_for('login'))
        response.delete_cookie(app.config['SESSION_COOKIE'], path=app.config['SESSION_COOKIE_PATH'], secure=True, httponly=True, samesite='Lax')
        return response

    @app.get('/change-password')
    def change_password():
        if not g.luisa_session or g.luisa_session['role'] != 'student':
            return redirect(url_for('login'))
        return render_template_string(CHANGE_PAGE, csrf=base_context(), error=None)

    @app.post('/change-password')
    def change_password_post():
        require_csrf()
        if not g.luisa_session or g.luisa_session['role'] != 'student' or not g.luisa_session['must_change']:
            abort(403)
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if len(password) < 12 or len(password) > 1024 or password != confirm:
            return render_template_string(CHANGE_PAGE, csrf=base_context(), error='Use at least 12 characters and enter the same password twice.'), 400
        number = g.luisa_session['school_number']
        if password in {number, number + '@marlboroughcollege.org'}:
            return render_template_string(CHANGE_PAGE, csrf=base_context(), error='Choose a password independent of your school number and email.'), 400
        old = db().execute('SELECT password_hash,temporary_hash FROM accounts WHERE school_number=? AND active=1', (number,)).fetchone()
        if old is None:
            abort(403)
        if any(password_ok(value, password) for value in old if value):
            return render_template_string(CHANGE_PAGE, csrf=base_context(), error='Choose a different Luisa password.'), 400
        new_hash = _PH.hash(password)
        db().execute('BEGIN IMMEDIATE')
        if not db().execute('SELECT 1 FROM sessions WHERE session_hash=? AND must_change=1', (g.luisa_session['session_hash'],)).fetchone():
            db().execute('ROLLBACK')
            abort(403)
        changed = db().execute('UPDATE accounts SET password_hash=?,force_change=0,temporary_hash=NULL,temporary_expires_utc=NULL WHERE school_number=? AND active=1', (new_hash, number))
        if changed.rowcount != 1:
            abort(403)
        db().execute('DELETE FROM sessions WHERE school_number=?', (number,))
        token = new_session('student', number, False)
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

    def temporary_password(number: str, chosen: str, hours: int):
        candidate = chosen or secrets.token_urlsafe(18)
        if len(candidate) < 12 or len(candidate) > 128:
            raise ValueError('Temporary passwords must be 12 to 128 characters.')
        if candidate in {number, number + '@marlboroughcollege.org'}:
            raise ValueError('Temporary passwords must be independent of the school number and email.')
        candidate_hash = _PH.hash(candidate)
        now = utc_text()
        db().execute('BEGIN IMMEDIATE')
        try:
            db().execute('UPDATE accounts SET temporary_hash=NULL,temporary_expires_utc=NULL WHERE temporary_expires_utc IS NOT NULL AND temporary_expires_utc<=?', (now,))
            other_hashes = db().execute('SELECT temporary_hash FROM accounts WHERE school_number<>? AND active=1 AND temporary_hash IS NOT NULL AND temporary_expires_utc>?', (number, now)).fetchall()
            if any(password_ok(row['temporary_hash'], candidate) for row in other_hashes):
                raise ValueError('That password is already active for another pupil. Choose or generate another.')
            db().execute('UPDATE accounts SET password_hash=NULL,force_change=1,temporary_hash=?,temporary_expires_utc=? WHERE school_number=?',
                         (candidate_hash, utc_text(utc_now() + timedelta(hours=hours)), number))
            db().execute('DELETE FROM sessions WHERE school_number=?', (number,))
            db().execute('COMMIT')
        except Exception:
            db().execute('ROLLBACK')
            raise
        return candidate

    def render_admin(notice=None, temp_password=None, temp_school_number=None, temp_hours=None, status=200):
        rows = []
        labels = {'2026-27': {'23': 'Lower Sixth', '22': 'Upper Sixth'}}
        mapping = labels.get(app.config['SCHOOL_YEAR'], {})
        for account in db().execute('SELECT * FROM accounts ORDER BY school_number'):
            sign_in = 'Never signed in'
            if account['last_sign_in_utc']:
                value = datetime.fromisoformat(account['last_sign_in_utc'].replace('Z', '+00:00')).astimezone(_UK)
                sign_in = value.strftime('%d %B %Y, %H:%M %Z')
            rows.append({'number': account['school_number'], 'cohort': mapping.get(account['school_number'][:2], '—'),
                         'active': bool(account['active']), 'force_change': bool(account['force_change']), 'last_sign_in': sign_in})
        return render_template_string(ADMIN_PAGE, rows=rows, csrf=base_context(), notice=notice,
                                      temp_password=temp_password, temp_school_number=temp_school_number,
                                      temp_hours=temp_hours), status

    @app.get('/admin')
    @admin_only
    def admin_home():
        return render_admin()

    @app.post('/admin/roster')
    @admin_only
    def add_roster():
        require_csrf()
        raw = request.form.get('numbers', '')
        candidates = [piece for piece in re.split(r'[\s,;]+', raw.strip()) if piece]
        invalid = False
        db().execute('BEGIN IMMEDIATE')
        for candidate in candidates:
            if not _SCHOOL_NUMBER.fullmatch(candidate):
                invalid = True
                continue
            db().execute('INSERT OR IGNORE INTO accounts(school_number,active) VALUES(?,1)', (candidate,))
        db().execute('COMMIT')
        return render_admin('Roster update complete. Check that every roster entry is exactly five ASCII digits.' if invalid else 'Roster update complete.')

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
                hours = int(request.form.get('hours', '24'))
            except ValueError:
                abort(400)
            if hours < 1 or hours > 24:
                abort(400)
            try:
                temp = temporary_password(number, chosen, hours)
            except ValueError as error:
                return render_admin(str(error), status=400)
            return render_admin('Temporary password issued. It will not be shown again after this response.', temp, number, hours)
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
        if not g.luisa_session or g.luisa_session['role'] != 'student' or g.luisa_session['must_change']:
            return redirect(url_for('login'))
        return send_from_directory(str(build_dir), 'index.html')

    @app.get('/<path:asset>')
    def private_asset(asset: str):
        if not g.luisa_session or g.luisa_session['role'] != 'student' or g.luisa_session['must_change']:
            return redirect(url_for('login'))
        if asset not in asset_paths:
            abort(404)
        target = (build_dir / asset).resolve()
        if not target.is_relative_to(build_dir) or not target.is_file():
            abort(404)
        return send_from_directory(str(build_dir), asset, conditional=False, etag=False, max_age=0)

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
