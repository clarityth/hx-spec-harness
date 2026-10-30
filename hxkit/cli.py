"""Portable CLI. State lives in the task; the toolkit can live elsewhere."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

from . import __version__
from .core import (atomic_json, digest, evidence_scope, fingerprint, locked, now,
                   plan_gate, read_json, require_plan_approval, requirement_status,
                   safe_path, snapshot, validate, validate_plan)
from .data import profile, join_profile
from .runner import execute
from .release import release_files

TOOLKIT = Path(__file__).resolve().parents[1]


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def paths(root):
    return (safe_path(root, '.harness/contract.json'), safe_path(root, '.harness/state.json'))


def load(root):
    cp, sp = paths(root)
    contract, state = read_json(cp), read_json(sp)
    if not isinstance(state, dict) or state.get('schema_version') != 1:
        raise ValueError('invalid state schema')
    return contract, state


def ensure_open(state):
    if state.get('phase') == 'closed':
        raise ValueError('task is closed; no further AI-assisted work or explanation is permitted')


def initialize(root, minutes):
    directory = safe_path(root, '.harness', must_exist=False)
    if directory.exists():
        raise ValueError('.harness already exists; init never overwrites task state')
    if minutes < 1 or minutes > 10080:
        raise ValueError('duration must be between 1 and 10080 minutes (7 days)')
    directory.mkdir()
    contract = {'schema_version': 1, 'title': '', 'requirements': [], 'checks': [], 'deliverables': []}
    plan = {'schema_version': 1, 'goal': '', 'scope': '', 'acceptance': [],
            'steps': [], 'questions': []}
    state = {'schema_version': 1, 'started_at': now(),
             'deadline': (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat(),
             'phase': 'framing', 'next': '과제 원문을 읽고 contract.json과 plan.json을 작성합니다.',
             'decisions': [], 'observations': [], 'latest_checks': {}}
    atomic_json(directory / 'contract.json', contract)
    atomic_json(directory / 'plan.json', plan)
    atomic_json(directory / 'state.json', state)
    emit({'created': ['.harness/contract.json', '.harness/plan.json', '.harness/state.json'],
          'next': state['next'], 'note': '이 로컬 타이머는 작업 시간 참고용입니다. 실제 마감 시간을 별도로 확인합니다.'})
    return 0


def install(root, dry_run=False):
    runtime = safe_path(root, '.harness-kit', must_exist=False)
    # Validate the entire explicit release boundary before creating any target.
    declared = release_files(TOOLKIT)
    entry = next((src for src in declared
                  if src.relative_to(TOOLKIT).as_posix() == 'templates/entry-HARNESS.md'), None)
    agents_entry = next((src for src in declared
                         if src.relative_to(TOOLKIT).as_posix() == 'templates/entry-AGENTS.md'), None)
    agents = safe_path(root, 'AGENTS.md', must_exist=False)
    if agents.exists() and not agents.is_file():
        raise ValueError('install collision: AGENTS.md is not a file; no files copied')
    existing_agents = agents.exists()
    if runtime.exists():
        raise ValueError('install collision: .harness-kit; no files copied')
    targets = [(src, runtime / src.relative_to(TOOLKIT)) for src in declared]
    if agents_entry is not None and not existing_agents:
        targets.append((agents_entry, agents))
    for src in declared:
        relative = src.relative_to(TOOLKIT)
        if relative.as_posix() == 'HARNESS.md':
            targets.append((entry or src, root / 'HARNESS.md'))
        if len(relative.parts) >= 3 and relative.parts[0] == 'skills':
            targets.append((src, root / '.agents' / relative))
    for src, dst in targets:
        safe_path(root, dst.relative_to(root).as_posix(), must_exist=False)
        for parent in dst.parents:
            if parent == root:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError(f'install parent is not a directory: {parent.relative_to(root)}; no files copied')
        if dst.exists():
            raise ValueError(f'install collision: {dst.relative_to(root)}; no files copied')
    if dry_run:
        emit({'dry_run': True, 'would_create': [dst.relative_to(root).as_posix() for _, dst in targets],
              'existing_AGENTS': 'unchanged' if existing_agents else 'would_create' if agents_entry else 'not_in_manifest',
              'note': '읽기 전용 설치 계획입니다. 실제 설치 시 충돌과 경로를 다시 확인합니다.'})
        return 0
    created = []
    try:
        for src, dst in targets:
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open('xb') as output:
                output.write(src.read_bytes())
            created.append(dst.relative_to(root).as_posix())
    except OSError as exc:
        raise ValueError(f'install interrupted; created paths: {created}; {exc}') from exc
    if existing_agents:
        agents_status = 'unchanged'
        next_step = '기존 AGENTS 보존. Codex가 HARNESS.md 및 .harness-kit/GUARDRAILS.md를 직접 읽고 진행하세요. '
    elif agents_entry is not None:
        agents_status = 'created'
        next_step = '새 AGENTS.md와 HARNESS.md를 읽으세요. '
    else:
        agents_status = 'not_in_manifest'
        next_step = 'HARNESS.md를 읽으세요. '
    next_step += '스킬 자동 발견이 안 되면 SKILL.md를 직접 읽으세요.'
    emit({'created': created, 'existing_AGENTS': agents_status,
          'next': next_step,
          'initialize': 'python3 .harness-kit/hx.py --root . init'})
    return 0


def overview(root, contract, state):
    errors = []
    try:
        validate(contract, root)
        requirements = requirement_status(root, contract, state)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        errors.append(str(exc))
        requirements = []
    remaining = (datetime.fromisoformat(state['deadline']) - datetime.now(timezone.utc)).total_seconds()
    gate = plan_gate(root, contract, state)
    advice = ('설정한 작업 시간이 지났습니다. 현재 상태와 실제 마감 시간을 확인하세요.' if remaining <= 0
              else '새 기능을 늘리지 말고 현재 결과, 필수 파일과 실제 제출 절차를 확인하세요.' if remaining <= 10 * 60
              else '필수 검사를 마무리하고 인계 문서와 미확인을 정리하세요.' if remaining <= 30 * 60
              else '필수 기능과 검증을 진행하세요.' if gate['status'] == 'approved'
              else '계획과 미해결 질문을 확인하고 사용자에게 승인을 요청하세요.')
    mandatory = [r for r in requirements if r['mandatory']]
    statuses = {r['status'] for r in mandatory}
    if state.get('phase') == 'closed':
        recommended = '작업이 닫혔습니다. AI 작업을 재개하지 않습니다.'
    elif errors or gate['status'] != 'approved':
        recommended = '원문과 계획, 미해결 질문을 확인하고 필요한 명시적 승인을 받으세요.'
    elif 'reported_failed' in statuses:
        recommended = '사용자가 보고한 실패 동작과 조건을 확인하고 구현에서 원인을 조사하세요.'
    elif statuses & {'failed', 'error'}:
        recommended = '실패한 필수 검사의 입력과 로그를 확인하고 원인을 수정하세요.'
    elif statuses & {'stale', 'approval_stale'}:
        recommended = '변경된 파일과 근거를 확인하고 관련 검사를 다시 실행하세요.'
    elif any(r['verification'] != 'manual' and r['status'] != 'passed' for r in mandatory):
        recommended = '승인된 필수 동작을 구현하고 연결한 검사를 실행하세요.'
    elif any(r['verification'] == 'manual' for r in mandatory):
        recommended = '자동 검사 결과와 인계를 정리하고 사용자 직접 확인 항목을 안내하세요.'
    else:
        recommended = '인계 문서를 실제 코드와 대조하고 freeze로 제출 전 상태를 확인하세요.'
    if remaining > 30 * 60:
        advice = recommended
    return {'title': contract.get('title', ''), 'phase': state['phase'],
            'plan_gate': gate,
            'remaining_minutes': round(remaining / 60, 1),
            'time_advice': advice,
            'recommended_action': recommended,
            'next': recommended if state.get('next', '') == '과제 원문을 읽고 contract.json과 plan.json을 작성합니다.' else state.get('next', ''),
            'requirements': requirements,
            'contract_errors': errors, 'decisions': state.get('decisions', []),
            'evidence_limit': '명세 해석과 검사 연결의 타당성은 원문과 직접 대조해야 합니다.'}


def previous_run(root, contract, state, check_definition, gate, before, stable, result):
    pointer = state.get('latest_checks', {}).get(check_definition['id'])
    if not pointer:
        return {'status': 'no_previous_run'}
    try:
        path = safe_path(root, pointer['path'])
        if digest(path) != pointer['sha256']:
            raise ValueError('previous evidence hash mismatch')
        old = read_json(path)
        if not (stable and old.get('stable') is True
                and old.get('contract_hash') == fingerprint(contract)
                and old.get('plan_hash') == gate['plan_hash']
                and old.get('check_hash') == fingerprint(check_definition)
                and old.get('scope') == evidence_scope(contract, check_definition)):
            return {'status': 'not_comparable', 'reason': 'definition, approval, scope or execution stability differs'}
        previous = old['result']['status']
        if previous not in {'passed', 'failed', 'error'}:
            raise ValueError('invalid previous result')
        old_snapshot = old['snapshot_after']
        changed = sorted(p for p in set(old_snapshot) | set(before) if old_snapshot.get(p) != before.get(p))
        return {'status': 'same_definition', 'previous_status': previous,
                'current_status': result['status'], 'previous_manifest': pointer['path'],
                'changed_files': changed,
                'note': '같은 정의의 실행 결과입니다. 변경 파일에 입력과 테스트가 포함됐는지 확인하세요. 수정의 인과관계나 성능 향상을 인증하지 않습니다.'}
    except (ValueError, OSError, TypeError, KeyError):
        return {'status': 'unavailable', 'reason': 'previous evidence could not be verified'}


def check(root, selected):
    with locked(root):
        contract, state = load(root)
        ensure_open(state)
        gate = require_plan_approval(root, contract, state)
        sp = safe_path(root, '.harness/state.json')
        expected_state = digest(sp)
        checks = [c for c in contract['checks'] if not selected or c['id'] in selected]
        if not checks or selected and set(selected) - {c['id'] for c in checks}:
            raise ValueError('no checks selected or unknown check ID')
        results = []
        state['phase'] = 'verifying'
        for c in checks:
            current_gate = require_plan_approval(root, contract, state)
            if current_gate['plan_hash'] != gate['plan_hash']:
                raise ValueError('approved plan changed before the next check')
            scope = evidence_scope(contract, c)
            run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:12]
            directory = safe_path(root, '.harness/evidence', must_exist=False) / run_id
            directory.mkdir(parents=True)
            try:
                before = snapshot(root, scope)
            except (ValueError, OSError) as exc:
                before = {}
                result = {'id': c['id'], 'status': 'error', 'reason': str(exc),
                          'returncode': None, 'tests': [], 'executed': False}
            else:
                result = execute(root, c, directory)
                result['executed'] = True
            try:
                after = snapshot(root, scope)
                contract_after = read_json(safe_path(root, '.harness/contract.json'))
                after_gate = plan_gate(root, contract_after, state)
                stable = (bool(before) and before == after
                          and fingerprint(contract_after) == fingerprint(contract)
                          and after_gate['status'] == 'approved'
                          and after_gate['plan_hash'] == gate['plan_hash'])
            except (ValueError, OSError):
                after, stable = {}, False
            record = {'schema_version': 1, 'created_at': now(), 'toolkit_version': __version__,
                      'contract_hash': fingerprint(contract), 'scope': scope,
                      'plan_hash': gate['plan_hash'],
                      'check_hash': fingerprint(c), 'kind': c['kind'],
                      'timeout_seconds': c.get('timeout_seconds'),
                      'snapshot_before': before, 'snapshot_after': after,
                      'stable': stable, 'result': result}
            if not stable and result['status'] != 'error':
                result['status'], result['reason'] = 'failed', 'source, contract, or plan changed during execution'
            result['comparison'] = previous_run(root, contract, state, c, gate, before, stable, result)
            target = directory / 'manifest.json'
            atomic_json(target, record)
            state['latest_checks'][c['id']] = {'path': target.relative_to(root).as_posix(), 'sha256': digest(target)}
            results.append(result)
            # Keep completed work even if a later check or file read fails.
            atomic_json(sp, state, expected_state)
            expected_state = digest(sp)
            if not stable:
                break
    emit({'checks': results, 'requirements': requirement_status(root, contract, state)})
    return 0 if all(r['status'] == 'passed' for r in results) else 1


def update(root, args):
    with locked(root):
        contract, state = load(root)
        ensure_open(state)
        sp = safe_path(root, '.harness/state.json')
        expected_state = digest(sp)
        if args.command == 'next':
            state['next'] = args.text
        elif args.command == 'plan-approve':
            validate(contract, root)
            plan = read_json(safe_path(root, '.harness/plan.json'))
            validate_plan(plan, contract)
            if any(question['status'] == 'open' for question in plan['questions']):
                raise ValueError('plan cannot be approved while questions remain open')
            gate = plan_gate(root, contract, state)
            if gate['status'] not in {'awaiting_approval', 'stale', 'approved'}:
                raise ValueError(f"plan cannot be approved: {gate['status']}: {gate['reason']}")
            if args.actor != 'user' or not args.quote.strip() or not args.source.strip():
                raise ValueError('plan approval needs user-reported quote and source')
            source_paths = sorted({r['source']['path'] for r in contract['requirements']})
            state['plan_approval'] = {'actor': 'user', 'quote': args.quote, 'source': args.source,
                                      'recorded_at': now(), 'plan_hash': fingerprint(plan),
                                      'contract_hash': fingerprint(contract),
                                      'source_snapshot': snapshot(root, source_paths),
                                      'verification': 'unverified_local_user_report'}
        elif args.command == 'close':
            state['phase'] = 'closed'
            state['closed_at'] = now()
            state['next'] = '작업을 닫았습니다. 추가 작업을 진행하지 않습니다.'
        elif args.command == 'decision':
            validate(contract, root)
            ids = {r['id'] for r in contract['requirements']}
            if args.requirement not in ids:
                raise ValueError('unknown requirement')
            if set(args.evidence) - {c['id'] for c in contract['checks']}:
                raise ValueError('unknown evidence check ID')
            state['decisions'].append({'created_at': now(), 'requirement': args.requirement,
                                      'actor': args.actor, 'choice': args.choice, 'reason': args.reason,
                                      'alternatives': args.alternative, 'tradeoff': args.tradeoff,
                                      'evidence': args.evidence, 'contract_hash': fingerprint(contract)})
        elif args.command == 'observe':
            gate = require_plan_approval(root, contract, state)
            req = next((r for r in contract['requirements'] if r['id'] == args.requirement), None)
            if req is None or req['verification'] != 'manual':
                raise ValueError('observation must refer to a manual requirement')
            scope = sorted(set(req['implementation'] + [req['source']['path']]))
            state['observations'].append({'created_at': now(), 'requirement': req['id'],
                'status': args.result, 'note': args.note, 'actor': 'candidate-reported',
                'verification': 'unverified_self_report',
                'plan_hash': gate['plan_hash'],
                'contract_hash': fingerprint(contract), 'scope': scope, 'snapshot': snapshot(root, scope)})
        atomic_json(sp, state, expected_state)
    emit({'saved': args.command, 'phase': state['phase'], 'next': state['next']})
    return 0


def freeze(root, contract, state):
    report = overview(root, contract, state)
    gate = report['plan_gate']
    missing = []
    manifest = {}
    for path in contract.get('deliverables', []):
        try:
            manifest.update(snapshot(root, [path]))
        except (ValueError, OSError) as exc:
            missing.append(str(exc))
    handoff = {'path': 'handoff.md', 'status': 'missing', 'content_accuracy': 'not_verified'}
    try:
        handoff_path = safe_path(root, 'handoff.md')
        if not handoff_path.is_file():
            raise ValueError('handoff.md must be a regular file')
        handoff_text = handoff_path.read_text(encoding='utf-8').strip()
        handoff['status'] = ('template' if '작성 상태: 미작성 양식입니다.' in handoff_text
                             else 'present' if handoff_text else 'empty')
        if handoff['status'] == 'present':
            handoff['sha256'] = snapshot(root, ['handoff.md'])['handoff.md']
    except (ValueError, OSError) as exc:
        handoff['reason'] = str(exc)
    ready = gate['status'] == 'approved' and bool(report['requirements']) and not report['contract_errors'] and not missing and bool(manifest) and handoff['status'] == 'present'
    ready = ready and all(r['status'] == 'passed' for r in report['requirements'] if r['mandatory'])
    automatic = [r for r in report['requirements'] if r['mandatory'] and r['verification'] != 'manual']
    manual = [r['id'] for r in report['requirements'] if r['mandatory'] and r['verification'] == 'manual']
    report.update({'ready_for_candidate_review': ready, 'missing_deliverables': missing,
                   'handoff': handoff,
                   'automatic_checks_passed': gate['status'] == 'approved' and bool(automatic) and all(r['status'] == 'passed' for r in automatic),
                   'requires_manual_review': manual,
                   'submission_files': manifest,
                   'note': '자동 검사와 자기보고를 구분한 점검입니다. 수동 요구사항은 도구가 통과를 인증하지 않습니다. 실제 제출은 사용자가 확인합니다.'})
    emit(report)
    return 0 if ready else 1


def parser():
    ap = argparse.ArgumentParser(description='과제 요구사항과 실제 검증 결과를 연결하는 로컬 툴킷')
    ap.add_argument('--root', type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('--minutes', type=int, default=60)
    p = sub.add_parser('install'); p.add_argument('--dry-run', action='store_true')
    sub.add_parser('doctor'); sub.add_parser('status'); sub.add_parser('freeze'); sub.add_parser('close')
    sub.add_parser('spec'); sub.add_parser('brief'); sub.add_parser('git-check'); sub.add_parser('plan')
    p = sub.add_parser('plan-approve')
    p.add_argument('--actor', choices=['user'], required=True)
    p.add_argument('--quote', required=True)
    p.add_argument('--source', required=True)
    p = sub.add_parser('check'); p.add_argument('--id', action='append', default=[])
    p = sub.add_parser('next'); p.add_argument('--text', required=True)
    p = sub.add_parser('decision')
    p.add_argument('--requirement', required=True); p.add_argument('--actor', choices=['candidate', 'ai'], required=True)
    p.add_argument('--choice', required=True); p.add_argument('--reason', required=True)
    p.add_argument('--alternative', action='append', default=[])
    p.add_argument('--tradeoff', default='')
    p.add_argument('--evidence', action='append', default=[])
    p = sub.add_parser('observe')
    p.add_argument('--requirement', required=True); p.add_argument('--result', choices=['passed', 'failed'], required=True)
    p.add_argument('--note', required=True)
    p = sub.add_parser('inspect'); p.add_argument('file'); p.add_argument('--limit', type=int, default=10000)
    p.add_argument('--encoding', default='utf-8-sig')
    p = sub.add_parser('join'); p.add_argument('left'); p.add_argument('right'); p.add_argument('--keys', nargs='+', required=True)
    p.add_argument('--limit', type=int, default=10000); p.add_argument('--encoding', default='utf-8-sig')
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if not root.is_dir():
            raise ValueError('--root must be an existing task directory')
        state_path = safe_path(root, '.harness/state.json', must_exist=False)
        if state_path.exists() and read_json(state_path).get('phase') == 'closed':
            emit({'phase': 'closed', 'note': '작업이 닫혔습니다. 작업과 설명 명령을 중단합니다.'})
            return 0 if args.command == 'status' else 2
        if args.command == 'init':
            return initialize(root, args.minutes)
        if args.command == 'install':
            return install(root, dry_run=args.dry_run)
        if args.command == 'doctor':
            emit({'python': sys.version.split()[0], 'python_supported': sys.version_info >= (3, 11),
                  'tools': {x: shutil.which(x) is not None for x in ['git', 'node', 'npm', 'codex']},
                  'optional_python': {x: importlib.util.find_spec(x) is not None for x in ['pytest', 'pandas']},
                  'skill_auto_discovery': 'not_verified', 'multi_agent': 'not_verified',
                  'note': '환경 정보만 확인했습니다. 과제 기능의 통과 판정이 아닙니다.'})
            return 0 if sys.version_info >= (3, 11) else 1
        if args.command == 'git-check':
            from .views import git_report
            report = git_report(root)
            emit(report)
            return 2 if report['status'] == 'error' else 0
        if args.command == 'inspect':
            emit(profile(safe_path(root, args.file), args.limit, args.encoding)); return 0
        if args.command == 'join':
            emit(join_profile(safe_path(root, args.left), safe_path(root, args.right), args.keys, args.limit, args.encoding)); return 0
        if args.command == 'check':
            return check(root, args.id)
        if args.command in {'decision', 'observe', 'next', 'close', 'plan-approve'}:
            return update(root, args)
        contract, state = load(root)
        ensure_open(state)
        if args.command == 'plan':
            plan_path = safe_path(root, '.harness/plan.json', must_exist=False)
            emit({'plan': read_json(plan_path) if plan_path.is_file() else None,
                  'plan_gate': plan_gate(root, contract, state),
                  'approval_limit': '로컬 기록은 실제 사용자 신원을 인증하지 않습니다.'})
            return 0
        if args.command in {'spec', 'brief'}:
            from .views import render_spec, render_brief
            validate(contract, root)
            render = render_spec if args.command == 'spec' else render_brief
            print(render(root, contract, state))
            return 0
        if args.command == 'freeze':
            return freeze(root, contract, state)
        report = overview(root, contract, state)
        emit(report)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        emit({'error': str(exc), 'status': 'blocked'})
        return 2
