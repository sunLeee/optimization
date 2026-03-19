# 에이전트 오케스트레이션 가이드

> 참조: docs/ref/bestpractice/claude-code-rule-convention.md (Practice 6~8)
> 참조: docs/design/ref/team-operations.md (AW-001: 모델 선택, AW-002: 3-agent 조사)

## 1. 사용 가능한 에이전트 목록

OMC에서 `oh-my-claudecode:` prefix로 호출 가능한 에이전트.

| 에이전트 | 목적 | 언제 사용 |
|---------|------|---------|
| `explore` | 코드베이스 탐색, symbol/파일 매핑 | 작업 시작 전 컨텍스트 파악 |
| `planner` | 태스크 순서화, 구현 계획 | 복잡한 기능, 리팩토링 |
| `architect` | 시스템 설계, 경계 정의 | 아키텍처 결정, ADR 작성 |
| `executor` | 코드 구현, 리팩토링 | 표준 구현 작업 |
| `deep-executor` | 복잡한 자율 목표 작업 | 여러 파일에 걸친 복잡한 구현 |
| `debugger` | 근본 원인 분석 | 버그 수정, 회귀 격리 |
| `verifier` | 완료 증거 검증 | 구현 후 검증 |
| `code-reviewer` | 포괄적 코드 리뷰 | PR 전 최종 리뷰 |
| `security-reviewer` | 보안 취약점 탐지 | 인증/암호화 변경 시 |
| `test-engineer` | 테스트 전략, coverage | 새 기능 테스트 작성 |
| `build-fixer` | 빌드/타입 오류 수정 | CI 실패, import 오류 |
| `document-specialist` | 외부 문서 조회 | SDK 사용법, API 문서 |
| `writer` | 문서 작성 | README, docs 업데이트 |

## 2. 에이전트 역할 분리 원칙 (Practice 6)

하나의 에이전트에 탐색과 구현을 동시에 맡기지 않는다. context 오염 방지.

| 역할 | 에이전트 | 출력 |
|------|---------|------|
| 탐색 | `explore` (haiku) | 파일 경로 목록 |
| 계획 | `planner` (sonnet) | 구현 계획 |
| 구현 | `executor` (sonnet) | 코드 변경 |
| 검증 | `verifier` (sonnet) | 통과/실패 |

**상황 1**: bug 수정 → `debugger`로 원인 파악 → `executor`로 수정 → `verifier`로 통과 확인
**상황 2**: 신기능 → `explore`로 파일 탐색 → `planner`로 계획 → `executor`로 구현

## 3. 에이전트 model 크기 매칭 (Practice 7)

내부망 제한으로 opus 사용 불가. sonnet이 최상위 모델.

| 작업 | 권장 모델 | 예시 |
|------|---------|------|
| 단순 탐색, 파일 찾기 | haiku | `explore haiku` |
| 표준 구현, 리뷰 | sonnet | `executor sonnet` |
| 아키텍처, 복잡 분석 | sonnet (opus 대체) | `architect sonnet` |

**상황 1**: 파일 위치 탐색 → haiku (5배 저렴, 충분)
**상황 2**: 보안 리뷰 → sonnet (내부망에서 opus 불가, AW-001)

## 4. 전문 에이전트 chain 구성 (Practice 8)

새 SDK/API 사용 전 `document-specialist`로 공식 문서를 먼저 조회한다. hallucination 방지.

```
document-specialist (공식 문서 조회) → executor (구현) → verifier (검증)
```

**상황 1**: Google ADK 새 기능 → `document-specialist`로 공식 API 조회 → `executor`로 구현
**상황 2**: pandas 버전 업 → `document-specialist`로 변경사항 조회 → `build-fixer`로 수정

## 5. 즉시 사용 원칙 (사용자 프롬프트 불필요)

특정 상황에서 에이전트를 자동으로 투입한다. 사용자가 명시적으로 요청하지 않아도.

