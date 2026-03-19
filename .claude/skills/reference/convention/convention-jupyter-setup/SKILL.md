---
name: convention-jupyter-setup
triggers:
  - "convention jupyter setup"
description: "Jupyter 노트북 설정 및 구조 컨벤션 참조 스킬. 자동 리로드, 셀 구조, 한글 폰트, 재현성 설정 등 노트북 사용 시 필수 설정을 제공한다."
argument-hint: "[섹션] - setup, structure, visualization, all"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  Jupyter 노트북 사용 시 설정, 구조, 시각화 모범 사례를 제공한다.
  데이터 분석/ML 프로젝트에서 일관된 노트북 환경을 구축한다.
agent: |
  Jupyter 노트북 전문가.
  노트북 자동화, 셀 구조화, 시각화 설정을 명확하게 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by:
  - "@skills/check-notebook-coverage/SKILL.md"
  - "@skills/extract-module-from-notebook/SKILL.md"
  - "@skills/generate-notebook-from-module/SKILL.md"
  - "@skills/quality-notebook/SKILL.md"

---
# Jupyter 노트북 설정 및 구조

Jupyter 노트북 사용 시 준수해야 할 설정 및 구조 규칙.

> **컨벤션 우선순위**: 노트북 규칙 > Python 규칙. 이 스킬의 규칙이 [@skills/convention-python/SKILL.md]를 오버라이드한다.

---

## 0. 컨텍스트 윈도우 제한 (200k 기준)

Claude Code의 최대 컨텍스트 윈도우는 **200k 토큰**이다. 노트북이 컨텍스트의 40%를 초과하지 않도록 제한한다.

| 항목 | 제한 | 근거 |
|------|------|------|
| **노트북 전체** | 1,000줄 이하 | 200k 토큰 중 40% (80k) 할당 |
| **셀 개수** | 20개 이하 | 셀당 평균 50줄 기준 |
| **단일 셀** | 50줄 이하 | 가독성 + 토큰 효율 |
| **출력** | 100행 이하 | 대용량은 파일 저장 |

### 토큰 계산 기준

```
1 토큰 ≈ 4 문자 (영어 기준)
1 토큰 ≈ 1-2 문자 (한글 기준)
200k 토큰 ≈ 800k 문자 (영어) / 400k 문자 (한글)

노트북 할당: 40% = 80k 토큰 ≈ 320k 문자 ≈ 1,000줄
```

---

## 핵심 원칙 (프로젝트 통괄)

**모듈/기능 완성 시 Jupyter Notebook 필수 생성 규칙**

Python 코드로 모듈이나 주요 기능이 완성되면 반드시 대응하는 Jupyter Notebook을 작성한다. 이는 **테스트 우선 철학과 동일한 수준의 필수 규칙**이다.

| 구분 | 내용 |
|------|------|
| **적용 시점** | 모듈 구현 완료 → 단위 테스트 완료 → **노트북 작성** |
| **목적** | 모듈 사용법 검증, API 실행 예시, 재현 가능한 환경 구축 |
| **대상** | 데이터 로더, 전처리 파이프라인, 모델 학습, API 엔드포인트 등 |

**작성 순서**:
1. 모듈 구현 (`src/module.py`)
2. 단위 테스트 작성 (`tests/test_module.py`)
3. **Jupyter Notebook 작성** (`notebooks/0X-module-demo.ipynb`)
4. 노트북에서 실제 사용 시나리오 검증

**예시**:
- 데이터 로더 완성 → `notebooks/01-data-loading.ipynb`
- 전처리 파이프라인 완성 → `notebooks/02-preprocessing.ipynb`
- 모델 학습 함수 완성 → `notebooks/03-model-training.ipynb`

---

## 목적

- 노트북 자동화 설정 (자동 리로드)
- 일관된 셀 구조 (import → 설정 → 분석)
- 재현성 확보 (random seed 고정)
- 시각화 최적화 (한글 폰트, 크기 설정)

## 사용법

```
/convention-jupyter-setup [섹션]
```

| 섹션 | 설명 |
|------|------|
| `setup` | 자동 리로드 및 기본 설정 |
| `structure` | 셀 구조 및 레이아웃 |
| `visualization` | 시각화 설정 |
| `all` | 전체 내용 (기본값) |

---

## 1. 자동 리로드 설정

### 1.1 필수 설정 (첫 번째 셀)

모든 노트북은 **markdown 셀 + code 셀** 쌍으로 시작한다. 설명은 markdown 셀에, 코드는 code 셀에 분리한다.

> **⚠️ Magic Keyword 주의**: `%load_ext`, `%autoreload`, `%matplotlib` 등 magic command는 **셀의 첫 번째 줄**에 작성해야 한다. 주석이나 다른 코드보다 위에 배치할 것.

