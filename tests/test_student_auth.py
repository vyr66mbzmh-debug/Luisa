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
            'question-bundle.js': {}, 'resources/printouts/sample.pdf': {}, 'sw.js': {},
            'teaching-lesson-viewer.html': {}
        }}))
        (self.build / 'index.html').write_text('<h1>Student content</h1>')
        (self.build / 'teaching-lesson-viewer.html').write_text('<main>Teaching slides</main>')
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

    def test_admin_can_sign_in_with_only_the_password(self):
        config = dict(self.app.config, ADMIN_AUTH_MODE='password', ADMIN_TOTP_SECRET='')
        client = create_app(config).test_client()
        page = client.get('/admin/login', base_url='https://ada.test')
        self.assertEqual(re.findall(r'<input\b[^>]*\bname=([^ >]+)', page.text), ['_csrf', 'password'])
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
        new = 'x' * 8
        form = {'current': self.teacher_password, 'password': new, 'confirm': new}
        short = new[:-1]
        self.assertEqual(self.post_form(client, '/admin/password', dict(form, password=short, confirm=short)).status_code, 400)
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
        self.assertIn('https://adazmq.marlboroughcollege.org/login', sheet)
        self.assertNotIn('https://ada.test/login', sheet)
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

    def test_licensed_chapters_are_selected_by_authenticated_role(self):
        staff_dir = self.root / 'staff-library'
        staff_dir.mkdir()
        chapter = 'chapter.pdf'
        catalogue = 'textbook-catalogue.json'
        (staff_dir / chapter).write_bytes(b'%PDF-licensed')
        for directory, edition in ((self.build, 'student'), (staff_dir, 'staff')):
            body = {'edition': edition}
            if edition == 'staff':
                body['chapter'] = chapter
            (directory / catalogue).write_text(json.dumps(body))
            (directory / 'index.html').write_text(edition + ' library')
            files = {'index.html': {}, catalogue: {}}
            if edition == 'staff':
                files[chapter] = {}
            (directory / 'build-manifest.json').write_text(json.dumps({
                'edition': edition, 'files': files, 'revision': 'sample-release', 'version': '1'
            }))
        app = create_app(dict(self.app.config, STAFF_BUILD_DIR=str(staff_dir)))
        staff, pupil, anon = (app.test_client() for _ in range(3))
        password = 'Sample-course-password'
        encoded = PasswordHasher().hash(password)
        self.add('02340')
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('UPDATE accounts SET password_hash=? WHERE school_number=?', (encoded, '02340'))
            conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)',
                         ('sample.teacher', encoded))
        host = 'https://ada.test'
        for device, identity in ((staff, 'sample.teacher'), (pupil, '02340@marlboroughcollege.org')):
            self.assertEqual(self.post_form(device, '/login', {'email': identity, 'password': password}).location, '/')
        self.assertEqual(staff.get('/', base_url=host).get_data(as_text=True), 'staff library')
        self.assertTrue(pupil.get('/', base_url=host).text.startswith('student library'))
        for device, allowed in ((staff, True), (pupil, False)):
            response = device.get('/' + catalogue, base_url=host)
            self.assertEqual('chapter' in response.get_json(), allowed)
            self.assertIn('no-store', response.headers['Cache-Control'])
            response.close()
        with staff.get('/' + chapter, base_url=host) as response:
            self.assertEqual(response.get_data(), b'%PDF-licensed')
            self.assertIn('no-store', response.headers['Cache-Control'])
        self.assertEqual(pupil.get('/' + chapter + '?role=staff', base_url=host).status_code, 404)
        self.assertEqual(anon.get('/' + chapter, base_url=host).location, '/login')

    def test_teacher_exam_paper_is_staff_only_and_denied_to_pupils_PAP_065(self):
        import importlib.util
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('luisa_build', root / 'scripts/luisa.py')
        luisa = importlib.util.module_from_spec(spec); spec.loader.exec_module(luisa)
        self.assertEqual(luisa.TEACHER_ONLY_FILES, {'papers-exam.js', 'papers-exam.css'})
        source = (root / 'papers.html').read_bytes()
        staff_dir = self.root / 'staff-library'
        staff_dir.mkdir()
        for directory, edition in ((self.build, 'student'), (staff_dir, 'staff')):
            page = luisa.student_content('papers.html', source, set(), set(), root, staff=edition == 'staff').decode()
            (directory / 'papers.html').write_text(page)
            files = {'papers.html': {}}
            if edition == 'staff':
                for name in luisa.TEACHER_ONLY_FILES:
                    (directory / name).write_bytes((root / name).read_bytes()); files[name] = {}
            (directory / 'build-manifest.json').write_text(json.dumps({'edition': edition, 'files': files, 'revision': 'sample-release', 'version': '1'}))
        pupil_page = (self.build / 'papers.html').read_text()
        staff_page = (staff_dir / 'papers.html').read_text()
        # The pupil edition carries no exam controls, script reference or marker.
        for marker in ('papers-exam', 'luisa-teacher-exam', 'Exam paper', 'Teachers only'):
            self.assertNotIn(marker, pupil_page)
        self.assertEqual(staff_page.count('<script defer src="papers-exam.js"></script>'), 1)
        for control in ('id="papers-exam"', 'id="papers-exam-print"', 'id="papers-exam-instructions"', 'id="papers-exam-minutes"', 'id="papers-exam-generate"', 'data-exam-preset="32"', 'data-exam-preset="60"'):
            self.assertIn(control, staff_page)
        # PAP-067-2: the mark scheme print choice is a staff control.
        for choice in ('value="questions"', 'value="scheme"', 'value="both"'):
            self.assertIn(f'name="papers-exam-content" {choice}', staff_page)
        self.assertNotIn('papers-exam-content', pupil_page)
        # PAP-066-3 and PAP-067-4/5: removed controls and helper texts stay gone.
        for removed in ('papers-exam-map', 'Regenerate course map', 'no solutions', 'is added automatically when any question comes from Mechanics'):
            self.assertNotIn(removed, staff_page)
        app = create_app(dict(self.app.config, STAFF_BUILD_DIR=str(staff_dir)))
        staff, pupil, anon = (app.test_client() for _ in range(3))
        password = 'Sample-course-password'
        encoded = PasswordHasher().hash(password)
        self.add('02341')
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('UPDATE accounts SET password_hash=? WHERE school_number=?', (encoded, '02341'))
            conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)', ('sample.teacher', encoded))
        host = 'https://ada.test'
        for device, identity in ((staff, 'sample.teacher'), (pupil, '02341@marlboroughcollege.org')):
            self.assertEqual(self.post_form(device, '/login', {'email': identity, 'password': password}).location, '/')
        for name in sorted(luisa.TEACHER_ONLY_FILES):
            with staff.get('/' + name, base_url=host) as response:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_data(), (root / name).read_bytes())
            self.assertEqual(pupil.get('/' + name, base_url=host).status_code, 404)
            self.assertEqual(pupil.get('/' + name + '?role=staff', base_url=host).status_code, 404)
            self.assertEqual(anon.get('/' + name, base_url=host).location, '/login')
        self.assertIn('id="papers-exam"', staff.get('/papers.html', base_url=host).get_data(as_text=True))
        self.assertNotIn('papers-exam', pupil.get('/papers.html', base_url=host).get_data(as_text=True))

    def test_private_preview_uses_only_its_bare_username_and_pupil_rights(self):
        self.add('00001')
        first = 'Private-first-secret'
        alias = 'test_example'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('INSERT INTO pupil_preview_logins VALUES(?,?)', ('00001', alias))
        slips = self.post_form(self.admin, '/admin/slips', {})
        self.assertNotIn('<article>', slips.text)
        self.action('00001', 'reset', chosen_password=first)
        for identifier in (alias, 'test_unknown'):
            response = self.student_login(identifier, 'incorrect password')
            self.assertEqual(response.status_code, 401)
            self.assertIn('Check your details or contact your teacher.', response.text)
        for invalid in ('00001@marlboroughcollege.org', alias+'@marlboroughcollege.org', alias+'@other.test'):
            self.assertEqual(self.student_login(invalid, first).status_code, 401)
        self.assertEqual(self.student_login(alias, first).location, '/change-password')
        self.assertEqual(self.client.get('/', base_url='https://ada.test').location, '/change-password')
        self.assertEqual(self.student_login(alias, first).status_code, 401)
        password = 'Preview-new-password'
        self.assertEqual(self.change_password(self.client, password).location, '/')
        (self.build/'index.html').write_text('<!--luisa-account-name-->')
        self.assertTrue(self.client.get('/', base_url='https://ada.test').text.startswith(alias))
        second = self.app.test_client()
        self.assertEqual(self.post_form(second, '/login', {'email':alias, 'password':password}).location, '/')
        self.assertEqual(self.client.get('/', base_url='https://ada.test').location, '/login')
        self.assertEqual(second.get('/admin', base_url='https://ada.test').status_code, 403)
        self.assertEqual(second.get('/staff-chapter.pdf', base_url='https://ada.test').status_code, 404)
        self.action('00001', 'suspend')
        self.assertEqual(second.get('/', base_url='https://ada.test').location, '/login')
        self.assertEqual(self.student_login(alias, password).status_code, 401)

    def test_admin_creates_teacher_and_records_only_successful_sign_in(self):
        host = 'https://ada.test'
        path = '/admin/teachers'
        self.assertEqual(self.admin.post(path, data={'acronym':'XY'}, base_url=host).status_code, 400)
        self.assertEqual(self.client.post(path, base_url=host).location, '/admin/login')
        for invalid in ('admin', '02340', 'staff@wrong.test', 'test_example'):
            self.assertEqual(self.post_form(self.admin, path, {'acronym':invalid}).status_code, 400)
        created = self.post_form(self.admin, path, {'acronym':'XY'})
        self.assertEqual(created.status_code, 200)
        secret = re.search(r'<code>([^<]+)</code>', created.text)[1]
        self.assertIn('Awaiting first sign-in', created.text)
        duplicate = self.post_form(self.admin, path, {'acronym':'xy'})
        self.assertEqual(duplicate.status_code, 409)
        self.assertNotIn(secret, duplicate.text)
        with closing(sqlite3.connect(self.db_path)) as conn:
            def stamp():
                return conn.execute("SELECT last_sign_in_utc FROM staff_accounts WHERE username='xy'").fetchone()[0]
            self.assertIsNone(stamp())
            self.assertEqual(self.student_login('XY', secret).location, '/change-password')
            first = stamp()
            self.assertTrue(first)
            self.assertEqual(self.change_password(self.client, 'A-second-secret').location, '/')
            self.assertEqual(self.client.post(path, base_url=host).status_code, 403)
            self.assertEqual(self.student_login('xy', secret).status_code, 401)
            self.client.get('/', base_url=host)
            self.assertEqual(stamp(), first)
            conn.execute("UPDATE staff_accounts SET last_sign_in_utc='2026-01-01T00:00:00Z' WHERE username='xy'")
            conn.commit()
            self.assertEqual(self.student_login('xy@marlboroughcollege.org', 'A-second-secret').location, '/')
            self.assertNotEqual(stamp(), '2026-01-01T00:00:00Z')
            self.assertNotIn(secret, self.admin.get('/admin', base_url=host).text)

    def test_directory_names_are_private_and_independent_of_login_state(self):
        host = 'https://ada.test'
        self.add('02342 02343')
        before = dict(self.database_account('02342'))
        endpoint = '/admin/students/name'
        fields = {'identifier': '02342', 'first_name': 'Fictional'}
        self.assertEqual(self.admin.post(endpoint, data=fields, base_url=host).status_code, 400)
        self.assertEqual(self.client.post(endpoint, data=fields, base_url=host).location, '/admin/login')
        self.assertEqual(self.post_form(self.admin, endpoint, fields).status_code, 302)
        self.assertEqual(dict(self.database_account('02342')), before)
        self.assertIn('Fictional', self.admin.get('/admin', base_url=host).text)
        self.assertNotIn('Fictional', self.client.get('/login', base_url=host).text)
        added = self.post_form(self.admin, '/admin/teachers', {'acronym': 'abc', 'first_name': 'Example'})
        self.assertIn('Copy password', added.text)
        self.assertIn('Example', added.text)
        self.assertNotIn('Fictional', added.text)
        self.assertNotIn('Copy password', self.admin.get('/admin?role=teachers', base_url=host).text)
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("UPDATE accounts SET last_sign_in_utc='2026-10-01T00:00:00Z' WHERE school_number='02342'")
            conn.execute("UPDATE accounts SET last_sign_in_utc='2026-01-31T00:00:00Z' WHERE school_number='02343'")
        def order(direction):
            page = self.admin.get('/admin?sort=signin&direction='+direction, base_url=host)
            return re.findall(r'aria-label="Manage (\d+)"', page.text)
        self.assertEqual(order('desc'), ['02342', '02343'])
        self.assertEqual(order('asc'), ['02343', '02342'])
        first = re.search(r'<code>([^<]+)</code>', added.text)[1]
        self.assertEqual(self.student_login('abc', first).location, '/change-password')
        self.assertEqual(self.change_password(self.client, 'Example-owned password').location, '/')
        self.assertEqual(self.client.post(endpoint, data=fields, base_url=host).status_code, 403)
        self.assertEqual(self.post_form(self.admin, endpoint, dict(fields, first_name='')).status_code, 302)
        self.assertNotIn('Fictional', self.admin.get('/admin', base_url=host).text)

    def test_manage_teacher_preserves_other_accounts_and_enforces_controls(self):
        host = 'https://ada.test'
        path = '/admin/teachers/account'
        username = 'example'
        password = 'Existing teacher pass'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            for name in (username, 'colleague'):
                conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)',
                             (name, PasswordHasher().hash(password)))
        def manage(action, **extra):
            return self.post_form(self.admin, path, dict(username=username, action=action, **extra))
        def signin(device, name=username, secret=password):
            return self.post_form(device, '/login', dict(email=name, password=secret))
        colleague = self.app.test_client()
        self.assertEqual(signin(colleague, 'colleague').location, '/')
        self.assertEqual(signin(self.client).location, '/')
        self.assertEqual(self.client.post(path, base_url=host).status_code, 403)
        self.assertEqual(self.admin.post(path, base_url=host).status_code, 400)
        self.assertEqual(self.post_form(self.admin, path, dict(username='admin', action='reset')).status_code, 404)
        second = self.app.test_client()
        self.assertEqual(signin(second).location, '/')
        with closing(sqlite3.connect(self.db_path)) as conn:
            def stamp():
                return conn.execute('SELECT last_sign_in_utc FROM staff_accounts WHERE username=?', (username,)).fetchone()[0]
            before = stamp()
            self.assertEqual(manage('revoke').status_code, 200)
            for device in (second, self.client):
                self.assertEqual(device.get('/', base_url=host).location, '/login')
            self.assertEqual(manage('suspend').status_code, 200)
            self.assertEqual(signin(second).status_code, 401)
            self.assertEqual(manage('reset').status_code, 400)
            self.assertEqual(manage('reactivate').status_code, 200)
            self.assertEqual(before, stamp())
        self.assertEqual(manage('force').status_code, 200)
        self.assertEqual(signin(second).location, '/change-password')
        self.assertEqual(second.get('/', base_url=host).location, '/change-password')
        self.assertEqual(self.change_password(second, 'New teacher pass').location, '/')
        first = re.search(r'<code>([^<]+)</code>', manage('reset').text)[1]
        self.assertEqual(second.get('/', base_url=host).location, '/login')
        self.assertEqual(manage('reset', chosen_password=first).status_code, 400)
        replacement = 'Private first pass'
        self.assertEqual(manage('reset', chosen_password=replacement).status_code, 200)
        self.assertEqual(signin(second, secret=first).status_code, 401)
        self.assertEqual(signin(second, secret='New teacher pass').status_code, 401)
        self.assertEqual(signin(second, secret=replacement).location, '/change-password')
        self.assertEqual(signin(self.client, secret=replacement).status_code, 401)
        self.assertEqual(colleague.get('/', base_url=host).status_code, 200)
        self.assertNotIn(replacement, self.admin.get('/admin?role=teachers', base_url=host).text)

    def test_further_mechanics_role_access(self):
        host = 'https://ada.test'
        base = 'resources/teaching/v003/further-mechanics-1/'
        directory = self.build.parent / 'school-resources' / 'further-mechanics-1'
        student_pdf = 'booklets/chapter-01.pdf'
        teacher_pdf = 'textbook/chapter-01.pdf'
        for name in [student_pdf, teacher_pdf, 'unlisted.pdf']:
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(('%PDF-' + name).encode())
        self.assertEqual(self.client.get('/' + base + teacher_pdf, base_url=host).status_code, 302)
        password = 'School fixture password'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)',
                         ('mechanics.staff', PasswordHasher().hash(password)))
        self.assertEqual(self.student_login('mechanics.staff', password).location, '/')
        for name in [student_pdf, teacher_pdf]:
            with self.client.get('/' + base + name, base_url=host) as response:
                self.assertEqual(response.data, ('%PDF-' + name).encode())
        self.assertEqual(self.client.get('/' + base + 'unlisted.pdf', base_url=host).status_code, 404)
        self.add('01239')
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('UPDATE accounts SET password_hash=?,force_change=0 WHERE school_number=?',
                         (PasswordHasher().hash(password), '01239'))
        self.assertEqual(self.student_login('01239@marlboroughcollege.org', password).location, '/')
        self.assertEqual(self.client.get('/' + base + teacher_pdf, base_url=host).status_code, 404)
        with self.client.get('/teaching-lesson-viewer.html', base_url=host) as teaching:
            self.assertEqual(teaching.status_code, 200)
            self.assertIn("frame-src 'self' https://www.youtube-nocookie.com/embed/6dTyOl1fmDo;",
                          teaching.headers['Content-Security-Policy'])
        with self.client.get('/' + base + student_pdf, base_url=host) as handout:
            self.assertNotIn('youtube-nocookie.com', handout.headers['Content-Security-Policy'])
        viewer = self.client.get('/' + base + student_pdf + '?page=12', base_url=host,
                                 headers={'Sec-Fetch-Dest': 'document'})
        self.assertIn((base + student_pdf + '?inline=1#page=12').encode(), viewer.data)
        with self.client.get('/' + base + student_pdf, base_url=host) as response:
            self.assertEqual(response.data, ('%PDF-' + student_pdf).encode())

    def test_staff_content_login_is_independent_of_pupils_and_admin(self):
        login = 'sample.teacher'
        temp = 'One-use-test-secret!'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('INSERT INTO staff_accounts(username,temporary_hash,temporary_available) VALUES(?,?,1)',
                         (login, PasswordHasher().hash(temp)))
        self.assertEqual(self.student_login('unknown.teacher', temp).status_code, 401)
        self.assertEqual(self.student_login(login, temp).location, '/change-password')
        self.assertEqual(self.client.get('/content/questions.json', base_url='https://ada.test').location, '/change-password')
        self.assertEqual(self.student_login(login, temp).status_code, 401)
        new = 'abcdefgh'
        self.assertEqual(self.change_password(self.client, new[:-1]).status_code, 400)
        self.assertEqual(self.change_password(self.client, new).location, '/')
        self.assertEqual(self.student_login(login, new).location, '/')
        self.assertEqual(self.client.get('/admin', base_url='https://ada.test').status_code, 403)
        self.assertEqual(self.client.get('/', base_url='https://ada.test').status_code, 200)
        second = self.app.test_client()
        def attempt(address):
            return self.post_form(second, '/login', {'email': address, 'password': new})
        self.assertEqual(attempt(login + '@marlboroughcollege.org.evil').status_code, 401)
        self.assertEqual(attempt(login.upper() + '@MARLBOROUGHCOLLEGE.ORG').location, '/')
        for device in (self.client, second):
            self.assertEqual(device.get('/', base_url='https://ada.test').status_code, 200)
        admin = self.admin.get('/admin?role=teachers', base_url='https://ada.test').get_data(as_text=True)
        self.assertIn('<h2>Teacher accounts</h2>', admin)
        self.assertIn('Manage ' + login, admin)
        self.assertIsNone(self.database_account(login))

    def test_offline_logout_is_limited_to_the_launching_staff_session(self):
        host = 'https://ada.test'
        # The admin cookie is scoped to /admin, so this course URL requires its own login.
        denied = self.admin.get('/staff/offline-logout', base_url=host)
        self.assertEqual((denied.status_code, denied.location), (302, '/login'))
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)',
                         ('fixture', PasswordHasher().hash('staff fixture password')))
        (self.build / 'index.html').write_text('<a href="https://example.test/offline.html#ada-staff=__LUISA_OFFLINE_LOGOUT__">Offline</a>')
        first, second = self.client, self.app.test_client()
        for client in (first, second):
            self.assertEqual(self.post_form(client, '/login', {'email':'fixture', 'password':'staff fixture password'}).location, '/')
        ticket = re.search(r'#ada-staff=([a-f0-9]{64})', first.get('/', base_url=host).text).group(1)
        for client, expected, submitted in [(second, 403, ticket), (first, 403, '0'*64), (first, 302, ticket)]:
            page = client.get('/staff/offline-logout', base_url=host)
            self.assertEqual(page.status_code, 200)
            csrf = re.search(r'name="_csrf" value="([^"]+)"', page.text).group(1)
            self.assertNotEqual(ticket, csrf)
            result = client.post('/staff/offline-logout', data={'ticket':submitted, '_csrf':csrf}, base_url=host)
            self.assertEqual(result.status_code, expected)
        self.assertEqual(first.get('/', base_url=host).location, '/login')
        self.assertEqual(second.get('/', base_url=host).status_code, 200)

    def test_latest_success_replaces_only_prior_pupil_session(self):
        number, password = '02340', 'Eight-or-more'
        self.add(number)
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('UPDATE accounts SET password_hash=? WHERE school_number=?', (PasswordHasher().hash(password), number))
        second = self.app.test_client()
        def enter(device, secret):
            return self.post_form(device, '/login', {'email': number + '@marlboroughcollege.org', 'password': secret})
        self.assertEqual(enter(self.client, password).location, '/')
        self.assertEqual(enter(second, 'incorrect').status_code, 401)
        self.assertEqual(self.client.get('/', base_url='https://ada.test').status_code, 200)
        self.assertEqual(enter(second, password).location, '/')
        self.assertEqual(self.client.get('/', base_url='https://ada.test').location, '/login')
        self.assertEqual(second.get('/', base_url='https://ada.test').status_code, 200)

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
        stamp = datetime.fromisoformat(first_sign_in.replace('Z', '+00:00'))
        expected_uk_time = f'{stamp:%d/%m/%y} {stamp.hour}:{stamp:%M}'
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

    def test_session_status_does_not_renew_activity_and_logout_requires_its_token(self):
        host = 'https://ada.test'
        self.add('02341')
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('UPDATE accounts SET password_hash=? WHERE school_number=?',
                         (PasswordHasher().hash('My-pupil-password'), '02341'))
        login = {'email': '02341@marlboroughcollege.org', 'password': 'My-pupil-password'}
        self.post_form(self.client, '/login', login)
        with closing(sqlite3.connect(self.db_path)) as conn:
            def snapshot():
                return conn.execute("""SELECT sessions.expires_utc, accounts.last_sign_in_utc
                    FROM sessions JOIN accounts USING(school_number) WHERE school_number='02341'""").fetchone()
            before = snapshot()
            check = self.client.get('/session-status', base_url=host)
            self.assertEqual(check.status_code, 204)
            self.assertNotIn('Set-Cookie', check.headers)
            self.assertEqual(snapshot(), before)
        second = self.app.test_client()
        self.post_form(second, '/login', login)
        self.assertEqual(self.client.get('/session-status', base_url=host).status_code, 401)
        self.assertEqual(second.post('/logout', base_url=host).status_code, 400)
        with second.get('/resources/printouts/sample.pdf', headers={'Sec-Fetch-Dest':'document'}, base_url=host) as pdf:
            token = re.search(r'name="_csrf" value="([^"]+)"', pdf.text)[1]
            self.assertIn('action="/logout"', pdf.text)
        self.assertEqual(second.post('/logout', data={'_csrf':token}, base_url=host).location, '/login')
        self.assertEqual(second.get('/session-status', base_url=host).status_code, 401)

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

    def test_recent_chapters_resume_across_teacher_sessions_and_are_private(self):
        host = 'https://ada.test'
        path = '/recent-chapters'
        (self.build / 'index.html').write_text("<input type=hidden name=_csrf value='__LUISA_SESSION_CSRF__'>")
        password = 'Synthetic teaching password'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            hashed = PasswordHasher().hash(password)
            conn.executemany('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)',
                             [('first', hashed), ('second', hashed)])
        teacher, second, other_device = (self.app.test_client() for _ in range(3))
        for client, username in [(teacher, 'first'), (second, 'second'), (other_device, 'first')]:
            self.assertEqual(self.post_form(client, '/login', {'email': username, 'password': password}).location, '/')
        def teacher_summary():
            with closing(sqlite3.connect(self.db_path)) as conn:
                return conn.execute("SELECT signins, latest_session, session_ended FROM staff_accounts WHERE username='first'").fetchone()
        latest = teacher_summary()
        self.assertEqual(latest[0], 2)
        self.assertIsNone(latest[2])
        def save(client, chapter, slide):
            data = {'key': f'maths-pure-year-1:{chapter}', 'slide': slide}
            return self.post_form(client, path, data, client.get('/', base_url=host))
        def recent(client):
            result = client.get(path, base_url=host)
            self.assertEqual(result.status_code, 200)
            return [(r['key'], r['slide']) for r in result.json]
        self.assertEqual(teacher.post(path, data={'key':'maths-pure-year-1:1', 'slide':4}, base_url=host).status_code, 400)
        for chapter in range(1, 6):
            self.assertEqual(save(teacher, chapter, chapter + 1).status_code, 204)
        self.assertEqual(save(other_device, 3, 17).status_code, 204)
        expected = [(f'maths-pure-year-1:{n}', slide) for n, slide in [(3,17),(5,6),(4,5),(2,3)]]
        self.assertEqual(recent(teacher), expected)
        self.assertEqual(recent(second), [])
        self.assertEqual(save(second, 3, 2).status_code, 204)
        self.assertEqual(recent(other_device), expected)
        self.assertEqual(self.post_form(teacher, '/logout', {}, teacher.get('/', base_url=host)).status_code, 302)
        self.assertEqual(teacher.get(path, base_url=host).location, '/login')
        self.assertEqual(teacher_summary(), latest)
        self.assertEqual(self.post_form(teacher, '/login', {'email':'first','password':password}).location, '/')
        self.assertEqual(recent(teacher), expected)
        self.assertEqual(teacher_summary()[0], 3)
        self.assertNotEqual(teacher_summary()[1], latest[1])
        self.add('02340')
        self.action('02340', 'reset', chosen_password='Synthetic first pupil password')
        self.assertEqual(self.student_login('02340@marlboroughcollege.org','Synthetic first pupil password').location, '/change-password')
        self.assertEqual(self.change_password(self.client,'Synthetic second pupil password').location, '/')
        self.assertEqual(self.client.get(path, base_url=host).status_code, 403)
        self.assertEqual(save(self.client, 3, 1).status_code, 403)
        self.assertEqual(recent(teacher), expected)

    def test_pupil_signin_count_and_duration_survive_password_rotation_logout_and_expiry(self):
        host = 'https://ada.test'
        number, email = '02340', '02340@marlboroughcollege.org'
        self.add(number)
        self.action(number, 'reset', chosen_password='Synthetic pupil initial password')
        self.assertEqual(self.student_login(email, 'wrong').status_code, 401)
        self.assertEqual(self.database_account(number)['signins'], 0)
        self.assertEqual(self.student_login(email, 'Synthetic pupil initial password').location, '/change-password')
        first = self.database_account(number)
        self.assertEqual(first['signins'], 1)
        self.assertEqual(self.change_password(self.client, 'Synthetic pupil changed password').location, '/')
        rotated = self.database_account(number)
        self.assertNotEqual(rotated['latest_session'], first['latest_session'])
        self.assertEqual(rotated['last_sign_in_utc'], first['last_sign_in_utc'])
        self.assertEqual(rotated['signins'], 1)
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("UPDATE accounts SET last_sign_in_utc=strftime('%Y-%m-%dT%H:%M:%SZ','now','-315 seconds') WHERE school_number=?", (number,))
        def directory():
            return self.admin.get('/admin', base_url=host).text
        self.assertIn('5 min · signed in', directory())
        (self.build / 'index.html').write_text("<input type=hidden name=_csrf value='__LUISA_SESSION_CSRF__'>")
        self.assertEqual(self.post_form(self.client, '/logout', {}, self.client.get('/', base_url=host)).status_code, 302)
        self.assertIn('5 min · ended', directory())
        self.assertEqual(self.student_login(email, 'Synthetic pupil changed password').location, '/')
        self.assertEqual(self.database_account(number)['signins'], 2)
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("UPDATE accounts SET last_sign_in_utc=strftime('%Y-%m-%dT%H:%M:%SZ','now','-10 minutes') WHERE school_number=?", (number,))
            conn.execute("""UPDATE sessions SET created_utc=strftime('%Y-%m-%dT%H:%M:%SZ','now','-10 minutes'),
                          expires_utc=strftime('%Y-%m-%dT%H:%M:%SZ','now','-165 seconds') WHERE school_number=?""", (number,))
        self.assertIn('7 min · expired', directory())
        self.assertEqual(self.client.get('/', base_url=host).location, '/login')
        self.assertIn('7 min · expired', directory())
        self.assertEqual(self.database_account(number)['signins'], 2)

    def test_signing_out_of_admin_preserves_the_same_browsers_teaching_session(self):
        host = 'https://ada.test'
        app = create_app(dict(self.app.config, ADMIN_AUTH_MODE='password'))
        client = app.test_client()
        password = 'Synthetic teaching password'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)',
                         ('first', PasswordHasher().hash(password)))
        self.assertEqual(self.post_form(client, '/login', {'email':'first','password':password}).location, '/')
        teacher_cookie = client.get_cookie(app.config['SESSION_COOKIE'], domain='ada.test').value
        form = client.get('/admin/login', base_url=host)
        self.assertEqual(self.post_form(client, '/admin/login', {'password':self.teacher_password}, form).location, '/admin')
        page = client.get('/admin', base_url=host)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(client.get('/', base_url=host).status_code, 200)
        self.assertEqual(client.post('/admin/logout', data={'library':'1'}, base_url=host).status_code, 400)
        self.assertEqual(self.post_form(client, '/admin/logout', {'library':'1'}, page).location, '/')
        self.assertEqual(client.get('/', base_url=host).status_code, 200)
        self.assertEqual(client.get_cookie(app.config['SESSION_COOKIE'], domain='ada.test').value, teacher_cookie)
        self.assertNotEqual(client.get('/admin', base_url=host).status_code, 200)

    def test_new_admin_signin_retires_legacy_cookie_before_logout(self):
        host = 'https://ada.test'
        app = create_app(dict(self.app.config, ADMIN_AUTH_MODE='password'))
        client = app.test_client()
        legacy = self.admin.get_cookie('luisa_admin_session', domain='ada.test', path='/admin').value
        client.set_cookie(app.config['SESSION_COOKIE'], legacy, domain='ada.test', path='/')
        self.assertEqual(client.get('/admin', base_url=host).status_code, 200)
        form = client.get('/admin/login', base_url=host)
        self.assertEqual(self.post_form(client, '/admin/login', {'password':self.teacher_password}, form).location, '/admin')
        self.assertIsNone(client.get_cookie(app.config['SESSION_COOKIE'], domain='ada.test', path='/'))
        page = client.get('/admin', base_url=host)
        self.assertEqual(self.post_form(client, '/admin/logout', {'library': '1'}, page).location, '/')
        self.assertEqual(client.get('/admin', base_url=host).location, '/admin/login')
        client.set_cookie(app.config['SESSION_COOKIE'], legacy, domain='ada.test', path='/')
        self.assertEqual(client.get('/admin', base_url=host).location, '/admin/login')

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


    # ---- NAV-091: return to the last page and selection, privately per account ----
    PREFERENCES_META = ('<meta name="luisa-preferences" content="ada" data-csrf="__LUISA_SESSION_CSRF__" '
                        'data-scope="__LUISA_TAB_SCOPE__" data-default-course="__LUISA_DEFAULT_COURSE__" '
                        'data-modules="__LUISA_PREFERENCE_MODULES__" data-state="__LUISA_PREFERENCES__">')

    def preference_build(self):
        names = ['index.html', 'papers.html', 'textbook-view.html', 'teaching-chapters.html']
        for name in names:
            (self.build / name).write_text(f"<!doctype html>{self.PREFERENCES_META}<form><input type=hidden name=_csrf value='__LUISA_SESSION_CSRF__'></form>{name}")
        manifest = json.loads((self.build / 'build-manifest.json').read_text())
        manifest['files'].update({name: {} for name in names})
        (self.build / 'build-manifest.json').write_text(json.dumps(manifest))
        # The asset list is read at start-up; the existing admin session carries over to the new app.
        cookies = [(cookie.key, cookie.value, cookie.path) for cookie in self.admin._cookies.values()]
        self.app = create_app({**self.app.config, 'STUDENT_BUILD_DIR': str(self.build)})
        self.client = self.app.test_client()
        self.admin = self.app.test_client()
        for key, value, path in cookies:
            self.admin.set_cookie(key, value, domain='ada.test', path=path)

    def page_preferences(self, client, page='/papers.html'):
        response = client.get(page, base_url='https://ada.test')
        self.assertEqual(response.status_code, 200, response.location)
        text = response.get_data(as_text=True)
        meta = re.search(r'<meta name="luisa-preferences" content="ada" data-csrf="([^"]*)" data-scope="([^"]*)" '
                         r'data-default-course="([^"]*)" data-modules="([^"]*)" data-state="([^"]*)">', text)
        self.assertIsNotNone(meta, text)
        import html as _html
        return {'csrf': meta[1], 'scope': meta[2], 'course': meta[3], 'modules': meta[4], 'state': json.loads(_html.unescape(meta[5]))}

    def save_preference(self, client, csrf, **fields):
        return client.post('/preferences', data={'_csrf': csrf, **fields}, base_url='https://ada.test')

    def pupil(self, number, class_code, password):
        self.post_form(self.admin, '/admin/roster', {'numbers': number, 'class_code': class_code})
        self.action(number, 'reset', chosen_password='Temporary ' + password)
        client = self.app.test_client()
        page = client.get('/login', base_url='https://ada.test')
        self.assertEqual(self.post_form(client, '/login', {'email': number + '@marlboroughcollege.org', 'password': 'Temporary ' + password}, page).location, '/change-password')
        self.assertEqual(self.change_password(client, password).location, '/')
        return client

    def sign_in(self, email, password, path='/login', fragment=''):
        client = self.app.test_client()
        page = client.get(path, base_url='https://ada.test')
        return client, self.post_form(client, path, {'email': email, 'password': password, 'fragment': fragment}, page)

    def test_pupil_preferences_follow_the_account_to_a_second_browser_NAV_091(self):
        self.preference_build()
        further = self.pupil('02340', 'U6Y', 'Synthetic further pupil password')
        other = self.pupil('02341', '', 'Synthetic other pupil password')
        prefs = self.page_preferences(further)
        self.assertEqual((prefs['course'], prefs['modules'], prefs['state']), ('further-maths-a-level', 'papers,resources,skill,textbook', {'last': None, 'modules': {}}))
        self.assertEqual(self.page_preferences(other)['course'], 'maths-a-level')
        draft = {'version': 4, 'course': 'further-maths-a-level', 'chapters': ['a', 'b'], 'sources': {'old-spec': True},
                 'mode': 'time', 'minutes': '45', 'selected': [], 'note': '__LUISA_SESSION_CSRF__'}
        csrf = prefs['csrf']
        self.assertEqual(self.save_preference(further, csrf, module='papers', state=json.dumps(draft)).status_code, 204)
        self.assertEqual(self.save_preference(further, csrf, last='papers').status_code, 204)
        # Invalid writes, a wrong token and a teacher-only module are refused.
        self.assertEqual(self.save_preference(further, 'wrong', last='skill').status_code, 400)
        self.assertEqual(self.save_preference(further, csrf, module='exam', state='{}').status_code, 400)
        self.assertEqual(self.save_preference(further, csrf, module='papers', state='[1]').status_code, 400)
        self.assertEqual(self.save_preference(further, csrf, module='papers', state='{"x":"' + 'y' * 12000 + '"}').status_code, 400)
        self.assertEqual(self.save_preference(further, csrf, last='admin').status_code, 400)
        self.assertEqual(self.save_preference(self.app.test_client(), csrf, last='papers').status_code, 302)
        # A second browser opens Papers with the same draft; the saved text cannot fill a page placeholder.
        second, signed = self.sign_in('02340@marlboroughcollege.org', 'Synthetic further pupil password')
        self.assertEqual(signed.location, '/papers.html')
        restored = self.page_preferences(second)
        self.assertEqual(restored['state'], {'last': 'papers', 'modules': {'papers': draft}})
        self.assertNotEqual(restored['scope'], prefs['scope'])
        # Another pupil sees only their own (empty) preferences.
        self.assertEqual(self.page_preferences(other)['state'], {'last': None, 'modules': {}})
        # A shared link survives sign-in, including its fragment; unsafe destinations are ignored.
        anonymous = self.app.test_client()
        self.assertEqual(anonymous.get('/textbook-view.html', base_url='https://ada.test').location, '/login?next=/textbook-view.html')
        self.assertEqual(anonymous.get('/', base_url='https://ada.test').location, '/login')
        for path, fragment, expected in [
                ('/login?next=/textbook-view.html', '#course=maths-a-level&book=maths-pure-year-1&chapter=3', '/textbook-view.html#course=maths-a-level&book=maths-pure-year-1&chapter=3'),
                ('/login', '#course=maths-a-level&skill=smq-1.1&question=2', '/#course=maths-a-level&skill=smq-1.1&question=2'),
                ('/login?next=//evil.test/x.html', '', '/papers.html'), ('/login?next=/admin', '', '/papers.html'),
                ('/login?next=https://evil.test/', '', '/papers.html'), ('/login', '#"><script>', '/papers.html')]:
            _, response = self.sign_in('02340@marlboroughcollege.org', 'Synthetic further pupil password', path, fragment)
            self.assertEqual(response.location, expected, path)
        # Preferences are removed with the account and hold no timestamps.
        with closing(sqlite3.connect(self.db_path)) as conn:
            columns = {row[1] for row in conn.execute('PRAGMA table_info(pupil_preferences)')}
            self.assertEqual(columns, {'school_number', 'module', 'state'})

    def test_teacher_preferences_keep_exam_settings_and_last_module_NAV_091(self):
        self.preference_build()
        password = 'Synthetic teaching password'
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute('INSERT INTO staff_accounts(username,password_hash,force_change) VALUES(?,?,0)', ('first', PasswordHasher().hash(password)))
        teacher, signed = self.sign_in('first', password)
        self.assertEqual(signed.location, '/')
        prefs = self.page_preferences(teacher, '/textbook-view.html')
        self.assertEqual(prefs['course'], '')
        self.assertEqual(self.save_preference(teacher, prefs['csrf'], module='exam', state='{"title":"Mock","draft":true}').status_code, 204)
        self.assertEqual(self.save_preference(teacher, prefs['csrf'], module='textbook', state='{"course":"maths-a-level","chapter":"4"}').status_code, 204)
        self.assertEqual(self.save_preference(teacher, prefs['csrf'], last='textbook').status_code, 204)
        other, signed = self.sign_in('first', password)
        self.assertEqual(signed.location, '/textbook-view.html')
        state = self.page_preferences(other, '/papers.html')['state']
        self.assertEqual(state['modules']['exam'], {'title': 'Mock', 'draft': True})
        self.assertEqual(state['last'], 'textbook')
        self.assertEqual(self.save_preference(other, prefs['csrf'], last='skill').status_code, 400)

if __name__ == '__main__':
    unittest.main()
