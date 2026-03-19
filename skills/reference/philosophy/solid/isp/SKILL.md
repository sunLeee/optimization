---
name: convention-solid-isp
description: ISP (Interface Segregation Principle). 클라이언트는 사용하지 않는 인터페이스에 의존하지 않아야 한다. 큰 인터페이스를 작게 분리.
user-invocable: true
triggers:
  - "ISP"
  - "interface segregation"
  - "인터페이스 분리"
  - "뚱뚱한 인터페이스"
---

# convention-solid-isp

**@AW-015** | @docs/design/ref/team-operations.md § AW-015

ISP: 클라이언트가 사용하지 않는 메서드에 의존하도록 강제하지 말라. 하나의 큰 인터페이스보다 여러 작은 인터페이스가 낫다.

## VIOLATION 1: 뚱뚱한 DataProcessor 인터페이스

```python
# VIOLATION: 모든 처리기가 관련 없는 메서드까지 구현 강제
class DataProcessor(ABC):
    @abstractmethod
    def load_csv(self, path: str) -> pd.DataFrame: ...
    @abstractmethod
    def load_parquet(self, path: str) -> pd.DataFrame: ...
    @abstractmethod
    def save_csv(self, df: pd.DataFrame, path: str) -> None: ...
    @abstractmethod
    def save_parquet(self, df: pd.DataFrame, path: str) -> None: ...
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool: ...
    @abstractmethod
    def visualize(self, df: pd.DataFrame) -> None: ...

# 읽기만 하는 ReportGenerator가 save_*, visualize 구현 강제
class ReportGenerator(DataProcessor):
    def load_csv(self, path: str) -> pd.DataFrame: ...
    def load_parquet(self, path: str) -> pd.DataFrame: ...
    def save_csv(self, ...) -> None: raise NotImplementedError  # 불필요
    def save_parquet(self, ...) -> None: raise NotImplementedError  # 불필요
    def validate(self, ...) -> bool: raise NotImplementedError  # 불필요
    def visualize(self, ...) -> None: raise NotImplementedError  # 불필요
```

```python
# CORRECT: 인터페이스를 역할별로 분리
class DataReader(ABC):
    @abstractmethod
    def load(self, path: str) -> pd.DataFrame: ...

class DataWriter(ABC):
    @abstractmethod
    def save(self, df: pd.DataFrame, path: str) -> None: ...

class DataValidator(ABC):
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool: ...

# 필요한 인터페이스만 구현
class CSVReader(DataReader):
    def load(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)

class ReportGenerator(DataReader):  # 읽기만 필요
    def load(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)
```

## VIOLATION 2: ADK Agent 인터페이스 과부하

```python
# VIOLATION: 모든 에이전트가 불필요한 메서드 구현
class BaseAgent(ABC):
    @abstractmethod
    def analyze(self) -> dict: ...
    @abstractmethod
    def visualize(self) -> None: ...   # 분석 에이전트에는 불필요
    @abstractmethod
    def export_excel(self) -> None: ... # 대부분 에이전트에 불필요
    @abstractmethod
    def send_email(self) -> None: ...   # 불필요
```

```python
# CORRECT: 역할별 분리
class Analyzable(ABC):
    @abstractmethod
    def analyze(self) -> dict: ...

class Visualizable(ABC):
    @abstractmethod
    def visualize(self) -> None: ...

class DemandAgent(Analyzable):          # 분석만
    def analyze(self) -> dict: ...

class ReportAgent(Analyzable, Visualizable):  # 분석 + 시각화
    def analyze(self) -> dict: ...
    def visualize(self) -> None: ...
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-015 | @docs/design/ref/team-operations.md § AW-015 | ISP |
| @AW-012 | @docs/design/ref/team-operations.md § AW-012 | SRP — 단일 책임과 연계 |
| @AW-020 | @docs/design/ref/team-operations.md § AW-020 | SoC — 관심사 분리 |

## 참조

- @docs/design/ref/team-operations.md § AW-015
- @.claude/skills/convention-solid-srp/SKILL.md
- @.claude/skills/convention-soc/SKILL.md
