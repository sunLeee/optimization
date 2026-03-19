# Codex 에이전트 — 코드/구조 품질 기준 (pane 2)

코드베이스 구조의 완성도를 측정하는 10개 기준.

## 기준 목록

| ID | 명령 | 기준 | 설명 |
|----|------|------|------|
| COD-01 | `find .claude/skills -name SKILL.md \| wc -l` | ≥ 127 | 전체 skill 수 |
| COD-02 | `find .claude/skills -name SKILL.md -exec grep -l '^name:' {} \; \| wc -l` | = 127 | name 필드 완비 |
| COD-03 | `find .claude/skills -name SKILL.md -exec grep -l '^description:' {} \; \| wc -l` | = 127 | description 완비 |
| COD-04 | `find .claude/skills -name SKILL.md -exec grep -l '^triggers:' {} \; \| wc -l` | = 127 | triggers 완비 |
| COD-05 | `find .claude/rules -name '*.md' \| wc -l` | ≥ 12 | rules 파일 수 |
| COD-06 | `find .claude/skills/quality -name SKILL.md \| wc -l` | ≥ 15 | quality 카테고리 skill 수 |
| COD-07 | `find .claude/skills/reference -name SKILL.md \| wc -l` | ≥ 40 | reference 카테고리 skill 수 |
| COD-08 | `find .claude/skills -name SKILL.md -exec grep -il 'gotcha\|실패 포인트' {} \; \| wc -l` | ≥ 50 | Gotchas 있는 skill 수 |
| COD-09 | `python3 -m json.tool .claude/settings.json > /dev/null 2>&1 && echo 0 \|\| echo 1` | = 0 | settings.json JSON 유효성 |
| COD-10 | `test -f .claude/setup.sh && echo 0 \|\| echo 1` | = 0 | setup.sh 존재 |
