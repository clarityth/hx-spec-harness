# 작업별 외부 스킬 선택표

이 표는 Codex가 사용합니다. 사용자는 시험 중 스킬을 검색하거나 이름을 선택할 필요가 없습니다. 원문과 실제 기술을 확인한 뒤 조건에 맞는 파일을 직접 읽습니다. 자체 hx 지침은 승인·경로·기록을 연결하며 외부 개발 방법의 대체물이 아닙니다.

설치 전 링크는 이 저장소 기준입니다. 설치 후에는 모든 `third_party/` 경로 앞에 `.harness-kit/`를 붙입니다. 자동 스킬 발견을 전제하지 않습니다. 먼저 [적용 규칙](upstream-policy.md)을 읽고 원문의 미포함 스킬 호출, 원격 전송과 자동 UI 조작을 수행하지 않습니다.

| 조건 | 실제 스킬 파일 | 적용 결과 |
|---|---|---|
| 요구와 대안이 모호함 | [brainstorming](../third_party/obra-superpowers/skills/brainstorming/SKILL.md) | 질문과 설계 대안을 정리합니다. |
| 전체 구조를 결정함 | [system-design](../third_party/system-design-skills/skills/system-design/SKILL.md) | 필요한 구성요소와 선택 비용을 정리합니다. |
| 책임과 데이터 소유권을 나눔 | [service-decomposition](../third_party/system-design-skills/skills/service-decomposition/SKILL.md) | 모듈 경계를 정합니다. 별도 서비스 배포를 강요하지 않습니다. |
| 저장 구조를 결정함 | [data-storage](../third_party/system-design-skills/skills/data-storage/SKILL.md) | 실제 접근 패턴, 키와 인덱스를 정합니다. |
| 기능·제약이 불명확함 | [requirements-scoping](../third_party/system-design-skills/skills/requirements-scoping/SKILL.md) | 기존 답변을 보존하고 남은 질문을 정리합니다. |
| API를 설계함 | [api-design](../third_party/system-design-skills/skills/api-design/SKILL.md) | 입출력과 오류 계약을 정합니다. |
| 구현 계획을 작성함 | [writing-plans](../third_party/obra-superpowers/skills/writing-plans/SKILL.md) | 검증 가능한 실행 순서를 작성합니다. |
| 승인된 계획을 실행함 | [executing-plans](../third_party/obra-superpowers/skills/executing-plans/SKILL.md) | 작은 단위로 구현하고 검사합니다. |
| 업무 로직과 회귀를 구현함 | [test-driven-development](../third_party/obra-superpowers/skills/test-driven-development/SKILL.md) | 독립적인 기대값을 먼저 확인합니다. |
| 독립 조사·오류가 여러 개임 | [dispatching-parallel-agents](../third_party/obra-superpowers/skills/dispatching-parallel-agents/SKILL.md) | 지원되는 에이전트로 분담합니다. |
| 승인된 독립 구현이 있음 | [subagent-driven-development](../third_party/obra-superpowers/skills/subagent-driven-development/SKILL.md) | 파일 소유권과 검토 담당을 나눕니다. |
| 실제 동시 수정 충돌을 격리해야 함 | [using-git-worktrees](../third_party/obra-superpowers/skills/using-git-worktrees/SKILL.md) | 기존 Git 상태와 권한을 먼저 확인합니다. 기본 경로는 단일 프로젝트입니다. |
| 의미 있는 구현을 마침 | [requesting-code-review](../third_party/obra-superpowers/skills/requesting-code-review/SKILL.md) | 범위와 인수 조건을 지정해 독립 검토합니다. |
| 검토 의견을 받음 | [receiving-code-review](../third_party/obra-superpowers/skills/receiving-code-review/SKILL.md) | 근거를 확인하고 수정합니다. |
| 재현 가능한 오류가 있음 | [systematic-debugging](../third_party/obra-superpowers/skills/systematic-debugging/SKILL.md) | 원인 가설을 검증합니다. |
| 완료를 보고함 | [verification-before-completion](../third_party/obra-superpowers/skills/verification-before-completion/SKILL.md) | 현재 코드의 실제 검사 결과를 확인합니다. |
| 파싱·변환·집계 불변조건이 있음 | [property-based-testing](../third_party/data-quality-extra/plugins/property-based-testing/skills/property-based-testing/SKILL.md) | 반례와 경계조건을 검사합니다. |
| PDF 입력 또는 출력이 있음 | [pdf](../third_party/openai-task-skills/skills/.curated/pdf/SKILL.md) | 로컬 추출·렌더링과 누락을 확인합니다. |
| Notebook을 만들거나 수정함 | [jupyter-notebook](../third_party/openai-task-skills/skills/.curated/jupyter-notebook/SKILL.md) | 동봉 템플릿을 쓰고 전체 실행과 저장 결과를 구분합니다. |
| UI 접근성·폼·레이아웃을 설계하거나 검토함 | [ui-ux-pro-max](../third_party/ui-ux-pro-max/.claude/skills/ui-ux-pro-max/SKILL.md) | 동봉 데이터에서 필요한 지침을 로컬 검색합니다. |
| 웹 화면을 구현함 | [frontend-design](../third_party/frontend-design/skills/frontend-design/SKILL.md) | 실제 사용 흐름과 상태를 설계합니다. |
| 업무 용어가 확정되거나 중요한 결정이 생김 | [domain-modeling](../third_party/mattpocock-domain/skills/engineering/domain-modeling/SKILL.md) | 용어집과 필요한 설계 결정 기록을 작성합니다. |
| 실제 SQL이 있음 | [sql-code-review](../third_party/sql-code-review/skills/sql-code-review/SKILL.md) | 조인·집계·NULL 조건을 검토합니다. |
| 기존 코드에 변경을 추가함 | [test-gap-audit](../third_party/test-gap-audit/skills/test-gap-audit/SKILL.md) | 변경 범위의 검사 누락을 찾습니다. |
| 명시적으로 보안 검토를 요청함 | [security-best-practices](../third_party/security-best-practices/skills/.curated/security-best-practices/SKILL.md) | 지원 기술의 보안 참조를 읽습니다. |
| React19 동시성 작업임 | [react19-concurrent-patterns](../third_party/react-guidance/skills/react19-concurrent-patterns/SKILL.md) | 실제 버전에 맞는 원문만 읽습니다. |
| React18 클래스 배칭 회귀임 | [react18-batching-patterns](../third_party/react-guidance/skills/react18-batching-patterns/SKILL.md) | 일반 React 개발에는 적용하지 않습니다. |

하나의 작업에 표 전체를 적용하지 않습니다. 필요한 원문과 직접 참조만 읽습니다. 실제로 읽은 경로, 사용 이유와 확인한 결과를 handoff에 남깁니다. 라이선스와 고정 커밋은 각 폴더의 SOURCE.json을 확인합니다.

## 추가 기술과 개발 작업

기본 표에 없는 아키텍처, 언어, 프레임워크, 성능, 문서와 설계 작업은 [확장 색인](external-library.md)을 사용합니다. 검색은 동봉 파일만 읽으며 reference-only 항목을 기본으로 제외합니다.
