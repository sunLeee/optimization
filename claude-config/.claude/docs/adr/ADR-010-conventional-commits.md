# ADR-010: Conventional Commits + 필수 스코프

- **상태**: Accepted
- **날짜**: 2026-03-19

## 맥락
자유 형식 커밋 메시지는 CHANGELOG 자동 생성, 의미 파악, AI 컨텍스트 이해가 어려움.

## 결정
`type(scope): subject` 형식. **scope 필수** (없으면 거부).
주요 타입: feat/fix/docs/refactor/test/chore

## 이유
- scope로 변경 영역 즉시 파악
- CHANGELOG 자동 생성 가능
- AI agent가 변경 의도 파악 용이
- 타인 파일 불간섭 원칙과 연계

## 대안 검토
| 대안 | 거부 이유 |
|------|---------|
| 자유 형식 | 검색/파악 어려움 |
| scope 선택적 | 일관성 없음 |

## Gotchas
- Co-Authored-By 푸터 금지 (팀 정책)
- `#숫자` 포함 시 external repo에 cross-reference 생성 (삭제 불가)

## 결과
- check-commit-message skill로 검증
- pre-commit에 통합 가능
