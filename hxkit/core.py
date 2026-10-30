"""Task contracts, evidence freshness and bounded, atomic state updates."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone

EXCLUDED = {'.git', '.harness', '.harness-kit', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
ID = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')


def now():
    return datetime.now(timezone.utc).isoformat()


def strict_json(text):
    def pairs(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise ValueError(f'duplicate JSON key: {k}')
            obj[k] = v
        return obj
    def constant(value):
        raise ValueError(f'non-finite JSON number: {value}')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def read_json(path):
    if path.stat().st_size > 2_000_000:
        raise ValueError('JSON file exceeds 2 MB')
    return strict_json(path.read_text(encoding='utf-8'))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False).encode()).hexdigest()


def safe_path(root, relative, must_exist=True):
    root = root.resolve()
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('path must be a nonempty project-relative path')
    parts = Path(relative).parts
    if '..' in parts:
        raise ValueError(f'parent traversal is not allowed: {relative}')
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise ValueError(f'symlink path is not supported: {relative}')
    if not p.resolve().is_relative_to(root):
        raise ValueError('path is outside the project')
    if must_exist and not p.exists():
        raise ValueError(f'path does not exist: {relative}')
    return p


def snapshot(root, paths):
    root = root.resolve()
    if not isinstance(paths, list) or not paths:
        raise ValueError('tracked paths must not be empty')
    files = {}
    total = 0
    for relative in paths:
        p = safe_path(root, relative)
        if any(part in EXCLUDED for part in p.relative_to(root).parts):
            raise ValueError(f'tracked path is excluded: {relative}')
        candidates = [p] if p.is_file() else sorted(p.rglob('*'))
        found = 0
        for f in candidates:
            rel = f.relative_to(root)
            if any(part in EXCLUDED for part in rel.parts):
                continue
            if f.is_symlink():
                raise ValueError(f'symlink in tracked tree: {rel}')
            if not f.is_file():
                continue
            total += f.stat().st_size
            if total > 200_000_000 or len(files) >= 10000:
                raise ValueError('snapshot scope exceeds 200 MB or 10000 files; narrow tracked_paths')
            files[rel.as_posix()] = digest(f)
            found += 1
        if found == 0:
            raise ValueError(f'tracked path contains no files: {relative}')
    return files


def atomic_json(path, value, expected=None):
    """Callers hold the project lock; CAS detects intervening editor changes."""
    if path.is_symlink():
        raise ValueError('refusing to replace symlink')
    if expected is not None and (not path.exists() or digest(path) != expected):
        raise ValueError('state changed during update; reload and retry')
    data = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    fd, tmp = tempfile.mkstemp(prefix='.hx-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if expected is not None and digest(path) != expected:
            raise ValueError('state changed during update; reload and retry')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextmanager
def locked(root):
    directory = safe_path(root, '.harness')
    lock = directory / 'write.lock'
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError('another toolkit operation holds write.lock; inspect before removing a stale lock') from exc
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        lock.unlink(missing_ok=True)


def validate(contract, root):
    if not isinstance(contract, dict) or type(contract.get('schema_version')) is not int or contract['schema_version'] != 1:
        raise ValueError('contract schema_version must be 1')
    if not str(contract.get('title', '')).strip():
        raise ValueError('task title is missing')
    requirements, checks = contract.get('requirements'), contract.get('checks')
    if not isinstance(requirements, list) or not requirements:
        raise ValueError('requirements must not be empty')
    if not isinstance(checks, list):
        raise ValueError('checks must be a list')
    ids = set()
    for c in checks:
        if not isinstance(c, dict) or not ID.fullmatch(str(c.get('id', ''))) or c['id'] in ids:
            raise ValueError('check IDs must be unique identifiers')
        ids.add(c['id'])
        if c.get('kind') not in {'unittest', 'json', 'command'}:
            raise ValueError(f'{c["id"]}: unsupported check kind')
        if not isinstance(c.get('tracked_paths'), list) or not c['tracked_paths']:
            raise ValueError(f'{c["id"]}: tracked_paths are required')
        for path in c['tracked_paths']:
            safe_path(root, path, must_exist=False)
    seen = set()
    for r in requirements:
        if not isinstance(r, dict) or not ID.fullmatch(str(r.get('id', ''))) or r['id'] in seen:
            raise ValueError('requirement IDs must be unique identifiers')
        seen.add(r['id'])
        for field in ('description', 'expected'):
            if not isinstance(r.get(field), str) or not r[field].strip():
                raise ValueError(f'{r["id"]}: {field} is missing')
        src = r.get('source', {})
        if not isinstance(src, dict) or not isinstance(src.get('quote'), str) or not src['quote'].strip():
            raise ValueError(f'{r["id"]}: source quote is missing')
        p = safe_path(root, src.get('path'))
        if not p.is_file() or p.stat().st_size > 2_000_000:
            raise ValueError('source must be a text file under 2 MB')
        if src['quote'] not in p.read_text(encoding='utf-8'):
            raise ValueError(f'{r["id"]}: quote not found in source')
        if r.get('verification') not in {'behavior', 'process', 'manual'}:
            raise ValueError(f'{r["id"]}: verification must be behavior, process or manual')
        if not isinstance(r.get('mandatory', True), bool):
            raise ValueError('mandatory must be boolean')
        if not isinstance(r.get('implementation'), list) or not r['implementation']:
            raise ValueError(f'{r["id"]}: implementation paths are required')
        for path in r['implementation']:
            safe_path(root, path, must_exist=False)
        refs = r.get('checks', [])
        if not isinstance(refs, list) or any(x not in ids for x in refs):
            raise ValueError(f'{r["id"]}: unknown check reference')
        if r['verification'] != 'manual' and not refs:
            raise ValueError(f'{r["id"]}: no check mapped')
        if r['verification'] == 'behavior' and not any(c['id'] in refs and c['kind'] != 'command' for c in checks):
            raise ValueError(f'{r["id"]}: command exit alone cannot verify behavior')
    if not any(r.get('mandatory', True) for r in requirements):
        raise ValueError('at least one mandatory requirement is needed')
    paths = contract.get('deliverables')
    if not isinstance(paths, list) or not paths:
        raise ValueError('deliverables must list actual submission paths')
    for path in paths:
        safe_path(root, path, must_exist=False)


def validate_plan(plan, contract):
    """Validate a reviewable plan without requiring future implementation files."""
    if not isinstance(plan, dict) or type(plan.get('schema_version')) is not int or plan['schema_version'] != 1:
        raise ValueError('plan schema_version must be 1')
    for field in ('goal', 'scope'):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            raise ValueError(f'plan {field} is missing')
    acceptance = plan.get('acceptance')
    if not isinstance(acceptance, list) or not acceptance or not all(isinstance(x, str) and x.strip() for x in acceptance):
        raise ValueError('plan acceptance must list expected outcomes')
    req_ids = {r['id'] for r in contract['requirements']}
    check_ids = {c['id'] for c in contract['checks']}
    steps = plan.get('steps')
    if not isinstance(steps, list) or not steps:
        raise ValueError('plan steps must be a nonempty list')
    covered_requirements = set()
    covered_checks = set()
    for step in steps:
        if not isinstance(step, dict) or not isinstance(step.get('description'), str) or not step['description'].strip():
            raise ValueError('each plan step needs a description')
        if (not isinstance(step.get('requirements'), list) or not step['requirements']
                or any(x not in req_ids for x in step['requirements'])):
            raise ValueError('plan step references unknown requirements')
        if (not isinstance(step.get('checks'), list)
                or any(x not in check_ids for x in step['checks'])):
            raise ValueError('plan step references unknown checks')
        covered_requirements.update(step['requirements'])
        covered_checks.update(step['checks'])
    if covered_requirements != req_ids or covered_checks != check_ids:
        raise ValueError('plan steps must cover every requirement and check')
    questions = plan.get('questions')
    if not isinstance(questions, list):
        raise ValueError('plan questions must be a list')
    seen = set()
    for question in questions:
        if not isinstance(question, dict) or not ID.fullmatch(str(question.get('id', ''))):
            raise ValueError('plan question needs a valid ID')
        if question['id'] in seen:
            raise ValueError('plan question IDs must be unique')
        seen.add(question['id'])
        for field in ('question', 'impact'):
            if not isinstance(question.get(field), str) or not question[field].strip():
                raise ValueError(f'plan question {field} is missing')
        options = question.get('options')
        if not isinstance(options, list) or not options or not all(isinstance(x, str) and x.strip() for x in options):
            raise ValueError('plan question needs options')
        if question.get('status') not in {'open', 'answered'}:
            raise ValueError('plan question status must be open or answered')
        if question['status'] == 'answered' and any(
            not isinstance(question.get(field), str) or not question[field].strip()
            for field in ('resolution', 'response_source')
        ):
            raise ValueError('answered question needs resolution and response_source')


def plan_gate(root, contract, state):
    """Report the local plan record's validity; this cannot authenticate a user."""
    root = root.resolve()
    try:
        validate(contract, root)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        status = 'stale' if isinstance(state.get('plan_approval'), dict) else 'invalid_contract'
        return {'status': status, 'reason': str(exc), 'open_questions': []}
    try:
        plan = read_json(safe_path(root, '.harness/plan.json'))
        validate_plan(plan, contract)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        status = 'stale' if isinstance(state.get('plan_approval'), dict) else 'invalid_plan'
        return {'status': status, 'reason': str(exc), 'open_questions': []}
    open_questions = [q['id'] for q in plan['questions'] if q['status'] == 'open']
    if open_questions:
        status = 'stale' if isinstance(state.get('plan_approval'), dict) else 'questions_open'
        return {'status': status, 'reason': 'unresolved plan questions',
                'open_questions': open_questions}
    approval = state.get('plan_approval')
    if not isinstance(approval, dict):
        return {'status': 'awaiting_approval', 'reason': 'explicit user approval record is missing',
                'open_questions': []}
    try:
        source_paths = sorted({r['source']['path'] for r in contract['requirements']})
        current_sources = snapshot(root, source_paths)
        current_plan = fingerprint(plan)
        current_contract = fingerprint(contract)
        if (approval.get('actor') != 'user' or not isinstance(approval.get('quote'), str)
                or not approval['quote'].strip() or not isinstance(approval.get('source'), str)
                or not approval['source'].strip()):
            raise ValueError('approval record has no user-reported basis')
        if (approval.get('plan_hash') != current_plan
                or approval.get('contract_hash') != current_contract
                or approval.get('source_snapshot') != current_sources):
            return {'status': 'stale', 'reason': 'plan, contract, or source changed after approval',
                    'open_questions': []}
    except (ValueError, OSError, TypeError, KeyError) as exc:
        return {'status': 'stale', 'reason': str(exc), 'open_questions': []}
    return {'status': 'approved', 'reason': 'local approval record matches current files; user identity is not authenticated',
            'open_questions': [], 'plan_hash': current_plan}


