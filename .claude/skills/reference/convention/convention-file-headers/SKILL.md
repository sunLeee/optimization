---
name: convention-file-headers
triggers:
  - "convention file headers"
description: "Python 모듈 헤더 정보 컨벤션 참조 스킬. 모든 Python 파일 최상단의 메타데이터 형식을 정의한다. Author, Created Date, Modified Date 등 필수 정보를 명시한다. 코드 작성 시 이 스킬을 참조하여 일관된 모듈 정보를 유지한다."
argument-hint: "[섹션] - template, fields, examples"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  Python 파일의 모듈 헤더 정보 표준을 제공한다.
  이 스킬은 메타데이터 작성 시 참조 가능한 템플릿과 가이드를 제공한다.
agent: |
  Python 모듈 메타데이터 가이드 전문가.
  파일 헤더 정보의 필수 필드, 선택 필드, 형식을 명확하게 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# Python 모듈 헤더 정보 컨벤션

Python 파일의 최상단에 작성하는 모듈 메타데이터 규칙을 정의한다.

## 목적

- 모든 Python 파일의 메타데이터 표준화
- 작성자, 생성일, 수정일 등 추적 정보 기록
- 버전 관리 및 라이센스 명시
- 코드 유지보수성 향상

## 사용법

```
/convention-file-headers [섹션]
```

| 섹션 | 설명 |
|------|------|
| `template` | 표준 헤더 템플릿 |
| `fields` | 필드 정의 및 설명 |
| `examples` | 프로젝트별 예시 |
| `all` | 전체 내용 (기본값) |

---

## 1. 표준 헤더 템플릿

### 1.1 기본 템플릿 (모든 파일 필수)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모듈 기능을 한 줄로 간단히 설명한다.

