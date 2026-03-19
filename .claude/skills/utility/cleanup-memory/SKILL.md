---
name: cleanup-memory
triggers:
  - "cleanup memory"
description: "CLAUDE.md를 정리하고 최적화하는 스킬. 50번 대화마다 자동으로 실행이 권장되며, 불필요한 내용 제거, 중복 통합, 구조 개선을 수행한다."
argument-hint: "[--dry-run] [--aggressive] [--section=<섹션>]"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
model: claude-haiku-4-5-20251001
context: |
  CLAUDE.md의 크기와 구조를 최적화하여 컨텍스트 효율성을 높인다.
  토큰 경제학 원칙에 따라 30-40% 컨텍스트 윈도우 사용률을 목표로 한다.
agent: |
  메모리 정리 전문가. CLAUDE.md의 내용을 분석하고,
  불필요한 정보 제거, 중복 통합, 구조 개선을 통해 최적화된 버전을 생성한다.
  importance-scorer 기준을 역으로 적용하여 저중요도 항목을 식별한다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 관리
skill-type: Atomic
references:
  - "@skills/project-init/SKILL.md"
  - "@skills/reset-counter/SKILL.md"
referenced-by:
  - "@skills/memory-workflow/SKILL.md"
  - "@skills/project-init/SKILL.md"
  - "@skills/reset-counter/SKILL.md"

---
# cleanup-memory

> CLAUDE.md 정리 및 최적화 스킬

---

## 목적

1. **불필요 정보 제거**: 일회성, 만료된, 중복 정보 삭제
2. **구조 최적화**: 계층 구조 정리, 섹션 통합
3. **토큰 절약**: 컨텍스트 윈도우 효율성 향상
4. **가독성 개선**: 명확하고 간결한 표현으로 정리

---

## 사용법

```
/cleanup-memory [옵션]
```

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 변경 미리보기만 표시 (기본값) |
| `--apply` | 실제 변경 적용 |
| `--aggressive` | 적극적 정리 (더 많은 항목 제거) |
| `--section=<섹션>` | 특정 섹션만 정리 |

---

## 정리 대상

### 1. 즉시 제거 (High Priority)

```
탐지 기준:
- 완료된 작업 항목 (체크된 할일)
- 7일 이상 지난 임시 메모
- 더 이상 존재하지 않는 파일 참조
- 중복된 명령어/설정
```

**액션**: 즉시 삭제 권장

### 2. 통합 대상 (Medium Priority)

```
탐지 기준:
- 유사한 내용의 분산된 항목
- 같은 카테고리의 중복 섹션
- 반복되는 경고/주의사항
```

**액션**: 하나로 통합

### 3. 압축 대상 (Medium Priority)

```
탐지 기준:
- 과도하게 상세한 설명
- 불필요한 예시 코드
- 장황한 문장
```

**액션**: 간결하게 압축

### 4. 보관 대상 (Low Priority)

```
탐지 기준:
- 유용하지만 자주 참조되지 않는 정보
- 특정 상황에서만 필요한 가이드
- 히스토리성 정보
```

**액션**: Level 3 (references/)로 이동

---

## 실행 프로세스

### Step 1: 현재 상태 분석

```
1. CLAUDE.md 파일 크기 측정
2. 섹션별 라인 수 계산
3. 최근 수정일 확인
4. 참조 빈도 추정
```

### Step 2: 정리 대상 식별

```
각 항목에 대해:
- 정리 유형 분류 (제거/통합/압축/보관)
- 우선순위 결정
- 예상 절감 토큰 수 계산
```

### Step 3: 정리 계획 제시

```markdown
## Cleanup 계획

### 현재 상태
- 전체 라인: 244줄
- 예상 토큰: ~2,500 토큰
- 권장 최대: ~2,000 토큰

### 정리 계획

#### 제거 예정 (High Priority)
1. **완료된 작업** (8줄 절감)
   - "Section 8: 현재 작업 컨텍스트" 내 완료 항목

2. **만료된 참조** (5줄 절감)
   - 삭제된 파일 경로 참조

#### 통합 예정 (Medium Priority)
3. **중복 명령어** (10줄 절감)
   - Quick Commands 섹션 정리

#### Level 3 이동 (Low Priority)
4. **상세 가이드** (20줄 절감)
   - 트러블슈팅 가이드 → references/

### 예상 결과
- 절감: 43줄 (~430 토큰)
- 최종: 201줄 (~2,000 토큰)
```

