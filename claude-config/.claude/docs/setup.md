# Claude Code 환경 초기 설정 가이드

이 가이드는 claude-config를 처음 적용하는 개발자를 위한 필수 설정 절차다.

---

## 1. 필수 도구 설치

```bash
# tmux (OMC omc-teams 사용 필수)
brew install tmux           # macOS
sudo apt install tmux       # Ubuntu/Debian

# oh-my-claudecode (OMC) 플러그인
/oh-my-claudecode:omc-setup  # Claude Code 내에서 실행

# GitHub CLI (Session Start 체크리스트용)
brew install gh && gh auth login
```

---

## 2. tmux 설정 — OMC 권장 레이아웃

omc-teams는 tmux pane을 생성하여 worker를 실행한다.
권장 레이아웃: **메인 좌 2/3 + worker 우 1/3 (1/n 균등 분할)**

```bash
# ~/.tmux.conf 에 추가
# 메인 pane: 좌측 67%, worker pane: 우측 33% 균등 분할
set-option -g main-pane-width 67%
set-option -g main-pane-height 100%

# 기본 레이아웃: main-vertical (메인 좌, worker 우 스택)
bind-key M select-layout main-vertical
```

**pane 구조 (omc-teams 실행 시):**

- **메인 pane**: 전체 가로 2/3 (좌측, Claude Code 영역)
- **worker pane**: 전체 가로 1/3 (우측), worker 수만큼 세로로 균등 분할

```
┌──────────────────────┬──────────┐  ← worker 1개
│   main (Claude Code) │ worker 1 │
└──────────────────────┴──────────┘

┌──────────────────────┬──────────┐  ← worker 2개
│                      │ worker 1 │
│   main (Claude Code) ├──────────┤
│                      │ worker 2 │
└──────────────────────┴──────────┘

┌──────────────────────┬──────────┐  ← worker 3개
│                      │ worker 1 │
│   main (Claude Code) ├──────────┤
│                      │ worker 2 │
│                      ├──────────┤
│                      │ worker 3 │
└──────────────────────┴──────────┘
         2/3                1/3
```

우측 1/3은 worker 수(N)에 따라 **세로로 1/N씩 균등 분할**된다.

tmux 설정 적용:
```bash
tmux source-file ~/.tmux.conf
```

---

## 3. omc-teams 프롬프트 전달 방식

omc-teams는 각 tmux pane에서 CLI worker를 실행한다. 프롬프트를 어떻게 전달하느냐에 따라 3가지 방식이 있다.

### 방식 1: 인라인 (짧은 프롬프트)

```bash
omc-teams 2:codex "Claude Code skills 관리 best practice 조사" \
           3:gemini "Claude Code skills 관리 best practice 조사"
```

### 방식 2: 파일에서 읽기 (긴 프롬프트 권장)

```bash
# 프롬프트 파일 저장
cat > /tmp/prompt.md << 'EOF'
다음을 조사하라:
1. Claude Code skills 관리 전략
2. 전역 vs 프로젝트 skill 충돌 처리
3. 최신 best practice
EOF

# 파일에서 읽어 전달
omc-teams 2:codex "$(cat /tmp/prompt.md)" \
           3:gemini "$(cat /tmp/prompt.md)"
```

### 방식 3: .omc/research/ 디렉토리 활용

```bash
# 프롬프트 저장
echo "조사 내용..." > .omc/research/query-001.md

# worker가 파일을 읽도록 지시
omc-teams 2:codex "파일 .omc/research/query-001.md 읽고 조사하라" \
           3:gemini "파일 .omc/research/query-001.md 읽고 조사하라"
```

### 모델 명시적 지정

```bash
# Gemini: 고성능 사고 모델 지정
# codex: gpt-5.2-codex 자동 사용

# Gemini CLI에서 모델 지정 방법 (pane 내 환경변수)
export GEMINI_MODEL=gemini-2.0-flash-thinking-exp
omc-teams 2:codex "조사 내용" 3:gemini "조사 내용"

# 또는 claude-config/.claude/settings.json에 모델 설정 추가 가능
```

### 결과 수집

각 worker의 결과는 tmux pane에 출력된다. 결과를 파일로 저장하려면:

```bash
# worker에게 결과를 파일로 저장하도록 지시
omc-teams 2:codex "조사 후 결과를 .omc/research/result-codex.md에 저장하라: {조사 내용}" \
           3:gemini "조사 후 결과를 .omc/research/result-gemini.md에 저장하라: {조사 내용}"

# 결과 확인
cat .omc/research/result-codex.md
cat .omc/research/result-gemini.md
```

---

## 4. omc-teams pane 번호 규칙

pane 번호는 **자동 순차 증가**다. 하드코딩하지 않는다.

```bash
# pane 1 = Claude Code 메인 (고정)
# pane 2 = 첫 번째 worker
# pane 3 = 두 번째 worker
# pane N+1 = N번째 worker

# 패턴: 시작 번호(2)부터 worker 수만큼 순차 증가
omc-teams 2:codex "주제 A" 3:gemini "주제 A"    # 2개 worker
omc-teams 2:codex "A" 3:gemini "A" 4:codex "B" 5:gemini "B"  # 4개 worker

# 주의: 번호를 건너뛰거나 중복하면 오류 발생
```

**worker 수 결정 기준:**
- 조사 주제 수 × agent 종류 = 총 worker 수
- 예: 2개 주제 × (codex + gemini) = 4개 worker (pane 2~5)

---

## 4. claude-config 설치

```bash
# 전역 설치 (skills → ~/.claude/skills/)
git clone git@github.com:sunLeee/claude-config.git
cd claude-config && ./install.sh

# 프로젝트에 subtree 배포
git subtree add --prefix=.claude \
  git@github.com:sunLeee/claude-config.git main --squash
```

---

## 5. 설치 확인

```bash
# OMC 정상 작동 확인
/oh-my-claudecode:omc-doctor

# tmux 세션 테스트
tmux new-session -d -s test && tmux split-window -h -p 33 && tmux kill-session -t test

# skill 설치 확인
ls ~/.claude/skills/ | wc -l   # 127+ 개 표시
```

---

## 6. omc-teams 타임아웃 설정

omc-teams worker(codex/gemini)가 응답이 느릴 때 타임아웃 조정:

```bash
# ~/.claude/settings.json 또는 .claude/settings.json 에 추가
{
  "env": {
    "GEMINI_TIMEOUT": "120",        # Gemini CLI 응답 대기 (초)
    "OPENAI_TIMEOUT": "120"          # Codex CLI 응답 대기 (초)
  }
}

# 또는 omc-teams 호출 시 환경변수 직접 설정
GEMINI_TIMEOUT=180 omc-teams 2:codex "조사 주제" 3:gemini "조사 주제"
```

**worker가 멈췄을 때:**
```bash
# tmux pane 확인
tmux list-panes -a

# 특정 pane 강제 종료
tmux kill-pane -t {session}:{window}.{pane}

# omc-teams 전체 재시작
# claude-config/.omc-config.json에 타임아웃 설정
```

**`.omc-config.json` 설정 (프로젝트 루트):**
```json
{
  "team": {
    "shutdownTimeoutMs": 30000,
    "monitorIntervalMs": 15000
  }
}
```

## 참조

- [AGENTS.md](../AGENTS.md) — 에이전트 계층 구조
- [omc.md](./omc.md) — OMC 운영 가이드
- [.claude/settings.json](../settings.json) — 훅 설정
