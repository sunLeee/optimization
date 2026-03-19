---
name: convention-solid-srp
description: SRP (Single Responsibility Principle). 클래스/함수는 단 하나의 변경 이유만 가져야 한다.
user-invocable: true
triggers:
  - "SRP"
  - "단일 책임"
  - "single responsibility"
  - "god class"
---

# convention-solid-srp

**@AW-012** | @docs/design/ref/team-operations.md § AW-012

SRP: 클래스(또는 함수)는 단 하나의 변경 이유만 가져야 한다. 여러 책임이 섞이면 하나의 변경이 다른 기능을 망가뜨린다.

## VIOLATION 1: ADK Agent God Class

```python
# VIOLATION: DemandAgent가 데이터 로딩 + 전처리 + 분석 + 리포트 모두 담당
class DemandAgent:
    def load_csv(self, path: str) -> pd.DataFrame: ...      # 데이터 로딩 책임
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame: ...  # 전처리 책임
    def analyze(self, df: pd.DataFrame) -> dict: ...         # 분석 책임
    def generate_report(self, result: dict) -> str: ...      # 리포트 책임
    def send_notification(self, report: str) -> None: ...    # 알림 책임

# 문제: CSV 포맷이 바뀌면 load_csv 수정 → 리포트 로직도 같은 클래스에 있어 테스트 어려움
```

```python
# CORRECT: 각 책임을 독립 클래스로 분리
class DemandDataLoader:
    """수요 데이터 로딩만 담당한다."""
    def load(self, path: str) -> pd.DataFrame: ...

class DemandPreprocessor:
    """전처리만 담당한다."""
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame: ...

class DemandAnalyzer:
    """분석만 담당한다."""
    def analyze(self, df: pd.DataFrame) -> dict: ...

class DemandReporter:
    """리포트 생성만 담당한다."""
    def generate(self, result: dict) -> str: ...

# DemandAgent는 오케스트레이션만
class DemandAgent:
    def __init__(self) -> None:
        self.loader = DemandDataLoader()
        self.preprocessor = DemandPreprocessor()
        self.analyzer = DemandAnalyzer()
        self.reporter = DemandReporter()
```

## VIOLATION 2: 함수에 여러 책임

```python
# VIOLATION: load_and_validate_and_save()는 3가지 책임
def load_and_validate_and_save(
    file_path: str, output_path: str
) -> bool:
    df = pd.read_csv(file_path)        # 로딩 책임
    if df.empty or df.isnull().any():  # 검증 책임
        return False
    df.to_parquet(output_path)         # 저장 책임
    return True
```

```python
# CORRECT: 각 함수는 하나의 책임
def load_data(file_path: str) -> pd.DataFrame:
    """CSV를 로드하여 DataFrame으로 반환한다."""
    return pd.read_csv(file_path)

def validate_data(df: pd.DataFrame) -> bool:
    """데이터 유효성을 검증한다."""
    return not df.empty and not df.isnull().any().any()

def save_data(df: pd.DataFrame, output_path: str) -> None:
    """DataFrame을 Parquet으로 저장한다."""
    df.to_parquet(output_path)
```

## 탐지 방법

```bash
# 200줄 초과 클래스 = SRP 위반 의심
python3 -c "
import ast, pathlib
for py in pathlib.Path('agents').rglob('*.py'):
    tree = ast.parse(py.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            lines = node.end_lineno - node.lineno
            if lines > 100:
                print(f'{py}:{node.lineno} {node.name} — {lines}줄 (SRP 의심)')
"
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — 단일 변경 이유 |
| Simplicity First | CLAUDE.md § LLM 행동지침 | 파일당 200-400줄, 최대 800줄 |
| High cohesion | CLAUDE.md § 코드 구성 | High cohesion, low coupling |

## 참조

- @docs/design/ref/team-operations.md § AW-012
- @.claude/skills/check-anti-patterns/SKILL.md — God Class 탐지
- @.claude/skills/convention-solid-ocp/SKILL.md — OCP와 함께 적용
