# ADR-043: common-criteria.sh + project-criteria.sh 분리 패턴

- **상태**: Accepted
- **날짜**: 2026-03-20
- **범용 여부**: ✅ 모든 프로젝트 적용 가능

## 맥락

claude-config의 check-criteria.sh를 다른 프로젝트(optimization 등)에 배포하면
claude-config 전용 항목(PYQ, CLD-10 ralplan 참조 등)이 강제 적용되어
Stop hook이 exit 2를 반복하는 문제가 발생했다.

setup.sh에도 "claude-config" 하드코딩이 있어 다른 프로젝트에서 혼란을 야기했다.

## 결정

품질 체크 스크립트를 두 계층으로 분리한다:

1. `common-criteria.sh` — 모든 프로젝트에 적용되는 미니멀 공통 기준 (4개)
2. `.claude/project-criteria.sh` — 각 프로젝트의 특화 기준 (선택, 없으면 skip)

check-criteria.sh는 orchestrator 역할로, common + project(있으면)를 순차 실행한다.

## 이유

- **DRY**: 공통 기준을 한 파일로 관리
- **SRP**: 프로젝트 특화 기준은 각 프로젝트가 책임
- **YAGNI**: project-criteria.sh가 없으면 common만 실행 — 복잡도 최소화
- **Gall's Law**: 단순한 common(4개)에서 시작, 필요시 project-criteria.sh 추가

## 대안 검토

| 대안 | 거부 이유 |
|------|----------|
| 단일 파일 + 레포 감지 로직 | 레포 경로 기반 분기 → 이식성 낮음, 새 레포마다 수정 필요 |
| 환경변수 기반 섹션 선택 | 팀원이 env 설정 필요 → 마찰 증가 |
| project-type 태그 (CLAUDE.md 수정) | 기존 CLAUDE.md 수정 필요, 오버헤드 |

## 결과

- `common-criteria.sh`: 4개 항목, --score/--counts 플래그 지원
- `.claude/project-criteria.sh`: 각 프로젝트에서 생성 (선택사항)
- 모든 프로젝트: Stop hook이 common-criteria.sh 점수로 gate
- claude-config: 기존 check-criteria.sh(35개) 유지 (프로젝트 기준 자체)

## Gotchas

- common-criteria.sh에 git clean 체크 금지: Stop hook 직전은 항상 dirty
- project-criteria.sh 없으면 common(4개) 100% 달성이 90% 기준

## 참조

- `check-criteria.sh` (orchestrator)
- `common-criteria.sh` (공통 기준)
- `.claude/docs/criteria-pattern.md` (사용 가이드)
