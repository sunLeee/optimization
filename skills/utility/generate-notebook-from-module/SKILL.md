---
name: generate-notebook-from-module
triggers:
  - "generate notebook from module"
description: "Python 모듈 완성 시 대응하는 Jupyter Notebook을 자동 생성한다. AST 파싱으로 public API를 추출하고 사용 예시 템플릿을 제공한다. convention-jupyter-setup의 '모듈 완성 시 노트북 필수' 규칙을 자동화한다."
argument-hint: "<module_path> - Python 모듈 파일 경로"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
model: claude-sonnet-4-6[1m]
context: |
  Python 모듈 구현 완료 후 Jupyter Notebook 생성을 자동화한다.
  모듈의 public API를 분석하여 사용 예시 템플릿을 제공한다.
agent: |
  Jupyter Notebook 생성 전문가.
  AST 파싱으로 모듈 구조를 분석하고, 실행 가능한 노트북 템플릿을 생성한다.
hooks:
  pre_execution: []
  post_execution: []
category: 기타
skill-type: Atomic
references:
  - "@skills/convention-jupyter-setup/SKILL.md"
referenced-by: []

---
# Jupyter Notebook 자동 생성 (모듈 기반)

Python 모듈 완성 시 대응하는 Jupyter Notebook을 자동 생성한다.

## 목적

- **모듈 완성 시 노트북 필수** 규칙 자동화
- 모듈 API를 분석하여 사용 예시 템플릿 제공
- convention-jupyter-setup 규칙 준수
- 노트북 작성 시간 단축

## 사용법

```bash
/generate-notebook-from-module <module_path>
```

**예시**:
```bash
/generate-notebook-from-module src/data_loader.py
→ notebooks/03_data_loader.ipynb 생성

/generate-notebook-from-module src/models/classifier.py
→ notebooks/04_classifier.ipynb 생성
```

---

## 워크플로우

### Phase 1: 모듈 분석

**1.1 AST 파싱**

```python
import ast
from pathlib import Path

def analyze_module(file_path: Path) -> dict:
    """모듈에서 public API 추출."""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    # Public 클래스 추출 (이름이 _로 시작하지 않음)
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
            # 클래스의 public 메서드 추출
            methods = [m.name for m in node.body
                      if isinstance(m, ast.FunctionDef)
                      and not m.name.startswith('_')]
            classes.append({
                'name': node.name,
                'methods': methods,
                'docstring': ast.get_docstring(node)
            })

    # Public 함수 추출
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
            functions.append({
                'name': node.name,
                'docstring': ast.get_docstring(node)
            })

    # Import 문 추출
    imports = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.unparse(node))

    return {
        'classes': classes,
        'functions': functions,
        'imports': imports
    }
```

**1.2 노트북 파일명 결정**

```python
def get_notebook_path(module_path: Path) -> Path:
    """모듈 경로에서 노트북 경로 결정."""
    # src/data_loader.py → notebooks/0X_data_loader.ipynb

    # notebooks/ 디렉토리 확인
    notebooks_dir = Path('notebooks')
    if not notebooks_dir.exists():
        notebooks_dir = Path.cwd() / 'notebooks'

    # 번호 결정 (3단계 우선순위)
    next_num = get_notebook_number(module_path, notebooks_dir)

    # 파일명 생성
    module_name = module_path.stem  # data_loader
    notebook_name = f"{next_num:02d}_{module_name}.ipynb"

    return notebooks_dir / notebook_name


def get_notebook_number(module_path: Path, notebooks_dir: Path) -> int:
    """노트북 번호 결정 (3단계 우선순위)."""

    # 1순위: docs/tasks/ YAML 파싱
    tasks_dir = Path('docs/tasks')
    if tasks_dir.exists():
        task_files = sorted(tasks_dir.glob('*.md'))
        for task_file in task_files:
            # YAML frontmatter에서 순서 추출
            with open(task_file) as f:
                content = f.read()
                if '---' in content:
                    yaml_block = content.split('---')[1]
                    # 모듈명이 task 파일에 언급되는지 확인
                    if module_path.stem in content.lower():
                        # task 순서 번호 추출
                        import re
                        match = re.search(r'order:\s*(\d+)', yaml_block)
                        if match:
                            return int(match.group(1))

    # 2순위: 마지막 번호 + 1
    existing = sorted(notebooks_dir.glob('*.ipynb'))
    if existing:
        numbers = []
        for nb in existing:
            # 파일명에서 숫자 부분 추출 (01, 02, ...)
            import re
            match = re.match(r'(\d+)_', nb.stem)
            if match:
                numbers.append(int(match.group(1)))

        if numbers:
            return max(numbers) + 1

    # 3순위: len(existing) + 1 (기존 로직)
    return len(existing) + 1
```

