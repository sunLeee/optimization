# Git Subtree 워크플로우: claude-config

`optimization` 프로젝트는 `claude-config`를 `claude-config/` 경로에 git subtree로 내장한다.

```
optimization/
└── claude-config/   ← sunLeee/claude-config.git의 subtree
```

---

## 핵심 개념

subtree는 **별도의 git 명령이 없다.** `claude-config/` 내 파일 수정은
일반 파일 수정과 동일하게 `optimization` 리포에서 커밋한다.
단, 변경사항을 원본 `claude-config` 리포와 동기화할 때만 subtree 명령을 쓴다.

---

## 1. claude-config 파일 수정 후 커밋

```bash
# 파일 수정 (예: claude-config/README.md)
vim claude-config/README.md

# 일반 git add/commit — subtree 전용 명령 불필요
git add claude-config/
git commit -m "feat(claude-config): README 업데이트"

# optimization 리포에 push
git push origin main
```

---

## 2. 원본 claude-config 리포의 최신 변경사항 가져오기 (pull)

```bash
git subtree pull \
  --prefix=claude-config \
  git@github.com:sunLeee/claude-config.git \
  main \
  --squash
```

`--squash`: 원본 리포의 전체 히스토리를 하나의 커밋으로 압축해 가져온다.

---

## 3. optimization에서 수정한 내용을 원본 claude-config 리포로 역push

```bash
git subtree push \
  --prefix=claude-config \
  git@github.com:sunLeee/claude-config.git \
  main
```

> 원본 리포 쓰기 권한이 있어야 한다.

---

## 변수로 URL 관리 (편의용)

```bash
CLAUDE_CONFIG=git@github.com:sunLeee/claude-config.git

# pull
git subtree pull --prefix=claude-config $CLAUDE_CONFIG main --squash

# push (역방향)
git subtree push --prefix=claude-config $CLAUDE_CONFIG main
```

---

## 자주 하는 실수

| 상황 | 원인 | 해결 |
|------|------|------|
| `fatal: working tree has modifications` | 미커밋 변경사항 존재 | `git add -A && git commit` 후 재시도 |
| subtree pull 충돌 | 양쪽 리포에서 같은 파일 수정 | 충돌 해결 후 `git commit` |
| push 거부 | 원본 리포에 새 커밋 존재 | `subtree pull` 먼저 수행 후 push |

---

## 워크플로우 요약

```
[optimization 내 수정]
      ↓ git add && git commit && git push
[optimization/main 최신화]

[claude-config 원본에서 업데이트 가져오기]
      ↓ git subtree pull --prefix=claude-config ... --squash
[claude-config/ 최신화]

[수정 내용을 claude-config 원본으로 보내기]
      ↓ git subtree push --prefix=claude-config ...
[sunLeee/claude-config main 최신화]
```
