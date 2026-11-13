#!/usr/bin/env python3
"""Create initial admin MFA/hash secrets in a new private env file."""
import argparse
from getpass import getpass
import os
from pathlib import Path
import shlex

from argon2 import PasswordHasher
import pyotp


def main():
    parser = argparse.ArgumentParser(description='Bootstrap Luisa teacher password hashing and MFA secrets.')
    parser.add_argument('environment_file', help='New absolute path outside all public/source directories')
    parser.add_argument('--teacher-label', default='Luisa teacher', help='Label shown in the authenticator app')
    args = parser.parse_args()
    destination = Path(args.environment_file)
    if not destination.is_absolute():
        parser.error('The environment file path must be absolute.')
    destination = destination.resolve()
    source_root = Path(__file__).resolve().parents[1]
    if destination.is_relative_to(source_root):
        parser.error('The environment file must be outside the source repository and public build tree.')
    password = getpass('Choose the teacher admin password (minimum 16 characters): ')
    confirmation = getpass('Repeat the teacher admin password: ')
    if len(password) < 16 or len(password) > 1024 or password != confirmation:
        parser.error('Passwords must match and be 16 to 1024 characters.')
    password_hash = PasswordHasher().hash(password)
    totp_secret = pyotp.random_base32()
    uri = pyotp.TOTP(totp_secret).provisioning_uri(name=args.teacher_label, issuer_name='Luisa')
    values = {
        'LUISA_ADMIN_PASSWORD_HASH': password_hash,
        'LUISA_ADMIN_TOTP_SECRET': totp_secret,
    }
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(destination, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        for key, value in values.items():
            stream.write(f'export {key}={shlex.quote(value)}\n')
    os.chmod(destination, 0o600)
    print(f'Private environment file created: {destination}')
    print('Add the TOTP account below to the teacher authenticator now; the seed is private.')
    print(uri)


if __name__ == '__main__':
    main()
