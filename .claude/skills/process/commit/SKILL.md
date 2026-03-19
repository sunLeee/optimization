---
name: convention-commit
triggers:
  - "convention commit"
description: Git commit 메시지 작성 전 Conventional Commits 형식 확인이 필요할 때. 브랜치 전략, commit 타입, 스코프 선택이 불명확할 때. "/convention-commit quick"으로 빠른 참조.
argument-hint: "[섹션] - quick, format, types, scope, branch, examples, generate, validate, all"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Bash
model: claude-sonnet-4-6[1m]
context: Git commit 컨벤션 참조 스킬. Conventional Commits 형식과 팀 브랜치 전략을 제공한다. 검증은 check-commit-message 스킬이 담당한다.
agent: Git 워크플로우 전문가. 일관된 커밋 히스토리와 브랜치 전략을 유지하여 팀 협업 효율을 높인다.
hooks:
  pre_execution: []
  post_execution: []
category: 프로세스
skill-type: Atomic
references: []
referenced-by:
  - "@skills/quality/check/check-commit-message/SKILL.md"
---

# convention-commit

Git commit 및 브랜치 컨벤션.

## 형식

```
type(scope): subject  ← 50자 이내
```

## 주요 타입

| 타입 | 용도 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `refactor` | 리팩토링 (기능 변화 없음) |
| `docs` | 문서 수정 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 변경 |

## 스코프 예시

```
feat(demand-agent): add zone aggregation tool
fix(preprocessing): resolve H3 null cell handling
docs(claude): update team-operations AW rules
```

## 브랜치 전략

```
{type}/issue-{number}-{subject}    ← kebab-case
feat/issue-74-ai-pr-workflow
fix/issue-12-zone-id-validation
```

## 금지

- Co-Authored-By 푸터 사용 금지
- `main`/`master` 직접 commit 금지
- 50자 초과 제목

## Gotchas (실패 포인트)

- **스코프 없음**: `feat: add something` → `feat(demand-agent): add zone tool`로 스코프 필수
- **너무 큰 커밋**: PR = 설계 결정 하나 (@AW-006). commit도 마찬가지.
- **제목에 마침표**: `feat: add tool.` → 마침표 제거
- **영어 소문자**: `feat(ADK): Add Tool` → `feat(adk): add tool`로 소문자 시작

## 빠른 참조

```bash
# 마지막 commit 메시지 검증
git log --oneline -1

# Conventional Commits 형식 검증
echo "feat(scope): subject" | grep -E "^(feat|fix|docs|refactor|test|chore|style|perf|ci|build|revert)(\(.+\))?: .{1,50}$"
```

## 관련 규칙

- @AW-006 (설계문서 먼저, 코드 PR 전 설계 PR)
- Git Workflow: CLAUDE.md § Git Workflow
- [convention-pr](../pr/SKILL.md) — PR 범위 규칙
