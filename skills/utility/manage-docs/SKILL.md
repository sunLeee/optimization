---
name: manage-docs
triggers:
  - "manage docs"
description: 프로젝트 문서를 통합 관리한다. 문서 목록 조회, 상태 점검, 누락 감지를 지원한다.
argument-hint: "[action] - list, status, update, check"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Task
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: 문서 통합 관리 스킬이다. CLAUDE.md, README.md, docs/ 디렉토리의 문서를 관리한다.
agent: 당신은 기술 문서 관리자입니다. 프로젝트 문서의 일관성과 완성도를 관리합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 관리
skill-type: Atomic

- "manage-readme"
references:
  - "@skills/doc-adr/SKILL.md"
  - "@skills/manage-claude-md/SKILL.md"
  - "@skills/manage-readme/SKILL.md"
referenced-by:
  - "@skills/doc-adr/SKILL.md"
  - "@skills/manage-claude-md/SKILL.md"
  - "@skills/manage-readme/SKILL.md"

---
# manage-docs

프로젝트 문서를 통합 관리하는 스킬.

## 목적

- 프로젝트 내 모든 문서 목록 조회
- 문서 상태 점검 (수정일, 크기, 완성도)
- 필수 문서 누락 감지
- 개별 문서 관리 스킬 호출

## 사용법

```
/manage-docs list           # 문서 목록 조회
/manage-docs status         # 상태 점검
/manage-docs check          # 품질 검사
/manage-docs update readme  # README 업데이트
/manage-docs update claude  # CLAUDE.md 업데이트
```

## 관리 대상 문서

| 카테고리 | 경로 | 필수 |
|----------|------|:----:|
| Context | `.claude/CLAUDE.md` | O |
| Root | `README.md` | O |
| Architecture | `docs/architecture/*.md` | - |
| PRD | `tasks/*-prd.md` | - |
| ADR | `docs/adr/*.md` | - |
| API | `docs/api/*.md` | - |
| Scenarios | `docs/scenarios/*.md` | - |
| References | `docs/references/*.md` | - |

## 프로세스

### list 액션

```
/manage-docs list
    |
    v
[Step 1] 문서 스캔
    |-- Glob으로 MD 파일 검색
    |-- .claude/, docs/, README.md
    |
    v
[Step 2] 목록 분류
    |-- 카테고리별 그룹화
    |-- 수정일 정렬
    |
    v
[Step 3] 목록 출력
    |-- 테이블 형식
    |-- 파일명, 경로, 수정일
    |
    v
완료
```

### status 액션

```
/manage-docs status
    |
    v
[Step 1] 필수 문서 확인
    |-- CLAUDE.md 존재?
    |-- README.md 존재?
    |
    v
[Step 2] 문서 분석
    |-- 각 문서 크기
    |-- 최종 수정일
    |-- 완성도 추정 (섹션 수)
    |
    v
[Step 3] 경고 생성
    |-- 오래된 문서 (7일+)
    |-- 빈 문서
    |-- 누락 문서
    |
    v
[Step 4] 상태 보고서 출력
    |
    v
완료
```

### check 액션

```
/manage-docs check
    |
    v
[Step 1] 필수 문서 체크
    |
    v
[Step 2] 품질 검사
    |-- 깨진 내부 링크
    |-- 빈 섹션
    |-- TODO/FIXME 태그
    |
    v
[Step 3] 보고서 출력
    |
    v
완료
```

### update 액션

```
/manage-docs update [type]
    |
    v
[Step 1] 타입 확인
    |-- readme → /manage-readme 호출
    |-- claude → /manage-claude-md 호출
    |-- adr → /doc-adr 호출
    |
    v
[Step 2] 하위 스킬 실행
    |
    v
완료
```

## 예제

### 문서 목록 조회

```
User: /manage-docs list

Claude:
=== 프로젝트 문서 목록 ===

| 카테고리 | 파일 | 수정일 | 크기 |
|----------|------|--------|------|
| Context | .claude/CLAUDE.md | 2026-01-21 | 2.5KB |
| Root | README.md | 2026-01-20 | 3.2KB |
| Architecture | docs/architecture/system.md | 2026-01-19 | 5.1KB |
| PRD | tasks/auth-prd.md | 2026-01-18 | 8.4KB |
| ADR | docs/adr/ADR-001.md | 2026-01-15 | 1.8KB |
| ADR | docs/adr/ADR-002.md | 2026-01-16 | 2.1KB |
| Scenarios | docs/scenarios/user-auth.md | 2026-01-17 | 3.5KB |

총 7개 문서
```

### 상태 점검

```
User: /manage-docs status

Claude:
=== 문서 상태 점검 ===

필수 문서:
✅ .claude/CLAUDE.md (2.5KB, 2026-01-21)
✅ README.md (3.2KB, 2026-01-20)

문서 현황:
| 카테고리 | 개수 | 최신 수정일 |
|----------|------|-------------|
| Context | 1 | 2026-01-21 |
| Root | 1 | 2026-01-20 |
| Architecture | 1 | 2026-01-19 |
| PRD | 1 | 2026-01-18 |
| ADR | 2 | 2026-01-16 |

경고:
⚠️ docs/architecture/system.md - 7일 전 수정됨 (업데이트 권장)
⚠️ docs/adr/ADR-002.md - 본문 내용 부족 (500자 미만)

권장 조치:
1. /manage-claude-md 로 CLAUDE.md 업데이트 검토
2. docs/architecture/system.md 코드 변경 반영 확인
3. docs/adr/ADR-002.md 상세 내용 보완
```

### 품질 검사

```
User: /manage-docs check

Claude:
=== 문서 품질 검사 ===

필수 문서:
✅ .claude/CLAUDE.md 존재
✅ README.md 존재

링크 검사:
⚠️ docs/architecture/system.md:45 - 깨진 링크: ../api/auth.md
⚠️ README.md:23 - 깨진 링크: docs/setup-guide.md (파일 없음)

TODO/FIXME:
📌 tasks/auth-prd.md:78 - TODO: 에러 시나리오 추가
📌 docs/architecture/system.md:102 - FIXME: 다이어그램 업데이트

빈 섹션:
⚠️ docs/adr/ADR-002.md - "## 결정 사항" 섹션 비어 있음

요약:
- 깨진 링크: 2개
- TODO/FIXME: 2개
- 빈 섹션: 1개
```

### 개별 문서 업데이트

```
User: /manage-docs update readme

Claude:
/manage-readme 스킬을 호출합니다...

[manage-readme 실행 중]
...

README.md 업데이트 완료.
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/manage-claude-md/SKILL.md] | 하위 | CLAUDE.md 관리 |
| [@skills/manage-readme/SKILL.md] | 하위 | README.md 관리 |
| [@skills/doc-adr/SKILL.md] | 하위 | ADR 생성 |
| [@skills/sync-docs/SKILL.md] | 관련 | 문서 동기화 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-02-12 | 저장 경로 통일: docs/prd/ → tasks/ |
| 2026-01-21 | 초기 스킬 생성 |
