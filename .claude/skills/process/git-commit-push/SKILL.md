---
name: git-commit-push
triggers:
  - "git commit push"
description: Git 커밋과 푸시를 안전하게 수행한다. 변경 확인, 커밋 메시지 생성, 푸시 전 확인을 포함한다.
argument-hint: "[--push] [--message msg] - 푸시 여부, 메시지"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: Git 워크플로우 스킬이다. 안전한 커밋과 푸시를 지원한다. convention-commit 스킬의 규칙을 준수한다.
agent: 당신은 Git 워크플로우 전문가입니다. Conventional Commits 규칙을 따르며 안전한 버전 관리를 수행합니다. 본문은 한국어로, 기술 용어는 영어로 작성합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 기타
skill-type: Atomic
references:
  - "@skills/convention-commit/SKILL.md"
referenced-by:
  - "@skills/convention-commit/SKILL.md"

---
# git-commit-push

Git 커밋과 푸시를 안전하게 수행하는 스킬.

## 목적

- 변경 사항 확인 및 스테이징
- Conventional Commits 형식 커밋 메시지 생성
- 푸시 전 브랜치 확인 및 사용자 승인

## 사용법

```
/git-commit-push
/git-commit-push --push
/git-commit-push --message "feat: Add new feature"
/git-commit-push --push --message "fix: Fix critical bug"
```

## Conventional Commits 형식

**커밋 메시지 형식과 규칙은 [@skills/convention-commit/SKILL.md] 스킬을 참조하세요.**

→ `@skills/convention-commit/SKILL.md`

**핵심 요약**:
- 형식: `<type>(<scope>): <한국어 제목>`
- 제목: 한국어 (50자 이내)
- 본문: 한국어 (기술 용어는 영어 유지)
- Co-Authored-By 푸터 사용 금지
- 커밋 단위는 원자적단위로

## 프로세스

```
/git-commit-push [options]
    |
    v
[Step 1] 변경 확인
    |-- git status 실행
    |-- git diff 실행
    |-- 변경 파일 목록 표시
    |
    v
[Step 2] 커밋 메시지 생성
    |-- 변경 내용 분석
    |-- Conventional Commits 형식 제안
    |-- 사용자 확인/수정 (AskUserQuestion)
    |
    v
[Step 3] 스테이징 & 커밋
    |-- git add (변경 파일)
    |-- git commit -m "..."
    |-- 커밋 해시 출력
    |
    v
[Step 4] 푸시 (--push 옵션 시)
    |-- 현재 브랜치 확인
    |-- main/master 직접 푸시 경고
    |-- 사용자 확인 (AskUserQuestion)
    |-- git push origin <branch>
    |
    v
완료 보고
```

## 안전 장치

| 항목 | 동작 |
|------|------|
| **main 직접 푸시** | 경고 메시지 표시 + 확인 요청 |
| **force push** | 지원하지 않음 |
| **빈 커밋** | 변경 없을 시 중단 |
| **pre-commit 훅 실패** | 오류 표시 + 안내 |

## 예제

### 기본 커밋

```
User: /git-commit-push

Claude:
=== Git Commit ===

[1/3] 변경 확인...

변경된 파일:
M src/api/routes/auth.py
A src/services/auth_service.py
A tests/test_auth.py

[2/3] 커밋 메시지 제안...

제안 메시지:
feat(auth): user authentication endpoints 추가

사용자 인증을 위한 API 엔드포인트를 추가한다.

변경 사항:
- login/logout API 엔드포인트 구현
- JWT 토큰 생성 로직 추가
- auth service 단위 테스트 작성

이 메시지로 커밋하시겠습니까? [Y/n/edit]

User: Y

[3/3] 커밋 실행...

git add src/api/routes/auth.py src/services/auth_service.py tests/test_auth.py
git commit -m "..."

✓ 커밋 완료: abc1234

=== 완료 ===
```

### 커밋 + 푸시

```
User: /git-commit-push --push

Claude:
=== Git Commit & Push ===

[1/4] 변경 확인...
  M src/utils/helpers.py

[2/4] 커밋 메시지 제안...
refactor(utils): 공통 helper 함수 추출

중복된 헬퍼 함수들을 공통 모듈로 추출한다.

변경 사항:
- 날짜 포맷팅 함수를 utils.helpers로 이동
- JSON 파싱 로직 통합

이 메시지로 커밋하시겠습니까? [Y/n/edit]

User: Y

[3/4] 커밋 실행...
✓ 커밋 완료: def5678

[4/4] 푸시 확인...

현재 브랜치: feature/refactor-utils
원격: origin/feature/refactor-utils

푸시하시겠습니까? [Y/n]

User: Y

git push origin feature/refactor-utils
✓ 푸시 완료

=== 완료 ===
```

### main 브랜치 경고

```
User: /git-commit-push --push

Claude:
[4/4] 푸시 확인...

⚠️ 경고: 현재 브랜치가 main입니다.
main 브랜치에 직접 푸시하면 코드 리뷰 없이 변경이 반영됩니다.

정말 main에 푸시하시겠습니까? [y/N]

User: N

푸시가 취소되었습니다.
feature 브랜치 생성 후 PR을 권장합니다.
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/convention-commit/SKILL.md] | 참조 | 커밋 컨벤션 규칙 |
| [@skills/check-commit-message/SKILL.md] | 연계 | 커밋 메시지 검증 |
| [@skills/done/SKILL.md] | 선행 | 작업 완료 후 커밋 |
| [@skills/code-review/SKILL.md] | 선행 | 커밋 전 코드 리뷰 |

## 커밋 메시지 작성 가이드

**상세한 작성 규칙은 [@skills/convention-commit/SKILL.md] 스킬을 참조하세요.**

### 빠른 참조 예시

```bash
# 형식
<type>(<scope>): <한국어 제목>

# 예시
feat(api): user endpoint 추가
fix(auth): null token 처리
docs(readme): 설치 가이드 업데이트
```

### 본문 예시

```bash
feat(api): user endpoint 추가

사용자 리소스에 대한 CRUD API를 추가한다.
Pydantic을 사용한 입력 검증을 포함한다.

변경 사항:
- GET /users, POST /users 엔드포인트 구현
- UserSchema 모델 추가
- 권한 검증 로직 추가
```

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-22 | 1.1.0 | 한국어 본문 규칙 및 Co-Authored-By 생략 정책 반영 |
| 2026-01-21 | 1.0.0 | 초기 스킬 생성 |

## Gotchas (실패 포인트)

- push 전 반드시 `git status` 확인 — 의도치 않은 파일 포함 방지
- force push 명시적 승인 없으면 절대 금지
- 민감 정보(.env, secrets) 실수 commit 시 git history에 영구 기록
