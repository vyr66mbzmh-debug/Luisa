#!/usr/bin/env python3
"""Create initial teacher sign-in settings in a new private env file."""
import argparse
from getpass import getpass
import os
from pathlib import Path
import shlex

from argon2 import PasswordHasher
import pyotp


def main():
    parser = argparse.ArgumentParser(description='Set up the private Luisa teacher password.')
    parser.add_argument('environment_file', help='New absolute path outside all public/source directories')
    parser.add_argument('--with-totp', action='store_true', help='Also require an authenticator code')
    parser.add_argument('--teacher-label', default='Luisa teacher', help='Label shown in the authenticator app')
    args = parser.parse_args()
    destination = Path(args.environment_file)
    if not destination.is_absolute():
        parser.error('The environment file path must be absolute.')
    destination = destination.resolve()
    source_root = Path(__file__).resolve().parents[1]
    if destination.is_relative_to(source_root):
        parser.error('The environment file must be outside the source repository and public build tree.')
    password = getpass('Choose the teacher admin password (minimum 9 characters): ')
    confirmation = getpass('Repeat the teacher admin password: ')
    if len(password) < 9 or len(password) > 1024 or password != confirmation:
        parser.error('Passwords must match and be 9 to 1024 characters.')
    password_hash = PasswordHasher().hash(password)
    values = {
        'LUISA_ADMIN_PASSWORD_HASH': password_hash,
        'LUISA_ADMIN_AUTH_MODE': 'totp' if args.with_totp else 'password',
    }
    if args.with_totp:
        values['LUISA_ADMIN_TOTP_SECRET'] = pyotp.random_base32()
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(destination, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        for key, value in values.items():
            stream.write(f'export {key}={shlex.quote(value)}\n')
    os.chmod(destination, 0o600)
    print(f'Private environment file created: {destination}')
    if args.with_totp:
        print(pyotp.TOTP(values['LUISA_ADMIN_TOTP_SECRET']).provisioning_uri(name=args.teacher_label, issuer_name='Luisa'))


if __name__ == '__main__':
    main()
