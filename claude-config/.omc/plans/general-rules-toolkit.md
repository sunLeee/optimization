# Plan: 팀 General Rules 완전 정의 시스템 구현

- Plan ID: general-rules-toolkit
- Spec: `.omc/specs/deep-interview-general-rules.md`
- Generated: 2026-03-18
- Status: READY FOR REVIEW

---

## Context

`shucle-ai-agent-general-rules` repo를 git clone하면 팀원이 다음날부터 Claude Code로 일할
수 있는 완전한 툴킷을 만든다. 동시에 이 내용을 PR로 제출하여 팀 전체가 Claude Code
개발 워크플로우를 논의하는 출발점으로 삼는다.

**현재 상태 (이미 존재하는 것)**

| 경로 | 줄 수 | 상태 |
|------|-------|------|
| `CLAUDE.md` | 177줄 | AW-001~005 일부만 있음, AW-006~010 없음 |
| `.claude/skills/python-patterns/` | - | 영문, 팀 규칙 미반영 |
| `.claude/skills/python-testing/` | - | 존재 |
| `.claude/skills/code-simplifier/` | - | 존재 |
| `.claude/skills/lint-fix/` | - | 존재 |
| `.claude/agents/python-reviewer.md` | - | 존재 |
| `docs/design/ref/team-operations.md` | 91줄 | AW-001~005 일부 |
| `docs/ref/bestpractice/claude-code-rule-convention.md` | 281줄 | 28개 best practice |
| `docs/references/github-issues/` | - | README + issue-74 존재 |

**새로 만들어야 할 것**: Skills 9개, nested CLAUDE.md 4개, pre-commit 설정, Stop hook
설정, output-styles 파일, 루트 CLAUDE.md 확장

---

## Work Objectives

1. 루트 CLAUDE.md를 AW-001~010 완전 체계 + LLM 행동지침 4개로 확장 (200줄 이하 유지)
2. `.claude/skills/`에 convention 계열 skills 9개를 신규 생성
3. `agents/`, `libs/`, `apps/`, `.claude/` 4곳에 nested CLAUDE.md 작성
4. `pre-commit` + Stop hook 이중 안전망 설정
5. `.claude/output-styles/data-driven-minds.md` 생성

---

## Guardrails

**Must Have**

- 모든 CLAUDE.md 파일 200줄 이하
- 모든 skill에 구체적 상황 예시 2개 이상
- AW-001~AW-010 전부 어딘가에 존재 (루트 또는 `.claude/CLAUDE.md`)
- pre-commit: ruff `line-length=79`, mypy `--strict`, bandit 3종 모두
- 기술 용어 영어, 설명 한국어 규칙 준수
- `docs/references/github-issues/` 파일명 규칙 (`issue-{number}-{subject}.md`, kebab-case, 30자 이하) 문서화

**Must NOT Have**

- 200줄 초과 CLAUDE.md
- 상황 예시 없는 규칙
- pip install 직접 사용 언급 (uv 전용만)
- Co-Authored-By 푸터 언급
- pre-commit `--no-verify` 허용 문구

---

## Option A vs Option B

### Option A: 병렬 ultrawork (모든 파일 한꺼번에)

**장점**
- 전체 구현 시간 단축 (병렬 실행)
- 파일 간 의존성을 executor가 전체 컨텍스트에서 처리

**단점**
- 루트 CLAUDE.md 줄 수 제약을 여러 executor가 동시에 편집하면 충돌 위험
- 검증(verifier)이 15개 종료조건을 한 번에 체크해야 해서 누락 위험

### Option B: 우선순위별 순차 구현 (핵심 먼저)

**장점**
- 루트 CLAUDE.md는 단독 편집 후 줄 수 확인 가능
- 기반 파일(루트 CLAUDE.md, `.claude/CLAUDE.md`) 완성 후 나머지 파일이 이를 참조하며 일관성 유지
- 단계별 verifier 검증으로 오류 조기 발견

**단점**
- 총 소요 시간 다소 증가

**권장: Option B** — 루트 CLAUDE.md 줄 수 제약(200줄 이하)이 모든 하위 파일에 영향을 주는
기반 파일이므로 먼저 확정 후 나머지를 병렬 처리하는 혼합 전략을 사용한다.

