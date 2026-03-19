---
name: convention-soc
description: SoC (Separation of Concerns). 서로 다른 관심사를 독립적인 모듈/레이어로 분리한다.
user-invocable: true
triggers:
  - "SoC"
  - "separation of concerns"
  - "관심사 분리"
  - "레이어 분리"
---

# convention-soc

**@AW-020** | @docs/design/ref/team-operations.md § AW-020

SoC: 시스템의 각 부분은 분리된 관심사를 다루어야 한다. 비즈니스 로직, 데이터 접근, 표현 로직이 섞이면 변경이 어려워진다.

## VIOLATION 1: 비즈니스 로직과 데이터 접근 혼재

```python
# VIOLATION: tool function에서 파일 읽기 + 비즈니스 로직 + 결과 포맷이 혼재
def analyze_demand(tool_context: ToolContext) -> dict:
    # 데이터 접근 관심사 (SoC 위반 — 비즈니스 로직과 혼재)
    df = pd.read_csv(tool_context.state["app:demand_file"])
    df = df.dropna()

    # 비즈니스 로직 관심사
    high_demand = df[df["demand"] > df["demand"].quantile(0.8)]
    zone_ranks = high_demand.groupby("zone_id")["demand"].sum()

    # 표현/포맷 관심사 (SoC 위반)
    result_str = "\n".join(
        f"Zone {z}: {v:.2f}" for z, v in zone_ranks.items()
    )
    return {"report": result_str}
```

```python
# CORRECT: 관심사 분리
# 데이터 접근 레이어 (libs/data/)
def load_demand_dataframe(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path).dropna()

# 비즈니스 로직 레이어 (libs/processing/)
def compute_high_demand_zones(df: pd.DataFrame) -> pd.Series:
    threshold = df["demand"].quantile(0.8)
    return df[df["demand"] > threshold].groupby("zone_id")["demand"].sum()

# 표현 레이어는 리포트 에이전트가 담당
# tool function = 오케스트레이션만
def analyze_demand(tool_context: ToolContext) -> dict:
    df = load_demand_dataframe(tool_context.state["app:demand_file"])
    zone_ranks = compute_high_demand_zones(df)
    return {"zone_ranks": zone_ranks.to_dict()}
```

## VIOLATION 2: 설정과 로직 혼재

```python
# VIOLATION: 설정값이 비즈니스 로직 안에 하드코딩
def process_zones(df: pd.DataFrame) -> pd.DataFrame:
    MAX_ZONES = 500             # 설정 관심사 — 로직 안에 혼재
    MIN_DEMAND = 10.0           # 설정 관심사
    return df[df["demand"] >= MIN_DEMAND].head(MAX_ZONES)
```

```python
# CORRECT: OmegaConf 설정으로 분리 — @AW-020 + ADR-020
def process_zones(
    df: pd.DataFrame, config: DictConfig
) -> pd.DataFrame:
    """zone 데이터를 처리한다.

    Logics:
        config에서 임계값을 읽어 필터링한다.
    """
    return (
        df[df["demand"] >= config.processing.min_demand]
          .head(config.processing.max_zones)
    )
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-020 | @docs/design/ref/team-operations.md § AW-020 | SoC — 관심사 분리 |
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — 함께 적용 |
| 코드 구성 | CLAUDE.md § 코드 구성 | 기능/도메인별 구성 |

## 참조

- @docs/design/ref/team-operations.md § AW-020
- @.claude/skills/convention-solid-srp/SKILL.md
- @.claude/skills/convention-adk-agent/SKILL.md