def require_plan_approval(root, contract, state):
    gate = plan_gate(root, contract, state)
    if gate['status'] != 'approved':
        raise ValueError(f"plan gate {gate['status']}: {gate['reason']}")
    return gate


def evidence_scope(contract, check=None):
    paths = [r['source']['path'] for r in contract['requirements']]
    selected = contract['checks'] if check is None else [check]
    paths += [p for c in selected for p in c['tracked_paths']]
    # The runner always imports this directory, even if tracking was omitted.
    paths += [c.get('test_dir', 'tests') for c in selected if c['kind'] == 'unittest']
    # Bind each check to its declared implementation, not only the author's tracking list.
    paths += [p for r in contract['requirements']
              if check is None or check['id'] in r.get('checks', [])
              for p in r['implementation']]
    return sorted(set(paths))


def requirement_status(root, contract, state):
    result = []
    current_contract = fingerprint(contract)
    gate = plan_gate(root, contract, state)
    if gate['status'] != 'approved':
        return [{'id': req['id'], 'description': req['description'],
                 'status': 'plan_pending' if gate['status'] != 'stale' else 'approval_stale',
                 'verification': req['verification'],
                 'evidence_source': 'unverified_self_report' if req['verification'] == 'manual' else 'local_execution',
                 'mandatory': req.get('mandatory', True), 'reasons': [gate['reason']]}
                for req in contract['requirements']]
    plan_hash = gate['plan_hash']
    for req in contract['requirements']:
        status, reasons = 'passed', []
        if req['verification'] == 'manual':
            observation = next((o for o in reversed(state.get('observations', [])) if o['requirement'] == req['id']), None)
            if not observation:
                status, reasons = 'not_run', ['candidate observation is missing']
            else:
                try:
                    fresh = (observation['contract_hash'] == current_contract
                             and observation.get('plan_hash') == plan_hash
                             and observation['snapshot'] == snapshot(root, observation['scope']))
                except (ValueError, OSError):
                    fresh = False
                status = 'reported_' + observation['status'] if fresh else 'stale'
                reasons = [observation['note'] if fresh else 'implementation or contract changed']
        else:
            for cid in req['checks']:
                pointer = state.get('latest_checks', {}).get(cid)
                if not pointer:
                    status, reasons = 'not_run', reasons + [f'{cid}: no execution evidence']
                    continue
                try:
                    p = safe_path(root, pointer['path'])
                    if digest(p) != pointer['sha256']:
                        raise ValueError('evidence file changed')
                    evidence = read_json(p)
                    check = next(c for c in contract['checks'] if c['id'] == cid)
                    scope = evidence_scope(contract, check)
                    fresh = (evidence['contract_hash'] == current_contract
                             and evidence.get('plan_hash') == plan_hash
                             and evidence['snapshot_after'] == snapshot(root, scope))
                    cs = evidence['result']['status'] if fresh and evidence['stable'] else 'stale'
                    if cs != 'passed':
                        status, reasons = cs, reasons + [f'{cid}: {cs}']
                except (OSError, ValueError, KeyError, StopIteration) as exc:
                    status, reasons = 'stale', reasons + [f'{cid}: {exc}']
        result.append({'id': req['id'], 'description': req['description'], 'status': status,
                       'verification': req['verification'],
                       'evidence_source': 'unverified_self_report' if req['verification'] == 'manual' else 'local_execution',
                       'mandatory': req.get('mandatory', True), 'reasons': reasons})
    return result