구체적으로: Phase 1(기반 파일) 순차 → Phase 2(Skills, nested CLAUDE.md) 병렬 → Phase
3(자동화 설정) 순차 → Phase 4(output-styles) 단독.

---

## Task Flow

```
Phase 1: 기반 파일 확정 (순차, 다른 모든 것의 기준)
  └─ Step 1: 루트 CLAUDE.md 확장 (AW-006~010, LLM 행동지침 4개, 200줄 이하)
  └─ Step 2: .claude/CLAUDE.md 신규 생성 (AW-001~010 전체 + 기술 어휘 규칙)

Phase 2: Skills + nested CLAUDE.md (병렬 가능, Phase 1 완료 후)
  ├─ [병렬 A] Skills 9개 생성
  │     convention-python, convention-commit, convention-design,
  │     convention-design-patterns, convention-folder-structure,
  │     convention-logging, convention-adr, convention-pr, check-design-doc
  └─ [병렬 B] Nested CLAUDE.md 3개 생성
        agents/CLAUDE.md, libs/CLAUDE.md, apps/CLAUDE.md

Phase 3: 자동화 설정 (순차, Skills 완료 후 설정 파일이 skill 이름 참조)
  └─ Step 3: .pre-commit-config.yaml 생성
  └─ Step 4: settings.json Stop hook 등록

Phase 4: 부속 파일 (독립, 어느 단계에서든 병렬 실행 가능)
  └─ Step 5: .claude/output-styles/data-driven-minds.md 생성
```

---

## Detailed TODOs

### Step 1: 루트 CLAUDE.md 확장

**대상 파일**: `CLAUDE.md` (현재 177줄, 200줄 이하로 완성)

**추가 내용 (섹션 제목 수준)**

1. `## Team Operations` 섹션에 AW-006~AW-010 추가
   - AW-006: 설계문서 먼저, 코드 나중 (코드 PR 전 설계 PR 통과 필수)
   - AW-007: 모든 구현 `/ralph` 사용, max iteration 100
   - AW-008: ralplan 종료조건 10개 이상 정량적 목표
   - AW-009: 되돌리기 어려운 결정 = ADR 먼저
   - AW-010: Stop hook + pre-commit 이중 안전망
2. `## LLM 행동지침` 섹션 신규 추가 (한국어, 상황 예시 포함)
   - 1. Think Before Coding
   - 2. Simplicity First
   - 3. Surgical Changes
   - 4. Goal-Driven Execution
3. `## 구현 시 필수 스킬` 테이블에 신규 skills 추가
   - convention-design, convention-adr, convention-pr 행 추가

**줄 수 전략**: AW 규칙은 요약 1줄 + 상황 예시 없이 표 형태로 기재 후 `.claude/CLAUDE.md`로
상세 내용 위임. LLM 행동지침은 각 항목 3~4줄로 압축.

**수락 기준**
- `wc -l CLAUDE.md` 출력이 200 이하
- `grep -c "AW-0" CLAUDE.md` 출력이 10 이상 (AW-001~010)
- `grep "LLM 행동지침" CLAUDE.md` 존재

---

### Step 2: `.claude/CLAUDE.md` 신규 생성

**대상 파일**: `.claude/CLAUDE.md` (신규, 200줄 이하)

**섹션 구조**

```
# 팀 운영 상세 규칙

## AW 규칙 전체 (AW-001~AW-010) — 상세 버전
  각 규칙: 내용 + 구체적 상황 예시 2개

## 기술 어휘 언어 규칙
  영어 유지 목록 | 한국어 사용 목록
  kebab-case vs snake_case 사용 기준표

## 명명 규칙 요약표
  Python 파일/모듈 → snake_case
  문서 파일 → kebab-case
  Git 브랜치 → kebab-case
  Skills/plugin → kebab-case

## GitHub Issues md화 규칙
  파일명: issue-{number}-{subject}.md
  저장 경로: docs/references/github-issues/
  생성 방법: gh api 기반
```

