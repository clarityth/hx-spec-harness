"""Synthetic fixtures exercise the plan gate without claiming user identity."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from hxkit.cli import main
from hxkit.core import atomic_json, read_json


class PlanGateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        (self.root / 'TASK.md').write_text('Return five.', encoding='utf-8')
        self.assertEqual(self.cli('init')[0], 0)
        self.contract = {'schema_version': 1, 'title': 'Synthetic fixture',
            'requirements': [{'id': 'R1', 'description': 'Return five',
                'source': {'path': 'TASK.md', 'quote': 'Return five.'},
                'expected': 'JSON 5', 'verification': 'behavior',
                'implementation': ['app.py'], 'checks': ['C1']}],
            'checks': [{'id': 'C1', 'kind': 'json', 'tracked_paths': ['app.py'],
                'argv': ['{python}', 'app.py'], 'expected': 5, 'timeout_seconds': 3}],
            'deliverables': ['app.py']}
        self.plan = {'schema_version': 1, 'goal': 'Return five',
            'scope': 'Synthetic local fixture', 'acceptance': ['JSON 5'],
            'steps': [{'description': 'Implement and verify R1',
                       'requirements': ['R1'], 'checks': ['C1']}], 'questions': []}
        self.write_contract_plan()

    def cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['--root', str(self.root), *args])
        return code, json.loads(output.getvalue())

    def write_contract_plan(self):
        atomic_json(self.root / '.harness/contract.json', self.contract)
        atomic_json(self.root / '.harness/plan.json', self.plan)

    def approve_fixture(self):
        return self.cli('plan-approve', '--actor', 'user',
                        '--quote', 'Synthetic test fixture approval only',
                        '--source', 'tests/test_plan_gate.py:synthetic-fixture')

    def test_unapproved_check_does_not_run_or_write_evidence(self):
        state_path = self.root / '.harness/state.json'
        before = state_path.read_bytes()
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'awaiting_approval')
        self.assertEqual(self.cli('check')[0], 2)
        self.assertEqual(before, state_path.read_bytes())
        self.assertFalse((self.root / '.harness/evidence').exists())
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'plan_pending')
        code, frozen = self.cli('freeze')
        self.assertEqual(code, 1)
        self.assertFalse(frozen['ready_for_candidate_review'])
        self.assertFalse(frozen['automatic_checks_passed'])
        self.assertEqual(self.cli('decision', '--requirement', 'R1', '--actor', 'ai',
                                  '--choice', 'Use Python', '--reason', 'It is available')[0], 0)
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'awaiting_approval')

    def test_open_question_blocks_approval_until_answered(self):
        self.plan['questions'] = [{'id': 'Q1', 'question': 'Which output?',
            'impact': 'Changes the result', 'options': ['JSON', 'text'], 'status': 'open'}]
        self.write_contract_plan()
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'questions_open')
        self.assertEqual(self.approve_fixture()[0], 2)
        self.plan['questions'][0].update(status='answered', resolution='JSON',
                                         response_source='synthetic fixture response')
        self.write_contract_plan()
        self.assertEqual(self.approve_fixture()[0], 0)
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'approved')
        approval = read_json(self.root / '.harness/state.json')['plan_approval']
        self.assertEqual(approval['verification'], 'unverified_local_user_report')

    def test_approval_command_requires_user_actor_quote_and_source(self):
        entry = Path(__file__).resolve().parents[1] / 'hx.py'
        invalid = [
            ('--actor', 'ai', '--quote', 'yes', '--source', 'fixture'),
            ('--actor', 'user', '--source', 'fixture'),
            ('--actor', 'user', '--quote', 'yes'),
        ]
        for args in invalid:
            with self.subTest(args=args):
                done = subprocess.run([sys.executable, str(entry), '--root', str(self.root),
                                       'plan-approve', *args], capture_output=True, timeout=5)
                self.assertEqual(done.returncode, 2)
                self.assertNotIn('plan_approval', read_json(self.root / '.harness/state.json'))

    def test_future_implementation_file_may_be_missing_during_approval(self):
        self.assertFalse((self.root / 'app.py').exists())
        self.assertEqual(self.approve_fixture()[0], 0)
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'approved')
        self.assertEqual(self.cli('check')[0], 1)
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')

    def test_plan_change_requires_reapproval_and_new_execution(self):
        (self.root / 'app.py').write_text('print(5)\n', encoding='utf-8')
        self.assertEqual(self.approve_fixture()[0], 0)
        self.assertEqual(self.cli('check')[0], 0)
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'passed')
        self.plan['scope'] = 'Synthetic fixture with updated explanation'
        self.write_contract_plan()
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'stale')
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'approval_stale')
        self.assertEqual(self.cli('check')[0], 2)
        self.assertFalse(self.cli('freeze')[1]['ready_for_candidate_review'])
        self.assertEqual(self.approve_fixture()[0], 0)
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'stale')
        self.assertEqual(self.cli('check')[0], 0)
        self.assertEqual(self.cli('status')[1]['requirements'][0]['status'], 'passed')

    def test_plan_change_during_check_fails_and_stops_following_commands(self):
        (self.root / 'app.py').write_text(
            'import json\nfrom pathlib import Path\n'
            'p = Path(".harness/plan.json")\n'
            'data = json.loads(p.read_text())\n'
            'data["scope"] = "changed during execution"\n'
            'p.write_text(json.dumps(data))\nprint(5)\n', encoding='utf-8')
        (self.root / 'next.py').write_text(
            'from pathlib import Path\nPath("second-ran.txt").write_text("ran")\nprint(5)\n',
            encoding='utf-8')
        self.contract['checks'].append({'id': 'C2', 'kind': 'json',
            'tracked_paths': ['next.py'], 'argv': ['{python}', 'next.py'],
            'expected': 5, 'timeout_seconds': 3})
        self.contract['requirements'][0]['checks'].append('C2')
        self.plan['steps'][0]['checks'].append('C2')
        self.write_contract_plan()
        self.assertEqual(self.approve_fixture()[0], 0)
        code, report = self.cli('check')
        self.assertEqual(code, 1)
        self.assertEqual(len(report['checks']), 1)
        self.assertEqual(report['checks'][0]['status'], 'failed')
        self.assertFalse((self.root / 'second-ran.txt').exists())
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'stale')

    def test_contract_and_source_changes_invalidate_approval(self):
        self.assertEqual(self.approve_fixture()[0], 0)
        self.contract['requirements'][0]['expected'] = 'JSON number five'
        self.write_contract_plan()
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'stale')
        self.contract['requirements'][0]['expected'] = 'JSON 5'
        self.write_contract_plan()
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'approved')
        (self.root / 'TASK.md').write_text('Return five. Include a newline.', encoding='utf-8')
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'stale')

    def test_invalid_revised_plan_cannot_be_reapproved(self):
        self.assertEqual(self.approve_fixture()[0], 0)
        self.plan['scope'] = ''
        self.write_contract_plan()
        self.assertEqual(self.cli('plan')[1]['plan_gate']['status'], 'stale')
        self.assertEqual(self.approve_fixture()[0], 2)
        self.assertEqual(self.cli('check')[0], 2)

    def test_legacy_state_without_plan_never_gains_approval(self):
        (self.root / '.harness/plan.json').unlink()
        code, report = self.cli('plan')
        self.assertEqual(code, 0)
        self.assertIsNone(report['plan'])
        self.assertEqual(report['plan_gate']['status'], 'invalid_plan')
        self.assertEqual(self.cli('check')[0], 2)

    def test_manual_observation_is_blocked_before_approval(self):
        self.contract['requirements'].append({'id': 'R2', 'description': 'View output',
            'source': {'path': 'TASK.md', 'quote': 'Return five.'},
            'expected': 'Candidate sees five', 'verification': 'manual',
            'implementation': ['app.py'], 'checks': []})
        self.plan['steps'].append({'description': 'Observe R2', 'requirements': ['R2'], 'checks': []})
        self.write_contract_plan()
        self.assertEqual(self.cli('observe', '--requirement', 'R2', '--result', 'passed',
                                  '--note', 'Synthetic report')[0], 2)
        self.assertEqual(read_json(self.root / '.harness/state.json')['observations'], [])


if __name__ == '__main__':
    unittest.main()
