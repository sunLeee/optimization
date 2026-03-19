# claude-config 품질 종료 조건 생성 요청

## 목적
claude-config 레포지토리의 완성도를 grep/wc 명령어로 측정 가능한 정량적 기준 10개 이상 생성.

## 조건
- 모든 기준은 bash 명령어 하나로 측정 가능해야 함
- 기준값은 "≥", "=", "≤" 중 하나로 표현
- 추상적 조건 ("구현 완료" 등) 금지
- 워킹 디렉토리: /Users/hmc123/Documents/claude-config

## 각 에이전트의 관점
- pane 2 (codex): 코드/구조 품질 관점 — skill 파일 구조, frontmatter 완비
- pane 3 (gemini): 문서화 품질 관점 — docs 커버리지, ADR, 링크 완비
- pane 4 (claude): 워크플로우 품질 관점 — hook 설정, AW 규칙 반영

## 출력 형식
각 기준마다:
```
ID: C1 (에이전트-숫자)
명령: find .claude/skills -name SKILL.md | wc -l
기준: ≥ 127
설명: 전체 skill 수 127개 유지
```
