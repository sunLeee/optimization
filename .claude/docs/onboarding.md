# 신규 팀원 온보딩 가이드

> **목표**: 이 가이드를 따라 30분 내에 첫 commit을 완료한다.

---

## 1. 전제 조건 설치 (5분)

```bash
# 필수 도구
brew install tmux gh
npm install -g @google/gemini-cli

# oh-my-claudecode 설치
# Claude Code 실행 후: /oh-my-claudecode:omc-setup
```

## 2. 환경 설정 (5분)

```bash
git clone <이 리포>
cd claude-config

# 환경 초기화
bash .claude/setup.sh

# pre-commit 활성화 (필수)
pip install pre-commit
pre-commit install
```

## 3. 핵심 규칙 5가지

| 규칙 | 내용 |
|------|------|
| **AW-001** | Claude = sonnet, opus 불가, Gemini 우선 고성능 |
| **AW-005** | 구현 전 deep-interview 필수 (모호성 5% 미만) |
| **AW-007** | 모든 구현은 `/ralph` 사용 |
| **AW-009** | 되돌리기 어려운 결정 = ADR 먼저 |
| **AW-010** | pre-commit 통과 필수, `--no-verify` 금지 |

## 4. 첫 작업 시나리오

```
1. gh issue list --assignee @me  # 작업 확인
2. Claude Code 실행
3. 작업 설명 입력 → TASK-MODE-ACTIVATED 발동
4. deep-interview 완료 → ralplan → ralph 실행
5. pre-commit 통과 확인 후 PR 생성
```

## 5. Hook Profile (첫 주 권장)

strict 모드가 부담스러우면 첫 주에는 아래 설정으로 시작:

```bash
export ECC_HOOK_PROFILE=minimal
# ~/.zshrc에 추가하면 영구 적용
```

standard(기본)와 strict의 차이는 `.claude/docs/hooks-guide-ko.md` 참조.

## 6. 막혔을 때 (트러블슈팅)

| 증상 | 해결 |
|------|------|
| Write/Edit 차단됨 | `rm /tmp/.claude-task-*.lock` |
| pre-commit mypy 실패 | `pip install types-<패키지>` |
| Gemini SSL 오류 | `export NODE_TLS_REJECT_UNAUTHORIZED=0` |
| ralplan 합의 안 됨 | `--deliberate` 플래그 추가 |
| claude opus 오류 | sonnet으로 자동 대체됨, 정상 |
