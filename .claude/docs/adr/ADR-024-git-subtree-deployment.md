# ADR-024: git subtree로 .claude/ 배포

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`sunLeee/claude-config`의 `.claude/`를 다른 프로젝트에 `git subtree add --prefix=.claude`로 배포.

## 이유
- git submodule: `--recursive` clone 필요 → 복잡
- 심볼릭 링크: CI/CD 불가
- git subtree: 히스토리 통합, 일반 `git clone`으로 사용 가능
- 배포 후 업데이트: `git subtree pull`

## Gotchas
- .claude/settings.json merge 충돌 → `.gitattributes merge=ours`로 해결
- 양방향 sync: `git subtree push`로 역방향 가능

## 결과
- `how_to_subtree_in_git.md` 가이드 작성
