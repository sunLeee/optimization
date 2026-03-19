---
name: convention-pragmatic-programmer
description: Pragmatic Programmer Rules. Tracer Bullets, DRY, 직교성(Orthogonality), 가역성(Reversibility). Hunt & Thomas.
user-invocable: true
triggers:
  - "pragmatic programmer"
  - "프래그매틱 프로그래머"
  - "tracer bullets"
  - "직교성"
  - "가역성"
---

# convention-pragmatic-programmer

**@AW-045** | @docs/design/ref/team-operations.md § AW-045

Pragmatic Programmer (Andrew Hunt & David Thomas, 1999): 실용적인 소프트웨어 개발을 위한 핵심 원칙들. 이 프로젝트에 직접 적용 가능한 4가지.

## 원칙 1: Tracer Bullets (예광탄)

먼저 end-to-end로 작동하는 얇은 슬라이스를 만들고, 그 위에 살을 붙여라.

```python
# VIOLATION: 완벽한 구현 후 통합 시도 (Big Bang)
# → 통합 때 모든 문제 발견 = 늦은 피드백

# CORRECT: Tracer Bullet — 얇지만 end-to-end로 작동하는 것 먼저
def demand_analysis_v0(
    input_csv: str, output_json: str
) -> None:
    """MVP Tracer Bullet: CSV 입력 → 기본 집계 → JSON 출력.

    Logics:
        완벽하지 않아도 전체 흐름이 작동하는 것을 먼저.
        이후 각 단계를 개선한다.
    """
    df = pd.read_csv(input_csv)                          # 로딩 (단순)
    result = df.groupby("zone_id")["demand"].sum()       # 집계 (단순)
    result.to_json(output_json)                          # 저장 (단순)

# v0가 작동하면 → 각 단계를 점진적으로 개선
# load_demand_data() → preprocess_demand() → aggregate() → save()
```

## 원칙 2: Orthogonality (직교성)

컴포넌트 간 독립성. 하나를 변경해도 다른 것에 영향 없어야 한다.

```python
# VIOLATION: 데이터 로딩과 분석이 결합 (직교성 없음)
class DemandProcessor:
    def load_and_analyze(self, file_path: str) -> dict:
        # 파일 형식이 바뀌면 분석 로직도 수정 필요
        df = pd.read_csv(file_path)
        return df.groupby("zone_id")["demand"].sum().to_dict()

# CORRECT: 독립적인 컴포넌트 (직교성 확보)
def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)  # 로딩만

def analyze_demand(df: pd.DataFrame) -> dict[int, float]:
    return df.groupby("zone_id")["demand"].sum().to_dict()  # 분석만

# 파일 형식 변경 → load_data()만 수정
# 집계 방법 변경 → analyze_demand()만 수정
```

## 원칙 3: Reversibility (가역성)

중요한 결정을 되돌릴 수 있게 설계하라. 특히 데이터 포맷과 API.

```python
# VIOLATION: 특정 DB에 의존 → 변경 불가
class ZoneRepository:
    def __init__(self) -> None:
        self.client = pymongo.MongoClient("localhost:27017")  # 직접 의존

# CORRECT: 추상화 + 설정으로 가역성 확보 (AW-016 DIP + Reversibility)
class ZoneRepository(ABC):
    @abstractmethod
    def get(self, zone_id: int) -> dict: ...

# OmegaConf 설정으로 DB 선택 (ADR로 변경 기록)
def create_zone_repo(config: DictConfig) -> ZoneRepository:
    if config.db.type == "mongo":
        return MongoZoneRepository(config.db.url)
    return InMemoryZoneRepository()  # 테스트/개발 환경
```

## 원칙 4: Don't Live with Broken Windows

깨진 창문(나쁜 코드, 잘못된 설계)을 방치하지 말라.

```python
# VIOLATION: "나중에 고칠게" — broken window 방치
def process_data(df):  # type hint 없음 — 깨진 창문
    # TODO: 이 함수 나중에 리팩토링 (6개월째 방치)
    x = df.groupby('z')['d'].sum()  # 변수명 의미 없음
    return x.to_dict()

# CORRECT: 발견 즉시 수정 (Boy Scout Rule + Broken Windows 없앰)
def aggregate_zone_demand(df: pd.DataFrame) -> dict[int, float]:
    """zone별 수요 합계를 반환한다."""
    return df.groupby("zone_id")["demand"].sum().to_dict()
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-045 | @docs/design/ref/team-operations.md § AW-045 | Pragmatic Programmer |
| @AW-009 | @docs/design/ref/team-operations.md § AW-009 | ADR — 가역성 없는 결정 기록 |
| @AW-035 | @docs/design/ref/team-operations.md § AW-035 | Boy Scout Rule — 깨진 창문 수리 |

## 참조

- @docs/design/ref/team-operations.md § AW-045
- @.claude/skills/convention-adr/SKILL.md
- @.claude/skills/convention-boy-scout-rule/SKILL.md
- @.claude/skills/convention-single-abstraction/SKILL.md
