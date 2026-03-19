# ADR-030: 3-agent 병렬 조사 합의 패턴

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
기술 결정 전 codex + gemini + claude 3개 에이전트 병렬 조사. 결과: 만장일치 → 즉시 진행, 불일치 → Gemini(가장 깊은 thinking) 우선.

## 이유
- 단일 AI 편향 제거
- 다모델 합의 → 더 나은 결정
- Gemini: 고성능 thinking 모델로 사내 사용 (opus 대체, AW-001)

## 구현
- `omc-teams 2:codex "주제" 3:gemini "주제"`
- 결과 `.omc/research/*.md`에 저장
- Claude가 종합

## Gotchas
- pane 번호 순차 증가 (1=메인, 2=첫째 worker, ...)
