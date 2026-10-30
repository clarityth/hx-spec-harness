---
name: hx-plan
description: 구현 전에 계획과 선택지를 작성하고 미해결 요구를 질문하며 사용자의 명시적 승인을 현재 판본에 연결합니다.
---

# 구현 전 계획과 질문

먼저 `.harness-kit/docs/upstream-policy.md`와 `.harness-kit/third_party/obra-superpowers/skills/writing-plans/SKILL.md`를 읽습니다. 목표, 범위, 파일별 책임, 구현 순서와 검증 명령을 구체화합니다. 계획의 길이는 작업에 맞춥니다. 원문의 별도 executor 스킬은 호출하지 않고 승인 뒤 hx-build로 진행합니다.

`.harness/plan.json`에는 goal, scope, acceptance, steps와 questions를 작성합니다. steps의 requirements와 checks는 계약 ID를 참조합니다. 결과를 바꿀 모호함과 선택은 질문, 영향, 선택지와 권장안을 제시해 사용자에게 묻습니다. 답변 없이 answered로 바꾸지 않습니다. 명시적 선택 위임도 범위와 근거를 기록합니다.

`python3 .harness-kit/hx.py --root . plan`으로 현재 계획을 보고 사용자에게 명시적인 승인을 요청합니다. 실제 답변을 받은 뒤에만 `plan-approve --actor user --quote TEXT --source SOURCE`로 근거를 기록합니다. SOURCE에는 현재 대화나 실제 로컬 승인 기록의 위치를 씁니다. AI의 검토나 이 명령 실행 자체는 사용자 승인이 아닙니다.

승인 범위 안의 구현과 검사는 이어서 진행합니다. 계획·계약·원문이 바뀌어 승인이 stale이면 변경 이유와 새 판본을 사용자에게 제시합니다. 구현 실패를 숨기려고 기대값을 바꾸지 않습니다. 사용자가 승인하지 않은 변경은 진행하지 않습니다.
