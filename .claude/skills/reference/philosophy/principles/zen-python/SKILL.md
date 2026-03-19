---
name: convention-zen-python
description: Zen of Python (PEP 20). 19개 아포리즘 — Beautiful > Ugly, Explicit > Implicit, Simple > Complex.
user-invocable: true
triggers:
  - "zen of python"
  - "PEP 20"
  - "파이썬 철학"
  - "import this"
---

# convention-zen-python

**@AW-021** | @docs/design/ref/team-operations.md § AW-021

Zen of Python (Tim Peters, 1999): `import this`로 확인 가능한 19개 Python 철학. 가장 실용적인 원칙들.

## 핵심 원칙 5가지 (가장 자주 위반되는 것)

### 1. Explicit is better than implicit (명시적 > 암시적)

```python
# VIOLATION: 암시적 — 뭘 반환하는지 불명확
def get_data(flag=True):
    if flag:
        return pd.read_csv("data.csv")
    # flag=False면 None 반환 (암시적)

# CORRECT: 명시적 반환 타입 + 명확한 파라미터
def load_demand_csv(file_path: str) -> pd.DataFrame:
    """수요 CSV를 로드한다."""
    return pd.read_csv(file_path)

def load_demand_if_exists(file_path: str) -> pd.DataFrame | None:
    """파일이 있으면 로드, 없으면 None."""
    return pd.read_csv(file_path) if Path(file_path).exists() else None
```

### 2. Simple is better than complex (단순 > 복잡)

```python
# VIOLATION: 복잡한 one-liner
result = {k: v for k, v in sorted(
    {z: df[df.zone_id==z].demand.sum() for z in df.zone_id.unique()}.items(),
    key=lambda x: x[1], reverse=True
) if v > 0}

# CORRECT: 단순하고 읽기 쉬운 형태
def get_top_demand_zones(df: pd.DataFrame) -> dict[int, float]:
    """상위 수요 zone을 반환한다."""
    zone_demands = df.groupby("zone_id")["demand"].sum()
    positive_demands = zone_demands[zone_demands > 0]
    return positive_demands.sort_values(ascending=False).to_dict()
```

### 3. Errors should never pass silently (에러는 조용히 지나가지 않는다)

```python
# VIOLATION: 에러 무시
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        pass  # 에러 무시 — Zen 위반
    return {}

# CORRECT: 에러를 명시적으로 처리하거나 전파
def load_config(path: str) -> dict:
    """설정 파일을 로드한다."""
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"설정 파일 없음: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 파싱 오류: {e}") from e
```

### 4. There should be one obvious way to do it (명확한 방법은 하나)

```python
# VIOLATION: 같은 작업을 여러 방식으로 혼재
zones = list(df["zone_id"].values)      # 방법 1
zones = df["zone_id"].tolist()          # 방법 2
zones = [x for x in df["zone_id"]]     # 방법 3

# CORRECT: 팀에서 합의한 하나의 방법만 사용
# @convention-python의 pandas vectorization 패턴 따름
zones = df["zone_id"].tolist()  # Series.tolist()로 통일
```

### 5. Readability counts (가독성이 중요하다)

```python
# VIOLATION: 변수명이 의미 없음
def f(x: pd.DataFrame, t: float = 0.8) -> pd.DataFrame:
    q = x["d"].quantile(t)
    return x[x["d"] > q]

# CORRECT: 의미 있는 이름
def filter_high_demand(
    df: pd.DataFrame, quantile_threshold: float = 0.8
) -> pd.DataFrame:
    """높은 수요의 zone을 필터링한다."""
    threshold = df["demand"].quantile(quantile_threshold)
    return df[df["demand"] > threshold]
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-021 | @docs/design/ref/team-operations.md § AW-021 | Zen of Python |
| @AW-017 | @docs/design/ref/team-operations.md § AW-017 | KISS — Simple > Complex |
| convention-python | CLAUDE.md § 구현 시 필수 스킬 | Python 컨벤션 전반 |

## 참조

- @docs/design/ref/team-operations.md § AW-021
- @.claude/skills/convention-python/SKILL.md
- @.claude/skills/convention-kiss/SKILL.md
