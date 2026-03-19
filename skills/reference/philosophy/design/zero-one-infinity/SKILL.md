---
name: convention-zero-one-infinity
description: Zero One Infinity Rule. 0, 1, 무한대만 허용. 임의의 제한값(2, 3, 7...)은 결국 틀린다.
user-invocable: true
triggers:
  - "zero one infinity"
  - "0 1 무한대"
  - "임의의 제한"
  - "magic number"
---

# convention-zero-one-infinity

**@AW-040** | @docs/design/ref/team-operations.md § AW-040

Zero One Infinity Rule (Willem van der Poel): "컴퓨터 프로그램에서 허용되는 숫자는 0, 1, 무한대뿐이다. 임의의 한계를 두지 말라."

## VIOLATION 1: 임의의 제한값

```python
# VIOLATION: "최대 5개 에이전트" — 왜 5?
MAX_AGENTS = 5  # 임의의 제한 — Zero One Infinity 위반

class AgentOrchestrator:
    def add_agent(self, agent: BaseAgent) -> None:
        if len(self.agents) >= MAX_AGENTS:
            raise ValueError("최대 5개 에이전트만 지원")
        self.agents.append(agent)

# 문제: 6번째 에이전트가 필요하면? 코드 수정 필요
```

```python
# CORRECT: 0 (없음), 1 (하나), 무한대 (제한 없음)
class AgentOrchestrator:
    def __init__(self, max_agents: int | None = None) -> None:
        """에이전트 오케스트레이터.

        Args:
            max_agents: 최대 에이전트 수. None이면 무제한.
        """
        self._agents: list[BaseAgent] = []
        self._max = max_agents  # 필요하면 설정 가능

    def add_agent(self, agent: BaseAgent) -> None:
        if self._max and len(self._agents) >= self._max:
            raise ValueError(f"최대 {self._max}개 제한 초과")
        self._agents.append(agent)
```

## VIOLATION 2: 하드코딩된 재시도 횟수

```python
# VIOLATION: "3번 재시도" — 왜 3?
def call_api_with_retry(url: str) -> dict:
    for attempt in range(3):  # 임의의 3 — Zero One Infinity 위반
        try:
            return requests.get(url).json()
        except Exception:
            if attempt == 2:
                raise
    return {}
```

```python
# CORRECT: 설정에서 받거나 무제한 (컨텍스트에 따라)
def call_api_with_retry(
    url: str,
    max_retries: int | None = None  # None = 무제한 (외부 제어)
) -> dict:
    """API를 호출하고 실패 시 재시도한다.

    Logics:
        max_retries가 None이면 성공할 때까지 재시도한다.
    """
    attempts = 0
    while True:
        try:
            return requests.get(url, timeout=10).json()
        except Exception:
            attempts += 1
            if max_retries and attempts >= max_retries:
                raise
```

## Magic Number 탐지

```bash
# 임의의 숫자 (magic number) 탐지
grep -rn "\b[2-9][0-9]*\b" agents/ --include="*.py" |
  grep -v "test_\|#\|docstring\|79\|100\|1000" |
  head -20
# 검토 후 config로 이동하거나 주석으로 이유 설명
```

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| @AW-040 | @docs/design/ref/team-operations.md § AW-040 | Zero One Infinity |
| @AW-019 | @docs/design/ref/team-operations.md § AW-019 | YAGNI — 불필요한 제한 |
| OmegaConf | CLAUDE.md § 아키텍처 | 설정값은 YAML로 외부화 |

## 참조

- @docs/design/ref/team-operations.md § AW-040
- @.claude/skills/convention-yagni/SKILL.md
