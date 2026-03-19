---
name: check-data-pipeline
description: ADK 데이터 파이프라인 패턴 검증. ToolContext 사용, 파일 경로 anti-pattern, tool function 인자 규칙 검사.
user-invocable: true
triggers:
  - "data pipeline 검증"
  - "tool context 확인"
  - "파일 경로 패턴"
  - "ADK tool 검사"
---

# check-data-pipeline

ADK tool function과 데이터 파이프라인 코드에서 CLAUDE.md § File Path & Data Access Pattern 위반을 탐지한다.

## 검사 규칙 (CLAUDE.md § File Path & Data Access Pattern 5원칙)

### Rule 1: 파일 경로는 cli_runner/config.py에서만 정의

**탐지 대상**: tool function 또는 agent `__init__` 내부에 하드코딩된 파일 경로

```python
# VIOLATION: tool function 내 파일 경로 하드코딩
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    return pd.read_csv("data/demand/2024.csv")  # 금지

# CORRECT: config.py의 get_*_path() 사용
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    file_path = tool_context.state.get("app:demand_file")
    return pd.read_csv(file_path)
```

### Rule 2: Agent `__init__`에서 파일 존재 확인 후 즉시 raise

**탐지 대상**: tool function 내부에서 파일 존재 재확인하는 코드

```python
# VIOLATION: tool function 내 파일 존재 재검사
def process_data(tool_context: ToolContext) -> dict:
    file_path = tool_context.state.get("app:file")
    if not os.path.exists(file_path):  # 금지 — agent __init__에서 이미 확인
        raise FileNotFoundError(...)

# CORRECT: tool function은 상태에서 경로를 읽고 바로 사용
def process_data(tool_context: ToolContext) -> dict:
    file_path = tool_context.state.get("app:file")
    df = pd.read_csv(file_path)
    ...
```

### Rule 3: 파일 경로는 initial_state에 app: prefix로 저장

**탐지 대상**: `app:` prefix 없는 state key로 파일 경로 저장

```python
# VIOLATION: app: prefix 없음
self.initial_state = {"demand_file": str(demand_path)}  # 금지

# CORRECT: app: prefix 필수
self.initial_state = {"app:demand_file": str(demand_path)}
```

### Rule 4: Tool function은 파일 경로를 인자로 받지 않음

**탐지 대상**: tool function signature에 파일 경로 관련 인자

```python
# VIOLATION: file_path를 직접 인자로 받음
def load_data(
    file_path: str,          # 금지
    tool_context: ToolContext
) -> pd.DataFrame: ...

# CORRECT: tool_context.state에서 읽음
def load_data(tool_context: ToolContext) -> pd.DataFrame:
    file_path = tool_context.state.get("app:data_file")
    ...
```

### Rule 5: ToolContext 없는 tool function 금지

**탐지 대상**: ADK tool로 등록된 function에 `ToolContext` 인자 누락

```python
# VIOLATION: ToolContext 없음
def aggregate_zones(df: pd.DataFrame) -> pd.DataFrame:  # ADK tool로 등록 불가
    ...

# CORRECT
def aggregate_zones(
    tool_context: ToolContext
) -> dict[str, Any]:
    df_path = tool_context.state.get("app:zone_file")
    ...
```

## 검사 방법

코드 검토 시 아래 순서로 확인한다:

```bash
# 1. tool function에 file_path 인자가 있는지 탐지
grep -rn "def.*file_path.*ToolContext\|def.*ToolContext.*file_path" agents/

# 2. tool function 내부 os.path.exists 중복 검사 탐지
grep -rn "os.path.exists" agents/*/tools/ agents/*/src/

# 3. app: prefix 없는 state key로 파일 경로 저장 탐지
grep -rn '"[^a]*_file"\|"[^a]*_path"' agents/*/src/

# 4. 하드코딩된 경로 탐지 (data/, output/ 직접 참조)
grep -rn '"data/\|"output/' agents/
```

## Pandas 성능 규칙 (AW-011 Rob Pike Rule 3/4)

```python
# VIOLATION: iterrows 사용 — n이 커지면 치명적
for idx, row in df.iterrows():  # 금지
    result[idx] = process(row)

# CORRECT: vectorized 연산
result = df.apply(process, axis=1)
# 또는
result = df["col"].map(transform_func)
```

## 관련 규칙

- CLAUDE.md § File Path & Data Access Pattern (5원칙)
- [team-operations.md](../../docs/design/ref/team-operations.md) § AW-011
- [convention-adk-agent](../convention-adk-agent/SKILL.md)
- [claude-code-rule-convention.md](../../docs/ref/bestpractice/claude-code-rule-convention.md) § Practice 27