**수락 기준**
- `wc -l .claude/CLAUDE.md` 출력이 200 이하
- `grep -c "AW-0" .claude/CLAUDE.md` 출력이 10 이상
- `grep "kebab-case" .claude/CLAUDE.md` 존재
- `grep "snake_case" .claude/CLAUDE.md` 존재
- `grep "issue-{number}" .claude/CLAUDE.md` 존재

---

### Step 3: Skills 9개 생성 (병렬 A)

각 skill 경로: `.claude/skills/{skill-name}/SKILL.md`

**기존 skill 형식 준수**: frontmatter (`name`, `description`) + `## When to Activate` +
`## Core Principles` + 상황 예시 code block

#### 3-1. `convention-python`

```
## Core Principles
  - 타입힌트: 모든 function 파라미터 + 반환값 필수 (mypy strict)
  - 줄 길이: 79자 엄격 적용 (80 아님) — ruff line-length=79
  - Docstring: Google style, 한국어, 73자 이하, Logics 섹션 필수
  - 한국어 블록 주석: 모든 기능 단위에 반드시 작성
  - 네이밍: snake_case(함수/변수), PascalCase(class), UPPER_SNAKE_CASE(상수)
  - Import 순서: 표준 → 서드파티 → 로컬 (isort 기준)

## Data Science Rules (pandas)
  - vectorization 필수: df.iterrows() 금지
  - Query: ANSI SQL로 구현
  - function 구현: 명시적 요청 시에만

## 실제 사고 사례
  - 타입 미선언 + 79자 미준수로 코드 대량 재작업 발생 사례
```

수락 기준: `grep "79자" .claude/skills/convention-python/SKILL.md` 존재,
`grep "Logics" .claude/skills/convention-python/SKILL.md` 존재,
`grep "iterrows" .claude/skills/convention-python/SKILL.md` 존재

#### 3-2. `convention-commit`

```
## Core Principles
  - 포맷: type(scope): subject (50자 이내)
  - 타입: feat, fix, docs, refactor, test, chore
  - scope: 필수 (패키지/모듈명)
  - 브랜치명: {type}/{issue-number}-{brief-description}
  - Co-Authored-By 푸터 금지

## 상황 예시
  - 상황 1: feat(demand-analyst): add zone aggregation metric
  - 상황 2: 브랜치명 feat/74-pr-workflow-rules
```

수락 기준: `grep "Co-Authored-By" .claude/skills/convention-commit/SKILL.md` 존재,
`grep "kebab-case\|{type}/{issue" .claude/skills/convention-commit/SKILL.md` 존재

#### 3-3. `convention-design`

```
## Core Principles
  - SRP: 단일 책임 — class/function이 하나의 이유로만 변경
  - KISS: 단순하게 — 가장 단순한 해법 선택
  - DRY: 중복 금지 — 동일 로직 2회 이상 등장 시 추출
  - YAGNI: 필요한 것만 — 미래 요구사항 대비 코드 금지
  - God Class 탐지: 500줄 초과 class → 분리 검토
  - Long Method 탐지: 50줄 초과 function → 분리 검토

## 상황 예시 (SRP)
  상황 1: DataLoader가 파일 읽기 + 전처리 + 저장을 동시에 → 분리
  상황 2: Agent class가 prompt 관리 + tool 실행 + 결과 포맷팅 → 분리
```

수락 기준: `grep "SRP\|KISS\|DRY\|YAGNI" .claude/skills/convention-design/SKILL.md` 4개 모두 존재

#### 3-4. `convention-design-patterns`

```
## Patterns
  - Factory: 객체 생성 로직 분리 (상황 2개)
  - Strategy: 알고리즘 교체 가능 설계 (상황 2개)
  - Repository: data access layer 분리 (상황 2개)
  - Observer: event 기반 처리 (상황 2개)
```

수락 기준: `grep -c "상황 1\|상황 2" .claude/skills/convention-design-patterns/SKILL.md` 출력
8 이상 (패턴 4개 × 상황 2개)

#### 3-5. `convention-folder-structure`

```
## Structures
  - Python monorepo (uv workspace): 언제 사용 + 상황 2개
  - 단일 패키지: 언제 사용 + 상황 2개
  - Data Science 프로젝트: notebooks, src, data, output + 상황 2개
  - Agent 프로젝트: agents, libs, apps + 상황 2개
```

