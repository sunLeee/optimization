# Plan: Python Quality Enforcement & Team Onboarding

- **작성일**: 2026-03-19
- **Iteration**: 2 (Architect + Critic 수정 반영)
- **상태**: Draft — 사용자 승인 대기
- **관련 ADR**: ADR-004~010, ADR-014, ADR-022, ADR-039~040

---

## RALPLAN-DR Summary

### Principles (4개)

1. **Fail Fast at Commit** — 품질 오류는 PR/CI가 아닌 pre-commit에서 차단한다.
2. **Config as Truth** — 도구 설정(pyproject.toml, .pre-commit-config.yaml)이 규칙의 단일 진원지다. 문서는 설정을 설명하되 대체하지 않는다.
3. **YAGNI on Hook Complexity** — 환경변수 기반 profile 분기는 실제 수요가 확인될 때 추가한다. 현재는 onboarding.md 한 줄 안내로 충분하다.
4. **Self-Enforcing Rules** — Claude 자신이 Stop hook quality gate로 규칙 준수 여부를 측정한다. 사람이 수동 확인하지 않는다.

### Decision Drivers (Top 3)

1. **Stop hook 버그가 quality gate를 무력화** — line 77의 빈 변수 버그로 현재 점수 계산이 전혀 동작하지 않음. 최우선 수정 대상.
2. **pre-commit 설정 파일 부재** — ADR-014가 결정을 선언했으나 실제 `.pre-commit-config.yaml`과 `pyproject.toml`이 없어 연동이 미완 상태.
3. **ADR-022/CLD-05 모순** — ADR-022는 CLAUDE.md 한도를 200줄로, CLD-05는 250줄로 규정해 단일 진원지 원칙 위반. 실행 전 해소 필수.

### Viable Options

#### Option A: 설정 파일 우선 (Bottom-Up)
pyproject.toml + .pre-commit-config.yaml을 먼저 완성한 뒤 문서/hook을 정렬한다.

| Pros | Cons |
|------|------|
| 실제 동작하는 결과물이 먼저 나옴 | 문서 없이 신규 팀원이 배경 이해 어려움 |
| ADR-014 이행을 즉시 검증 가능 | ADR-022/CLD-05 모순이 미해결인 채 CLAUDE.md 수정 진행 위험 |

#### Option B: 문서/Hook 우선 (Top-Down)
onboarding.md와 Stop hook 버그 수정을 먼저, 설정 파일은 후행.

| Pros | Cons |
|------|------|
| 팀원이 맥락을 먼저 이해하고 설정 적용 | 실제 pre-commit 오류는 계속 발생 |
| Stop hook 수정은 독립적으로 빠름 | 설정 완성 전까지 반쪽짜리 개선 |

#### Option C: 병렬 + 모순 선해소 (Recommended)
ADR-022/CLD-05 모순 해소를 Phase 1C의 선행 단계로 지정. 이후 Stop hook 수정(독립) + 설정 파일 생성(독립) + onboarding.md(독립)를 병렬 실행. ECC_HOOK_PROFILE 분기는 YAGNI 판단으로 제거, onboarding.md 한 줄 안내로 대체.

| Pros | Cons |
|------|------|
| 의존성이 없는 작업을 동시에 처리해 최단 시간 완료 | 3개 병렬 PR이면 리뷰 부담 증가 |
| ADR 모순을 실행 전에 해소해 일관성 유지 | 설정-문서 간 불일치 가능성 → 교차 검증 필요 |
| ECC_HOOK_PROFILE YAGNI 적용으로 파일 수 11→9개 감소 | — |

**선택: Option C** — ADR-022/CLD-05 모순은 CLAUDE.md 수정 전에 반드시 해소해야 하며, 이는 Phase 1C의 선행 조건이다. ECC_HOOK_PROFILE 복잡도는 현재 수요가 없어 YAGNI 원칙으로 제거한다.

---

## Context

**현재 상태 요약**

