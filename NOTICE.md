# 배포 범위와 제3자 고지

이 패키지는 요구사항, 계획 승인과 검사 결과를 연결하는 로컬 개발 도구입니다. 자체 코드와 스킬, 일반 문서, 테스트와 합성 예제로 구성합니다. 프로젝트별 원문과 작업 기록, 사용자 승인 문구는 배포하지 않습니다.

## 실제 포함한 제3자 파일

| 원본 | 판본과 포함 범위 | 고지 |
|---|---|---|
| obra/superpowers | 커밋 `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`의 스킬 4개와 직접 참조 4개입니다. | [MIT LICENSE](third_party/obra-superpowers/LICENSE), [출처 및 파일 해시](third_party/obra-superpowers/SOURCE.json) |
| snflkd/fluent-korean | 커밋 `ce8683f0eba8cddb91de4dcd151425ff73e60498`의 코딩용·비코딩용 원문입니다. | [MIT LICENSE](third_party/fluent-korean/LICENSE), [출처 및 파일 해시](third_party/fluent-korean/SOURCE.json) |

해당 원문과 저작권·허가 고지를 그대로 보존합니다. 각 프로젝트의 전체 플러그인, 실행기나 자동 훅을 포함한 것으로 표시하지 않습니다. 자체 적용 안내는 [upstream-policy](docs/upstream-policy.md)에 분리했습니다. MIT 고지는 해당 제3자 자료에 적용되며 이를 자체 코드 전체의 별도 라이선스 선언으로 해석하지 않습니다.

## 추가한 기술별 원문

| 원본 | 포함 범위 | 원래 고지와 출처 |
|---|---|---|
| anthropics/skills | frontend-design 원문 | [Apache-2.0](third_party/frontend-design/skills/frontend-design/LICENSE.txt), [SOURCE](third_party/frontend-design/SOURCE.json) |
| openai/skills | security-best-practices와 언어별 참조 10개 | [Apache-2.0](third_party/security-best-practices/skills/.curated/security-best-practices/LICENSE.txt), [SOURCE](third_party/security-best-practices/SOURCE.json) |
| github/awesome-copilot | sql-code-review 원문 | [MIT](third_party/sql-code-review/LICENSE), [SOURCE](third_party/sql-code-review/SOURCE.json) |
| github/awesome-copilot | test-gap-audit 원문과 coverage_map.py | [MIT](third_party/test-gap-audit/LICENSE), [SOURCE](third_party/test-gap-audit/SOURCE.json) |

고정 커밋과 원본 파일별 SHA-256은 각 SOURCE.json에 있습니다. 제3자 원문은 수정하지 않았습니다. 자체 코드와 자체 문서에는 루트 [MIT LICENSE](LICENSE)를 적용합니다. 제3자 파일은 각 원래 라이선스를 유지합니다. 외부 모델이나 플러그인 전체를 연결하지 않습니다.

## 개념 참고

