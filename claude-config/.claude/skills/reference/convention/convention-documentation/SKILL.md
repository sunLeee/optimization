---
name: convention-documentation
triggers:
  - "convention documentation"
description: 문서 작성 컨벤션 참조 스킬. 마크다운 스타일, README 구조, 기술 문서 템플릿 등 문서 작성 시 준수해야 할 규칙을 제공한다. 문서 작성 시 이 스킬을 참조하여 일관된 문서를 유지한다.
argument-hint: "[섹션] - markdown, readme, technical, api, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: 문서 작성 시 참조해야 할 컨벤션을 제공한다. 마크다운 스타일, README 구조, 기술 문서 템플릿을 포함한다.
agent: 기술 문서 작성 가이드 전문가. 명확하고 일관된 문서 작성 규칙을 제시하고, 프로젝트 유형별 문서 구조를 안내한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 문서 작성 컨벤션

기술 문서 작성 시 준수해야 할 규칙을 제공한다.

## 목적

- 문서의 일관된 스타일 유지
- 마크다운 작성 규칙 참조
- README, 기술 문서 템플릿 제공
- 프로젝트별 문서 구조 가이드

## 사용법

```
/convention-documentation [섹션]
```

| 섹션 | 설명 |
|------|------|
| `markdown` | 마크다운 스타일 규칙 |
| `readme` | README.md 구조 |
| `technical` | 기술 문서 템플릿 |
| `api` | API 문서 규칙 |
| `all` | 전체 규칙 (기본값) |

---

## 0. 핵심 원칙

| 원칙 | 설명 |
|-----|------|
| **명확성 우선** | 독자가 이해하기 쉽게 작성 |
| **일관성 유지** | 동일한 스타일과 구조 사용 |
| **최신성 유지** | 코드 변경 시 문서도 업데이트 |
| **예제 포함** | 실행 가능한 코드 예제 제공 |

---

## 1. 마크다운 스타일

### 1.1 제목 계층

```markdown
# 문서 제목 (H1 - 파일당 1개만)
## 주요 섹션 (H2)
### 하위 섹션 (H3)
#### 세부 항목 (H4 - 최대 깊이)
```

**규칙**:
- H1은 파일당 1개만 사용
- 제목 레벨을 건너뛰지 않음 (H2 → H4 금지)
- 제목 전후에 빈 줄 1개

### 1.2 코드 블록

언어 명시 필수:

````markdown
```python
def hello():
    return "Hello, World!"
```

```bash
uv run python -m src.main
```

```yaml
config:
  debug: true
```
````

**규칙**:
- 언어 태그 필수 지정
- 실행 가능한 예제 포함
- 출력 결과는 주석으로 표시

```python
result = calculate(10, 20)
print(result)  # 출력: 30
```

### 1.3 목록

```markdown
# 순서 없는 목록 (항목 나열)
- 첫 번째 항목
- 두 번째 항목
  - 중첩 항목

# 순서 있는 목록 (단계별 절차)
1. 첫 번째 단계
2. 두 번째 단계
3. 세 번째 단계
```

### 1.4 표

```markdown
| 헤더 1 | 헤더 2 | 헤더 3 |
|--------|--------|--------|
| 값 1   | 값 2   | 값 3   |
| 값 4   | 값 5   | 값 6   |
```

**규칙**:
- 헤더와 구분선 필수
- 셀 내용 정렬: 왼쪽 `|:---|`, 중앙 `|:---:|`, 오른쪽 `|---:|`

### 1.5 링크와 이미지

```markdown
# 상대 경로 (권장)
[설정 가이드](./docs/setup.md)
![아키텍처](./docs/images/architecture.png)

# 절대 경로 (금지)
[Bad Link](/Users/name/project/docs/setup.md)
```

---

## 2. README.md 구조

### 2.1 필수 섹션

```markdown
# 프로젝트 이름

프로젝트 목적을 1-2문장으로 설명한다.

## 설치

​```bash
uv sync
​```

## 빠른 시작

​```bash
uv run python -m src.main
​```

## 주요 기능

- 기능 1: 설명
- 기능 2: 설명

## 라이선스

MIT License
```

### 2.2 선택 섹션

| 섹션 | 포함 시점 |
|------|----------|
| **요구사항** | 특별한 의존성이 있을 때 |
| **환경 설정** | 환경 변수 설정이 필요할 때 |
| **API 문서** | API가 있을 때 |
| **기여 가이드** | 오픈소스일 때 |
| **Changelog** | 버전 관리가 중요할 때 |

