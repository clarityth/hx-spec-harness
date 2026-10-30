"""Run bounded local checks and retain redacted evidence."""

import json
import math
import os
from pathlib import Path
import re
import signal
import shlex
import subprocess
import sys
import tempfile
import threading
import time
import uuid


MAX_OUTPUT_BYTES = 256 * 1024
_ID = re.compile(r"[A-Za-z0-9_-]+\Z")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth(?:orization)?|password|passwd|secret|token)"
    r"(\s*[:=]\s*|\s+)(?:bearer\s+)?([^\s,;]+)"
)
_BEARER = re.compile(r"(?i)\bBearer\s+[^\s,;]+")
_KEY = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{12,}|AKIA[0-9A-Z]{16})\b")
_JSON_SECRET = re.compile(
    r"(?i)([\"'](?:api[_-]?key|access[_-]?token|auth(?:orization)?|password|passwd|secret|token)"
    r"[\"']\s*:\s*[\"']?)([^\"'\s,}]+)"
)


def _redact(value):
    value = _JSON_SECRET.sub(lambda match: match.group(1) + "[REDACTED]", value)
    value = _SECRET_ASSIGNMENT.sub(lambda match: match.group(1) + match.group(2) + "[REDACTED]", value)
    value = _BEARER.sub("Bearer [REDACTED]", value)
    return _KEY.sub("[REDACTED]", value)


def _reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError("non-finite JSON number: " + value)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _environment():
    allowed = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "SYSTEMROOT", "WINDIR")
    return {key: os.environ[key] for key in allowed if key in os.environ}


def _validate(root, check):
    if not isinstance(check, dict):
        raise ValueError("check must be an object")
    check_id = check.get("id")
    if not isinstance(check_id, str) or not _ID.fullmatch(check_id):
        raise ValueError("id must contain only letters, digits, _ or -")
    kind = check.get("kind")
    if kind not in {"unittest", "json", "command"}:
        raise ValueError("unsupported check kind")
    timeout = check.get("timeout_seconds")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 1 <= timeout <= 300:
        raise ValueError("timeout_seconds must be between 1 and 300")
    if kind == "unittest":
        names = check.get("tests")
        if not isinstance(names, list) or not all(isinstance(name, str) and name.strip() for name in names):
            raise ValueError("tests must be a list of dotted names")
        test_dir = check.get("test_dir", "tests")
        if not isinstance(test_dir, str) or not test_dir or Path(test_dir).is_absolute():
            raise ValueError("test_dir must be a relative directory")
        resolved = (root / test_dir).resolve()
        if not resolved.is_relative_to(root.resolve()) or not resolved.is_dir():
            raise ValueError("test_dir must exist within root")
        return resolved
    argv = check.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
        raise ValueError("argv must be a nonempty list of strings")
    if kind == "json":
        if "expected" not in check:
            raise ValueError("json check needs expected")
        _canonical(check["expected"])
    return None


def _run(argv, root, timeout):
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    output_size = 0
    lock = threading.Lock()
    process = subprocess.Popen(
        argv, cwd=root, env=_environment(), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
        start_new_session=(os.name == "posix"),
    )

    def drain(stream, label):
        nonlocal output_size
        with stream:
            while chunk := stream.read(65536):
                with lock:
                    remaining = max(0, MAX_OUTPUT_BYTES - sum(map(len, captured.values())))
                    if remaining:
                        captured[label].extend(chunk[:remaining])
                    output_size += len(chunk)

    readers = [threading.Thread(target=drain, args=(stream, name), daemon=True)
               for stream, name in ((process.stdout, "stdout"), (process.stderr, "stderr"))]
    for reader in readers:
        reader.start()
    timed_out = False
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        returncode = process.wait()
    for reader in readers:
        reader.join(timeout=1)
    incomplete = any(reader.is_alive() for reader in readers)
    if incomplete and os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        for reader in readers:
            reader.join(timeout=1)
    return (returncode, timed_out, bytes(captured["stdout"]),
            bytes(captured["stderr"]), output_size > MAX_OUTPUT_BYTES, incomplete)


