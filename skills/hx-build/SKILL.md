---
name: hx-build
description: 명시적으로 승인된 계획 안에서 작은 기능을 구현하고 기대값 검사와 실제 실행 근거를 연결합니다.
---

# 승인된 기능 구현

`plan`과 `status`로 현재 승인 판본을 확인합니다. 미해결 질문이나 승인 대기이면 hx-plan으로 돌아갑니다. 계약의 원문과 기대값을 직접 대조하고 핵심 입력부터 출력을 한 경로로 구현합니다.

`.harness-kit/docs/upstream-policy.md`, `.harness-kit/third_party/obra-superpowers/skills/test-driven-development/SKILL.md`와 같은 폴더의 `writing-good-tests.md`를 읽습니다. 의미 있는 계산과 분기에는 독립적으로 정한 기대값을 먼저 검사합니다. 미구현 import 오류와 실제 동작의 단언 실패는 구분해서 기록합니다. 기존 사용자 코드를 삭제하거나 문구 변경에 형식적인 테스트를 만들지 않습니다.

중요한 선택의 이유와 대안, 비용 및 관련 검사를 decision에 기록합니다. 새 선택이 범위와 동작을 바꾸면 먼저 사용자에게 질문합니다. 이미 승인한 선택을 반복해서 묻지 않습니다. 관련 `check --id C1` 뒤 status에서 현재 근거를 확인합니다.

사용자에게 입력, 처리, 출력과 확인한 범위를 설명합니다. 화면이 있으면 사람이 직접 확인할 절차와 기대 결과를 제공합니다. 사용자가 직접 보지 않은 결과를 observe에 기록하지 않습니다. 문서는 hx-document를 적용합니다.

API, 웹 화면, SQL, 명시적인 보안 요청 또는 기존 코드의 테스트 공백이 있으면 `.agents/skills/hx-specialist/SKILL.md`에서 해당 항목만 선택해 읽습니다.

승인 후 `.harness-kit/docs/external-routing.md`의 실행·병렬 항목에 따라 executing-plans와 조건에 맞는 원문을 직접 읽습니다.
