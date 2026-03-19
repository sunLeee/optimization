---
name: convention-wirths-law
description: Wirth's Law. 소프트웨어는 하드웨어가 빨라지는 것보다 더 빨리 느려진다. 성능 최적화 주의.
user-invocable: true
triggers:
  - "Wirth's Law"
  - "비르트의 법칙"
  - "소프트웨어 비대화"
  - "성능 저하"
---

# convention-wirths-law

**@AW-030** | @docs/design/ref/team-operations.md § AW-030

Wirth's Law: "소프트웨어는 하드웨어가 빨라지는 것보다 더 빨리 느려진다." (Niklaus Wirth, 1995) 불필요한 레이어, 과도한 추상화, 메모리 낭비를 경계하라.

## VIOLATION 1: 과도한 레이어로 성능 저하

```python
# VIOLATION: 단순한 CSV 읽기에 5개 레이어
class DataSourceAdapter:
    def adapt(self, raw: bytes) -> str: return raw.decode()

class DataParser:
    def parse(self, text: str) -> list: return text.splitlines()

class DataTransformer:
    def transform(self, rows: list) -> dict: ...

class DataValidator:
    def validate(self, data: dict) -> bool: ...

class DataLoader:
    def load(self, path: str) -> pd.DataFrame:
        raw = open(path, "rb").read()
        text = DataSourceAdapter().adapt(raw)
        rows = DataParser().parse(text)
        data = DataTransformer().transform(rows)
        valid = DataValidator().validate(data)
        return pd.DataFrame(data) if valid else pd.DataFrame()
        # pandas의 read_csv 하나로 충분했던 것을

# CORRECT: 단순하고 직접적인 구현
def load_demand_data(file_path: str) -> pd.DataFrame:
    """수요 데이터를 로드한다."""
    return pd.read_csv(file_path)  # pandas가 이미 모든 것을 최적화
```

## VIOLATION 2: 불필요한 중간 저장으로 메모리 낭비

```python
# VIOLATION: 중간 결과를 계속 복사/저장
def process_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    step1 = df.copy()                    # 불필요한 복사
    step1 = step1.dropna()

    step2 = step1.copy()                 # 불필요한 복사
    step2 = step2[step2["demand"] > 0]

    step3 = step2.copy()                 # 불필요한 복사
    step3 = step3.reset_index(drop=True)

    return step3
```

```python
# CORRECT: 체이닝으로 메모리 효율적 처리
def process_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """수요 데이터를 처리한다.

    Logics:
        method chaining으로 중간 복사 없이 처리한다.
    """
    return (
        df.dropna()
          .loc[lambda x: x["demand"] > 0]
          .reset_index(drop=True)
    )
```

## Wirth's Law 방지 체크리스트

```bash
# 메모리 사용량 확인 (AW-011 Rob Pike Rule 1 - 측정 먼저)
python3 -c "
import tracemalloc, pandas as pd
tracemalloc.start()
df = pd.read_csv('data/demand.csv')
current, peak = tracemalloc.get_traced_memory()
print(f'Peak memory: {peak / 1024 / 1024:.2f} MB')
"

# 처리 시간 측정
import time
start = time.perf_counter()
result = process_demand(df)
elapsed = time.perf_counter() - start
print(f"처리 시간: {elapsed:.3f}초")
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-030 | @docs/design/ref/team-operations.md § AW-030 | Wirth's Law |
| @AW-011 | @docs/design/ref/team-operations.md § AW-011 | Rob Pike — 측정 먼저 |
| @AW-017 | @docs/design/ref/team-operations.md § AW-017 | KISS — 레이어 최소화 |

## 참조

- @docs/design/ref/team-operations.md § AW-030
- @.claude/skills/convention-kiss/SKILL.md
- @docs/design/ref/team-operations.md § AW-011
