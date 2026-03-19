---
name: convention-folder-structure
triggers:
  - "convention folder structure"
description: 프로젝트 폴더 구조 가이드. monorepo, single pkg, DS, Agent 구조.
user-invocable: true
---

# convention-folder-structure

## Python Monorepo (uv workspace) — 현재 프로젝트 구조

```
project-root/
├── pyproject.toml          # workspace root
├── uv.lock
├── agents/                 # Agent implementations
│   └── {agent_name}/
│       ├── pyproject.toml
│       ├── src/{agent_name}/
│       └── tests/
├── libs/                   # Shared libraries
│   └── {lib_name}/
│       ├── pyproject.toml
│       ├── src/{lib_name}/
│       └── tests/
└── apps/                   # CLI applications
    └── cli_runner/
```

**상황 1**: 새 library 추가 시 → `libs/{name}/src/{name}/__init__.py` 구조 필수
**상황 2**: 여러 agent가 공통 utility 사용 시 → `libs/utils/`에 공통 코드

## Single Package 구조

```
package/
├── pyproject.toml
├── src/package_name/
│   ├── __init__.py
│   ├── py.typed
│   └── module.py
└── tests/
    ├── __init__.py         # pytest 탐색 필수
    └── test_module.py
```

**상황 1**: `tests/__init__.py` 없으면 pytest가 test를 발견하지 못함 → 필수 생성
**상황 2**: `src/` layout 없이 flat 구조 → import 충돌 위험. `src/` 사용

## Data Science 프로젝트 구조

```
ds-project/
├── notebooks/              # 탐색적 분석 (Jupyter)
├── src/                    # 재사용 가능한 코드
│   └── {domain}/
├── data/
│   ├── raw/                # 원본 (수정 금지)
│   ├── processed/          # 전처리 완료
│   └── output/             # 결과물
└── tests/
```

**상황 1**: notebook 함수 3개 이상 반복 사용 → `src/`로 추출
**상황 2**: raw data 수정 → 금지. processed/에 별도 저장

## 도메인별 분류 원칙

기능/도메인 기반 분류 (type 기반 금지):

```
# 올바른 분류
libs/data_processing/domains/boundary/
libs/data_processing/domains/transit/

# 금지 (type 기반)
utils/
helpers/
models/
```

**상황 1**: 모든 utility를 `utils/`에 몰아넣기 → 도메인별로 분리
**상황 2**: 에이전트 도구를 `tools/`에 몰아넣기 → 각 에이전트 폴더 안에 위치

## Gotchas (실패 포인트)

- 하이픈 포함 디렉터리 `grid-population/` → Python import 불가 — `grid_population/`으로 변경
- `__init__.py` 누락 시 패키지로 인식 안 됨
- 모듈이 너무 평탄한 구조 (`utils.py` 하나에 모든 것) → 도메인별 분리 필요
- 중첩 5단계 이상은 탐색 어려움 — 구조 단순화 검토
