# ADR-002: ulw + deep-interview + ralplan 항상 묶기

- **상태**: Accepted
- **날짜**: 2026-03-19
- **결정자**: sunLeee

## 맥락

모든 구현 요청에 대해 "그냥 해줘" 방식으로 즉시 구현하면 다음 문제가 발생한다:
1. 요구사항이 5% 이상 모호한 상태에서 구현 시작 → 재작업 필요
2. 병렬 실행 없이 순차 작업 → 시간 낭비
3. 합의 없는 계획 → architect/critic 검토 부재 → 품질 하락
4. "잘못 만든 것을 잘 만드는" 문제 (Build the wrong thing right)

## 결정

**모든 구현 요청(구현/fix/add/create/build)에 대해 반드시 아래 순서로 진행:**

```
STEP 1: omc-teams 사전조사 (codex + gemini 병렬)
STEP 2: ultrawork (병렬 실행 엔진 준비)
STEP 3: deep-interview (모호성 5% 미만까지)
STEP 4: ralplan (Planner → Architect → Critic 합의)
STEP 5: ralph (구현 루프, max 100회)
```

## 이유

- **deep-interview 전 사전조사**: 인터뷰 질문이 더 구체적이고 맥락에 맞음 (AW-003)
- **ultrawork**: 독립 태스크를 병렬 실행하여 시간 단축
- **deep-interview**: 모호성 수학적 측정 후 5% 미만에서만 진행 (AW-005)
- **ralplan**: Planner → Architect → Critic 합의 → "올바른 것을 올바르게 만들기"
- **ralph max 100**: 검증 루프로 완성도 보장 (AW-007)

## 대안 검토

| 대안 | 이유 채택 안 함 |
|------|----------------|
| 즉시 구현 | 요구사항 모호성으로 재작업률 높음 |
| deep-interview만 | 사전조사 없으면 질문이 피상적 |
| ralplan만 | 모호성 측정 없이 계획 → 방향 오류 가능 |

## 강제 메커니즘

`.claude/settings.json` UserPromptSubmit 훅이 키워드 감지 시 자동 발동.
`TASK-MODE-ACTIVATED` → 4단계 워크플로우 강제.

## 결과

- **긍정**: 구현 품질 향상, 재작업 감소, 모호성 측정 가능
- **부정**: 빠른 단순 fix에도 과정이 무거울 수 있음
- **완화**: "skip", "그냥 해줘" 명시 시 예외 허용

## 참조

- [hooks-guide-ko.md](../hooks-guide-ko.md) § TASK-MODE-ACTIVATED
- [settings.json](../../settings.json) § UserPromptSubmit
- [team-operations.md](../team-operations.md) § AW-003, AW-005, AW-007