### Phase 2: 노트북 생성

> **핵심 변경 (v2.0)**: 모든 셀을 **markdown 셀 + code 셀** 쌍으로 생성한다. 설명은 markdown 셀에, 코드는 code 셀에 분리.

**2.1 Cell 구조**

```python
cells = [
    # Markdown + Code 쌍으로 생성
    *create_autoreload_cells(),      # 2 cells (md + code)
    *create_import_cells(module_info, module_path),  # 2 cells
    *create_api_cells(module_info),  # N * 2 cells
    *create_conclusion_cells()       # 2 cells
]
```

**2.2 Cell 1: Jupyter 환경 설정**

```python
def create_autoreload_cells() -> list[dict]:
    """환경 설정 셀 생성 (markdown + code)."""
    return [
        # Markdown Cell
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## 1. Jupyter 환경 설정\n',
                '\n',
                '자동 리로드 및 경고 억제 설정. **노트북 시작 시 반드시 먼저 실행.**\n',
                '\n',
                '> ⚠️ Magic command는 셀 최상단에 작성해야 한다.'
            ]
        },
        # Code Cell
        {
            'cell_type': 'code',
            'metadata': {},
            'source': [
                '%load_ext autoreload\n',
                '%autoreload 2\n',
                '%matplotlib inline\n',
                '\n',
                'import warnings\n',
                'warnings.filterwarnings("ignore", category=DeprecationWarning)\n',
                '\n',
                'print("✓ Jupyter 환경 설정 완료")'
            ],
            'outputs': [],
            'execution_count': None
        }
    ]
```

**2.3 Cell 2: Import**

```python
def create_import_cells(module_info: dict, module_path: Path) -> list[dict]:
    """Import 셀 생성 (markdown + code)."""
    module_import_path = '.'.join(module_path.with_suffix('').parts)
    api_names = [c['name'] for c in module_info['classes']]
    api_names += [f['name'] for f in module_info['functions']]

    return [
        # Markdown Cell
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## 2. 라이브러리 Import\n',
                '\n',
                '**Import 순서**: 표준 라이브러리 → 서드파티 → 로컬 모듈'
            ]
        },
        # Code Cell
        {
            'cell_type': 'code',
            'metadata': {},
            'source': [
                '# 1. 표준 라이브러리\n',
                'import os\n',
                'import sys\n',
                'from pathlib import Path\n',
                'from datetime import datetime\n',
                '\n',
                '# 2. 서드파티 라이브러리\n',
                'import numpy as np\n',
                'import pandas as pd\n',
                'import matplotlib.pyplot as plt\n',
                '\n',
                '# 3. 로컬 모듈\n',
                f'from {module_import_path} import {", ".join(api_names)}\n',
                '\n',
                '# 상수 정의\n',
                'DATA_DIR = Path("data")\n',
                'OUTPUT_DIR = Path("outputs")\n',
                'RANDOM_SEED = 42\n',
                '\n',
                'np.random.seed(RANDOM_SEED)\n',
                'print("✓ 라이브러리 및 설정 완료")'
            ],
            'outputs': [],
            'execution_count': None
        }
    ]
```

**2.4 Cell 3-N: API별 사용 예시**

