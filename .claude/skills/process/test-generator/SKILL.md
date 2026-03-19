---
name: test-generator
triggers:
  - "test generator"
description: 테스트 코드 자동 생성 스킬. 소스 코드를 분석하여 pytest 기반 테스트 코드를 생성한다. convention-testing 스킬의 규칙(AAA 패턴, 명명 규칙)을 준수한다.
argument-hint: "[소스 파일 경로] [--unit|--integration|--all] - 테스트 생성 대상"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: 소스 코드를 분석하여 테스트 코드를 자동 생성한다. convention-testing 스킬에 정의된 AAA 패턴, 명명 규칙, 구조를 준수한다. pytest fixtures와 parametrize를 활용하여 효율적인 테스트를 생성한다.
agent: 테스트 코드 생성 전문가. 소스 코드의 함수, 클래스, 메서드를 분석하여 엣지 케이스를 포함한 테스트를 생성한다. AAA 패턴을 준수하고, 명확한 테스트 이름을 사용한다.
hooks:
  pre_execution: []
  post_execution: []
category: 개발 지원
skill-type: Atomic
references:
  - "@skills/sync-docs/SKILL.md"
referenced-by:
  - "@skills/sync-docs/SKILL.md"

---
# 테스트 코드 생성

소스 코드를 분석하여 pytest 기반 테스트 코드를 자동 생성한다.

## 목적

- 소스 코드 분석 및 테스트 케이스 도출
- AAA 패턴 준수 테스트 생성
- Fixtures 및 Parametrize 활용
- 엣지 케이스 자동 탐지

## 사용법

```
/test-generator src/utils.py                    # 단일 파일
/test-generator src/api/                        # 디렉토리 전체
/test-generator src/models.py --unit            # 단위 테스트만
/test-generator src/services.py --integration   # 통합 테스트만
/test-generator src/ --all                      # 전체 테스트
```

### AskUserQuestion 활용 지점

**지점 1: 테스트 타입 선택**

플래그가 없을 때 테스트 타입을 선택한다:

```yaml
AskUserQuestion:
  questions:
    - question: "생성할 테스트 타입을 선택해주세요"
      header: "테스트 타입"
      multiSelect: false
      options:
        - label: "unit - 단위 테스트 (권장)"
          description: "함수/메서드 단위 | 빠른 실행 | 격리된 테스트"
        - label: "integration - 통합 테스트"
          description: "컴포넌트 간 상호작용 | DB/API 포함"
        - label: "all - 전체"
          description: "단위 + 통합 테스트 모두 생성"
```

**지점 2: 커버리지 목표 설정**

```yaml
AskUserQuestion:
  questions:
    - question: "목표 커버리지를 설정해주세요"
      header: "커버리지 목표"
      multiSelect: false
      options:
        - label: "80% (권장)"
          description: "핵심 로직 커버 | 실용적 수준"
        - label: "90%"
          description: "높은 품질 | 추가 엣지 케이스"
        - label: "100%"
          description: "완벽 커버 | 모든 분기/예외"
        - label: "커스텀"
          description: "직접 지정"
```

---

## 생성 프로세스

### 1단계: 소스 코드 분석

```python
# 분석 대상
- 함수/메서드 시그니처
- 클래스 구조
- 타입 힌트
- Docstring
- 의존성 (import)
```

### 2단계: 테스트 케이스 도출

```
소스 함수: process_data(data: pd.DataFrame) -> pd.DataFrame

테스트 케이스:
1. 정상 입력 처리 (Happy Path)
2. 빈 DataFrame 처리
3. None 입력 처리
4. 잘못된 타입 입력
5. 경계값 테스트
```

### 3단계: 테스트 코드 생성

