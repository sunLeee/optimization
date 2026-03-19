---
name: convention-data-validation
triggers:
  - "convention data validation"
description: "데이터 검증(Data Validation) 컨벤션 참조 스킬. Pydantic, Great Expectations, schema 검증으로 데이터 품질을 보장하고 입력 오류를 조기에 탐지한다."
argument-hint: "[섹션] - pydantic, great-expectations, schema, quality, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  데이터 입력 검증 및 품질 보장 전략을 제공한다.
  비즈니스 로직 실행 전 데이터 정합성 확보를 코드로 구현한다.
agent: |
  데이터 검증 전문가.
  Pydantic schema, Great Expectations, 데이터 품질 메트릭을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 데이터 검증(Data Validation) 컨벤션

Pydantic, Great Expectations, schema 검증을 통해 데이터 품질을 보장하는 규칙.

## 목적

- **입력 검증**: Pydantic으로 API/함수 입력값 검증
- **타입 안전성**: 런타임 타입 체크로 버그 조기 탐지
- **데이터 품질**: Great Expectations로 데이터셋 전체 검증
- **스키마 검증**: 구조 및 제약조건 명시
- **오류 추적**: 어느 필드, 어느 행에서 실패했는지 정확히 파악

---

## 1. Pydantic을 사용한 입력 검증

### 1.1 기본 모델 정의

**UserInputModel 클래스**: [@templates/skill-examples/convention-data-validation/pydantic-basic.py]

**필드 검증**:
- `user_id`: 1 이상의 정수 (`conint(ge=1)`)
- `email`: 유효한 이메일 형식 (`EmailStr`)
- `age`: 0~150 범위 (`conint(ge=0, le=150)`)
- `name`: 2~100자 문자열 (`constr(min_length=2, max_length=100)`)

**커스텀 검증**:
- `@field_validator`: 이메일 도메인 허용 목록 검증
- `@model_validator`: 나이와 생성 날짜의 일관성 검증

사용 예시:
```python
user_input = {
    'user_id': 1,
    'email': 'user@example.com',
    'name': 'John',
    'age': 30
}
result = create_user(user_input)
```

### 1.2 중첩된 모델 및 리스트

**중첩 모델 예시**: [@templates/skill-examples/convention-data-validation/pydantic-nested.py]

**AddressModel + UserProfileModel**:
- 주소 정보 (`AddressModel`) 중첩
- 관심사 리스트 (1~10개)
- 우편번호 정규식 검증 (`constr(regex=r'^\d{5}$')`)

---

## 2. Great Expectations를 사용한 데이터셋 검증

### 2.1 데이터셋 전체 검증

**Great Expectations 함수**: [@templates/skill-examples/convention-data-validation/great-expectations.py]

**Expectation 예시**:
- `expect_table_columns_to_match_set()`: 필수 컬럼 확인
- `expect_column_values_to_not_be_null()`: 결측치 비율 확인 (< 10%)
- `expect_column_values_to_be_between()`: 값 범위 확인 (age: 0~150)
- `expect_column_distinct_values_to_be_in_set()`: 유니크 값 확인

### 2.2 간단한 DataFrame 검증 헬퍼

**validate_dataframe_simple()**: 빠른 검증
- 빈 DataFrame 확인
- 필수 컬럼 존재 확인
- 컬럼별 결측치 비율 확인 (기본 10% 한계)

---

## 3. 스키마 검증

### 3.1 데이터 타입 스키마

**스키마 검증 함수**: [@templates/skill-examples/convention-data-validation/schema-validation.py]

타입 매핑:
- Python 타입 → Numpy/Pandas 타입 자동 매핑
- `int` → `int64`, `int32`
- `float` → `float64`, `float32`
- `str` → `object`

사용 예시:
```python
schema = {'age': int, 'name': str}
is_valid = validate_dataframe_schema(df, schema)
```

---

## 4. 데이터 품질 메트릭

### 4.1 품질 점수 계산

**품질 메트릭 함수**: [@templates/skill-examples/convention-data-validation/quality-metrics.py]

**메트릭 구성** (가중치 포함):
- **완성도 (Completeness, 40%)**: 결측치 비율
- **중복도 (Uniqueness, 30%)**: 중복행 비율
- **유효성 (Validity, 30%)**: 필수 컬럼 포함 여부

품질 점수: 0~100점

### 4.2 품질 리포트 생성

**generate_data_quality_report()**: 상세 리포트
- 타임스탬프, shape, 품질 점수
- 컬럼별 결측치 분석
- 중복행 개수
- 경고/오류 항목 식별

---

## 5. 엣지 케이스 처리

### 5.1 엣지 케이스 검증

**엣지 케이스 함수**: [@templates/skill-examples/convention-data-validation/edge-cases.py]

**검사 항목**:
- 빈 DataFrame 확인
- 모든 행이 결측치인 컬럼 확인
- 모든 행이 중복인 경우 확인
- 무한값 (inf, -inf) 검사
- 타입 불일치 검사

---

## 6. 종합 예제: 데이터 수집 파이프라인

**파이프라인 함수**: [@templates/skill-examples/convention-data-validation/pipeline-example.py]

**프로세스**:
1. Pydantic으로 입력 검증
2. DataFrame 변환
3. 스키마 검증
4. 엣지 케이스 검사
5. 품질 리포트 생성 (점수 < 70점 시 경고)
6. 검증 통과 시 DataFrame 반환

---

## 7. 데이터 검증 체크리스트

구현 완료 후 다음을 확인하세요:

- [ ] Pydantic BaseModel 정의 (필드 타입, 검증)
- [ ] Field validator 구현 (커스텀 검증 로직)
- [ ] Model validator 구현 (필드 간 검증)
- [ ] 중첩 모델 및 리스트 검증
- [ ] Great Expectations Expectation Suite 정의
- [ ] 스키마 검증 함수 구현
- [ ] 엣지 케이스 검증 (빈 DataFrame, 모든 null 컬럼 등)
- [ ] 데이터 품질 메트릭 계산
- [ ] 품질 리포트 생성
- [ ] 전체 파이프라인 통합 테스트
- [ ] 오류 처리 및 로깅 추가

---

## 8. 외부 도구

### 8.1 Pandera (대안)

**Pandera 예시**: [@templates/skill-examples/convention-data-validation/pandera-alternative.py]

Pydantic 대신 Pandera 사용 가능:
- DataFrame 전용 스키마 검증
- 더 직관적인 DataFrame 검증 API
- 조건부 검증 지원

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-data-handling/SKILL.md] | 데이터 처리 (결측치, 이상치) |
| [@skills/convention-error-handling/SKILL.md] | 에러 처리 (검증 실패) |
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |
| [@skills/test-generator/SKILL.md] | 테스트 작성 (검증 테스트) |

---

## 참고

- Pydantic Documentation: https://docs.pydantic.dev/
- Great Expectations: https://greatexpectations.io/
- Pandera: https://pandera.readthedocs.io/
- Python Data Validation: https://docs.python.org/3/library/inspect.html

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.1.0 | 보수적 리팩토링 - 973→262줄. Python 코드 예시를 템플릿으로 분리 |
| 2026-01-21 | 1.0.0 | 초기 생성 - Pydantic, Great Expectations, 스키마 검증 |

## Gotchas (실패 포인트)

- Pydantic v1 vs v2 API 불일치 — `validator` (v1) vs `field_validator` (v2)
- 검증 없이 외부 입력을 DB에 저장 → injection 위험
- 검증 로직이 여러 곳에 분산 — DRY 위반, 검증 누락 가능성
- Great Expectations는 초기 설정 복잡 — 소규모 프로젝트에서 overkill