```python
def create_api_cells(module_info: dict) -> list[dict]:
    """API별 사용 예시 셀 생성 (markdown + code 쌍)."""
    cells = []
    cell_num = 3

    # 클래스별 셀
    for cls in module_info['classes']:
        # Markdown Cell
        cells.append({
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                f'## {cell_num}. {cls["name"]} 사용 예시\n',
                '\n',
                f'{cls["docstring"] or "클래스 설명 없음"}\n',
                '\n',
                '**사용 가능한 메서드**:\n',
                *[f'- `{m}`\n' for m in cls['methods']]
            ]
        })
        # Code Cell
        cells.append({
            'cell_type': 'code',
            'metadata': {},
            'source': [
                f'# TODO: {cls["name"]} 클래스 사용\n',
                f'# instance = {cls["name"]}(...)\n',
                f'# result = instance.{cls["methods"][0] if cls["methods"] else "method"}()\n',
                '# print(result)'
            ],
            'outputs': [],
            'execution_count': None
        })
        cell_num += 1

    # 함수별 셀
    for func in module_info['functions']:
        # Markdown Cell
        cells.append({
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                f'## {cell_num}. {func["name"]} 함수 사용\n',
                '\n',
                f'{func["docstring"] or "함수 설명 없음"}'
            ]
        })
        # Code Cell
        cells.append({
            'cell_type': 'code',
            'metadata': {},
            'source': [
                f'# TODO: {func["name"]} 함수 사용\n',
                f'# result = {func["name"]}(...)\n',
                '# print(result)'
            ],
            'outputs': [],
            'execution_count': None
        })
        cell_num += 1

    return cells
```

**2.5 Cell N+1: 결론**

```python
def create_conclusion_cells() -> list[dict]:
    """결론 셀 생성 (markdown + code)."""
    return [
        # Markdown Cell
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## 결론\n',
                '\n',
                '분석 결과 요약 및 후속 작업.'
            ]
        },
        # Code Cell
        {
            'cell_type': 'code',
            'metadata': {},
            'source': [
                '# TODO: 분석 결과 요약\n',
                'print(f"생성 일시: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")'
            ],
            'outputs': [],
            'execution_count': None
        }
    ]
```

### Phase 3: 노트북 저장

```python
import json

def save_notebook(cells: list[dict], output_path: Path):
    """Jupyter Notebook 형식으로 저장."""
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'
            },
            'language_info': {
                'codemirror_mode': {'name': 'ipython', 'version': 3},
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.11.0'
            }
        },
        'nbformat': 4,
        'nbformat_minor': 5
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
```

---

## 실행 예시

### 입력: src/data_loader.py

```python
"""데이터 로더 모듈."""

from pathlib import Path
import pandas as pd

class DataLoader:
    """CSV 파일을 로드하는 클래스."""

    def __init__(self, file_path: Path):
        """초기화."""
        self.file_path = file_path

    def load(self) -> pd.DataFrame:
        """데이터 로드."""
        return pd.read_csv(self.file_path)

    def validate(self, df: pd.DataFrame) -> bool:
        """데이터 검증."""
        return not df.empty

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """데이터 전처리."""
    return df.dropna()
```

### 출력: notebooks/03_data_loader.ipynb

```
# 번호 03의 결정 이유:
# - 1순위: docs/tasks/feature-x.md에 order: 3 명시 (또는)
# - 2순위: 기존 01, 02 존재 → max(1,2) + 1 = 3 (또는)
# - 3순위: 노트북 2개 존재 → len([01, 02]) + 1 = 3
```

**[Markdown Cell 1]**
```markdown
## 1. Jupyter 환경 설정

자동 리로드 및 경고 억제 설정. **노트북 시작 시 반드시 먼저 실행.**
```

**[Code Cell 1]**
```python
%load_ext autoreload
%autoreload 2
%matplotlib inline

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
print("✓ Jupyter 환경 설정 완료")
```

**[Markdown Cell 2]**
```markdown
## 2. 라이브러리 Import

**Import 순서**: 표준 라이브러리 → 서드파티 → 로컬 모듈
```

**[Code Cell 2]**
```python
from pathlib import Path
import numpy as np
import pandas as pd

from src.data_loader import DataLoader, preprocess_data

DATA_DIR = Path("data")
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
print("✓ 라이브러리 및 설정 완료")
```

**[Markdown Cell 3]**
```markdown
## 3. DataLoader 사용 예시

CSV 파일을 로드하는 클래스.

**사용 가능한 메서드**:
- `load`
- `validate`
```

