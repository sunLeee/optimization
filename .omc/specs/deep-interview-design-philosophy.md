# Deep Interview Spec: Design Philosophy Integration

## Metadata
- Interview ID: di-design-philosophy-001
- Rounds: 2
- Final Ambiguity Score: 13%
- Type: brownfield
- Generated: 2026-03-19
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.90 | 40% | 0.36 |
| Constraint Clarity | 0.85 | 30% | 0.255 |
| Success Criteria | 0.85 | 30% | 0.255 |
| **Total Clarity** | | | **0.87** |
| **Ambiguity** | | | **13%** |

## Goal

34개 프로그래밍 design philosophy를 AW 규칙번호(AW-012~AW-045) + `.claude/skills/` skill 형태로 통합한다.
각 skill은 Python 코드 예시(위반 사례 + 개선 사례) 2개 이상을 포함하고, @ 링킹으로 AW 규칙, 파일, skill 간 참조관계를 완성한다.
추가로 Anthropic 공식 claude-md-management 플러그인을 통합한다.

## Constraints

- 각 skill에 Python 코드 예시 **2개 이상** 필수 (위반 사례 + 개선 사례 쌍)
- @ 링킹: `@AW-XXX` + `@파일경로` + `@skill이름` 혼합 방식
- skill 파일 위치: `.claude/skills/{principle-name}/SKILL.md`
- AW 규칙 위치: `docs/design/ref/team-operations.md`
- CLAUDE.md Team Operations 테이블에도 AW-012~045 추가
- 브랜치 범위: `.claude/skills/`, `CLAUDE.md`, `docs/` 만 수정
- Python 예시는 프로젝트 도메인(ADK 에이전트, 데이터 파이프라인) 반영

## Non-Goals

- 실제 Python 코드 구현 변경 없음
- `.py` 파일 수정 없음
- agents/, libs/, apps/ 변경 없음

## Acceptance Criteria

- [ ] `docs/design/ref/team-operations.md`에 AW-012~045 (34개) 등록
- [ ] `.claude/skills/` 에 34개 신규 SKILL.md 생성
- [ ] 각 SKILL.md: Python 코드 예시 2개 이상 (violation + fix)
- [ ] 각 SKILL.md: `## 관련 CLAUDE.md 규칙` 섹션에 @AW-XXX 링크
- [ ] 각 SKILL.md: `## 참조` 섹션에 @파일경로 + @skill이름 링크
- [ ] `CLAUDE.md` Team Operations 테이블 AW-012~045 추가
- [ ] `.claude/skill-catalog.md` 업데이트 (34개 신규 항목)
- [ ] claude-md-management 플러그인 통합 (claude-md-improver + /revise-claude-md)

## 34개 Design Philosophy 목록 (AW-012~AW-045)

