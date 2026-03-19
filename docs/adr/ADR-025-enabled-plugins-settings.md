# ADR-025: settings.json에 enabledPlugins 명시

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
`.claude/settings.json`에 `enabledPlugins: { "oh-my-claudecode@omc": true }` 추가.

## 이유
- 전역 설치된 OMC 플러그인을 프로젝트 레벨에서 명시적 활성화
- git subtree 배포 시 다른 프로젝트도 자동으로 OMC 활성화
- Claude Code가 플러그인 인식 명확화

## 결과
- settings.json 최상단에 위치
- clone + `bash .claude/setup.sh` 후 OMC 즉시 사용 가능
