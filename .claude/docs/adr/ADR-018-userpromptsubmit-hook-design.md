# ADR-018: UserPromptSubmit Hook으로 태스크 자동 감지

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`settings.json`의 UserPromptSubmit hook이 구현/생성 키워드를 regex로 감지하여 [TASK-DETECTED] 출력.

## 이유
- 사용자가 매번 `ulw deep-interview ralplan`을 직접 타이핑하지 않아도 됨
- 일관된 워크플로우 강제
- regex + haiku AI fallback으로 감지 정확도 향상

## 구현 세부사항
- Regex 1차: `구현|implement|추가해|fix|add|create|build|refactor`
- haiku AI 2차 (regex 미감지 시): TASK/QUERY 분류
- 제외 키워드: `공유|알고싶|진행상황|설명해|언제|얼마나`

## Gotchas
- Claude가 hook 지시를 무시하는 경우 있음 → 사용자 재요청 필요
- 상태 조회 질문에도 발동 가능 (false positive)