| 상황 | 투입 에이전트 |
|------|------------|
| 복잡한 기능 요청 | `planner` 먼저 |
| 코드 작성/수정 후 | `code-reviewer` |
| 버그 수정 | `debugger` 먼저 |
| 아키텍처 결정 | `architect` |
| SDK/API 첫 사용 | `document-specialist` 먼저 |

**상황 1**: "demand 분석에 새 집계 지표 추가"라고 하면 → `planner`로 계획 → `executor`로 구현 → `verifier`로 검증
**상황 2**: API 문서가 없는 신규 라이브러리 사용 → `document-specialist`로 조회 후 `executor`에 전달

## 3. 모델 티어 선택 기준

| 티어 | 모델 | 사용 |
|------|------|------|
| LOW | haiku | 단순 탐색, 반복 작업, 파일 검색 |
| MEDIUM | sonnet | 표준 구현, 코드 리뷰, 테스트 작성 |
| HIGH | opus | 복잡한 분석, 아키텍처, 보안 리뷰 |

**내부망 주의**: opus 접근 불가 → sonnet으로 대체 (AW-001 참조)

```python
# 좋은 예시: 티어 명시
Task(subagent_type="oh-my-claudecode:explore", model="haiku", prompt="파일 위치 찾기")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="함수 구현")

# 나쁜 예시: 모든 작업에 opus 사용 → 비용 낭비
```

**상황 1**: 30개 파일 탐색 → `explore haiku` (cheap + fast)
**상황 2**: 보안 관련 변경 → `security-reviewer opus` (thorough)

## 4. 병렬 실행 원칙

독립적인 작업은 항상 병렬로 실행한다.

```python
# 좋은 예시: 3개 독립 작업 동시 실행
Task(executor, model="sonnet", prompt="libs/data_processing 유닛 테스트 작성")
Task(executor, model="sonnet", prompt="libs/preprocessing 유닛 테스트 작성")
Task(executor, model="sonnet", prompt="libs/utils 유닛 테스트 작성")

# 나쁜 예시: 순차 실행 (불필요한 지연)
result1 = Task(executor, "libs/data_processing 테스트")
# 기다린 후
result2 = Task(executor, "libs/preprocessing 테스트")
```

**상황 1**: 여러 agent 패키지에 테스트 추가 → 모두 병렬 실행 (의존성 없음)
**상황 2**: 공통 타입 먼저 수정 → 소비자 패키지는 그 다음 실행 (의존성 있음)

## 5. Iterative Retrieval Pattern

Sub-agent 결과를 그대로 수락하지 않는다. orchestrator가 평가 후 follow-up.

```
orchestrator → sub-agent: 쿼리 + 목적 컨텍스트
sub-agent → orchestrator: 요약 반환
orchestrator: 충분한가? 평가
  → 부족: follow-up 질문 (최대 3 cycles)
  → 충분: 수락
```

**핵심**: 쿼리뿐만 아니라 "왜 이 정보가 필요한가"도 sub-agent에 전달.

**상황 1**: `explore`가 30개 파일 반환 → "수정 대상 5개만 보내줘"로 follow-up
**상황 2**: sub-agent 요약에 핵심 내용 누락 → "security impact도 포함해"로 추가 조회

## 6. 3-agent 조사 패턴 (AW-002)

기술 결정 시 claude + codex + gemini 병렬 조사 후 다수결 또는 사용자 결정.

```bash
# omc-teams로 병렬 조사
/oh-my-claudecode:omc-teams 2:codex "Python async best practice for {topic}"
/oh-my-claudecode:omc-teams 2:gemini "Python async best practice for {topic}"
# 결과를 Claude가 종합하여 (Recommended) 명시
```

**상황 1**: 새 라이브러리 선택 → 3-agent 조사 후 pros/cons 비교 → AskUserQuestion
**상황 2**: 코딩 패턴 결정 → 3-agent 일치 시 즉시 적용, 불일치 시 사용자 결정