여러 줄 설명이 필요한 경우, 이곳에 추가 설명을 작성한다.
모듈의 주요 기능, 사용 시나리오, 주의사항 등을 기록한다.
"""

__author__ = "taeyang lee"
__email__ = "taeyang.lee@company.com"
__created__ = "2026-01-21 15:30(KST, UTC+09:00)"
__modified__ = "2026-01-21 15:30(KST, UTC+09:00)"
__version__ = "1.0.0"
__status__ = "Development"
__license__ = "Proprietary"

# ============================================================================
# 모듈 import 시작
# ============================================================================

import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from my_package.utils import helper_function
```

### 1.2 헤더 순서

**주석 구성 (위에서 아래 순서)**:
1. `#!/usr/bin/env python3` - Shebang (스크립트 실행 시)
2. `# -*- coding: utf-8 -*-` - 인코딩 선언
3. `"""모듈 설명"""` - 모듈 docstring
4. `__author__` - 작성자
5. `__email__` - 이메일
6. `__created__` - 생성 일시
7. `__modified__` - 최종 수정 일시
8. `__version__` - 버전
9. `__status__` - 상태
10. `__license__` - 라이센스
11. (선택) `__maintainer__`, `__copyright__` 등
12. (선택) 기밀 경고 (독점 라이센스)
13. import 문

---

## 2. 필드 정의

### 2.1 필수 필드

| 필드 | 형식 | 설명 |
|-----|------|------|
| `__author__` | 문자열 | 파일 작성자 이름 (필수) |
| `__email__` | 문자열 | 작성자 이메일 주소 (필수) |
| `__created__` | ISO 형식 | 파일 생성 일시 (필수) |
| `__modified__` | ISO 형식 | 최종 수정 일시 (필수) |
| `__license__` | 문자열 | 라이센스 유형 (필수) |

### 2.2 권장 필드

| 필드 | 형식 | 설명 |
|-----|------|------|
| `__version__` | Semantic | 모듈 버전 |
| `__status__` | Enum | Development / Production / Deprecated |
| `__maintainer__` | 문자열 | 현재 유지보수 담당자 |

### 2.3 선택 필드

| 필드 | 형식 | 설명 |
|-----|------|------|
| `__copyright__` | 문자열 | 저작권 표기 |
| `__contact__` | URL | 연락처 또는 이슈 추적 URL |
| `__keywords__` | 리스트 | 모듈 키워드 |

---

## 3. 날짜 형식

### 3.1 필수 형식

```
YYYY-MM-DD HH:MM(KST, UTC+09:00)
```

**예시**:
```
2026-01-21 15:30(KST, UTC+09:00)
2026-12-31 23:59(KST, UTC+09:00)
```

### 3.2 형식 규칙

- **YYYY**: 4자리 년도 (예: 2026)
- **MM**: 2자리 월 (01~12)
- **DD**: 2자리 일 (01~31)
- **HH**: 2자리 시간 (00~23)
- **MM**: 2자리 분 (00~59)
- **(KST, UTC+09:00)**: 한국 시간대 명시

### 3.3 수정 규칙

**`__modified__` 필드는 파일을 수정할 때마다 업데이트**:

```python
# 최초 작성
__modified__ = "2026-01-01 10:00(KST, UTC+09:00)"

# 수정 후 (버그 수정, 기능 추가 등)
__modified__ = "2026-01-21 15:30(KST, UTC+09:00)"  # 최신 수정 시간
```

---

## 4. 버전 형식

### 4.1 Semantic Versioning

```
MAJOR.MINOR.PATCH
```

| 컴포넌트 | 의미 | 예시 |
|---------|------|------|
| `MAJOR` | 호환성 파괴 변경 | `2.0.0` → `1.x.x`에서 변경 |
| `MINOR` | 신기능, 호환성 유지 | `1.1.0` → `1.0.x`에서 기능 추가 |
| `PATCH` | 버그 수정 | `1.0.1` → `1.0.0`에서 버그 수정 |

### 4.2 예시

```python
__version__ = "1.0.0"      # 초기 릴리스
__version__ = "1.1.0"      # 신기능 추가
__version__ = "1.1.1"      # 버그 수정
__version__ = "2.0.0"      # 주요 버전 변경
__version__ = "0.1.0"      # 개발 버전
```

---

## 5. 상태(Status) 값

### 5.1 상태 정의

| 값 | 의미 | 사용 시점 |
|---|------|----------|
| `Development` | 개발 중 | 기능 개발/테스트 중 |
| `Prototype` | 프로토타입 | 초기 구현, 안정성 미정 |
| `Staging` | 스테이징 | 운영 배포 전 최종 테스트 |
| `Production` | 운영 중 | 안정적, 운영 배포됨 |
| `Maintenance` | 유지보수 중 | 버그 수정만 진행 |
| `Deprecated` | 폐기 예정 | 대체 함수 존재, 곧 제거 |
| `Archived` | 아카이브됨 | 완전 폐기, 참고용만 |

### 5.2 예시

```python
# 개발 중인 모듈
__status__ = "Development"

# 운영 서버에 배포된 모듈
__status__ = "Production"

# 곧 제거될 예정인 모듈
__status__ = "Deprecated"
```

---

## 6. 라이센스 유형

### 6.1 오픈소스 라이센스

| 라이센스 | 설명 |
|---------|------|
| `MIT` | 매우 관대한 라이센스 |
| `Apache-2.0` | 특허 조항 포함 |
| `GPL-3.0` | 카피레프트 |
| `BSD-3-Clause` | BSD 3조항 |

### 6.2 사내 라이센스

```python
__license__ = "Proprietary"
```

---

## 7. 사내용 (Proprietary) 라이센스 템플릿

### 7.1 기밀 정보 포함 파일

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
기밀 및 독점 정보 / CONFIDENTIAL AND PROPRIETARY
=============================================================================
Copyright (c) 2026 현대자동차 그룹. All Rights Reserved.

본 소프트웨어 및 관련 문서는 현대자동차 그룹의 독점 자산입니다.
무단 복제, 배포 또는 사용은 엄격히 금지됩니다.
=============================================================================
"""

__author__ = "taeyang lee"
__email__ = "taeyang.lee@company.com"
__created__ = "2026-01-21 15:30(KST, UTC+09:00)"
__modified__ = "2026-01-21 15:30(KST, UTC+09:00)"
__version__ = "1.0.0"
__status__ = "Production"
__license__ = "Proprietary"
__copyright__ = "Copyright 2026 현대자동차 그룹. All Rights Reserved."

