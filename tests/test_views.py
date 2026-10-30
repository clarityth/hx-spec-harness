"""Read-only reports preserve evidence and actor boundaries."""

from pathlib import Path
import subprocess
import tempfile
import unittest

from hxkit import core
from hxkit.runner import execute
from hxkit.views import git_report, render_brief, render_spec


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'TASK.md').write_text('Return the sum. Display it.', encoding='utf-8')
        (self.root / 'app.py').write_text('print("{\\"sum\\": 5}")\n', encoding='utf-8')
        self.contract = {
            'schema_version': 1, 'title': '덧셈 과제',
            'requirements': [
                {'id': 'R1', 'description': '합계를 반환합니다',
                 'source': {'path': 'TASK.md', 'quote': 'Return the sum.'},
                 'expected': 'sum 값이 5입니다', 'verification': 'behavior',
                 'implementation': ['app.py'], 'checks': ['C1']},
                {'id': 'R2', 'description': '화면을 확인합니다',
                 'source': {'path': 'TASK.md', 'quote': 'Display it.'},
                 'expected': '사용자가 화면을 확인합니다', 'verification': 'manual',
                 'implementation': ['app.py'], 'checks': []}],
            'checks': [{'id': 'C1', 'kind': 'json', 'tracked_paths': ['app.py'],
                        'argv': ['{python}', 'app.py'], 'expected': {'sum': 5},
                        'timeout_seconds': 3}],
            'deliverables': ['app.py']}
        self.state = {'schema_version': 1, 'phase': 'framing', 'next': 'app.py를 확인합니다.',
                      'latest_checks': {}, 'observations': [], 'decisions': []}
        self.approve_synthetic_plan()

    def approve_synthetic_plan(self):
        directory = self.root / '.harness'
        directory.mkdir(exist_ok=True)
        plan = {'schema_version': 1, 'goal': 'Synthetic fixture', 'scope': 'Temporary tests',
                'acceptance': [r['expected'] for r in self.contract['requirements']],
                'steps': [{'description': r['description'], 'requirements': [r['id']],
                           'checks': r.get('checks', [])} for r in self.contract['requirements']],
                'questions': []}
        core.atomic_json(directory / 'plan.json', plan)
        sources = sorted({r['source']['path'] for r in self.contract['requirements']})
        self.state['plan_approval'] = {'actor': 'user',
            'quote': 'Synthetic test fixture approval only',
            'source': 'tests/test_views.py:synthetic-fixture',
            'plan_hash': core.fingerprint(plan), 'contract_hash': core.fingerprint(self.contract),
            'source_snapshot': core.snapshot(self.root, sources)}

    def record_check(self):
        self.approve_synthetic_plan()
        check = self.contract['checks'][0]
        directory = self.root / '.harness/evidence/run1'
        directory.mkdir(parents=True, exist_ok=True)
        scope = core.evidence_scope(self.contract, check)
        snap = core.snapshot(self.root, scope)
        result = execute(self.root, check, directory)
        self.assertEqual(result['status'], 'passed')
        record = {'contract_hash': core.fingerprint(self.contract),
                  'plan_hash': self.state['plan_approval']['plan_hash'],
                  'check_hash': core.fingerprint(check), 'kind': check['kind'],
                  'scope': scope, 'snapshot_after': snap, 'stable': True,
                  'result': result}
        manifest = directory / 'manifest.json'
        core.atomic_json(manifest, record)
        self.state['latest_checks']['C1'] = {
            'path': manifest.relative_to(self.root).as_posix(), 'sha256': core.digest(manifest)}
        return manifest

    def test_spec_links_source_expected_check_and_next_without_writing(self):
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        rendered = render_spec(self.root, self.contract, self.state)
        self.assertIn('Return the sum.', rendered)
        self.assertIn('sum 값이 5입니다', rendered)
        self.assertIn('`app.py`', rendered)
        self.assertIn('`C1`', rendered)
        self.assertIn('app.py를 확인합니다.', rendered)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_spec_masks_known_secret_pattern_in_command(self):
        self.contract['checks'][0]['argv'].append('password=synthetic-example')
        rendered = render_spec(self.root, self.contract, self.state)
        self.assertNotIn('synthetic-example', rendered)
        self.assertIn('password=[REDACTED]', rendered)

    def test_brief_keeps_pending_manual_and_ai_actor_distinct(self):
        self.contract['requirements'][1].pop('checks')
        self.approve_synthetic_plan()
        self.state['decisions'] = [
            {'requirement': 'R1', 'actor': 'ai', 'choice': '방식 A', 'reason': '간단합니다',
             'alternatives': ['방식 B'], 'tradeoff': '속도 비용', 'evidence': ['C1'],
             'contract_hash': 'old-contract-hash'},
            {'requirement': 'R2', 'actor': 'candidate', 'choice': '화면 확인', 'reason': '직접 봤습니다',
             'contract_hash': core.fingerprint(self.contract)}]
        self.assertIn('자동 검사가 없습니다', render_spec(self.root, self.contract, self.state))
        text = render_brief(self.root, self.contract, self.state)
        self.assertIn('미실행 (`not_run`)', text)
        self.assertIn('AI 제안 기록', text)
        self.assertIn('사용자 자기보고 기록(인증 안 됨)', text)
        self.assertIn('방식 B', text)
        self.assertIn('속도 비용', text)
        self.assertIn('과거 명세의 판단 기록', text)
        self.assertIn('인증하지 않습니다', text)
        self.assertNotIn('실제 실행 명령: `{python} app.py`', text)

    def test_brief_fresh_stale_and_tampered_manifest(self):
        manifest = self.record_check()
        fresh = render_brief(self.root, self.contract, self.state)
        self.assertIn('통과 (`passed`)', fresh)
        self.assertIn('실제 실행 명령:', fresh)
        self.assertIn('실제 JSON 비교: 실행함', fresh)
        self.assertNotIn('실행한 테스트: 0건', fresh)
        self.assertIn('로그 경로: `.harness/evidence/run1/C1.log`', fresh)
        manifest.write_text(manifest.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        self.assertIn('증거 무효 (`stale`)', render_brief(self.root, self.contract, self.state))
        self.record_check_again_after_tamper()
        (self.root / 'app.py').write_text('print("{}")\n', encoding='utf-8')
        self.assertIn('증거 무효 (`stale`)', render_brief(self.root, self.contract, self.state))

    def test_brief_names_unittest_count_and_command_process(self):
        (self.root / 'tests').mkdir()
        (self.root / 'tests/test_app.py').write_text(
            'import unittest\nclass Cases(unittest.TestCase):\n'
            ' def test_ok(self): self.assertTrue(True)\n', encoding='utf-8')
        self.contract['checks'][0] = {'id': 'C1', 'kind': 'unittest', 'tracked_paths': ['app.py'],
                                      'test_dir': 'tests', 'tests': ['test_app.Cases.test_ok'],
                                      'timeout_seconds': 3}
        self.record_check()
        unit = render_brief(self.root, self.contract, self.state)
        self.assertIn('실행한 테스트: 1건', unit)
        self.assertNotIn('실제 JSON 비교', unit)

        self.state['latest_checks'] = {}
        self.contract['requirements'][0]['verification'] = 'process'
        self.contract['checks'][0] = {'id': 'C1', 'kind': 'command', 'tracked_paths': ['app.py'],
                                      'argv': ['{python}', 'app.py'], 'timeout_seconds': 3}
        (self.root / '.harness/evidence/run1/manifest.json').unlink()
        self.record_check()
        command = render_brief(self.root, self.contract, self.state)
        self.assertIn('프로세스 검사: 종료 코드 0', command)
        self.assertNotIn('실행한 테스트:', command)
        self.assertNotIn('실제 JSON 비교', command)

    def record_check_again_after_tamper(self):
        # Preserve a fresh pointer without reusing the previous manifest filename.
        manifest = self.root / self.state['latest_checks']['C1']['path']
        self.state['latest_checks']['C1']['sha256'] = core.digest(manifest)

    def test_manual_report_is_not_certification(self):
        scope = ['TASK.md', 'app.py']
        self.state['observations'] = [{
            'requirement': 'R2', 'status': 'passed', 'note': '사용자 자기보고',
            'contract_hash': core.fingerprint(self.contract), 'scope': scope,
            'plan_hash': self.state['plan_approval']['plan_hash'],
            'snapshot': core.snapshot(self.root, scope)}]
        text = render_brief(self.root, self.contract, self.state)
        self.assertIn('사용자 자기보고 통과(인증 안 됨)', text)
        (self.root / 'app.py').write_text('print("{}")\n', encoding='utf-8')
        self.assertIn('증거 무효 (`stale`)', render_brief(self.root, self.contract, self.state))

    def test_closed_task_blocks_both_renderers(self):
        self.state['phase'] = 'closed'
        for render in (render_spec, render_brief):
            with self.subTest(render=render.__name__), self.assertRaises(ValueError):
                render(self.root, self.contract, self.state)


class GitReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))

    def test_non_repository_has_distinct_status(self):
        report = git_report(self.root)
        self.assertEqual(report['status'], 'not_git_repository')
        self.assertIsNone(report['head'])

    def test_local_status_handles_korean_rename_and_does_not_write(self):
        self.git('init', '-q')
        (self.root / '기존.txt').write_text('old\n', encoding='utf-8')
        (self.root / '수정.txt').write_text('clean\n', encoding='utf-8')
        self.git('add', '기존.txt', '수정.txt')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'initial')
        self.git('mv', '기존.txt', '이름변경.txt')
        (self.root / '수정.txt').write_text('bad space  \n', encoding='utf-8')
        (self.root / '새파일.txt').write_text('new\n', encoding='utf-8')
        index = self.root / '.git/index'
        index_before = index.read_bytes()
        files_before = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        report = git_report(self.root)
        self.assertEqual(report['status'], 'ok', report.get('error'))
        self.assertEqual(len(report['head']), 40)
        self.assertTrue(report['branch'])
        self.assertEqual(report['staged'][0]['path'], '이름변경.txt')
        self.assertEqual(report['staged'][0]['original_path'], '기존.txt')
        self.assertEqual(report['unstaged'][0]['path'], '수정.txt')
        self.assertEqual(report['untracked'][0]['path'], '새파일.txt')
        self.assertTrue(report['whitespace_errors'])
        self.assertEqual(index_before, index.read_bytes())
        self.assertEqual(files_before, {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()})

    def test_merge_conflict_is_reported(self):
        self.git('init', '-q')
        initial = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], cwd=self.root,
                                 capture_output=True, check=True, timeout=5).stdout.decode().strip()
        target = self.root / '충돌.txt'
        target.write_text('base\n', encoding='utf-8')
        self.git('add', '충돌.txt')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'base')
        self.git('checkout', '-qb', 'side')
        target.write_text('side\n', encoding='utf-8')
        self.git('add', '충돌.txt')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'side')
        self.git('checkout', '-q', initial)
        target.write_text('main\n', encoding='utf-8')
        self.git('add', '충돌.txt')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'main')
        merge = subprocess.run(['git', 'merge', 'side'], cwd=self.root, capture_output=True, timeout=5)
        self.assertNotEqual(merge.returncode, 0)
        report = git_report(self.root)
        self.assertEqual(report['status'], 'ok', report.get('error'))
        self.assertEqual(report['conflicts'][0]['path'], '충돌.txt')
        self.assertEqual(report['conflicts'][0]['code'], 'UU')

    def test_subdirectory_scope_excludes_outside_changes(self):
        self.git('init', '-q')
        task = self.root / 'task'
        task.mkdir()
        (task / 'inside.txt').write_text('base\n', encoding='utf-8')
        (self.root / 'outside.txt').write_text('base\n', encoding='utf-8')
        self.git('add', 'task/inside.txt', 'outside.txt')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'base')
        (task / 'inside.txt').write_text('inside  \n', encoding='utf-8')
        (self.root / 'outside.txt').write_text('outside  \n', encoding='utf-8')
        (task / '새파일.txt').write_text('new\n', encoding='utf-8')
        (self.root / '밖.txt').write_text('new\n', encoding='utf-8')
        report = git_report(task)
        self.assertEqual(report['status'], 'ok', report.get('error'))
        self.assertEqual(len(report['unstaged']), 1)
        self.assertTrue(report['unstaged'][0]['path'].endswith('inside.txt'))
        self.assertEqual(len(report['untracked']), 1)
        self.assertTrue(report['untracked'][0]['path'].endswith('새파일.txt'))
        self.assertTrue(report['whitespace_errors'])
        self.assertTrue(all('outside.txt' not in line for line in report['whitespace_errors']))
        self.git('add', 'task/inside.txt', 'outside.txt')
        staged = git_report(task)
        self.assertEqual(staged['status'], 'ok', staged.get('error'))
        self.assertEqual(len(staged['staged']), 1)
        self.assertTrue(staged['staged'][0]['path'].endswith('inside.txt'))
        self.assertTrue(all('outside.txt' not in line for line in staged['whitespace_errors']))


if __name__ == '__main__':
    unittest.main()
