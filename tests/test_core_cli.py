import contextlib
from datetime import datetime
import io
import json
import re
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from hxkit.cli import main
from hxkit.core import atomic_json, digest, read_json, safe_path, snapshot, validate


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'TASK.md').write_text('Return the sum. Display the result. Build successfully.')
        (self.root / 'app.py').write_text('import json\nprint(json.dumps({"sum": 5}))\n')
        (self.root / 'handoff.md').write_text('Synthetic fixture. Run app.py to return sum 5.\n')
        code, _ = self.cli('init')
        self.assertEqual(code, 0)
        self.contract = {
            'schema_version': 1, 'title': 'Synthetic addition fixture',
            'requirements': [{'id': 'R1', 'description': 'Return the sum',
                'source': {'path': 'TASK.md', 'quote': 'Return the sum.'},
                'expected': 'The result is 5', 'verification': 'behavior',
                'implementation': ['app.py'], 'checks': ['C1']}],
            'checks': [{'id': 'C1', 'kind': 'json', 'tracked_paths': ['app.py'],
                'argv': ['{python}', 'app.py'], 'expected': {'sum': 5}, 'timeout_seconds': 3}],
            'deliverables': ['app.py']}
        self.write_contract()

    def cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['--root', str(self.root), *args])
        return code, json.loads(output.getvalue())

    def write_contract(self):
        atomic_json(self.root / '.harness/contract.json', self.contract)
        plan = {'schema_version': 1, 'goal': 'Synthetic test fixture',
                'scope': 'Only this temporary test project',
                'acceptance': [r['expected'] for r in self.contract['requirements']],
                'steps': [{'description': r['description'], 'requirements': [r['id']],
                           'checks': r.get('checks', [])} for r in self.contract['requirements']],
                'questions': []}
        atomic_json(self.root / '.harness/plan.json', plan)
        self.cli('plan-approve', '--actor', 'user',
                 '--quote', 'Synthetic test fixture approval only',
                 '--source', 'tests/test_core_cli.py:synthetic-fixture')

    def test_custom_duration_supports_longer_projects_and_validates_bounds(self):
        for minutes, expected_code in ((240, 0), (0, 2), (10081, 2)):
            project = self.root / f'duration-{minutes}'
            project.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(['--root', str(project), 'init', '--minutes', str(minutes)])
            self.assertEqual(code, expected_code)
            if code == 0:
                state = read_json(project / '.harness/state.json')
                duration = datetime.fromisoformat(state['deadline']) - datetime.fromisoformat(state['started_at'])
                self.assertAlmostEqual(duration.total_seconds(), 240 * 60, delta=1)
            else:
                self.assertFalse((project / '.harness').exists())

    def test_fresh_pass_then_code_change_and_rerun_failure(self):
        self.assertEqual(self.cli('freeze')[0], 1)
        self.assertEqual(self.cli('check')[0], 0)
        pointer = read_json(self.root / '.harness/state.json')['latest_checks']['C1']
        record = read_json(self.root / pointer['path'])
        self.assertIn('app.py', record['result']['command'])
        self.assertTrue(self.cli('freeze')[1]['ready_for_candidate_review'])
        (self.root / 'app.py').write_text('print("{\\"sum\\": 6}")\n')
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')
        self.assertEqual(self.cli('check')[0], 1)
        self.assertEqual(self.cli('freeze')[0], 1)

    def test_freeze_requires_nonempty_handoff_without_claiming_content_accuracy(self):
        self.assertEqual(self.cli('check')[0], 0)
        path = self.root / 'handoff.md'
        path.unlink()
        code, report = self.cli('freeze')
        self.assertEqual(code, 1)
        self.assertTrue(report['automatic_checks_passed'])
        self.assertEqual(report['handoff']['status'], 'missing')
        path.write_text(' \n\t')
        self.assertEqual(self.cli('freeze')[1]['handoff']['status'], 'empty')
        self.assertEqual(self.cli('freeze')[0], 1)
        path.write_text('Synthetic handoff: run app.py; expected sum is 5.')
        code, report = self.cli('freeze')
        self.assertEqual(code, 0)
        self.assertEqual(report['handoff']['content_accuracy'], 'not_verified')
        self.assertNotIn('handoff.md', report['submission_files'])
        self.assertEqual(report['handoff']['sha256'], digest(path))
        self.contract['deliverables'].append('handoff.md')
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 0)
        self.assertIn('handoff.md', self.cli('freeze')[1]['submission_files'])

    def test_exit_zero_is_not_behavior_and_false_json_fails(self):
        self.contract['checks'][0]['kind'] = 'command'
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 2)
        self.contract['checks'][0]['kind'] = 'json'
        self.contract['checks'][0]['expected'] = {'sum': True}
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 1)

    def test_empty_contract_unknown_check_and_wrong_quote(self):
        self.contract['requirements'] = []
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 2)
        self.assertEqual(self.cli('freeze')[0], 1)

    def test_declared_implementation_is_always_tracked(self):
        (self.root / 'helper.txt').write_text('stable')
        self.contract['checks'][0]['tracked_paths'] = ['helper.txt']
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 0)
        (self.root / 'app.py').write_text('print("{}")')
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')

    def test_tests_directory_addition_invalidates_pass(self):
        (self.root / 'tests').mkdir()
        (self.root / 'tests/a.txt').write_text('test definition')
        self.contract['checks'][0]['tracked_paths'].append('tests')
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 0)
        (self.root / 'tests/b.txt').write_text('new test definition')
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')

    def test_evidence_modification_is_detected(self):
        self.assertEqual(self.cli('check')[0], 0)
        state = read_json(self.root / '.harness/state.json')
        path = self.root / state['latest_checks']['C1']['path']
        path.write_text('{}')
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')

    def test_mutation_during_check_fails(self):
        self.contract['checks'][0]['argv'] = ['{python}', '-c',
            'from pathlib import Path; Path("app.py").write_text("changed"); print("{\\"sum\\":5}")']
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 1)
        self.assertEqual(self.cli('freeze')[0], 1)

    def test_manual_report_remains_separate_and_stales(self):
        self.contract['requirements'].append({'id': 'R2', 'description': 'Display',
            'source': {'path': 'TASK.md', 'quote': 'Display the result.'},
            'expected': 'Candidate sees 5', 'verification': 'manual',
            'implementation': ['app.py'], 'checks': []})
        self.write_contract()
        self.cli('check')
        self.assertEqual(self.cli('freeze')[0], 1)
        self.assertEqual(self.cli('observe', '--requirement', 'R2', '--result', 'passed',
                                  '--note', 'Candidate reported seeing 5')[0], 0)
        report = self.cli('freeze')
        self.assertEqual(report[0], 1)
        self.assertTrue(report[1]['automatic_checks_passed'])
        self.assertEqual(report[1]['requires_manual_review'], ['R2'])
        self.assertEqual(report[1]['requirements'][1]['status'], 'reported_passed')
        self.assertEqual(report[1]['requirements'][1]['evidence_source'], 'unverified_self_report')
        state = read_json(self.root / '.harness/state.json')
        self.assertEqual(state['observations'][0]['actor'], 'candidate-reported')
        (self.root / 'app.py').write_text('changed')
        self.assertEqual(self.cli('status')[1]['requirements'][1]['status'], 'stale')

    def test_unittest_directory_is_automatically_tracked(self):
        (self.root / 'tests').mkdir()
        test = self.root / 'tests/test_app.py'
        test.write_text('import unittest\nclass T(unittest.TestCase):\n def test_sum(self): self.assertTrue(True)\n')
        self.contract['checks'][0] = {'id': 'C1', 'kind': 'unittest', 'test_dir': 'tests',
            'tests': ['test_app.T.test_sum'], 'tracked_paths': ['app.py'], 'timeout_seconds': 3}
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 0)
        test.write_text('import unittest\nclass T(unittest.TestCase):\n def test_sum(self): self.fail("changed")\n')
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')
        self.assertEqual(self.cli('freeze')[0], 1)

    def test_partial_run_preserves_completed_failure_and_records_missing_input(self):
        (self.root / 'helper.txt').write_text('input')
        second = dict(self.contract['checks'][0], id='C2', tracked_paths=['helper.txt'])
        self.contract['checks'].append(second)
        self.contract['requirements'][0]['checks'].append('C2')
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 0)
        (self.root / 'app.py').write_text('print("{}")')
        (self.root / 'helper.txt').unlink()
        code, report = self.cli('check')
        self.assertEqual(code, 1)
        self.assertEqual([r['status'] for r in report['checks']], ['failed', 'error'])
        state = read_json(self.root / '.harness/state.json')
        latest = read_json(self.root / state['latest_checks']['C1']['path'])
        self.assertEqual(latest['result']['status'], 'failed')

    def test_install_parent_collision_makes_no_partial_copy(self):
        (self.root / '.agents').mkdir()
        (self.root / '.agents/skills').write_text('preserve me')
        code, report = self.cli('install')
        self.assertEqual(code, 2)
        self.assertIn('parent is not a directory', report['error'])
        self.assertFalse((self.root / '.harness-kit').exists())
        self.assertFalse((self.root / 'HARNESS.md').exists())
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_install_preserves_agents_and_runs_installed_copy(self):
        agents = self.root / 'AGENTS.md'
        agents.write_bytes(b'Existing project instructions\n')
        before = agents.read_bytes()
        code, report = self.cli('install')
        self.assertEqual(code, 0)
        self.assertEqual(agents.read_bytes(), before)
        self.assertNotIn('AGENTS.md', report['created'])
        self.assertIn('기존 AGENTS 보존', report['next'])
        self.assertIn('HARNESS.md', report['next'])
        self.assertIn('GUARDRAILS', report['next'])
        self.assertTrue((self.root / '.harness-kit/START_HERE.md').is_file())
        self.assertTrue((self.root / '.harness-kit/examples/delayed-orders/TASK.md').is_file())
        self.assertTrue((self.root / '.harness-kit/skills/hx-explain/SKILL.md').is_file())
        self.assertEqual(self.cli('install')[0], 2)
        completed = subprocess.run([sys.executable, str(self.root / '.harness-kit/hx.py'),
            '--root', str(self.root), 'status'], capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['requirements'][0]['status'], 'not_run')

    def test_install_creates_entry_agents_with_resolving_links(self):
        readme = self.root / 'README.md'
        readme.write_bytes(b'Existing task instructions\n')
        readme_before = readme.read_bytes()
        code, report = self.cli('install')
        self.assertEqual(code, 0)
        self.assertEqual(readme.read_bytes(), readme_before)
        agents = self.root / 'AGENTS.md'
        self.assertEqual(agents.read_bytes(),
                         (self.root / '.harness-kit/templates/entry-AGENTS.md').read_bytes())
        self.assertIn('AGENTS.md', report['created'])
        links = re.findall(r'\]\(([^)]+)\)', agents.read_text(encoding='utf-8'))
        self.assertTrue(links)
        for link in links:
            target = (agents.parent / link).resolve()
            self.assertTrue(target.is_relative_to(self.root.resolve()), link)
            self.assertTrue(target.is_file(), link)

    def test_install_rejects_agents_symlink_without_partial_copy(self):
        agents = self.root / 'AGENTS.md'
        agents.symlink_to(self.root / 'app.py')
        before = (self.root / 'app.py').read_bytes()
        code, report = self.cli('install')
        self.assertEqual(code, 2)
        self.assertIn('symlink', report['error'])
        self.assertTrue(agents.is_symlink())
        self.assertEqual((self.root / 'app.py').read_bytes(), before)
        self.assertFalse((self.root / '.harness-kit').exists())
        self.assertFalse((self.root / 'HARNESS.md').exists())

    def test_installed_entry_guide_links_resolve_inside_project(self):
        self.assertEqual(self.cli('install')[0], 0)
        guide = self.root / 'HARNESS.md'
        links = re.findall(r'\]\(([^)]+)\)', guide.read_text())
        self.assertTrue(links)
        for link in links:
            target = (guide.parent / link).resolve()
            self.assertTrue(target.is_relative_to(self.root.resolve()), link)
            self.assertTrue(target.is_file(), link)

    def test_init_collision_preserves_state_and_close_stops_assistance(self):
        p = self.root / '.harness/state.json'
        before = p.read_bytes()
        self.assertEqual(self.cli('init')[0], 2)
        self.assertEqual(before, p.read_bytes())
        self.assertEqual(self.cli('close')[0], 0)
        self.assertEqual(self.cli('status')[1]['phase'], 'closed')
        self.assertEqual(self.cli('check')[0], 2)
        self.assertEqual(self.cli('freeze')[0], 2)

    def test_path_cas_and_lock_guards(self):
        with self.assertRaises(ValueError):
            safe_path(self.root, '../outside')
        (self.root / 'link').symlink_to(self.root / 'app.py')
        with self.assertRaises(ValueError):
            safe_path(self.root, 'link')
        path = self.root / '.harness/state.json'
        baseline = digest(path)
        state = read_json(path)
        state['next'] = 'external edit'
        atomic_json(path, state)
        with self.assertRaises(ValueError):
            atomic_json(path, {}, baseline)
        (self.root / '.harness/write.lock').write_text('busy')
        self.assertEqual(self.cli('check')[0], 2)

    def test_quote_and_source_changes_are_not_silently_accepted(self):
        self.contract['requirements'][0]['source']['quote'] = 'invented quote'
        self.write_contract()
        self.assertEqual(self.cli('check')[0], 2)

    def test_required_deliverable_missing(self):
        self.contract['deliverables'].append('missing.csv')
        self.write_contract()
        self.cli('check')
        self.assertEqual(self.cli('freeze')[0], 1)


if __name__ == '__main__':
    unittest.main()