| 항목 | 상태 | 비고 |
|------|------|------|
| ADR-004~010, ADR-014 | 선언 완료 | 미이행 상태 |
| ADR-022 vs CLD-05 | **모순** | ADR-022=200줄, CLD-05=250줄 — 실행 전 해소 필수 |
| `.pre-commit-config.yaml` | 없음 | 핵심 미완 |
| `pyproject.toml` (ruff/bandit 설정) | 없음 | 핵심 미완 |
| `onboarding.md` | 없음 | AC-3 미달 |
| Stop hook quality gate | 버그 있음 | line 77 빈 변수 |
| ECC_HOOK_PROFILE | YAGNI로 제거 | onboarding.md 한 줄 안내로 대체 |
| get-api-docs skill | 없음 | AC-5 미달 |
| check-criteria.sh | 동작함 | 단, Stop hook 연동 깨짐 |

**Stop hook 버그 상세** (`.claude/settings.json` line 77):
```bash
# 현재 (broken)
if [ -f "" ]; then bash "" --score ...;  SCORE=; if [ -n "" ] ...

# 의도한 동작
SCRIPT=".claude/check-criteria.sh"
if [ -f "$SCRIPT" ]; then SCORE=$(bash "$SCRIPT" --score 2>/dev/null); ...
```
변수 확장이 전혀 이루어지지 않아 quality gate가 항상 무시된다.

**ADR-022/CLD-05 모순 상세**:
- ADR-022: CLAUDE.md 최대 200줄
- CLD-05 (check-criteria.sh): CLAUDE.md 최대 250줄
- 현재 CLAUDE.md: 246줄 (ADR-022 위반, CLD-05 준수)
- 해결 방향: ADR-022를 250줄로 업데이트하여 CLD-05와 일치시킴

---

## Work Objectives

1. Stop hook quality gate가 실제로 작동하여 점수를 계산하고 90% 미달 시 exit 2를 반환한다.
2. `pyproject.toml` + `.pre-commit-config.yaml`이 존재하고 `pre-commit run --all-files`가 통과한다.
3. 신규 팀원이 `.claude/docs/onboarding.md`를 읽고 30분 내에 첫 commit을 할 수 있다.
4. `check-criteria.sh`에 Python 품질 항목(ruff violations, bandit)이 추가되어 정량 측정된다.
5. `get-api-docs` skill이 추가되어 context-hub 방식의 API 문서 조회가 가능하다.
6. ADR-022와 CLD-05가 동일한 250줄 한도로 일치한다.

---

## Guardrails

**Must Have**
- `.pre-commit-config.yaml`: ruff + bandit 포함 (mypy hook은 Phase 2A에서 추가)
- `pyproject.toml`: `[tool.ruff] line-length = 79`, `[tool.mypy] strict = true` 설정 포함 (pre-commit hook 연동은 Phase 2A)
- Stop hook: `$SCRIPT` 변수 올바르게 확장, `--score` 플래그로 숫자만 출력하는 모드 지원
- `onboarding.md`: clone → pre-commit install → 첫 commit 3단계, `ECC_HOOK_PROFILE=minimal claude` 첫 주 권장 안내 포함
- ADR-042 (get-api-docs skill) 작성
- ADR-022를 250줄로 업데이트 (CLD-05와 일치)

**Must NOT Have**
- `--no-verify` 사용 허용 (ADR-014 위반)
- 기존 38개 ADR 내용 변경 (ADR-022 제외 — 명시적 수정 대상)
- `CLAUDE.md` 250줄 초과 (ADR-022 수정 후 기준)
- check-criteria.sh 기존 30개 항목 제거 또는 변경
- ECC_HOOK_PROFILE 환경변수 분기 구현 (YAGNI — onboarding.md 안내로 충분)

---

## Task Flow (Phase별 실행 순서)

```
Phase 1 (병렬, 독립)
  ├── 1A: Stop hook 버그 수정 (settings.json + check-criteria.sh --score)
  ├── 1B: [Step 0: ruff pre-flight] pyproject.toml(ruff+bandit) + .pre-commit-config.yaml(ruff+bandit)
  └── 1C: [Step 0: ADR-022 → 250줄로 수정] onboarding.md + CLAUDE.md 링크

Phase 2A (1B 완료 후)
  └── 2A: .claude/tests/ 생성 + type_error_fixture.py + mypy hook 추가

Phase 2B (독립)
  └── 2B: check-criteria.sh PYQ 5개 항목 추가

Phase 3A (2A 완료 후)
  └── 3A: get-api-docs skill + COD-01 임계값 127→128 반영 + skill-catalog.md

Phase 3B (독립)
  └── 3B: ADR-042 작성

Phase 3C (전체 완료 후)
  └── 3C: 최종 검증
```

