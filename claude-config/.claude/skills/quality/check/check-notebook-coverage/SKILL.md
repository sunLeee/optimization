---
name: check-notebook-coverage
triggers:
  - "check notebook coverage"
description: "모듈-노트북 커버리지를 검증한다. '모듈 완성 시 노트북 필수' 규칙 준수 여부를 자동으로 확인하고 누락된 노트북 목록을 보고한다."
argument-hint: "[--src-dir src] [--notebooks-dir notebooks] - 검증 대상 디렉토리"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: |
  모든 모듈에 대응하는 노트북이 존재하는지 검증한다.
  convention-jupyter-setup의 핵심 원칙 준수를 자동화한다.
agent: |
  커버리지 검증 전문가.
  모듈과 노트북의 매핑을 분석하고 누락된 항목을 보고한다.
hooks:
  pre_execution: []
  post_execution: []
category: 코드 검증
skill-type: Atomic
references:
  - "@skills/convention-jupyter-setup/SKILL.md"
referenced-by: []

---
# 모듈-노트북 커버리지 검증

모듈에 대응하는 Jupyter Notebook이 존재하는지 자동으로 검증한다.

## 목적

- **모듈 완성 시 노트북 필수** 규칙 준수 검증
- 누락된 노트북 자동 탐지
- CI/CD 파이프라인 통합
- 프로젝트 문서화 완성도 측정

## 사용법

```bash
/check-notebook-coverage [--src-dir src] [--notebooks-dir notebooks]
```

**예시**:
```bash
# 기본 디렉토리 검증
/check-notebook-coverage

# 커스텀 디렉토리
/check-notebook-coverage --src-dir my_package --notebooks-dir docs/notebooks
```

---

## 검증 로직

### Phase 1: 모듈 수집

**1.1 Python 모듈 탐색**

```python
from pathlib import Path

def find_modules(src_dir: Path) -> list[Path]:
    """src/ 디렉토리에서 Python 모듈 찾기."""
    modules = []

    for py_file in src_dir.rglob('*.py'):
        # 제외 대상
        if py_file.name == '__init__.py':
            continue
        if py_file.name.startswith('_'):
            continue
        if 'test' in py_file.parts:
            continue

        modules.append(py_file)

    return sorted(modules)
```

**1.2 Public API 확인**

```python
import ast

def has_public_api(file_path: Path) -> bool:
    """모듈에 public 클래스/함수가 있는지 확인."""
    with open(file_path) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return False

    for node in tree.body:
        # Public 클래스
        if isinstance(node, ast.ClassDef):
            if not node.name.startswith('_'):
                return True
        # Public 함수
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):
                return True

    return False
```

### Phase 2: 노트북 수집

**2.1 Jupyter Notebook 탐색**

```python
def find_notebooks(notebooks_dir: Path) -> list[Path]:
    """notebooks/ 디렉토리에서 .ipynb 찾기."""
    notebooks = []

    for nb_file in notebooks_dir.glob('*.ipynb'):
        # .ipynb_checkpoints 제외
        if '.ipynb_checkpoints' in nb_file.parts:
            continue

        notebooks.append(nb_file)

    return sorted(notebooks)
```

**2.2 노트북-모듈 매핑**

```python
import json
import re

def extract_imported_modules(notebook_path: Path) -> list[str]:
    """노트북에서 import한 모듈 목록 추출."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    imported = []

    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue

        source = ''.join(cell['source'])

        # from X.Y import Z 패턴
        from_imports = re.findall(r'from\s+([\w.]+)\s+import', source)
        imported.extend(from_imports)

        # import X 패턴
        direct_imports = re.findall(r'import\s+([\w.]+)', source)
        imported.extend(direct_imports)

    return list(set(imported))
```

### Phase 3: 커버리지 계산

**3.1 매핑 테이블 생성**

```python
def build_coverage_map(
    modules: list[Path],
    notebooks: list[Path],
    src_dir: Path
) -> dict:
    """모듈-노트북 매핑 테이블 생성."""
    coverage = {}

    for module in modules:
        # 모듈 경로를 import 경로로 변환
        # src/data_loader.py → src.data_loader
        relative = module.relative_to(src_dir.parent)
        import_path = '.'.join(relative.with_suffix('').parts)

        coverage[str(module)] = {
            'import_path': import_path,
            'has_notebook': False,
            'notebooks': []
        }

    # 노트북에서 import된 모듈 확인
    for notebook in notebooks:
        imported_modules = extract_imported_modules(notebook)

        for module_path, info in coverage.items():
            if info['import_path'] in imported_modules:
                info['has_notebook'] = True
                info['notebooks'].append(str(notebook))

    return coverage
```

**3.2 커버리지 통계**

```python
def calculate_statistics(coverage: dict) -> dict:
    """커버리지 통계 계산."""
    total_modules = len(coverage)
    covered_modules = sum(1 for info in coverage.values() if info['has_notebook'])
    coverage_percent = (covered_modules / total_modules * 100) if total_modules > 0 else 0

    return {
        'total_modules': total_modules,
        'covered_modules': covered_modules,
        'uncovered_modules': total_modules - covered_modules,
        'coverage_percent': coverage_percent
    }
```

