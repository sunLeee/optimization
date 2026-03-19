---
name: sync-skill-catalog
triggers:
  - "sync skill catalog"
description: "모든 스킬의 메타데이터를 자동 추출하여 skill-catalog.md를 동기화한다."
argument-hint: "[--auto-version] - 버전 자동 증분"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Write
model: claude-sonnet-4-6[1m]
context: 스킬 카탈로그를 자동으로 유지보수하는 스킬. 모든 SKILL.md 파일을 파싱하여 메타데이터를 추출하고, skill-catalog.md를 자동 생성한다. 버전 관리, 카테고리 분류, 글로벌 동기화를 지원한다.
agent: 당신은 스킬 카탈로그 관리 전문가입니다. 모든 스킬의 메타데이터를 정확히 추출하고 카탈로그를 자동으로 최신화합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 관리
skill-type: Atomic
references: []
referenced-by: []

---
# sync-skill-catalog

모든 스킬 메타데이터를 자동 추출하여 카탈로그를 동기화하는 스킬.

## 목적

- 스킬 추가/수정 시 자동 카탈로그 업데이트
- 버전 관리 자동화
- 메타데이터 일관성 유지
- 글로벌 디렉토리 동기화

## 사용법

```
/sync-skill-catalog              # 표준 동기화
/sync-skill-catalog --auto-version # 버전 자동 증분 (v1.16.0 → v1.17.0)
```

## 자동 추출 필드

| 필드 | 추출 위치 | 용도 |
|------|----------|------|
| `name` | frontmatter | 스킬 이름 |
| `description` | frontmatter | 설명 (카탈로그) |
| `user-invocable` | frontmatter | 호출 유형 (Primary/Internal) |
| `model` | frontmatter | 사용 모델 |
| `version` | Changelog | 스킬 버전 |
| `category` | 스킬명 분석 | 자동 분류 |
| `skill-type` | context 분석 | Atomic/Composite 판정 |

## 카테고리 분류 규칙

| 스킬명 패턴 | 카테고리 |
|-----------|----------|
| `check-*` | 코드 검증 |
| `quality-*` | 품질 관리 |
| `convention-*` | 컨벤션 참조 |
| `setup-*` | 환경 설정 |
| `doc-*` | 문서 생성 |
| `manage-*` | 문서 관리 |
| `ref-*` | 레퍼런스/시나리오 |

## 실행 예제

```
User: /sync-skill-catalog

Claude:
=== 스킬 카탈로그 동기화 ===

📊 스킬 파싱 중...
✅ 파싱 완료: 61개 스킬

📋 카테고리별 분류:
  개발 지원: 4개
  코드 검증: 8개
  ...

📝 카탈로그 생성 중...
✅ Project: /Users/hmc123/Documents/hyundai/.../skill-catalog.md
✅ Global: /Users/hmc123/.claude/docs/skill-catalog.md

===== 동기화 완료 =====
v1.16.0 → v1.17.0
61개 스킬 카탈로그 업데이트
```

## 통합 방식

### 1. 수동 호출
스킬 추가/수정 후 `/sync-skill-catalog` 실행.

### 2. manage-skill 통합
스킬 생성 후 자동으로 카탈로그 동기화.

### 3. Pre-commit Hook
`.git/hooks/pre-commit`에서 SKILL.md 변경 감지 시 자동 실행.

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - 스킬 카탈로그 자동 생성 |


## Gotchas (실패 포인트)

- skill-catalog.md가 실제 파일과 불일치 시 오래된 정보로 Claude 혼란
- 새 skill 추가 후 sync 미실행 시 catalog 누락
- name: 필드 없는 SKILL.md는 catalog에서 제외됨 — frontmatter 필수
- category 분류가 자동화되지 않음 — 수동 검토 필요
