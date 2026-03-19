---
name: extract-module-from-notebook
triggers:
  - "extract module from notebook"
description: "Jupyter Notebook에서 반복 사용되는 함수를 자동으로 src/ 모듈로 추출한다. convention-jupyter-setup의 '함수 3개 이하' 규칙을 자동으로 준수하도록 리팩토링을 지원한다."
argument-hint: "<notebook_path> [--threshold 3] - 노트북 경로 및 함수 개수 임계값"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: |
  Jupyter Notebook에서 함수 정의가 많아질 때 자동으로 모듈로 추출한다.
  convention-jupyter-setup의 "함수 3개 이하" 규칙 준수를 자동화한다.
agent: |
  노트북 리팩토링 전문가.
  함수 추출, import 문 생성, 노트북 정리를 자동으로 수행한다.
hooks:
  pre_execution: []
  post_execution: []
category: 기타
skill-type: Atomic
references:
  - "@skills/convention-jupyter-setup/SKILL.md"
referenced-by: []

---
# 노트북에서 모듈 추출 (역방향)

Jupyter Notebook에서 반복 사용되는 함수를 자동으로 `src/` 모듈로 추출한다.

## 목적

- **함수 3개 이하** 규칙 자동 준수 (convention-jupyter-setup)
- 노트북 내 함수 정의를 모듈로 리팩토링
- 코드 재사용성 향상
- 노트북 가독성 개선

## 사용법

```bash
/extract-module-from-notebook <notebook_path> [--threshold 3]
```

**예시**:
```bash
# 함수 3개 이상이면 추출
/extract-module-from-notebook notebooks/03_analysis.ipynb

# 임계값 변경 (5개 이상)
/extract-module-from-notebook notebooks/03_analysis.ipynb --threshold 5
```

---

## 워크플로우

### Phase 1: 노트북 분석

**1.1 노트북 로드**

```python
import json
from pathlib import Path

def load_notebook(path: Path) -> dict:
    """노트북 파일 로드."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

**1.2 함수 추출**

```python
import ast

def extract_functions(notebook: dict) -> list[dict]:
    """노트북에서 함수 정의 추출."""
    functions = []

    for idx, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue

        # 셀 소스를 문자열로 변환
        source = ''.join(cell['source'])

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        # 함수 정의 찾기
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Private 함수 제외
                if node.name.startswith('_'):
                    continue

                functions.append({
                    'name': node.name,
                    'cell_index': idx,
                    'source': ast.unparse(node),
                    'docstring': ast.get_docstring(node),
                    'lineno': node.lineno
                })

    return functions
```

**1.3 추출 대상 결정**

```python
def should_extract(functions: list[dict], threshold: int = 3) -> bool:
    """함수 개수가 임계값을 초과하는지 확인."""
    return len(functions) > threshold
```

### Phase 2: 모듈 생성

**2.1 모듈 파일명 결정**

```python
def get_module_path(notebook_path: Path) -> Path:
    """노트북 경로에서 모듈 경로 결정."""
    # notebooks/03_analysis.ipynb → src/analysis_utils.py

    notebook_name = notebook_path.stem  # 03_analysis
    # 번호 제거
    clean_name = notebook_name.lstrip('0123456789_')  # analysis

    module_name = f"{clean_name}_utils.py"
    src_dir = Path('src')

    if not src_dir.exists():
        src_dir = Path.cwd() / 'src'

    return src_dir / module_name
```

**2.2 모듈 파일 생성**

```python
def create_module(functions: list[dict], output_path: Path):
    """추출된 함수로 모듈 파일 생성."""
    from datetime import datetime

    # 파일 헤더
    header = f'''"""
유틸리티 함수 모듈.

Jupyter Notebook에서 추출된 함수들.

Author: Auto-generated
Created: {datetime.now().strftime("%Y-%m-%d")}
Modified: {datetime.now().strftime("%Y-%m-%d")}
"""

from pathlib import Path
import numpy as np
import pandas as pd


'''

    # 함수 정의들
    function_bodies = '\n\n'.join([f['source'] for f in functions])

    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(function_bodies)
        f.write('\n')
```

### Phase 3: 노트북 업데이트

**3.1 함수 정의 제거**

```python
def remove_function_definitions(notebook: dict, functions: list[dict]) -> dict:
    """노트북에서 함수 정의 셀 제거 또는 주석 처리."""
    updated_cells = []
    removed_cell_indices = set()

    for func in functions:
        removed_cell_indices.add(func['cell_index'])

    for idx, cell in enumerate(notebook['cells']):
        if idx not in removed_cell_indices:
            updated_cells.append(cell)

    notebook['cells'] = updated_cells
    return notebook
```

**3.2 Import 문 추가**

```python
def add_import_cell(notebook: dict, module_path: Path, functions: list[dict]) -> dict:
    """노트북에 import 셀 추가."""
    # 모듈 import 경로 계산
    # src/analysis_utils.py → from src.analysis_utils import ...
    module_import = '.'.join(module_path.with_suffix('').parts)
    func_names = [f['name'] for f in functions]

    import_cell = {
        'cell_type': 'code',
        'metadata': {},
        'source': [
            f'# 추출된 함수 import\n',
            f'from {module_import} import {", ".join(func_names)}\n'
        ],
        'outputs': [],
        'execution_count': None
    }

    # Cell 2 (import 셀) 뒤에 삽입
    notebook['cells'].insert(2, import_cell)
    return notebook
