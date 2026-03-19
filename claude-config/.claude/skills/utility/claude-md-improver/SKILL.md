---
name: claude-md-improver
description: CLAUDE.md를 코드베이스 현재 상태와 비교하여 감사하고 업데이트를 제안한다. Anthropic 공식 claude-md-management 플러그인 기반.
user-invocable: true
triggers:
  - "claude.md 감사"
  - "audit claude.md"
  - "claude.md 업데이트"
  - "claude.md 최신화"
  - "revise claude.md"
---

# claude-md-improver

CLAUDE.md 파일을 코드베이스 현재 상태와 비교하여 품질을 감사하고 업데이트를 제안한다.

> 출처: Anthropic 공식 claude-md-management 플러그인 (Isabella He)
> @docs/design/ref/team-operations.md 와 연계하여 AW 규칙 반영 여부도 검증한다.

## 두 가지 도구

| 도구 | 목적 | 트리거 |
|------|------|--------|
| `claude-md-improver` (이 skill) | CLAUDE.md를 코드베이스와 비교 감사 | 주기적 유지보수 |
| `/revise-claude-md` (command) | 세션 학습을 CLAUDE.md에 반영 | 세션 종료 시 |

## VIOLATION 1: 코드베이스와 괴리된 CLAUDE.md

```python
# VIOLATION: CLAUDE.md의 빌드 명령어가 실제와 다름
# CLAUDE.md 내용: "python setup.py install"
# 실제 코드: pyproject.toml + uv workspace

# 결과: 에이전트가 잘못된 명령어 실행
# → FileNotFoundError: setup.py not found
```

```markdown
<!-- CORRECT: 실제 코드베이스 반영 -->
## 빌드, 실행 및 테스트
\`\`\`bash
uv run pytest -m unit           # Unit 테스트
uv sync                          # 의존성 동기화
\`\`\`
```

**상황 1**: 새 패키지 추가 후 CLAUDE.md 업데이트 누락 → 에이전트가 구 구조로 코드 생성
**상황 2**: 세션에서 발견한 새 패턴(ToolContext 사용법)이 CLAUDE.md에 없음 → `/revise-claude-md` 실행

## VIOLATION 2: 200줄 제한 초과

```bash
# VIOLATION: CLAUDE.md가 250줄로 비대해짐
wc -l CLAUDE.md
# 250 CLAUDE.md  ← 200줄 제한 초과

# CORRECT: 도메인별 분리
# 초과 내용 → docs/design/ref/team-operations.md 등으로 분리
# CLAUDE.md에는 링크만 남김
```

**상황 1**: AW 규칙 상세가 CLAUDE.md에 직접 작성됨 → `docs/design/ref/team-operations.md`로 분리
**상황 2**: skill 목록이 CLAUDE.md에 전부 나열됨 → `.claude/skill-catalog.md`로 분리 후 링크

## 실행 방법

```bash
# 1. CLAUDE.md 품질 감사
"audit my CLAUDE.md files"
"check if my CLAUDE.md is up to date"

# 2. 세션 학습 반영
/revise-claude-md

# 3. 줄 수 확인
wc -l CLAUDE.md docs/claude.md agents/CLAUDE.md
```

## 감사 체크리스트

- [ ] 빌드/실행 명령어가 현재 코드와 일치하는가?
- [ ] 저장소 구조가 현재 디렉토리와 일치하는가?
- [ ] AW-001~045 규칙이 모두 반영되어 있는가?
- [ ] 각 CLAUDE.md가 200줄 이하인가?
- [ ] 하위 CLAUDE.md(agents/, libs/, apps/)가 루트와 충돌하지 않는가?
- [ ] 세션에서 발견한 새 패턴이 반영되었는가?

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| 설계문서 관리 | docs/claude.md | CLAUDE.md 200줄 이하, 초과 시 분리 |
| AW-006 | @docs/design/ref/team-operations.md § AW-006 | 설계문서 먼저 — 코드 PR 전 설계 PR |

## 참조

- @docs/design/ref/team-operations.md § AW-006
- @docs/claude.md § 설계문서 관리 규칙
- @.claude/skill-catalog.md
- 출처: Anthropic claude-md-management plugin (Isabella He)
