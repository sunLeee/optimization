#!/usr/bin/env bash
# check-criteria.sh — 품질 종료 조건 오케스트레이터
# common-criteria.sh + project-criteria.sh(있으면) 실행
# 사용법: bash .claude/check-criteria.sh [--score]

_SCORE_ONLY=false
[ "$1" = "--score" ] && _SCORE_ONLY=true

COMMON=".claude/common-criteria.sh"
PROJECT=".claude/project-criteria.sh"

# common-criteria.sh 실행하여 pass/total 획득
if [ -f "$COMMON" ]; then
  c_out=$(bash "$COMMON" --counts 2>/dev/null)
  c_pass=$(echo "$c_out" | awk '{print $1}')
  c_total=$(echo "$c_out" | awk '{print $2}')
else
  c_pass=0; c_total=0
fi

# project-criteria.sh 실행 (있으면)
if [ -f "$PROJECT" ]; then
  p_out=$(bash "$PROJECT" --counts 2>/dev/null)
  p_pass=$(echo "$p_out" | awk '{print $1}')
  p_total=$(echo "$p_out" | awk '{print $2}')
else
  p_pass=0; p_total=0
fi

total_pass=$((c_pass + p_pass))
total_total=$((c_total + p_total))
pct=$((total_pass * 100 / (total_total > 0 ? total_total : 1)))

if $_SCORE_ONLY; then
  echo "$pct"
  exit 0
fi

echo ""
echo "=== 품질 체크 결과 ==="
bash "$COMMON" 2>/dev/null
[ -f "$PROJECT" ] && bash "$PROJECT" 2>/dev/null
echo ""
echo "=== 총점: $total_pass/$total_total ($pct%) ==="
[ "$pct" -ge 90 ] && echo "✅ 종료 조건 달성" || echo "❌ 미달 — 계속 작업"
[ "$pct" -ge 90 ] && exit 0 || exit 1