```

**3.3 노트북 저장**

```python
def save_notebook(notebook: dict, path: Path):
    """업데이트된 노트북 저장."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
```

---

## 실행 예시

### Before: notebooks/03_analysis.ipynb (함수 5개)

```python
# Cell 3
def calculate_mean(data):
    """평균 계산."""
    return np.mean(data)

def calculate_std(data):
    """표준편차 계산."""
    return np.std(data)

# Cell 4
def normalize(data):
    """정규화."""
    return (data - data.mean()) / data.std()

def filter_outliers(data, threshold=3):
    """이상치 제거."""
    z_scores = np.abs((data - data.mean()) / data.std())
    return data[z_scores < threshold]

def plot_distribution(data):
    """분포 시각화."""
    import matplotlib.pyplot as plt
    plt.hist(data, bins=30)
    plt.show()

# Cell 5
df = pd.read_csv('data.csv')
normalized = normalize(df['value'])
```

### After 1: src/analysis_utils.py (생성됨)

```python
"""
유틸리티 함수 모듈.

Jupyter Notebook에서 추출된 함수들.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def calculate_mean(data):
    """평균 계산."""
    return np.mean(data)


def calculate_std(data):
    """표준편차 계산."""
    return np.std(data)


def normalize(data):
    """정규화."""
    return (data - data.mean()) / data.std()


def filter_outliers(data, threshold=3):
    """이상치 제거."""
    z_scores = np.abs((data - data.mean()) / data.std())
    return data[z_scores < threshold]


def plot_distribution(data):
    """분포 시각화."""
    import matplotlib.pyplot as plt
    plt.hist(data, bins=30)
    plt.show()
```

### After 2: notebooks/03_analysis.ipynb (함수 0개)

```python
# Cell 1: 자동 리로드
%load_ext autoreload
%autoreload 2

# Cell 2: Import
import numpy as np
import pandas as pd

# Cell 3: 추출된 함수 import (자동 추가)
from src.analysis_utils import (
    calculate_mean,
    calculate_std,
    normalize,
    filter_outliers,
    plot_distribution
)

# Cell 4: 분석 (함수 정의 제거, 사용만 남음)
df = pd.read_csv('data.csv')
normalized = normalize(df['value'])
```

---

## 추출 기준

### 추출 대상 (✅)

- Public 함수 (이름이 `_`로 시작하지 않음)
- 3번 이상 사용되는 함수 (기본값)
- Docstring이 있는 함수 (우선순위 높음)

### 추출 제외 (❌)

- Private 함수 (`_helper()`)
- 1-2번만 사용되는 함수
- 노트북 특화 함수 (예: Jupyter 매직 사용)
- Inline 람다 함수

---

## 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--threshold` | 3 | 함수 개수 임계값 |
| `--keep-original` | False | 원본 노트북 백업 유지 |
| `--dry-run` | False | 실제 변경 없이 미리보기만 |

**예시**:
```bash
# 함수 5개 이상만 추출
/extract-module-from-notebook notebooks/03_analysis.ipynb --threshold 5

# 원본 백업
/extract-module-from-notebook notebooks/03_analysis.ipynb --keep-original

# 미리보기
/extract-module-from-notebook notebooks/03_analysis.ipynb --dry-run
```

---

## 워크플로우 통합

### 정방향 + 역방향 사이클

```bash
# 1. 모듈 구현
src/data_loader.py

# 2. 노트북 자동 생성
/generate-notebook-from-module src/data_loader.py
→ notebooks/03_data_loader.ipynb

# 3. 노트북에서 작업하다가 함수가 늘어남
# (함수 5개 추가)

# 4. 함수 자동 추출
/extract-module-from-notebook notebooks/03_data_loader.ipynb
→ src/data_loader_utils.py 생성
→ notebooks/03_data_loader.ipynb 정리

# 5. 다시 노트북은 깔끔해짐 (함수 0개)
```

---

## 체크리스트

스킬 실행 후:

- [ ] 생성된 모듈 파일 확인 (`src/*_utils.py`)
- [ ] 모듈에 추출된 함수 검토
- [ ] 노트북에서 함수 정의 제거 확인
- [ ] 노트북에 import 문 추가 확인
- [ ] 노트북 전체 실행하여 동작 검증
- [ ] `%autoreload` 설정으로 모듈 변경 자동 반영 확인

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-jupyter-setup/SKILL.md] | 함수 3개 이하 규칙 정의 |
| [@skills/generate-notebook-from-module/SKILL.md] | 모듈 → 노트북 (정방향) |
| [@skills/check-notebook-coverage/SKILL.md] | 모듈-노트북 커버리지 검증 |

---

## 한계 및 주의사항

**자동 추출 한계**:
- 복잡한 의존성이 있는 함수는 수동 확인 필요
- 전역 변수를 사용하는 함수는 파라미터로 변경 필요
- Jupyter 매직 명령을 사용하는 함수는 추출 불가

**수동 확인 필요**:
- 추출된 함수의 파라미터가 올바른지
- 모듈에서 필요한 import 문이 누락되지 않았는지
- 노트북 실행 결과가 이전과 동일한지

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-27 | 1.0.0 | 초기 생성 - 노트북에서 함수 자동 추출 |