---

## Detailed TODOs with Acceptance Criteria

### Phase 1A: Stop hook 버그 수정

**파일**: `.claude/settings.json` line 77

**변경 내용**:
```bash
# 수정 전 (broken)
"command": "SCRIPT=\".claude/check-criteria.sh\"; if [ -f \"\" ]; then bash \"\" --score ..."

# 수정 후
"command": "SCRIPT=\".claude/check-criteria.sh\"; if [ -f \"$SCRIPT\" ]; then SCORE=$(bash \"$SCRIPT\" --score 2>/dev/null); if [ -n \"$SCORE\" ] && [ \"$SCORE\" -lt 90 ]; then ..."
```

**check-criteria.sh에 `--score` 플래그 추가**:
현재 `check-criteria.sh`는 `--score` 인자를 받지 않는다. `$1 = --score` 일 때 숫자(`$pct`)만 stdout 출력하는 분기 추가.

**Acceptance Criteria**:
- `bash .claude/check-criteria.sh --score` 실행 시 `0`~`100` 사이 숫자만 출력됨
- `python3 -m json.tool .claude/settings.json` 오류 없음
- Stop hook을 수동으로 트리거했을 때 점수가 출력됨 (COD-09 통과 유지)

---

### Phase 1B: pyproject.toml + .pre-commit-config.yaml 생성

**Step 0 (pre-flight)**: 실행 전 기존 .py 파일 상태 확인
```bash
ruff check .claude/skills/data-fetch/markdown-converter/scripts/pdf_to_md.py
```
위반 사항이 있으면 먼저 수정 후 pyproject.toml 생성 진행.

**파일**: `/Users/hmc123/Documents/claude-config/pyproject.toml` (신규)

```toml
[tool.ruff]
line-length = 79
select = ["E", "F", "I", "B", "UP"]

[tool.mypy]
strict = true
ignore_missing_imports = true

[tool.bandit]
skips = ["B101"]  # assert 허용 (테스트 코드)
```

**파일**: `/Users/hmc123/Documents/claude-config/.pre-commit-config.yaml` (신규)
- Phase 1B 범위: ruff + bandit only
- mypy hook은 Phase 2A에서 추가

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.0
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
```

**Acceptance Criteria**:
- Step 0: `ruff check .claude/skills/data-fetch/markdown-converter/scripts/pdf_to_md.py` 위반 없음 (또는 수정 완료)
- `pre-commit run --all-files` 가 `.claude/` 내 .py 파일에 대해 통과함
- `python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` 오류 없음
- ADR-005(79자), ADR-009(ruff) 설정과 일치함
- mirrors-mypy hook이 .pre-commit-config.yaml에 없음 (Phase 2A에서 추가)

---

### Phase 1C: onboarding.md 작성 + ADR-022 수정

**Step 0 (선행 필수)**: ADR-022 수정 — CLAUDE.md 한도 200줄→250줄
- 파일: `.claude/docs/adr/ADR-022-claude-md-line-limit.md` (Edit)
- 변경: `최대 200줄` → `최대 250줄` (CLD-05와 일치)
- 검증: `grep '250' .claude/docs/adr/ADR-022-claude-md-line-limit.md` — 결과 있음
- 이 단계 완료 전 CLAUDE.md 수정 불가

**파일**: `.claude/docs/onboarding.md` (신규)

**필수 섹션**:
1. **환경 준비** (5분) — uv, tmux, gh, gemini-cli 설치
2. **리포 설정** (10분) — clone → `pre-commit install` → `.claude/setup.sh` 실행
3. **첫 commit** (15분) — Python 파일 수정 → `pre-commit run` 통과 확인 → commit
4. **핵심 워크플로우** — deep-interview → ralplan → ralph 3단계 설명 (1페이지)
5. **자주 하는 실수** — `--no-verify` 금지, `#숫자` 커밋 메시지 주의, 79자 줄 길이

