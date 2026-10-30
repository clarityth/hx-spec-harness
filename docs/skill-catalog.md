# 실제 포함된 스킬과 적용 경로

이 패키지는 자체 스킬 11개와 외부 스킬 원문 8개를 포함합니다. 한국어 작성을 위한 fluent-korean의 코딩용·비코딩용 원문도 함께 포함합니다. 외부 원문은 `third_party/`에 있고, 자체 스킬이 필요한 때 그 경로를 명시적으로 읽도록 연결합니다. 전체 플러그인이나 자동 훅을 설치한 것은 아닙니다.

## 자체 스킬

| 파일 | 사용 시점 | 외부 원문 연결 |
|---|---|---|
| [hx-start](../skills/hx-start/SKILL.md) | 원문 조사와 작업 재개 | hx-plan으로 연결합니다. |
| [hx-discover](../skills/hx-discover/SKILL.md) | 업무 담당자 질문과 요구 확정 | 질문·답변 양식을 사용합니다. |
| [hx-plan](../skills/hx-plan/SKILL.md) | 구현 전 계획·질문·승인 | writing-plans를 읽습니다. |
| [hx-build](../skills/hx-build/SKILL.md) | 승인 범위의 기능 구현 | TDD와 writing-good-tests를 읽습니다. |
| [hx-data](../skills/hx-data/SKILL.md) | 원본 데이터와 조인 점검 | 로컬 inspect와 join을 사용합니다. |
| [hx-specialist](../skills/hx-specialist/SKILL.md) | 실제 과제에 웹 화면, 보안, SQL 또는 기존 코드 검사 공백이 있을 때 | 관련 외부 스킬 원문만 조건부로 읽습니다. |
| [hx-debug](../skills/hx-debug/SKILL.md) | 실제 오류 재현과 원인 수정 | systematic-debugging과 필요한 참조를 읽습니다. |
| [hx-verify](../skills/hx-verify/SKILL.md) | 요구와 현재 실행 결과 대조 | verification-before-completion을 읽습니다. |
| [hx-explain](../skills/hx-explain/SKILL.md) | 핵심 처리·선택·검증 설명 | hx-document로 문서 작성을 연결합니다. |
| [hx-document](../skills/hx-document/SKILL.md) | 개발 문서와 handoff 작성 | fluent-korean의 해당 원문을 읽습니다. |
| [hx-deliver](../skills/hx-deliver/SKILL.md) | 산출물과 handoff 최종 확인 | 완료 검증 원문과 hx-document를 적용합니다. |

설치 명령은 자체 스킬을 프로젝트의 `.agents/skills/`에 복사합니다. 외부 원문은 `.harness-kit/third_party/`에 복사합니다. 전역 설치를 하지 않습니다. 실행 환경의 자동 발견은 별도로 확인해야 합니다. 자동 발견이 안 되면 자체 SKILL.md를 직접 읽도록 지시합니다.

## 포함한 외부 원문