수락 기준: `grep -c "상황 1\|상황 2" .claude/skills/convention-folder-structure/SKILL.md`
출력 8 이상

#### 3-6. `convention-logging`

```
## Core Principles
  - structlog vs logging 선택 기준
  - TRACE 레벨 사용 조건 (libs/logger 연동)
  - 포맷: JSON (production), 텍스트 (development)
  - 레벨 기준: DEBUG/INFO/WARNING/ERROR/CRITICAL 상황별 정의

## 상황 예시
  상황 1: production 환경에서 request_id를 모든 로그에 포함 → structlog
  상황 2: 개발 환경에서 agent 내부 상태 추적 → TRACE 레벨
```

수락 기준: `grep "structlog\|TRACE\|JSON" .claude/skills/convention-logging/SKILL.md` 3개 존재

#### 3-7. `convention-adr`

```
## When to Write ADR
  - 되돌리기 어려운 결정: 파일 포맷, API 계약, DB 스키마, 좌표계
  - 되돌리기 쉬운 결정: 변수명, 함수명, 주석 → ADR 불필요

## ADR 포맷
  Status / Context / Decision / Consequences /
  Considered Options / Completion Checklist

## 상황 예시
  상황 1: H3 좌표계 도입 결정 → ADR 필수
  상황 2: 변수명 user_id → uid 변경 → ADR 불필요
```

수락 기준: `grep "되돌리기 어려운\|되돌리기 쉬운" .claude/skills/convention-adr/SKILL.md` 존재,
`grep "Completion Checklist" .claude/skills/convention-adr/SKILL.md` 존재

#### 3-8. `convention-pr`

```
## Core Principles
  - Rule of Small: 하나의 PR = 하나의 설계 결정
  - Rule of Design: 코드 PR 전 설계 PR 통과 필수
  - PR description: 1문장 요약 + 설계문서 링크
  - check-design-doc 스킬로 코드-설계 일치 자동 검증

## 상황 예시
  상황 1: 파일 경로 패턴 변경과 column 네이밍 규칙 변경 → 별도 PR
  상황 2: 새 기능 → 설계문서 PR merge 후 코드 PR 생성
```

수락 기준: `grep "Rule of Small\|Rule of Design" .claude/skills/convention-pr/SKILL.md` 존재,
`grep "check-design-doc" .claude/skills/convention-pr/SKILL.md` 존재

#### 3-9. `check-design-doc`

```
## Purpose
  코드 변경과 설계문서(CLAUDE.md, docs/design/) 간 일치 여부를 검증

## Checklist
  - 새 function/class → CLAUDE.md 또는 관련 docs에 패턴 기술 여부 확인
  - 파일 경로 패턴 → config.py 패턴과 일치 여부 확인
  - import 방식 → 절대 import 규칙 준수 여부 확인
  - ADR 필요 결정 → ADR 파일 존재 여부 확인

## 상황 예시
  상황 1: ToolContext 사용 패턴이 CLAUDE.md와 다르면 → 불일치 보고
  상황 2: 새 데이터 파일 경로가 config.py get_*_path() 패턴을 따르지 않으면 → 위반
```

수락 기준: `grep "check-design-doc\|check_design_doc" .claude/skills/check-design-doc/SKILL.md`
존재

---

### Step 4: Nested CLAUDE.md 3개 생성 (병렬 B, Step 2와 동시 가능)

#### 4-1. `agents/CLAUDE.md`

```
# Agents 규칙

## ADK 에이전트 구현 패턴
  - root_agent 반드시 export (ADK module-level access)
  - __init__.py export 형식: from .agent import Agent, root_agent
  - 파일 존재 검증: __init__ 진입 전 FileNotFoundError raise

## Prompt 구조
  - YAML + Jinja2 (PromptLoader)
  - 입력 변수 명시 필수

## Session Context (app: prefix)
  - 모든 파일 경로: self.initial_state["app:{key}"]
  - Tool 함수: tool_context.state.get("app:{key}") 방식만

## Tool 설계 규칙
  - tool function: tool_context: ToolContext 인자만
  - 파일 경로 직접 인자 금지
  - 파일 존재 재검증 금지 (agent __init__에서 1회만)
```

