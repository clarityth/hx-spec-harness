"""Read-only task explanations and local Git state inspection."""

from __future__ import annotations

import os
from pathlib import Path
import shlex
import subprocess

from . import core
from .runner import _redact


def _open_contract(root: Path, contract: dict, state: dict) -> None:
    if state.get('phase') == 'closed':
        raise ValueError('closed task: AI-assisted reports are unavailable')
    core.validate(contract, root)


def _lines(value: object) -> str:
    return '\n'.join('> ' + line for line in str(value).splitlines()) or '> '


def _listed(values: list[str]) -> str:
    return ', '.join(f'`{value}`' for value in values) if values else '없음'


def _check_definition(check: dict) -> str:
    if check['kind'] == 'unittest':
        return f"unittest: {_listed(check.get('tests', []))}"
    return f"{check['kind']}: `{_redact(shlex.join(check['argv']))}`"


def render_spec(root: Path, contract: dict, state: dict) -> str:
    """Render the source-linked plan without changing task files."""
    root = Path(root).resolve()
    _open_contract(root, contract, state)
    lines = [f"# 과제 명세: {contract['title']}", '',
             '원문과 기대 결과를 확인한 뒤 구현하고 검사합니다.', '', '## 요구사항', '']
    checks = {check['id']: check for check in contract['checks']}
    for req in contract['requirements']:
        lines.extend([f"### {req['id']}: {req['description']}", '',
                      f"원문 위치: `{req['source']['path']}`", '',
                      _lines(req['source']['quote']), '',
                      f"기대 결과: {req['expected']}", '',
                      f"구현 경로: {_listed(req['implementation'])}", '',
                      f"검증 방식: `{req['verification']}`", '', '검사 목록:', ''])
        if req.get('checks', []):
            lines.extend(f"- `{cid}`: {_check_definition(checks[cid])}" for cid in req['checks'])
        else:
            lines.append('- 자동 검사가 없습니다. 사용자가 직접 관찰한 결과를 기록합니다.')
        lines.append('')
    lines.extend(['## 제출 경로', '', _listed(contract['deliverables']), '',
                  '## 다음 작업', '', str(state.get('next') or '원문과 구현 결과를 대조하고 검사를 실행합니다.'), ''])
    return '\n'.join(lines)


def _verified_check(root: Path, contract: dict, state: dict, check: dict) -> dict:
    """Read a manifest only after its pointer and current scope agree."""
    cid = check['id']
    gate = core.plan_gate(root, contract, state)
    if gate['status'] != 'approved':
        return {'status': 'approval_stale' if gate['status'] == 'stale' else 'plan_pending'}
    pointer = state.get('latest_checks', {}).get(cid)
    if not pointer:
        return {'status': 'not_run'}
    try:
        path = core.safe_path(root, pointer['path'])
        if core.digest(path) != pointer['sha256']:
            raise ValueError('manifest hash changed')
        record = core.read_json(path)
        scope = core.evidence_scope(contract, check)
        if (record.get('contract_hash') != core.fingerprint(contract)
                or record.get('plan_hash') != gate['plan_hash']
                or record.get('check_hash') != core.fingerprint(check)
                or record.get('kind') != check['kind']
                or record.get('scope') != scope
                or record.get('snapshot_after') != core.snapshot(root, scope)
                or record.get('stable') is not True):
            raise ValueError('manifest is stale or inconsistent')
        result = record['result']
        if result.get('id') != cid or result.get('status') not in {'passed', 'failed', 'error'}:
            raise ValueError('invalid check result')
        log = result.get('log')
        log_path = None
        if isinstance(log, str) and log and Path(log).name == log:
            candidate = path.parent / log
            if candidate.is_file() and not candidate.is_symlink():
                log_path = candidate.relative_to(root).as_posix()
        tests = result.get('tests', [])
        if not isinstance(tests, list):
            raise ValueError('invalid test records')
        return {'status': result['status'], 'command': result.get('command'),
                'test_count': sum(item.get('executed') is True for item in tests if isinstance(item, dict)),
                'log': log_path, 'returncode': result.get('returncode'),
                'reason': result.get('reason')}
    except (OSError, ValueError, TypeError, KeyError):
        return {'status': 'stale'}


