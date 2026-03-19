# ADR-020: AskUserQuestion/deep-interview 전 omc-teams 사전조사 의무

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
AW-003/AW-004: AskUserQuestion 전, deep-interview 시작 전 반드시 omc-teams로 codex+gemini 병렬 조사.

## 이유
- 단일 AI 관점의 편향 제거
- 사전조사 없이 질문 시 질문 자체가 피상적
- 만장일치 → 즉시 진행, 불일치 → Gemini 의견 우선
- 5분 무응답 = skip → omc-teams 합의 후 진행

## 결과
- setup.md § 3에 프롬프트 전달 표준 정의
- 쿼리 파일 → omc-teams 실행 → 결과 수집 → deep-interview
