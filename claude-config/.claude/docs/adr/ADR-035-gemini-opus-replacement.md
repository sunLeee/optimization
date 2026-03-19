# ADR-035: 사내 환경에서 Gemini로 Claude opus 대체

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
사내망에서 Claude opus 접근 불가 → **Gemini 최신 고성능 모델**로 대체 (AW-001).

## 이유
- 내부망 제한으로 Claude opus API 호출 불가
- Gemini: 고성능 thinking 모델 사용 가능
- 설계/분석/리뷰 등 opus 역할을 Gemini로 수행

## 적용 대상
- `analyst`, `architect`, `deep-executor`, `code-reviewer` → Gemini 모델 사용
- Claude: `claude-sonnet-4-6[1m]` 고정
- omc-teams gemini worker: `gemini-2.0-flash-thinking-exp` 권장
