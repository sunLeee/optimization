---
name: convention-unix-philosophy
description: Unix Philosophy. 한 가지 잘 하기, 함께 작동하기, 텍스트 스트림으로 소통하기. (McIlroy/Pike)
user-invocable: true
triggers:
  - "unix philosophy"
  - "유닉스 철학"
  - "한 가지만 잘"
  - "do one thing well"
---

# convention-unix-philosophy

**@AW-022** | @docs/design/ref/team-operations.md § AW-022

Unix Philosophy (McIlroy/Pike):
1. **Do one thing and do it well** — 프로그램은 한 가지 일만 잘 한다
2. **Write programs to work together** — 조합 가능하게 설계
3. **Write programs that handle text streams** — 표준 인터페이스로 소통

## VIOLATION 1: 하나의 tool이 너무 많은 일

```python
# VIOLATION: load_and_process_and_report()는 Unix 철학 위반
def process_demand_pipeline(
    input_path: str, output_path: str
) -> None:
    # 로딩 + 전처리 + 분석 + 저장 + 리포트 = 5가지 일
    df = pd.read_csv(input_path)
    df = df.dropna()
    df = df[df["demand"] > 0]
    result = df.groupby("zone_id")["demand"].sum()
    result.to_parquet(output_path)
    print(result.to_string())   # 리포트까지
```

```python
# CORRECT: 각 tool은 하나의 일만 (조합 가능)
def load_demand(file_path: str) -> pd.DataFrame:
    """수요 데이터를 로드한다."""
    return pd.read_csv(file_path)

def clean_demand(df: pd.DataFrame) -> pd.DataFrame:
    """결측값과 음수 수요를 제거한다."""
    return df.dropna().loc[lambda x: x["demand"] > 0]

def aggregate_by_zone(df: pd.DataFrame) -> pd.Series:
    """zone별 수요를 집계한다."""
    return df.groupby("zone_id")["demand"].sum()

def save_result(series: pd.Series, output_path: str) -> None:
    """결과를 Parquet으로 저장한다."""
    series.to_frame().to_parquet(output_path)

# 조합으로 파이프라인 구성 (조합 가능)
def run_pipeline(input_path: str, output_path: str) -> None:
    result = aggregate_by_zone(clean_demand(load_demand(input_path)))
    save_result(result, output_path)
```

## VIOLATION 2: ADK Tool이 다른 tool 결과에 직접 의존

```python
# VIOLATION: tool이 다른 tool의 내부 구현에 의존
def analyze_demand(tool_context: ToolContext) -> dict:
    # load_demand_data()가 특정 컬럼 구조를 만든다고 가정
    # 내부 구현 변경 시 여기도 깨짐
    df = pd.read_parquet("/tmp/demand_loaded.parquet")
    ...
```

```python
# CORRECT: tool은 state(텍스트 스트림 역할)로 소통
def load_demand_data(tool_context: ToolContext) -> dict:
    """수요 데이터를 로드하고 state에 경로를 저장한다."""
    df = pd.read_csv(tool_context.state["app:demand_file"])
    temp_path = "/tmp/demand_processed.parquet"
    df.to_parquet(temp_path)
    tool_context.state["agent:processed_path"] = temp_path  # 표준 인터페이스
    return {"rows": len(df)}

def analyze_demand(tool_context: ToolContext) -> dict:
    """state의 경로로 분석을 수행한다."""
    processed_path = tool_context.state["agent:processed_path"]
    df = pd.read_parquet(processed_path)  # 표준 인터페이스로 소통
    return {"total_demand": float(df["demand"].sum())}
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-022 | @docs/design/ref/team-operations.md § AW-022 | Unix Philosophy |
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — 하나의 책임 |
| @AW-020 | @docs/design/ref/team-operations.md § AW-020 | SoC — 관심사 분리 |

## 참조

- @docs/design/ref/team-operations.md § AW-022
- @.claude/skills/convention-solid-srp/SKILL.md
- @.claude/skills/convention-adk-agent/SKILL.md
