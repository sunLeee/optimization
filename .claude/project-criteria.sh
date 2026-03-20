#!/usr/bin/env bash
# project-criteria.sh — 프로젝트 특화 품질 기준 (선택사항)
# 이 파일이 존재하면 check-criteria.sh가 자동으로 실행함
# 사용법: bash .claude/project-criteria.sh [--counts]
# --counts 플래그: "pass total" 형식으로 출력 (orchestrator 합산용)

pass=0; total=0
_COUNTS_ONLY=false
[ "$1" = "--counts" ] && _COUNTS_ONLY=true

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

# 여기에 프로젝트 특화 체크 추가
# 예시:
# chk PRJ-01 "프로젝트 README" "test -f README.md && echo 0 || echo 1" "=" "0"

if $_COUNTS_ONLY; then
  echo "$pass $total"
  exit 0
fi

echo "=== 프로젝트 기준: $pass/$total ==="
