# 시작 안내

일반 사용자는 [README의 시작 지시](README.md#codex-cli에서-바로-시작하기)를 현재 과제를 열어 둔 Codex CLI에 보냅니다. 과제 경로나 JSON을 미리 작성할 필요는 없습니다. Codex는 저장소를 clone한 뒤 [BOOTSTRAP.md](BOOTSTRAP.md)에 따라 과제 폴더를 식별하고 설치 또는 재개를 진행합니다. 프로젝트 후보가 여러 개여서 식별할 수 없을 때만 경로를 질문합니다.

## Codex가 먼저 확인할 것

1. 현재 단계의 공식 규정, 과제 원문과 기존 프로젝트 지침을 확인합니다. 툴킷의 [가드레일](GUARDRAILS.md)을 읽습니다. 화면에만 있는 원문은 사용자에게 요청합니다.
2. `hx.py`, `hxkit/`와 `public-manifest.json`이 있는 툴킷 폴더를 실제 과제 프로젝트와 구분합니다. 기존 파일을 보존하고 설치 대상과 충돌을 확인합니다.
3. 프로젝트에 `.harness-kit`이 없을 때만 설치합니다. 설치 뒤 프로젝트의 `HARNESS.md`, `.harness-kit/GUARDRAILS.md`와 `.agents/skills/hx-start/SKILL.md`를 Codex가 직접 읽습니다. 스킬이 자동으로 발견되지 않아도 파일을 직접 읽습니다.
4. 기존 `.harness`가 있으면 `status`와 `plan`으로 재개합니다. 새 작업에서만 실제 안내에서 확인한 구현 시간을 사용해 `init`을 실행합니다.

## clone과 설치 명령을 직접 확인할 때

다음 명령은 새 설치의 예시입니다. `HX_TOOLKIT_DIR`에는 새 툴킷 폴더의 절대경로를, `HX_PROJECT_DIR`에는 실제 과제 프로젝트의 절대경로를 넣습니다. Codex가 두 경로를 식별해 실행합니다. Python 3.11 이상이 필요합니다.

```sh
HX_TOOLKIT_DIR=/absolute/path/to/hx-spec-harness
HX_PROJECT_DIR=/absolute/path/to/project
git clone https://github.com/clarityth/hx-spec-harness.git "$HX_TOOLKIT_DIR"
python3 "$HX_TOOLKIT_DIR/hx.py" --root "$HX_PROJECT_DIR" install
cd "$HX_PROJECT_DIR"
python3 .harness-kit/hx.py --root . doctor
```

설치는 툴킷을 `.harness-kit`에 복사하고 하네스 진입 문서와 스킬을 추가합니다. 기존 `README.md`, `AGENTS.md`와 Git 설정은 덮어쓰지 않습니다. 기존 파일과 충돌하면 설치를 중단하고 원인을 확인합니다. 기존 `.harness-kit`이 있으면 재설치하거나 자동 업그레이드하지 않습니다.

새 과제에서 `.harness`가 없을 때만 `N`을 실제 허용 시간의 분 단위 값으로 바꿔 초기화합니다. `init`은 빈 계약과 계획을 만듭니다. 이미 `.harness`가 있으면 아래 두 번째 명령 묶음으로 이어갑니다.

```sh
python3 .harness-kit/hx.py --root . init --minutes N
python3 .harness-kit/hx.py --root . plan
```

```sh
python3 .harness-kit/hx.py --root . status
python3 .harness-kit/hx.py --root . plan
```

## 질문과 승인 뒤에 진행할 일

Codex는 실제 원문과 담당자 답변을 바탕으로 `.harness/contract.json`에 요구와 기대 결과를, `.harness/plan.json`에 목표, 범위, 작업 순서, 검사와 미해결 질문을 작성합니다. 결과를 바꾸는 질문에는 선택지와 영향을 함께 제시합니다. 사용자는 질문에 답하고 읽기 쉬운 계획을 검토합니다. Codex는 합성 예제의 요구, 기대값이나 승인 문구를 실제 과제에 옮기지 않습니다.

**구현은 사용자가 실제 계획을 명시적으로 승인한 뒤 시작합니다.** 시작 지시나 침묵은 계획 승인이 아닙니다. 아래 명령도 Codex가 실제 승인 원문과 출처를 확보한 뒤에만 사용합니다. `TEXT`, `SOURCE`와 `C1`은 실제 승인 내용, 근거 위치와 계약의 검사 ID로 바꿉니다.

```sh
python3 .harness-kit/hx.py --root . spec
python3 .harness-kit/hx.py --root . plan
python3 .harness-kit/hx.py --root . plan-approve --actor user --quote TEXT --source SOURCE
python3 .harness-kit/hx.py --root . check --id C1
python3 .harness-kit/hx.py --root . status
python3 .harness-kit/hx.py --root . brief
```

Codex는 승인된 범위에서 필수 동작을 먼저 구현하고, 관련 검사를 실행한 뒤 실행법과 결과를 `handoff.md`에 적습니다. 사용자는 허용된 화면에서 동작을 직접 확인하고 최종 제출을 수행합니다. [한 과제를 끝내는 운영 순서](docs/session-playbook.md)가 단계별 기준을 설명합니다. 계획, 계약 또는 원문이 바뀌면 수정한 계획을 다시 보여 주고 승인받습니다.

`plan-approve`는 로컬 기록이며 사용자 신원을 인증하지 않습니다. `check`는 선택한 검사의 결과만 보여 줍니다. 이 도구는 네트워크를 차단하거나 실제 제출을 수행하지 않습니다. 현재 단계의 공식 규정을 먼저 확인합니다. 명령의 상세 입력과 결과는 [WORK_API.md](WORK_API.md)에 있습니다.
