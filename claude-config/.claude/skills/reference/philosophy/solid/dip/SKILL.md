---
name: convention-solid-dip
description: DIP (Dependency Inversion Principle). 고수준 모듈이 저수준 모듈에 의존하지 않는다. 둘 다 추상화에 의존한다.
user-invocable: true
triggers:
  - "DIP"
  - "dependency inversion"
  - "의존성 역전"
  - "의존성 주입"
---

# convention-solid-dip

**@AW-016** | @docs/design/ref/team-operations.md § AW-016

DIP: 고수준 모듈(비즈니스 로직)은 저수준 모듈(파일 I/O, DB)에 직접 의존해서는 안 된다. 둘 다 추상화(인터페이스)에 의존해야 한다.

## VIOLATION 1: 비즈니스 로직이 CSV 구현에 직접 의존

```python
# VIOLATION: 고수준(DemandAnalyzer)이 저수준(CSV 파일) 직접 사용
class DemandAnalyzer:
    def analyze(self, file_path: str) -> dict:
        # 저수준 구현(CSV)에 직접 의존 — DIP 위반
        df = pd.read_csv(file_path)  # CSV에 종속
        return {"total": df["demand"].sum()}

# 문제: Parquet으로 바꾸면 DemandAnalyzer 코드 수정 필요
```

```python
# CORRECT: 추상화(DataReader)에 의존
class DataReader(ABC):
    @abstractmethod
    def read(self, source: str) -> pd.DataFrame: ...

class CSVDataReader(DataReader):
    def read(self, source: str) -> pd.DataFrame:
        return pd.read_csv(source)

class ParquetDataReader(DataReader):
    def read(self, source: str) -> pd.DataFrame:
        return pd.read_parquet(source)

class DemandAnalyzer:
    def __init__(self, reader: DataReader) -> None:
        """DataReader 추상화에 의존한다.

        Logics:
            생성 시 reader를 주입받아 저수준 구현과 분리한다.
        """
        self._reader = reader  # 추상화에 의존

    def analyze(self, source: str) -> dict:
        df = self._reader.read(source)  # 구현과 무관
        return {"total": df["demand"].sum()}

# 사용 측에서 구현 선택
analyzer = DemandAnalyzer(reader=CSVDataReader())
analyzer = DemandAnalyzer(reader=ParquetDataReader())  # 교체 자유
```

## VIOLATION 2: ADK tool이 외부 서비스에 직접 의존

```python
# VIOLATION: tool이 특정 DB 구현에 직접 의존
def load_zone_config(tool_context: ToolContext) -> dict:
    # 저수준(MongoDB) 직접 사용 — DIP 위반
    client = pymongo.MongoClient("mongodb://localhost:27017")
    return client["myapp"]["zones"].find_one({"zone_id": 1})
```

```python
# CORRECT: 추상화된 저장소에 의존
class ZoneRepository(ABC):
    @abstractmethod
    def get_config(self, zone_id: int) -> dict: ...

class MongoZoneRepository(ZoneRepository):
    def get_config(self, zone_id: int) -> dict:
        client = pymongo.MongoClient("mongodb://localhost:27017")
        return client["myapp"]["zones"].find_one({"zone_id": zone_id})

# tool은 추상화에만 의존 (테스트 시 MockZoneRepository 주입 가능)
def load_zone_config(
    tool_context: ToolContext,
    repo: ZoneRepository  # 추상화 주입
) -> dict:
    zone_id = tool_context.state["app:zone_id"]
    return repo.get_config(int(zone_id))
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-016 | @docs/design/ref/team-operations.md § AW-016 | DIP |
| @AW-042 | @docs/design/ref/team-operations.md § AW-042 | IoC — DIP와 연계 |
| @AW-013 | @docs/design/ref/team-operations.md § AW-013 | OCP — 추상화로 확장 |

## 참조

- @docs/design/ref/team-operations.md § AW-016
- @.claude/skills/convention-ioc/SKILL.md
- @.claude/skills/convention-solid-ocp/SKILL.md
