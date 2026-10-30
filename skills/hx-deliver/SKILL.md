---
name: hx-deliver
description: 마무리 전에 현재 승인·산출물·검사와 handoff.md를 대조하고 실제 인계 상태를 구분해 보고합니다.
---

# 결과와 인계 문서 확인

원문의 산출물 조건과 현재 plan, status를 읽습니다. `.harness-kit/docs/upstream-policy.md`와 `.harness-kit/third_party/obra-superpowers/skills/verification-before-completion/SKILL.md`를 적용합니다. 변경 뒤 영향을 받은 검사를 실행하고 유효한 현재 결과를 확인합니다.

hx-document에 따라 handoff.md를 갱신합니다. 실행 명령을 재현하고 명세·코드·검사 링크를 확인합니다. 구현 선택과 한계, 사용자 직접 확인과 다음 작업을 실제 기록에 맞춥니다. 파일 존재만으로 문서 완성을 판정하지 않습니다. 프로젝트가 허용한 제출 경로와 파일 목록을 따릅니다.

freeze로 필수 파일과 자동 검사, 수동 확인 잔여를 대조합니다. 이 명령은 파일을 잠그거나 외부에 제출하지 않습니다. 수동 요구는 자기보고가 있어도 자동 통과 인증이 되지 않습니다. 실제 인계와 배포는 해당 시스템에서 따로 확인합니다.

작업을 끝내기로 결정했을 때만 close를 실행합니다. 닫은 뒤에는 status의 종료 표시 외 명령과 설명을 진행하지 않습니다. 실제로 끝내지 않은 확인을 완료로 표시하지 않습니다.