## omc-teams: CLI Worker 에이전트 팀

> 상세 사용법: [setup.md](./setup.md) § 3. omc-teams 프롬프트 전달 방식

omc-teams는 **Claude Code 네이티브 Team (SendMessage 기반)과 다르다.**
tmux pane에 독립 CLI 프로세스(codex, gemini)를 실행하는 방식이다.

### 동작 방식

```
Claude (Lead, main pane)
  │
  ├─ tmux pane 2: codex CLI  ← 독립 프로세스
  ├─ tmux pane 3: gemini CLI ← 독립 프로세스
  └─ 결과: .omc/research/*.md 파일로 수집
```

### 프롬프트 전달 패턴

workers에게 프롬프트를 전달할 때 `@파일경로` 또는 `$(cat 파일)` 형태를 사용한다:

```bash
# 방식 1: 인라인 (짧은 경우)
omc-teams 2:codex "Python best practice for async 조사" \
           3:gemini "Python best practice for async 조사"

# 방식 2: 파일 기반 (@파일 참조) — 긴 프롬프트 권장
cat > .omc/research/query.md << 'EOF'
조사 주제: Python async best practice
참고: @.claude/docs/team-operations.md  ← 이렇게 파일 내용 참조 가능
요청 형식: pros/cons + 권장사항
EOF

omc-teams 2:codex "$(cat .omc/research/query.md)" \
           3:gemini "$(cat .omc/research/query.md)"

# 방식 3: 결과를 파일로 저장하도록 지시
omc-teams 2:codex "조사 후 .omc/research/result-codex.md에 저장하라: {주제}" \
           3:gemini "조사 후 .omc/research/result-gemini.md에 저장하라: {주제}"
```

### @파일 참조란?

Claude Code에서 `@파일경로`는 해당 파일의 내용을 프롬프트에 인라인으로 포함시킨다.

```
@.claude/docs/team-operations.md   ← AW 규칙 전체 내용이 프롬프트에 포함됨
@.claude/skills/reference/python/SKILL.md ← skill 내용이 포함됨
```

workers에게 이 형식으로 컨텍스트를 전달하면 특정 파일의 내용을 기반으로 분석할 수 있다.

### Claude Team (SendMessage) vs omc-teams 비교

| 항목 | Claude Team | omc-teams |
|------|-------------|-----------|
| 통신 방식 | SendMessage (TaskList, TaskUpdate) | 파일 기반 I/O |
| 에이전트 유형 | Claude Code 에이전트 | Codex CLI, Gemini CLI |
| 적합한 용도 | 코드 구현, 반복 작업 | 사전조사, 다중 모델 의견 수집 |
| 결과 수집 | 자동 (TaskUpdate) | 수동 (파일 읽기) |

### 실전 사용 패턴

```bash
# AskUserQuestion 전 사전조사 (AW-004)
# Step 1: 쿼리 파일 작성
cat > .omc/research/query-$(date +%Y%m%d-%H%M).md << 'EOF'
모델: gemini-2.0-flash-thinking-exp
주제: {조사 주제}
요청: 10개 이상 정량적 기준 도출
참고 컨텍스트: @.claude/docs/team-operations.md
출력 형식: markdown table
EOF

# Step 2: workers 실행
omc-teams 2:codex "$(cat .omc/research/query-latest.md)" \
           3:gemini "$(cat .omc/research/query-latest.md)"

# Step 3: 결과 확인 (tmux pane에서 출력되거나 파일로 저장)
cat .omc/research/result-*.md
```

## 참조

- [setup.md](./setup.md) § 2. tmux 설정, § 3. omc-teams 프롬프트 전달 방식
- [docs/design/ref/team-operations.md](../../design/ref/team-operations.md) — AW-001: 모델 선택, AW-002: 3-agent 조사
- [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) — Practice 6~8
