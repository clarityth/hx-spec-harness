---
name: hx-document
description: 개발 문서와 handoff.md를 실제 코드·검증 근거에 맞게 작성하고 한국어 문장과 사실을 별도로 검토합니다.
---

# 한국어 개발 문서와 인계

`.harness-kit/docs/writing-standard.md`와 `.harness-kit/third_party/fluent-korean/plugins/fluent-korean/output-styles/fluent-korean.md`를 끝까지 읽고 적용합니다. 비개발 조사 문서이면 같은 폴더의 fluent-korean-not-coding.md를 사용합니다. 원문 frontmatter를 실행 환경 설정으로 해석하지 않습니다.

문서의 독자와 목적을 정합니다. 실행 방법에는 실제 환경, 명령과 기대 결과를 씁니다. 구현 설명에는 핵심 입력의 처리 경로와 파일·함수를 연결합니다. 계획, 실제 구현, 실행 결과와 미확인을 구분합니다. 사용자와 AI의 행동을 섞지 않습니다.

handoff.md는 `.harness-kit/templates/handoff.md`의 구조를 참고해 현재 과제에 맞게 작성합니다. 계약과 상태, evidence를 상세 근거로 연결하고 전체 로그를 반복해서 복사하지 않습니다. 기존 문서가 있으면 현재 상태와 달라진 부분을 갱신합니다. 양식만 채워진 상태를 완성본으로 보고하지 않습니다.

먼저 코드·명세·명령 출력과 문서의 사실을 대조합니다. 다음으로 한국어 문장을 읽고 주체, 조건과 서술어를 확인합니다. 수정 뒤 기술적 의미와 수치, 담당 주체를 다시 대조합니다. 코드를 읽었다는 사실을 사용자의 이해로 기록하지 않습니다.
