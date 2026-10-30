# 계약 형식과 검사 선택

`.harness/contract.json`은 프로젝트 요구 원문에서 파생한 명세입니다. 원문을 대체하지 않으며, 계약에 빠진 요구가 없는지는 사람이 대조해야 합니다. `init`은 빈 계약과 빈 `.harness/plan.json`을 만듭니다. 다음은 계약 형식 예시입니다.

```json
{
  "schema_version": 1,
  "title": "프로젝트에서 구현할 목적",
  "requirements": [{
    "id": "R1",
    "description": "원문에서 요구한 동작",
    "source": {"path": "TASK.md", "quote": "원문에 실제로 있는 문장"},
    "expected": "작은 입력과 관찰 가능한 기대 결과",
    "mandatory": true,
    "verification": "behavior",
    "implementation": ["solution.py"],
    "checks": ["C1"]
  }],
  "checks": [{
    "id": "C1",
    "kind": "unittest",
    "test_dir": "tests",
    "tests": ["test_solution.Rules.test_boundary"],
    "tracked_paths": ["solution.py", "tests", "data/input.csv"],
    "timeout_seconds": 30
  }],
  "deliverables": ["solution.py", "tests", "README.md"]
}
```

`source.path`는 프로젝트 안의 UTF-8 텍스트 파일입니다. 직접 읽기 어려운 원문은 프로젝트 안에 추출한 텍스트를 두고 원본 위치를 설명에 남깁니다. `source.quote`가 그 텍스트에 존재하는지는 검사하지만 해석이 올바른지는 검사하지 않습니다. `expected`는 현재 구현의 출력에서 복사하지 말고 원문과 작은 예제로 정합니다. 경로는 프로젝트 상대 경로로 지정합니다.

계약 검증은 원문 파일과 인용을 확인합니다. `implementation`, `tracked_paths`, `deliverables`에 적힌 미래 파일은 승인 전에는 없어도 됩니다. 실제 `check`는 실행 전에 해당 검사의 추적 범위를 읽으므로, 그때 필요한 파일이 없으면 검사 오류가 납니다.

## 계획과 승인 기록

`.harness/plan.json`에는 `schema_version: 1`, 비어 있지 않은 `goal`과 `scope`, 수용 기준 문자열 목록 `acceptance`, 작업 목록 `steps`, 질문 목록 `questions`를 둡니다. 각 작업은 `description`, `requirements` ID 목록과 `checks` ID 목록을 가집니다. 작업 목록 전체가 계약의 모든 요구 ID와 검사 ID를 포함해야 합니다. 수동 요구를 맡은 작업의 `checks`는 빈 목록일 수 있습니다.

질문이 없으면 `questions`를 빈 목록으로 둡니다. 질문이 있으면 `id`, `question`, `impact`, 비어 있지 않은 `options`, `status`를 기록합니다. `status`는 `open` 또는 `answered`입니다. `answered`에는 실제 답변을 반영한 `resolution`과 답변 근거인 `response_source`도 필요합니다. `open` 질문이 하나라도 있으면 계획 승인을 기록할 수 없습니다. 구체적인 형식은 [CSV 집계 계획](../examples/csv-summary/plan.example.json), [HTTP 서비스 계획](../examples/http-service/plan.example.json), [지연 주문 계획](../examples/delayed-orders/plan.example.json)에 있습니다. 이 파일은 합성 과제의 계획 예시이며 사용자 승인 기록이 아닙니다.

실제 사용자가 계획을 검토하고 명시적으로 승인한 뒤 `plan-approve --actor user --quote TEXT --source TEXT`로 짧은 승인 원문과 그 근거 위치를 기록합니다. `state.json`의 `plan_approval`에는 기록 시각과 계획·계약 해시, 원문 파일 판본도 저장됩니다. 도구는 로컬 기록과 현재 파일의 일치 여부를 확인하지만 기록자의 신원을 인증하지 않습니다. AI가 명령을 실행했다는 사실이나 `actor` 값만으로 사용자 승인을 증명할 수 없습니다.

계획, 계약 또는 원문이 승인 뒤 바뀌면 승인 판본이 오래된 상태가 됩니다. 이때 과거 검사와 관찰은 현재 통과 근거가 아닙니다. 변경 내용을 사용자에게 보여 주고 실제 재승인을 기록한 뒤 관련 검사를 새 판본에서 실행합니다. 기존 `.harness`에 계획이나 승인 기록이 없으면 자동으로 승인하지 않습니다.

| `verification` | 뜻 | 필요한 확인 |
|---|---|---|
| `behavior` | 실제 동작입니다. | `unittest`나 엄격한 JSON 비교가 적어도 하나 필요합니다. |
| `process` | 빌드나 생성 명령 등 프로세스의 성공입니다. | 명령의 종료 상태를 확인합니다. 기능의 기대값과 혼동하지 않습니다. |
| `manual` | 사람이 직접 보는 화면이나 동작입니다. | `observe`로 사용자 관찰을 자기보고로 남깁니다. 자동 통과 인증은 아닙니다. |

`unittest`는 모듈·클래스·메서드의 정확한 이름을 받아 실행한 개별 테스트를 수집합니다. 0건, 건너뛴 테스트와 예상 실패는 통과로 처리하지 않습니다. `json` 검사는 `argv` 명령의 표준 출력에 있는 JSON 하나를 `expected`와 엄격히 비교합니다. 중복 키, NaN, 불리언과 정수의 혼동을 허용하지 않습니다. `command`는 `argv` 명령의 종료 상태를 확인합니다. 셸 문자열을 자동 해석하지 않습니다. `{python}`은 현재 Python 실행 경로로 바꿉니다. 다른 언어 테스트는 `command`로 프로세스 실행을 기록할 수 있지만, 개별 동작은 JSON 비교나 별도 의미 있는 검사로 확인합니다.

`tracked_paths`에는 검사에 영향을 주는 코드, 입력과 설정을 포함합니다. 원문 파일, 연결된 구현 경로와 unittest의 `test_dir`는 도구가 함께 추적합니다. 새 파일과 삭제도 선언한 디렉터리에 포함되면 감지합니다. 다른 의존 파일은 자동으로 모두 찾아내지 못합니다. 파일과 계약·계획의 해시는 우발적인 변경을 감지하는 보조 근거이며 서명이나 위조 방지 인증이 아닙니다.

`check`는 검사 전과 후에 승인 판본을 확인합니다. 실행 중 계획, 계약, 원문 또는 추적 파일이 바뀌면 통과로 기록하지 않고 이후 검사를 중단합니다. 검사 뒤 관련 파일이 바뀌면 관련 검사를 다시 실행합니다. 계획이나 구현이 틀렸다는 이유로 기대 결과를 완화하지 않습니다. 원문 해석 오류 또는 요구 주체의 추가 설명을 확인한 경우에만 그 근거와 함께 계약과 검사 기준을 수정합니다. `.harness/state.json`과 evidence의 통과 표시를 손으로 만들지 않습니다.

전체 예시는 [지연 주문 합성 과제](../examples/delayed-orders/contract.example.json)에 있습니다. 데이터와 예상 결과는 연습용이며 다른 프로젝트의 정답이 아닙니다.
