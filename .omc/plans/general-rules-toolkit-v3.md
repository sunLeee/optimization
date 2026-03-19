# Plan: 팀 General Rules 완전 정의 시스템 구현 (v3)

- Plan ID: general-rules-toolkit-v3
- Spec: `.omc/specs/deep-interview-general-rules.md`
- Generated: 2026-03-18
- Supersedes: `general-rules-toolkit-v2.md`
- Status: READY FOR EXECUTION

---

## v2 → v3 변경 사항 요약

| 항목 | v2 | v3 변경 내용 |
|------|-----|------------|
| 블로커 1 | `.pre-commit-config.yaml`에 `rev:` 없음 | 각 repo에 안정 버전 명시 + autoupdate 주석 |
| 블로커 2 | 종료조건 17 — `grep "88" lint-fix/SKILL.md` 항상 실패 | grep 패턴을 실제 위반만 탐지하도록 좁힘 |
| 블로커 3 | Step 6에서 `[tool.ruff]` "추가" 지시 → TOML 중복 오류 | pyproject.toml line 53 기존 섹션 "수정"으로 변경 |
| 추가 항목 | 없음 | 브랜치 협업 규칙 (convention-pr + CLAUDE.md Git Workflow) |

v3에서 변경되지 않은 모든 내용(Context, Work Objectives, Guardrails, Option A/B, Task Flow,
Step 1~5, Step 7~8, 종료조건 1~16, ADR, Success Criteria)은 v2 동일이며 아래에서 생략한다.

---

## 변경된 Step 상세

### Step 6 (수정): pre-commit 설정

**역할**: v2 동일 (실제 강제 도구).

**대상 파일**: `.pre-commit-config.yaml` (신규)

```yaml
# 설치 후 `pre-commit autoupdate` 를 실행하여 최신 버전으로 업데이트할 것
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--select, E,W, --max-line-length, "79"]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
```

**v2와의 차이**:
- 각 repo 블록에 `rev:` 필드 추가 (없으면 `pre-commit install` 자체가 실패함)
  - ruff-pre-commit: `v0.4.4`
  - mirrors-mypy: `v1.10.0`
  - bandit: `1.7.8`
- 파일 상단에 `pre-commit autoupdate` 권장 주석 추가

**`pyproject.toml` 수정 (v2의 "추가"에서 "수정"으로 변경)**:

- `pyproject.toml` line 53의 기존 `[tool.ruff]` 섹션에서 `line-length = 88`을
  `line-length = 79`로 **수정**한다.
- TOML에 `[tool.ruff]` 섹션을 새로 추가하지 않는다 (중복 section은 parse error).

수락 기준:
- `grep "rev:" .pre-commit-config.yaml | wc -l` 출력 3 이상 (3개 repo 모두 rev 존재)
- `grep "autoupdate" .pre-commit-config.yaml` 존재
- `grep -E "line.length.{0,5}79|max.line.length.{0,5}79" .pre-commit-config.yaml pyproject.toml` 존재
- `grep "mypy" .pre-commit-config.yaml` 존재 및 `grep "strict" .pre-commit-config.yaml` 존재
- `grep "bandit" .pre-commit-config.yaml` 존재
- `python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read()); print('OK')"` 출력 OK
  (TOML parse error 없음 확인)

---

### Step 3-2 (수정): `lint-fix/SKILL.md` 79자 수정

**배경 (v2 동일)**: 기존 `lint-fix/SKILL.md`가 88자 기준을 사용하므로 79자로 수정.

**v2와의 차이 — 수락 기준 변경**:

v2의 종료조건 17은 다음이었다:
```bash
! grep "88" .claude/skills/lint-fix/SKILL.md && grep "79" .claude/skills/lint-fix/SKILL.md
```

이 조건은 `lint-fix/SKILL.md` lines 117, 190에 예시 출력으로 `> 88 characters`가 존재하여
항상 실패한다 (예시 출력은 제거 대상이 아님).

v3에서는 실제 설정값만 탐지하도록 grep 패턴을 좁힌다:

```bash
# v3 수정된 조건
! grep -E "line.length\s*=\s*88|88 characters.*Black" .claude/skills/lint-fix/SKILL.md \
  && grep "79" .claude/skills/lint-fix/SKILL.md
```