**onboarding.md 필수 포함 문구**:
```
> 첫 주에는 `ECC_HOOK_PROFILE=minimal claude` 실행을 권장한다. Stop hook이 경고만 출력하고 차단하지 않아 품질 규칙에 익숙해지는 데 도움이 된다.
```

**Acceptance Criteria**:
- Step 0: `grep '250' .claude/docs/adr/ADR-022-claude-md-line-limit.md` — 결과 있음
- 파일 존재: `test -f .claude/docs/onboarding.md`
- 섹션 수 5개 이상: `grep -c '^## ' .claude/docs/onboarding.md` >= 5
- pre-commit 명령 포함: `grep -c 'pre-commit install' .claude/docs/onboarding.md` >= 1
- ECC_HOOK_PROFILE=minimal 안내 포함: `grep -c 'ECC_HOOK_PROFILE=minimal' .claude/docs/onboarding.md` >= 1
- CLAUDE.md에 onboarding.md 링크 추가됨
- CLAUDE.md 줄 수: `wc -l CLAUDE.md` <= 250

---

### Phase 2A: mypy hook + type_error_fixture.py (1B 완료 후)

**배경**: mypy hook은 테스트 fixture가 먼저 존재해야 "hook이 실제로 실패를 잡는다"는 것을 검증할 수 있다. 따라서 fixture 생성과 hook 추가를 함께 묶는다.

**Step 1**: `.claude/tests/` 디렉토리 생성

**Step 2**: `.claude/tests/type_error_fixture.py` 생성
- 목적: mypy --strict에서 반드시 실패하는 타입 오류 코드 포함
- 내용 예시:
```python
# type_error_fixture.py — mypy --strict 검증용 (프로덕션 코드 아님)
def add(x, y):  # 타입 힌트 없음 → mypy --strict 실패
    return x + y

result: int = add("hello", "world")  # 반환 타입 불일치
```

**Step 3**: `.pre-commit-config.yaml`에 mypy hook 추가
```yaml
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        args: [--strict]
        files: ^(?!\.claude/tests/type_error_fixture\.py).*\.py$
```
(fixture는 hook 범위에서 제외하여 정상 pre-commit이 방해받지 않도록)

**Acceptance Criteria**:
- `test -d .claude/tests` — exit 0
- `test -f .claude/tests/type_error_fixture.py` — exit 0
- `pre-commit run mypy --files .claude/tests/type_error_fixture.py` — exit non-zero (mypy가 타입 오류 잡음)
- `pre-commit run --all-files` (fixture 제외 경로) — exit 0

---

### Phase 2B: check-criteria.sh Python 품질 항목 추가

**현재**: 30개 항목 (COD/GEM/CLD 각 10개)
**추가**: Python 품질 섹션 (PYQ 5개) — 선택적으로 실행

```bash
echo "=== Python Quality (선택) ==="
chk PYQ-01 "pyproject.toml 존재" "test -f pyproject.toml && echo 0 || echo 1" "=" 0
chk PYQ-02 "pre-commit-config 존재" "test -f .pre-commit-config.yaml && echo 0 || echo 1" "=" 0
chk PYQ-03 "ruff line-length=79" "grep -c 'line-length = 79' pyproject.toml" ">=" 1
chk PYQ-04 "mypy strict" "grep -c 'strict = true' pyproject.toml" ">=" 1
chk PYQ-05 "onboarding.md 존재" "test -f .claude/docs/onboarding.md && echo 0 || echo 1" "=" 0
```

**Acceptance Criteria**:
- `bash .claude/check-criteria.sh` 실행 시 `=== Python Quality ===` 섹션 출력됨
- PYQ 항목은 전체 점수(35개 분모)에 포함됨
- 기존 COD/GEM/CLD 30개 항목 결과 변화 없음

---

### Phase 3A: get-api-docs skill 생성 (2A 완료 후)

**파일**: `.claude/skills/reference/adk/get-api-docs/SKILL.md` (신규)