### 2.3 배지 (선택)

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

---

## 3. 기술 문서 템플릿

### 3.1 기능/모듈 문서

```markdown
# 모듈 이름

## 개요

모듈의 목적을 1-2문장으로 설명한다.

## 사용법

​```python
from module import function
result = function(arg1, arg2)
​```

## API 레퍼런스

### `function(arg1, arg2)`

설명: 함수의 목적

**파라미터**:
- `arg1` (str): 첫 번째 인자
- `arg2` (int): 두 번째 인자

**반환값**:
- `Result`: 처리 결과 객체

**예외**:
- `ValueError`: 잘못된 입력

## 예제

### 기본 사용

​```python
result = function("hello", 42)
print(result)
​```

### 고급 사용

​```python
# 옵션과 함께 사용
result = function("hello", 42, verbose=True)
​```
```

### 3.2 아키텍처 문서

```markdown
# 시스템 아키텍처

## 개요

시스템의 전체 구조를 설명한다.

## 컴포넌트 다이어그램

​```mermaid
graph TB
    A[Client] --> B[API Gateway]
    B --> C[Service Layer]
    C --> D[Database]
​```

## 컴포넌트 설명

### API Gateway
- 역할: 요청 라우팅, 인증
- 기술: FastAPI

### Service Layer
- 역할: 비즈니스 로직
- 패턴: Repository 패턴

## 데이터 흐름

1. 클라이언트가 API 요청
2. Gateway가 인증 확인
3. Service가 로직 처리
4. DB에 저장/조회
```

---

## 4. API 문서 규칙

### 4.1 엔드포인트 문서

```markdown
## POST /api/users

사용자를 생성한다.

### Request

**Headers**:
- `Authorization`: Bearer token

**Body**:
​```json
{
  "name": "홍길동",
  "email": "hong@example.com"
}
​```

### Response

**200 OK**:
​```json
{
  "id": 1,
  "name": "홍길동",
  "email": "hong@example.com"
}
​```

**400 Bad Request**:
​```json
{
  "error": "Invalid email format"
}
​```
```

### 4.2 OpenAPI/Swagger

FastAPI 사용 시 자동 생성된 문서 활용:

```python
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """사용자를 생성한다.

    Args:
        user: 사용자 생성 정보

    Returns:
        생성된 사용자 정보
    """
```

---

## 5. 금지 사항

| 항목 | 이유 | 대안 |
|------|------|------|
| 절대 경로 | 환경 의존성 | 상대 경로 사용 |
| 하드코딩된 버전 | 유지보수 어려움 | 변수/참조 사용 |
| 오래된 스크린샷 | 불일치 발생 | 텍스트 기반 설명 |
| 비실행 코드 예제 | 신뢰도 저하 | 실행 가능한 예제 |
| 중복 문서 | 불일치 위험 | 단일 소스 원칙 |

---

## 6. 문서 유지보수

### 6.1 업데이트 트리거

| 이벤트 | 업데이트 대상 |
|--------|--------------|
| API 변경 | API 문서, README |
| 설정 변경 | 설정 가이드, README |
| 아키텍처 변경 | 아키텍처 문서, ADR |
| 기능 추가 | README, 기능 문서 |

### 6.2 문서 리뷰 체크리스트

```markdown
- [ ] 코드 예제가 실행 가능한가?
- [ ] 링크가 모두 유효한가?
- [ ] 제목 계층이 올바른가?
- [ ] 최신 코드와 일치하는가?
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/manage-readme/SKILL.md] | README 생성/업데이트 |
| [@skills/doc-prd/SKILL.md] | PRD 문서 생성 |
| [@skills/doc-adr/SKILL.md] | ADR 생성 |
| [@skills/doc-spec/SKILL.md] | 기술 명세서 생성 |
| [@skills/sync-docs/SKILL.md] | 문서 동기화 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - 마크다운, README, 기술 문서, API 문서 규칙 통합 |

## Gotchas (실패 포인트)

- README에 설치/실행 방법 누락 시 신규 팀원이 환경 세팅 못함
- 기술 용어는 영어, 설명은 한국어 원칙 — 혼용 금지
- 마크다운 링크 경로가 이동 후 깨지는 경우 많음 — 상대 경로 vs 절대 경로 확인
