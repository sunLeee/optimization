# General Rules — 팀 Claude Code 운영 규칙

이 파일은 팀 전체가 Claude Code를 사용할 때 적용하는 핵심 운영 규칙이다.
루트 `CLAUDE.md`의 Team Operations 섹션과 함께 읽는다.

## 모델 규칙

| 도구 | 내부망 제한 | 사용 모델 |
|------|-----------|---------|
| Claude Code | opus 사용 불가 | `claude-sonnet-4-6[1m]` 고정 |
| Codex CLI | gpt-5.1-codex-mini/max, gpt-5.2, gpt-5.2-codex만 지원 | `gpt-5.2-codex` 고정 |
| Gemini | 제한 없음 | 고성능 사고 수준에 우선 사용 |

## AskUserQuestion 사전 조사 의무

AskUserQuestion 호출 전 반드시 `/omc-teams`로 codex + gemini에게 best practice를 조사한다.

```bash
# 필수 절차
/oh-my-claudecode:omc-teams 2:codex "조사 주제"  # + 동시에
2:gemini "조사 주제"

# 결과 종합 → pros/cons 비교 → (Recommended) 명시 → AskUserQuestion
```

**금지**: omc-teams 없이 AskUserQuestion 직접 호출.
**예외**: 컨벤션 스킬로 답이 정해지는 사항은 직접 결정.

deep-interview 시작 전에도 동일하게 omc-teams 사전 조사 의무 적용.

## 설계문서 관리 규칙

- 모든 작업: 설계문서(CLAUDE.md) 먼저 작성 → 준수
- CLAUDE.md: **200줄 이하** — 초과 시 `docs/design/ref/*.md`로 분리 후 링크
- 설계문서 수정: 반드시 `/ralplan`으로 계획 후 진행
- 설계-구현 무모순성 유지 — 차이 발생 시 즉시 일치시킨다

## 종료조건 정의 규칙

### ralph 실행 기준

모든 구현은 `/ralph` 사용. max iteration 100.

```bash
/oh-my-claudecode:ralph "구현 내용 설명"
# 계획 파일이 있으면 경로 지정
/oh-my-claudecode:ralph ".omc/plans/my-plan-v3.md 기반으로 구현"
```

### ralplan 종료조건: 30개 이상 정량적 목표

종료조건은 **grep/wc/test 명령어로 측정 가능한 것만** 인정한다.

**3-agent 병렬 도출 방법**:

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| Claude Code | `claude-sonnet-4-6[1m]` (내부망 고정) | 현재 codebase 패턴 분석 + 종료조건 초안 |
| Codex CLI | `gpt-5.2-codex` (내부망 고정) | 구현 관점의 검증 가능한 조건 도출 |
| Gemini | 고성능 모델 (제한 없음) | 엣지케이스 + 누락된 조건 추가 |

```bash
# 예시: demand analyst 에이전트 구현의 종료조건
grep -c "def test_" agents/demand_analyst/tests/*.py  # >= 10
grep "root_agent" agents/demand_analyst/__init__.py    # 존재
wc -l agents/demand_analyst/tools/*.py | awk '$1 > 200 {print}' | wc -l  # = 0
grep -rn "iterrows" agents/demand_analyst/ | wc -l    # = 0 (금지)
uv run mypy agents/demand_analyst/ --strict 2>&1 | grep "error:" | wc -l  # = 0
```

**나쁜 예시 (측정 불가 → 거절)**:
- "구현이 완료되었다"
- "테스트가 통과한다"
- "코드가 깔끔하다"

### deep-interview 모호성: 5% 미만까지

99.9999% 확신이 없으면 구현하지 말고 질문한다. 구체적 상황:

**변수명이 설계문서에 없는 경우**:

설계문서에 "집계 결과를 저장한다"라고만 적혀 있고 변수명이 없으면:
```
질문: "집계 결과를 담는 변수명을 정해야 합니다.
  - result_df (DataFrame 임을 명시)
  - aggregated_demand (도메인 의미 강조)
  - demand_summary (요약 성격 강조)
  어떤 명칭을 사용할까요? 또는 다른 이름이 있나요?"
```

**로직 구현 방법이 불명확한 경우**:

예: "zone_id별 수요를 집계한다"라는 요구사항에서:
```
질문: "zone_id별 집계 방식을 확인해야 합니다.
  현재 2가지 방법이 가능합니다:
  1. pandas groupby: df.groupby('zone_id')['demand'].sum()
     → 메모리 내 처리, zone_id가 수천 개 이하일 때 적합
  2. SQL ANSI query: SELECT zone_id, SUM(demand) FROM ... GROUP BY zone_id
     → DuckDB/SQLite 등 엔진 독립적, 대용량 적합
  현재 데이터 크기(zone_id 수, 행 수)가 어떻게 되나요?
  내부망에서 어떤 DB 엔진을 사용하고 있나요?"
```

**function 네이밍이 불명확한 경우**:

설계문서에 "수요 데이터를 불러온다"라고만 있을 때:
```
질문: "function 이름을 정해야 합니다.
  기존 코드베이스의 패턴을 확인했을 때:
  - load_demand_data() — 파일 로딩 강조
  - fetch_demand() — 데이터 소스 무관한 추상화
  - get_demand_dataframe() — 반환 타입 명시
  현재 팀 convention(snake_case)에 맞는 이름으로,
  어떤 네이밍을 선호하시나요?"
```

**판단 기준**: 설계문서에 없는 것은 추측하지 않는다. 팀 컨벤션(`/convention-python`)으로 명확히 결정되는 경우는 질문 없이 직접 적용.

## oh-my-claudecode (OMC) 워크플로우

```
deep-interview (모호성 5% 미만) → ralplan (Planner→Architect→Critic 합의) → ralph (구현 루프)
```

**상세**: [docs/references/claude-code/omc.md](./references/claude-code/omc.md)

## 참조

- [루트 CLAUDE.md](../CLAUDE.md) — 전체 Team Operations 규칙 (AW-001~010)
- [docs/design/ref/team-operations.md](./design/ref/team-operations.md) — AW 규칙 상세
- [docs/references/claude-code/](./references/claude-code/) — Claude Code 고급 활용 가이드
