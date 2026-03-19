---
name: convention-conways-law
description: Conway's Law. 소프트웨어 구조는 이를 설계하는 조직의 커뮤니케이션 구조를 반영한다.
user-invocable: true
triggers:
  - "Conway's Law"
  - "콘웨이의 법칙"
  - "팀 구조"
  - "조직 구조"
---

# convention-conways-law

**@AW-024** | @docs/design/ref/team-operations.md § AW-024

Conway's Law: "시스템을 설계하는 조직은 그 조직의 커뮤니케이션 구조를 닮은 설계를 만들어낸다." (Mel Conway, 1967)

## VIOLATION 1: 팀 경계와 모듈 경계 불일치

```python
# 상황: 팀 A = 데이터 수집, 팀 B = 분석, 팀 C = 리포트
# VIOLATION: 모듈이 팀 경계와 다르게 나뉨
# libs/utils/data.py     ← 팀 A + B + C가 모두 편집
# libs/utils/analysis.py ← 팀 A + B가 함께 편집
# libs/utils/report.py   ← 팀 B + C가 함께 편집
# 결과: 잦은 충돌, 의존성 혼재, PR 블로킹

# CORRECT: 팀 경계 = 모듈 경계 (Inverse Conway Maneuver)
# libs/data/          ← 팀 A 전담 (데이터 수집)
# libs/processing/    ← 팀 B 전담 (분석/처리)
# agents/format/      ← 팀 C 전담 (리포트)
# 인터페이스: 팀 간 계약은 명시적 API로 정의
```

## VIOLATION 2: 모노레포인데 팀 소유권 불명확

```python
# VIOLATION: 어느 팀이 어느 파일을 소유하는지 불명확
# libs/utils.py (3개 팀이 모두 수정)
# → 결과: 누가 리뷰해야 할지 불명확, 품질 관리 어려움

# agents/__init__.py (팀 A, B, C 모두 편집)
```

```python
# CORRECT: CODEOWNERS 파일로 팀 소유권 명시
# .github/CODEOWNERS
# libs/data/          @team-data-collection
# libs/processing/    @team-analysis
# agents/format/      @team-report
# libs/utils/         @team-platform  # 공통 인프라팀
```

## Conway's Law 활용: Inverse Conway Maneuver

목표 시스템 아키텍처를 먼저 정의하고, 그에 맞춰 팀 구조를 조정한다.

```
원하는 아키텍처:
  [데이터 수집] → [처리 파이프라인] → [분석 에이전트] → [리포트]

팀 구조 설계:
  Team A: 데이터 수집 (libs/data/)
  Team B: 파이프라인 (libs/processing/)
  Team C: 에이전트 (agents/)
  Team D: 리포트/CLI (apps/)
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-024 | @docs/design/ref/team-operations.md § AW-024 | Conway's Law |
| @AW-020 | @docs/design/ref/team-operations.md § AW-020 | SoC — 관심사 경계 = 팀 경계 |
| Git Workflow | CLAUDE.md § Git Workflow | PR은 하나의 설계 결정 |

## 참조

- @docs/design/ref/team-operations.md § AW-024
- @.claude/skills/convention-soc/SKILL.md
- @.claude/skills/convention-solid-srp/SKILL.md
