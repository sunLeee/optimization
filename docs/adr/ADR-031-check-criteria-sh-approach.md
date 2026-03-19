# ADR-031: check-criteria.sh + 30개 정량 기준으로 종료 조건 관리

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
ralph 루프의 종료 조건을 shell script(check-criteria.sh)로 구현. 3-agent 각 10개 = 30개 정량 기준.

## 이유
- shell script: 빠르고 신뢰할 수 있는 검증 (grep/wc 기반)
- 30개 기준: Codex(구조)+Gemini(문서)+Claude(워크플로우) 관점 분리
- 90% 달성 시 종료 → exit 0, 미달 시 exit 1 → ralph 계속

## 결과
- `.claude/check-criteria.sh` 생성
- `.omc/research/criteria-*.md`에 각 에이전트 기준 문서화
