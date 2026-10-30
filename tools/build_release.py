"""Build a checked ZIP from the public file manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hxkit.release import release_files  # noqa: E402


def build_release(root: Path, output: Path) -> dict:
    root = Path(root).resolve()
    output = Path(output).expanduser()
    if output.exists() or output.is_symlink():
        raise ValueError('ZIP output already exists')
    output = output.resolve()
    if output.is_relative_to(root):
        raise ValueError('ZIP output must be outside the release source directory')
    if not output.parent.is_dir():
        raise ValueError('ZIP output parent directory does not exist')
    files = release_files(root)
    names = [path.relative_to(root).as_posix() for path in files]
    created = False
    try:
        with output.open('xb') as destination:
            created = True
            with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED,
                                 allowZip64=True) as archive:
                for source, name in zip(files, names):
                    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o644 << 16
                    with source.open('rb') as input_file, archive.open(info, 'w') as entry:
                        shutil.copyfileobj(input_file, entry, length=65536)
            destination.flush()
            os.fsync(destination.fileno())
        with zipfile.ZipFile(output, 'r') as archive:
            if archive.namelist() != names or archive.testzip() is not None:
                raise ValueError('ZIP contents or CRC verification failed')
            crc32 = {item.filename: f'{item.CRC:08x}' for item in archive.infolist()}
        sha256 = hashlib.sha256()
        with output.open('rb') as stream:
            for chunk in iter(lambda: stream.read(65536), b''):
                sha256.update(chunk)
        return {'output': str(output), 'sha256': sha256.hexdigest(),
                'files': names, 'crc32': crc32}
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_release(ROOT, args.output), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f'release build failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
