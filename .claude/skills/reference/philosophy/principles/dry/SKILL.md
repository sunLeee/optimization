---
name: convention-dry
description: DRY (Don't Repeat Yourself) 원칙. 지식은 단일 표현 — 중복 로직, 하드코딩, copy-paste 탐지.
user-invocable: true
triggers:
  - "DRY"
  - "중복 코드"
  - "don't repeat yourself"
  - "copy paste"
---

# convention-dry

**@AW-018** | @docs/design/ref/team-operations.md § AW-018

DRY (Don't Repeat Yourself): 모든 지식은 시스템 내에서 단일하고, 명확하며, 권위 있는 표현을 가져야 한다.

## VIOLATION 1: 중복된 검증 로직

```python
# VIOLATION: create_user와 update_user에 동일 검증 로직 반복
def create_user(name: str, email: str, age: int) -> User:
    if not name or len(name) < 2:
        raise ValueError("이름은 2글자 이상이어야 합니다")
    if not email or "@" not in email:
        raise ValueError("유효한 이메일을 입력하세요")
    if age < 0 or age > 150:
        raise ValueError("나이는 0-150 사이여야 합니다")

    user = User(name, email, age)
    database.save(user)
    return user

def update_user(user_id: int, name: str, email: str, age: int) -> User:
    if not name or len(name) < 2:        # 동일 로직 반복 — DRY 위반
        raise ValueError("이름은 2글자 이상이어야 합니다")
    if not email or "@" not in email:     # 동일 로직 반복 — DRY 위반
        raise ValueError("유효한 이메일을 입력하세요")
    if age < 0 or age > 150:             # 동일 로직 반복 — DRY 위반
        raise ValueError("나이는 0-150 사이여야 합니다")

    user = database.get(user_id)
    user.update(name, email, age)
    database.save(user)
    return user
```

```python
# CORRECT: 검증 로직을 단일 함수로 추출
def validate_user_data(name: str, email: str, age: int) -> None:
    """사용자 데이터 유효성을 검증한다.

    Logics:
        1. 이름 길이 확인 (2글자 이상)
        2. 이메일 형식 확인 (@ 포함)
        3. 나이 범위 확인 (0-150)

    Raises:
        ValueError: 유효하지 않은 입력값.
    """
    if not name or len(name) < 2:
        raise ValueError("이름은 2글자 이상이어야 합니다")
    if not email or "@" not in email:
        raise ValueError("유효한 이메일을 입력하세요")
    if age < 0 or age > 150:
        raise ValueError("나이는 0-150 사이여야 합니다")

def create_user(name: str, email: str, age: int) -> User:
    validate_user_data(name, email, age)  # 단일 위치에서 관리
    return database.save(User(name, email, age))

def update_user(user_id: int, name: str, email: str, age: int) -> User:
    validate_user_data(name, email, age)  # 재사용
    user = database.get(user_id)
    user.update(name, email, age)
    return database.save(user)
```

## VIOLATION 2: 하드코딩된 설정값 중복

```python
# VIOLATION: 동일한 연결 정보가 여러 곳에 하드코딩
def connect_to_database() -> pymongo.database.Database:
    connection = pymongo.MongoClient("mongodb://localhost:27017")  # 중복
    return connection["myapp"]

def backup_database() -> None:
    connection = pymongo.MongoClient("mongodb://localhost:27017")  # 중복
    source = connection["myapp"]                                   # 중복
    # 백업 로직...
```

```python
# CORRECT: 설정 중앙화 — 단일 위치
class Config:
    DATABASE_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "myapp"

def get_database_connection() -> pymongo.database.Database:
    """데이터베이스 연결을 반환한다.

    Logics:
        Config에서 URL과 이름을 읽어 연결을 생성한다.
    """
    connection = pymongo.MongoClient(Config.DATABASE_URL)
    return connection[Config.DATABASE_NAME]

def backup_database() -> None:
    source = get_database_connection()  # 재사용
    # 백업 로직...
```

## ADK 도메인 예시: 파일 경로 중복

```python
# VIOLATION: ADK tool에서 파일 경로를 직접 반복 지정
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    return pd.read_csv("/data/demand/2024.csv")   # 하드코딩

def validate_demand_data(tool_context: ToolContext) -> bool:
    df = pd.read_csv("/data/demand/2024.csv")     # 동일 경로 반복
    return df.shape[0] > 0

# CORRECT: cli_runner/config.py에서 단일 정의 후 state를 통해 참조
def load_demand_data(tool_context: ToolContext) -> pd.DataFrame:
    file_path = tool_context.state["app:demand_file"]  # 단일 출처
    return pd.read_csv(file_path)

def validate_demand_data(tool_context: ToolContext) -> bool:
    file_path = tool_context.state["app:demand_file"]  # 동일 출처
    return pd.read_csv(file_path).shape[0] > 0
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-018 | @docs/design/ref/team-operations.md § AW-018 | DRY — 중복 지식 금지 |
| Simplicity First | CLAUDE.md § LLM 행동지침 | 200줄→50줄 가능하면 다시 써라 |
| File Path Pattern | CLAUDE.md § File Path Pattern | 파일 경로는 config.py에서만 — DRY 적용 |

## 참조

- @docs/design/ref/team-operations.md § AW-018
- @.claude/skills/convention-solid-srp/SKILL.md — SRP도 함께 적용
- @.claude/skills/check-anti-patterns/SKILL.md — 중복 검증 패턴 탐지