**수락 기준 (v3)**:
- `! grep -E "line.length\s*=\s*88|88 characters.*Black" .claude/skills/lint-fix/SKILL.md`
  통과 (설정값 또는 Black 기준 언급 없음)
- `grep "79" .claude/skills/lint-fix/SKILL.md` 존재
- 파일 내 `line-length = 88` 또는 `Black 88자` 형태의 설정 언급은 모두 79로 수정
- 예시 출력(`> 88 characters` 형태)은 수정 대상이 아님 — 그대로 유지

---

### Step 4-8 (확장): `convention-pr` — 브랜치 협업 규칙 추가

**v2와의 차이**: 브랜치 협업 규칙 섹션 신규 추가.

기존 v2 convention-pr Core Principles + 상황 예시에 더하여 아래 섹션을 추가한다:

```
## 브랜치 협업 규칙

  하나의 branch = 하나의 작업 범위
    - 하나의 branch에서 여러 설계 결정이나 기능을 동시에 수정하지 않는다.

  타인의 브랜치가 수정 중인 파일은 건드리지 않는다
    - 충돌 위험이 있는 파일은 팀원에게 먼저 확인 후 작업한다.
    - 현재 작업 중인 브랜치 목록과 대상 파일은 PR description에 명시한다.

  branch 시작 전 작업 범위를 PR description에 명시
    - 작업 범위 예시: "이 PR은 general rules 파일(CLAUDE.md, docs/design/ref/)만 수정"
    - 범위 외 파일을 수정해야 할 경우 별도 PR을 생성한다.

  현재 브랜치 예시 (참고):
    - shucle-ai-agent-general-rules: general rules 파일만 수정 대상
```

**루트 `CLAUDE.md` Git Workflow 섹션 보완**:

루트 CLAUDE.md의 `## Git Workflow` 섹션에 아래 항목을 추가한다 (기존 내용 유지, 항목 추가):

```
- 하나의 branch = 하나의 작업 범위 (상세: convention-pr 스킬 참조)
- 다른 사람의 branch가 수정 중인 파일은 건드리지 않음
- branch 시작 전 PR description에 작업 범위 명시
```

**수락 기준 (추가)**:
- `grep "하나의 branch" .claude/skills/convention-pr/SKILL.md` 존재
- `grep "PR description" .claude/skills/convention-pr/SKILL.md` 존재
- `grep "하나의 branch\|작업 범위" CLAUDE.md` 존재

---

## 정량적 종료조건 17개 (v3 — 조건 17 수정)

v2에서 변경 없는 조건 1~16은 아래에 그대로 포함한다.

