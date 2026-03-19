---
name: doc-adr
triggers:
  - "doc adr"
description: "아키텍처 결정 기록(ADR) 생성 스킬. Y-statement 형식으로 아키텍처 결정을 문서화한다."
argument-hint: "[결정 제목] - ADR 문서 생성"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: 아키텍처 결정 기록(ADR)을 생성한다. Y-statement 형식을 사용하여 결정의 맥락, 대안, 결과를 문서화한다. 기존 ADR과의 연결성을 관리한다.
agent: ADR 문서화 전문가. 아키텍처 결정의 배경, 대안, 트레이드오프를 명확하게 기록한다. 결정의 추적성과 일관성을 유지한다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 생성
skill-type: Atomic
references:
  - "@skills/doc-sys/SKILL.md"
  - "@skills/doc-workflow/SKILL.md"
  - "@skills/manage-docs/SKILL.md"
  - "@skills/sync-docs/SKILL.md"
referenced-by:
  - "@skills/doc-sys/SKILL.md"
  - "@skills/doc-workflow/SKILL.md"
  - "@skills/manage-docs/SKILL.md"
  - "@skills/sync-docs/SKILL.md"

---
# ADR 생성

아키텍처 결정 기록(Architecture Decision Record)을 생성한다.

## 목적

- 아키텍처 결정의 체계적 문서화
- Y-statement 형식 표준화
- 결정 이력 추적
- 팀 간 지식 공유

## 사용법

```
/doc-adr "데이터베이스 선택"
/doc-adr "인증 방식 결정"
/doc-adr "API 버저닝 전략"
/doc-adr list                    # 기존 ADR 목록
/doc-adr supersede ADR-001       # 기존 ADR 대체
```

### AskUserQuestion 활용 지점

**지점 1: 결정 컨텍스트 확인**

ADR 작성 시 배경과 컨텍스트를 명확히 한다:

```yaml
AskUserQuestion:
  questions:
    - question: "이 결정의 배경과 컨텍스트를 설명해주세요"
      header: "결정 배경"
      multiSelect: false
      options:
        - label: "대화 내용 기반 자동 추출 (권장)"
          description: "현재 대화에서 배경 정보 자동 요약"
        - label: "직접 입력"
          description: "사용자가 직접 컨텍스트 작성"
```

**지점 2: 대안 탐색**

검토한 다른 대안들을 기록한다:

```yaml
AskUserQuestion:
  questions:
    - question: "검토했던 다른 대안들이 있나요?"
      header: "대안"
      multiSelect: true
      options:
        - label: "[대안 1]"
          description: "장점: [설명] | 단점: [설명] | 거부 이유: [설명]"
        - label: "[대안 2]"
          description: "장점: [설명] | 단점: [설명] | 거부 이유: [설명]"
        - label: "직접 입력"
          description: "다른 대안 추가"
```

---

## ADR 템플릿

### 기본 구조

```markdown
# ADR-{번호}: {제목}

**상태**: Proposed | Accepted | Deprecated | Superseded by ADR-XXX
**날짜**: YYYY-MM-DD
**결정자**: {이름/팀}

## 컨텍스트 (Context)

{현재 상황과 결정이 필요한 이유}

## 결정 (Decision)

### Y-Statement

> **In the context of** {상황},
> **facing** {문제/도전},
> **we decided** {결정},
> **and neglected** {거부한 대안},
> **to achieve** {목표},
> **accepting** {트레이드오프}.

### 상세 설명

{결정에 대한 상세 설명}

## 대안 (Alternatives Considered)

### 대안 1: {이름}

**설명**: {대안 설명}

**장점**:
- {장점 1}
- {장점 2}

**단점**:
- {단점 1}
- {단점 2}

**거부 이유**: {거부 이유}

### 대안 2: {이름}

...

## 결과 (Consequences)

### 긍정적 영향

- {긍정적 결과 1}
- {긍정적 결과 2}

### 부정적 영향

- {부정적 결과 1}
- {부정적 결과 2}

### 리스크

- {리스크 1}
- {리스크 2}

## 관련 문서 (Related)

- **Upstream**: {이 결정에 영향을 준 문서}
- **Downstream**: {이 결정에 영향을 받는 문서}
- **Related ADRs**: ADR-XXX, ADR-YYY
```

---

## Y-Statement 형식

### 구조

```
In the context of {상황},
facing {문제/도전},
we decided {결정},
and neglected {거부한 대안},
to achieve {목표},
accepting {트레이드오프}.
```

### 예시: 데이터베이스 선택

```
In the context of 실시간 분석 데이터 저장,
facing 대규모 시계열 데이터 처리 요구,
we decided PostgreSQL with TimescaleDB 확장을 사용하기로,
and neglected InfluxDB와 순수 PostgreSQL을,
to achieve 시계열 쿼리 성능 최적화와 SQL 호환성,
accepting TimescaleDB 학습 곡선과 추가 운영 복잡성을.
```

### 예시: 인증 방식

```
In the context of 마이크로서비스 API 인증,
facing 서비스 간 안전한 통신 요구,
we decided JWT 기반 Bearer 토큰 인증을 사용하기로,
and neglected Session 기반 인증과 API Key를,
to achieve 무상태 인증과 서비스 독립성,
accepting 토큰 관리 복잡성과 토큰 탈취 리스크를.
```

---

## 생성 프로세스

### 1단계: 정보 수집

```
질문:
1. 어떤 결정을 문서화하려고 하시나요?
2. 현재 상황과 제약 조건은 무엇인가요?
3. 고려한 대안들은 무엇인가요?
4. 최종 결정의 이유는 무엇인가요?
```