### Step 4: 사용자 확인

```
적용할 항목을 선택하세요:
[x] 1. 완료된 작업 제거
[x] 2. 만료된 참조 제거
[ ] 3. 중복 명령어 통합
[ ] 4. Level 3 이동
```

### Step 5: 정리 실행

`--apply` 옵션 사용 시:
- 선택된 항목만 적용
- 변경 전 백업 생성
- 변경 전후 diff 표시

---

## 정리 규칙

### 제거 규칙

| 조건 | 액션 |
|------|------|
| 완료된 할일 (7일 이상) | 제거 |
| 존재하지 않는 파일 참조 | 제거 |
| 중복 항목 | 하나만 유지 |
| 빈 섹션 | 제거 |

### 보존 규칙

| 조건 | 액션 |
|------|------|
| Quick Commands | 항상 유지 |
| 기술 스택 정보 | 유지 |
| Memory Hierarchy | 유지 |
| 자동 적용 Rules | 유지 |

### 이동 규칙

| 조건 | 이동 대상 |
|------|----------|
| 상세 트러블슈팅 | `.claude/docs/references/` |
| 히스토리 정보 | `docs/adr/` |
| 상세 가이드 | `.claude/docs/conventions/` |

---

## 출력 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Memory Cleanup 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 현재 상태

| 항목 | 값 |
|------|-----|
| 전체 라인 | 244줄 |
| 예상 토큰 | ~2,500 |
| 마지막 정리 | 2026-01-15 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## [HIGH] 즉시 제거 권장

### 1. 완료된 작업 컨텍스트

```diff
- ### 진행 중인 작업
- - [x] license-guide 스킬 생성 완료
- - [x] project-init 통합 완료
```

예상 절감: 8줄 (~80 토큰)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## [MEDIUM] 통합 권장

### 2. Quick Commands 중복

현재:
```bash
uv run pytest tests/ -v
uv run pytest tests/ -v --tb=short
```

권장:
```bash
uv run pytest tests/ -v --tb=short
```

예상 절감: 2줄 (~20 토큰)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 요약

| 카테고리 | 항목 수 | 예상 절감 |
|----------|--------|----------|
| 즉시 제거 | 2 | ~100 토큰 |
| 통합 | 1 | ~20 토큰 |
| Level 3 이동 | 0 | 0 |
| **총계** | **3** | **~120 토큰** |

적용하시겠습니까? /cleanup-memory --apply
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/recommend-memory/SKILL.md] | CLAUDE.md 추가 제안 |
| [@skills/manage-claude-md/SKILL.md] | CLAUDE.md 직접 수정 |
| [@skills/importance-scorer/SKILL.md] | 중요도 평가 기준 |
| [@skills/done/SKILL.md] | 작업 완료 시 정리 제안 |

---

## 자동 트리거

`message-counter.sh` hook에 의해 50번 대화마다 실행 권장 메시지가 표시된다.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [Memory Cleanup] 50번째 대화입니다.
  /cleanup-memory 실행을 권장합니다.
  CLAUDE.md를 정리하여 컨텍스트 효율성을 높이세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.1.0 | user-invocable: false로 변경 (memory-workflow 내부 호출) |
| 2026-01-21 | 1.0.0 | 초기 생성 - CLAUDE.md 정리 및 최적화 스킬 |

## Gotchas (실패 포인트)

- 실행 전 현재 CLAUDE.md 백업 권장
- 중요 결정이 메모리 정리로 제거되지 않도록 ADR 먼저 작성
- 50번 대화 주기 기준은 프로젝트 규모에 따라 조정
- cleanup 후 Claude Code 재시작으로 새 CLAUDE.md 반영
