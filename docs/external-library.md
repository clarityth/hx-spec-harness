# 동봉 외부 스킬 전체 색인

기본 27개 선택표로 충분하지 않은 과제에서 Codex가 이 색인을 검색합니다. 사용자에게 웹에서 스킬을 찾으라고 요청하지 않습니다. 실제 원문과 참조 파일을 읽은 뒤 현재 과제에 적용할 부분만 선택합니다.

총 SKILL.md 153개이며 같은 출처·판본·내용의 중복 1개를 제외하면 152개입니다. 이름이 같아도 제작자가 다른 구현은 별개 자료입니다. 포함 개수는 실행 효과의 근거가 아닙니다.

```sh
python3 .harness-kit/tools/find_external_skills.py "아키텍처"
python3 .harness-kit/tools/find_external_skills.py "react testing"
```

검색은 동봉 JSON만 읽습니다. 네트워크, 설치와 스킬 실행을 하지 않습니다. 반환 순서는 문자열 관련도이며 품질 점수가 아닙니다. `reference-only`는 기본 검색에서 제외합니다. `--include-reference`는 목록 열람 옵션이며 실행 허가가 아닙니다.

| 출처 | 원문 수 |
|---|---|
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 6 |
| [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills) | 67 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 25 |
| [anthropics/skills](https://github.com/anthropics/skills) | 1 |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | 4 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 28 |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 1 |
| [obra/superpowers](https://github.com/obra/superpowers) | 11 |
| [openai/skills](https://github.com/openai/skills) | 3 |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 1 |
| [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) | 5 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 1 |

## 적용 상태

- `core`: 기존 기본 선택표에 연결한 원문입니다.
- `conditional`: 기술과 작업 조건이 맞을 때 검토합니다. 설치와 행동 검증을 모두 완료했다는 뜻이 아닙니다.
- `document-fallback`: 런처를 실행하지 않고 동봉 문서만 읽습니다.
- `reference-only`: 시험 중 호출하지 않습니다. 자동 UI, 외부 게시·설정, 외부 서비스와 연결되는 절차가 포함돼 있습니다.

추가 원문은 [적용 정책](upstream-policy.md)의 확장 자료 제한을 먼저 적용합니다. 이전 원문을 읽었다고 외부 모델, 플러그인, 훅, 업데이트, Git push를 실행하지 않습니다. 같은 역할의 스킬 여러 개를 동시에 전체 실행하지 않습니다.

## 개별 경로

| 이름 | 출처 | 적용 상태 | 원문 |
|---|---|---|---|
| api-and-interface-design | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/api-and-interface-design/SKILL.md) |
| browser-testing-with-devtools | addyosmani/agent-skills | reference-only | [파일](../third_party/addyosmani-library/skills/browser-testing-with-devtools/SKILL.md) |
| ci-cd-and-automation | addyosmani/agent-skills | reference-only | [파일](../third_party/addyosmani-library/skills/ci-cd-and-automation/SKILL.md) |
| code-review-and-quality | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/code-review-and-quality/SKILL.md) |
| code-simplification | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/code-simplification/SKILL.md) |
| constraint-driven-development | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/constraint-driven-development/SKILL.md) |
| context-engineering | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/context-engineering/SKILL.md) |
| debugging-and-error-recovery | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/debugging-and-error-recovery/SKILL.md) |
| deprecation-and-migration | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/deprecation-and-migration/SKILL.md) |
| documentation-and-adrs | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/documentation-and-adrs/SKILL.md) |
| doubt-driven-development | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/doubt-driven-development/SKILL.md) |
| frontend-ui-engineering | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/frontend-ui-engineering/SKILL.md) |
| git-workflow-and-versioning | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/git-workflow-and-versioning/SKILL.md) |
| idea-refine | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/idea-refine/SKILL.md) |
| incremental-implementation | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/incremental-implementation/SKILL.md) |
| interview-me | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/interview-me/SKILL.md) |
| observability-and-instrumentation | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/observability-and-instrumentation/SKILL.md) |
| performance-optimization | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/performance-optimization/SKILL.md) |
| planning-and-task-breakdown | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/planning-and-task-breakdown/SKILL.md) |
| security-and-hardening | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/security-and-hardening/SKILL.md) |
| shipping-and-launch | addyosmani/agent-skills | reference-only | [파일](../third_party/addyosmani-library/skills/shipping-and-launch/SKILL.md) |
| source-driven-development | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/source-driven-development/SKILL.md) |
| spec-driven-development | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/spec-driven-development/SKILL.md) |
| test-driven-development | addyosmani/agent-skills | conditional | [파일](../third_party/addyosmani-library/skills/test-driven-development/SKILL.md) |
| using-agent-skills | addyosmani/agent-skills | reference-only | [파일](../third_party/addyosmani-library/skills/using-agent-skills/SKILL.md) |
| property-based-testing | trailofbits/skills | core | [파일](../third_party/data-quality-extra/plugins/property-based-testing/skills/property-based-testing/SKILL.md) |
| frontend-design | anthropics/skills | core | [파일](../third_party/frontend-design/skills/frontend-design/SKILL.md) |
| impeccable | pbakaus/impeccable | document-fallback | [파일](../third_party/impeccable-library/.agents/skills/impeccable/SKILL.md) |
| angular-architect | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/angular-architect/SKILL.md) |
| api-designer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/api-designer/SKILL.md) |
| architecture-designer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/architecture-designer/SKILL.md) |
| atlassian-mcp | Jeffallan/claude-skills | reference-only | [파일](../third_party/jeffallan-library/skills/atlassian-mcp/SKILL.md) |
| chaos-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/chaos-engineer/SKILL.md) |
| cli-developer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/cli-developer/SKILL.md) |
| cloud-architect | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/cloud-architect/SKILL.md) |
| code-documenter | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/code-documenter/SKILL.md) |
| code-reviewer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/code-reviewer/SKILL.md) |
| cpp-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/cpp-pro/SKILL.md) |
| csharp-developer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/csharp-developer/SKILL.md) |
| database-optimizer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/database-optimizer/SKILL.md) |
| debugging-wizard | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/debugging-wizard/SKILL.md) |
| devops-engineer | Jeffallan/claude-skills | reference-only | [파일](../third_party/jeffallan-library/skills/devops-engineer/SKILL.md) |
| django-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/django-expert/SKILL.md) |
| django-storages-s3 | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/django-storages-s3/SKILL.md) |
| dotnet-core-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/dotnet-core-expert/SKILL.md) |
| embedded-systems | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/embedded-systems/SKILL.md) |
| fastapi-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/fastapi-expert/SKILL.md) |
| feature-forge | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/feature-forge/SKILL.md) |
| fine-tuning-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/fine-tuning-expert/SKILL.md) |
| flutter-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/flutter-expert/SKILL.md) |
| fullstack-guardian | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/fullstack-guardian/SKILL.md) |
| game-developer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/game-developer/SKILL.md) |
| golang-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/golang-pro/SKILL.md) |
| graphql-architect | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/graphql-architect/SKILL.md) |
| java-architect | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/java-architect/SKILL.md) |
| javascript-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/javascript-pro/SKILL.md) |
| kotlin-specialist | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/kotlin-specialist/SKILL.md) |
| kubernetes-specialist | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/kubernetes-specialist/SKILL.md) |
| laravel-specialist | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/laravel-specialist/SKILL.md) |
| legacy-modernizer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/legacy-modernizer/SKILL.md) |
| mcp-developer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/mcp-developer/SKILL.md) |
| microservices-architect | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/microservices-architect/SKILL.md) |
| ml-pipeline | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/ml-pipeline/SKILL.md) |
| monitoring-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/monitoring-expert/SKILL.md) |
| nestjs-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/nestjs-expert/SKILL.md) |
| nextjs-developer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/nextjs-developer/SKILL.md) |
| pandas-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/pandas-pro/SKILL.md) |
| php-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/php-pro/SKILL.md) |
| playwright-expert | Jeffallan/claude-skills | reference-only | [파일](../third_party/jeffallan-library/skills/playwright-expert/SKILL.md) |
| postgres-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/postgres-pro/SKILL.md) |
| prompt-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/prompt-engineer/SKILL.md) |
| python-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/python-pro/SKILL.md) |
| rag-architect | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/rag-architect/SKILL.md) |
| rails-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/rails-expert/SKILL.md) |
| react-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/react-expert/SKILL.md) |
| react-native-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/react-native-expert/SKILL.md) |
| rust-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/rust-engineer/SKILL.md) |
| salesforce-developer | Jeffallan/claude-skills | reference-only | [파일](../third_party/jeffallan-library/skills/salesforce-developer/SKILL.md) |
| secure-code-guardian | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/secure-code-guardian/SKILL.md) |
| security-reviewer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/security-reviewer/SKILL.md) |
| shopify-expert | Jeffallan/claude-skills | reference-only | [파일](../third_party/jeffallan-library/skills/shopify-expert/SKILL.md) |
| spark-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/spark-engineer/SKILL.md) |
| spec-miner | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/spec-miner/SKILL.md) |
| spring-boot-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/spring-boot-engineer/SKILL.md) |
| sql-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/sql-pro/SKILL.md) |
| sre-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/sre-engineer/SKILL.md) |
| swift-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/swift-expert/SKILL.md) |
| terraform-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/terraform-engineer/SKILL.md) |
| test-master | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/test-master/SKILL.md) |
| the-fool | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/the-fool/SKILL.md) |
| typescript-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/typescript-pro/SKILL.md) |
| vue-expert | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/vue-expert/SKILL.md) |
| vue-expert-js | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/vue-expert-js/SKILL.md) |
| websocket-engineer | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/websocket-engineer/SKILL.md) |
| wordpress-pro | Jeffallan/claude-skills | conditional | [파일](../third_party/jeffallan-library/skills/wordpress-pro/SKILL.md) |
| domain-modeling | mattpocock/skills | core | [파일](../third_party/mattpocock-domain/skills/engineering/domain-modeling/SKILL.md) |
| ask-matt | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/ask-matt/SKILL.md) |
| code-review | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/code-review/SKILL.md) |
| codebase-design | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/codebase-design/SKILL.md) |
| diagnosing-bugs | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/diagnosing-bugs/SKILL.md) |
| domain-modeling | mattpocock/skills | alias | [파일](../third_party/mattpocock-library/skills/engineering/domain-modeling/SKILL.md) |
| grill-with-docs | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/grill-with-docs/SKILL.md) |
| implement | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/implement/SKILL.md) |
| implement-spec | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/implement-spec/SKILL.md) |
| improve-codebase-architecture | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/improve-codebase-architecture/SKILL.md) |
| pr | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/pr/SKILL.md) |
| prototype | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/prototype/SKILL.md) |
| research | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/research/SKILL.md) |
| retro | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/retro/SKILL.md) |
| setup-matt-pocock-skills | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/setup-matt-pocock-skills/SKILL.md) |
| tdd | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/engineering/tdd/SKILL.md) |
| to-spec | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/to-spec/SKILL.md) |
| to-tickets | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/to-tickets/SKILL.md) |
| triage | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/triage/SKILL.md) |
| wayfinder | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/wayfinder/SKILL.md) |
| wizard | mattpocock/skills | reference-only | [파일](../third_party/mattpocock-library/skills/engineering/wizard/SKILL.md) |
| grill-me | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/grill-me/SKILL.md) |
| grilling | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/grilling/SKILL.md) |
| handoff | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/handoff/SKILL.md) |
| teach | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/teach/SKILL.md) |
| to-questionnaire | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/to-questionnaire/SKILL.md) |
| wait-what | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/wait-what/SKILL.md) |
| writing-for-agents | mattpocock/skills | conditional | [파일](../third_party/mattpocock-library/skills/productivity/writing-for-agents/SKILL.md) |
| brainstorming | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/brainstorming/SKILL.md) |
| dispatching-parallel-agents | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/dispatching-parallel-agents/SKILL.md) |
| executing-plans | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/executing-plans/SKILL.md) |
| receiving-code-review | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/receiving-code-review/SKILL.md) |
| requesting-code-review | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/requesting-code-review/SKILL.md) |
| subagent-driven-development | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/subagent-driven-development/SKILL.md) |
| systematic-debugging | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/systematic-debugging/SKILL.md) |
| test-driven-development | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/test-driven-development/SKILL.md) |
| using-git-worktrees | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/using-git-worktrees/SKILL.md) |
| verification-before-completion | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/verification-before-completion/SKILL.md) |
| writing-plans | obra/superpowers | core | [파일](../third_party/obra-superpowers/skills/writing-plans/SKILL.md) |
| jupyter-notebook | openai/skills | core | [파일](../third_party/openai-task-skills/skills/.curated/jupyter-notebook/SKILL.md) |
| pdf | openai/skills | core | [파일](../third_party/openai-task-skills/skills/.curated/pdf/SKILL.md) |
| ponytail | DietrichGebert/ponytail | conditional | [파일](../third_party/ponytail-library/skills/ponytail/SKILL.md) |
| ponytail-audit | DietrichGebert/ponytail | conditional | [파일](../third_party/ponytail-library/skills/ponytail-audit/SKILL.md) |
| ponytail-debt | DietrichGebert/ponytail | conditional | [파일](../third_party/ponytail-library/skills/ponytail-debt/SKILL.md) |
| ponytail-gain | DietrichGebert/ponytail | reference-only | [파일](../third_party/ponytail-library/skills/ponytail-gain/SKILL.md) |
| ponytail-help | DietrichGebert/ponytail | reference-only | [파일](../third_party/ponytail-library/skills/ponytail-help/SKILL.md) |
| ponytail-review | DietrichGebert/ponytail | conditional | [파일](../third_party/ponytail-library/skills/ponytail-review/SKILL.md) |
| react18-batching-patterns | github/awesome-copilot | core | [파일](../third_party/react-guidance/skills/react18-batching-patterns/SKILL.md) |
| react19-concurrent-patterns | github/awesome-copilot | core | [파일](../third_party/react-guidance/skills/react19-concurrent-patterns/SKILL.md) |
| security-best-practices | openai/skills | core | [파일](../third_party/security-best-practices/skills/.curated/security-best-practices/SKILL.md) |
| sql-code-review | github/awesome-copilot | core | [파일](../third_party/sql-code-review/skills/sql-code-review/SKILL.md) |
| api-design | proyecto26/system-design-skills | core | [파일](../third_party/system-design-skills/skills/api-design/SKILL.md) |
| data-storage | proyecto26/system-design-skills | core | [파일](../third_party/system-design-skills/skills/data-storage/SKILL.md) |
| requirements-scoping | proyecto26/system-design-skills | core | [파일](../third_party/system-design-skills/skills/requirements-scoping/SKILL.md) |
| service-decomposition | proyecto26/system-design-skills | core | [파일](../third_party/system-design-skills/skills/service-decomposition/SKILL.md) |
| system-design | proyecto26/system-design-skills | core | [파일](../third_party/system-design-skills/skills/system-design/SKILL.md) |
| test-gap-audit | github/awesome-copilot | core | [파일](../third_party/test-gap-audit/skills/test-gap-audit/SKILL.md) |
| ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | core | [파일](../third_party/ui-ux-pro-max/.claude/skills/ui-ux-pro-max/SKILL.md) |