### 2단계: ADR 번호 할당

```bash
# 기존 ADR 확인
ls docs/adr/

# 다음 번호 결정
ADR-001.md  →  ADR-002.md
```

### 3단계: 문서 생성

```
docs/adr/ADR-{번호}-{제목-kebab-case}.md
```

### 4단계: 인덱스 업데이트

```markdown
# docs/adr/README.md

## ADR 목록

| 번호 | 제목 | 상태 | 날짜 |
|------|------|------|------|
| ADR-001 | 데이터베이스 선택 | Accepted | 2026-01-15 |
| ADR-002 | 인증 방식 결정 | Accepted | 2026-01-20 |
| ADR-003 | API 버저닝 전략 | Proposed | 2026-01-21 |
```

---

## 상태 관리

### 상태 유형

| 상태 | 설명 |
|------|------|
| **Proposed** | 검토 중인 결정 |
| **Accepted** | 승인된 결정 |
| **Deprecated** | 더 이상 유효하지 않음 |
| **Superseded** | 다른 ADR로 대체됨 |

### 상태 전이

```
Proposed → Accepted
         → Rejected (삭제 또는 보관)

Accepted → Deprecated
         → Superseded by ADR-XXX
```

### Supersede 처리

```markdown
# ADR-001: 데이터베이스 선택 (SUPERSEDED)

**상태**: Superseded by [ADR-005](ADR-005-database-migration.md)
**날짜**: 2026-01-15
**대체일**: 2026-03-01

> ⚠️ 이 ADR은 ADR-005로 대체되었습니다.
```

---

## 디렉토리 구조

```
docs/
└── adr/
    ├── README.md                    # ADR 인덱스
    ├── _template.md                 # ADR 템플릿
    ├── ADR-001-database-selection.md
    ├── ADR-002-authentication-method.md
    └── ADR-003-api-versioning.md
```

---

## 실제 예시

### ADR-001: PostgreSQL 선택

```markdown
# ADR-001: 데이터베이스 선택

**상태**: Accepted
**날짜**: 2026-01-15
**결정자**: 백엔드 팀

## 컨텍스트

대중교통 취약지역 분석 시스템을 위한 데이터베이스를 선택해야 한다.
요구사항:
- 공간 데이터 처리 (GIS)
- 대량 데이터 배치 처리
- SQL 기반 분석 쿼리
- 오픈소스 선호

## 결정

### Y-Statement

> **In the context of** 공간 데이터 기반 분석 시스템 구축,
> **facing** GIS 기능과 대규모 배치 처리 요구,
> **we decided** PostgreSQL + PostGIS를 사용하기로,
> **and neglected** MySQL, MongoDB, DuckDB를,
> **to achieve** 강력한 공간 쿼리 기능과 SQL 호환성,
> **accepting** 초기 설정 복잡성과 클라우드 비용 증가를.

### 상세 설명

PostgreSQL + PostGIS 조합은 공간 데이터 처리에 최적화되어 있으며,
ST_Within, ST_Distance 등 GIS 함수를 네이티브로 지원한다.

## 대안

### MySQL + Spatial Extensions

**장점**: 익숙한 기술, 낮은 학습 곡선
**단점**: PostGIS 대비 제한적인 공간 기능
**거부 이유**: 복잡한 공간 쿼리 지원 부족

### MongoDB + GeoJSON

**장점**: 유연한 스키마, 스케일 아웃 용이
**단점**: 복잡한 공간 조인 어려움
**거부 이유**: SQL 기반 분석 요구사항과 불일치

### DuckDB (인메모리)

**장점**: 빠른 분석 쿼리, 설치 불필요
**단점**: 영구 저장 제한, 동시성 제한
**거부 이유**: 프로덕션 데이터베이스로 부적합

## 결과

### 긍정적 영향

- 강력한 GIS 기능으로 공간 분석 가능
- SQL 표준 준수로 분석가 접근성 향상
- 풍부한 생태계와 커뮤니티 지원

### 부정적 영향

- PostGIS 확장 설정 필요
- 수평 확장 제한 (수직 확장 우선)

### 리스크

- 대용량 데이터 시 쿼리 성능 저하 가능
- 완화: 파티셔닝, 인덱스 최적화 적용

## 관련 문서

- **Upstream**: tasks/requirements-prd.md
- **Downstream**: docs/architecture/database-schema.md
- **Related ADRs**: 없음
```

---

## 출력 예시

```
╔══════════════════════════════════════════════════════════════╗
║                      ADR CREATED                              ║
╠══════════════════════════════════════════════════════════════╣
║ ADR-003: API 버저닝 전략                                      ║
╚══════════════════════════════════════════════════════════════╝

✅ 생성된 파일:
   • docs/adr/ADR-003-api-versioning.md

📋 업데이트:
   • docs/adr/README.md (인덱스 추가)

💡 다음 단계:
   1. ADR 내용 검토
   2. 팀 리뷰 요청
   3. 상태를 Proposed → Accepted로 변경
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/doc-sys/SKILL.md] | 시스템 아키텍처 문서 |
| [@skills/doc-spec/SKILL.md] | 기술 명세 문서 |
| [@skills/doc-prd/SKILL.md] | 제품 요구사항 문서 |
| [@skills/project-init/SKILL.md] | 프로젝트 초기화 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-12 | 1.2.0 | 저장 경로 통일: docs/prd/ → tasks/ |
| 2026-01-28 | 1.1.0 | user-invocable: false로 변경 (doc-workflow 내부 호출) |
| 2026-01-21 | 1.0.0 | 초기 생성 - Y-statement 기반 ADR 생성 |