```bash
# 1. 루트 CLAUDE.md 200줄 이하
wc -l CLAUDE.md | awk '{print ($1 <= 200)}'
# 기대: 1

# 2. AW-001~010 루트 요약 + team-operations.md 상세에 모두 존재
grep -rh "AW-0" CLAUDE.md docs/design/ref/team-operations.md | grep -o "AW-0[0-9][0-9]" | sort -u | wc -l
# 기대: 10

# 3. LLM 행동지침 4개 존재
grep -c "Think Before Coding\|Simplicity First\|Surgical Changes\|Goal-Driven Execution" CLAUDE.md
# 기대: 4

# 4. convention-python skill 존재 + 79자 규칙 포함
grep "79자" .claude/skills/convention-python/SKILL.md
# 기대: 매칭 1줄 이상

# 5. convention-python에 Logics 섹션 + iterrows 금지 포함
grep "Logics" .claude/skills/convention-python/SKILL.md && grep "iterrows" .claude/skills/convention-python/SKILL.md
# 기대: 오류 없음

# 6. 9개 skills 모두 생성
ls .claude/skills/ | grep -E "^convention-|^check-design-doc$" | wc -l
# 기대: 9 이상

# 7. 모든 skill에 상황 예시 2개 이상
for d in .claude/skills/convention-*/; do count=$(grep -c "상황 [12]" "$d/SKILL.md" 2>/dev/null || echo 0); [ "$count" -ge 2 ] || echo "FAIL: $d ($count)"; done
# 기대: 출력 없음 (모두 통과)

# 8. team-operations.md 200줄 이하 + AW 10개 + kebab-case + 정보성 명시
wc -l docs/design/ref/team-operations.md | awk '{print ($1 <= 200)}' && grep "kebab-case" docs/design/ref/team-operations.md && grep "정보성" docs/design/ref/team-operations.md
# 기대: 1 출력 + 오류 없음

# 9. agents/CLAUDE.md에 root_agent 및 app: prefix 존재
grep "root_agent" agents/CLAUDE.md && grep "app:" agents/CLAUDE.md
# 기대: 오류 없음

# 10. nested CLAUDE.md 3개 모두 200줄 이하 (v2: .claude/CLAUDE.md 없음)
for f in agents/CLAUDE.md libs/CLAUDE.md apps/CLAUDE.md; do wc -l "$f" | awk -v f="$f" '{if($1>200) print "FAIL: "f" ("$1" lines)"}'; done
# 기대: 출력 없음

# 11. pre-commit ruff 79자 설정 + rev: 3개 존재
grep -E "line.length.{0,5}79|max.line.length.{0,5}79" .pre-commit-config.yaml pyproject.toml \
  && grep "rev:" .pre-commit-config.yaml | wc -l | awk '{print ($1 >= 3)}'
# 기대: 매칭 1줄 이상 + 1

# 12. pre-commit mypy strict + bandit 존재
grep "strict" .pre-commit-config.yaml && grep "bandit" .pre-commit-config.yaml
# 기대: 오류 없음

# 13. Stop hook 설정 존재 + echo만 (실제 ruff 없음)
grep "Stop" .claude/settings.json && ! grep -E '"ruff|mypy|bandit"' .claude/settings.json
# 기대: 오류 없음

# 14. output-styles 파일 존재 및 비어있지 않음
test -s .claude/output-styles/data-driven-minds.md && echo "OK"
# 기대: OK

# 15. convention-adr에 되돌리기 어려운/쉬운 결정 기준 존재
grep "되돌리기 어려운" .claude/skills/convention-adr/SKILL.md && grep "되돌리기 쉬운" .claude/skills/convention-adr/SKILL.md
# 기대: 오류 없음

# 16. python-patterns deprecated 처리 완료
grep "deprecated: true" .claude/skills/python-patterns/SKILL.md && grep "replaced_by: convention-python" .claude/skills/python-patterns/SKILL.md
# 기대: 오류 없음

# 17. [v3 수정] lint-fix 79자 수정 완료 — 설정값/Black 기준 88 없음, 예시 출력은 허용
! grep -E "line.length\s*=\s*88|88 characters.*Black" .claude/skills/lint-fix/SKILL.md \
  && grep "79" .claude/skills/lint-fix/SKILL.md
# 기대: 오류 없음

# 18. [v3 신규] pre-commit autoupdate 주석 존재 + pyproject.toml TOML parse 정상
grep "autoupdate" .pre-commit-config.yaml \
  && python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read()); print('OK')"
# 기대: 매칭 1줄 이상 + OK

# 19. [v3 신규] convention-pr에 브랜치 협업 규칙 존재
grep "하나의 branch" .claude/skills/convention-pr/SKILL.md \
  && grep "PR description" .claude/skills/convention-pr/SKILL.md
# 기대: 오류 없음

# 20. [v3 신규] 루트 CLAUDE.md Git Workflow에 브랜치 협업 규칙 존재
grep "하나의 branch\|작업 범위" CLAUDE.md
# 기대: 매칭 1줄 이상
```

---

## v3 Follow-ups (v2 Follow-ups에 추가)

v2 Follow-ups (team-operations.md 분리 기준 ADR, python-patterns deprecated 안내) 유지.

**추가 Follow-up**:
- 브랜치 협업 규칙이 실제로 지켜지는지 확인하는 방법 (예: PR 리뷰 체크리스트에 추가 여부) 논의 필요

---

## v3 Success Criteria (v2 Success Criteria에 추가)

v2 Success Criteria 전부 유지. 아래 항목 추가:

- `.pre-commit-config.yaml`의 모든 repo 블록에 `rev:` 필드 존재
- `pyproject.toml`이 TOML parse error 없이 로드됨 (중복 `[tool.ruff]` 섹션 없음)
- 종료조건 17이 예시 출력에 의한 false positive 없이 통과
- `convention-pr/SKILL.md`에 브랜치 협업 규칙 (하나의 branch = 하나의 작업 범위) 존재
- 루트 `CLAUDE.md` Git Workflow 섹션에 브랜치 협업 규칙 반영
- 종료조건 총 20개 전부 통과
