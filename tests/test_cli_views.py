import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from hxkit.cli import main
from hxkit.core import atomic_json, read_json, snapshot


class ViewCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'TASK.md').write_text('Return five.')
        (self.root / 'app.py').write_text('print("5")')
        self.call('init')
        contract = {'schema_version': 1, 'title': 'Synthetic CLI fixture',
            'requirements': [{'id': 'R1', 'description': 'Return five',
                'source': {'path': 'TASK.md', 'quote': 'Return five.'},
                'expected': 'JSON number 5', 'verification': 'behavior',
                'implementation': ['app.py'], 'checks': ['C1']}],
            'checks': [{'id': 'C1', 'kind': 'json', 'tracked_paths': ['app.py'],
                'argv': ['{python}', 'app.py'], 'expected': 5, 'timeout_seconds': 3}],
            'deliverables': ['app.py']}
        atomic_json(self.root / '.harness/contract.json', contract)

    def call(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(['--root', str(self.root), *args])
        return code, out.getvalue()

    def test_views_are_read_only_and_do_not_run_checks(self):
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        for command in ('spec', 'brief'):
            code, text = self.call(command)
            self.assertEqual(code, 0)
            self.assertIn('R1', text)
            self.assertIn('Return five', text)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(read_json(self.root / '.harness/state.json')['latest_checks'], {})

    def test_tradeoff_is_recorded_without_claiming_a_person_performed_it(self):
        code, _ = self.call('decision', '--requirement', 'R1', '--actor', 'ai',
            '--choice', 'Use standard library', '--reason', 'Existing runtime supports the task',
            '--alternative', 'Install framework', '--tradeoff', 'Fewer ready-made components',
            '--evidence', 'C1')
        self.assertEqual(code, 0)
        decision = read_json(self.root / '.harness/state.json')['decisions'][0]
        self.assertEqual(decision['actor'], 'ai')
        self.assertEqual(decision['alternatives'], ['Install framework'])
        self.assertEqual(decision['tradeoff'], 'Fewer ready-made components')
        self.assertEqual(decision['evidence'], ['C1'])
        self.assertTrue(decision['contract_hash'])
        self.assertEqual(self.call('decision', '--requirement', 'R1', '--actor', 'ai',
            '--choice', 'x', '--reason', 'y', '--evidence', 'unknown')[0], 2)
        self.assertEqual(len(read_json(self.root / '.harness/state.json')['decisions']), 1)

    def test_close_blocks_every_new_command(self):
        self.assertEqual(self.call('close')[0], 0)
        for command in ('spec', 'brief', 'git-check'):
            code, output = self.call(command)
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output)['phase'], 'closed')

    def test_git_query_error_does_not_return_success(self):
        with patch('hxkit.views.subprocess.run', side_effect=FileNotFoundError('git unavailable')):
            code, output = self.call('git-check')
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output)['status'], 'error')


if __name__ == '__main__':
    unittest.main()