```python
# tests/unit/test_utils.py
"""src/utils.py 모듈에 대한 단위 테스트.

이 모듈은 process_data 함수의 정상 동작, 엣지 케이스,
예외 처리를 검증한다.

Author: taeyang lee
Created: 2026-01-21 10:00(KST, UTC+09:00)
Modified: 2026-01-21 10:00(KST, UTC+09:00)
Version: 1.0.0
"""

import pytest
import pandas as pd
from src.utils import process_data


class TestProcessData:
    """process_data 함수의 테스트 클래스."""

    def test_process_data_with_valid_input_returns_dataframe(self):
        """유효한 입력으로 변환된 DataFrame을 반환하는지 검증.

        이 테스트는 AAA 패턴(Arrange-Act-Assert)을 따른다.
        """
        # Arrange: 테스트 데이터 준비
        input_data = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"]
        })
        expected_columns = ["col1", "col2", "processed"]

        # Act: 함수 실행
        result = process_data(input_data)

        # Assert: 결과 검증
        assert isinstance(result, pd.DataFrame), (
            "반환값은 DataFrame 타입이어야 함"
        )
        assert list(result.columns) == expected_columns, (
            f"기대 컬럼: {expected_columns}, "
            f"실제 컬럼: {list(result.columns)}"
        )

    def test_process_data_with_empty_dataframe_returns_empty(self):
        """빈 DataFrame을 입력했을 때 빈 DataFrame을 반환.

        엣지 케이스: 입력 데이터가 없는 경우를 검증한다.
        """
        # Arrange: 빈 DataFrame 준비
        input_data = pd.DataFrame()

        # Act: 함수 실행
        result = process_data(input_data)

        # Assert: 결과가 비어있는지 검증
        assert result.empty, "출력 DataFrame도 비어있어야 함"

    def test_process_data_with_none_raises_type_error(self):
        """None 입력 시 TypeError 발생.

        타입 검증: None을 넘겼을 때 적절한 예외를 발생시키는지
        확인한다.
        """
        # Arrange: None 입력 준비
        input_data = None

        # Act & Assert: 예외 발생 여부 검증
        with pytest.raises(TypeError):
            process_data(input_data)


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (pd.DataFrame({"a": [1]}), 1),
        (pd.DataFrame({"a": [1, 2]}), 2),
        (pd.DataFrame({"a": [1, 2, 3]}), 3),
    ],
    ids=["single_row", "two_rows", "three_rows"],
)
def test_process_data_row_count(
    input_value: pd.DataFrame,
    expected: int,
) -> None:
    """출력 행 개수가 입력과 일치하는지 검증.

    Args:
        input_value: 테스트 입력 DataFrame.
        expected: 기대하는 행 개수.

    Logics:
        1. 입력 DataFrame의 행 개수 파악.
        2. process_data 함수 실행.
        3. 출력의 행 개수가 기대값과 일치하는지 검증.
    """
    # Arrange-Act-Assert (간결한 테스트)
    result = process_data(input_value)
    assert len(result) == expected, (
        f"행 개수 불일치: 기대 {expected}, "
        f"실제 {len(result)}"
    )
```

### 4단계: Fixtures 생성

```python
# tests/conftest.py
"""모든 테스트에서 사용할 공유 Fixtures.

이 파일은 pytest의 conftest.py로서 프로젝트 전역 fixture를
정의한다. 테스트 간 코드 중복을 제거하고 재사용성을 높인다.

Author: taeyang lee
Created: 2026-01-21 10:00(KST, UTC+09:00)
Modified: 2026-01-21 10:00(KST, UTC+09:00)
Version: 1.0.0
"""

import pytest
import pandas as pd


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """테스트용 샘플 DataFrame을 제공한다.

    Returns:
        pd.DataFrame: 샘플 데이터를 포함한 DataFrame.
            - id: 1, 2, 3
            - name: "Alice", "Bob", "Charlie"
            - value: 100.0, 200.0, 300.0

    Logics:
        1. 3행의 테스트 데이터 생성.
        2. 숫자형(id, value)과 문자형(name) 컬럼 포함.
        3. 테스트마다 새로운 인스턴스 생성.

    Example:
        >>> def test_with_fixture(sample_dataframe):
        ...     assert len(sample_dataframe) == 3
    """
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [100.0, 200.0, 300.0],
    })


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """빈 DataFrame 샘플.

    Returns:
        pd.DataFrame: 행과 컬럼이 없는 빈 DataFrame.

    Logics:
        1. 빈 DataFrame 생성.
        2. 엣지 케이스 테스트용으로 사용.
    """
    return pd.DataFrame()


@pytest.fixture
def mock_api_response() -> dict:
    """API 응답을 모의(Mock)한 딕셔너리.

    Returns:
        dict: API 응답 형식의 딕셔너리.
            - status: "success"
            - data: [{"id": 1, "name": "Test"}]

    Logics:
        1. 성공 상태의 API 응답 생성.
        2. 1개의 데이터 항목 포함.
        3. 외부 API 호출 없이 테스트 가능.
    """
    return {
        "status": "success",
        "data": [{"id": 1, "name": "Test"}],
    }
```

---

## 테스트 유형

### 단위 테스트 (--unit)

```python
# tests/unit/test_<module>.py

def test_<function>_<scenario>_<expected>():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

**특징**:
- 단일 함수/메서드 테스트
- 외부 의존성 Mocking
- 빠른 실행

### 통합 테스트 (--integration)

```python
# tests/integration/test_<feature>.py

@pytest.mark.integration
def test_<feature>_workflow():
    """Test full feature workflow."""
    # Setup
    # Execute workflow
    # Verify results
    # Cleanup
```

**특징**:
- 여러 컴포넌트 연동 테스트
- 실제 의존성 사용 (DB, API)
- 느린 실행, 별도 마커

---

## 명명 규칙

### 테스트 파일

```
tests/
├── unit/
│   └── test_<source_module>.py      # 소스 파일명과 일치
├── integration/
│   └── test_<feature>_integration.py
└── conftest.py
```

### 테스트 함수

```
test_<function>_<scenario>_<expected>

