---
name: quality-notebook
triggers:
  - "quality notebook"
description: Jupyter Notebook 품질 관리 스킬. nbstripout, nbdime, nbqa를 활용하여 노트북 품질을 관리한다. Data Science 프로젝트의 노트북 협업 환경을 구축한다.
argument-hint: "[init|clean|diff|lint] - Notebook 품질 작업"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: Jupyter Notebook 품질 관리를 담당한다. nbstripout (출력 제거), nbdime (diff/merge), nbqa (린터 적용) 설정을 수행한다.
agent: Notebook 품질 관리 전문가. 노트북의 버전 관리, 코드 품질, 협업 환경을 최적화한다.
hooks:
  pre_execution: []
  post_execution: []
category: 품질 관리
skill-type: Atomic
references:
  - "@skills/convention-jupyter-setup/SKILL.md"
referenced-by:
  - "@skills/setup-quality/SKILL.md"

---
# Notebook 품질 관리

Jupyter Notebook 품질 관리 환경을 구성하고 관리한다.

## 목적

- nbstripout: 커밋 전 노트북 출력 자동 제거
- nbdime: 노트북 diff/merge 도구
- nbqa: 노트북에 린터/포맷터 적용
- Git 통합 설정

## 사용법

```
/quality-notebook init               # 기본: 설치만 (비활성화)
/quality-notebook init --enable      # 설치 + 활성화
/quality-notebook init --keep-output # 활성화 + 출력 유지
/quality-notebook clean              # 노트북 출력 제거
/quality-notebook diff               # 노트북 diff 설정
/quality-notebook lint               # nbqa 린트 검사
```

---

## 도구 설치

```bash
# 전체 설치
uv add --dev nbstripout nbdime nbqa

# 개별 설치
uv add --dev nbstripout    # 출력 제거
uv add --dev nbdime        # diff/merge
uv add --dev nbqa          # 린터 적용
```

---

## 1. nbstripout 설정

### 목적

Git 커밋 전 노트북의 출력(output), 메타데이터, 실행 카운트를 자동 제거하여 깔끔한 버전 관리를 지원한다.

**설치 vs 활성화**:
- **기본**: nbstripout 패키지만 설치 (Git filter 비활성화)
- **--enable**: Git filter 활성화 (.gitattributes 생성)
- **--keep-output**: 활성화 + 출력 유지 옵션

### Git 통합 (--enable 플래그 시에만)

```bash
# 기본 설치 (비활성화)
uv add --dev nbstripout

# --enable 플래그 사용 시 활성화
uv run nbstripout --install

# 전역 설치
uv run nbstripout --install --global

# 설치 확인
cat .git/config | grep -A 5 filter
```

### .gitattributes

```gitattributes
# Notebook output stripping
*.ipynb filter=nbstripout
*.ipynb diff=ipynb
```

### 옵션

```bash
# 출력만 제거 (메타데이터 유지)
uv run nbstripout --keep-output notebook.ipynb

# 실행 카운트 유지
uv run nbstripout --keep-count notebook.ipynb

# 특정 메타데이터 유지
uv run nbstripout --extra-keys "metadata.kernelspec" notebook.ipynb
```

### pyproject.toml

```toml
[tool.nbstripout]
keep_count = true
keep_output = false
extra_keys = [
    "metadata.kernelspec",
    "metadata.language_info",
]
drop_empty_cells = true
```

### 수동 실행

```bash
# 단일 파일
uv run nbstripout notebook.ipynb

# 전체 노트북
uv run nbstripout notebooks/*.ipynb

# dry-run (변경 없이 확인)
uv run nbstripout --dry-run notebook.ipynb
```

---

## 2. nbdime 설정

### 목적

노트북 전용 diff/merge 도구로, 셀 단위 비교와 출력 결과 비교를 지원한다.

### Git 통합

```bash
# Git diff/merge 설정
uv run nbdime config-git --enable

# 전역 설정
uv run nbdime config-git --enable --global

# 설정 확인
git config --list | grep nbdime
```

### 웹 기반 diff

```bash
# 웹 브라우저에서 diff
uv run nbdiff-web notebook_v1.ipynb notebook_v2.ipynb

# merge 도구
uv run nbmerge-web base.ipynb local.ipynb remote.ipynb merged.ipynb
```

### 터미널 diff

```bash
# 터미널에서 diff
uv run nbdiff notebook_v1.ipynb notebook_v2.ipynb

# 상세 출력
uv run nbdiff --details notebook_v1.ipynb notebook_v2.ipynb
```

### .gitattributes

```gitattributes
*.ipynb diff=jupyternotebook
*.ipynb merge=jupyternotebook
```

---

## 3. nbqa 설정

### 목적

기존 Python 린터/포맷터를 노트북에 적용한다. Ruff, mypy, Black 등을 노트북 코드 셀에 실행할 수 있다.

### 기본 사용법

```bash
# Ruff 린트
uv run nbqa ruff notebooks/

# Ruff 포맷
uv run nbqa ruff --fix notebooks/
uv run nbqa ruff-format notebooks/

# mypy 타입 검사
uv run nbqa mypy notebooks/

# isort
uv run nbqa isort notebooks/
```

### pyproject.toml

```toml
[tool.nbqa.addopts]
ruff = ["--extend-ignore=E402"]  # 노트북에서 import 순서 무시
mypy = ["--ignore-missing-imports"]

[tool.nbqa.files]
ruff = "^notebooks/"

[tool.nbqa.md]
# 마크다운 셀도 검사 (선택)
mdformat = true
```

### 특수 규칙

