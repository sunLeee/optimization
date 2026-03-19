---
name: quality-precommit
triggers:
  - "quality precommit"
description: Pre-commit hook 설정 및 관리 스킬. 프로젝트에 pre-commit 환경을 구성하고, 훅 설정을 최적화한다. 코드 품질 검사를 커밋 전에 자동으로 실행하는 환경을 구축한다.
argument-hint: "[init|update|run|ci] - Pre-commit 설정 작업"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: Pre-commit hook 설정 및 관리를 담당한다. .pre-commit-config.yaml 생성, 훅 최적화, CI 통합을 수행한다.
agent: Pre-commit 환경 구성 전문가. 프로젝트 특성에 맞는 훅 조합을 설계하고, 성능 최적화를 수행한다.
hooks:
  pre_execution: []
  post_execution: []
category: 품질 관리
skill-type: Atomic
references: []
referenced-by:
  - "@skills/setup-quality/SKILL.md"

---
# Pre-commit 설정 관리

Pre-commit hook 환경을 구성하고 관리한다.

## 목적

- Pre-commit 환경 초기 설정
- 프로젝트별 훅 최적화
- CI/CD 통합 설정
- 훅 실행 성능 개선

## 사용법

```
/quality-precommit init         # 초기 설정
/quality-precommit update       # 훅 버전 업데이트
/quality-precommit run          # 전체 파일 검사
/quality-precommit ci           # CI 설정 생성
```

---

## 프로젝트 유형별 설정

**.pre-commit-config.yaml 템플릿을 프로젝트 유형에 맞게 선택:**

### 1. 일반 Python 프로젝트

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### 2. Data Science 프로젝트

```yaml
repos:
  # 기본 + Ruff
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Notebook 전용
  - repo: https://github.com/kynan/nbstripout
    rev: 0.8.1
    hooks:
      - id: nbstripout
        args: [--keep-count]

  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.9.1
    hooks:
      - id: nbqa-ruff
        args: [--fix]
```

### 3. API/백엔드 프로젝트

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-requests]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.2
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml', '-r', 'src']
```

---

## 설치 및 실행

### 초기 설치

```bash
# uv 환경
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# pip 환경
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### 실행

```bash
# 스테이지된 파일만 검사
uv run pre-commit run

# 전체 파일 검사
uv run pre-commit run --all-files

# 특정 훅만 실행
uv run pre-commit run ruff --all-files

# 자동 수정
uv run pre-commit run --all-files --hook-stage manual
```

### 훅 업데이트

```bash
# 모든 훅 최신 버전으로 업데이트
uv run pre-commit autoupdate

# 특정 저장소만 업데이트
uv run pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit
```

---

## CI/CD 통합

**GitHub Actions**: [@templates/skill-examples/quality-precommit/ci-github-actions.yml]

**pre-commit.ci 서비스**: [@templates/skill-examples/quality-precommit/ci-precommit-service.yml]

---

## 성능 최적화

**핵심 전략**:
1. **스테이지 분리**: 빠른 검사(ruff)는 매 커밋, 느린 검사(mypy, bandit)는 푸시 시에만
2. **파일 필터링**: 필요한 디렉토리만 검사 (`files: ^src/`, `exclude: ^tests/`)
3. **병렬 실행**: `pre-commit run --all-files -j 4`

**상세 가이드**: [@templates/skill-examples/quality-precommit/performance-optimization.md]

---

## 훅 우회

### 임시 우회

```bash
# 모든 훅 우회
git commit --no-verify -m "WIP: temporary commit"

# 특정 훅만 우회
SKIP=mypy git commit -m "feat: add feature"
```

### 영구 제외

```yaml
# .pre-commit-config.yaml
- id: check-yaml
  exclude: |
    (?x)^(
      templates/.*\.yaml|
      fixtures/.*\.yaml
    )$
```

---

## 트러블슈팅

| 문제 | 해결 방법 |
|------|----------|
| 훅 동작 안함 | `pre-commit clean && pre-commit install` |
| 캐시 오류 | `pre-commit gc && rm -rf ~/.cache/pre-commit` |
| 특정 훅 실패 | `pre-commit run <hook-id> --verbose --all-files` |

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/quality-ruff/SKILL.md] | Ruff 린터/포맷터 설정 |
| [@skills/quality-mypy/SKILL.md] | mypy 타입 검사 설정 |
| [@skills/quality-bandit/SKILL.md] | Bandit 보안 검사 설정 |
| [@skills/check-python-style/SKILL.md] | 코드 스타일 검증 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-27 | 1.1.0 | 보수적 리팩토링 - 409→262줄. CI/CD 및 성능 최적화 템플릿 분리 |
| 2026-01-21 | 1.0.0 | 초기 생성 - Pre-commit 설정 관리 |

## Gotchas (실패 포인트)

- `pre-commit install` clone 후 1회 실행 안 하면 hook이 동작 안 함
- `--no-verify` 사용 절대 금지 (팀 규칙 AW-010)
- hooks 버전이 고정되어 있으면 보안 취약점 패치 누락 가능 — 주기적 `pre-commit autoupdate`
- Python 버전 불일치 시 hook 실행 실패 — `.pre-commit-config.yaml`에 language_version 명시
