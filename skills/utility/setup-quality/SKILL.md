---
name: setup-quality
triggers:
  - "setup quality"
description: "프로젝트 품질 도구 일괄 설정 스킬. pre-commit, ruff, mypy, bandit 등을 한 번에 설정한다."
argument-hint: "[--minimal|--standard|--strict|--ds] [--no-logging] - 설정 수준"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: 프로젝트 품질 도구 일괄 설정을 담당한다. quality-precommit, quality-ruff, quality-mypy, quality-bandit 등을 프로젝트 유형에 맞게 조합하여 설정한다.
agent: 품질 환경 설정 전문가. 프로젝트 특성을 분석하여 적절한 품질 도구 조합을 설정한다.
hooks:
  pre_execution: []
  post_execution: []
category: 환경 설정
skill-type: Composite
references:
  - "@skills/quality-ruff/SKILL.md"
  - "@skills/quality-mypy/SKILL.md"
  - "@skills/quality-bandit/SKILL.md"
  - "@skills/quality-precommit/SKILL.md"
  - "@skills/quality-notebook/SKILL.md"
  - "@skills/setup-logging/SKILL.md"
referenced-by:
  - "@skills/project-init/SKILL.md"

---
# 프로젝트 품질 설정

프로젝트 품질 도구를 일괄 설정하는 복합 스킬.

## 목적

- 품질 도구 일괄 설정
- 프로젝트 유형별 최적화
- pre-commit, ruff, mypy, bandit, logging 통합
- pyproject.toml 자동 구성

## 사용법

```bash
/setup-quality                    # 대화형 설정
/setup-quality --minimal          # 최소 설정 (ruff만)
/setup-quality --standard         # 표준 설정 (ruff + mypy + pre-commit)
/setup-quality --strict           # 엄격 설정 (전체 + bandit)
/setup-quality --ds               # Data Science 설정 (notebook 포함)
```

---

## 스킬 타입

**Composite Skill** - 다음 스킬들을 조합:

| 순서 | 스킬 | 역할 |
|------|------|------|
| 1 | 프로젝트 분석 | 구조 분석 → 권장 프로파일 결정 |
| 2 | [@skills/quality-ruff/SKILL.md] | Ruff 린트/포맷 설정 |
| 3 | [@skills/quality-mypy/SKILL.md] | mypy 타입 검사 설정 |
| 4 | [@skills/quality-bandit/SKILL.md] | Bandit 보안 검사 설정 (Strict) |
| 5 | [@skills/quality-notebook/SKILL.md] | Notebook 품질 설정 (DS) |
| 6 | [@skills/quality-precommit/SKILL.md] | pre-commit 훅 설정 |
| 7 | [@skills/setup-logging/SKILL.md] | 로깅 설정 (선택) |

---

## 설정 프로파일

| 프로파일 | 도구 | 용도 |
|----------|------|------|
| **Minimal** | ruff | 빠른 시작, 개인 프로젝트 |
| **Standard** | ruff + mypy + pre-commit + logging | 팀 프로젝트, 중규모 앱 (권장) |
| **Strict** | ruff + mypy + bandit + pre-commit + logging (JSON) | 프로덕션 배포, API 서버 |
| **DS** | ruff (DS) + mypy + nbtools + pre-commit + logging | 데이터 분석, ML 프로젝트 |

**프로파일별 도구 조합 상세**: [@templates/skill-examples/setup-quality/profile-comparison.md]

---

## 실행 프로세스

```
1. 프로젝트 분석
   - Notebook 존재 여부
   - FastAPI/Django 사용 여부
   - 테스트 디렉토리 존재 여부
   → 권장 프로파일 결정

2. 프로파일 선택 (AskUserQuestion)
   - 자동 감지 프로파일 확인
   - 또는 수동 선택

3. 도구 설치
   - uv add --dev [tools]

4. 설정 파일 생성
   - pyproject.toml 업데이트
   - .pre-commit-config.yaml 생성

5. 초기화
   - pre-commit install
   - nbstripout --install (DS)
   - 첫 실행 검증
```

