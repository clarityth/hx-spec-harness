"""Read-only, bounded inspection of CSV and TSV data."""

from __future__ import annotations

import csv
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator


MAX_LIMIT = 1_000_000
MAX_LINE_CHARS = 8_000_000
MAX_SAMPLE_CHARS = 32 * 1024 * 1024
LEADING_ZERO = re.compile(r"^0\d")


def _validate_limit(limit: int) -> None:
    if type(limit) is not int or not 1 <= limit <= MAX_LIMIT:
        raise ValueError(f"limit은 1부터 {MAX_LIMIT}까지의 정수여야 합니다.")


def _bounded_lines(file: object) -> Iterator[str]:
    total_chars = 0
    while line := file.readline(MAX_LINE_CHARS + 1):
        if len(line) > MAX_LINE_CHARS:
            raise ValueError(f"입력 행이 {MAX_LINE_CHARS}자를 초과합니다.")
        total_chars += len(line)
        if total_chars > MAX_SAMPLE_CHARS:
            raise ValueError(
                f"표본 원문이 {MAX_SAMPLE_CHARS}자를 초과합니다. limit을 줄여 표본을 축소하세요."
            )
        yield line


def _has_more_data(file: object) -> bool:
    """Detect a following CSV record without parsing beyond the sample."""
    return file.read(1) != ""


def _read_rows(path: Path, limit: int, encoding: str) -> tuple[list[str], list[list[str]], bool, int]:
    """Return the header, valid sampled rows, completeness, and malformed count."""
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".tsv"}:
        raise ValueError(f"CSV 또는 TSV 파일만 지원합니다: {path}")
    delimiter = "\t" if suffix == ".tsv" else ","
    try:
        with path.open("r", encoding=encoding, newline="") as file:
            reader = csv.reader(_bounded_lines(file), delimiter=delimiter, strict=True)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise ValueError(f"빈 파일입니다: {path}") from exc
            if not header or any(name == "" for name in header):
                raise ValueError(f"빈 열 이름이 있습니다: {path}")
            if len(set(header)) != len(header):
                raise ValueError(f"중복 열 이름이 있습니다: {path}")

            rows: list[list[str]] = []
            malformed = 0
            scanned = 0
            while scanned < limit:
                try:
                    row = next(reader)
                except StopIteration:
                    return header, rows, True, malformed
                scanned += 1
                if len(row) != len(header):
                    malformed += 1
                else:
                    rows.append(row)
            return header, rows, not _has_more_data(file), malformed
    except (csv.Error, UnicodeError, LookupError) as exc:
        raise ValueError(f"CSV/TSV를 읽을 수 없습니다: {path}: {exc}") from exc


def profile(path: Path, limit: int = 10_000, encoding: str = "utf-8-sig") -> dict:
    """Inspect original strings without inferring missing values or changing the file."""
    _validate_limit(limit)
    header, rows, complete, malformed = _read_rows(Path(path), limit, encoding)
    scanned = len(rows) + malformed
    columns = {}
    for index, name in enumerate(header):
        values = [row[index] for row in rows]
        numeric: list[Decimal] = []
        for value in values:
            if value == "":
                continue
            try:
                number = Decimal(value)
            except InvalidOperation:
                continue
            if number.is_finite():
                numeric.append(number)
        columns[name] = {
            "empty": sum(value == "" for value in values),
            "distinct": len(set(values)),
            "numeric_candidate": {
                "count": len(numeric),
                "min": str(min(numeric)) if numeric else None,
                "max": str(max(numeric)) if numeric else None,
            },
            "leading_zero_count": sum(bool(LEADING_ZERO.match(value)) for value in values),
        }

    warnings = []
    if malformed:
        warnings.append(f"열 개수가 다른 행 {malformed}개를 통계에서 제외했습니다.")
    if not complete:
        warnings.append(f"앞쪽 {limit}개 행만 검사했습니다. 전체 파일 통계가 아닙니다.")
    return {
        "header": header,
        "rows_scanned": scanned,
        "complete": complete,
        "malformed_rows": malformed,
        "duplicates": scanned - malformed - len({tuple(row) for row in rows}),
        "columns": columns,
        "warnings": warnings,
    }


def join_profile(
    left: Path,
    right: Path,
    keys: list[str],
    limit: int = 10_000,
    encoding: str = "utf-8-sig",
) -> dict:
    """Count rows produced by exact raw-string inner and left joins in the sample."""
    _validate_limit(limit)
    if not keys or any(not isinstance(key, str) or not key for key in keys) or len(set(keys)) != len(keys):
        raise ValueError("keys에는 중복 없는 열 이름을 하나 이상 지정해야 합니다.")
    left_header, left_data, left_complete, left_bad = _read_rows(Path(left), limit, encoding)
    right_header, right_data, right_complete, right_bad = _read_rows(Path(right), limit, encoding)
    for key in keys:
        if key not in left_header or key not in right_header:
            raise ValueError(f"양쪽 파일에 조인 열이 있어야 합니다: {key}")

    def counts(header: list[str], rows: list[list[str]]) -> tuple[Counter[tuple[str, ...]], int]:
        positions = [header.index(key) for key in keys]
        result: Counter[tuple[str, ...]] = Counter()
        missing = 0
        for row in rows:
            value = tuple(row[index] for index in positions)
            if any(part == "" for part in value):
                missing += 1
            else:
                result[value] += 1
        return result, missing

    left_counts, left_missing = counts(left_header, left_data)
    right_counts, right_missing = counts(right_header, right_data)
    common = left_counts.keys() & right_counts.keys()
    matched_left = sum(left_counts[key] for key in common)
    matched_right = sum(right_counts[key] for key in common)
    unmatched_left = sum(count for key, count in left_counts.items() if key not in right_counts)
    unmatched_right = sum(count for key, count in right_counts.items() if key not in left_counts)
    inner_rows = sum(left_counts[key] * right_counts[key] for key in common)
    many_left = any(left_counts[key] > 1 for key in common)
    many_right = any(right_counts[key] > 1 for key in common)
    relationship = (
        "undetermined" if not common else
        "many-to-many" if many_left and many_right else
        "many-to-one" if many_left else
        "one-to-many" if many_right else
        "one-to-one"
    )
    warnings = []
    if left_bad or right_bad:
        warnings.append("열 개수가 다른 행은 조인 계산에서 제외했습니다.")
    if not left_complete or not right_complete:
        warnings.append("표본만 검사했습니다. 조인 결과와 관계는 전체 파일의 결과가 아닙니다.")
    if not common:
        warnings.append("일치하는 키가 없어서 관계를 확인할 수 없습니다.")
    return {
        "keys": keys,
        "left_rows": len(left_data) + left_bad,
        "right_rows": len(right_data) + right_bad,
        "left_complete": left_complete,
        "right_complete": right_complete,
        "left_malformed_rows": left_bad,
        "right_malformed_rows": right_bad,
        "missing_key_left_rows": left_missing,
        "missing_key_right_rows": right_missing,
        "matched_left_rows": matched_left,
        "matched_right_rows": matched_right,
        "unmatched_left_rows": unmatched_left,
        "unmatched_right_rows": unmatched_right,
        "expected_inner_rows": inner_rows,
        "expected_left_rows": inner_rows + unmatched_left + left_missing,
        "relationship": relationship,
        "warnings": warnings,
    }