```toml
[tool.nbqa.addopts]
ruff = [
    "--extend-ignore=E402",   # import 순서
    "--extend-ignore=F401",   # 미사용 import (탐색용)
    "--extend-ignore=E501",   # 줄 길이
]
```

---

## Pre-commit 통합

### .pre-commit-config.yaml

```yaml
repos:
  # Notebook 출력 제거
  - repo: https://github.com/kynan/nbstripout
    rev: 0.8.1
    hooks:
      - id: nbstripout
        args: [--keep-count]

  # Notebook 린트
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.9.1
    hooks:
      - id: nbqa-ruff
        args: [--fix, --extend-ignore=E402]
      - id: nbqa-ruff-format

  # Notebook diff 설정 확인
  - repo: local
    hooks:
      - id: nbdime-check
        name: Check nbdime config
        entry: nbdime config-git --enable
        language: python
        additional_dependencies: [nbdime]
        pass_filenames: false
        always_run: true
```

---

## 사용 시나리오별 설정

### 시나리오 1: 교육/튜토리얼 (기본)

출력 결과를 Git에 포함해야 하는 경우.

```bash
# nbstripout 설치만 (비활성화)
/quality-notebook init
```

**특징**:
- 패키지만 설치됨
- .gitattributes 생성 안 됨
- 노트북 출력이 Git에 커밋됨

### 시나리오 2: 프로덕션 협업 (--enable)

팀 협업 시 출력 제거가 필요한 경우.

```bash
# 설치 + 활성화
/quality-notebook init --enable
```

**특징**:
- Git filter 활성화
- .gitattributes에 `*.ipynb filter=nbstripout` 추가
- 커밋 시 자동으로 출력 제거

### 시나리오 3: 하이브리드 (--keep-output)

출력은 유지하되 메타데이터만 제거.

```bash
# 활성화 + 출력 유지
/quality-notebook init --keep-output
```

**특징**:
- Git filter 활성화
- pyproject.toml에 `keep_output = true` 설정
- 실행 결과는 유지, 메타데이터만 제거

---

## 워크플로우

### 초기 설정

```bash
# 1. 도구 설치
uv add --dev nbstripout nbdime nbqa

# 2. Git 통합
uv run nbstripout --install
uv run nbdime config-git --enable

# 3. .gitattributes 생성
cat >> .gitattributes << 'EOF'
*.ipynb filter=nbstripout
*.ipynb diff=jupyternotebook
*.ipynb merge=jupyternotebook
EOF

# 4. pre-commit 설정
uv run pre-commit install
```

### 일일 작업

```bash
# 노트북 작업 후 린트
uv run nbqa ruff --fix notebooks/

# 커밋 (nbstripout 자동 실행)
git add notebooks/
git commit -m "feat: add analysis notebook"
```

### 코드 리뷰

```bash
# PR에서 노트북 diff 확인
uv run nbdiff-web main..feature-branch -- notebooks/analysis.ipynb

# 충돌 해결
uv run nbmerge-web base.ipynb ours.ipynb theirs.ipynb merged.ipynb
```

---

## 프로젝트 구조

```
project/
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_training.ipynb
├── src/
│   └── utils/
├── .gitattributes
├── .pre-commit-config.yaml
└── pyproject.toml
```

---

## 베스트 프랙티스

### 1. 버전 관리

- 항상 nbstripout 사용하여 출력 제거
- 큰 출력이 필요한 경우 별도 파일로 저장
- 데이터 파일은 `.gitignore`에 추가

### 2. 코드 품질

- nbqa로 린트 검사 수행
- 복잡한 로직은 `.py` 모듈로 분리
- 매직 넘버 대신 설정 파일 사용

### 3. 협업

- nbdime으로 diff/merge 설정
- 노트북당 하나의 주제
- 명확한 마크다운 설명 포함

### 4. 구조화

```python
# 노트북 시작 부분
# %% [markdown]
# # 노트북 제목
# ## 목적
# 이 노트북의 목적을 설명

# %%
# 설정 및 임포트
import pandas as pd
from src.utils import helper

# %%
# 데이터 로드
# ...
```

---

## 트러블슈팅

### nbstripout이 작동하지 않을 때

```bash
# 필터 재설치
uv run nbstripout --uninstall
uv run nbstripout --install

# .gitattributes 확인
cat .gitattributes
```

### nbdime merge 충돌

```bash
# 수동 merge
uv run nbmerge base.ipynb local.ipynb remote.ipynb -o merged.ipynb

# 웹 도구 사용
uv run nbmerge-web base.ipynb local.ipynb remote.ipynb merged.ipynb
```

### nbqa 오류

```bash
# 의존성 확인
uv run nbqa --version

# 상세 오류 출력
uv run nbqa ruff notebooks/ --verbose
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/quality-precommit/SKILL.md] | Pre-commit hook 설정 |
| [@skills/quality-ruff/SKILL.md] | Ruff 린터 설정 |
| [@skills/convention-jupyter-setup/SKILL.md] | Jupyter 노트북 코딩 컨벤션 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.2.0 | nbstripout 옵션화: 기본 비활성화, --enable/--keep-output 플래그 추가 |
| 2026-01-28 | 1.1.0 | references 수정: convention-jupyter-setup 참조 추가, 잘못된 스킬명 교체 |
| 2026-01-21 | 1.0.0 | 초기 생성 - Notebook 품질 관리 |

## Gotchas (실패 포인트)

- nbstripout 미설치 시 output이 그대로 commit됨 — 민감정보 노출 위험
- nbqa 실행 시 Python 환경이 다르면 import 오류 발생
- 노트북 셀 실행 순서가 바뀌면 재현성 깨짐 — Restart & Run All 확인 필수
- `%autoreload` 설정 없으면 모듈 변경 후 커널 재시작 필요
