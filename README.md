# HX Spec Harness

[AGENTS.md](AGENTS.md)와 [GUARDRAILS.md](GUARDRAILS.md)를 먼저 읽습니다. 범용 툴킷을 공개하는 준비 단계와 제한된 과제 수행 단계의 전송 규칙을 구분합니다. 과제 수행 중에는 Git push, 작업 자료 외부 전송과 자동 UI 조작을 하지 않습니다. 이 문서 규칙은 OS 수준의 네트워크 차단이 아닙니다.

원문 요구, 사용자 승인 계획, 구현과 실제 검사 결과를 연결하는 로컬 개발 하네스입니다. Python 3.11 이상과 표준 라이브러리를 사용합니다. 프로젝트 자료를 외부 서비스로 보내는 내장 기능과 별도 AI 연결은 없습니다. 사용자가 지정한 검사 프로그램의 네트워크 접근까지 차단하는 샌드박스는 아닙니다.

## 실제 포함한 것

| 구성 | 기능과 위치 |
|---|---|
| 실행 도구 | [hx.py](hx.py)와 [실행 코드](hxkit/cli.py)가 계획 승인, 검사, 근거 최신성, 데이터 점검과 Git 조회를 처리합니다. |
| 자체 스킬 11개 | 시작, 요구 발견, 계획, 구현, 데이터, 디버깅, 검증, 설명, 문서, 인계와 관련 작업을 안내합니다. [카탈로그](docs/skill-catalog.md)에서 실제 파일을 확인합니다. |
| 외부 원문 | Superpowers 스킬 4개와 기술별 스킬 4개, 참조 파일 및 fluent-korean 원문을 라이선스와 함께 포함합니다. [카탈로그](docs/skill-catalog.md)와 [고지](NOTICE.md)에 실제 포함 범위와 판본을 명시합니다. |
| 일반 문서와 양식 | [시작](START_HERE.md), [방법론](docs/methodology.md), [문서 기준](docs/writing-standard.md)과 [handoff 양식](templates/handoff.md)을 제공합니다. |
| 합성 예제 3개 | [CSV 집계](examples/csv-summary/TASK.md), [HTTP 서비스](examples/http-service/TASK.md), [지연 주문](examples/delayed-orders/TASK.md)의 계약과 계획, 코드를 제공합니다. |
| 검증과 배포 | 테스트와 [합성 실행](tools/smoke_demo.py), [정확한 파일 목록](public-manifest.json)을 사용하는 [ZIP 생성기](tools/build_release.py)를 제공합니다. |

## 한 번의 시작 지시