명세 기반 작업의 개념 참고는 [GitHub Spec Kit](https://github.com/github/spec-kit), [OpenSpec](https://github.com/Fission-AI/OpenSpec)입니다. 커밋 형식은 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)를 참고합니다. 이 도구들의 CLI와 코드는 포함하지 않습니다.

공개 파일은 `public-manifest.json`의 정확한 목록으로 관리합니다. 루트 Git 메타데이터와 캐시는 배포에서 제외하며 목록에 넣을 수 없습니다. 그 밖의 목록 밖 파일, 잘못된 경로와 배포 대상 심볼릭 링크를 거부합니다. 파일 내용의 공개 적합성이나 사용자의 배포 권한까지 자동 인증하지 않습니다. 공개 배포본의 URL과 판본은 저장소에서 확인합니다. ZIP 생성만으로 게시 완료를 주장하지 않습니다.

## 요구와 API 설계 보강

`proyecto26/system-design-skills`의 고정 커밋 `a70772efb956e8c9b78ef5b7538dee00cc3b9263`에서 requirements-scoping과 api-design 및 동봉 참조를 포함했습니다. [MIT LICENSE](third_party/system-design-skills/LICENSE)와 [원본 해시](third_party/system-design-skills/SOURCE.json)를 보존했습니다. 전체 플러그인과 미포함 스킬은 설치하지 않습니다.

React 상태 처리에는 `github/awesome-copilot`의 커밋 `5269f7ea2d6c3a9bfda5ed878b6726cf509121fd`에서 react19-concurrent-patterns와 react18-batching-patterns 및 참조 5개를 포함했습니다. [MIT LICENSE](third_party/react-guidance/LICENSE)와 [원본 해시](third_party/react-guidance/SOURCE.json)를 보존했습니다.

## 추가 개발 자료

Superpowers의 기존 고정 커밋에서 추가한 7개 스킬과 동반 자료에도 동봉 MIT 고지를 적용합니다. system-design-skills의 설계·책임 분리·저장 스킬에도 기존 MIT 고지를 유지합니다. 정확한 파일은 각 SOURCE.json에 기록했습니다.

OpenAI의 PDF와 Jupyter Notebook은 [원본 출처](third_party/openai-task-skills/SOURCE.json)와 각 스킬 폴더의 LICENSE.txt를 포함하며 Apache-2.0 조건을 유지합니다. Trail of Bits의 property-based-testing은 [출처](third_party/data-quality-extra/SOURCE.json)와 [CC BY-SA 4.0 고지](third_party/data-quality-extra/LICENSE)를 보존한 미수정 원문입니다. 이 제3자 자료에 루트 MIT 라이선스를 덮어씌우지 않습니다.

Matt Pocock의 domain-modeling은 [MIT LICENSE](third_party/mattpocock-domain/LICENSE)와 두 동봉 서식을 포함합니다. 고정 판본과 미수정 원본 해시는 [SOURCE.json](third_party/mattpocock-domain/SOURCE.json)에 있습니다.

UI UX Pro Max의 검색 스킬과 Python 스크립트, CSV 및 참조 문서는 [MIT LICENSE](third_party/ui-ux-pro-max/LICENSE)를 유지합니다. 원본 커밋과 파일별 해시는 [SOURCE.json](third_party/ui-ux-pro-max/SOURCE.json)에 있습니다. 전체 플러그인이나 갤러리를 설치한 것은 아닙니다.

## 확장 라이브러리

다음 자료는 고정 Git 커밋의 원문이며 원래 라이선스를 유지합니다. 파일별 출처·SHA-256·Git blob ID는 각 SOURCE.json에 있습니다.

| 자료 | 포함 범위 | 고지 |
|---|---|---|
| Matt Pocock | engineering 전체와 직접 의존 productivity 7개 | [MIT](third_party/mattpocock-library/LICENSE), [출처](third_party/mattpocock-library/SOURCE.json) |
| Jeffallan | skills 전체 | [MIT](third_party/jeffallan-library/LICENSE), [출처](third_party/jeffallan-library/SOURCE.json) |
| Addy Osmani | skills와 동반 참조·문서·역할·스크립트 | [MIT](third_party/addyosmani-library/LICENSE), [출처](third_party/addyosmani-library/SOURCE.json) |
| Impeccable | Codex용 스킬과 동반 자료 | [Apache-2.0](third_party/impeccable-library/LICENSE), [제3자 고지](third_party/impeccable-library/NOTICE.md), [출처](third_party/impeccable-library/SOURCE.json) |
| Ponytail | 6개 스킬과 참조 문서·스크립트·벤치마크 기록 | [MIT](third_party/ponytail-library/LICENSE), [출처](third_party/ponytail-library/SOURCE.json) |

플러그인과 훅을 등록하지 않으며 원문의 실행기 자동 다운로드를 허용하지 않습니다. 제3자 벤치마크는 원본 조건의 자료일 뿐 이 툴킷의 성능 수치가 아닙니다.
