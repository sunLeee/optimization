# Gemini 에이전트 — 문서화 품질 기준 (pane 3)

문서의 완성도와 링크 무결성을 측정하는 10개 기준.

## 기준 목록

| ID | 명령 | 기준 | 설명 |
|----|------|------|------|
| GEM-01 | `test -f CLAUDE.md && echo 0 \|\| echo 1` | = 0 | CLAUDE.md 존재 |
| GEM-02 | `grep -c '^## ' CLAUDE.md` | ≥ 8 | CLAUDE.md 섹션 수 |
| GEM-03 | `grep -c 'AW-' CLAUDE.md` | ≥ 10 | AW 규칙 참조 횟수 |
| GEM-04 | `find .claude/docs/adr -name 'ADR-*.md' \| wc -l` | ≥ 3 | ADR 파일 수 |
| GEM-05 | `find .claude/docs -name 'omc*.md' \| wc -l` | ≥ 2 | OMC 가이드 문서 수 |
| GEM-06 | `test -f .claude/docs/setup.md && echo 0 \|\| echo 1` | = 0 | setup.md 존재 |
| GEM-07 | `test -f .claude/docs/hooks-guide-ko.md && echo 0 \|\| echo 1` | = 0 | hooks 가이드 존재 |
| GEM-08 | `test -f .claude/docs/naming-conventions.md && echo 0 \|\| echo 1` | = 0 | 명명 규칙 문서 존재 |
| GEM-09 | `grep -c 'install.sh\|subtree' CLAUDE.md` | ≥ 2 | 배포 방법 언급 횟수 |
| GEM-10 | `find .claude/docs -name '*.md' \| wc -l` | ≥ 14 | 전체 docs md 수 |