새 작업에서 사용자는 [시작 안내의 한 문단 지시](START_HERE.md#codex에-보낼-시작-지시-하나)를 실제 경로로 바꿔 Codex에 보냅니다. Codex는 공식 규정과 원문을 읽고, 필요한 질문 초안과 계약·계획 JSON을 작성합니다. 사용자가 JSON을 직접 작성할 필요는 없습니다. 사용자는 결과를 바꾸는 질문에 답하고 실제 계획을 검토해 명시적으로 승인합니다. 그 뒤 Codex는 승인된 범위에서 구현, 검사와 handoff를 진행합니다. [첫 5분 절차](START_HERE.md#첫-5분에-할-일)에 설치와 재개 경로를 정리했습니다.

`원문 조사와 이해관계자 질문 → 목표·수용 기준과 계획 → 사용자 명시 승인 → 구현 → 실제 검사 → 독립 수용 확인 → 설명과 handoff` 순서로 진행합니다. 중요한 선택은 구현 전에 묻습니다. 사용자가 승인한 범위의 구현과 검증을 계속하고, 같은 승인을 반복해서 받지 않습니다.

공개 툴킷 폴더에서 과제 프로젝트로 설치한 뒤에는 **과제 프로젝트 폴더**에서 명령을 실행합니다. 다음 명령은 새 프로젝트 설치의 예시이며 두 경로를 실제 절대경로로 바꿉니다. 이미 `.harness-kit`이 있으면 설치를 반복하지 않습니다.

```sh
python3 TOOLKIT/hx.py --root PROJECT install
cd PROJECT
python3 .harness-kit/hx.py --root . init --minutes 180
python3 .harness-kit/hx.py --root . plan
```

위 180분은 명령 형식을 보여 주는 예시입니다. 실제 과제에서 허용된 구현 시간을 확인하고 `--minutes` 값을 정합니다. 기존 `.harness`가 있으면 `init`을 반복하지 않고 `status`와 `plan`을 실행합니다. `init` 직후 계약과 계획은 빈 양식입니다. [시작 안내](START_HERE.md)에 따라 원문과 실제 계획을 작성하고 승인받아야 합니다. 파일이 존재한다는 이유만으로 계획이나 작업이 완료되지는 않습니다. 설치는 기존 프로젝트의 `README.md`, `AGENTS.md`와 Git 설정을 바꾸지 않습니다. 기존 AGENTS.md가 있으면 사용자에게 `HARNESS.md`와 `.harness-kit/GUARDRAILS.md`를 직접 읽도록 안내합니다. 자동 스킬 발견은 환경에서 별도로 확인합니다.

## 명령과 한계

| 명령 | 확인하는 내용 | 범위 |
|---|---|---|
| doctor / inspect / join | 환경과 원본 데이터 | 계획 전 읽기 전용 조사입니다. |
| spec / plan | 계약과 계획, 질문과 승인 상태 | 요구 해석과 실제 사용자 신원을 인증하지 않습니다. |
| plan-approve | 실제 사용자 답변을 현재 계획 판본에 연결 | 로컬 승인 자기보고입니다. AI가 스스로 승인했다고 쓰면 안 됩니다. |
| check / status | 실제 검사와 현재 코드에서의 근거 | 선택하지 않은 요구와 잘못 정한 기대값까지 보증하지 않습니다. |
| decision / brief | 선택 이유, 현재 결과와 설명할 질문 | 사용자 행동과 이해를 자동 인증하지 않습니다. |
| git-check | 로컬 변경과 충돌, 공백 오류 | 커밋과 원격 작업을 하지 않습니다. |
| freeze | 필수 산출물과 승인, 최신 검사 및 수동 잔여 | 파일 잠금과 실제 제출 기능은 없습니다. |
| close | 로컬 작업 종료 | 이후 status 외 작업과 설명 명령을 차단합니다. |

계획·계약·원문이 승인 뒤 바뀌면 재승인이 필요합니다. 검사 후 코드나 관련 파일이 바뀌면 기존 증거는 stale이 됩니다. 이전 성공을 현재 파일의 성공으로 표시하지 않습니다. manual 관찰은 자기보고로 남습니다. handoff.md의 설명도 원문, 코드와 실제 출력에 대조해야 합니다.

## 검증과 공개 후보 생성

```sh
python3 -m unittest discover -s tests -v
python3 tools/smoke_demo.py
python3 tools/build_release.py --output /path/outside/source/hx-spec-harness.zip
```

합성 실행의 승인 fixture는 테스트용이며 실제 사용자 승인이 아닙니다. 배포 목록 밖 문서가 들어오면 설치와 ZIP 생성을 중단합니다. 루트 `.git`과 Python 캐시, `.DS_Store`는 제외하며 배포 목록에 넣을 수 없습니다. `.gitignore`만으로 공개 범위를 정하지 않습니다. 목록 검사는 내용의 공개 적합성을 자동 심사하지 않습니다.

범용 툴킷의 공개 배포 저장소는 [clarityth/hx-spec-harness](https://github.com/clarityth/hx-spec-harness)입니다. 사용할 판본과 파일은 해당 저장소에서 확인합니다. 공개 배포는 허용된 준비 단계에서 공개 대상 내용을 별도로 검토한 뒤 진행합니다. 제한된 과제 수행 중에는 과제 파일, 입력, 결과와 대화를 Git push, 이슈, PR, Gist 또는 다른 외부 경로로 전송하지 않습니다. 과제 중 다운로드도 현재 규정이 허용하는 공개 자료와 경로에 한정합니다.

프로젝트의 `.harness`와 실제 handoff, 입력과 로그는 프로젝트 자료입니다. 범용 툴킷의 공개 ZIP에 포함하지 않습니다. [구현 안내](docs/implementation-guide.md)는 기술적 한계를, [운영 규칙](docs/orchestration.md)은 역할과 재개 절차를 설명합니다.