| 원문 | 패키지 안 실제 파일 | 출처와 고지 |
|---|---|---|
| 계획 작성 | [writing-plans/SKILL.md](../third_party/obra-superpowers/skills/writing-plans/SKILL.md) | [고정 커밋 원문](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/writing-plans/SKILL.md) |
| 테스트 주도 개발 | [test-driven-development/SKILL.md](../third_party/obra-superpowers/skills/test-driven-development/SKILL.md), [writing-good-tests.md](../third_party/obra-superpowers/skills/test-driven-development/writing-good-tests.md) | [고정 커밋 원문](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/test-driven-development/SKILL.md) |
| 체계적 디버깅 | [systematic-debugging/SKILL.md](../third_party/obra-superpowers/skills/systematic-debugging/SKILL.md), [원인 추적](../third_party/obra-superpowers/skills/systematic-debugging/root-cause-tracing.md), [다층 검증](../third_party/obra-superpowers/skills/systematic-debugging/defense-in-depth.md), [조건 기반 대기](../third_party/obra-superpowers/skills/systematic-debugging/condition-based-waiting.md) | [고정 커밋 원문](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/systematic-debugging/SKILL.md) |
| 완료 전 검증 | [verification-before-completion/SKILL.md](../third_party/obra-superpowers/skills/verification-before-completion/SKILL.md) | [고정 커밋 원문](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/verification-before-completion/SKILL.md) |
| 한국어 문장 | [코딩용 원문](../third_party/fluent-korean/plugins/fluent-korean/output-styles/fluent-korean.md), [비코딩용 원문](../third_party/fluent-korean/plugins/fluent-korean/output-styles/fluent-korean-not-coding.md) | [고정 커밋 원문](https://github.com/snflkd/fluent-korean/tree/ce8683f0eba8cddb91de4dcd151425ff73e60498/plugins/fluent-korean/output-styles) |
| 웹 화면 설계 | [frontend-design/SKILL.md](../third_party/frontend-design/skills/frontend-design/SKILL.md) | [Anthropic 고정 커밋](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design/SKILL.md), [Apache-2.0](../third_party/frontend-design/skills/frontend-design/LICENSE.txt), [SOURCE.json](../third_party/frontend-design/SOURCE.json) |
| 언어별 보안 모범 사례 | [security-best-practices/SKILL.md](../third_party/security-best-practices/skills/.curated/security-best-practices/SKILL.md)와 [references](../third_party/security-best-practices/skills/.curated/security-best-practices/references/javascript-general-web-frontend-security.md) 등 10개 원문 | [OpenAI 고정 커밋](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-best-practices/SKILL.md), [Apache-2.0](../third_party/security-best-practices/skills/.curated/security-best-practices/LICENSE.txt), [SOURCE.json](../third_party/security-best-practices/SOURCE.json) |
| SQL 코드 검토 | [sql-code-review/SKILL.md](../third_party/sql-code-review/skills/sql-code-review/SKILL.md) | [GitHub 고정 커밋](https://github.com/github/awesome-copilot/blob/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/sql-code-review/SKILL.md), [MIT](../third_party/sql-code-review/LICENSE), [SOURCE.json](../third_party/sql-code-review/SOURCE.json) |
| 기존 코드의 검사 공백 | [test-gap-audit/SKILL.md](../third_party/test-gap-audit/skills/test-gap-audit/SKILL.md), [coverage_map.py](../third_party/test-gap-audit/skills/test-gap-audit/scripts/coverage_map.py) | [GitHub 고정 커밋](https://github.com/github/awesome-copilot/blob/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/test-gap-audit/SKILL.md), [MIT](../third_party/test-gap-audit/LICENSE), [SOURCE.json](../third_party/test-gap-audit/SOURCE.json) |

Superpowers는 [MIT LICENSE](../third_party/obra-superpowers/LICENSE)와 [SOURCE.json](../third_party/obra-superpowers/SOURCE.json)을 포함합니다. fluent-korean도 [MIT LICENSE](../third_party/fluent-korean/LICENSE)와 [SOURCE.json](../third_party/fluent-korean/SOURCE.json)을 포함합니다. 원본 바이트와 고정 판본의 해시는 출처 기록에서 확인합니다. 라이선스 고지를 제거하지 않습니다.

새로 포함한 네 후보는 `hx-specialist`가 실제 기술과 요청 범위를 확인한 뒤에만 읽습니다. `frontend-design`은 코드와 사용자 직접 화면 확인을 돕습니다. `security-best-practices`는 원문이 정한 명시적 보안 요청 조건을 따르고, 적용 언어·프레임워크의 참조 문서만 읽습니다. `sql-code-review`는 실제 SQL이 있을 때만 사용합니다. `test-gap-audit`는 기존 코드의 변경 범위에 있는 테스트 공백을 찾는 데 사용합니다. 원문을 포함한 사실은 스킬을 자동 호출하거나 보안성과 화면 품질을 입증하지 않습니다.

## 현재 작업에 맞춘 적용

[외부 원문 적용 규칙](upstream-policy.md)은 사용자 승인, 실행 인계, 테스트 범위, Git 정책과 한국어 메타데이터 처리를 명시합니다. 원문의 미포함 실행기 스킬을 자동 호출하지 않습니다. 원문 파일을 그대로 보존한 것과 원문의 모든 실행 절차를 사용한 것은 구분합니다. 실제로 읽거나 실행한 범위만 프로젝트 handoff에 기록합니다.

다음 두 도구는 참고 링크이며 **이번 패키지에는 포함하지 않았습니다**. 현재 계획·구현·검증에 필요한 의존성으로 채택하지 않았습니다.

- [Ponytail의 단일 SKILL.md](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/skills/ponytail/SKILL.md): 작업 범위를 작게 유지하는 참고 자료입니다.
- [UI UX Pro Max의 SKILL.md](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/.claude/skills/ui-ux-pro-max/SKILL.md): UI 검색이 별도로 필요한 경우 검토합니다. SKILL.md 외 검색 스크립트와 데이터가 필요하므로 한 파일만 복사해 실행 가능하다고 표시하지 않습니다.