수락 기준: `wc -l agents/CLAUDE.md` 200 이하,
`grep "root_agent" agents/CLAUDE.md` 존재,
`grep "app:" agents/CLAUDE.md` 존재

#### 4-2. `libs/CLAUDE.md`

```
# Libs 규칙

## uv Workspace 패키지 레이아웃
  - src/{package_name}/__init__.py (필수)
  - tests/__init__.py (필수 — pytest 탐색)
  - pyproject.toml에 [tool.uv.sources] 필수

## Import 스타일
  - 절대 import만: from utils.prompt_loader import ...
  - 상대 import 금지: from ..utils 금지
  - sys.path 조작 금지

## 모듈 구조 규칙
  - 기능/도메인 기반 분류 (타입 기반 금지)
  - utils/, helpers/ 이름 금지
  - 200~400줄 일반, 800줄 max
```

수락 기준: `wc -l libs/CLAUDE.md` 200 이하,
`grep "절대 import\|상대 import" libs/CLAUDE.md` 존재

#### 4-3. `apps/CLAUDE.md`

```
# Apps 규칙

## CLI 러너 패턴
  - 파일 경로: config.py의 get_*_path() 함수 통해 획득
  - 러너 진입 전 agent __init__에 경로 전달
  - 러너 자체에서 파일 존재 검증 금지

## config.py 구조
  - 모든 데이터 파일 경로 → 전용 get_*_path() 함수 정의
  - 하드코딩 금지: 모든 설정값 YAML로

## 설정 관리
  - OmegaConf + YAML 기반 3계층: base → domain → env
  - uv 전용 (pip install 직접 금지)
```

수락 기준: `wc -l apps/CLAUDE.md` 200 이하,
`grep "get_\*_path\|get_.*_path" apps/CLAUDE.md` 존재

---

### Step 5: pre-commit 설정 (Phase 3)

**대상 파일**: `.pre-commit-config.yaml` (신규)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff          # line-length=79, PEP8
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
        args: [--strict]  # 모든 타입힌트 필수

  - repo: https://github.com/PyCQA/bandit
    hooks:
      - id: bandit        # 보안 취약점 탐지
```

`pyproject.toml`에 ruff 설정 추가:
```toml
[tool.ruff]
line-length = 79
```

**중요 규칙 문서화**: `--no-verify` 사용 금지를 `.claude/CLAUDE.md` AW-010에 명시

수락 기준:
- `grep "line-length = 79\|line-length=79" .pre-commit-config.yaml pyproject.toml` 존재
- `grep "mypy" .pre-commit-config.yaml` 존재 및 `grep "strict" .pre-commit-config.yaml` 존재
- `grep "bandit" .pre-commit-config.yaml` 존재

---

### Step 6: Stop hook 등록 (Phase 3)

**대상 파일**: `.claude/settings.json` (기존 파일에 추가 또는 신규)

Stop hook 등록: Claude Code 응답 완료 후 `/check-python-style` 스킬 자동 호출

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[Stop Hook] /check-python-style 검사 실행'"
          }
        ]
      }
    ]
  }
}
```

수락 기준:
- `grep "Stop" .claude/settings.json` 존재
- `grep "check-python-style\|check_python_style" .claude/settings.json` 존재

---

### Step 7: output-styles 파일 (Phase 4, 독립 실행 가능)

**대상 파일**: `.claude/output-styles/data-driven-minds.md` (신규, 디렉토리 생성 포함)

```
# Data-Driven Minds Output Style

## 응답 형식 원칙
  - 수치와 근거 먼저, 의견 나중
  - 불확실성 명시: "추정", "측정 필요" 구분
  - 한국어 설명, 기술 용어 영어 유지

## 코드 출력 원칙
  - 실행 가능한 code block만 제시
  - 79자 줄 길이 준수
  - 타입힌트 포함

## 보고서 형식
  - 요약 → 상세 순서
  - 표/그래프 우선, 서술 보조
```

수락 기준:
- `ls .claude/output-styles/data-driven-minds.md` 파일 존재
- `wc -l .claude/output-styles/data-driven-minds.md` 출력이 0 초과

---

## 정량적 종료조건 15개

