---
name: recommend-memory
triggers:
  - "recommend memory"
description: "대화에서 학습한 내용을 분석하여 CLAUDE.md 업데이트를 추천하는 스킬. 10번 대화마다 자동으로 실행이 권장되며, 중요한 패턴, 결정, 워크플로우를 식별한다."
argument-hint: "[--dry-run] [--section=작업컨텍스트|워크플로우|명령어]"
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
  대화 히스토리를 분석하여 CLAUDE.md에 추가할 가치가 있는 내용을 식별한다.
  중요도 평가 기준: 반복 사용 패턴, 아키텍처 결정, 새로운 워크플로우, 트러블슈팅 경험.
agent: |
  메모리 관리 전문가. 대화에서 핵심 학습 내용을 추출하고,
  CLAUDE.md의 적절한 섹션에 배치할 구체적인 추천을 제공한다.
  importance-scorer 스킬의 기준을 참조하여 중요도를 평가한다.
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
# recommend-memory

> 대화 분석 기반 CLAUDE.md 업데이트 추천 스킬

---

## 목적

1. **학습 내용 추출**: 대화에서 반복되는 패턴, 결정사항 식별
2. **중요도 평가**: importance-scorer 기준으로 가치 판단
3. **구체적 추천**: CLAUDE.md의 어느 섹션에 무엇을 추가할지 제안
4. **선택적 적용**: 사용자 확인 후 업데이트

---

## 사용법

```
/recommend-memory [옵션]
```

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 추천만 표시, 실제 수정 안함 (기본값) |
| `--apply` | 사용자 확인 후 직접 적용 |
| `--section=<섹션>` | 특정 섹션만 분석 |

---

## 분석 대상

### 1. 반복 패턴 (High Priority)

```
탐지 기준:
- 동일 명령어 3회 이상 사용
- 같은 파일 패턴 반복 접근
- 유사한 질문 반복
```

**추천 위치**: Quick Commands 또는 워크플로우 섹션

### 2. 아키텍처 결정 (High Priority)

```
탐지 기준:
- "결정", "선택", "이유" 키워드 포함 대화
- 기술 스택 관련 논의
- 트레이드오프 분석
```

**추천 위치**: ADR 생성 또는 주의사항 섹션

### 3. 트러블슈팅 경험 (Medium Priority)

```
탐지 기준:
- 에러 해결 과정
- "문제", "해결", "수정" 키워드
- 디버깅 세션
```

**추천 위치**: 트러블슈팅 가이드 (Level 3)

### 4. 새로운 워크플로우 (Medium Priority)

```
탐지 기준:
- 순차적 작업 패턴
- 여러 도구 조합 사용
- 자동화 가능한 프로세스
```

**추천 위치**: 워크플로우 섹션

### 5. 프로젝트 특성 (Low Priority)

```
탐지 기준:
- 프로젝트 고유 용어
- 도메인 특화 규칙
- 팀 컨벤션
```

**추천 위치**: 프로젝트 개요 또는 컨벤션

---

## 실행 프로세스

### Step 1: 대화 히스토리 분석

```
1. 최근 대화 세션 로드
2. 키워드 패턴 매칭
3. 중요도 점수 계산
```

### Step 2: 추천 항목 생성

```
각 항목에 대해:
- 카테고리 분류
- 중요도 점수 (1-10)
- 추천 섹션
- 구체적 텍스트 제안
```

### Step 3: 추천 리포트 출력

```markdown
## Memory Update 추천

### High Priority (8+점)

1. **Quick Command 추가**
   - 내용: `uv run pytest tests/ -v --tb=short`
   - 이유: 5회 반복 사용됨
   - 섹션: Quick Commands

2. **아키텍처 결정 기록**
   - 내용: "FastAPI + SQLAlchemy 선택"
   - 이유: 기술 스택 결정 논의
   - 섹션: ADR 또는 주의사항

### Medium Priority (5-7점)

3. **워크플로우 추가**
   - 내용: "테스트 → 린트 → 커밋" 순서
   - 이유: 반복 패턴 감지
   - 섹션: 워크플로우

### Low Priority (1-4점)

4. **용어 정의**
   - 내용: "transit-analysis: 대중교통 분석 프로젝트"
   - 섹션: 프로젝트 개요
```

### Step 4: 사용자 확인

```
적용할 항목을 선택하세요:
[ ] 1. Quick Command 추가
[ ] 2. 아키텍처 결정 기록
[ ] 3. 워크플로우 추가
[ ] 4. 용어 정의
```

### Step 5: 선택적 적용

`--apply` 옵션 사용 시:
- 선택된 항목만 CLAUDE.md에 추가
- 변경 전후 diff 표시
- 롤백 가능하도록 백업

---

## 중요도 점수 기준

| 점수 | 기준 |
|------|------|
| 9-10 | 3회 이상 반복 + 핵심 기능 관련 |
| 7-8 | 아키텍처 결정 또는 중요 버그 해결 |
| 5-6 | 새로운 워크플로우 또는 자주 사용하는 패턴 |
| 3-4 | 프로젝트 특성 또는 도메인 용어 |
| 1-2 | 일회성 정보 또는 임시 설정 |

---

## 출력 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Memory Update 추천 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

분석 범위: 최근 10개 대화 턴
발견된 추천 항목: 3개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## [HIGH] Quick Command 추가 (점수: 9/10)

현재 대화에서 다음 명령어가 5회 반복 사용되었습니다:

\`\`\`bash
uv run pytest tests/ -v --tb=short
\`\`\`

**추천**: Quick Commands 섹션에 추가

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## [MEDIUM] 워크플로우 패턴 (점수: 6/10)

반복된 작업 순서가 감지되었습니다:
1. 코드 수정
2. ruff check --fix
3. pytest 실행
4. git commit

**추천**: 워크플로우 섹션에 "개발 사이클" 추가

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

적용하시겠습니까? /recommend-memory --apply
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/cleanup-memory/SKILL.md] | CLAUDE.md 정리 및 최적화 |
| [@skills/manage-claude-md/SKILL.md] | CLAUDE.md 직접 수정 |
| [@skills/importance-scorer/SKILL.md] | 중요도 평가 기준 |
| [@skills/done/SKILL.md] | 작업 완료 시 자동 호출 |

---

## 자동 트리거

`message-counter.sh` hook에 의해 10번 대화마다 실행 권장 메시지가 표시됩니다.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [Memory Update] 10번째 대화입니다.
  /recommend-memory 실행을 권장합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.1.0 | user-invocable: false로 변경 (memory-workflow 내부 호출) |
| 2026-01-21 | 1.0.0 | 초기 생성 - 대화 분석 기반 CLAUDE.md 업데이트 추천 |