import os
```

### 7.2 기밀 등급 (선택사항)

```python
__confidentiality__ = "Internal Use Only"
# 또는
__confidentiality__ = "Restricted"
# 또는
__confidentiality__ = "Confidential"
```

---

## 8. 모듈 Docstring

### 8.1 한 줄 설명 (필수)

```python
"""모듈 기능을 동사로 시작하여 한 줄로 명확하게 설명한다."""
```

### 8.2 상세 설명 (권장)

```python
"""모듈 기능을 한 줄로 설명한다.

상세 설명:
    이 모듈은 데이터 로딩 및 전처리 기능을 담당한다.
    Pandas DataFrame을 받아 정규화, 결측치 처리,
    특성 엔지니어링을 수행한다.

주요 함수:
    - load_data(): CSV/Parquet 파일 로드
    - preprocess(): 데이터 전처리
    - normalize(): 데이터 정규화

사용 예시:
    >>> from my_package.data.loader import load_data
    >>> df = load_data('data.csv')
    >>> processed = preprocess(df)

주의사항:
    - 메모리 사용량이 많으므로 대용량 파일은 chunking 권장
    - 인코딩을 명시적으로 지정해야 함

참고:
    관련 모듈: my_package.models.trainer
"""
```

---

## 9. 실제 예시

### 9.1 데이터 로더 모듈

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""데이터 로딩 및 캐싱 기능을 제공한다.

이 모듈은 CSV, Parquet, JSON 포맷의 데이터 파일을 로드하고,
메모리 캐싱을 통해 반복 로드 성능을 개선한다.

주요 클래스:
    - DataLoader: 데이터 로드 및 캐싱 관리

사용 예시:
    >>> loader = DataLoader(cache_dir="/tmp/cache")
    >>> df = loader.load("data/sales.csv", encoding="utf-8")
"""

__author__ = "taeyang lee"
__email__ = "taeyang.lee@company.com"
__created__ = "2026-01-15 09:30(KST, UTC+09:00)"
__modified__ = "2026-01-21 15:30(KST, UTC+09:00)"
__version__ = "1.2.1"
__status__ = "Production"
__license__ = "Proprietary"

from pathlib import Path
from typing import Any

import pandas as pd
```

### 9.2 유틸리티 스크립트

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 데이터 처리 유틸리티 스크립트.

매일 오전 6시에 실행되는 ETL 파이프라인.
Raw 데이터를 정제하여 Data Warehouse에 로드한다.

실행 방법:
    $ python scripts/batch_processor.py --date 2026-01-20

크론 작업:
    0 6 * * * /usr/bin/python3 /opt/scripts/batch_processor.py
"""

__author__ = "taeyang lee"
__email__ = "taeyang.lee@company.com"
__created__ = "2025-12-01 10:00(KST, UTC+09:00)"
__modified__ = "2026-01-20 14:45(KST, UTC+09:00)"
__version__ = "2.1.0"
__status__ = "Production"
__license__ = "Proprietary"

import logging
from datetime import datetime
from argparse import ArgumentParser
```

---

## 10. 체크리스트

코드 작성 후 다음을 확인하세요:

- [ ] `__author__` = "taeyang lee"로 설정됨
- [ ] `__created__` 형식: YYYY-MM-DD HH:MM(KST, UTC+09:00)
- [ ] `__modified__` 형식: YYYY-MM-DD HH:MM(KST, UTC+09:00)
- [ ] `__version__` Semantic Versioning 준수
- [ ] `__status__` 유효한 값 (Development/Production/Deprecated 등)
- [ ] `__license__` = "Proprietary" 명시
- [ ] 모듈 docstring 한국어로 작성
- [ ] 모듈 docstring 80자 이내 한 줄 설명

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 (전체) |
| [@skills/check-python-style/SKILL.md] | Python 스타일 검증 |
| [@skills/convention-logging/SKILL.md] | 로깅 컨벤션 |
| [@skills/code-review/SKILL.md] | 코드 리뷰 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - 모듈 헤더 정보 표준화 |