아래 명령어가 모두 기대 결과를 반환할 때 구현 완료로 판정한다.

```bash
# 1. 루트 CLAUDE.md 200줄 이하
wc -l /path/CLAUDE.md | awk '{print ($1 <= 200)}'
# 기대: 1

# 2. AW-001~010 루트 또는 .claude/CLAUDE.md에 모두 존재
grep -rh "AW-0" CLAUDE.md .claude/CLAUDE.md | grep -o "AW-0[0-9][0-9]" | sort -u | wc -l
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

# 8. nested CLAUDE.md 4개 모두 200줄 이하
for f in .claude/CLAUDE.md agents/CLAUDE.md libs/CLAUDE.md apps/CLAUDE.md; do wc -l "$f" | awk -v f="$f" '{if($1>200) print "FAIL: "f" ("$1" lines)"}'; done
# 기대: 출력 없음

# 9. agents/CLAUDE.md에 root_agent 및 app: prefix 존재
grep "root_agent" agents/CLAUDE.md && grep "app:" agents/CLAUDE.md
# 기대: 오류 없음

# 10. pre-commit ruff 79자 설정 존재
grep -E "line.length.{0,5}79" .pre-commit-config.yaml pyproject.toml
# 기대: 매칭 1줄 이상

# 11. pre-commit mypy strict + bandit 존재
grep "strict" .pre-commit-config.yaml && grep "bandit" .pre-commit-config.yaml
# 기대: 오류 없음

# 12. Stop hook 설정 존재
grep "Stop" .claude/settings.json
# 기대: 매칭 1줄 이상

# 13. output-styles 파일 존재 및 비어있지 않음
test -s .claude/output-styles/data-driven-minds.md && echo "OK"
# 기대: OK

# 14. convention-adr에 되돌리기 어려운/쉬운 결정 기준 존재
grep "되돌리기 어려운" .claude/skills/convention-adr/SKILL.md && grep "되돌리기 쉬운" .claude/skills/convention-adr/SKILL.md
# 기대: 오류 없음

# 15. convention-pr에 Rule of Small + check-design-doc 존재
grep "Rule of Small" .claude/skills/convention-pr/SKILL.md && grep "check-design-doc" .claude/skills/convention-pr/SKILL.md
# 기대: 오류 없음
```

---

## ADR: 핵심 결정 사항

**Decision**: Option B (우선순위별 순차+병렬 혼합)를 선택한다.

**Drivers**:
1. 루트 CLAUDE.md 200줄 제약이 모든 하위 파일에 영향 — 기반 파일 우선 확정 필요
2. `.claude/CLAUDE.md`가 AW 상세 버전 위임처 — 루트와 동시에 설계해야 줄 수 제약 충족 가능
3. Phase 2 이후는 파일 간 의존성 없음 — 병렬 처리로 시간 단축

**Alternatives Considered**:
- Option A (전체 병렬): 루트 CLAUDE.md 동시 편집 충돌 위험으로 기각

**Why Chosen**: 기반 파일(루트, `.claude/CLAUDE.md`) 확정 → 나머지 병렬의 혼합 전략이 품질과
속도를 동시에 달성

**Consequences**:
- 긍정: 루트 CLAUDE.md 줄 수 초과 위험 제거, 단계별 verifier 검증 가능
- 부정: Phase 1 완료 전 Phase 2 착수 불가 (대기 시간 소량 발생)

**Follow-ups**:
- `.claude/CLAUDE.md` 작성 후 루트 CLAUDE.md와 AW 규칙 번호 중복 없는지 확인
- convention-python skill이 기존 `python-patterns` skill과 내용 중복되지 않는지 확인 후
  `python-patterns`를 이 repo 규칙 기준으로 갱신 또는 deprecated 표시 결정

---

## Success Criteria

- `wc -l CLAUDE.md` 200 이하
- AW-001~010 전부 문서화됨
- Skills 9개 모두 생성, 각 skill 상황 예시 2개 이상
- Nested CLAUDE.md 4개 모두 200줄 이하
- pre-commit: ruff 79자, mypy strict, bandit 3종 설정
- Stop hook 등록
- `.claude/output-styles/data-driven-minds.md` 존재
- 정량적 종료조건 15개 전부 통과
