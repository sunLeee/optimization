# 메모리 & 컨텍스트 관리 가이드

> 참조: docs/ref/bestpractice/claude-code-rule-convention.md (Practice 19~21)
> 참조: .omc/notepad.md, .omc/project-memory.json

## 1. 세션 간 기억 유지: 세션 로그 패턴

세션 종료 전 현재 상태를 파일로 저장하고, 다음 세션 시작 시 해당 파일을 컨텍스트로 제공한다.

```bash
# 세션 로그 저장 위치
.omc/sessions/YYYY-MM-DD-{topic}.md

# 다음 세션에서 로딩
claude --system-prompt "$(cat .omc/sessions/2026-03-18-demand-analysis.md)"
```

**세션 로그 포맷**:
```markdown
## 세션 요약: {날짜} {주제}

### 완료된 작업
- [x] demand_analyst에 집계 지표 추가
- [x] unit test 작성 (15개 통과)

### 미완료 작업
- [ ] integration test 작성
- [ ] CLI runner 업데이트

### 관련 파일
- agents/demand_analyst/tools/aggregation.py (수정됨)
- libs/utils/src/utils/aggregation_helpers.py (신규)

### 다음 세션 액션
1. integration test 작성: `uv run pytest -m integration`
2. runner 업데이트: apps/cli_runner/runners/hchat_demand_runner.py
```

**상황 1**: context limit 도달 → 세션 로그 저장 → 새 대화에서 파일 경로 제공
**상황 2**: 다음 날 작업 재개 → 세션 로그로 어제 작업 즉시 파악

## 2. OMC 기본 제공 메모리 도구

omc는 notepad와 project-memory를 기본 제공한다.

```bash
# Notepad: 단기 작업 메모 (7일 자동 삭제)
notepad_write_working "zone_id=102는 해외 지역 (boundary/grid 매핑 없음이 정상)"
notepad_read  # 전체 읽기

# Project Memory: 영구 아키텍처 결정 기록
project_memory_add_note "build" "uv sync 없이 pip install 사용 시 workspace 의존성 실패"
project_memory_add_directive "항상 uv run 사용, python 직접 실행 금지"
project_memory_read  # 전체 읽기
```

**이 프로젝트 저장 위치**:
- `.omc/notepad.md` — 단기 메모
- `.omc/project-memory.json` — 영구 기록

**상황 1**: 반복적인 실수 발견 → `project_memory_add_directive`로 영구 등록
**상황 2**: 특정 zone_id 특성 발견 → `notepad_write_working`으로 현재 작업에만 기록

## 3. Hook 체인 설정 방법 (PreCompact / SessionStart / Stop)

**현재 상태**: `.claude/settings.json`에 Stop hook만 설정됨 (정보성 알림)
**목표 설정**: PreCompact → SessionStart → Stop 3단계 체인 (선택적 추가)

```json
// 현재 설정 (.claude/settings.json)
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "echo '[Stop Hook 알림] /check-python-style 실행 권장'"
      }]
    }]
  }
}

// 목표 설정 (세션 기억 체인 — 선택적 추가)
{
  "hooks": {
    "PreCompact": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "~/.claude/hooks/pre-compact.sh"}]
    }],
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "~/.claude/hooks/session-start.sh"}]
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{"type": "command", "command": "~/.claude/hooks/session-end.sh"}]
    }]
  }
}
```

**주의**: PreCompact와 SessionStart는 이 프로젝트에 현재 설정되어 있지 않음. 위는 확장 방법 안내.

**상황 1**: 긴 개발 세션에서 context limit 접근 → PreCompact가 핵심 내용 먼저 저장
**상황 2**: 다음 날 작업 재개 → SessionStart가 어제 세션 요약 자동 로딩

## 4. Strategic Compact

자동 compact 대신 논리적 단계마다 수동 compact하여 중요한 컨텍스트를 보존한다.

**자동 compact의 문제**: 작업 중간에 발생하여 진행 중인 컨텍스트 손실 가능
**전략적 compact 시점**:
- 탐색 완료 → 구현 시작 전
- 하나의 마일스톤 완료 → 다음 마일스톤 시작 전
- 50 tool call 마다 (affaan-m 권장값)

```bash
# 50 tool call 알림 hook (PreToolUse에 등록)
COUNTER_FILE="/tmp/claude-tool-count-$$"
count=$(($(cat "$COUNTER_FILE" 2>/dev/null || echo 0) + 1))
echo "$count" > "$COUNTER_FILE"
[ "$count" -eq 50 ] && echo "[StrategicCompact] 단계 전환 시 /compact 고려" >&2
```

**상황 1**: 코드 탐색 30 tool call → 구현 시작 전 compact → 구현에 필요한 정보만 남김
**상황 2**: 자동 compact 비활성화 (Claude Code 설정) → 수동으로 논리적 단계마다 실행

## 5. Project Memory로 세션 간 지식 유지

```bash
# 중요한 아키텍처 발견 즉시 기록
project_memory_add_note "architecture" "cli_runner/config.py가 모든 파일 경로의 SSOT"
project_memory_add_note "build" "uv sync 없으면 workspace 의존성 실패"

# 다음 세션에서 즉시 참조
project_memory_read section="notes"
```

**이 프로젝트 기존 메모리**:
```bash
cat .omc/project-memory.json  # 현재 저장된 내용 확인
```

**상황 1**: 특수한 에러 해결 방법 발견 → 즉시 project_memory_add_note로 기록
**상황 2**: 새 세션 시작 → project_memory_read로 프로젝트 컨텍스트 즉시 복원

## 참조

- [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) — Practice 19~21
- `.omc/notepad.md` — 단기 메모
- `.omc/project-memory.json` — 영구 기록