_STATUS = {'passed': '통과', 'failed': '실패', 'error': '실행 오류',
           'not_run': '미실행', 'stale': '증거 무효',
           'plan_pending': '계획 승인 대기', 'approval_stale': '계획 재승인 필요',
           'reported_passed': '사용자 자기보고 통과(인증 안 됨)',
           'reported_failed': '사용자 자기보고 실패(인증 안 됨)'}


def render_brief(root: Path, contract: dict, state: dict) -> str:
    """Render current evidence and questions for the candidate to answer."""
    root = Path(root).resolve()
    _open_contract(root, contract, state)
    statuses = {item['id']: item for item in core.requirement_status(root, contract, state)}
    checks = {check['id']: check for check in contract['checks']}
    details = {cid: _verified_check(root, contract, state, check) for cid, check in checks.items()}
    lines = [f"# 현재 설명 준비: {contract['title']}", '',
             '이 문서는 로컬 기록을 정리합니다. 원문과 실제 실행 결과를 사용자가 직접 확인합니다.',
             'AI 제안이나 AI 기록은 사용자가 수행한 행동이 아닙니다. 수동 관찰은 자기보고이며 도구가 인증하지 않습니다.',
             '', '## 요구사항별 현재 상태', '']
    for req in contract['requirements']:
        status = statuses[req['id']]
        value = status['status']
        if value == 'passed' and any(details[cid]['status'] != 'passed' for cid in req.get('checks', [])):
            value = 'stale'
        lines.extend([f"### {req['id']}: {req['description']}", '',
                      f"원문 위치: `{req['source']['path']}`", '',
                      _lines(req['source']['quote']), '',
                      f"기대 결과: {req['expected']}",
                      f"현재 상태: {_STATUS.get(value, value)} (`{value}`)",
                      f"검증 방식: `{req['verification']}`", ''])
        if status['reasons']:
            lines.append('상태 근거: ' + '; '.join(str(reason) for reason in status['reasons']))
            lines.append('')
        if req['verification'] == 'manual':
            lines.extend(['검사 기록: 자동 검사 대상이 아닙니다. 화면이나 동작은 사용자가 직접 확인합니다.', ''])
        else:
            lines.extend(['실제 검사 기록:', ''])
            for cid in req.get('checks', []):
                item = details[cid]
                label = _STATUS.get(item['status'], item['status'])
                lines.append(f"- `{cid}`: {label}")
                if item['status'] not in {'not_run', 'stale', 'plan_pending', 'approval_stale'}:
                    lines.append(f"  - 실제 실행 명령: `{item['command']}`" if item['command'] else '  - 실제 실행 명령: 기록 없음')
                    kind = checks[cid]['kind']
                    if kind == 'unittest':
                        lines.append(f"  - 실행한 테스트: {item['test_count']}건")
                    elif kind == 'json':
                        compared = str(item.get('reason', '')).startswith(('JSON ', 'invalid JSON output:'))
                        lines.append('  - 실제 JSON 비교: 실행함' if compared else '  - 실제 JSON 비교: 완료되지 않음')
                    else:
                        lines.append(f"  - 프로세스 검사: 종료 코드 {item['returncode']}")
                    lines.append(f"  - 로그 경로: `{item['log']}`" if item['log'] else '  - 로그 경로: 기록 없음')
            lines.append('')
    lines.extend(['## 선택 기록', ''])
    decisions = state.get('decisions', [])
    if not decisions:
        lines.extend(['기록된 선택이 없습니다.', ''])
    for index, item in enumerate(decisions, 1):
        actor = item.get('actor')
        label = '사용자 자기보고 기록(인증 안 됨)' if actor == 'candidate' else 'AI 제안 기록' if actor == 'ai' else '주체 불명 기록'
        lines.extend([f"### {index}. {item.get('requirement', '요구사항 미지정')} ({label})", '',
                      f"선택: {item.get('choice', '기록 없음')}",
                      f"이유: {item.get('reason', '기록 없음')}"])
        decision_hash = item.get('contract_hash')
        if decision_hash and decision_hash != core.fingerprint(contract):
            lines.append('명세 버전: 과거 명세의 판단 기록입니다. 현재 명세에 그대로 적용됐는지는 확인이 필요합니다.')
        elif not decision_hash:
            lines.append('명세 버전: 기록이 없어 현재 명세와의 일치 여부를 확인할 수 없습니다.')
        if isinstance(item.get('alternatives'), list):
            lines.append('검토한 대안: ' + '; '.join(str(value) for value in item['alternatives']))
        if isinstance(item.get('tradeoff'), str):
            lines.append('선택 비용: ' + item['tradeoff'])
        if isinstance(item.get('evidence'), list):
            lines.append('연결한 검사 ID: ' + _listed(item['evidence']))
        lines.append('')
    lines.extend(['## 자기 설명 점검', '',
                  '1. 입력은 무엇이고, 어떤 처리를 거쳐, 어떤 출력을 만들었습니까?',
                  '2. 어떤 선택을 했고, 검토한 대안과 비용은 무엇입니까? 그 선택의 주체는 누구입니까?',
                  '3. 실제로 검증한 것은 무엇입니까? 아직 검증하지 못한 것은 무엇입니까?', ''])
    return '\n'.join(lines)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update({'GIT_OPTIONAL_LOCKS': '0', 'GIT_CONFIG_NOSYSTEM': '1',
                'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_EXTERNAL_DIFF': '',
                'LANG': 'C', 'LC_ALL': 'C'})
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false',
                           '-c', 'diff.external=', *args], cwd=root, env=env,
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=5, check=False)


