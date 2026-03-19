# oh-my-claudecode (OMC) 사용 가이드

> 참조: docs/ref/bestpractice/claude-code-rule-convention.md (Practice 9~12)
> OMC 공식: https://github.com/Yeachan-Heo/oh-my-claudecode

## 1. OMC 개요

Claude Code를 위한 멀티에이전트 오케스트레이션 레이어. skill, agent, hook, plugin을 통합하여 복잡한 작업을 자동화한다.

**이 프로젝트에서 사용하는 OMC 주요 기능**:

| 명령어 | 목적 | 사용 시점 |
|--------|------|---------|
| `/ralplan` | 합의 기반 계획 수립 | 구현 전 설계 합의 필요 시 |
| `/ralph` | 완료 보장 루프 (max 100 iter) | 구현 작업, 버그 수정 |
| `/ultrawork` | 독립 태스크 병렬 실행 | 여러 파일 동시 수정 |
| `/omc-teams` | codex + gemini 병렬 조사 | AskUserQuestion 전 사전 조사 |
| `/deep-interview` | 소크라테스식 요구사항 수집 | 모호성 5% 미만까지 |
| `/team` | 단계별 멀티에이전트 파이프라인 | plan→exec→verify→fix |

**상황 1**: 새 기능 추가 전 → `/deep-interview` → `/ralplan` → `/ralph`
**상황 2**: 기술 결정 필요 → `/omc-teams 2:codex "주제" + 2:gemini "주제"` → AskUserQuestion

## 2. 내부망 환경 설정

```bash
# Claude Code 환경 변수 (내부망)
export ANTHROPIC_BASE_URL="https://h-chat-api.autoever.com/claude-code"
export API_TIMEOUT_MS="1800000"

# Gemini CLI SSL 우회 (내부망 전용)
export NODE_TLS_REJECT_UNAUTHORIZED=0
```

**모델 제한 (AW-001)**:
- Claude Code: `claude-sonnet-4-6[1m]` 고정 (opus 불가)
- Codex CLI: `gpt-5.2-codex` 고정
- Gemini: 모든 모델 사용 가능

## 3. OMC 워크플로우 (AW-003~010 기반)

### 표준 개발 흐름

```
1. 요구사항 수집
   /deep-interview → 모호성 5% 미만까지
   (시작 전 omc-teams로 domain best practice 조사)

2. 설계 합의
   /ralplan → Planner → Architect → Critic 합의
   종료조건 10개 이상 정량적 목표 정의

3. 구현
   /ralph (max iteration 100)
   → 모든 story passes: true
   → Architect APPROVE
   → /cancel

4. 검증
   /check-design-doc → 코드-설계 일치 확인
   pre-commit → ruff(79자) + mypy(strict) + bandit
```

**상황 1**: 단순 버그 수정 → deep-interview 생략, `/ralph`로 바로 시작
**상황 2**: 새 시스템 설계 → 전체 흐름 필수 (deep-interview → ralplan → ralph)

## 4. ralplan 사용법

```bash
# 기본 (자동 합의)
/ralplan "태스크 설명"

# 대화형 (사용자 승인 포함)
/ralplan --interactive "태스크 설명"

# 고위험 작업 (pre-mortem + 확장 테스트 계획)
/ralplan --deliberate "태스크 설명"
```

**종료조건 작성 기준**:
```bash
# 좋은 예시 (측정 가능)
grep -c "## Team Operations" CLAUDE.md  # = 1

# 나쁜 예시 (측정 불가)
"구현이 완료되었다"
```

**상황 1**: ralplan 결과를 ralph로 실행 → 계획 파일 경로를 ralph에 전달
**상황 2**: Critic REJECT → Planner 수정 → Architect → Critic (최대 5 루프)

**ralph 실행 명령어 + 계획 파일 연동**:
```bash
# 1. ralplan으로 계획 수립 → .omc/plans/에 plan 파일 자동 저장
/ralplan "태스크 설명"

# 2. ralph로 계획 실행 (prd.json 기반 story 추적)
/ralph "태스크 설명"
# ralph는 .omc/prd.json을 읽어 story-by-story 실행

# 3. 종료 조건 검증
bash .claude/check-criteria.sh  # 90% 이상이면 종료
/cancel  # 완료 시 ralph 상태 정리
```