**Markdown Cell 1:**
```markdown
## 1. Jupyter 환경 설정

자동 리로드 및 경고 억제 설정. **노트북 시작 시 반드시 먼저 실행.**
```

**Code Cell 1:**
```python
%load_ext autoreload
%autoreload 2
%matplotlib inline

# 경고 억제 (선택사항)
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

print("✓ Jupyter 환경 설정 완료")
```

> **Magic Command 위치 규칙**:
> ```python
> # ❌ Bad: magic command 위에 주석/코드
> # 자동 리로드 설정
> %load_ext autoreload
>
> # ✅ Good: magic command가 셀 최상단
> %load_ext autoreload
> %autoreload 2
> # 이후 주석/코드 작성
> ```

### 1.2 라이브러리 Import (두 번째 셀)

**Markdown Cell 2:**
```markdown
## 2. 라이브러리 Import

**Import 순서**: 표준 라이브러리 → 서드파티 → 로컬 모듈
```

**Code Cell 2:**
```python
# 1. 표준 라이브러리
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# 2. 서드파티 라이브러리
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 3. 로컬 모듈 (필요 시)
sys.path.insert(0, str(Path.cwd().parent))
# from my_package.utils import helper_function

# 상수 정의
DATA_DIR = Path.cwd().parent / 'data'
OUTPUT_DIR = Path.cwd().parent / 'outputs'
RANDOM_SEED = 42
FIGURE_SIZE = (12, 6)

# 재현성 설정
np.random.seed(RANDOM_SEED)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

print("✓ 라이브러리 및 설정 완료")
```

---

## 2. 셀 구조

**상세 템플릿**: [@templates/skill-examples/convention-jupyter-setup/cell-structure-examples.md]

**핵심 내용**:
- **markdown + code 셀 쌍**: 모든 셀은 설명(markdown) + 코드(code) 조합
- **표준 8단계 구조**: 설정 → Import → 로드 → EDA → 전처리 → 학습 → 평가 → 결론
- **셀별 작성 규칙**: 각 단계별 필수 항목 및 출력 형식

---

## 3. 시각화 설정

**상세 템플릿**: [@templates/skill-examples/convention-jupyter-setup/visualization-setup.md]

**핵심 내용**:
- **한글 폰트**: OS별 자동 감지 (Mac: AppleGothic, Windows: Malgun Gothic)
- **그래프 스타일**: Seaborn + Matplotlib 일관된 테마
- **인터랙티브 시각화**: folium/plotly는 파일 저장 필수 (인라인 출력 금지)

---

## 4. 재현성 설정

**상세 템플릿**: [@templates/skill-examples/convention-jupyter-setup/reproducibility-setup.md]

**핵심 내용**:
- **Random Seed 고정**: NumPy, Pandas, PyTorch, TensorFlow 모두 고정
- **환경 정보 기록**: Python 버전, 패키지 버전, 실행 시간 JSON 저장
- **메모리 관리**: psutil로 모니터링, gc.collect()로 해제
- **노트북 연계**: `%run` 매직 키워드로 순차 실행 검증

---

## 5. 노트북 파일 명명 규칙

```
01-eda.ipynb                    # 탐색적 데이터 분석
02-preprocessing.ipynb          # 데이터 전처리
03-model-training.ipynb         # 모델 학습
04-evaluation.ipynb             # 평가 및 분석
05-visualization.ipynb          # 최종 시각화
```

**규칙**:
- 순번: 2자리 (01, 02, 03, ...)
- 설명: kebab-case (하이픈 사용), 영문
- 순차적 진행 가능하도록 구성

---

## 6. 셀 태그 (선택사항)

### Cell 태그 사용

```python
# 셀 우측 상단 "Add Tag" → 다음 중 선택:
# - "analysis": 분석 셀
# - "visualization": 시각화 셀
# - "code": 유틸리티 코드
# - "skip": 스킵할 셀
```

### 태그 기반 실행 필터링

```python
# 태그별로 특정 셀만 실행 가능
# (Jupyter Book, nbconvert 등에서 활용)
```

---

## 7. Claude Code 토큰 최적화

Claude Code와 노트북 사용 시 토큰 효율성을 위한 규칙.

### 8.1 하드코딩 금지

```python
# ❌ Bad: 하드코딩
df = pd.read_csv('/Users/user/data/sales.csv')
threshold = 0.8
epochs = 100

# ✓ Good: 상수 정의
DATA_PATH = Path('data/sales.csv')
THRESHOLD = 0.8
N_EPOCHS = 100

df = pd.read_csv(DATA_PATH)
```

**규칙**:
- 경로, 파라미터는 셀 상단에 상수로 정의
- 매직 넘버(0.8, 100 등) 대신 의미 있는 상수명 사용
- `Path` 객체로 경로 관리

### 8.2 함수 정의 최소화

