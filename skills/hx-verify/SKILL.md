---
name: hx-verify
description: 완료를 보고하기 전에 원문, 승인 계획, 현재 코드와 실제 검사 근거를 독립적으로 대조합니다.
---

# 현재 결과 검증

`.harness-kit/docs/upstream-policy.md`와 `.harness-kit/third_party/obra-superpowers/skills/verification-before-completion/SKILL.md`를 읽습니다. 원문과 현재 계획, 구현과 검사 내용을 직접 대조합니다. plan의 승인 상태를 확인한 뒤 필요한 check를 실제 실행합니다. 출력과 종료 코드, 실행 범위를 읽습니다.

process의 종료 0과 behavior의 기대값 충족은 구분합니다. 실행 0건, 건너뜀, 오류와 오래된 근거를 통과로 처리하지 않습니다. 테스트가 현재 출력을 정답으로 다시 사용하지 않는지 확인합니다. 구현자의 성공 보고를 그대로 검증 결과로 쓰지 않습니다.

manual 요구는 사용자가 실제 관찰했다고 보고했을 때만 observe에 남깁니다. 이 기록은 인증되지 않은 자기보고입니다. 자동 검사, 사용자 관찰과 미확인을 구분합니다. handoff.md의 명령, 파일 링크와 결과 설명을 실제 근거에 대조합니다. 문체만 다듬고 사실 확인을 생략하지 않습니다.

웹 화면, SQL, 명시적인 보안 요청 또는 기존 코드의 테스트 공백이 있으면 `.agents/skills/hx-specialist/SKILL.md`에서 해당 항목만 선택해 읽습니다.

리뷰가 필요한 변경은 `.harness-kit/docs/external-routing.md`의 리뷰 원문을 읽습니다. 파싱·변환의 불변조건이 있으면 property-based-testing 적용을 검토합니다.