## 5. omc-teams 조사 패턴

```bash
# AskUserQuestion 전 필수
/oh-my-claudecode:omc-teams 2:codex "Python {domain} best practice"
# + 동시에
2:gemini "Python {domain} best practice"

# 결과 종합 → (Recommended) 명시 → AskUserQuestion
```

**이 프로젝트 제한**: codex는 `gpt-5.2-codex`, gemini는 전체 모델 사용 가능

**상황 1**: 새 라이브러리 선택 → 3종 조사 후 pros/cons 비교 표 작성
**상황 2**: 설계 패턴 선택 → 조사 없이 AskUserQuestion 직접 호출 금지

## 5-1. deep-interview 질문 형식 예시

deep-interview 시 AskUserQuestion으로 **선택지를 제시**하는 형식:

**변수명 질문 (선택지 제시형)**:
```
"zone_id 변수명을 어떻게 할까요?"
→ [A] zone_id  [B] zoneId  [C] ZONE_ID  [D] 직접 입력
```

**로직 구현 질문 (기술 비교형)**:
```
"수요 집계 로직을 어떻게 구현할까요?"
→ [A] pandas groupby: df.groupby('zone_id')['demand'].sum()
→ [B] ANSI SQL: SELECT zone_id, SUM(demand) FROM df GROUP BY zone_id
→ [C] 순수 Python dict comprehension
```

**function 명명 질문 (3가지 대안 제시형)**:
```
"집계 함수 이름을 어떻게 할까요?"
→ [A] aggregate_demand_by_zone  (동사_명사_전치사_명사)
→ [B] get_zone_demand_summary   (get_ prefix, 반환값 중심)
→ [C] compute_zone_totals       (compute_, 연산 강조)
```

**규칙**: 선택지 없이 개방형 질문만 하면 안 됨. 최소 3개 대안 + 차이점 명시.

## 6. 설정 파일 구조

```
.claude/
├── settings.json          # Stop hook (정보성 알림)
├── skills/                # 팀 커스텀 skills
│   ├── convention-python/ # Python 코딩 컨벤션
│   ├── convention-commit/ # Git 커밋 규칙
│   ├── convention-pr/     # PR 범위 + 브랜치 협업
│   └── ...               # 총 13개 skills
└── output-styles/
    └── data-driven-minds.md # 출력 스타일 가이드
```

## 7. omc-teams 타임아웃 방지 가이드

omc-teams workers (codex, gemini)는 태스크가 개방형이면 무한 실행될 수 있다.

### 타임아웃 방지 원칙

```bash
# 나쁜 예시 — 개방형 태스크
/omc-teams 2:codex "Python best practice 전부 알려줘"

# 좋은 예시 — 제한된 출력 명시
/omc-teams 2:codex "Python logging best practice 3가지만, 각 50자 이내로 마크다운 목록 출력"
```

### 효과적인 태스크 작성 패턴

1. **출력 형식 명시**: "마크다운 표로", "번호 목록 3개만", "100단어 이내로"
2. **범위 제한**: "이 파일에서만", "이 함수에 대해서만"
3. **즉시 완료 가능한 크기**: 5분 이내 완료 가능한 단위로 분할

### wait 타임아웃 설정

```python
# omc_run_team_wait 호출 시 명시적 타임아웃 설정
omc_run_team_wait(job_id, timeout_ms=120000)  # 2분
# 타임아웃 후 omc_run_team_cleanup으로 정리
omc_run_team_cleanup(job_id)
```

**상황 1**: 28개 best practice 조사 요청 → 타임아웃 → "5가지만, 각 2줄 이내로" 재요청
**상황 2**: 전체 코드베이스 분석 요청 → "이 파일 3개만 분석" 으로 범위 제한

## 참조

- [agents.md](./agents.md) — 에이전트 선택 가이드
- [orchestration.md](./orchestration.md) — ralph/team/ultrawork 비교
- [memory.md](./memory.md) — 세션 간 메모리 관리
- [docs/design/ref/team-operations.md](../../design/ref/team-operations.md) — AW-001~010 규칙