def _decode(value: bytes) -> str:
    return value.decode('utf-8', errors='surrogateescape')


def _status_entries(data: bytes) -> dict:
    groups = {'staged': [], 'unstaged': [], 'untracked': [], 'conflicts': []}
    pieces = data.split(b'\0')
    if pieces[-1] != b'':
        raise ValueError('incomplete Git status output')
    index = 0
    while index < len(pieces) - 1:
        entry = pieces[index]
        if len(entry) < 4 or entry[2:3] != b' ':
            raise ValueError('invalid Git status entry')
        x, y = chr(entry[0]), chr(entry[1])
        item = {'path': _decode(entry[3:]), 'code': x + y}
        index += 1
        if 'R' in (x, y) or 'C' in (x, y):
            if index >= len(pieces) - 1:
                raise ValueError('incomplete Git rename entry')
            item['original_path'] = _decode(pieces[index])
            index += 1
        if x == '?' and y == '?':
            groups['untracked'].append(item)
        elif x + y in {'DD', 'AU', 'UD', 'UA', 'DU', 'AA', 'UU'}:
            groups['conflicts'].append(item)
        else:
            if x not in {' ', '?'}:
                groups['staged'].append(item)
            if y not in {' ', '?'}:
                groups['unstaged'].append(item)
    return groups


def git_report(root: Path) -> dict:
    """Read local Git state. No remote, commit, or configuration mutation occurs."""
    root = Path(root).resolve()
    report = {'status': 'error', 'head': None, 'branch': None, 'staged': [],
              'unstaged': [], 'untracked': [], 'conflicts': [], 'whitespace_errors': []}
    try:
        probe = _git(root, 'rev-parse', '--is-inside-work-tree')
        if probe.returncode != 0 or probe.stdout.strip() != b'true':
            report['status'] = 'not_git_repository' if b'not a git repository' in probe.stderr.lower() else 'error'
            report['error'] = 'Git 저장소가 아닙니다.' if report['status'] == 'not_git_repository' else _decode(probe.stderr).strip()
            return report
        head = _git(root, 'rev-parse', '--verify', 'HEAD')
        if head.returncode == 0:
            report['head'] = _decode(head.stdout).strip()
        branch = _git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD')
        if branch.returncode == 0:
            report['branch'] = _decode(branch.stdout).strip()
        status = _git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all',
                      '--ignore-submodules=all', '--', '.')
        if status.returncode != 0:
            raise ValueError(_decode(status.stderr).strip() or 'Git status failed')
        report.update(_status_entries(status.stdout))
        for args in (('diff', '--no-ext-diff', '--no-textconv', '--check', '--', '.'),
                     ('diff', '--no-ext-diff', '--no-textconv', '--cached', '--check', '--', '.')):
            diff = _git(root, *args)
            if diff.returncode not in {0, 1, 2} or (diff.returncode != 0 and not diff.stdout):
                raise ValueError(_decode(diff.stderr).strip() or 'Git diff --check failed')
            report['whitespace_errors'].extend(_decode(diff.stdout).splitlines())
        report['status'] = 'ok'
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        report['status'] = 'error'
        report['error'] = str(exc)
    return report
