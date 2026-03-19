# Git Subtree 워크플로우: .claude/

## 현재 구조

```
optimization/                          ← sunLeee/optimization.git
└── .claude/                           ← sunLeee/claude-config.git의 .claude/ 만 subtree
    ├── AGENTS.md
    ├── settings.json
    ├── skills/
    └── ...

claude-config/ (로컬 별도 리포)        ← sunLeee/claude-config.git
└── .claude/                           ← subtree 원본 소스
```

subtree는 `claude-config` 리포 전체가 아닌 `.claude/` 디렉토리만 추출해 사용한다.
이를 위해 `git subtree split`으로 `.claude/`만 담긴 브랜치를 별도 생성했다.

---

## 초기 설정 (최초 1회)

### Step 1: claude-config 리포에서 .claude/ 만 분리

```bash
cd /Users/hmc123/Documents/claude-config

# .claude/ 내용만 담긴 브랜치 생성
git subtree split --prefix=.claude -b claude-dot-only
```

- `--prefix=.claude`: `.claude/` 하위 내용만 추출
- `-b claude-dot-only`: 추출 결과를 저장할 로컬 브랜치명

### Step 2: optimization 리포에 subtree로 추가

```bash
cd /Users/hmc123/Documents/optimization

git subtree add \
  --prefix=.claude \
  /Users/hmc123/Documents/claude-config \
  claude-dot-only \
  --squash
```

- `--prefix=.claude`: `optimization/.claude/` 경로에 배치
- `--squash`: 원본 히스토리를 커밋 1개로 압축

---

## 일상 작업

### .claude/ 파일 수정 후 optimization에 커밋

subtree 내 파일도 일반 파일과 동일하게 커밋한다.

```bash
cd /Users/hmc123/Documents/optimization

# 파일 수정 후
git add .claude/
git commit -m "feat(.claude): 스킬 추가"
git push origin main
```

### claude-config 원본 업데이트를 optimization에 반영 (pull)

`claude-config`에 새 커밋이 생겼을 때:

```bash
# 1. claude-config 리포에서 분리 브랜치 갱신
cd /Users/hmc123/Documents/claude-config
git pull origin main
git subtree split --prefix=.claude -b claude-dot-only

# 2. optimization에서 pull
cd /Users/hmc123/Documents/optimization
git subtree pull \
  --prefix=.claude \
  /Users/hmc123/Documents/claude-config \
  claude-dot-only \
  --squash
```

### optimization의 수정 내용을 claude-config 원본으로 역push

```bash
cd /Users/hmc123/Documents/optimization

git subtree push \
  --prefix=.claude \
  /Users/hmc123/Documents/claude-config \
  claude-dot-only
```

> 이후 `claude-config` 리포에서 `git push origin main`으로 원격에도 반영한다.

---

## settings.json 프로젝트별 오버라이드

subtree pull 시 `settings.json`이 원본으로 덮어써지는 문제를 방지하는 두 가지 방법.

### 방법 A: merge=ours (단순, pull 시 로컬 버전 고정)

```bash
# optimization 루트에서
echo ".claude/settings.json merge=ours" >> .gitattributes
git add .gitattributes
git commit -m "chore: settings.json subtree pull 시 로컬 버전 유지"
```

subtree pull 시 `settings.json`은 항상 `optimization` 버전이 유지된다.
단점: 원본의 `settings.json` 업데이트도 차단된다.

### 방법 B: settings.local.json 분리 (권장)

```
.claude/
├── settings.json        ← subtree 원본 기본값 (수정하지 않음)
└── settings.local.json  ← optimization 전용 오버라이드
```

Claude Code는 `settings.local.json`을 자동으로 병합해 읽는다.
원본 기본값 업데이트는 그대로 받으면서 프로젝트 설정만 격리할 수 있다.

```bash
# settings.local.json을 git에서 제외하거나 별도 커밋
echo ".claude/settings.local.json" >> .gitignore
```

---

## 자주 하는 실수

| 증상 | 원인 | 해결 |
|------|------|------|
| `fatal: working tree has modifications` | 미커밋 변경사항 존재 | `git add -A && git commit` 후 재시도 |
| subtree pull 충돌 | 양쪽에서 같은 파일 수정 | 충돌 해결 후 `git commit` |
| push 거부 | 원본 브랜치에 새 커밋 존재 | `subtree pull` 먼저 후 push |
| split 후 pull 해도 변경 없음 | split 브랜치 미갱신 | `claude-config`에서 `git subtree split` 재실행 |

---

## 워크플로우 한눈에 보기

```
[claude-config/.claude/ 수정]
      ↓ git push origin main
[sunLeee/claude-config 최신화]
      ↓ git subtree split --prefix=.claude -b claude-dot-only  (claude-config 리포)
[claude-dot-only 브랜치 갱신]
      ↓ git subtree pull --prefix=.claude ... claude-dot-only --squash  (optimization 리포)
[optimization/.claude/ 최신화]
      ↓ git push origin main
[sunLeee/optimization 최신화]
```

역방향 (optimization → claude-config):

```
[optimization/.claude/ 수정 및 커밋]
      ↓ git subtree push --prefix=.claude ... claude-dot-only  (optimization 리포)
[claude-dot-only 브랜치 갱신]
      ↓ git push origin main  (claude-config 리포)
[sunLeee/claude-config 최신화]
```
