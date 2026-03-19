#!/usr/bin/env bash
# check-criteria.sh — claude-config 품질 종료 조건 (AW-008)
# 3-agent 합산: Codex(10) + Gemini(10) + Claude(10) = 30개 정량 기준
# 사용법: bash .claude/check-criteria.sh

pass=0; total=0

chk() {
  local id="$1" desc="$2" cmd="$3" op="$4" target="$5"
  total=$((total+1))
  val=$(eval "$cmd" 2>/dev/null || echo "ERR")
  ok=false
  case "$op" in
    ">=") [[ "$val" =~ ^[0-9]+$ ]] && [ "$val" -ge "$target" ] && ok=true ;;
    "=")  [[ "$val" == "$target" ]] && ok=true ;;
    "<=") [[ "$val" =~ ^[0-9]+$ ]] && [ "$val" -le "$target" ] && ok=true ;;
  esac
  $ok && pass=$((pass+1)) && echo "✅ [$id] $desc ($val $op $target)" \
      || echo "❌ [$id] $desc ($val vs $op$target)"
}

echo "=== Codex: 코드/구조 품질 ==="
chk COD-01 "skill 수" "find .claude/skills -name SKILL.md | wc -l | tr -d ' '" ">=" 127
chk COD-02 "name 완비" "find .claude/skills -name SKILL.md -exec grep -l '^name:' {} \; | wc -l | tr -d ' '" "=" 127
chk COD-03 "description 완비" "find .claude/skills -name SKILL.md -exec grep -l '^description:' {} \; | wc -l | tr -d ' '" "=" 127
chk COD-04 "triggers 완비" "find .claude/skills -name SKILL.md -exec grep -l '^triggers:' {} \; | wc -l | tr -d ' '" "=" 127
chk COD-05 "rules 수" "find .claude/rules -name '*.md' | wc -l | tr -d ' '" ">=" 12
chk COD-06 "quality skill 수" "find .claude/skills/quality -name SKILL.md | wc -l | tr -d ' '" ">=" 15
chk COD-07 "reference skill 수" "find .claude/skills/reference -name SKILL.md | wc -l | tr -d ' '" ">=" 40
chk COD-08 "Gotchas 있는 skill" "find .claude/skills -name SKILL.md -exec grep -il 'gotcha' {} \; | wc -l | tr -d ' '" ">=" 50
chk COD-09 "settings.json 유효" "python3 -m json.tool .claude/settings.json >/dev/null 2>&1 && echo 0 || echo 1" "=" 0
chk COD-10 "setup.sh 존재" "test -f .claude/setup.sh && echo 0 || echo 1" "=" 0

echo ""
echo "=== Gemini: 문서화 품질 ==="
chk GEM-01 "CLAUDE.md 존재" "test -f CLAUDE.md && echo 0 || echo 1" "=" 0
chk GEM-02 "CLAUDE.md 섹션 수" "grep -c '^## ' CLAUDE.md" ">=" 8
chk GEM-03 "AW 규칙 참조" "grep -cE 'AW-[0-9]' CLAUDE.md" ">=" 10
chk GEM-04 "ADR 수" "find .claude/docs/adr -name 'ADR-*.md' 2>/dev/null | wc -l | tr -d ' '" ">=" 3
chk GEM-05 "OMC 가이드 수" "find .claude/docs -name 'omc*.md' | wc -l | tr -d ' '" ">=" 2
chk GEM-06 "setup.md 존재" "test -f .claude/docs/setup.md && echo 0 || echo 1" "=" 0
chk GEM-07 "hooks-guide-ko.md 존재" "test -f .claude/docs/hooks-guide-ko.md && echo 0 || echo 1" "=" 0
chk GEM-08 "naming-conventions.md 존재" "test -f .claude/docs/naming-conventions.md && echo 0 || echo 1" "=" 0
chk GEM-09 "배포 가이드 (setup.sh 언급)" "grep -cE 'setup\.sh' CLAUDE.md" ">=" 1
chk GEM-10 "전체 docs md 수" "find .claude/docs -name '*.md' | wc -l | tr -d ' '" ">=" 14

echo ""
echo "=== Claude: 워크플로우 품질 ==="
chk CLD-01 "UserPromptSubmit 훅" "grep -c 'UserPromptSubmit' .claude/settings.json" ">=" 1
chk CLD-02 "haiku AI 분류 훅" "grep -c '\"type\": \"prompt\"' .claude/settings.json" ">=" 1
chk CLD-03 "PreToolUse 차단" "grep -c 'PreToolUse' .claude/settings.json" ">=" 1
chk CLD-04 "PostToolUse 해제" "grep -c 'PostToolUse' .claude/settings.json" ">=" 1
chk CLD-05 "CLAUDE.md ≤250줄" "wc -l < CLAUDE.md | tr -d ' '" "<=" 250
chk CLD-06 "git clean" "git status --short | wc -l | tr -d ' '" "=" 0
chk CLD-07 "ADR ≥3개" "find .claude/docs/adr -name '*.md' 2>/dev/null | wc -l | tr -d ' '" ">=" 3
chk CLD-08 "skill-catalog.md" "test -f .claude/skill-catalog.md && echo 0 || echo 1" "=" 0
chk CLD-09 "hook 문서화" "grep -cE 'TASK-MODE-ACTIVATED|TASK-DETECTED' .claude/docs/hooks-guide-ko.md" ">=" 1
chk CLD-10 "워크플로우 규칙" "grep -cE 'deep-interview|ralplan' CLAUDE.md" ">=" 3

pct=$((pass * 100 / total))
echo ""
echo "=== 총점: $pass/$total ($pct%) ==="
[ "$pct" -ge 90 ] && echo "✅ 종료 조건 달성" || echo "❌ 미달 — 계속 작업"
[ "$pct" -ge 90 ] && exit 0 || exit 1
