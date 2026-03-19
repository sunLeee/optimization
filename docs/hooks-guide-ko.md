# Claude Code 훅 사용 가이드 (한국어)

> 이 파일은 CLAUDE.md § TASK-MODE-ACTIVATED 사용법에서 참조됨
> 원본 설정: [.claude/settings.json](../settings.json)

---

## TASK-MODE-ACTIVATED

### 감지 메커니즘

UserPromptSubmit 훅이 사용자 프롬프트를 **정규식으로 스캔**한다.

```
감지 대상 키워드: 구현|implement|작성해|만들어|추가해|수정해|fix|add|create|build|refactor|개발|설계해|생성
제외 키워드:     공유|알려줘|알고싶|현황|진행상황|설명해|언제|얼마나|어떻게|어디|뭐야|무엇|왜|상태
```

**중요:** AI가 판단하는 것이 아니다. 단순 문자열 패턴 매칭이다.
- "omc-teams가 판단하는가?" → **아니다**, 정규식이 판단한다
- "어떤 task인지 AI가 분석하는가?" → **아니다**, 키워드 존재 여부만 확인한다

---

### 발동 시 워크플로우 (순서 엄수)

```
STEP 1: omc-teams 사전조사 (AW-003 — deep-interview 전 필수)
   └─ 사전조사 없이 deep-interview 시작 금지

STEP 2: Skill oh-my-claudecode:ultrawork (병렬 실행 엔진 준비)

STEP 3: Skill oh-my-claudecode:deep-interview (사전조사 결과 컨텍스트 포함)
   └─ 모호성 5% 미만 달성까지 계속
   └─ 5분 무응답 = skip 판단 (omc-teams 합의 후)

STEP 4: Skill oh-my-claudecode:ralplan (Planner→Architect→Critic 합의)

STEP 5: ralph 구현 (max 100 iterations — AW-007)
```

---

### 차단 메커니즘

`TASK-MODE-ACTIVATED` 발동 시 마커 파일 생성:
```bash
/tmp/.claude-task-{프로젝트해시}.lock
```

**PreToolUse 훅**이 `Write`, `Edit`, `NotebookEdit` 도구 실행 전 마커 확인:
- 마커 있음 → `[BLOCKED: DEEP-INTERVIEW REQUIRED]` 출력 + exit 1 (도구 실행 차단)
- 마커 없음 → 정상 실행

**Bash, Read, Glob, Grep 도구는 차단하지 않는다** (탐색/확인은 허용).

---

### 차단 해제

**자동 해제:** deep-interview가 완료되면 PostToolUse 훅이 마커 삭제:
```bash
# deep-interview state 파일 확인
.omc/state/sessions/{id}/deep-interview-state.json → active: false
→ /tmp/.claude-task-{hash}.lock 자동 삭제
```

**수동 해제 (긴급):**
```bash
rm /tmp/.claude-task-*.lock
```

---

### Magic Keyword 감지 표시

훅 발동 시 감지된 키워드가 출력에 표시된다:
```
[TASK-DETECTED] 감지된 키워드: "구현"
```

OMC 전역 훅이 추가 magic keyword 감지:
- `RALPH` → ralph 루프 즉시 발동
- `ULTRAWORK` → ultrawork 병렬 엔진 발동
- `RALPLAN` → ralplan 합의 계획 발동
- `TEAM` → team 오케스트레이션 발동

---

## Stop Hook

Claude Code가 응답을 완료할 때마다 실행:
```
[Stop Hook] 코드 작성 완료. /check-python-style 실행 권장
```

- check-criteria.sh 점수 < 90% 시 exit 2 (강제 차단). `.claude/check-criteria.sh` 없으면 정보성 알림만.
- 실제 강제는 pre-commit (`ruff` + `mypy`) — AW-010

---

## PreToolUse Hook

```json
PreToolUse(Write/Edit) → 마커 파일 확인 → 없으면 차단
```

```json
PostToolUse(Skill) → deep-interview 완료 여부 확인 → 마커 삭제
```

---

## 훅 우선순위

```
1. 사용자 프롬프트 제출
2. UserPromptSubmit 훅 (정규식 감지)
   → TASK-DETECTED: 마커 생성 + 워크플로우 지시
3. Claude 응답
4. 도구 실행 시도
5. PreToolUse 훅 (Write/Edit 차단 여부 확인)
6. 도구 실행 완료
7. PostToolUse 훅 (deep-interview 완료 시 마커 해제)
8. Claude 응답 완료
9. Stop 훅
```

---

## 참조

- [settings.json](../settings.json) — 실제 훅 설정
- [omc.md](./omc.md) — OMC 워크플로우
- [CLAUDE.md](../../CLAUDE.md) § TASK-MODE-ACTIVATED
