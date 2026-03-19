---
name: convention-pareto-rule
description: Pareto Rule (80/20). 80%의 효과는 20%의 원인에서 온다. 핵심 20%에 집중하라.
user-invocable: true
triggers:
  - "pareto"
  - "80/20"
  - "파레토"
  - "핵심 집중"
---

# convention-pareto-rule

**@AW-037** | @docs/design/ref/team-operations.md § AW-037

Pareto Rule: "80%의 결과는 20%의 원인에서 온다." (Vilfredo Pareto, 1906) 코드의 20%가 80%의 버그를 만들고, 20%의 기능이 80%의 사용을 차지한다.

## 적용 1: 성능 최적화에서 80/20

```python
# 측정 먼저 (AW-011 Rob Pike Rule) — 어느 20%가 80% 시간을 먹는지 확인
import cProfile
import pstats

def profile_pipeline() -> None:
    profiler = cProfile.Profile()
    profiler.enable()

    run_demand_analysis()  # 전체 파이프라인

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)  # 상위 10개 병목만 확인
    # 결과: load_csv()가 전체 시간의 70% → 여기만 최적화

# VIOLATION: 측정 없이 모든 곳을 최적화
def over_optimize_everything() -> None:
    # 전체를 최적화하다가 정작 병목은 그대로
    optimize_string_concat()      # 0.1% 효과
    optimize_list_comprehension() # 0.5% 효과
    # load_csv()는 손도 안 댐 → 70% 효과 미개선
```

## 적용 2: 기능 개발에서 80/20

```python
# 80%의 사용자는 다음 3가지 기능만 사용:
# 1. 기본 수요 분석
# 2. zone별 집계
# 3. CSV 출력

# VIOLATION: 사용 빈도 낮은 기능에 80% 시간 투자
def implement_all_features():
    # 나머지 20% 사용자를 위한 기능들:
    implement_excel_export()       # 사용자 5%
    implement_pdf_report()         # 사용자 8%
    implement_real_time_streaming() # 사용자 2%
    # 핵심 3가지는 미완성 상태

# CORRECT: 핵심 20%를 먼저 완성 (@AW-019 YAGNI와 연계)
def implement_core_features():
    implement_basic_demand_analysis()  # 80% 가치
    implement_zone_aggregation()       # 80% 가치
    implement_csv_output()             # 80% 가치
    # 나머지는 실제 요청 있을 때 추가
```

## 측정 기준 (AW-037 적용 체크)

```bash
# 어떤 기능이 80% 사용을 차지하는지 측정
grep -c "analyze_demand\|zone_aggregate\|csv_output" logs/access.log

# 어떤 코드가 80% 버그를 만드는지 확인
git log --oneline | grep "fix:" | head -20  # 수정 빈도 높은 모듈 파악
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-037 | @docs/design/ref/team-operations.md § AW-037 | Pareto Rule |
| @AW-011 | @docs/design/ref/team-operations.md § AW-011 | 측정 먼저 — Rob Pike |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 핵심만 |

## 참조

- @docs/design/ref/team-operations.md § AW-037
- @docs/design/ref/team-operations.md § AW-011
- @.claude/skills/convention-yagni/SKILL.md