def execute(root: Path, check: dict, evidence_dir: Path) -> dict:
    """Execute one check. A zero process exit alone proves only a command check."""
    started = time.monotonic()
    root = Path(root).resolve()
    evidence_dir = Path(evidence_dir)
    raw_id = check.get("id") if isinstance(check, dict) else None
    check_id = raw_id if isinstance(raw_id, str) and _ID.fullmatch(raw_id) else "invalid-check"
    log_name = check_id + ".log"
    strength = "process" if isinstance(check, dict) and check.get("kind") == "command" else "behavior"
    result = {"id": check_id, "status": "error", "reason": None, "returncode": None,
              "duration_seconds": 0.0, "evidence_strength": strength, "tests": [],
              "log": log_name, "output_truncated": False}
    result_file = None
    stdout = stderr = b""
    try:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        test_dir = _validate(root, check)
        kind = check["kind"]
        if kind == "unittest":
            if not check["tests"]:
                result.update(status="failed", reason="no tests configured")
                return result
            nonce = uuid.uuid4().hex
            with tempfile.NamedTemporaryFile(prefix="unittest-", suffix=".json", dir=evidence_dir, delete=False) as handle:
                result_file = Path(handle.name)
            result_file.unlink()
            argv = [sys.executable, str(Path(__file__).with_name("unittest_adapter.py").resolve()),
                    str(result_file.resolve()), str(test_dir), json.dumps(check["tests"]), nonce]
        else:
            argv = [sys.executable if arg == "{python}" else arg for arg in check["argv"]]
        result['command'] = _redact(shlex.join(argv))
        result['timeout_seconds'] = check['timeout_seconds']
        returncode, timed_out, stdout, stderr, truncated, incomplete = _run(argv, root, check["timeout_seconds"])
        result["returncode"] = returncode
        result["output_truncated"] = truncated or incomplete
        if timed_out:
            result.update(status="failed", reason="timeout")
        elif truncated:
            result.update(status="failed", reason="output exceeded 256 KiB; log truncated")
        elif incomplete:
            result.update(status="failed", reason="output stream remained open after process exit")
        elif kind == "unittest":
            if not result_file.is_file():
                result.update(status="error", reason="unittest adapter result missing")
            else:
                record = json.loads(result_file.read_text(encoding="utf-8"))
                tests = record.get("tests")
                count = record.get("tests_run")
                if (record.get("nonce") != nonce or not isinstance(tests, list)
                        or isinstance(count, bool) or not isinstance(count, int)
                        or count != sum(item.get("executed") is True for item in tests if isinstance(item, dict))
                        or any(
                            not isinstance(item, dict) or not isinstance(item.get("id"), str)
                            or not isinstance(item.get("executed"), bool)
                            or item.get("status") not in {"passed", "failed", "error", "skipped", "expected_failure", "unexpected_success"}
                            for item in tests)):
                    result.update(status="error", reason="invalid unittest adapter result")
                else:
                    result["tests"] = tests
                    if returncode != 0 or any(item["status"] != "passed" for item in tests):
                        result.update(status="failed", reason="one or more tests did not pass")
                    elif count == 0:
                        result.update(status="failed", reason="zero tests executed")
                    else:
                        result.update(status="passed", reason="all tests passed")
        elif returncode != 0:
            result.update(status="failed", reason="nonzero exit")
        elif kind == "json":
            try:
                actual = json.loads(stdout.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys,
                                    parse_constant=_reject_constant)
                if _canonical(actual) == _canonical(check["expected"]):
                    result.update(status="passed", reason="JSON matched expected value")
                else:
                    result.update(status="failed", reason="JSON differed from expected value")
            except (UnicodeDecodeError, ValueError, TypeError) as exc:
                result.update(status="failed", reason="invalid JSON output: " + str(exc))
        else:
            result.update(status="passed", reason="process exited with code 0")
    except (OSError, ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError) as exc:
        result.update(status="error", reason=_redact(str(exc)))
    finally:
        if result_file is not None:
            result_file.unlink(missing_ok=True)
        result["duration_seconds"] = round(time.monotonic() - started, 3)
        if evidence_dir.is_dir():
            evidence_dir.joinpath(log_name).write_text(
                _redact("STDOUT\n" + stdout.decode("utf-8", errors="replace")
                        + "\nSTDERR\n" + stderr.decode("utf-8", errors="replace"))
                + ("\n[OUTPUT TRUNCATED]\n" if result["output_truncated"] else ""),
                encoding="utf-8")
    return result
