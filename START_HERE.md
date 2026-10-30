# 시작 안내

Python 3.11 이상을 사용합니다. 공개 툴킷 폴더와 실제 과제 프로젝트 폴더는 서로 다릅니다. 설치 명령은 공개 툴킷의 `hx.py`로 시작합니다. 설치 뒤 모든 작업 명령은 **과제 프로젝트 폴더**에서 `.harness-kit/hx.py --root .` 형식으로 실행합니다. [가드레일](GUARDRAILS.md)과 현재 작업의 공식 규정을 먼저 확인합니다.

## 첫 5분에 할 일

| 순서 | 사용자와 Codex가 할 일 |
|---|---|
| 1. 규정과 원문 | 사용자는 현재 단계에서 허용된 AI, 파일 경로와 화면 확인 방법을 확인합니다. Codex는 프로젝트의 기존 지침과 원문 파일을 읽습니다. 화면에만 있는 정보는 사용자가 전달할 때까지 미확인으로 둡니다. |
| 2. 설치와 상태 | Codex는 아래 시작 지시에 따라 설치 여부를 확인합니다. 새 프로젝트만 `init`을 실행합니다. 기존 `.harness`가 있으면 `status`와 `plan`을 읽습니다. |
| 3. 질문과 계획 | Codex는 원문 인용과 작은 기대값을 계약에 연결하고 질문 초안과 계획을 작성합니다. 사용자는 결과를 바꾸는 질문에 답하고 계획을 검토합니다. |
| 4. 승인 경계 | Codex는 미해결 질문과 계획을 사용자에게 보여 줍니다. 실제 사용자 승인이 확인될 때까지 구현과 `check`를 시작하지 않습니다. |

이 표의 5분은 시작 순서를 보여 주는 기준입니다. 답변이 필요한 질문이나 환경 장애가 있으면 그 상태를 명시하고 조사와 계획 작성만 계속합니다. 사용자가 JSON을 직접 작성할 필요는 없습니다. Codex가 `.harness/contract.json`과 `.harness/plan.json`을 작성하며, 사용자는 의미와 계획을 검토하고 승인합니다.

## Codex에 보낼 시작 지시 하나

아래 문장에서 두 경로를 실제 **절대경로**로 바꾼 뒤, 허용된 Codex 대화에 한 번 보냅니다. `PROJECT`는 과제 프로젝트 폴더이고 `TOOLKIT`은 이 공개 툴킷 폴더입니다. 이미 설치된 프로젝트에서는 `TOOLKIT` 경로가 필요하지 않을 수 있습니다.

> 현재 과제 프로젝트는 `PROJECT`이고, 공개 툴킷 폴더는 `TOOLKIT`입니다. 먼저 공식 규정과 프로젝트의 기존 AGENTS.md, 원문을 확인하세요. 현재 단계에서 허용된 AI와 도구만 사용하고, 화면을 자동으로 조작하거나 작업 자료를 외부로 보내지 마세요. `.harness-kit`이 없다면 `python3 TOOLKIT/hx.py --root PROJECT install`로 설치하세요. 설치가 기존 파일과 충돌하면 덮어쓰지 말고 알려 주세요. 기존 AGENTS.md가 있으면 보존하고 `PROJECT/HARNESS.md`와 `PROJECT/.harness-kit/GUARDRAILS.md`를 직접 읽으세요. 실제 과제에서 허용된 구현 시간을 확인하고, 프로젝트 폴더에서 `.harness`가 없을 때만 `python3 .harness-kit/hx.py --root . init --minutes N`을 실행하세요. `N`에는 확인한 시간을 분 단위로 넣으세요. 기존 상태가 있으면 `status`와 `plan`으로 이어가세요. `doctor`로 환경을 확인하고, hx-start와 필요할 때 hx-discover, hx-plan의 SKILL.md를 읽으세요. 원문이 화면에만 있거나 해석이 불명확하면 제가 제공해야 할 내용과 선택지를 먼저 물어보세요. 원문 인용, 기대 결과, 예정 파일과 검사 ID를 `.harness/contract.json`에 작성하고, 목표, 범위, 수용 기준, 작업 순서와 미해결 질문을 `.harness/plan.json`에 작성하세요. JSON 작성은 맡아 주세요. 질문을 해결한 뒤 실제 계약과 계획을 제게 보여 주고 명시적인 승인을 요청하세요. 제 답변이 없으면 승인으로 기록하거나 구현을 시작하지 마세요. 승인받은 뒤에만 실제 승인 원문과 근거 위치를 `plan-approve`에 기록하고 구현, 관련 검사, 상태 확인과 handoff를 진행하세요. 화면 확인과 최종 제출은 제가 직접 합니다. AI 사용이 금지된 단계에 들어가면 즉시 중단하세요.

이 지시는 계획 승인이 아닙니다. 사용자가 뒤에서 제시된 실제 계획을 확인하고 별도로 승인해야 합니다. AI가 승인 문구를 만들어 기록하거나 합성 예제의 문구를 옮겨 쓰면 안 됩니다. 로컬 승인 기록도 사용자 신원을 인증하지 않습니다.

## 명령을 직접 확인할 때

새 프로젝트에만 다음 설치 명령을 실행합니다. 첫 줄은 어느 폴더에서든 사용할 수 있으며 두 경로를 실제 절대경로로 바꿉니다. `cd` 뒤 명령은 모두 과제 프로젝트 폴더에서 실행합니다.

```sh
python3 TOOLKIT/hx.py --root PROJECT install
cd PROJECT
python3 .harness-kit/hx.py --root . init --minutes 180
python3 .harness-kit/hx.py --root . doctor
python3 .harness-kit/hx.py --root . status
python3 .harness-kit/hx.py --root . plan
```

설치는 공개 파일 목록에 있는 파일을 `.harness-kit`으로 복사하고, 하네스 스킬과 진입 문서를 프로젝트에 추가합니다. 프로젝트의 기존 `README.md`, `AGENTS.md`와 Git 설정을 덮어쓰지 않습니다. 기존 AGENTS.md가 있으면 설치 출력에 별도 읽기 안내가 나옵니다. 기존 설치와 충돌하면 자동으로 지우거나 덮어쓰지 않습니다. `init`은 빈 계약과 계획을 만듭니다. 위 명령의 180분은 예시이므로 실제 과제 안내에서 구현 시간을 확인한 뒤 값을 정합니다. `--minutes N`은 1~10080분 범위이며, 도구의 로컬 시간은 실제 마감 시간을 대신하지 않습니다.

Codex가 계약과 계획을 작성한 뒤에는 과제 프로젝트 폴더에서 `spec`과 `plan`으로 내용을 봅니다. 실제 사용자 승인을 받은 경우에만 실제 짧은 인용과 근거 위치를 넣습니다.

```sh
python3 .harness-kit/hx.py --root . spec
python3 .harness-kit/hx.py --root . plan
python3 .harness-kit/hx.py --root . plan-approve --actor user --quote TEXT --source SOURCE
```

승인 뒤 `check --id C1`의 `C1`을 실제 검사 ID로 바꾸고, `status`, `brief`, `freeze`로 현재 근거를 확인합니다. 계획, 계약 또는 원문이 바뀌면 승인이 오래된 상태가 됩니다. 변경된 계획은 사용자에게 다시 보여 줍니다. `freeze`는 실제 제출이나 파일 잠금이 아닙니다. 화면 관찰과 제출은 사용자가 직접 수행합니다. 인계 문서는 [양식](templates/handoff.md)과 [작성 기준](docs/writing-standard.md)을 참고합니다. 전체 명령은 [WORK_API](WORK_API.md)에 있습니다.