| AW | 원칙 | 출처 | Skill 이름 |
|----|------|------|-----------|
| AW-012 | SRP (Single Responsibility) | SOLID | `convention-solid-srp` |
| AW-013 | OCP (Open/Closed) | SOLID | `convention-solid-ocp` |
| AW-014 | LSP (Liskov Substitution) | SOLID | `convention-solid-lsp` |
| AW-015 | ISP (Interface Segregation) | SOLID | `convention-solid-isp` |
| AW-016 | DIP (Dependency Inversion) | SOLID | `convention-solid-dip` |
| AW-017 | KISS | Kelly Johnson | `convention-kiss` |
| AW-018 | DRY | Hunt & Thomas | `convention-dry` |
| AW-019 | YAGNI | XP | `convention-yagni` |
| AW-020 | SoC (Separation of Concerns) | Dijkstra 1974 | `convention-soc` |
| AW-021 | Zen of Python | Tim Peters 1999 | `convention-zen-python` |
| AW-022 | Unix Philosophy | McIlroy/Pike | `convention-unix-philosophy` |
| AW-023 | Gall's Law | John Gall 1975 | `convention-galls-law` |
| AW-024 | Conway's Law | Mel Conway 1967 | `convention-conways-law` |
| AW-025 | Hyrum's Law | Hyrum Wright | `convention-hyrums-law` |
| AW-026 | Chesterton's Fence | G.K. Chesterton | `convention-chestertons-fence` |
| AW-027 | Kernighan's Law | Brian Kernighan | `convention-kernighans-law` |
| AW-028 | Brooks' Law | Fred Brooks | `convention-brooks-law` |
| AW-029 | Postel's Law | Jon Postel | `convention-postels-law` |
| AW-030 | Wirth's Law | Niklaus Wirth | `convention-wirths-law` |
| AW-031 | Law of Leaky Abstractions | Joel Spolsky | `convention-leaky-abstractions` |
| AW-032 | Law of Demeter (LoD) | Lieberherr 1987 | `convention-law-of-demeter` |
| AW-033 | Command-Query Separation | Bertrand Meyer | `convention-cqs` |
| AW-034 | Tell, Don't Ask | Andy Hunt | `convention-tell-dont-ask` |
| AW-035 | Boy Scout Rule | Robert Martin | `convention-boy-scout-rule` |
| AW-036 | Worse Is Better | Richard Gabriel | `convention-worse-is-better` |
| AW-037 | 80/20 Rule (Pareto) | Pareto 1906 | `convention-pareto-rule` |
| AW-038 | Rule of Three | Martin Fowler | `convention-rule-of-three` |
| AW-039 | Principle of Least Astonishment | UI 원칙 | `convention-least-astonishment` |
| AW-040 | Zero One Infinity | Van der Poel | `convention-zero-one-infinity` |
| AW-041 | Technical Debt | Ward Cunningham | `convention-technical-debt` |
| AW-042 | Inversion of Control (IoC) | Martin Fowler | `convention-ioc` |
| AW-043 | Four Rules of Simple Design | Kent Beck | `convention-simple-design` |
| AW-044 | Single Level of Abstraction | Kent Beck | `convention-single-abstraction` |
| AW-045 | Pragmatic Programmer Rules | Hunt & Thomas | `convention-pragmatic-programmer` |

## @ 링킹 포맷 표준

```markdown
## 관련 CLAUDE.md 규칙
@AW-018 | @docs/design/ref/team-operations.md § AW-018

## 선행 skill
@convention-python → 먼저 실행
@check-anti-patterns → 함께 실행

## 참조
@docs/design/ref/team-operations.md § AW-018
@.claude/skills/check-anti-patterns/SKILL.md
```

## Python 예시 포맷 표준 (DRY 참고)

```python
# VIOLATION: [원칙 위반 설명]
def create_user(name, email, age):
    if not name or len(name) < 2:  # 중복 로직
        raise ValueError("이름은 2글자 이상")
    ...

def update_user(user_id, name, email, age):
    if not name or len(name) < 2:  # 동일 로직 반복 — DRY 위반
        raise ValueError("이름은 2글자 이상")
    ...

# CORRECT: [개선 설명]
def validate_user_data(name: str, email: str, age: int) -> None:
    if not name or len(name) < 2:
        raise ValueError("이름은 2글자 이상")
    ...  # 단일 위치에서 관리

def create_user(name: str, email: str, age: int) -> User:
    validate_user_data(name, email, age)
    ...
```

## claude-md-management 통합

- `claude-md-improver` skill: CLAUDE.md를 코드베이스와 비교하여 감사
- `/revise-claude-md` command: 세션 학습을 CLAUDE.md에 반영
- 출처: Anthropic 공식 플러그인 (Isabella He, isabella@anthropic.com)
- 통합 방법: `.claude/skills/claude-md-improver/SKILL.md` 생성

## Technical Context

- 브랜치: `shucle-ai-agent-general-rules`
- 기존 AW 규칙: AW-001~AW-011 (team-operations.md)
- 기존 skill: 16개 (.claude/skills/)
- 추가 skill: 34개 + 1개(claude-md-improver) = 35개 신규

## Interview Transcript

### Round 1 — Constraint Clarity (target)
Q: "@ 형태로 링킹"의 정확한 의미는?
A: 모두 포함 (혼합 방식) — @AW-011 | @파일경로 + @skill이름
Ambiguity: 35%

### Round 2 — Success Criteria (target)
Q: 34개 중 이번 PR에 얼마나, 완료 시점은?
A: 전체 34개 시도 (Full Coverage). 모든 내용에 2개 이상 구체적 Python 예시 (위반+개선).
Ambiguity: 13% ✅ (임계값 20% 이하)
