# 팀 운영 규칙 (Team Operations)

> **AW (Agent Workflow)**: Claude Code 에이전트가 작업 시 따라야 하는 워크플로우 규칙 번호체계.
> AW-001~045 = 모델 선택부터 설계 원칙까지 팀 전체가 준수하는 정량적 규칙 집합.
> 관리 위치: 이 파일 + [CLAUDE.md](../../CLAUDE.md) § Team Operations
>
> 적용 범위: 에이전트 운영 규칙 (모델 선택, AskUserQuestion 절차, 설계문서 관리, 종료조건)
> 이 파일은 데이터 파이프라인 기술 명세(R-001~R-027)와 별개다.
> **버전**: 2026-03-18
> **관련 문서**: [CLAUDE.md](../../CLAUDE.md#team-operations) · [project-overall-rule.md](./project-overall-rule.md)

---

## AW-001~005 (기존 규칙)

### 모델 선택 (AW-001)

- Claude Code: `claude-sonnet-4-6[1m]` 고정 (내부망 opus 불가)
- Codex CLI: `gpt-5.2-codex` 고정
- Gemini: 모든 모델 사용 가능 — 최고 성능 사고 수준에 우선 사용

**상황 1**: 내부망에서 opus 호출 시도 → `claude-sonnet-4-6[1m]`으로 자동 대체
**상황 2**: 고성능 분석 필요 시 Gemini 먼저 고려 후 Claude 보완

### 3-agent 조사 (AW-002)

claude + codex + gemini에게 병렬 질의 → 다수결 또는 사용자 결정

**상황 1**: 기술 스택 선택 시 3-agent 조사 결과 비교 후 (Recommended) 명시
**상황 2**: 코드 패턴 결정 시 3개 의견이 일치하면 즉시 적용

### AskUserQuestion 사전 조사 (AW-003, AW-004)

- AW-003: deep-interview 시작 전 omc-teams 사전조사 의무
- AW-004: AskUserQuestion 전 omc-teams 사전조사 의무
- 금지: omc-teams 없이 직접 질문

절차: `2:codex + 2:gemini` 병렬 → pros/cons 비교 → (Recommended) 명시 → 질문
예외: convention skill로 답이 정해지는 사항은 직접 결정

### deep-interview (AW-005)

- 모호성 5% 미만까지 진행. 구현 전 필수.
- 구현 확신 99.9999% 미만이면 계속 질문

---

## AW-006~010 (신규 규칙)

### 설계문서 먼저 (AW-006)

코드 PR 전 설계 PR 통과 필수. 설계-구현 무모순성 의무.

**상황 1**: 새 기능 구현 시 CLAUDE.md 또는 docs/design/ 먼저 작성 → 리뷰 → 코드 구현
**상황 2**: 구현 중 설계문서와 달라진 경우 → 즉시 설계문서 업데이트 후 계속 진행

### ralph 사용 의무 (AW-007)

모든 구현은 `/ralph` 사용. max iteration: 100

**상황 1**: 단순 함수 추가도 ralph로 감싸서 verifier 검증까지 완료
**상황 2**: ralph가 3+ 반복에서 같은 오류 → 사용자에게 근본 문제 보고

### ralplan 종료조건 (AW-008)

ralplan 시 종료조건 10개 이상, 정량적 목표. claude+codex+gemini 3-agent 조사로 도출.

**상황 1**: ralplan 결과물에 grep/wc 명령어로 측정 가능한 조건만 인정
**상황 2**: "구현 완료" 같은 추상 조건 → 거절 후 정량적으로 재정의

**좋은 예시 (grep/wc/test 측정 가능):**
```bash
find .claude/skills -name SKILL.md | wc -l          # ≥ 127
find .claude/skills -name SKILL.md -exec grep -l '^triggers:' {} \; | wc -l  # = 127
grep -c 'UserPromptSubmit' .claude/settings.json    # ≥ 1
find .claude/docs/adr -name '*.md' | wc -l          # ≥ 3
bash .claude/check-criteria.sh | grep -c '✅'       # ≥ 27
```

**나쁜 예시 (추상적, 측정 불가):**
- "구현 완료" — 언제 완료인지 판단 불가
- "기능이 잘 동작함" — "잘"의 기준 없음
- "코드가 깔끔함" — 주관적 판단
- "충분히 테스트됨" — 커버리지 수치 없음

### ADR 의무 (AW-009)

되돌리기 어려운 결정 = ADR 먼저. (`/convention-adr` 참조)

| 유형 | 예시 | 처리 |
|------|------|------|
| 되돌리기 쉬운 | 변수명, 주석 | 바로 결정 |
| 되돌리기 어려운 | 파일 포맷, API 계약, 좌표계 | ADR 작성 후 ralplan |

**상황 1**: 파일 포맷을 CSV→Parquet 변경 시 → ADR-XXX 작성 후 진행
**상황 2**: 변수명 변경 → ADR 불필요, 바로 결정

### pre-commit 안전망 + Stop hook 알림 (AW-010)

| 도구 | 역할 | 강제 여부 |
|------|------|----------|
| pre-commit | ruff(79자) + mypy(strict) + bandit | commit 차단 (실제 강제) |
| Stop hook | 정보성 알림 메시지 출력 | 알림만 (실제 강제 없음) |

- `--no-verify` 사용 금지
- pre-commit 설치: `pre-commit install` (clone 후 1회)

**상황 1**: type hint 누락 코드 commit 시 → mypy --strict가 commit 차단
**상황 2**: 79자 초과 줄 → ruff가 commit 전 자동 감지

---

## AW-011 (Rob Pike Rules 통합)

> 출처: Rob Pike의 프로그래밍 5가지 규칙 (1989)

### 측정 전 구현 금지 (AW-011)

- **Rule 1/2**: 병목은 예상 못한 곳에서 발생한다. 측정 전 최적화 금지.
- **Rule 3/4**: n이 작을 때 단순 알고리즘이 빠르다. 복잡한 알고리즘은 버그가 많다.
- **Rule 5**: 데이터 구조가 코드를 지배한다. ADK state 설계를 먼저 확정하라.

| Rule | 행동지침 | 매핑 |
|------|----------|------|
| 측정 먼저 | "성능 개선" 요청 시 → baseline 수치 먼저 확인 | Rule 1/2 |
| 단순 알고리즘 | n이 명시되지 않은 최적화 코드 작성 금지 | Rule 3/4 |
| 데이터 구조 우선 | ADK `tool_context.state` schema 먼저 설계, 코드 나중 | Rule 5 |

**상황 1**: "이 함수 성능 개선해줘" → `uv run python -m cProfile` 결과 먼저 요청, 수치 확정 후 구현
**상황 2**: 복잡한 집계 알고리즘 제안 시 → 처리 데이터 크기(n) 확인 후 pandas vectorization vs SQL 결정
**상황 3**: 새 ADK 에이전트 구현 전 → `initial_state`, `tool_context.state` schema 설계 먼저

---

## LLM 행동지침 상세

### Think Before Coding

가정하지 말라. 불명확하면 deep-interview 시작.

**상황 1**: function signature가 설계문서에 없으면 → 추측 구현 금지, 질문
**상황 2**: "이 API를 추가해줘"에 request/response schema 없으면 → 구현 전 schema 확정

### Simplicity First

요청받은 것만. speculative code 금지. 200줄로 썼는데 50줄 가능하면 다시 써라.

**상황 1**: CSV 읽는 function 작성 시 XML/JSON도 지원하는 generic reader 추가 → 금지
**상황 2**: pipeline 구현 시 미래 대비 plugin system 추가 → 요청받지 않았으면 금지

### Surgical Changes

반드시 수정할 것만 건드려라. 인접 code "개선" 금지.

**상황 1**: bug 수정 중 인접 function 개선 가능해 보여도 → 건드리지 않는다
**상황 2**: import 순서가 PEP8 위반인 기존 파일 편집 시 → import 정렬 "개선" 금지

### Goal-Driven Execution

success criteria 정의 → 검증 → 반복.

**상황 1**: "잘 되게 해줘" → 거절 후 정량적 기준 요청 → deep-interview
**상황 2**: "성능 개선" → "현재 응답시간? 목표?" → 수치 확정 후 구현

---

## 기술 어휘 언어 규칙

기술 용어는 영어, 일반 설명은 한국어.

| 영어 유지 | 한국어 사용 |
|-----------|-------------|
| class, function, method, import | 이 함수는, 이 클래스는 |
| pre-commit, hook, skill, plugin | 사전 검사, 기능 |
| PR, ADR, CLAUDE.md | - |
| snake_case, PascalCase | - |
| omc-teams, deep-interview, ralph | - |

## 명명 규칙 요약표

| 용도 | 표기법 | 예시 |
|------|--------|------|
| Python 파일/모듈/변수/함수 | `snake_case` | `demand_analysis.py`, `zone_id` |
| Python class | `PascalCase` | `DataProcessor` |
| Python 상수 | `UPPER_SNAKE_CASE` | `MAX_RETRY` |
| 문서 파일 (.md) | `kebab-case` | `issue-74-ai-pr.md` |
| Git 브랜치명 | `kebab-case` | `feat/issue-74-pr-rules` |
| Skills/plugin 이름 | `kebab-case` | `convention-python` |
| Python import 대상 디렉토리 | `snake_case` | `libs/data_processing/` |
| 문서/설정 디렉토리 | `kebab-case` | `docs/github-issues/` |
| OmegaConf/YAML 키 | `snake_case` | `zone_id: 40` |

원칙: `snake_case` = Python namespace 안, `kebab-case` = 파일시스템/URL/CLI 단위

---

## AW-012~045 (Design Philosophy Rules)

> 출처: 프로그래밍 설계 철학 34원칙 (deep-interview 2026-03-19)
> 각 규칙은 `.claude/skills/convention-{name}/SKILL.md`에 Python 예시 2개 이상과 @ 링킹 포함

### SOLID 원칙 (AW-012~016)

| 규칙 | 원칙 | Skill | 핵심 |
|------|------|-------|------|
| AW-012 | SRP — Single Responsibility | @convention-solid-srp | 클래스/함수는 하나의 변경 이유만 |
| AW-013 | OCP — Open/Closed | @convention-solid-ocp | 확장에 열려 있고, 수정에 닫혀 있다 |
| AW-014 | LSP — Liskov Substitution | @convention-solid-lsp | 서브타입은 기반 타입 대체 가능 |
| AW-015 | ISP — Interface Segregation | @convention-solid-isp | 클라이언트는 불필요한 인터페이스 강제 없음 |
| AW-016 | DIP — Dependency Inversion | @convention-solid-dip | 고수준 모듈이 저수준 모듈에 의존하지 않는다 |

**상황 1**: `DemandAgent`가 데이터 로딩 + 분석 + 리포트를 모두 담당 → SRP 위반 → 역할 분리
**상황 2**: CSV reader가 Parquet도 지원하도록 if/elif 추가 → OCP 위반 → 새 클래스 추가로 확장

### 핵심 원칙 (AW-017~022)

| 규칙 | 원칙 | Skill | 핵심 |
|------|------|-------|------|
| AW-017 | KISS | @convention-kiss | 불필요한 복잡성 금지 |
| AW-018 | DRY | @convention-dry | 지식은 단일 표현 — 중복 제거 |
| AW-019 | YAGNI | @convention-yagni | 필요할 때만 구현 |
| AW-020 | SoC | @convention-soc | 관심사 분리 |
| AW-021 | Zen of Python | @convention-zen-python | 명시적 > 암시적, 단순 > 복잡 |
| AW-022 | Unix Philosophy | @convention-unix-philosophy | 한 가지 잘 하기, 조합 |

**상황 1**: 한 번만 쓸 validation 로직을 abstract factory로 감쌈 → YAGNI 위반 → 직접 구현
**상황 2**: `create_user()`와 `update_user()`에 동일 검증 로직 복붙 → DRY 위반 → `validate_user_data()` 추출

### 법칙 (AW-023~032)

| 규칙 | 원칙 | Skill | 핵심 |
|------|------|-------|------|
| AW-023 | Gall's Law | @convention-galls-law | 복잡한 시스템은 단순한 것에서 진화 |
| AW-024 | Conway's Law | @convention-conways-law | 소프트웨어 구조 = 조직 구조 |
| AW-025 | Hyrum's Law | @convention-hyrums-law | 충분한 사용자 → 모든 동작이 의존된다 |
| AW-026 | Chesterton's Fence | @convention-chestertons-fence | 이유 모르면 제거하지 말라 |
| AW-027 | Kernighan's Law | @convention-kernighans-law | 디버깅은 코딩보다 2배 어렵다 |
| AW-028 | Brooks' Law | @convention-brooks-law | 늦은 프로젝트에 인력 추가 = 더 늦어짐 |
| AW-029 | Postel's Law | @convention-postels-law | 보내는 것 엄격히, 받는 것 관대히 |
| AW-030 | Wirth's Law | @convention-wirths-law | 소프트웨어는 하드웨어보다 빨리 느려진다 |
| AW-031 | Law of Leaky Abstractions | @convention-leaky-abstractions | 모든 추상화는 결국 새어나온다 |
| AW-032 | Law of Demeter | @convention-law-of-demeter | 직접 친구에게만 말하라 |

### 설계 규칙 (AW-033~045)

| 규칙 | 원칙 | Skill | 핵심 |
|------|------|-------|------|
| AW-033 | CQS | @convention-cqs | 질문하거나 명령하거나 — 둘 다 금지 |
| AW-034 | Tell, Don't Ask | @convention-tell-dont-ask | 객체에 결정권을 줘라 |
| AW-035 | Boy Scout Rule | @convention-boy-scout-rule | 발견했을 때보다 조금 더 깨끗하게 |
| AW-036 | Worse Is Better | @convention-worse-is-better | 단순 인터페이스 > 단순 구현 |
| AW-037 | Pareto Rule (80/20) | @convention-pareto-rule | 80% 효과는 20% 원인에서 |
| AW-038 | Rule of Three | @convention-rule-of-three | 3번 반복되면 리팩토링 |
| AW-039 | Least Astonishment | @convention-least-astonishment | 사용자/개발자를 놀라게 하지 말라 |
| AW-040 | Zero One Infinity | @convention-zero-one-infinity | 0, 1, 무한대만 허용 |
| AW-041 | Technical Debt | @convention-technical-debt | 빠른 해결책은 이자를 낸다 |
| AW-042 | IoC | @convention-ioc | 제어권을 프레임워크에 위임 |
| AW-043 | Simple Design (Kent Beck) | @convention-simple-design | 테스트 통과 > 의도 표현 > 중복 없음 > 최소 요소 |
| AW-044 | Single Level of Abstraction | @convention-single-abstraction | 함수 내 모든 코드는 같은 추상화 수준 |
| AW-045 | Pragmatic Programmer | @convention-pragmatic-programmer | Tracer Bullets, DRY, 직교성, 가역성 |

## GitHub Issues md화 규칙

작업 시작 전 관련 issue를 md화하여 컨텍스트로 활용한다.

- **저장 경로**: `docs/references/github-issues/`
- **파일명**: `issue-{number}-{subject}.md` (subject: kebab-case, 30자 이하)
- **생성**: `gh api 'repos/hkmc-airlab/shucle-ai-agent/contents/...' ` 또는 `gh issue view {number}`
- **예시**: `issue-74-ai-pr-workflow.md`
