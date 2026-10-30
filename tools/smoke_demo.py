"""Exercise installation and synthetic tasks without modifying the examples."""
from __future__ import annotations

import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


KIT = Path(__file__).resolve().parents[1]


def run(hx, root, *args, expected=0, json_output=True):
    completed = subprocess.run([sys.executable, str(hx), '--root', str(root), *args],
        capture_output=True, text=True, timeout=60,
        env={k: os.environ[k] for k in ('PATH', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TMPDIR', 'SYSTEMROOT', 'WINDIR') if k in os.environ})
    if completed.returncode != expected:
        raise AssertionError(f'{args}: expected exit {expected}, got {completed.returncode}\n{completed.stdout}\n{completed.stderr}')
    return json.loads(completed.stdout) if json_output else completed.stdout


def prepare_synthetic_plan(hx, root):
    shutil.copyfile(root / 'contract.example.json', root / '.harness/contract.json')
    shutil.copyfile(root / 'plan.example.json', root / '.harness/plan.json')
    assert run(hx, root, 'plan')['plan_gate']['status'] == 'awaiting_approval'
    run(hx, root, 'check', expected=2)
    run(hx, root, 'plan-approve', '--actor', 'user',
        '--quote', 'Synthetic test fixture approval only',
        '--source', 'tools/smoke_demo.py:synthetic-fixture')


def main():
    parser = argparse.ArgumentParser(description='합성 과제로 하네스의 실제 동작을 확인합니다.')
    parser.add_argument('--reports', type=Path, help='명세와 설명 보기 예제를 저장할 디렉터리')
    args = parser.parse_args()
    if args.reports:
        args.reports.mkdir(parents=True, exist_ok=True)
        for name in ('sample-spec.md', 'sample-brief.md'):
            if (args.reports / name).exists():
                parser.error(f'기존 결과를 덮어쓰지 않습니다: {name}')
    started = time.monotonic()
    results = []
    with tempfile.TemporaryDirectory(prefix='hx-demo-') as directory:
        root = Path(directory) / 'csv'
        shutil.copytree(KIT / 'examples/csv-summary', root)
        (root / 'AGENTS.md').write_text('Preserve existing project instructions.\n')
        run(KIT / 'hx.py', root, 'install')
        assert (root / 'AGENTS.md').read_text() == 'Preserve existing project instructions.\n'
        hx = root / '.harness-kit/hx.py'
        run(hx, root, 'init')
        prepare_synthetic_plan(hx, root)
        state_before = (root / '.harness/state.json').read_bytes()
        spec = run(hx, root, 'spec', json_output=False)
        brief = run(hx, root, 'brief', json_output=False)
        assert 'R1' in spec and '미실행' in brief
        assert (root / '.harness/state.json').read_bytes() == state_before
        assert run(hx, root, 'git-check')['status'] == 'not_git_repository'
        checked = run(hx, root, 'check')
        frozen = run(hx, root, 'freeze')
        assert frozen['ready_for_candidate_review']
        source = root / 'solution.py'
        original = source.read_text()
        source.write_text(original + '\n# Simulate a source edit after verification.\n')
        stale = run(hx, root, 'freeze', expected=1)
        assert all(r['status'] == 'stale' for r in stale['requirements'])
        assert '`stale`' in run(hx, root, 'brief', json_output=False)
        source.write_text('raise RuntimeError("synthetic regression")\n')
        failed = run(hx, root, 'check', expected=1)
        assert any(c['status'] != 'passed' for c in failed['checks'])
        source.write_text(original)
        run(hx, root, 'check')
        run(hx, root, 'freeze')
        results.append({'example': 'csv-summary', 'checks_passed': len(checked['checks']),
            'installation_preserved_AGENTS': True, 'source_edit_became_stale': True,
            'regression_failed': True, 'restored_implementation_passed': True,
            'spec_and_brief_read_only': True, 'brief_detected_stale': True,
            'git_unavailable_repository_distinguished': True})

        root = Path(directory) / 'http'
        shutil.copytree(KIT / 'examples/http-service', root)
        hx = KIT / 'hx.py'
        run(hx, root, 'init')
        prepare_synthetic_plan(hx, root)
        checked = run(hx, root, 'check')
        frozen = run(hx, root, 'freeze', expected=1)
        assert frozen['automatic_checks_passed']
        assert frozen['requires_manual_review'] == ['R3']
        assert not frozen['ready_for_candidate_review']
        results.append({'example': 'http-service', 'checks_passed': len(checked['checks']),
            'real_local_HTTP_requests': True, 'manual_UI_confirmation': 'not_performed',
            'manual_requirement_remains_pending': True})

        root = Path(directory) / 'orders'
        shutil.copytree(KIT / 'examples/delayed-orders', root)
        run(hx, root, 'init')
        prepare_synthetic_plan(hx, root)
        actual = subprocess.run([sys.executable, str(root / 'solution.py')],
            cwd=root, capture_output=True, text=True, check=True, timeout=10)
        expected = {'counts': {'001': 2, '1': 1}, 'excluded_rows': 4, 'duplicate_rows': 1}
        assert json.loads(actual.stdout) == expected
        checked = run(hx, root, 'check')
        run(hx, root, 'decision', '--requirement', 'R1', '--actor', 'ai',
            '--choice', 'CSV를 원본 문자열로 읽는 구현을 사용합니다.',
            '--reason', '고객 ID 001과 1을 구분하라는 합성 과제의 원문을 따릅니다.',
            '--alternative', 'ID를 정수로 변환하는 방법은 원문의 문자열 보존 조건과 맞지 않습니다.',
            '--tradeoff', '숫자 크기 순서가 아닌 원문이 요구한 문자열 순서로 정렬합니다.',
            '--evidence', 'C1')
        spec = run(hx, root, 'spec', json_output=False)
        brief = run(hx, root, 'brief', json_output=False)
        assert 'AI 제안 기록' in brief and '선택 비용' in brief
        if args.reports:
            prefix = '> 합성 예제의 실제 실행 기록으로 생성했습니다. 개인 경로는 표시용 이름으로 치환했습니다.\n\n'
            for name, text in [('sample-spec.md', spec), ('sample-brief.md', brief)]:
                text = text.replace(str(KIT), '<HARNESS>').replace(str(root), '<EXAMPLE_WORKSPACE>').replace(sys.executable, '<PYTHON>')
                (args.reports / name).write_text(prefix + text, encoding='utf-8')
        assert run(hx, root, 'freeze')['ready_for_candidate_review']
        results.append({'example': 'delayed-orders', 'checks_passed': len(checked['checks']),
            'independent_task_output_matched': True, 'decision_and_brief_connected': True, 'actual': expected})
    print(json.dumps({'synthetic_examples_only': True, 'python': sys.version.split()[0],
        'duration_seconds': round(time.monotonic() - started, 3), 'results': results},
        ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
