# Claude 에이전트 — 워크플로우 품질 기준 (pane 4)

OMC 워크플로우, AW 규칙 반영, hook 설정의 완성도를 측정하는 10개 기준.

## 기준 목록

| ID | 명령 | 기준 | 설명 |
|----|------|------|------|
| CLD-01 | `grep -c 'UserPromptSubmit' .claude/settings.json` | ≥ 1 | UserPromptSubmit 훅 존재 |
| CLD-02 | `grep -c '"type": "prompt"' .claude/settings.json` | ≥ 1 | haiku AI 분류 훅 존재 |
| CLD-03 | `grep -c 'PreToolUse' .claude/settings.json` | ≥ 1 | PreToolUse 차단 훅 존재 |
| CLD-04 | `grep -c 'PostToolUse' .claude/settings.json` | ≥ 1 | PostToolUse 해제 훅 존재 |
| CLD-05 | `wc -l < CLAUDE.md` | ≤ 250 | CLAUDE.md 줄 수 과도하지 않음 |
| CLD-06 | `git status --short \| wc -l` | = 0 | 미commit 변경 없음 |
| CLD-07 | `find .claude/docs/adr -name '*.md' \| wc -l` | ≥ 3 | 설계 근거 ADR 수 |
| CLD-08 | `test -f .claude/skill-catalog.md && echo 0 \|\| echo 1` | = 0 | skill-catalog 존재 |
| CLD-09 | `grep -c 'TASK-MODE-ACTIVATED\|TASK-DETECTED' .claude/docs/hooks-guide-ko.md` | ≥ 1 | hook 사용법 문서화 |
| CLD-10 | `grep -c 'deep-interview\|ralplan' CLAUDE.md` | ≥ 3 | 워크플로우 규칙 반영 |
