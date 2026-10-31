# HX Spec Harness

시험 중 개발 스킬을 검색하고 작업 순서를 다시 정하는 시간을 줄이는 Codex용 준비 툴킷입니다. 요구 파악, 설계, 구현, 리뷰와 인계에 사용할 외부 스킬 27개와 지원 자료를 담았습니다. Codex가 실제 과제에 맞는 파일을 골라 읽습니다. Python 3.11 이상에서 설치 도구를 사용할 수 있습니다.

## 시작할 때 보낼 문장

실제 과제를 열어 둔 Codex CLI에 다음 문장을 보냅니다.

> https://github.com/clarityth/hx-spec-harness 를 과제와 별도 폴더에 clone하고 BOOTSTRAP.md를 따르세요. 기존 파일을 보존하고 실제 과제 원문을 읽으세요. 필요한 외부 스킬은 docs/external-routing.md에서 직접 선택해 읽으세요. 결과를 바꾸는 미확인은 먼저 질문하고, 설계와 구현 계획을 제게 보여 준 뒤 명시적인 승인을 받으세요. 승인 후 구현·검사·리뷰를 수행하고 실행법, 선택 이유, 검증과 남은 문제를 handoff.md에 남기세요. 시험 규정을 우선하며 화면 확인과 제출은 제가 직접 합니다.

이 문장은 과제의 구현 계획을 승인한 것이 아닙니다. 과제 요구와 계획을 확인한 뒤 별도로 승인합니다. 설치와 경로 확인은 Codex가 수행합니다. 사용자가 JSON이나 스킬 이름을 작성할 필요는 없습니다.

## Codex와 내가 할 일

| 단계 | Codex가 하는 일 | 내가 하는 일 |
|---|---|---|
| 요구 파악 | 원문에서 확정된 내용과 모호한 정책을 찾고 현업자에게 물을 질문을 작성합니다. | 허용된 플랫폼에서 질문하고 실제 답변을 전달합니다. |
| 설계와 계획 | 구조, 데이터, 입력·출력, 대안과 검증 방법을 제안합니다. | 결과를 바꾸는 선택에 답하고 계획을 승인합니다. |
| 구현과 검사 | 승인 범위에서 코드를 만들고 오류를 재현·수정하며 관련 검사를 실행합니다. | 주요 선택의 이유와 동작을 이해합니다. |
| 리뷰와 인계 | 요구 충족 여부를 검토하고 실행법, 실제 근거와 미확인을 handoff.md에 적습니다. | 허용된 화면에서 필요한 동작을 직접 확인하고 제출합니다. |
| AI 금지 서술형 | AI 작업을 중단합니다. | 본인 말로 직접 답합니다. |

## 어떤 스킬을 준비했나

| 필요 | 포함한 외부 스킬 |
|---|---|
| 요구와 설계 | domain-modeling, brainstorming, requirements-scoping, system-design, service-decomposition, data-storage, api-design |
| 계획과 구현 | writing-plans, executing-plans, test-driven-development |
| 리뷰와 오류 수정 | requesting-code-review, receiving-code-review, systematic-debugging, verification-before-completion, test-gap-audit |
| 독립 작업 분담 | dispatching-parallel-agents, subagent-driven-development, using-git-worktrees |
| 데이터와 문서 | property-based-testing, sql-code-review, pdf, jupyter-notebook |
| 웹과 보안 | ui-ux-pro-max, frontend-design, security-best-practices, react19-concurrent-patterns, react18-batching-patterns |

[실제 파일과 선택 조건](docs/external-routing.md)을 확인할 수 있습니다. 원문 제작자는 Superpowers, proyecto26, OpenAI, Anthropic, Trail of Bits, GitHub, Matt Pocock과 Next Level Builder입니다. 고정 커밋과 라이선스는 [출처 목록](NOTICE.md)에 있습니다. 마지막 두 React 스킬은 특정 버전·문제용이며 일반적인 React 설계 전체를 다루지 않습니다. 자체 hx 지침 11개는 승인과 기록, 파일 경로를 연결합니다. 별도로 성능을 입증한 개발 방법론으로 표시하지 않습니다.

## 작업이 끝나면 무엇이 남나

- `handoff.md`: 실행 방법, 핵심 코드, 선택 이유, 실제 검사 결과와 남은 문제입니다.
- `.harness/contract.json`: 원문 요구와 기대 결과의 연결입니다.
- `.harness/plan.json`: 승인된 구현 범위와 검증 계획입니다.
- `.harness/evidence/`: 실행한 검사와 당시 파일 상태입니다.

코드가 바뀌면 예전 검사를 현재 통과로 사용하지 않도록 확인합니다. 자동 검사와 사용자의 화면 확인은 구분합니다. 이 파일들이 공식 제출물인지는 실제 과제 안내를 확인합니다.

## 어디까지 확인했나

파일 설치와 보존, 검사 기록 기능, 합성 예제 실행을 검증합니다. 정확한 판본별 결과는 [검증 기록](docs/validation.md)에 있습니다. 실제 시험의 점수, 모든 스킬의 성능과 사용자 이해를 보증하지 않습니다. PDF·Notebook용 실행 패키지와 MCP 서버를 자동 설치하지 않습니다.

## 필요한 안내

- [BOOTSTRAP](BOOTSTRAP.md): Codex가 설치하고 과제를 시작하는 순서입니다.
- [짧은 요청문](PROMPTS.md): 질문, 승인 계획, 구현과 인계를 요청할 때 사용합니다.
- [과제별 입력 처리](docs/task-routing.md): CSV, PDF, Notebook과 웹 과제의 확인 기준입니다.
- [가드레일](GUARDRAILS.md): 시험 중 외부 전송·Git push·금지된 UI 조작과 서술형 AI 사용을 제한합니다.
- [운영 순서](docs/session-playbook.md): 시간 안에 구현과 검증을 마치는 절차입니다.
- [직접 실행 안내](START_HERE.md)와 [명령 설명](WORK_API.md): 명령을 직접 확인할 때 읽습니다.