**목적**: context-hub 방식 — SDK/라이브러리 공식 문서를 직접 조회하여 hallucination 방지.

**핵심 동작**:
1. 인자로 패키지명 수신 (예: `fastapi`, `pydantic`)
2. PyPI JSON API 또는 공식 docs URL 조회
3. 핵심 API 시그니처 + 예제 추출 후 SKILL.md 형식으로 응답

**COD-01 임계값 업데이트**:
- 기존: skill 수 >= 127
- 신규: skill 수 >= 128 (get-api-docs 추가 후)
- check-criteria.sh의 COD-01 항목 임계값을 127→128로 수정

**Acceptance Criteria**:
- `find .claude/skills -name SKILL.md | wc -l` >= 128
- SKILL.md에 `name: get-api-docs`, `triggers:`, `description:` 포함
- skill-catalog.md에 항목 추가됨 (`sync-skill-catalog` 실행)
- check-criteria.sh COD-01 임계값이 128로 수정됨

---

### Phase 3B: ADR-042 작성

**ADR-042**: context-hub 방식 API 문서 조회 (get-api-docs skill)
- 결정: 외부 SDK 사용 전 get-api-docs로 공식 문서 먼저 조회
- 이유: hallucination 방지, 최신 API 시그니처 보장

> 참고: ADR-041 (ECC_HOOK_PROFILE)은 YAGNI 판단으로 제거됨. onboarding.md 한 줄 안내(`ECC_HOOK_PROFILE=minimal claude`)로 대체.

**Acceptance Criteria**:
- `test -f .claude/docs/adr/ADR-042-context-hub-api-docs.md` — exit 0
- ADR에 결정/이유/대안/결과 섹션 포함
- ADR-041 파일이 존재하지 않음

---

### Phase 3C: 최종 검증

**Acceptance Criteria (전체 AC 매핑)**:

| AC | 검증 명령 | 기대값 |
|----|----------|--------|
| AC-1 Stop hook 버그 수정 | `bash .claude/check-criteria.sh --score` | 숫자 출력 |
| AC-2 pre-commit 통과 | `pre-commit run --all-files` (fixture 제외) | exit 0 |
| AC-3 onboarding.md | `test -f .claude/docs/onboarding.md` | exit 0 |
| AC-4 onboarding ECC 안내 | `grep -c 'ECC_HOOK_PROFILE=minimal' .claude/docs/onboarding.md` | >= 1 |
| AC-5 get-api-docs skill | `find .claude/skills -name SKILL.md \| wc -l` | >= 128 |
| AC-6 AW 자동 준수 | `check-criteria.sh` 전체 점수 | >= 90% |
| AC-7 mypy strict config | `grep 'strict = true' pyproject.toml` | 결과 있음 |
| AC-8 quality gate 계산 | Stop hook 실행 후 로그 | 점수 출력됨 |
| AC-9 ADR-022 수정 | `grep '250' .claude/docs/adr/ADR-022-claude-md-line-limit.md` | 결과 있음 |
| AC-10 ADR-042 | `test -f .claude/docs/adr/ADR-042-context-hub-api-docs.md` | exit 0 |
| AC-11 mypy fixture | `pre-commit run mypy --files .claude/tests/type_error_fixture.py` | exit non-zero |

---

## 예상 파일 변경 범위

| 파일 | 변경 유형 | Phase |
|------|----------|-------|
| `.claude/settings.json` | Edit (line 77 버그 수정) | 1A |
| `.claude/check-criteria.sh` | Edit (`--score` 플래그 + PYQ 섹션 + COD-01 128) | 1A, 2B, 3A |
| `pyproject.toml` | Create (신규, ruff+bandit+mypy 설정) | 1B |
| `.pre-commit-config.yaml` | Create (신규, ruff+bandit; mypy는 2A에서 추가) | 1B, 2A |
| `.claude/docs/adr/ADR-022-claude-md-line-limit.md` | Edit (200→250줄) | 1C Step 0 |
| `.claude/docs/onboarding.md` | Create (신규) | 1C |
| `.claude/tests/type_error_fixture.py` | Create (신규) | 2A |
| `.claude/skills/reference/adk/get-api-docs/SKILL.md` | Create (신규) | 3A |
| `.claude/skill-catalog.md` | Edit (get-api-docs 항목 추가) | 3A |
| `CLAUDE.md` | Edit (onboarding.md 링크 추가) | 1C |

