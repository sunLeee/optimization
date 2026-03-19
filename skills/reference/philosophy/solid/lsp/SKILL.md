---
name: convention-solid-lsp
description: LSP (Liskov Substitution Principle). 서브타입은 기반 타입으로 대체 가능해야 한다. 상속 시 계약을 파기하지 않는다.
user-invocable: true
triggers:
  - "LSP"
  - "liskov"
  - "리스코프"
  - "서브타입"
---

# convention-solid-lsp

**@AW-014** | @docs/design/ref/team-operations.md § AW-014

LSP: 서브타입(자식 클래스)의 인스턴스는 기반 타입(부모 클래스)으로 대체할 수 있어야 하며 프로그램의 정확성이 유지되어야 한다.

## VIOLATION 1: 자식 클래스가 부모 계약 파기

```python
# 부모 클래스: load()는 항상 pd.DataFrame 반환
class BaseDataLoader:
    def load(self, file_path: str) -> pd.DataFrame:
        raise NotImplementedError

class CSVLoader(BaseDataLoader):
    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)      # 올바른 구현

class EmptyLoader(BaseDataLoader):
    def load(self, file_path: str) -> pd.DataFrame:
        # VIOLATION: 빈 파일이면 None 반환 — LSP 파기
        if not Path(file_path).stat().st_size:
            return None  # type: ignore  # 계약 위반
        return pd.read_csv(file_path)

# 사용 측에서 None 체크가 필요해짐 → LSP 위반의 파급효과
def process(loader: BaseDataLoader, path: str) -> None:
    df = loader.load(path)
    if df is None:     # EmptyLoader 때문에 추가된 방어 코드
        return
    print(df.shape)
```

```python
# CORRECT: 예외를 명시적으로 던지거나 빈 DataFrame 반환
class EmptyLoader(BaseDataLoader):
    def load(self, file_path: str) -> pd.DataFrame:
        """빈 파일이면 빈 DataFrame을 반환한다.

        Logics:
            파일이 비어도 계약(pd.DataFrame 반환)을 지킨다.
        """
        if not Path(file_path).stat().st_size:
            return pd.DataFrame()   # 계약 유지 — 빈 DF 반환
        return pd.read_csv(file_path)
```

## VIOLATION 2: ADK tool 서브클래스가 상위 타입 메서드 강화

```python
# 부모: process()는 어떤 DataFrame도 처리
class BaseProcessor:
    def process(self, df: pd.DataFrame) -> dict:
        return {"rows": len(df)}

# VIOLATION: 자식이 precondition을 강화 (더 엄격하게) — LSP 위반
class DemandProcessor(BaseProcessor):
    def process(self, df: pd.DataFrame) -> dict:
        if "demand" not in df.columns:    # 부모보다 엄격한 조건 추가
            raise ValueError("demand 컬럼 필요")
        return {"rows": len(df), "total": df["demand"].sum()}

# 문제: BaseProcessor를 기대하는 코드에 DemandProcessor 주입 시 예외 발생 가능
```

```python
# CORRECT: 새 타입 파라미터나 명시적 인터페이스 분리
class DemandDataFrame:
    """demand 컬럼이 보장된 DataFrame 래퍼."""
    def __init__(self, df: pd.DataFrame) -> None:
        if "demand" not in df.columns:
            raise ValueError("demand 컬럼 필요")
        self.df = df

class DemandProcessor(BaseProcessor):
    def process(self, df: pd.DataFrame) -> dict:
        # 호출 전 검증은 생성 시점에 완료됨
        return {"rows": len(df), "total": df.get("demand", pd.Series()).sum()}
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-014 | @docs/design/ref/team-operations.md § AW-014 | LSP |
| @AW-013 | @docs/design/ref/team-operations.md § AW-013 | OCP — 확장 시 LSP 유지 |
| Type Hint | CLAUDE.md § 코드 스타일 | 명시적 타입으로 계약 표현 |

## 참조

- @docs/design/ref/team-operations.md § AW-014
- @.claude/skills/convention-solid-ocp/SKILL.md
- @.claude/skills/convention-solid-srp/SKILL.md
