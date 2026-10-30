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