**[Code Cell 3]**
```python
# TODO: DataLoader 클래스 사용
# loader = DataLoader(DATA_DIR / "file.csv")
# df = loader.load()
# print(df.shape)
```

**[Markdown Cell 4]**
```markdown
## 4. preprocess_data 함수 사용

데이터 전처리.
```

**[Code Cell 4]**
```python
# TODO: preprocess_data 함수 사용
# df_clean = preprocess_data(df)
# print(df_clean.shape)
```

---

## 넘버링 전략

### 우선순위 시스템

노트북 번호는 다음 순서로 결정된다:

```mermaid
flowchart TD
    A[넘버링 시작] --> B{docs/tasks/<br/>존재?}
    B -->|Yes| C[YAML frontmatter<br/>order 필드 파싱]
    C --> D{모듈명<br/>매칭?}
    D -->|Yes| E[order 값 사용]
    D -->|No| F{기존 노트북<br/>존재?}
    B -->|No| F
    F -->|Yes| G[마지막 번호 + 1]
    F -->|No| H[len(existing) + 1]

    E --> I[번호 확정]
    G --> I
    H --> I
```

### 1순위: Task 파일 연동

`docs/tasks/` 디렉토리에 YAML frontmatter가 있는 경우:

```yaml
---
order: 3
module: data_loader
---
```

→ 노트북 번호: **03**

### 2순위: 마지막 번호 + 1

기존: 01_eda.ipynb, 03_model.ipynb (02 삭제됨)

→ max(1, 3) + 1 = **04**

### 3순위: 개수 기반 (기존 로직)

기존: 01, 02, 03 (연속)

→ len([01, 02, 03]) + 1 = **04**

### 충돌 회피

| 상황 | 처리 |
|------|------|
| Task order와 기존 번호 충돌 | Task order 우선 (1순위) |
| 번호 공백 (01, 03, ...) | 마지막 번호 +1로 메움 (2순위) |
| 빈 디렉토리 | 01부터 시작 (3순위) |

---

## 자동화 범위

| 항목 | 자동 생성 | 사용자 작성 |
|------|----------|-----------|
| **Cell 1-2** | ✅ 완전 자동 | |
| **Import 문** | ✅ 모듈 API 기반 | |
| **API 목록** | ✅ AST 파싱 | |
| **코드 스니펫** | ✅ 최소 예시 | ⚠️ 파라미터 수정 |
| **데이터 출력** | | ❌ 완전히 수동 |
| **분석 로직** | | ❌ 비즈니스 규칙 |

---

## 체크리스트

스킬 실행 후:

- [ ] 생성된 노트북 경로 확인
- [ ] Cell 1 실행: 자동 리로드 설정
- [ ] Cell 2 실행: Import 문 동작 확인
- [ ] Cell 3-N: TODO 주석 확인
- [ ] 각 셀에 실제 코드 작성
- [ ] 노트북 전체 실행하여 검증

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-jupyter-setup/SKILL.md] | 노트북 규칙 참조 |
| [@skills/extract-module-from-notebook/SKILL.md] | 노트북 → 모듈 역방향 추출 |
| [@skills/check-notebook-coverage/SKILL.md] | 모듈-노트북 커버리지 검증 |

---

## 한계 및 주의사항

**자동화 불가능한 부분**:
- 어떤 데이터를 출력할지 (비즈니스 로직)
- 어떤 파라미터를 사용할지 (도메인 지식)
- 어떤 시각화를 그릴지 (분석 목적)

**사용자 책임**:
- TODO 주석을 실제 코드로 채우기
- 실제 파일 경로 입력
- 분석 목표에 맞는 출력 선택

**원칙**:
> 스킬은 "어떻게(How)" 작성할지 알려주지만, "무엇을(What)" 분석할지는 당신이 결정한다.

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-02 | 2.0.0 | **Breaking**: 셀 구조 변경 - markdown + code 셀 쌍으로 생성. convention-jupyter-setup v2.0.0 동기화. Magic keyword 주의사항 추가. |
| 2026-01-28 | 1.1.0 | 넘버링 로직 개선: Task 파일 연동, 마지막 번호 +1 우선순위 |
| 2026-01-27 | 1.0.0 | 초기 생성 - AST 기반 노트북 자동 생성 |