### Phase 4: 셀 구조 검증 (v2.0.0+)

**4.1 markdown + code 쌍 검증**

```python
import json
from pathlib import Path

def validate_cell_structure(notebook_path: Path) -> list[str]:
    """셀 구조 검증. 위반 사항 목록 반환."""
    violations = []

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb.get('cells', [])

    for i, cell in enumerate(cells):
        cell_type = cell.get('cell_type')
        source = ''.join(cell.get('source', []))

        # 1. 첫 4개 셀: markdown + code 쌍 검증
        if i < 4:
            expected = 'markdown' if i % 2 == 0 else 'code'
            if cell_type != expected:
                violations.append({
                    'cell': i + 1,
                    'type': 'structure',
                    'message': f'{expected} 예상, {cell_type} 발견'
                })

        # 2. code 셀 docstring 안티패턴 검출
        if cell_type == 'code' and source.strip().startswith('"""'):
            violations.append({
                'cell': i + 1,
                'type': 'antipattern',
                'message': 'docstring을 markdown 셀로 분리 필요'
            })

        # 3. magic keyword 위치 검증
        if cell_type == 'code':
            lines = [l for l in source.split('\n') if l.strip()]
            magic_indices = [j for j, l in enumerate(lines) if l.strip().startswith('%')]

            for idx in magic_indices:
                # magic이 첫 줄이 아니고, 그 앞에 다른 magic이 없으면 경고
                if idx > 0:
                    has_magic_before = any(lines[k].strip().startswith('%') for k in range(idx))
                    if not has_magic_before:
                        violations.append({
                            'cell': i + 1,
                            'type': 'magic_position',
                            'message': f'magic keyword ({lines[idx].strip()})가 셀 최상단이 아님'
                        })

    return violations
```

**4.2 검증 보고서 생성**

```python
def generate_structure_report(notebooks: list[Path]) -> dict:
    """모든 노트북의 셀 구조 검증 보고서."""
    report = {
        'total_notebooks': len(notebooks),
        'valid_notebooks': 0,
        'invalid_notebooks': 0,
        'violations': []
    }

    for nb_path in notebooks:
        violations = validate_cell_structure(nb_path)

        if violations:
            report['invalid_notebooks'] += 1
            report['violations'].append({
                'notebook': str(nb_path),
                'issues': violations
            })
        else:
            report['valid_notebooks'] += 1

    return report
```

---

## 출력 형식

### 요약 보고서

```
========================================
모듈-노트북 커버리지 보고서
========================================

📊 통계
- 전체 모듈: 15개
- 커버된 모듈: 12개 (80.0%)
- 누락된 모듈: 3개 (20.0%)

✅ 커버된 모듈 (12개)
src/data_loader.py → notebooks/01_data_loader.ipynb
src/preprocessing.py → notebooks/02_preprocessing.ipynb
src/models/classifier.py → notebooks/03_classifier.ipynb
...

❌ 누락된 모듈 (3개)
src/utils/helper.py (노트북 없음)
src/api/endpoints.py (노트북 없음)
src/config.py (노트북 없음)

📝 권장 조치
1. /generate-notebook-from-module src/utils/helper.py
2. /generate-notebook-from-module src/api/endpoints.py
3. /generate-notebook-from-module src/config.py

========================================
```

### 셀 구조 검증 보고서 (v2.0.0+)

```
========================================
📐 셀 구조 검증 보고서
========================================

📊 통계
- 전체 노트북: 3개
- 정상 구조: 2개 (66.7%)
- 구조 위반: 1개 (33.3%)

⚠️ 위반 사항
notebooks/01_data_loader.ipynb:
  - Cell 1: markdown 예상, code 발견 (structure)
  - Cell 3: docstring을 markdown 셀로 분리 필요 (antipattern)
  - Cell 5: magic keyword (%matplotlib)가 셀 최상단이 아님 (magic_position)

✅ 정상 노트북
- notebooks/02_preprocessing.ipynb
- notebooks/03_classifier.ipynb

📝 권장 조치
1. /generate-notebook-from-module src/data_loader.py --overwrite
   (기존 노트북 재생성으로 v2.0.0 구조 적용)

========================================
```

### 상세 보고서 (JSON)

```json
{
  "summary": {
    "total_modules": 15,
    "covered_modules": 12,
    "uncovered_modules": 3,
    "coverage_percent": 80.0,
    "timestamp": "2026-01-27T14:30:00+09:00"
  },
  "covered": [
    {
      "module": "src/data_loader.py",
      "notebooks": ["notebooks/01_data_loader.ipynb"],
      "import_path": "src.data_loader"
    }
  ],
  "uncovered": [
    {
      "module": "src/utils/helper.py",
      "import_path": "src.utils.helper",
      "reason": "no_notebook_found"
    }
  ]
}
```

---

## CI/CD 통합

### GitHub Actions 예시

