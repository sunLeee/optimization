# How to Use `.claude/` as a Git Subtree

이 문서는 `shucle-claude` 단독 리포의 `.claude/` 디렉토리를 다른 프로젝트에 **git subtree**로 배포하는 방법을 설명한다.

---

## 배경

### 왜 Git Subtree인가?

| 방법 | 장점 | 단점 |
|------|------|------|
| **Git Subtree** ← 권장 | clone 시 추가 명령 불필요, 히스토리 통합 | pull/push 시 명령이 복잡 |
| Git Submodule | 독립 히스토리 | `git clone --recursive` 필수, 복잡 |
| 심볼릭 링크 | 즉시 적용 | 팀원마다 수동 설정, CI 불가 |
| 복사 스크립트 | 단순 | 버전 추적 없음 |

### 목표 구조

```
shucle-claude/         ← 단독 Claude Code 환경 리포
└── .claude/
    ├── AGENTS.md
    ├── agents/
    ├── docs/
    ├── output-styles/
    ├── settings.json
    ├── skill-catalog.md
    └── skills/ (52개)

shucle-ai-agent/       ← 사용 리포
└── .claude/           ← subtree로 shucle-claude 내용 포함
```

---

## Step 1: shucle-claude 리포 생성

```bash
# 새 리포 생성
mkdir shucle-claude && cd shucle-claude
git init
git remote add origin https://github.com/hkmc-airlab/shucle-claude.git

# 현재 shucle-ai-agent의 .claude/ 내용을 shucle-claude로 이동
cp -r /path/to/shucle-ai-agent/.claude/* .
cp /path/to/shucle-ai-agent/CLAUDE.md .  # 베이스 템플릿

git add .
git commit -m "feat(init): shucle-claude 초기 Claude Code 환경 구성"
git push -u origin main
```

---

## Step 2: 다른 리포에 subtree로 추가

```bash
cd /path/to/target-repo

# shucle-claude의 루트를 target-repo의 .claude/ 경로에 embed
git subtree add \
  --prefix=.claude \
  https://github.com/hkmc-airlab/shucle-claude.git \
  main \
  --squash

# 확인
ls .claude/
# AGENTS.md  agents/  docs/  output-styles/  settings.json  skill-catalog.md  skills/
```

**`--squash` 옵션**: shucle-claude의 전체 히스토리를 하나의 커밋으로 압축. 이 옵션 없이도 가능하나 히스토리가 길어짐.

---

## Step 3: shucle-claude 업데이트를 각 리포에 적용

```bash
# shucle-claude에 새 skill/agent 추가 후:
cd /path/to/target-repo

git subtree pull \
  --prefix=.claude \
  https://github.com/hkmc-airlab/shucle-claude.git \
  main \
  --squash
```

---

## Step 4: 프로젝트별 커스터마이즈

subtree pull 후 충돌을 최소화하기 위해 **프로젝트 전용 설정은 별도 파일로 관리**한다.

```
target-repo/
├── .claude/                    ← shucle-claude subtree (공유)
│   ├── settings.json           ← 기본 훅 (shucle-claude에서 옴)
│   └── skills/                 ← 52개 공유 skills
└── .claude.local/              ← 프로젝트 전용 (gitignore 또는 별도 관리)
    ├── settings.local.json     ← 프로젝트 추가 훅
    └── skills/                 ← 프로젝트 전용 skills
```

또는 `settings.json`을 merge 전략으로 관리:

```bash
# .gitattributes에 추가하여 merge 시 우리 버전 유지
echo ".claude/settings.json merge=ours" >> .gitattributes
```

---

## 워크플로우 요약

```
shucle-claude (중앙 리포)
    ↓ git subtree add/pull
shucle-ai-agent/.claude/
shucle-ai-agent-v2/.claude/
other-project/.claude/
```

```bash
# skill 추가 시 워크플로우:
# 1. shucle-claude에서 작업
cd shucle-claude
# .claude/skills/convention-new-skill/ 추가
git add && git commit && git push

# 2. 각 리포에서 pull
cd shucle-ai-agent
git subtree pull --prefix=.claude https://github.com/hkmc-airlab/shucle-claude.git main --squash
```

---

## 현재 진행 상황 (2026-03-19)

현재 `shucle-ai-agent-general-rules` 브랜치가 사실상 `shucle-claude`의 내용을 담고 있다:

```
shucle-ai-agent (master)
└── branch: shucle-ai-agent-general-rules  ← 현재 작업 브랜치
    └── .claude/                            ← shucle-claude가 될 내용
```

**다음 단계:**
1. 이 브랜치를 master에 merge (PR 제출)
2. `shucle-claude` 단독 리포 생성
3. `shucle-ai-agent/.claude/` 를 subtree로 연결
4. 다른 프로젝트에도 동일하게 적용

---

## 자주 쓰는 명령 모음

```bash
# 리모트 URL 변수로 관리
SHUCLE_CLAUDE=https://github.com/hkmc-airlab/shucle-claude.git

# 초기 추가
git subtree add --prefix=.claude $SHUCLE_CLAUDE main --squash

# 업데이트 가져오기
git subtree pull --prefix=.claude $SHUCLE_CLAUDE main --squash

# 내 변경사항을 shucle-claude로 역push (권한 있을 때)
git subtree push --prefix=.claude $SHUCLE_CLAUDE main

# 현재 subtree 상태 확인
git log --oneline --graph .claude/ | head -10
```

---

## 참조

- [Git subtree 공식 문서](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- [.claude/ 구조](.claude/skill-catalog.md)
- [AGENTS.md](.claude/AGENTS.md)
- [설정 가이드](.claude/docs/README.md)
