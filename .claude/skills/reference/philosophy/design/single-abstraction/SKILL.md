---
name: convention-single-abstraction
description: Single Level of Abstraction (SLA). 함수 내 모든 코드는 같은 추상화 수준에 있어야 한다.
user-invocable: true
triggers:
  - "single level abstraction"
  - "SLA"
  - "추상화 수준"
  - "혼재된 추상화"
---

# convention-single-abstraction

**@AW-044** | @docs/design/ref/team-operations.md § AW-044

Single Level of Abstraction: 하나의 함수 안에서 고수준 로직과 저수준 구현이 혼재되면 읽기 어려워진다. 같은 추상화 수준의 코드만 함수에 넣어라.

## VIOLATION 1: 고수준과 저수준 혼재

```python
# VIOLATION: 파이프라인 함수가 고수준(의도)과 저수준(구현)을 혼재
def run_demand_analysis(config: DictConfig) -> dict:
    # 고수준: "데이터를 로드한다"
    df = load_demand_data(config.file_path)

    # 저수준 구현이 갑자기 등장 (추상화 수준 위반)
    df["demand"] = df["demand"].fillna(0)          # 저수준: fillna
    df = df[df["demand"].between(0, 1e6)]           # 저수준: between
    df["zone_id"] = df["zone_id"].astype(int)       # 저수준: astype

    # 고수준: "집계한다"
    result = aggregate_by_zone(df)

    # 저수준 구현 다시 등장
    output_path = f"{config.output_dir}/result_{datetime.now():%Y%m%d}.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)              # 저수준: json.dump

    return result
```

```python
# CORRECT: 같은 추상화 수준 유지
def run_demand_analysis(config: DictConfig) -> dict:
    """수요 분석 파이프라인을 실행한다.

    Logics:
        1. 데이터 로드 → 2. 전처리 → 3. 집계 → 4. 저장
        모든 단계가 같은 추상화 수준 (고수준 개념)
    """
    # 모두 고수준 — 저수준 구현은 각 함수 내부에 숨김
    df = load_demand_data(config.file_path)
    df = preprocess_demand(df)            # 저수준은 여기 안에
    result = aggregate_by_zone(df)
    save_analysis_result(result, config.output_dir)  # 저수준은 여기 안에
    return result

def preprocess_demand(df: pd.DataFrame) -> pd.DataFrame:
    """수요 데이터를 전처리한다. (저수준 구현 캡슐화)"""
    return (
        df.assign(demand=df["demand"].fillna(0))
          .loc[lambda x: x["demand"].between(0, 1e6)]
          .assign(zone_id=df["zone_id"].astype(int))
    )
```

## VIOLATION 2: ADK tool에서 추상화 수준 혼재

```python
# VIOLATION: tool이 조회 + 처리 + 저장 + 알림 동시에
def analyze_and_save_demand(tool_context: ToolContext) -> dict:
    file_path = tool_context.state["app:demand_file"]  # 조회 (저수준)
    df = pd.read_csv(file_path)                         # I/O (저수준)
    result = df.groupby("zone_id")["demand"].sum()      # 비즈니스 (고수준)
    output = result.to_dict()
    tool_context.state["agent:result"] = str(output)   # 저장 (저수준)
    return output
```

```python
# CORRECT: 각 tool은 하나의 추상화 수준만
def analyze_demand(tool_context: ToolContext) -> dict:
    """수요를 분석한다. (비즈니스 로직만)"""
    df = pd.read_csv(tool_context.state["app:demand_file"])
    return df.groupby("zone_id")["demand"].sum().to_dict()
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-044 | @docs/design/ref/team-operations.md § AW-044 | Single Level of Abstraction |
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — 단일 책임 |
| @AW-022 | @docs/design/ref/team-operations.md § AW-022 | Unix Philosophy — 한 가지만 |

## 참조

- @docs/design/ref/team-operations.md § AW-044
- @.claude/skills/convention-solid-srp/SKILL.md
- @.claude/skills/convention-unix-philosophy/SKILL.md