```yaml
name: Check Notebook Coverage

on: [push, pull_request]

jobs:
  notebook-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check Notebook Coverage
        run: |
          claude-code /check-notebook-coverage

      - name: Upload Coverage Report
        uses: actions/upload-artifact@v3
        with:
          name: notebook-coverage
          path: coverage-report.json
```

### Pre-commit Hook 예시

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: notebook-coverage
        name: Check Notebook Coverage
        entry: claude-code /check-notebook-coverage
        language: system
        pass_filenames: false
        always_run: true
```

---

## 검증 규칙

### 커버리지 대상 모듈

| 포함 | 제외 |
|------|------|
| `src/**/*.py` | `__init__.py` |
| Public API 보유 | `_private.py` |
| 기능 모듈 | `tests/**/*.py` |
| | `scripts/**/*.py` |

### 노트북 인정 기준

```python
def is_valid_coverage(module_info: dict) -> bool:
    """노트북 커버리지 인정 기준."""
    # 조건 1: 노트북이 존재
    if not module_info['notebooks']:
        return False

    # 조건 2: 노트북에서 실제로 import
    # (단순히 파일명이 비슷한 것은 인정 안 함)

    return True
```

---

## 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--src-dir` | `src` | 모듈 디렉토리 |
| `--notebooks-dir` | `notebooks` | 노트북 디렉토리 |
| `--min-coverage` | `80` | 최소 커버리지 (%) |
| `--format` | `text` | 출력 형식 (text/json/html) |
| `--fail-under` | None | 커버리지 미달 시 exit code 1 |

**예시**:
```bash
# 최소 90% 요구
/check-notebook-coverage --min-coverage 90

# JSON 출력
/check-notebook-coverage --format json > coverage.json

# CI/CD용 (미달 시 실패)
/check-notebook-coverage --fail-under 80
```

---

## 실행 예시

### 프로젝트 구조

```
project/
├── src/
│   ├── data_loader.py      # ✅ notebooks/01에서 import
│   ├── preprocessing.py    # ✅ notebooks/02에서 import
│   ├── models/
│   │   ├── classifier.py   # ✅ notebooks/03에서 import
│   │   └── regressor.py    # ❌ 노트북 없음
│   └── utils/
│       └── helper.py        # ❌ 노트북 없음
└── notebooks/
    ├── 01_data_loader.ipynb
    ├── 02_preprocessing.ipynb
    └── 03_classifier.ipynb
```

### 실행 결과

```bash
$ /check-notebook-coverage

========================================
모듈-노트북 커버리지 보고서
========================================

📊 통계
- 전체 모듈: 5개
- 커버된 모듈: 3개 (60.0%)
- 누락된 모듈: 2개 (40.0%)

⚠️ 경고: 커버리지 60.0%는 권장 기준 80% 미만입니다.

✅ 커버된 모듈 (3개)
1. src/data_loader.py
   → notebooks/01_data_loader.ipynb

2. src/preprocessing.py
   → notebooks/02_preprocessing.ipynb

3. src/models/classifier.py
   → notebooks/03_classifier.ipynb

❌ 누락된 모듈 (2개)
1. src/models/regressor.py
   - Public API: Regressor (class)
   - 권장: /generate-notebook-from-module src/models/regressor.py

2. src/utils/helper.py
   - Public API: format_output, validate_input (functions)
   - 권장: /generate-notebook-from-module src/utils/helper.py

📝 빠른 수정
bash -c '
  /generate-notebook-from-module src/models/regressor.py
  /generate-notebook-from-module src/utils/helper.py
'

========================================
```

---

## 체크리스트

실행 후:

- [ ] 커버리지 비율 확인 (권장: 80% 이상)
- [ ] 누락된 모듈 목록 확인
- [ ] 각 누락된 모듈에 대해 `/generate-notebook-from-module` 실행
- [ ] CI/CD 파이프라인에 통합 (선택)

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-jupyter-setup/SKILL.md] | 노트북 필수 규칙 정의 |
| [@skills/generate-notebook-from-module/SKILL.md] | 누락된 노트북 자동 생성 |
| [@skills/extract-module-from-notebook/SKILL.md] | 노트북 → 모듈 역방향 추출 |

---

## 한계 및 주의사항

**오탐 가능성**:
- 노트북에서 import했지만 실제로 사용하지 않는 경우도 "커버됨"으로 인정
- 모듈명과 노트북명이 일치하지 않으면 매핑 실패 가능

**검증 제외 대상**:
- `__init__.py` (패키지 초기화 파일)
- Private 모듈 (`_internal.py`)
- 테스트 파일 (`tests/`)
- 스크립트 파일 (`scripts/`)

**개선 방향**:
- 노트북에서 실제 사용 여부까지 검증 (현재는 import만 확인)
- 모듈별 "노트북 필수" 예외 설정 지원

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-03 | 2.0.0 | Phase 4 추가: 셀 구조 검증 (markdown+code 쌍, docstring 안티패턴, magic keyword 위치) |
| 2026-01-27 | 1.0.0 | 초기 생성 - 모듈-노트북 커버리지 검증 |
