# ADR-033: Rules vs Skills 분류 기준

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
- **rules**: 경로 기반 자동 로드 (항상 토큰 소비) → 핵심 요약만, `@skills/` 위임 링크
- **skills**: 명시적 호출 → 상세 가이드 + Gotchas + 예시

## 이유
- rules는 매 편집 시 로드 → 짧아야 컨텍스트 낭비 없음
- skills는 필요 시만 → 상세 내용 허용
- 애매하면 → skill (토큰 절약 효과 큼)

## Gotchas
- 모든 rules 파일은 마지막에 `@skills/` 링크 포함
- 중복 내용: rules에서 제거, skill에 상세 유지
