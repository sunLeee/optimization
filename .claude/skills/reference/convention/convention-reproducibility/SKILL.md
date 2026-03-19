---
name: convention-reproducibility
triggers:
  - "convention reproducibility"
description: "재현성(Reproducibility) 컨벤션 참조 스킬. Random seed 고정, 버전 관리, 환경 정보 기록으로 동일한 결과 재생성을 보장한다."
argument-hint: "[섹션] - seed, versioning, environment, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  데이터 분석 및 ML 실험의 재현성 확보 가이드를 제공한다.
  과학적 연구의 필수 요소인 재현성을 코드로 구현한다.
agent: |
  재현성 전문가.
  Random seed, 버전 관리, 환경 설정의 모범 사례를 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 재현성(Reproducibility) 컨벤션

데이터 분석 및 기계학습 실험에서 동일 결과를 재생성하기 위한 규칙.

## 목적

- **Random seed 고정**: 난수 생성 결정화
- **버전 관리**: 패키지 버전 명시
- **환경 정보 기록**: 실행 환경 추적
- **코드 재사용**: 특정 시점 결과 재현 가능

---

## 1. Random Seed 고정

### 1.1 핵심 원칙

**규칙**: 모든 난수 생성기를 동일한 seed로 초기화.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""재현성을 고려한 데이터 분석 모듈.