### AskUserQuestion 활용

**지점 1: 프로파일 선택**

플래그 없을 때 대화형으로 프로파일 선택.

**지점 2: 프로젝트 타입 확인**

자동 감지 결과를 사용자에게 확인.

**지점 3: 로깅 포함 여부**

setup-logging 함께 실행 여부 확인.

**상세 질문 형식**: [@templates/skill-examples/setup-quality/askuserquestion-examples.md]

---

## 설정 참조

**각 도구의 설정은 해당 스킬을 참조 (단일 소스 원칙)**:

- **Ruff**: [@skills/quality-ruff/SKILL.md]
- **mypy**: [@skills/quality-mypy/SKILL.md]
- **Bandit**: [@skills/quality-bandit/SKILL.md]
- **Pre-commit**: [@skills/quality-precommit/SKILL.md]
- **Notebook**: [@skills/quality-notebook/SKILL.md]
- **Logging**: [@skills/setup-logging/SKILL.md]

### 프로파일별 설정값 요약

| 도구 | Minimal | Standard | Strict | DS |
|------|---------|----------|--------|-----|
| Ruff | 기본 | 기본 | 전체 | DS 특화 |
| mypy | - | 기본 | strict | 느슨 |
| Bandit | - | - | ✓ | - |
| Pre-commit | 기본 | 전체 | 전체 | notebook |
| Logging | - | 텍스트 | JSON | 텍스트 |

---

## project-init 연계

project-init 워크플로우에서 자동 호출:

```
/project-init "my-project" --type=ds
    |
    +-- scaffold-structure
    +-- setup-quality --ds    ← 자동 호출
    +-- setup-uv-env
```

---

## 출력 예시

```
╔══════════════════════════════════════════════════════════════╗
║                    QUALITY SETUP COMPLETE                     ║
╠══════════════════════════════════════════════════════════════╣
║ Profile: Standard                                             ║
╚══════════════════════════════════════════════════════════════╝

✅ 설치된 도구:
   • ruff 0.8.6
   • mypy 1.14.1
   • pre-commit 4.0.1

✅ 생성된 파일:
   • pyproject.toml (ruff, mypy 설정 추가)
   • .pre-commit-config.yaml

✅ 초기화 완료:
   • pre-commit hooks 설치됨
   • commit-msg hook 설치됨

📋 다음 단계:
   1. `uv run pre-commit run --all-files` 로 전체 검사
   2. 필요시 pyproject.toml 설정 조정
   3. `uv run ruff check . --fix` 로 자동 수정
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/quality-precommit/SKILL.md] | Pre-commit 설정 |
| [@skills/quality-ruff/SKILL.md] | Ruff 설정 |
| [@skills/quality-mypy/SKILL.md] | mypy 설정 |
| [@skills/quality-bandit/SKILL.md] | Bandit 설정 |
| [@skills/quality-notebook/SKILL.md] | Notebook 품질 설정 |
| [@skills/setup-logging/SKILL.md] | 로깅 설정 자동화 |
| [@skills/project-init/SKILL.md] | 프로젝트 초기화 |
| [@skills/code-review/SKILL.md] | 코드 리뷰 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-27 | 1.2.0 | 보수적 리팩토링 - 424→296줄. 다이어그램 간소화 |
| 2026-01-21 | 1.1.0 | setup-logging 통합 (standard 이상 프로파일) |
| 2026-01-21 | 1.0.0 | 초기 생성 - 품질 도구 일괄 설정 |

## Gotchas (실패 포인트)

- pre-commit install 누락 시 hook이 동작 안 함 — 설치 후 반드시 확인
- ruff와 mypy 설정이 pyproject.toml에 없으면 기본값 적용 — 팀 기준 불일치
- bandit false positive 많음 — nosec 주석 이유와 함께 사용
