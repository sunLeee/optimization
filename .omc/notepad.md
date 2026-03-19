# Notepad
<!-- Auto-managed by OMC. Manual edits preserved in MANUAL section. -->

## Priority Context
<!-- ALWAYS loaded. Keep under 500 chars. Critical discoveries only. -->
## General Rules 구축 — 다음 세션 실행

계획: .omc/plans/general-rules-toolkit-v3.md (v2 함께 참조)
스펙: .omc/specs/deep-interview-general-rules.md
상태: Critic APPROVE → ralph 실행 대기

실행: /ralph max iteration 100
결정: python-patterns deprecated→convention-python(79자), .claude/CLAUDE.md 미생성, pre-commit rev 명시됨

## General Rules 시스템 구축 — 다음 세션 실행 정보

**계획 파일**: .omc/plans/general-rules-toolkit-v3.md (v2 참조 필요)
**스펙 파일**: .omc/specs/deep-interview-general-rules.md
**상태**: Ralplan 합의 완료 (Critic APPROVE) → ralph로 구현 대기

**실행 명령**: /ralph (또는 "ralph로 구현해줘")
**max iteration**: 100
**종료조건**: 20개 (.omc/plans/general-rules-toolkit-v3.md 참조)

**핵심 결정**:
- python-patterns → deprecated, convention-python(79자)으로 대체
- .claude/CLAUDE.md 미생성 → team-operations.md 확장
- pre-commit rev: ruff=v0.4.4, mypy=v1.10.0, bandit=1.7.8
- Stop hook = 정보성 알림 (pre-commit이 실제 강제)

## Working Memory
<!-- Session notes. Auto-pruned after 7 days. -->

## MANUAL
<!-- User content. Never auto-pruned. -->

