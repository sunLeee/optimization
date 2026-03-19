# ADR-013: 외부 리포 직접 Push 금지

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
현재 작업 중인 리포 외 리포에는 PR 없이 직접 push 절대 금지.
force push는 명시적 사용자 요청 없으면 금지.

## 이유
- 팀 리뷰 프로세스 보호
- 실수로 다른 팀 브랜치 덮어쓰기 방지
- `#숫자` cross-reference 오발생 방지

## Gotchas
- `git push --force-with-lease`도 명시적 요청 없으면 금지
- 이슈 참조 `#숫자` → GitHub 정책상 cross-reference 삭제 불가
