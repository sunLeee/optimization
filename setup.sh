#!/usr/bin/env bash
# .claude/setup.sh — claude-config 환경 초기화 스크립트
#
# subtree 배포 후 실행:
#   cd your-project && bash .claude/setup.sh
#
# 또는 global install:
#   git clone sunLeee/claude-config && cd claude-config && bash .claude/setup.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }

echo ""
echo -e "${BLUE}=== claude-config 환경 초기화 ===${NC}"
echo ""

# ─────────────────────────────────────────────
# 1. tmux (omc-teams worker 실행 필수)
# ─────────────────────────────────────────────
info "tmux 확인 중..."
if command -v tmux &>/dev/null; then
  ok "tmux $(tmux -V | cut -d' ' -f2) 설치됨"
else
  warn "tmux 미설치 — 설치 시도 중..."
  if command -v brew &>/dev/null; then
    brew install tmux && ok "tmux 설치 완료"
  elif command -v apt-get &>/dev/null; then
    sudo apt-get install -y tmux && ok "tmux 설치 완료"
  elif command -v yum &>/dev/null; then
    sudo yum install -y tmux && ok "tmux 설치 완료"
  else
    fail "tmux 자동 설치 불가 — 수동 설치 필요: https://github.com/tmux/tmux"
    exit 1
  fi
fi

# ─────────────────────────────────────────────
# 2. tmux 설정 — 권장 레이아웃 (.tmux.conf)
# ─────────────────────────────────────────────
TMUX_CONF="$HOME/.tmux.conf"
LAYOUT_MARKER="# omc-teams: recommended layout"

info "tmux pane 레이아웃 설정 확인..."
if grep -q "$LAYOUT_MARKER" "$TMUX_CONF" 2>/dev/null; then
  ok "tmux 레이아웃 이미 설정됨"
else
  cat >> "$TMUX_CONF" << 'EOF'

# omc-teams: recommended layout
# 메인 좌 2/3 + worker 우 1/3 (세로 균등 분할)
set-option -g main-pane-width 67%
set-hook -g after-split-window 'select-layout main-vertical'
bind-key M select-layout main-vertical
EOF
  tmux source-file "$TMUX_CONF" 2>/dev/null || true
  ok "tmux 레이아웃 설정 완료 (~/.tmux.conf)"
fi

# ─────────────────────────────────────────────
# 3. GitHub CLI
# ─────────────────────────────────────────────
info "GitHub CLI (gh) 확인 중..."
if command -v gh &>/dev/null; then
  ok "gh $(gh --version | head -1 | cut -d' ' -f3) 설치됨"
  if ! gh auth status &>/dev/null 2>&1; then
    warn "gh 인증 필요 → 실행: gh auth login"
  fi
else
  warn "gh 미설치 (권장 도구)"
  if command -v brew &>/dev/null; then
    brew install gh && ok "gh 설치 완료"
  else
    warn "수동 설치: https://cli.github.com"
  fi
fi

# ─────────────────────────────────────────────
# 4. Gemini CLI (omc-teams gemini worker)
# ─────────────────────────────────────────────
info "Gemini CLI 확인 중..."
if command -v gemini &>/dev/null; then
  ok "gemini CLI 설치됨"
else
  warn "Gemini CLI 미설치"
  warn "설치: npm install -g @google/gemini-cli 또는 pip install google-generativeai"
  warn "모델 설정: export GEMINI_MODEL=gemini-2.0-flash-thinking-exp"
fi

# ─────────────────────────────────────────────
# 5. skills → ~/.claude/skills/ 설치
# ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HOME/.claude/skills"

info "skills 전역 설치 중 ($SKILLS_DST)..."
mkdir -p "$SKILLS_DST"
installed=0

while IFS= read -r skill_file; do
  skill_dir="$(dirname "$skill_file")"
  skill_name=$(grep -m1 "^name:" "$skill_file" 2>/dev/null | sed 's/name: *//')
  [ -z "$skill_name" ] && continue
  target="$SKILLS_DST/$skill_name"
  if [ ! -d "$target" ]; then
    cp -r "$skill_dir" "$target"
    ((installed++))
  fi
done < <(find "$SKILLS_SRC" -name "SKILL.md" | sort)

ok "$installed개 skill 설치 완료 (~/.claude/skills/)"

# ─────────────────────────────────────────────
# 6. oh-my-claudecode (OMC) 안내
# ─────────────────────────────────────────────
echo ""
echo -e "${YELLOW}=== 추가 설정 필요 (Claude Code 내에서 실행) ===${NC}"
echo ""
echo "  OMC 플러그인 설치:"
echo "  → Claude Code 실행 후: /oh-my-claudecode:omc-setup"
echo ""
echo "  Gemini 모델 환경변수 설정 (~/.zshrc 또는 ~/.bashrc):"
echo "  export GEMINI_MODEL=gemini-2.0-flash-thinking-exp"
echo ""

# ─────────────────────────────────────────────
# 완료
# ─────────────────────────────────────────────
echo -e "${GREEN}=== 설정 완료 ===${NC}"
echo ""
echo "다음 단계:"
echo "  1. Claude Code 실행: claude"
echo "  2. OMC 설치: /oh-my-claudecode:omc-setup"
echo "  3. 문서 확인: .claude/docs/setup.md"
echo ""
