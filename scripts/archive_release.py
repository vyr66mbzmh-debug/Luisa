"""Create a checked website recovery ZIP and retain the newest five."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import zipfile

NAME = re.compile(r'(?:Luisa-|luisa-)?v(\d+)\.(\d+)-[0-9a-f]{7,40}-website\.zip\Z')


def archive(directory):
    directory = directory.resolve(strict=True)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    release = json.loads(subprocess.check_output(['git', 'show', 'HEAD:release.json']))
    path = directory / f"v{release['version']}-{revision[:12]}-website.zip"
    if not NAME.fullmatch(path.name):
        raise ValueError('Unexpected release version')
    staging = directory / (path.name + '.staging')
    if not path.exists():
        subprocess.run(['git','archive','--format=zip','-1','--output',str(staging),revision],check=True)
    candidate = path if path.exists() else staging
    with zipfile.ZipFile(candidate) as z:
        if z.comment.decode() != revision or z.testzip() or json.loads(z.read('release.json')) != release:
            raise ValueError('Recovery ZIP verification failed')
    with candidate.open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
    if candidate == staging:
        staging.replace(path)
    path.with_suffix('.zip.sha256').write_text(checksum+'  '+path.name+'\n')
    known = [p for p in directory.iterdir() if p.is_file() and NAME.fullmatch(p.name)]
    known.sort(key=lambda p: (*map(int,NAME.fullmatch(p.name).groups()),p.stat().st_mtime),reverse=True)
    for old in known[5:]:
        old.unlink()
        old.with_suffix('.zip.sha256').unlink(missing_ok=True)
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(archive(parser.parse_args().directory).name)
