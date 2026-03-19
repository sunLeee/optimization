---
name: convention-adr
triggers:
  - "convention adr"
description: Architecture Decision Record 작성 규칙. 되돌리기 어려운 결정에 ADR 필수.
user-invocable: true
---

# convention-adr

## Rule of Reversibility

| 유형 | 예시 | 처리 |
|------|------|------|
| 되돌리기 쉬운 | 변수명, 함수명, 주석 | 바로 결정, ADR 불필요 |
| 되돌리기 어려운 | 파일 포맷, 좌표계, API 계약, DB 스키마 | ADR 작성 → ralplan 합의 |

**상황 1**: 데이터 저장 포맷을 CSV→Parquet 변경 → ADR 필수 (되돌리기 어려운 결정)
**상황 2**: 변수명 `data` → `zone_data` 변경 → ADR 불필요

## ADR 표준 포맷 (claude-config 기준)

```markdown
# ADR-{number}: {제목}

- **상태**: Accepted | Proposed | Deprecated | Superseded
- **날짜**: YYYY-MM-DD
- **범용 여부**: ✅ 모든 프로젝트 적용 가능 | ⚠️ 프로젝트 특화

## 맥락
왜 이 결정이 필요했는가 — 문제 상황.

## 결정
무엇을 결정했는가 — 한 문단으로 명확히.

## 이유
왜 이 결정이 최선인가 — 근거 나열.

## 대안 검토 (선택)

| 대안 | 거부 이유 |
|------|---------|
| 대안A | 이유 |

## 결과
긍정적 영향 + 부정적 trade-off.

## Gotchas (선택)
- 주의사항

## 참조 (선택)
- 관련 skill/doc 링크
```

## 저장 위치

`.claude/docs/adr/ADR-{number}-{kebab-subject}.md`

**상황 1**: `ADR-004-pep8-python-style-guide.md` — Python 스타일 결정
**상황 2**: ADR 작성 전 ralplan으로 합의 먼저 (AW-009)

## 번호 규칙

기존 최대 ADR 번호 + 1. `.claude/docs/adr/` 목록 확인 후 채번.
```bash
ls .claude/docs/adr/ | sort | tail -1  # 마지막 번호 확인
```

## Gotchas (실패 포인트)

- ADR은 '결정 이유'가 핵심 — 단순 선택만 기록하면 미래에 맥락 분실
- 과도한 문서화 금지 — 되돌리기 쉬운 결정에는 ADR 불필요 (AW-009)
- ADR 번호 순서는 시간 순 — 번호 재사용 또는 건너뜀 금지
- 'Consequences' 섹션에 긍정적 결과와 부정적 trade-off 모두 기록해야 함