Author: taeyang lee
Created: 2026-01-21 10:00(KST, UTC+09:00)
Modified: 2026-01-21 10:00(KST, UTC+09:00)
"""

# ===== 재현성 설정 (반드시 최상단에) =====
import random
import numpy as np
import torch
import tensorflow as tf

RANDOM_SEED = 42

def set_random_seed(seed: int) -> None:
    """모든 난수 생성기의 seed를 설정한다.

    Args:
        seed (int): 설정할 seed 값.

    Logics:
        1. Python random 모듈 seed 설정.
        2. NumPy 난수 생성기 초기화.
        3. PyTorch seed 설정.
        4. TensorFlow seed 설정.
        5. CUDA (GPU) seed 설정.
    """
    # Python random
    random.seed(seed)

    # NumPy
    np.random.seed(seed)

    # PyTorch
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # 모든 GPU

    # TensorFlow
    tf.random.set_seed(seed)

# 프로그램 시작 시 호출
set_random_seed(RANDOM_SEED)
```

### 1.2 라이브러리별 Seed 설정

| 라이브러리 | 설정 방법 | 영향 범위 |
|-----------|---------|---------|
| **Python random** | `random.seed(42)` | 내장 난수 생성 |
| **NumPy** | `np.random.seed(42)` | NumPy 배열 연산 |
| **scikit-learn** | `random_state=42` (파라미터) | 모델 학습, 데이터 분할 |
| **PyTorch** | `torch.manual_seed(42)` | 신경망 가중치 초기화 |
| **TensorFlow** | `tf.random.set_seed(42)` | 모델 가중치 |
| **Pandas** | `np.random.seed()` 사용 | DataFrame 샘플링 |

### 1.3 scikit-learn 모델 seed 설정

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42  # ← seed 설정
)

# 모델 생성
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,  # ← seed 설정
    n_jobs=-1
)
model.fit(X_train, y_train)
```

### 1.4 시드 설정 검증

```python
def verify_reproducibility(
    func,
    iterations: int = 3,
) -> bool:
    """함수가 재현성을 가지는지 검증한다.

    Args:
        func: 테스트할 함수.
        iterations: 실행 반복 횟수.

    Returns:
        bool: 재현성 여부 (모두 같은 결과면 True).

    Logics:
        1. 함수를 iterations 횟수 실행.
        2. seed 초기화 후 매 실행마다 seed 고정.
        3. 결과 비교.
        4. 모두 일치하면 재현성 확보.
    """
    results = []

    for i in range(iterations):
        set_random_seed(RANDOM_SEED)
        result = func()
        results.append(result)

    # 모든 결과가 동일한지 확인
    first_result = results[0]
    all_same = all(
        np.allclose(r, first_result) if isinstance(r, np.ndarray)
        else r == first_result
        for r in results
    )

    if all_same:
        print(f"✓ 재현성 확보: {iterations}회 동일 결과")
    else:
        print("✗ 재현성 미확보: 결과 불일치")

    return all_same
```

---

## 2. 패키지 버전 관리

### 2.1 requirements.txt 또는 pyproject.toml

```toml
# pyproject.toml
[project]
name = "analysis-project"
version = "1.0.0"

dependencies = [
    "numpy==1.24.0",      # 명시적 버전
    "pandas==2.0.0",
    "scikit-learn==1.2.0",
    "matplotlib==3.6.0",
    "seaborn==0.12.0",
]

[project.optional-dependencies]
dev = [
    "jupyter==1.0.0",
    "jupyterlab==3.6.0",
    "pytest==7.2.0",
]

ml = [
    "torch==2.0.0",
    "tensorflow==2.12.0",
]
```

### 2.2 버전 고정 규칙

| 전략 | 형식 | 용도 |
|------|------|------|
| **정확한 버전** | `numpy==1.24.0` | Production, 재현성 중요 |
| **호환 버전** | `numpy~=1.24.0` | 마이너 업데이트 허용 |
| **범위** | `numpy>=1.24,<2.0` | 유연한 버전 관리 |

### 2.3 현재 환경 버전 내보내기

```python
import subprocess
import json

def export_requirements(output_file: str = 'requirements.txt'):
    """현재 환경의 패키지 버전을 내보낸다.

    Args:
        output_file: 저장할 파일명.

    Logics:
        1. pip freeze 실행.
        2. 결과를 파일로 저장.
        3. 나중에 pip install -r로 복원 가능.
    """
    result = subprocess.run(
        ['pip', 'freeze'],
        capture_output=True,
        text=True
    )

    with open(output_file, 'w') as f:
        f.write(result.stdout)

    print(f"✓ 버전 정보 저장: {output_file}")

# 실행
export_requirements('requirements_frozen.txt')
```

---

## 3. 환경 정보 기록

### 3.1 환경 정보 수집

```python
import json
import platform
from datetime import datetime
from pathlib import Path


def collect_environment_info() -> dict:
    """현재 실행 환경의 정보를 수집한다.

    Returns:
        dict: 환경 정보 딕셔너리.

    Logics:
        1. 실행 시간 기록.
        2. 운영체제 정보.
        3. Python 버전.
        4. 설치된 패키지 버전.
        5. Random seed.
        6. GPU 정보 (필요시).
    """
    import subprocess

    environment = {
        'timestamp': datetime.now().isoformat(),
        'timezone': 'KST (UTC+09:00)',
        'system': platform.system(),
        'system_version': platform.version(),
        'python_version': platform.python_version(),
        'random_seed': RANDOM_SEED,
        'packages': {
            'numpy': np.__version__,
            'pandas': pd.__version__,
            'sklearn': __import__('sklearn').__version__,
            'matplotlib': __import__('matplotlib').__version__,
        }
    }

    # GPU 정보 (CUDA 사용 시)
    try:
        import torch
        environment['pytorch_version'] = torch.__version__
        environment['cuda_available'] = torch.cuda.is_available()
        if torch.cuda.is_available():
            environment['gpu_model'] = (
                torch.cuda.get_device_name(0)
            )
    except ImportError:
        pass

    return environment
```

### 3.2 환경 정보 저장

```python
def save_environment_info(
    output_dir: Path = Path.cwd(),
) -> None:
    """환경 정보를 JSON 파일로 저장한다.

    Args:
        output_dir: 저장 디렉토리.

    Logics:
        1. 환경 정보 수집.
        2. JSON으로 변환.
        3. 타임스탬프 포함하여 저장.
    """
    env_info = collect_environment_info()

    # 파일명에 타임스탬프 포함
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"environment_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(env_info, f, indent=2)

    print(f"✓ 환경 정보 저장: {filename}")
    print(json.dumps(env_info, indent=2))
```

### 3.3 실험 정보 통합 기록

```python
def save_experiment_report(
    output_dir: Path,
    model_results: dict,
    config: dict,
) -> None:
    """실험 전체 정보를 통합 기록한다.

    Args:
        output_dir: 저장 디렉토리.
        model_results: 모델 성능 메트릭.
        config: 실험 설정 (하이퍼파라미터 등).

    Logics:
        1. 환경 정보 수집.
        2. 실험 설정, 결과 추가.
        3. JSON으로 저장하여 나중에 조회 가능.
    """
    report = {
        'environment': collect_environment_info(),
        'config': config,
        'results': model_results,
        'notes': '추가 메모',
    }

    filename = output_dir / 'experiment_report.json'
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ 실험 리포트 저장: {filename}")
```

---

## 4. 코드 버전 관리 (Git)

### 4.1 Git Tag 사용

```bash
# 안정적인 버전 태그 설정
git tag -a v1.0.0 -m "Initial stable release"
git push origin v1.0.0

# 실험 재현 시 해당 버전 체크아웃
git checkout v1.0.0
python analysis.py
```

### 4.2 실험 메타데이터 포함

```python
# notebook 또는 script 최상단
GIT_HASH = "abc123def456"  # git rev-parse --short HEAD
GIT_BRANCH = "main"
MODEL_VERSION = "1.0.0"
ANALYSIS_DATE = "2026-01-21"

print(f"분석 버전: {MODEL_VERSION} (Git: {GIT_HASH})")
```

---

## 5. 재현성 체크리스트

구현 완료 후 다음을 확인하세요:

- [ ] Random seed 고정 (모든 라이브러리)
- [ ] `set_random_seed(RANDOM_SEED)` 호출
- [ ] pyproject.toml에 정확한 패키지 버전 명시
- [ ] 환경 정보 기록 (environment.json)
- [ ] 실행 결과 저장 및 메타데이터 기록
- [ ] Git commit hash 기록
- [ ] 노트북/스크립트 첫 셀에서 seed 설정
- [ ] 최소 2회 이상 실행으로 재현성 검증

---

## 6. 재현성 검증 가이드

### 6.1 단계별 검증

**Step 1**: 초기 실행 후 결과 저장

```python
# 첫 실행
set_random_seed(42)
result_1 = run_analysis()
np.save('result_1.npy', result_1)
```

**Step 2**: 나중에 동일 환경에서 재실행

```python
# 재실행
set_random_seed(42)
result_2 = run_analysis()
np.save('result_2.npy', result_2)

# 비교
assert np.allclose(
    result_1, result_2
), "결과 불일치"
print("✓ 재현성 확보!")
```

### 6.2 다른 환경에서 재현성 검증

```bash
# Docker 컨테이너 사용 (환경 고정)
docker run -v $(pwd):/work my-analysis:v1.0.0 \
    python /work/analysis.py

# 또는 conda 환경 사용
conda env create -f environment.yml
conda activate my-project
python analysis.py
```

---

## 7. 논문/보고서용 재현성 정보

분석 보고서에 포함해야 할 정보:

```markdown
## 재현성 정보

### 환경
- Python: 3.11.0
- 주요 라이브러리:
  - NumPy: 1.24.0
  - Pandas: 2.0.0
  - scikit-learn: 1.2.0

### 설정
- Random Seed: 42
- Train/Test Split: 80/20
- Cross-Validation: 5-fold

### 코드
- Repository: https://github.com/...
- Commit: abc123def456
- Tag: v1.0.0

### 실행 환경
- OS: macOS 13.1
- 실행 시간: 2026-01-21 10:30:45 (KST)
- 소요 시간: 12분 34초

### 재현 방법
1. 저장소 클론: `git clone ...`
2. 환경 설정: `pip install -r requirements.txt`
3. 스크립트 실행: `python analysis.py`
4. 결과 확인: `outputs/` 디렉토리
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |
| [@skills/convention-jupyter-setup/SKILL.md] | Jupyter 노트북 설정 |
| [@skills/convention-data-handling/SKILL.md] | 데이터 처리 |

---

## 참고

- NumPy Random: https://numpy.org/doc/stable/reference/random/
- PyTorch Reproducibility: https://pytorch.org/docs/stable/notes/randomness.html
- TensorFlow Reproducibility: https://www.tensorflow.org/api_docs/python/tf/random/set_seed

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - seed 고정, 버전 관리, 환경 정보 |

## Gotchas (실패 포인트)

- random seed 미설정 시 매 실행마다 결과 달라짐
- pip freeze가 아닌 수동 requirements.txt 관리 시 버전 불일치
- 절대 경로 하드코딩 시 다른 환경에서 실행 불가
- 환경 정보(Python 버전, OS) 미기록 시 재현 불가
