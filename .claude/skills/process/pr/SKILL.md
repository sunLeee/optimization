---
name: convention-pr
triggers:
  - "convention pr"
description: PR 범위, 설계문서 우선, 브랜치 협업 규칙. Rule of Small + Rule of Reversibility.
user-invocable: true
---

# convention-pr

## Rule of Small

하나의 PR = 하나의 설계 결정.
코드 변경량이 아니라 설계 결정의 수로 PR 범위를 정의한다.

**상황 1**: 파일 경로 패턴 변경 + column 네이밍 규칙 변경을 한 PR에 → 분리 필요
**상황 2**: 큰 기능: 설계문서 PR → code 구현 PR로 순서 분리

## 설계문서 먼저 (AW-006)

코드 PR 전 설계문서 PR 통과 필수.

PR description 필수 항목:
1. **1문장 요약**: 이 PR이 하는 설계 결정
2. **설계문서 링크**: CLAUDE.md 또는 docs/design/ 경로
3. **Breaking Changes**: 있으면 명시

**상황 1**: 코드만 수정한 PR에 설계문서 링크 없음 → merge 거절
**상황 2**: 설계문서 PR이 먼저 merge된 후 코드 PR 생성 → 올바른 순서

## 브랜치 협업 규칙

- 하나의 branch = 하나의 작업 범위
- 타인 branch가 수정 중인 파일 → 건드리지 않는다
- branch 시작 전 GitHub open PR 확인 → 충돌 파일 파악
- 이 프로젝트 현재 branch: `shucle-ai-agent-general-rules` (general rules 파일만)

**상황 1**: 팀원 A가 `libs/CLAUDE.md` 수정 중 → 내 PR에서 그 파일 편집 금지
**상황 2**: 범위 겹치면 → Slack/PR comment로 우선순위 협의

## check-design-doc 실행

PR 제출 전 `/check-design-doc` skill로 코드-설계 일치 확인.

**상황 1**: function이 설계문서의 signature와 다름 → 수정 후 PR
**상황 2**: 새 function이 CLAUDE.md 패턴 위반 → 수정 후 PR

## Gotchas (실패 포인트)

- 하나의 PR에 여러 설계 결정 혼재 금지 — 리뷰 어려움
- 타인 branch 파일 수정 시 즉시 conflict 발생 — 반드시 확인
- PR 제목에 이슈 번호 `#숫자` 포함 시 자동 cross-reference 생성