> **ADR-041-hook-profile.md**: YAGNI 판단으로 제거. 생성하지 않음.

**총 변경 파일**: 9개 (Create 4 신규 파일 + Edit 5 기존 파일 + .pre-commit-config.yaml은 1B Create 후 2A Edit)

실질적으로:
- 신규 파일 5개: pyproject.toml, .pre-commit-config.yaml, onboarding.md, type_error_fixture.py, get-api-docs/SKILL.md
- 수정 파일 4개: settings.json, check-criteria.sh, ADR-022, skill-catalog.md
- CLAUDE.md (onboarding 링크 추가), .pre-commit-config.yaml (mypy hook 추가) 는 각 Phase에서 Edit

---

## 리스크

### 기술적 리스크

| 리스크 | 가능성 | 영향 | 완화 전략 |
|--------|--------|------|----------|
| ruff pre-flight에서 pdf_to_md.py 위반 발견 시 수정 범위 예상 외 증가 | 중간 | 중간 | Step 0에서 위반 수 먼저 파악, 자동 수정 가능 여부 확인 후 진행 |
| settings.json 수정 후 JSON 파싱 오류 | 중간 | 높음 | 수정 후 즉시 `python3 -m json.tool` 검증 |
| CLAUDE.md 250줄 초과 (onboarding 링크 추가 시) | 낮음 | 중간 | 추가 전 `wc -l CLAUDE.md` 확인, ADR-022 수정(Step 0) 완료 후 진행 |
| check-criteria.sh `--score` 플래그 추가 후 기존 30개 항목 합산 오류 | 낮음 | 높음 | `--score` 분기는 early return, 기존 로직 무변경 |
| mypy fixture가 pre-commit --all-files에서 정상 경로까지 오염 | 중간 | 중간 | files 패턴으로 fixture 경로 제외 명시 |

### 완화 전략 요약
- 모든 settings.json 수정 후 즉시 `python3 -m json.tool` 검증
- 각 Phase는 독립적으로 commit 및 검증 후 다음 Phase 진행
- Phase 1C Step 0(ADR-022 수정) 완료 확인 후 CLAUDE.md 수정 진행

---

## ADR (Decision Record)

**결정**: Option C (병렬 + 모순 선해소) 채택

**Drivers**:
1. Stop hook 버그 독립성 — 다른 작업과 병렬 가능
2. pre-commit 설정 파일 부재의 긴급성
3. ADR-022/CLD-05 모순은 CLAUDE.md 수정 전 반드시 해소 필요
4. ECC_HOOK_PROFILE YAGNI — 실제 수요 없이 복잡도 추가 금지

**대안 검토**:
- Option A (설정 우선): 문서 없어 맥락 이해 어려움. ADR 모순 미해소 위험.
- Option B (문서 우선): 실제 pre-commit 오류 계속 발생.
- ADR-041 (Hook Profile ADR): YAGNI 위반 — onboarding.md 한 줄로 동일 효과 달성.

**선택 이유**: Phase 1의 세 작업(1A/1B/1C)이 서로 의존성이 없어 병렬이 최단 경로. Phase 1C는 ADR-022 수정을 Step 0으로 선행하여 일관성 유지. mypy hook은 fixture 검증이 선행되어야 해서 Phase 2A로 분리.

**결과**: 9개 파일, 3개 주요 Phase + 세부 단계. 각 Phase 독립 검증 가능.

**Follow-ups**:
- ECC_HOOK_PROFILE 실제 수요 발생 시 별도 ADR로 재검토
- mypy strict 적용 후 기존 .py 파일 오류 발생 시 `ignore_missing_imports` 추가로 단계적 도입
- ADR-042 미작성 상태로 3A 실행 금지 (설계 문서 먼저 원칙 AW-006) — 단, 3B가 독립 Phase이므로 병렬 실행 가능