예시:
- test_process_data_with_valid_input_returns_dataframe
- test_calculate_total_with_negative_values_raises_error
- test_fetch_user_when_not_found_returns_none
```

### 테스트 클래스

```python
class Test<ClassName>:
    """Tests for <ClassName>."""

    def test_<method>_<scenario>_<expected>(self):
        ...
```

---

## Fixtures 전략

### 공통 Fixtures (conftest.py)

```python
# tests/conftest.py

@pytest.fixture
def db_session():
    """Database session fixture."""
    session = create_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def api_client():
    """API client fixture."""
    return TestClient(app)
```

### 모듈별 Fixtures

```python
# tests/unit/test_users.py

@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(id=1, name="Test User", email="test@example.com")
```

---

## Mocking 패턴

### 외부 API Mocking

```python
from unittest.mock import patch, MagicMock

def test_fetch_data_calls_api_correctly(self):
    """Test that API is called with correct parameters."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []}

    with patch("src.api.requests.get", return_value=mock_response) as mock_get:
        # Act
        result = fetch_data("endpoint")

        # Assert
        mock_get.assert_called_once_with("https://api.example.com/endpoint")
```

### 데이터베이스 Mocking

```python
from unittest.mock import patch

def test_get_user_returns_user_from_db(self, sample_user):
    """Test that get_user retrieves user from database."""
    # Arrange
    with patch("src.repository.db.query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = sample_user

        # Act
        result = get_user(1)

        # Assert
        assert result.id == sample_user.id
```

---

## Parametrize 활용

### 기본 사용

```python
@pytest.mark.parametrize(
    "input_value,expected",
    [
        (1, 2),
        (2, 4),
        (3, 6),
    ],
)
def test_double_returns_doubled_value(input_value, expected):
    assert double(input_value) == expected
```

### ID 지정

```python
@pytest.mark.parametrize(
    "input_value,expected",
    [
        pytest.param(0, 0, id="zero"),
        pytest.param(1, 1, id="one"),
        pytest.param(-1, 1, id="negative"),
    ],
)
def test_absolute_value(input_value, expected):
    assert abs(input_value) == expected
```

### 여러 인자 조합

```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    assert multiply(x, y) == x * y
```

---

## 출력 예시

```
╔══════════════════════════════════════════════════════════════╗
║                   TEST GENERATOR REPORT                       ║
╠══════════════════════════════════════════════════════════════╣
║ Source: src/utils.py                                          ║
║ Functions: 5 │ Classes: 2 │ Methods: 8                        ║
╚══════════════════════════════════════════════════════════════╝

✅ 생성된 파일:
   • tests/unit/test_utils.py (15 tests)
   • tests/conftest.py (3 fixtures added)

📋 생성된 테스트:
   • test_process_data_with_valid_input_returns_dataframe
   • test_process_data_with_empty_dataframe_returns_empty
   • test_process_data_with_none_raises_type_error
   • test_calculate_total_with_positive_values_returns_sum
   • test_calculate_total_with_empty_list_returns_zero
   • ... (10 more)

💡 수동 검토 필요:
   • fetch_external_data: 외부 API 의존성, Mock 설정 확인 필요
   • DatabaseHandler: 통합 테스트로 분리 권장
```

---

## uv 테스트 실행

> **참조**: `@.claude/docs/references/research/uv-best-practices.md`

생성된 테스트 코드는 `uv run`으로 실행한다:

```bash
# 단일 테스트 파일 실행
uv run pytest tests/test_utils.py -v

# 전체 테스트 실행 + 커버리지
uv run pytest tests/ -v --cov=src --cov-report=html

# 특정 테스트만 실행
uv run pytest tests/test_utils.py::test_function_name -v

# 파라미터화 테스트 실행
uv run pytest tests/ -v -k "parametrize"

# 디버그 모드
uv run pytest tests/ -v --pdb
```

테스트 실행 전 의존성 설치:
```bash
uv sync
uv run pytest tests/
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-testing/SKILL.md] | 테스트 코드 컨벤션 참조 |
| [@skills/check-test-quality/SKILL.md] | 테스트 품질 검증 |
| [@skills/systematic-debugging/SKILL.md] | 체계적 디버깅 |
| [@skills/code-review/SKILL.md] | 코드 리뷰 |
| [@skills/setup-uv-env/SKILL.md] | uv 환경 설정 |

## 참조

- uv 베스트 프랙티스: `@.claude/docs/references/research/uv-best-practices.md`

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.2.0 | 코드 예시 강화 (한국어 주석 + Google docstring) |
| 2026-01-21 | 1.1.0 | uv 테스트 실행 패턴 추가 |
| 2026-01-21 | 1.0.0 | 초기 생성 - pytest 기반 테스트 자동 생성 |
