# ADR-038: 코드 리뷰 + 리팩토링 원칙

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
**코드 리뷰**: adversarial-review skill로 레드팀/블루팀 관점. 15개 우선순위, 요청받은 코드만.
**리팩토링**: 테스트 먼저 → 리팩토링 → 동일 테스트 통과 확인.

## 이유
- Surgical Changes 원칙: 관련 없는 코드 개선 금지
- Boy Scout Rule: 발견했을 때보다 조금 더 깨끗하게 (단, 범위 초과 금지)
- Kernighan's Law: 디버깅은 코딩보다 2배 어려움 → 단순하게 작성

## 도구
- `code-review` skill: check-* 스킬 조합
- `adversarial-review` skill: 레드팀/블루팀
- `code-refactor` skill: 체계적 리팩토링

## Gotchas
- 리팩토링 중 새 기능 추가 금지
- 타인 코드 개선은 별도 PR
