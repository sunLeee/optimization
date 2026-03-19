# ADR-036: deep-interview 모호성 5% 미만 종료 기준

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
deep-interview는 모호성이 수학적으로 5% 미만이 될 때까지 진행. Agent 자의 판단으로 건너뛰기 금지.

## 이유
- "충분히 알겠다"는 agent의 주관적 판단 → 잘못된 구현으로 이어짐
- 수학적 기준(5%) → 객관적 종료 조건
- 모호성 = 1 - (Goal×0.4 + Constraints×0.3 + Criteria×0.3)

## 예외
- 사용자가 "skip", "그냥 해줘" 명시 시 예외 허용
- 5분 무응답 = skip 판단 → omc-teams 합의 후 결정

## Gotchas
- skip 판단 시 omc-teams 3개 에이전트 만장일치 필요
- 불일치 시 Gemini(가장 깊은 thinking) 의견 따름
