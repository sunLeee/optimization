# ADR-019: PreToolUse로 deep-interview 완료 전 Write/Edit 차단

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
태스크 감지 시 마커 파일 생성 → PreToolUse(Write/Edit) 훅이 마커 확인 → 차단.
deep-interview 완료 시 PostToolUse(Skill) 훅이 마커 삭제.

## 이유
- "그냥 해줘" 우회 방지 → deep-interview 강제 실행
- Claude가 hook 지시를 무시해도 실제 파일 수정 차단
- 마커 = `/tmp/.claude-task-{hash}.lock`

## Gotchas
- Bash/Read/Glob은 차단 안 함 (탐색/확인 허용)
- 긴급 해제: `rm /tmp/.claude-task-*.lock`
- deep-interview state 파일이 없으면 마커 자동 유지
