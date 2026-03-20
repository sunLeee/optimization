#!/usr/bin/env bash
# common-criteria.sh — 모든 프로젝트에 적용되는 공통 품질 기준
# 사용법: bash .claude/common-criteria.sh [--score|--counts]

pass=0; total=0

_SCORE_ONLY=false; _COUNTS_ONLY=false
case "$1" in
  --score) _SCORE_ONLY=true ;;
  --counts) _COUNTS_ONLY=true ;;
esac

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

$_SCORE_ONLY && exec 3>&1 1>/dev/null
$_COUNTS_ONLY && exec 3>&1 1>/dev/null

echo "=== Common: 공통 품질 기준 ==="
chk CMN-01 "CLAUDE.md 존재" "test -f CLAUDE.md && echo 0 || echo 1" "=" "0"
chk CMN-02 "settings.json 유효" "python3 -m json.tool .claude/settings.json >/dev/null 2>&1 && echo 0 || echo 1" "=" "0"
chk CMN-03 ".claude/ 구조" "test -d .claude/docs && echo 0 || echo 1" "=" "0"
chk CMN-04 "ADR 존재" "ls .claude/docs/adr/*.md 2>/dev/null | wc -l | tr -d ' '" ">=" "1"

pct=$((pass * 100 / (total > 0 ? total : 1)))

if $_SCORE_ONLY; then
  exec 1>&3 3>&-
  echo "$pct"
  exit 0
fi

if $_COUNTS_ONLY; then
  exec 1>&3 3>&-
  echo "$pass $total"
  exit 0
fi

echo ""
echo "=== 공통 기준: $pass/$total ($pct%) ==="
[ "$pct" -ge 90 ] && echo "✅ 공통 기준 달성" || echo "❌ 공통 기준 미달"
[ "$pct" -ge 90 ] && exit 0 || exit 1
