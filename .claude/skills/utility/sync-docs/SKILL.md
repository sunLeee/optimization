---
name: sync-docs
triggers:
  - "sync docs"
description: 새로운 시나리오나 엣지케이스가 추가될 때 모든 관련 문서를 자동으로 업데이트한다. Traceability 기반으로 영향받는 문서를 식별하고 각 문서에 관련 내용을 반영한다. 사용자가 "문서 동기화", "시나리오 반영", "문서 업데이트" 등을 요청할 때 또는 /sync-docs를 호출할 때 사용한다. 호출 컨텍스트: - 단독 사용: 시나리오 추가 후 문서 동기화 시 직접 호출
argument-hint: "[시나리오 파일 경로]"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
model: claude-sonnet-4-6[1m]
context: 프로젝트 문서 간의 Traceability를 관리하며, 시나리오나 요구사항 변경 시 모든 관련 문서가 일관성을 유지하도록 업데이트한다.
agent: 문서 일관성 관리 전문가. 시나리오 분석과 영향도 평가에 능숙하며, 문서 간 참조 관계(Traceability)를 파악하여 체계적으로 업데이트를 수행한다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 관리
skill-type: Composite
references:
  - "@skills/doc-adr/SKILL.md"
referenced-by: []

---
# sync-docs (DEPRECATED)

