"""Validate the explicit file allowlist for a public release."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re


MANIFEST = 'public-manifest.json'
_FORBIDDEN = {'.git', '.harness', '.harness-kit', 'internal', 'private',
              'secrets', '.ssh', '.aws', '__pycache__'}
_CACHE_FILES = {'.DS_Store'}
_DRIVE = re.compile(r'^[A-Za-z]:')


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate manifest key: {key}')
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f'invalid manifest number: {value}')


def _relative_file(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or '\\' in value or '\0' in value:
        raise ValueError('manifest files must be nonempty POSIX relative paths')
    path = PurePosixPath(value)
    if path.is_absolute() or _DRIVE.match(value) or path.as_posix() != value:
        raise ValueError(f'invalid release path: {value}')
    if any(part in {'.', '..'} or ':' in part for part in path.parts):
        raise ValueError(f'path traversal or invalid component: {value}')
    if any(part.casefold() in _FORBIDDEN or part.casefold() == '.env'
           or part.casefold().startswith('.env.') for part in path.parts):
        raise ValueError(f'forbidden release path: {value}')
    if path.name in _CACHE_FILES or path.suffix == '.pyc':
        raise ValueError(f'cache file is not a release file: {value}')
    return path


def _is_cache(relative: Path) -> bool:
    return ('__pycache__' in relative.parts or relative.name in _CACHE_FILES
            or relative.suffix == '.pyc')


def release_files(root: Path) -> list[Path]:
    """Return validated absolute files in manifest order; reject unlisted files."""
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('release root must be an existing regular directory')
    root = root.resolve()
    manifest_path = root / MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError('public-manifest.json is missing or not a regular file')
    if manifest_path.stat().st_size > 1_000_000:
        raise ValueError('public-manifest.json exceeds 1 MB')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'),
                          object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    if not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1:
        raise ValueError('public manifest schema_version must be 1')
    declared = manifest.get('files')
    if not isinstance(declared, list) or not declared:
        raise ValueError('public manifest files must be a nonempty list')
    names = []
    seen = set()
    for value in declared:
        name = _relative_file(value)
        if name.as_posix() in seen:
            raise ValueError(f'duplicate release file: {name}')
        seen.add(name.as_posix())
        names.append(name)
    if MANIFEST not in seen:
        raise ValueError('public-manifest.json must list itself')
    files = []
    for name in names:
        current = root
        for part in name.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f'symlink is not allowed in release path: {name}')
        if not current.is_file() or not current.resolve().is_relative_to(root):
            raise ValueError(f'declared release file is missing or not regular: {name}')
        files.append(current)
    for current in root.rglob('*'):
        relative = current.relative_to(root)
        # A checkout's root Git metadata is never a distributable file.
        # It remains forbidden in the manifest itself.
        if relative.parts[0] == '.git':
            continue
        if current.is_symlink():
            raise ValueError(f'symlink is not allowed in release tree: {relative}')
        if current.is_dir():
            continue
        if not current.is_file():
            raise ValueError(f'nonregular item in release tree: {relative}')
        if _is_cache(relative):
            continue
        if relative.as_posix() not in seen:
            raise ValueError(f'unlisted release file: {relative}')
    return files
