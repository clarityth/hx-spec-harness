"""The release archive contains only explicitly declared files."""

import hashlib
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from hxkit.release import release_files
from hxkit import cli
from tools.build_release import build_release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'source'
        self.root.mkdir()
        (self.root / 'hxkit').mkdir()
        (self.root / 'hxkit/core.py').write_text('print("public")\n', encoding='utf-8')
        self.names = ['public-manifest.json', 'hxkit/core.py']
        self.manifest()

    def manifest(self, names=None):
        (self.root / 'public-manifest.json').write_text(json.dumps(
            {'schema_version': 1, 'files': self.names if names is None else names}),
            encoding='utf-8')

    def test_only_declared_files_are_packed_and_hashes_match(self):
        (self.root / '__pycache__').mkdir()
        (self.root / '__pycache__/core.cpython-311.pyc').write_bytes(b'cache')
        (self.root / '.DS_Store').write_bytes(b'cache')
        output = self.base / 'release.zip'
        result = build_release(self.root, output)
        self.assertEqual(result['files'], self.names)
        self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), result['sha256'])
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.namelist(), self.names)
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read('hxkit/core.py'), b'print("public")\n')
            self.assertEqual({item.filename: f'{item.CRC:08x}' for item in archive.infolist()}, result['crc32'])

    def test_unlisted_internal_document_blocks_build_before_output(self):
        (self.root / 'internal').mkdir()
        (self.root / 'internal/notes.md').write_text('not for release', encoding='utf-8')
        output = self.base / 'release.zip'
        with self.assertRaisesRegex(ValueError, 'unlisted release file'):
            build_release(self.root, output)
        self.assertFalse(output.exists())

    def test_git_checkout_metadata_is_excluded_and_cannot_be_declared(self):
        metadata = self.root / '.git'
        metadata.mkdir()
        (metadata / 'config').write_text('local repository metadata', encoding='utf-8')
        output = self.base / 'checkout.zip'
        result = build_release(self.root, output)
        self.assertEqual(result['files'], self.names)
        self.manifest(self.names + ['.git/config'])
        with self.assertRaisesRegex(ValueError, 'forbidden'):
            release_files(self.root)
        self.manifest()
        (metadata / 'config').unlink()
        metadata.rmdir()
        metadata.write_text('gitdir: external-worktree-metadata', encoding='utf-8')
        self.assertEqual(len(release_files(self.root)), len(self.names))

    def test_declared_forbidden_and_traversal_paths_are_rejected(self):
        for path in ('../other.txt', '/tmp/other.txt', 'internal/notes.md', '.env',
                     'private/data.txt', 'secrets/token.txt', 'C:/private.txt',
                     'hxkit\\..\\private.txt'):
            with self.subTest(path=path):
                self.manifest(self.names + [path])
                with self.assertRaises(ValueError):
                    release_files(self.root)

    def test_duplicate_missing_and_unlisted_file_are_rejected(self):
        self.manifest(self.names + ['hxkit/core.py'])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            release_files(self.root)
        self.manifest(self.names + ['missing.txt'])
        with self.assertRaisesRegex(ValueError, 'missing'):
            release_files(self.root)
        self.manifest(['hxkit/core.py'])
        with self.assertRaisesRegex(ValueError, 'list itself'):
            release_files(self.root)
        self.manifest()
        (self.root / 'extra.md').write_text('extra', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            release_files(self.root)

    def test_symlink_is_rejected_whether_declared_or_unlisted(self):
        target = self.base / 'outside.txt'
        target.write_text('outside', encoding='utf-8')
        (self.root / 'linked.txt').symlink_to(target)
        self.manifest(self.names + ['linked.txt'])
        with self.assertRaisesRegex(ValueError, 'symlink'):
            release_files(self.root)
        self.manifest()
        with self.assertRaisesRegex(ValueError, 'symlink'):
            release_files(self.root)

    def test_existing_output_is_preserved_and_inside_output_rejected(self):
        output = self.base / 'release.zip'
        output.write_bytes(b'preserve')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            build_release(self.root, output)
        self.assertEqual(output.read_bytes(), b'preserve')
        with self.assertRaisesRegex(ValueError, 'outside'):
            build_release(self.root, self.root / 'release.zip')
        self.assertFalse((self.root / 'release.zip').exists())

    def test_install_rejects_unlisted_document_before_copying(self):
        (self.root / 'notes.md').write_text('unlisted preparation notes', encoding='utf-8')
        project = self.base / 'project'
        project.mkdir()
        with patch.object(cli, 'TOOLKIT', self.root):
            with self.assertRaisesRegex(ValueError, 'unlisted'):
                cli.install(project)
        self.assertEqual(list(project.iterdir()), [])

    def test_install_copies_exact_manifest_and_local_skills(self):
        (self.root / 'HARNESS.md').write_text('generic guide', encoding='utf-8')
        skill = self.root / 'skills/demo/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('generic skill', encoding='utf-8')
        self.names += ['HARNESS.md', 'skills/demo/SKILL.md']
        self.manifest()
        project = self.base / 'project'
        project.mkdir()
        with patch.object(cli, 'TOOLKIT', self.root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.install(project), 0)
        self.assertEqual(sorted(p.relative_to(project / '.harness-kit').as_posix()
                                for p in (project / '.harness-kit').rglob('*') if p.is_file()),
                         sorted(self.names))
        self.assertEqual((project / 'HARNESS.md').read_text(), 'generic guide')
        self.assertEqual((project / '.agents/skills/demo/SKILL.md').read_text(), 'generic skill')
        self.assertEqual([p.relative_to(project / '.harness-kit').as_posix()
                          for p in release_files(project / '.harness-kit')], self.names)


if __name__ == '__main__':
    unittest.main()