> ⚠️ **이 스킬은 [@skills/doc-workflow/SKILL.md]에 통합되었습니다.**
>
> **사용 방법**:
> ```bash
> # 기존 (deprecated)
> /sync-docs docs/scenarios/scenario.md --auto-adr
>
> # 새 방법 (권장)
> /doc-workflow sync docs/scenarios/scenario.md --auto-adr
> ```
>
> **마이그레이션 가이드**: [@skills/doc-workflow/SKILL.md#mode-8-sync]

---

## 기존 문서 (참고용)

새로운 시나리오나 엣지케이스를 모든 관련 문서에 동기화한다.

## 목적

- 시나리오/엣지케이스 추가 시 관련 문서 자동 업데이트
- 문서 간 일관성 유지
- Traceability 기반 영향 범위 파악

## 사용법

```
/sync-docs <scenario-file-path> [--auto-adr] [--threshold=N] [--yes]
```

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| `scenario-file-path` | 동기화할 시나리오 파일 경로 | docs/references/scenarios/2026-01-21_auth-edge-case.md |
| `--auto-adr` | ADR 자동 생성 모드 활성화 | /sync-docs scenario.md --auto-adr |
| `--threshold=N` | ADR 자동 생성 신뢰도 임계값 (기본: 85) | --threshold=80 |
| `--yes` | 확인 프롬프트 생략 (임계값 이상 항목 자동 생성) | --auto-adr --yes |

### --auto-adr 모드

문서 동기화 완료 후 감지된 ADR 후보를 자동으로 생성한다.

**워크플로우:**

```
/sync-docs scenario.md --auto-adr
    ↓
[1~4단계] 문서 동기화 실행
    ↓
[5단계] ADR 후보 탐지
    ↓
[6단계] 사용자 확인 (--yes 시 생략)
    ├── 전체 승인 → 순차적 /doc-adr 실행
    ├── 선택 승인 → 선택된 항목만 실행
    └── 취소 → ADR 생성 건너뜀
    ↓
[7단계] ADR 생성 결과 요약
```

**--yes 플래그 (확인 생략):**

```bash
# 임계값(85%) 이상 ADR 후보를 확인 없이 자동 생성
/sync-docs scenario.md --auto-adr --yes

# 신뢰도 80% 이상 항목을 확인 없이 자동 생성
/sync-docs scenario.md --auto-adr --threshold=80 --yes
```

워크플로우 (--yes 모드):

```
/sync-docs scenario.md --auto-adr --yes
    ↓
[1~4단계] 문서 동기화 실행
    ↓
[5단계] ADR 후보 탐지
    ↓
[6단계] 임계값 이상 항목 자동 생성 (확인 생략)
    ↓
[7단계] ADR 생성 결과 요약
```

**확인 프롬프트:**

```markdown
## ADR 자동 생성 확인

다음 ADR을 자동 생성합니다:

| # | 결정 사항 | 신뢰도 | 상태 |
|---|----------|:------:|------|
| 1 | FastAPI 프레임워크 선택 | 90% | ✅ 승인 |
| 2 | PostgreSQL 데이터베이스 선택 | 85% | ✅ 승인 |
| 3 | Redis 캐시 도입 | 75% | ⚠️ 임계값 미달 |

진행할 항목을 선택하세요: [1,2] / [all] / [cancel]
```

**생성 순서:**

ADR은 다음 우선순위로 순차 생성된다:
1. 기반 기술 (DB, 언어, 프레임워크)
2. 아키텍처 패턴 (MSA, 계층 구조)
3. 통합 방식 (API, 메시징)
4. 운영 관련 (배포, 모니터링)

**결과 요약:**

```markdown
## Auto-ADR 결과

### 생성된 ADR (2개)
| ADR | 제목 | 위치 |
|-----|------|------|
| ADR-008 | FastAPI 프레임워크 선택 | docs/adr/ADR-008-fastapi.md |
| ADR-009 | PostgreSQL 데이터베이스 선택 | docs/adr/ADR-009-postgresql.md |

### 건너뛴 항목 (1개)
- Redis 캐시 도입 (신뢰도 75% < 임계값 85%)

### Traceability 갱신
- SCENARIO-008 → ADR-008, ADR-009
```

## 프로세스

### 1단계: 시나리오 파일 분석

시나리오 파일에서 핵심 정보를 추출한다:

```markdown
## 추출 항목
- 시나리오 ID / 제목
- 영향받는 기능/모듈
- 새로운 요구사항
- 엣지케이스 상세
- 테스트 조건
```

### 2단계: 영향받는 문서 식별 (Traceability 기반)

Traceability 링크를 따라 영향받는 문서를 찾는다:

```
시나리오 파일
    ↓
[Upstream 분석]
    ├── tasks/requirements.md (요구사항)
    ├── docs/architecture/system-design.md (아키텍처)
    └── docs/architecture/components.md (컴포넌트)
    ↓
[Downstream 분석]
    ├── docs/tasks/task-list.md (작업 분해)
    ├── docs/adr/ (관련 ADR)
    └── tests/ (테스트 케이스)
```

### 3단계: 각 문서 업데이트

문서 유형별로 적절한 섹션에 시나리오를 반영한다:

| 문서 유형 | 업데이트 위치 | 추가 내용 |
|----------|--------------|----------|
| PRD | 시나리오 섹션 | 새 시나리오 항목 추가 |
| Architecture | 엣지케이스 섹션 | 처리 방안 기술 |
| Components | 해당 컴포넌트 섹션 | 변경 사항 반영 |
| Tasks | 태스크 목록 | 새 태스크 추가 |
| ADR | 신규 ADR 생성 (필요시) | 결정 사항 기록 |
| Tests | 테스트 케이스 | 새 테스트 케이스 추가 |

### 4단계: 변경 사항 요약 출력

모든 업데이트 완료 후 요약을 출력한다:

```markdown
## Sync Summary

### 분석된 시나리오
- 파일: docs/references/scenarios/2026-01-21_auth-edge-case.md
- 제목: 토큰 만료 시 자동 갱신 처리

### 업데이트된 문서 (5개)
| 문서 | 변경 내용 | 라인 |
|------|----------|------|
| tasks/requirements.md | 시나리오 REQ-015 추가 | +12 |
| docs/architecture/system-design.md | 토큰 갱신 로직 섹션 추가 | +25 |
| docs/architecture/components.md | AuthService 섹션 업데이트 | +8 |
| docs/tasks/task-list.md | TASK-042 추가 | +5 |
| docs/adr/ADR-007-token-refresh.md | 신규 ADR 생성 | +45 |

### Traceability 갱신
- Upstream: REQ-015 ← SCENARIO-008
- Downstream: TASK-042, ADR-007, test_token_refresh.py
```

### 5단계: 다음 스킬 추천

시나리오의 **Decisions** 섹션을 분석하여 ADR이 필요한 결정 사항을 식별하고 추천한다.

#### ADR 필요 여부 판단 기준

| 조건 | ADR 필요 | 예시 |
|------|:--------:|------|
| 기술 스택 선택 | ● | 프레임워크, 데이터베이스, 라이브러리 |
| 아키텍처 패턴 결정 | ● | MSA vs 모놀리식, 인증 방식 |
| 트레이드오프 존재 | ● | 성능 vs 유지보수성 |
| 팀 영향 | ● | 다른 팀/모듈에 영향 |
| 되돌리기 어려움 | ● | DB 스키마, API 계약 |
| 단순 구현 선택 | ○ | 변수명, 파일 구조 |

#### 분석 대상

시나리오 파일의 다음 섹션을 분석한다:

```markdown
## Decisions

- [x] 프레임워크: FastAPI          ← ADR 후보
- [x] ORM: SQLAlchemy 2.0         ← ADR 후보
- [ ] 배포 방식 (미결정)          ← ADR 후보 (미결정 항목)
```

#### 기존 ADR 확인

```bash
# 기존 ADR 목록 확인하여 중복 제외
ls docs/adr/
```

#### 추천 출력 형식

```markdown
## 다음 스킬 추천

### ADR 생성 추천 (3개)

시나리오에서 ADR이 필요한 결정 사항을 감지했습니다:

| # | 결정 사항 | 유형 | 명령어 |
|---|----------|------|--------|
| 1 | FastAPI 선택 | 프레임워크 | `/doc-adr "FastAPI 프레임워크 선택"` |
| 2 | SQLAlchemy 2.0 | ORM | `/doc-adr "SQLAlchemy 2.0 ORM 선택"` |
| 3 | 배포 방식 | 인프라 (미결정) | `/doc-adr "배포 방식 결정"` |

### 기타 추천 스킬

| 스킬 | 이유 |
|------|------|
| `/diagram-generator` | 아키텍처 다이어그램 업데이트 필요 |
| `/test-generator` | 새 엣지케이스에 대한 테스트 필요 |

### 빠른 실행

\`\`\`bash
/doc-adr "FastAPI 프레임워크 선택"
\`\`\`
```

#### ADR 연쇄 생성 가이드

여러 ADR이 필요한 경우 우선순위:

1. **기반 기술 결정** (DB, 언어, 프레임워크)
2. **아키텍처 패턴** (MSA, 계층 구조)
3. **통합 방식** (API, 메시징)
4. **운영 관련** (배포, 모니터링)

#### Decisions 섹션 없는 시나리오 처리 (휴리스틱 탐지)

Decisions 섹션이 없는 시나리오에서도 ADR 후보를 자동 탐지한다.

**대체 소스 분석 순서:**

| 순서 | 소스 | 추출 방법 | 신뢰도 |
|:----:|------|----------|:------:|
| 1 | 기술 스택 섹션 | 명시된 기술명 파싱 | 90% |
| 2 | 요구사항 섹션 | 기술 키워드 탐지 | 85% |
| 3 | 코드 블록 | import/require 문 분석 | 80% |
| 4 | 메타데이터 | tech 필드 확인 | 75% |
| 5 | 본문 휴리스틱 | 패턴 매칭 | 70% |

**휴리스틱 탐지 규칙:**

```markdown
## 패턴 1: 키워드 기반 (신뢰도 85%)
- "선택", "결정", "채택" + 기술명
- 예: "FastAPI를 선택했다", "PostgreSQL로 결정"

## 패턴 2: 비교 표현 (신뢰도 80%)
- "A vs B", "A 대신 B", "A보다 B"
- 예: "Django 대신 FastAPI", "REST vs GraphQL"

## 패턴 3: 이유 설명 (신뢰도 75%)
- "~때문에", "~위해" + 기술명
- 예: "성능 때문에 Redis 도입", "확장성을 위해 MSA 채택"

## 패턴 4: 확정 표현 (신뢰도 70%)
- "~로 확정", "~를 사용"
- 예: "TypeScript로 확정", "Tailwind CSS를 사용"
```

**휴리스틱 결과 출력:**

```markdown
### 휴리스틱 ADR 후보 (Decisions 섹션 없음)

| # | 탐지된 기술 | 소스 | 신뢰도 | 명령어 |
|---|-----------|------|:------:|--------|
| 1 | FastAPI | 기술 스택 | 90% | `/doc-adr "FastAPI 프레임워크 선택"` |
| 2 | PostgreSQL | 요구사항 | 85% | `/doc-adr "PostgreSQL 데이터베이스 선택"` |
| 3 | Redis | 본문 휴리스틱 | 75% | `/doc-adr "Redis 캐시 도입"` |

⚠️ 신뢰도 70% 미만 항목은 표시하지 않음
```

**신뢰도 임계값:**

- **≥85%**: 자동 추천 (--auto-adr 시 자동 생성 대상)
- **70~84%**: 수동 확인 권장
- **<70%**: 추천에서 제외

## 시나리오 파일 형식

동기화할 시나리오 파일은 다음 형식을 따른다:

```markdown
# 시나리오: [제목]

## 메타데이터
- ID: SCENARIO-XXX
- 날짜: YYYY-MM-DD
- 작성자: [이름]
- 영향 범위: [모듈/기능 목록]

## 배경
[시나리오 발생 배경 설명]

## 상세 설명
[시나리오 상세 내용]

## 엣지케이스
- [ ] 케이스 1: ...
- [ ] 케이스 2: ...

## 예상 영향
- **요구사항**: [영향받는 요구사항 ID]
- **아키텍처**: [영향받는 컴포넌트]
- **테스트**: [추가 필요한 테스트]

## Traceability
- **Upstream**: [관련 PRD/요구사항]
- **Downstream**: [영향받는 문서/코드]
```

## 예시

### 예시 1: 인증 엣지케이스 동기화

```bash
/sync-docs docs/references/scenarios/2026-01-21_auth-edge-case.md
```

실행 결과:
```
[1단계] 시나리오 분석 완료
  - ID: SCENARIO-008
  - 제목: 토큰 만료 시 자동 갱신 처리
  - 영향 범위: AuthService, TokenManager, API Gateway

[2단계] 영향 문서 식별 완료
  - Upstream: tasks/requirements.md (REQ-010, REQ-011)
  - Downstream: 5개 문서 식별

[3단계] 문서 업데이트 진행
  - [1/5] tasks/requirements.md... 완료 (+12 lines)
  - [2/5] docs/architecture/system-design.md... 완료 (+25 lines)
  - [3/5] docs/architecture/components.md... 완료 (+8 lines)
  - [4/5] docs/tasks/task-list.md... 완료 (+5 lines)
  - [5/5] docs/adr/ADR-007-token-refresh.md... 생성 완료

[4단계] 동기화 완료
  - 총 5개 문서 업데이트
  - 총 95줄 추가
```

### 예시 2: 데이터 검증 시나리오 동기화

```bash
/sync-docs docs/references/scenarios/2026-01-21_data-validation.md
```

실행 결과:
```
[1단계] 시나리오 분석 완료
  - ID: SCENARIO-009
  - 제목: 대용량 데이터 입력 시 유효성 검증
  - 영향 범위: DataProcessor, Validator, InputHandler

[2단계] 영향 문서 식별 완료
  - Upstream: tasks/requirements.md (REQ-020)
  - Downstream: 3개 문서 식별

[3단계] 문서 업데이트 진행
  - [1/3] tasks/requirements.md... 완료 (+8 lines)
  - [2/3] docs/architecture/components.md... 완료 (+15 lines)
  - [3/3] docs/tasks/task-list.md... 완료 (+3 lines)

[4단계] 동기화 완료
  - 총 3개 문서 업데이트
  - 총 26줄 추가
```

### 예시 3: 여러 시나리오 일괄 동기화

```bash
# 특정 날짜의 모든 시나리오 동기화
/sync-docs docs/references/scenarios/2026-01-21_*.md
```

## 문서 업데이트 규칙

### PRD 업데이트

```markdown
## 시나리오 (Scenarios)

### SCENARIO-008: 토큰 만료 시 자동 갱신 처리 <!-- NEW -->

**배경**: 장시간 세션 유지 시 토큰 만료로 인한 사용자 경험 저하

**요구사항**:
- REQ-015: 토큰 만료 5분 전 자동 갱신 시도
- REQ-016: 갱신 실패 시 사용자에게 재로그인 안내

**Traceability**: ← SCENARIO-008
```

### Architecture 업데이트

```markdown
## 엣지케이스 처리

### EC-008: 토큰 자동 갱신 <!-- NEW -->

**상황**: 토큰 만료 임박 시 자동 갱신

**처리 방안**:
1. TokenManager가 만료 시간 모니터링
2. 만료 5분 전 갱신 요청 전송
3. 갱신 성공 시 새 토큰으로 교체
4. 갱신 실패 시 재로그인 플로우 트리거

**Traceability**: ← SCENARIO-008, REQ-015
```

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/save-scenario/SKILL.md] | 시나리오 파일 생성 |
| [@skills/doc-adr/SKILL.md] | ADR 문서 생성 (5단계 추천) |
| [@skills/manage-docs/SKILL.md] | 문서 통합 관리 |
| [@skills/doc-prd/SKILL.md] | PRD 문서 생성 |
| [@skills/doc-tasks/SKILL.md] | 작업 분해 생성 |
| [@skills/diagram-generator/SKILL.md] | 아키텍처 다이어그램 생성 |
| [@skills/test-generator/SKILL.md] | 테스트 케이스 생성 |

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-12 | 2.1.0 | 저장 경로 통일: docs/prd/requirements.md → tasks/requirements.md |
| 2026-01-28 | 2.0.0 | user-invocable: false, doc-workflow에 통합됨 (sync 모드) |
| 2026-01-21 | 1.4.0 | --yes 플래그 추가 (확인 프롬프트 생략) |
| 2026-01-21 | 1.3.0 | --auto-adr 플래그 추가, 휴리스틱 ADR 탐지 규칙 추가 |
| 2026-01-21 | 1.2.0 | 5단계 ADR 추천 기능 추가, 관련 스킬 확장 |
| 2026-01-21 | 1.1.0 | 전체 한국어화 (Phase → 단계) |
| 2026-01-21 | 1.0.0 | 초기 생성 |
