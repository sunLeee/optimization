# Skill Catalog — .claude/skills

> 업데이트: 2026-03-19 | 브랜치: shucle-ai-agent-general-rules
> 총 skill: 54개 (convention 44 + check 5 + utility 3 + reference 2)

---

## Python Convention Skills

| Skill | 목적 | AW 규칙 |
|-------|------|---------|
| `convention-python` | PEP8, type hint, Google docstring(한국어 73자), 79자 | AW-010 |
| `convention-commit` | Conventional Commits, kebab-case 브랜치 | - |
| `convention-logging` | structlog vs logging, TRACE 레벨, JSON/text | AW-010 |
| `convention-testing` | AAA 패턴, pytest fixture, 80% coverage | - |
| `convention-adr` | Y-statement ADR, 되돌리기 어려운 결정 | AW-009 |
| `convention-pr` | Rule of Small, 설계문서 먼저 | AW-006 |
| `convention-folder-structure` | monorepo, DS, Agent 구조 | - |
| `convention-design` | SRP, KISS, DRY, YAGNI, SoC 요약 | - |
| `convention-design-patterns` | Factory, Strategy, Repository, Observer, Decorator, Command, Adapter, Template Method | AW-013, AW-016 |

---

## Design Philosophy Skills (AW-012~045)

### SOLID 원칙 (AW-012~016)

| Skill | AW | 핵심 |
|-------|-----|------|
| `convention-solid-srp` | AW-012 | 단일 변경 이유 |
| `convention-solid-ocp` | AW-013 | 확장 open, 수정 closed |
| `convention-solid-lsp` | AW-014 | 서브타입 대체 가능 |
| `convention-solid-isp` | AW-015 | 인터페이스 분리 |
| `convention-solid-dip` | AW-016 | 추상화에 의존 |

### 핵심 원칙 (AW-017~022)

| Skill | AW | 핵심 |
|-------|-----|------|
| `convention-kiss` | AW-017 | 불필요한 복잡성 금지 |
| `convention-dry` | AW-018 | 지식의 단일 표현 |
| `convention-yagni` | AW-019 | 필요할 때만 구현 |
| `convention-soc` | AW-020 | 관심사 분리 |
| `convention-zen-python` | AW-021 | Explicit > Implicit, Simple > Complex |
| `convention-unix-philosophy` | AW-022 | 한 가지 잘 하기, 조합 |

### 법칙 (AW-023~032)

| Skill | AW | 핵심 |
|-------|-----|------|
| `convention-galls-law` | AW-023 | 단순한 것에서 복잡으로 진화 |
| `convention-conways-law` | AW-024 | 조직 구조 = 소프트웨어 구조 |
| `convention-hyrums-law` | AW-025 | 모든 동작이 의존된다 |
| `convention-chestertons-fence` | AW-026 | 이유 모르면 제거하지 말라 |
| `convention-kernighans-law` | AW-027 | 디버깅은 코딩보다 2배 어렵다 |
| `convention-brooks-law` | AW-028 | 늦은 프로젝트에 인력 추가 = 더 늦어짐 |
| `convention-postels-law` | AW-029 | 입력 관대, 출력 엄격 |
| `convention-wirths-law` | AW-030 | 소프트웨어는 하드웨어보다 빨리 느려진다 |
| `convention-leaky-abstractions` | AW-031 | 모든 추상화는 결국 새어나온다 |
| `convention-law-of-demeter` | AW-032 | 직접 친구에게만 말하라 |

### 설계 규칙 (AW-033~045)

| Skill | AW | 핵심 |
|-------|-----|------|
| `convention-cqs` | AW-033 | 질문 or 명령 — 둘 다 금지 |
| `convention-tell-dont-ask` | AW-034 | 객체에게 결정권을 |
| `convention-boy-scout-rule` | AW-035 | 왔을 때보다 깨끗하게 |
| `convention-worse-is-better` | AW-036 | 단순 인터페이스 > 완벽한 구현 |
| `convention-pareto-rule` | AW-037 | 80% 효과는 20% 원인 |
| `convention-rule-of-three` | AW-038 | 3번 반복 → 리팩토링 |
| `convention-least-astonishment` | AW-039 | 예측 가능하게 설계 |
| `convention-zero-one-infinity` | AW-040 | 0, 1, 무한대만 허용 |
| `convention-technical-debt` | AW-041 | 의도적 부채 관리 |
| `convention-ioc` | AW-042 | 제어권을 프레임워크에 |
| `convention-simple-design` | AW-043 | 테스트>의도>중복없음>최소 |
| `convention-single-abstraction` | AW-044 | 같은 추상화 수준 유지 |
| `convention-pragmatic-programmer` | AW-045 | Tracer Bullets, 직교성, 가역성 |

---

## ADK / 파이프라인 Skills

| Skill | 목적 | AW 규칙 |
|-------|------|---------|
| `convention-adk-agent` | ADK 에이전트 boilerplate, state schema 우선 | AW-011, AW-016 |
| `check-data-pipeline` | ToolContext 패턴, 파일 경로 anti-pattern | AW-011 |

---

## Check Skills (검증)

| Skill | 목적 | AW 규칙 |
|-------|------|---------|
| `check-python-style` | ruff(79자) + mypy(strict) + docstring | AW-010 |
| `check-anti-patterns` | God Class, Long Method, Feature Envy | AW-012 |
| `check-design-doc` | 코드-설계문서 일치 검증 | AW-006 |
| `check-data-pipeline` | ToolContext, 파일 경로 anti-pattern | AW-011 |

---

## CLAUDE.md Management Skills

| Skill | 목적 | 트리거 |
|-------|------|--------|
| `claude-md-improver` | CLAUDE.md 코드베이스 일치 감사 | 주기적 유지보수 |

---

## Utility Skills

| Skill | 목적 |
|-------|------|
| `lint-fix` | ruff 자동 수정 |
| `adversarial-review` | 레드팀/블루팀 셀프 리뷰 |
| `code-simplifier` | 코드 명확성/일관성 개선 |

---

## Reference Skills (외부 소스)

| Skill | 목적 | 주의 |
|-------|------|------|
| `python-patterns` | Pythonic idioms, PEP8 | `convention-python`과 중복 가능 |
| `python-testing` | pytest, TDD | `convention-testing`과 중복 가능 |
| `get-api-docs` | 외부 SDK/라이브러리 공식 문서를 직접 조회하여 hallucination 방지 | reference/adk |

---

## Skill 실행 체인 (구현 시 필수)

```
1. convention-python       → 코딩 컨벤션
2. convention-design       → 설계 원칙
3. check-anti-patterns     → 안티패턴 탐지
4. adversarial-review      → 셀프 리뷰
```

ADK 에이전트 추가:
```
5. convention-adk-agent    → ADK 패턴
6. check-data-pipeline     → ToolContext 검증
7. check-design-doc        → 설계문서 일치
```

---

## 관련 문서

- @CLAUDE.md § 구현 시 필수 스킬
- @docs/design/ref/team-operations.md § AW-001~045
- @docs/ref/bestpractice/claude-code-rule-convention.md § Practice 5, 14
- @.claude/AGENTS.md — 에이전트 계층 구조
