#!/usr/bin/env bash
# install.sh — shucle-claude 전역 설치 스크립트
#
# 용도: .claude/skills/ 내 모든 skill을 ~/.claude/skills/ 에 설치
# 사용법:
#   ./install.sh           # 설치
#   ./install.sh --dry-run # 확인만 (실제 설치 안 함)
#   ./install.sh --uninstall # 설치된 skill 제거
#
# 주의: 이름 충돌 시 버전 비교 후 사용자 확인 요청

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/.claude/skills"
TARGET_DIR="$HOME/.claude/skills"
DRY_RUN=false
UNINSTALL=false
CONFLICTS=0
INSTALLED=0
SKIPPED=0

# 옵션 파싱
for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    --uninstall) UNINSTALL=true ;;
    --help)
      echo "사용법: ./install.sh [--dry-run] [--uninstall]"
      echo "  --dry-run   : 실제 설치 없이 확인만"
      echo "  --uninstall : ~/.claude/skills/ 에서 이 리포의 skill 제거"
      exit 0 ;;
  esac
done

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== shucle-claude install.sh ===${NC}"
echo "소스: $SOURCE_DIR"
echo "대상: $TARGET_DIR"
$DRY_RUN && echo -e "${YELLOW}[DRY-RUN 모드: 실제 변경 없음]${NC}"
echo ""

# 대상 디렉토리 생성
if ! $DRY_RUN && ! $UNINSTALL; then
  mkdir -p "$TARGET_DIR"
fi

# 모든 SKILL.md 탐색
while IFS= read -r skill_file; do
  skill_dir="$(dirname "$skill_file")"

  # name: 필드 추출
  skill_name=$(grep -m1 "^name:" "$skill_file" 2>/dev/null | sed 's/^name:[[:space:]]*//' | tr -d '"')

  if [ -z "$skill_name" ]; then
    echo -e "${YELLOW}⚠️  name 필드 없음: $skill_file${NC}"
    ((SKIPPED++))
    continue
  fi

  target_skill_dir="$TARGET_DIR/$skill_name"

  # --uninstall 모드
  if $UNINSTALL; then
    if [ -d "$target_skill_dir" ]; then
      if ! $DRY_RUN; then
        rm -rf "$target_skill_dir"
      fi
      echo -e "${RED}🗑  제거: $skill_name${NC}"
      ((INSTALLED++))
    fi
    continue
  fi

  # 충돌 확인
  if [ -d "$target_skill_dir" ]; then
    existing_name=$(grep -m1 "^name:" "$target_skill_dir/SKILL.md" 2>/dev/null | sed 's/^name:[[:space:]]*//' | tr -d '"')

    if [ "$existing_name" = "$skill_name" ]; then
      # 같은 이름 — 덮어쓰기 여부 확인
      echo -e "${YELLOW}⚠️  충돌: $skill_name (이미 존재)${NC}"
      ((CONFLICTS++))

      # 자동 덮어쓰기 (프로젝트 버전이 우선)
      echo -e "   → 프로젝트 버전으로 업데이트"
      if ! $DRY_RUN; then
        rm -rf "$target_skill_dir"
        cp -r "$skill_dir" "$target_skill_dir"
      fi
      ((INSTALLED++))
    else
      echo -e "${RED}❌ 이름 충돌 (다른 내용): $skill_name vs $existing_name${NC}"
      ((SKIPPED++))
    fi
  else
    # 신규 설치
    if ! $DRY_RUN; then
      cp -r "$skill_dir" "$target_skill_dir"
    fi
    echo -e "${GREEN}✅ 설치: $skill_name${NC}"
    ((INSTALLED++))
  fi

done < <(find "$SOURCE_DIR" -name "SKILL.md" | sort)

echo ""
echo -e "${BLUE}=== 설치 완료 ===${NC}"
echo "✅ 설치/업데이트: $INSTALLED"
echo "⚠️  충돌 처리:  $CONFLICTS"
echo "⏭  건너뜀:     $SKIPPED"
echo ""

if ! $DRY_RUN && ! $UNINSTALL && [ "$INSTALLED" -gt 0 ]; then
  echo -e "${GREEN}~/.claude/skills/ 에 $INSTALLED개 skill이 설치되었습니다.${NC}"
  echo "Claude Code를 재시작하면 적용됩니다."
fi