```python
# ❌ Bad: 노트북 내 복잡한 함수 정의
def preprocess(df):
    # 50줄의 복잡한 로직
    ...

def train_model(X, y):
    # 또 다른 50줄
    ...

# ✓ Good: 모듈 분리 + import
from src.preprocessing import preprocess
from src.training import train_model

# 노트북은 실행 흐름만 보여줌
df_clean = preprocess(df)
model = train_model(X, y)
```

**규칙**:
- 노트북 내 함수 정의 **3개 이하**
- 3회 이상 사용되는 함수는 `src/` 모듈로 분리
- `%autoreload` 매직으로 모듈 변경 시 자동 반영

### 8.3 셀 크기 제한

| 항목 | 제한 | 이유 |
|------|------|------|
| **코드 셀** | 50줄 이하 | 토큰 효율성 |
| **출력** | 100행 이하 | 컨텍스트 절약 |
| **이미지** | 별도 저장 | 바이너리 제외 |

```python
# ❌ Bad: 대용량 출력
df.head(1000)  # 1000행 출력

# ✓ Good: 제한된 출력
df.head(10)  # 10행만 확인
df.shape     # 크기 정보만

# ❌ Bad: 전체 DataFrame 출력
print(df)

# ✓ Good: 요약 정보
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.describe())
```

**대용량 출력 처리**:
```python
# 파일로 저장 후 경로만 표시
output_path = OUTPUT_DIR / 'full_results.csv'
df.to_csv(output_path)
print(f"결과 저장: {output_path}")
```

### 7.4 대용량 시각화 출력 제거

**상세 템플릿**: [@templates/skill-examples/convention-jupyter-setup/visualization-setup.md#대용량-시각화-출력-제거]

**핵심 내용**:
- **인라인 출력 금지**: folium, plotly는 파일 저장만 사용
- **토큰 소비량**: folium 5k~20k, plotly 3k~10k 토큰
- **해결책**: nbstripout + `.write_html()` + 출력 제거

---

## 체크리스트

코드 작성 후 다음을 확인하세요:

### 핵심 규칙 (필수)
- [ ] **모듈 완성 시 노트북 생성**: 새 모듈/기능 구현 완료 시 대응하는 `.ipynb` 작성
- [ ] **노트북 전체 1,000줄 이하**: 200k 컨텍스트 윈도우 제한 준수

### 구조 및 설정
- [ ] Cell 1: 자동 리로드 설정 완료
- [ ] Cell 2: Import + 상수 정의
- [ ] Random seed 고정 (재현성)
- [ ] 한글 폰트 설정
- [ ] 각 셀마다 한국어 문서화
- [ ] 파일 명명 규칙 준수 (`01-name.ipynb`, kebab-case)

### 노트북 간 연계
- [ ] `%run` 매직 키워드로 선행 노트북 실행
- [ ] `99-pipeline-test.ipynb`로 전체 파이프라인 검증
- [ ] 순차 실행 가능성 확보

### 토큰 최적화
- [ ] **하드코딩 제거**: 모든 경로/파라미터 상수화
- [ ] **함수 3개 이하**: 복잡한 로직은 src/ 분리
- [ ] **셀 50줄 이하**: 대용량 출력은 파일 저장
- [ ] **인터랙티브 출력 제거**: folium/plotly 인라인 출력 금지
- [ ] 불필요한 출력 억제 (세미콜론 사용)
- [ ] 메모리 관리 (대용량 데이터 후 del)

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |
| [@skills/convention-data-handling/SKILL.md] | 데이터 처리 |
| [@skills/quality-notebook/SKILL.md] | 노트북 품질 도구 |
| [@skills/generate-notebook-from-module/SKILL.md] | 모듈 → 노트북 자동 생성 |
| [@skills/extract-module-from-notebook/SKILL.md] | 노트북 → 모듈 자동 추출 |
| [@skills/check-notebook-coverage/SKILL.md] | 모듈-노트북 커버리지 검증 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-02 | 2.0.0 | **Breaking**: 셀 구조 변경 - docstring을 markdown 셀로 분리. 모든 셀을 "markdown + code" 쌍으로 구성. Jupyter 표준 관행 준수. |
| 2026-01-28 | 1.4.0 | 파일명을 kebab-case로 변경 (`01-name.ipynb`), %run 매직 키워드 통합 섹션 추가 (6.5), @-style 참조 적용, 용어 통일 가이드 제거, 25k→200k 컨텍스트 윈도우 정정 |
| 2026-01-22 | 1.2.0 | 컨텍스트 윈도우 제한 섹션, 컨벤션 우선순위, 대용량 시각화 출력 제거 규칙 추가 |
| 2026-01-22 | 1.1.0 | Claude Code 토큰 최적화 섹션 추가 (하드코딩 금지, 함수 최소화, 셀 크기 제한) |
| 2026-01-21 | 1.0.0 | 초기 생성 - 자동 리로드, 셀 구조, 시각화 설정 |
