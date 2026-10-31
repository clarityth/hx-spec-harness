---
name: hx-data
description: CSV와 TSV의 원본 값, 빈 값, 중복과 조인 행 증가 위험을 읽기 전용으로 살핍니다.
---

# 데이터 점검

데이터 과제에만 `python3 .harness-kit/hx.py --root . inspect FILE --limit 10000`을 사용합니다. 원본 ID, 빈 값, 모든 열이 동일한 행의 중복, 형식 오류와 표본 범위를 확인합니다. `complete=false`면 앞부분 표본의 결과입니다. `duplicates`는 모든 열이 같은 행의 수이며 업무 키의 중복 수가 아닙니다. 원본 문자열 `001`이나 `NA`를 자동 정제 결과로 해석하지 않습니다.

조인이 필요하면 `python3 .harness-kit/hx.py --root . join LEFT RIGHT --keys k1 k2 --limit 10000`을 실행합니다. 도구는 복합키를 원본 문자열로 비교합니다. 예상 inner·left 조인 행 수, 관계 유형, 미일치·빈 키·형식 오류 행을 확인합니다. 표본이면 계산값을 전체 데이터의 예상 행 수로 제시하지 않습니다.

제외, 중복 제거와 단위 변환 규칙은 프로젝트 원문으로 정합니다. 정제가 필요하면 원본을 보존하고 별도 결과를 검증합니다. 도구가 값을 자동 변환하거나 정제하지 않습니다.

PDF 또는 Notebook 입력은 `.harness-kit/docs/task-routing.md`의 해당 절차를 읽습니다. 저장한 분석 결과를 다시 읽고 스키마, 행 수와 핵심 값을 확인합니다. 저장된 Notebook 출력은 이번 실행의 근거로 취급하지 않습니다.

PDF·Notebook 작업은 `.harness-kit/docs/external-routing.md`에 연결된 실제 외부 스킬을 읽고 동봉 파일 경로를 사용합니다.
