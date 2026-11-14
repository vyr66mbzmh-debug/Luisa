import json
from contextlib import closing
import re
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from argon2 import PasswordHasher
import pyotp
from werkzeug.test import Client
from werkzeug.wrappers import Response

from student_server.app import LoginLimiter, backup_database, create_app
from student_server.middleware import PrefixMiddleware


class StudentAuthAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.build = self.root / 'public-student'
        self.build.mkdir()
        (self.build / 'build-manifest.json').write_text(json.dumps({'edition': 'student', 'files': {
            'index.html': {}, 'content/questions.json': {}, 'assets/question.png': {},
            'question-bundle.js': {}, 'resources/printouts/sample.pdf': {}, 'sw.js': {}
        }}))
        (self.build / 'index.html').write_text('<h1>Student content</h1>')
        (self.build / 'content').mkdir()
        (self.build / 'content/questions.json').write_text('{"question":"private question"}')
        (self.build / 'assets').mkdir()
        (self.build / 'assets/question.png').write_bytes(b'private image bytes')
        (self.build / 'question-bundle.js').write_text('const question="private question";')
        (self.build / 'resources/printouts').mkdir(parents=True)
        (self.build / 'resources/printouts/sample.pdf').write_bytes(b'%PDF-private')
        (self.build / 'sw.js').write_text("self.addEventListener('activate',e=>e.waitUntil(self.registration.unregister()));")
        self.db_path = self.root / 'private-data' / 'accounts.sqlite'
        self.totp_secret = pyotp.random_base32()
        self.teacher_password = 'A-long-teacher-password-3029!'
        self.app = create_app({
            'TESTING': True,
            'STUDENT_BUILD_DIR': str(self.build),
            'DATABASE_PATH': str(self.db_path),
            'ADMIN_PASSWORD_HASH': PasswordHasher().hash(self.teacher_password),
            'ADMIN_TOTP_SECRET': self.totp_secret,
            'SCHOOL_YEAR': '2026-27',
        })
        self.app.extensions['luisa_init_db']()
        self.client = self.app.test_client()
        self.admin = self.app.test_client()
        self.admin_totp_code = None
        self.sign_in_admin()

    def tearDown(self):
        self.temp.cleanup()

    def csrf(self, response):
        match = re.search(r'name=_csrf value=["\']([^"\']+)', response.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def post_form(self, client, path, values, csrf_response=None):
        values = dict(values)
        if path == "/admin/login":
            values.setdefault("username", "admin")
        if csrf_response is None:
            page = '/admin' if path.startswith('/admin/') else ('/change-password' if path in {'/change-password', '/logout'} else '/login')
            csrf_response = client.get(page, base_url='https://ada.test')
        values['_csrf'] = self.csrf(csrf_response)
        return client.post(path, data=values, base_url='https://ada.test')

    def sign_in_admin(self):
        page = self.admin.get('/admin/login', base_url='https://ada.test')
        self.admin_totp_code = pyotp.TOTP(self.totp_secret).now()
        response = self.post_form(self.admin, '/admin/login', {
            'password': self.teacher_password, 'totp': self.admin_totp_code
        }, page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.admin.get('/admin', base_url='https://ada.test').status_code, 200)

    def add(self, numbers):
        return self.post_form(self.admin, '/admin/roster', {'numbers': numbers})

    def action(self, number, action, **fields):
        return self.post_form(self.admin, '/admin/account', {
            'school_number': number, 'action': action, **fields
        })

    def student_login(self, email, password):
        page = self.client.get('/login', base_url='https://ada.test')
        return self.post_form(self.client, '/login', {'email': email, 'password': password}, page)

    def database_account(self, number):
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute('SELECT * FROM accounts WHERE school_number=?', (number,)).fetchone()

    def change_password(self, client, password):
        page = client.get('/change-password', base_url='https://ada.test')
        return self.post_form(client, '/change-password', {'password': password, 'confirm': password}, page)

    def test_single_teacher_can_sign_in_with_only_the_password(self):
        config = dict(self.app.config, ADMIN_AUTH_MODE='password', ADMIN_TOTP_SECRET='')
        client = create_app(config).test_client()
        page = client.get('/admin/login', base_url='https://ada.test')
        self.assertNotIn('name=totp', page.get_data(as_text=True))
        failed = self.post_form(client, '/admin/login', {'password': 'incorrect'}, page)
        self.assertEqual(failed.status_code, 401)
        self.assertEqual(client.get('/admin', base_url='https://ada.test').status_code, 302)
        signed_in = self.post_form(client, '/admin/login', {'password': self.teacher_password}, failed)
        self.assertEqual(signed_in.status_code, 302)
        self.assertEqual(client.get('/admin', base_url='https://ada.test').status_code, 200)

    def test_teacher_password_change_persists_and_revokes_other_admin_sessions(self):
        config = dict(self.app.config, ADMIN_AUTH_MODE='password')
        app = create_app(config)
        client = app.test_client()
        def login(client, password):
            page = client.get('/admin/login', base_url='https://ada.test')
            return self.post_form(client, '/admin/login', {'password': password}, page)
        self.assertEqual(login(client, self.teacher_password).status_code, 302)
        new = 'My separately chosen teacher passphrase'
        form = {'current': self.teacher_password, 'password': new, 'confirm': new}
        self.assertEqual(self.post_form(client, '/admin/password', dict(form, current='invalid')).status_code, 400)
        self.assertEqual(self.post_form(client, '/admin/password', dict(form, confirm='different')).status_code, 400)
        self.assertEqual(client.post('/admin/password', data=form, base_url='https://ada.test').status_code, 400)
        self.assertEqual(self.post_form(client, '/admin/password', form).status_code, 302)
        self.assertEqual(client.get('/admin', base_url='https://ada.test').status_code, 200)
        self.assertEqual(self.admin.get('/admin', base_url='https://ada.test').status_code, 302)
        restarted = create_app(config)
        restarted.extensions['luisa_init_db']()
        fresh = restarted.test_client()
        self.assertEqual(login(fresh, self.teacher_password).status_code, 401)
        self.assertEqual(login(fresh, new).status_code, 302)

    def test_print_class_slips_once_and_consume_at_first_login(self):
        self.post_form(self.admin, '/admin/roster', {'numbers': '02340 02341', 'class_code': 'A'})
        self.post_form(self.admin, '/admin/roster', {'numbers': '09999', 'class_code': 'B'})
        slips = self.post_form(self.admin, '/admin/slips', {'class_code': 'A'})
        sheet = slips.get_data(as_text=True)
        self.assertNotIn('09999', sheet)
        passwords = re.findall(r'<code>([^<]+)</code>', sheet)
        self.assertEqual(len(set(passwords)), 2)
        self.assertIn('no-store', slips.headers['Cache-Control'])
        again = self.post_form(self.admin, '/admin/slips', {'class_code': 'A'})
        self.assertNotIn('<code>', again.get_data(as_text=True))
        self.assertIsNone(self.database_account('02340')['temporary_expires_utc'])
        self.assertEqual(self.student_login('02340@marlboroughcollege.org', passwords[0]).status_code, 302)
        self.assertEqual(self.student_login('02340@marlboroughcollege.org', passwords[0]).status_code, 401)
        self.assertEqual(self.post_form(self.admin, '/admin/slips', {}).get_data(as_text=True).count('<article>'), 1)

    def test_admin_setup_requires_bootstrap_and_own_password(self):
        app = create_app(dict(self.app.config, ADMIN_AUTH_MODE='password', TEACHER_SETUP=True))
        client = app.test_client()
        page = client.get('/admin/login', base_url='https://ada.test')
        login = self.post_form(client, '/admin/login', {'password': self.teacher_password}, page)
        self.assertTrue(login.location.endswith('/admin/password'))
        self.assertTrue(client.get('/admin', base_url='https://ada.test').location.endswith('/admin/password'))
        form = {'current': self.teacher_password, 'password': 'Private replacement phrase!', 'confirm': 'Private replacement phrase!'}
        self.post_form(client, '/admin/password', form, client.get('/admin/password', base_url='https://ada.test'))
        self.assertEqual(client.get('/admin', base_url='https://ada.test').status_code, 200)

    def test_roster_leading_zero_duplicates_and_mfa_admin(self):
        self.add('02340\n23401')
        invalid_batch = self.add('02401\nAlice Example')
        self.assertNotIn('Alice Example', invalid_batch.get_data(as_text=True))
        self.assertIsNotNone(self.database_account('02401'))
        self.assertIsNone(self.database_account('Alice'))
        account = self.database_account('02340')
        self.assertIsNotNone(account)
        self.assertEqual(len(account['school_number']), 5)
        temp = 'Unique-temp-pass-482!'
        self.action('02340', 'reset', chosen_password=temp, hours='24')
        before = self.database_account('02340')['temporary_hash']
        self.add('02340, 23401, 23401')
        self.assertEqual(self.database_account('02340')['temporary_hash'], before)
        self.assertEqual(self.database_account('02340')['active'], 1)
        reused = self.action('23401', 'reset', chosen_password=temp, hours='24')
        self.assertEqual(reused.status_code, 400)
        generated = self.action('23401', 'reset', hours='24')
        self.assertEqual(generated.status_code, 200)
        self.assertRegex(generated.get_data(as_text=True), r'Give this temporary password to pupil 23401')
        # Teacher access requires both password and current TOTP.
        fresh = self.app.test_client()
        page = fresh.get('/admin/login', base_url='https://ada.test')
        failed = self.post_form(fresh, '/admin/login', {'password': self.teacher_password, 'totp': '000000'}, page)
        self.assertEqual(failed.status_code, 401)
        replay_client = self.app.test_client()
        replay_page = replay_client.get('/admin/login', base_url='https://ada.test')
        replay = self.post_form(replay_client, '/admin/login', {
            'password': self.teacher_password, 'totp': self.admin_totp_code
        }, replay_page)
        self.assertEqual(replay.status_code, 401)

    def test_exact_email_validation_temporary_use_force_change_and_content_gate(self):
        self.add('02340')
        temp_password = 'Unique-temp-pass-482!'
        self.action('02340', 'reset', chosen_password=temp_password, hours='24')
        for email in ('99999@marlboroughcollege.org', '02340@marlboroughcollege.org.evil', '٠2340@marlboroughcollege.org'):
            response = self.student_login(email, temp_password)
            self.assertEqual(response.status_code, 401, email)
        response = self.student_login('02340@MarlboroughCollege.org', temp_password)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/change-password', response.location)
        self.assertEqual(self.change_password(self.client, temp_password).status_code, 400)
        sign_in_before_password_change = self.database_account('02340')['last_sign_in_utc']
        self.assertIsNotNone(sign_in_before_password_change)
        pending = self.client.get('/content/questions.json', base_url='https://ada.test')
        self.assertEqual(pending.status_code, 302)
        self.assertNotIn('private question', pending.get_data(as_text=True))
        response = self.change_password(self.client, 'New-student-password-998!')
        self.assertEqual(response.status_code, 302)
        account = self.database_account('02340')
        first_sign_in = account['last_sign_in_utc']
        self.assertEqual(first_sign_in, sign_in_before_password_change)
        self.assertTrue(first_sign_in.endswith('Z'))
        protected = self.client.get('/content/questions.json', base_url='https://ada.test')
        self.assertEqual(protected.status_code, 200)
        self.assertIn('private question', protected.get_data(as_text=True))
        self.assertIn('no-store', protected.headers['Cache-Control'])
        self.assertIn('Secure', protected.headers.get('Set-Cookie', ''))
        self.assertIn('HttpOnly', protected.headers.get('Set-Cookie', ''))
        protected.close()
        password_hash = self.database_account('02340')['password_hash']
        self.add('02340\n02340')
        self.assertEqual(self.database_account('02340')['password_hash'], password_hash)
        self.assertEqual(self.database_account('02340')['last_sign_in_utc'], first_sign_in)
        renewed_after_roster = self.client.get('/content/questions.json', base_url='https://ada.test')
        self.assertEqual(renewed_after_roster.status_code, 200)
        renewed_after_roster.get_data(); renewed_after_roster.close()
        self.assertEqual(self.database_account('02340')['last_sign_in_utc'], first_sign_in)
        self.assertEqual(self.client.get('/admin', base_url='https://ada.test').status_code, 403)
        shown = self.admin.get('/admin', base_url='https://ada.test').get_data(as_text=True)
        expected_uk_time = datetime.fromisoformat(first_sign_in.replace('Z', '+00:00')).astimezone(ZoneInfo('Europe/London')).strftime('%d %B %Y, %H:%M %Z')
        self.assertIn(expected_uk_time, shown)
        # The consumed temporary credential cannot be replayed.
        failed = self.student_login('02340@marlboroughcollege.org', temp_password)
        self.assertEqual(failed.status_code, 401)
        self.assertEqual(self.database_account('02340')['last_sign_in_utc'], first_sign_in)
        # Failed attempts and session renewals do not update last sign-in; a later successful login does.
        failed = self.student_login('02340@marlboroughcollege.org', 'wrong-password-for-this-account')
        self.assertEqual(failed.status_code, 401)
        renewed = self.client.get('/content/questions.json', base_url='https://ada.test')
        renewed.get_data(); renewed.close()
        self.assertEqual(self.database_account('02340')['last_sign_in_utc'], first_sign_in)
        self.client.post('/logout', data={'_csrf': self.csrf(self.client.get('/change-password', base_url='https://ada.test'))}, base_url='https://ada.test')
        time.sleep(1.05)
        second = self.student_login('02340@marlboroughcollege.org', 'New-student-password-998!')
        self.assertEqual(second.status_code, 302)
        self.assertNotEqual(self.database_account('02340')['last_sign_in_utc'], first_sign_in)
        page = self.client.get('/change-password', base_url='https://ada.test')
        logged_out = self.client.post('/logout', data={'_csrf': self.csrf(page)}, base_url='https://ada.test')
        self.assertEqual(logged_out.status_code, 302)
        self.assertEqual(self.client.get('/content/questions.json', base_url='https://ada.test').status_code, 302)

    def test_expiry_reset_suspension_force_change_and_reactivation(self):
        self.add('23401')
        first_temp = 'First-temp-password-998!'
        self.action('23401', 'reset', chosen_password=first_temp, hours='24')
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute("UPDATE accounts SET temporary_expires_utc='2000-01-01T00:00:00Z' WHERE school_number='23401'")
            conn.commit()
        self.assertEqual(self.student_login('23401@marlboroughcollege.org', first_temp).status_code, 401)
        new_temp = 'Second-temp-password-119!'
        reset = self.action('23401', 'reset', chosen_password=new_temp, hours='1')
        self.assertIn(new_temp, reset.get_data(as_text=True))
        self.assertEqual(self.student_login('23401@marlboroughcollege.org', new_temp).status_code, 302)
        self.change_password(self.client, 'Student-password-2000!')
        content = self.client.get('/content/questions.json', base_url='https://ada.test')
        self.assertEqual(content.status_code, 200)
        content.get_data(); content.close()
        replacement_temp = 'Replacement-temp-4200!'
        self.action('23401', 'reset', chosen_password=replacement_temp, hours='24')
        self.assertEqual(self.client.get('/content/questions.json', base_url='https://ada.test').status_code, 302)
        self.assertEqual(self.student_login('23401@marlboroughcollege.org', 'Student-password-2000!').status_code, 401)
        self.assertEqual(self.student_login('23401@marlboroughcollege.org', new_temp).status_code, 401)
        self.assertIn('/change-password', self.student_login('23401@marlboroughcollege.org', replacement_temp).location)
        self.change_password(self.client, 'Student-password-2001!')
        self.action('23401', 'force')
        self.assertEqual(self.client.get('/content/questions.json', base_url='https://ada.test').status_code, 302)
        forced = self.student_login('23401@marlboroughcollege.org', 'Student-password-2001!')
        self.assertIn('/change-password', forced.location)
        self.assertEqual(self.client.get('/resources/printouts/sample.pdf', base_url='https://ada.test').status_code, 302)
        self.action('23401', 'suspend')
        self.assertEqual(self.student_login('23401@marlboroughcollege.org', 'Student-password-2001!').status_code, 401)
        self.action('23401', 'reactivate')
        self.assertEqual(self.student_login('23401@marlboroughcollege.org', 'Student-password-2001!').status_code, 302)
        self.assertIn('/change-password', self.client.get('/resources/printouts/sample.pdf', base_url='https://ada.test').location)

    def test_never_signed_in_cohort_uk_time_and_private_schema(self):
        self.add('23401\n22999')
        page = self.admin.get('/admin', base_url='https://ada.test').get_data(as_text=True)
        self.assertIn('Never signed in', page)
        self.assertIn('Lower Sixth', page)
        self.assertIn('Upper Sixth', page)
        with closing(sqlite3.connect(self.db_path)) as conn:
            columns = {row[1] for row in conn.execute('PRAGMA table_info(accounts)')}
            self.assertTrue({'school_number', 'last_sign_in_utc', 'password_hash'} <= columns)
            self.assertFalse({'first_name', 'surname', 'date_of_birth', 'ip_address', 'login_count'} & columns)
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertFalse({'login_history', 'activity', 'analytics'} & tables)

    def test_direct_assets_are_gated_and_backup_can_be_recovered(self):
        self.add('02340')
        source_root = Path(__file__).resolve().parents[1]
        with self.assertRaises(RuntimeError):
            create_app({
                'STUDENT_BUILD_DIR': str(self.build), 'DATABASE_PATH': str(source_root / 'must-not-be-created.sqlite'),
                'ADMIN_PASSWORD_HASH': PasswordHasher().hash(self.teacher_password), 'ADMIN_TOTP_SECRET': self.totp_secret,
            })
        unauth_admin = self.app.test_client().get('/admin', base_url='https://ada.test')
        self.assertIn('/admin/login', unauth_admin.location)
        for path in ('/', '/content/questions.json', '/assets/question.png', '/question-bundle.js',
                     '/resources/printouts/sample.pdf', '/build-manifest.json', '/admin/account'):
            response = self.client.get(path, base_url='https://ada.test')
            self.assertEqual(response.status_code, 302, path)
            self.assertNotIn('private question', response.get_data(as_text=True))
        self.action('02340', 'reset', chosen_password='Unique-temp-pass-482!', hours='24')
        backup = self.root / 'private-backups' / 'accounts-copy.sqlite'
        backup_database(self.db_path, backup, self.build)
        with closing(sqlite3.connect(backup)) as conn:
            self.assertEqual(conn.execute('SELECT school_number FROM accounts').fetchone()[0], '02340')
        restored = self.root / 'restored-private-data' / 'accounts.sqlite'
        restored.parent.mkdir(mode=0o700)
        restored.write_bytes(backup.read_bytes())
        restored_app = create_app({
            'TESTING': True, 'STUDENT_BUILD_DIR': str(self.build), 'DATABASE_PATH': str(restored),
            'ADMIN_PASSWORD_HASH': PasswordHasher().hash(self.teacher_password), 'ADMIN_TOTP_SECRET': self.totp_secret,
        })
        restored_app.extensions['luisa_init_db']()
        restored_admin = restored_app.test_client()
        page = restored_admin.get('/admin/login', base_url='https://ada.test')
        future_step = time.time() + 60
        values = {'username': 'admin', 'password': self.teacher_password, 'totp': pyotp.TOTP(self.totp_secret).at(future_step), '_csrf': self.csrf(page)}
        with patch('student_server.app.time.time', return_value=future_step):
            restored_response = restored_admin.post('/admin/login', data=values, base_url='https://ada.test')
        self.assertEqual(restored_response.status_code, 302)
        self.assertIn('02340', restored_admin.get('/admin', base_url='https://ada.test').get_data(as_text=True))
        self.action('02340', 'reset', chosen_password='Printed-content-temp-420!', hours='24')
        self.student_login('02340@marlboroughcollege.org', 'Printed-content-temp-420!')
        self.change_password(self.client, 'Printed-content-student-421!')
        printable = self.client.get('/resources/printouts/sample.pdf', base_url='https://ada.test')
        self.assertEqual(printable.status_code, 200)
        self.assertEqual(printable.headers['Content-Type'], 'application/pdf')
        self.assertIn('no-store', printable.headers['Cache-Control'])
        printable.close()
        self.assertEqual(self.client.get('/resources/pure-year-1/chapters/chapter-01.pdf', base_url='https://ada.test').status_code, 404)
        with self.assertRaises(ValueError):
            backup_database(self.db_path, self.build / 'leak.sqlite', self.build)

    def test_login_limiter_is_ephemeral_security_state(self):
        limiter = LoginLimiter(limit=2, window_seconds=60)
        self.assertTrue(limiter.allowed('opaque-identifier-digest'))
        limiter.failed('opaque-identifier-digest')
        limiter.failed('opaque-identifier-digest')
        self.assertFalse(limiter.allowed('opaque-identifier-digest'))
        limiter.succeeded('opaque-identifier-digest')
        self.assertTrue(limiter.allowed('opaque-identifier-digest'))

    def test_server_sessions_have_idle_and_absolute_expiry(self):
        self.add('23401')
        self.action('23401', 'reset', chosen_password='Session-temp-password-902!', hours='24')
        self.student_login('23401@marlboroughcollege.org', 'Session-temp-password-902!')
        self.change_password(self.client, 'Session-student-password-903!')
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute("UPDATE sessions SET created_utc='2000-01-01T00:00:00Z' WHERE school_number='23401'")
            conn.commit()
        expired = self.client.get('/content/questions.json', base_url='https://ada.test')
        self.assertEqual(expired.status_code, 302)
        self.assertEqual(expired.headers['Location'], '/login')

    def test_gateway_mounts_below_ada_al_prefix_and_rejects_other_paths(self):
        prefixed_app = create_app({
            'TESTING': True, 'STUDENT_BUILD_DIR': str(self.build),
            'DATABASE_PATH': str(self.root / 'prefix-private' / 'accounts.sqlite'),
            'ADMIN_PASSWORD_HASH': PasswordHasher().hash(self.teacher_password),
            'ADMIN_TOTP_SECRET': self.totp_secret, 'SESSION_COOKIE_PATH': '/AL',
        })
        prefixed_app.extensions['luisa_init_db']()
        client = Client(PrefixMiddleware(prefixed_app.wsgi_app, '/AL'), Response)
        page = client.get('/AL/login', base_url='https://ada.test')
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.headers.get('Cache-Control'), 'private, no-store, max-age=0')
        self.assertIn('Path=/AL;', page.headers.get('Set-Cookie', ''))
        self.assertIn('Strict-Transport-Security', page.headers)
        denied = client.get('/AL/content/questions.json', base_url='https://ada.test')
        self.assertEqual(denied.status_code, 302)
        self.assertEqual(denied.headers['Location'], '/AL/login')
        self.assertEqual(client.get('/content/questions.json', base_url='https://ada.test').status_code, 404)


if __name__ == '__main__':
    unittest.main()
