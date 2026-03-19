---
name: setup-logging
triggers:
  - "setup logging"
description: "프로젝트 로깅 설정 자동화 스킬. Python 표준 logging 기반으로 로깅 인프라를 구성한다."
argument-hint: "[--minimal|--standard|--json] - 설정 수준"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: 프로젝트 로깅 설정을 자동화한다. convention-logging 컨벤션을 준수하는 설정 파일을 생성한다. 환경별(개발/프로덕션) 설정을 분리하여 관리한다.
agent: 로깅 설정 전문가. 프로젝트 특성을 분석하여 적절한 로깅 구성을 설정한다. 표준 logging 기반으로 확장 가능한 구조를 제공한다.
hooks:
  pre_execution: []
  post_execution: []
category: 환경 설정
skill-type: Atomic
references:
  - "@skills/setup-quality/SKILL.md"
referenced-by:
  - "@skills/setup-quality/SKILL.md"

---
# 프로젝트 로깅 설정

프로젝트 로깅 인프라를 자동으로 구성하는 스킬.

## 목적

- 로깅 모듈 자동 생성
- 환경별 설정 분리 (개발/프로덕션)
- JSON 포맷터 및 컨텍스트 필터 제공
- 로그 파일 로테이션 설정

## 사용법

```bash
/setup-logging                  # 대화형 설정
/setup-logging --minimal        # 최소 설정 (콘솔만)
/setup-logging --standard       # 표준 설정 (콘솔 + 파일)
/setup-logging --json           # JSON 로깅 (프로덕션용)
```

### AskUserQuestion 활용 지점

**지점 1: 로깅 수준 선택**

플래그가 없을 때 로깅 수준을 선택한다:

```yaml
AskUserQuestion:
  questions:
    - question: "로깅 수준을 선택해주세요"
      header: "로깅 수준"
      multiSelect: false
      options:
        - label: "standard - 텍스트 로깅 (권장)"
          description: "콘솔 + 파일 로테이션 | 개발/일반 애플리케이션"
        - label: "json - JSON 로깅"
          description: "구조화 로그 | 프로덕션, 로그 분석 파이프라인"
        - label: "minimal - 최소 로깅"
          description: "콘솔만 | 빠른 시작, 스크립트"
        - label: "verbose - 상세 로깅"
          description: "디버그 정보 포함 | 문제 진단"
```

**지점 2: 민감정보 필터 활성화**

보안을 위해 민감정보 자동 필터링 여부를 확인한다:

```yaml
AskUserQuestion:
  questions:
    - question: "민감정보 자동 필터를 활성화할까요?"
      header: "보안 필터"
      multiSelect: false
      options:
        - label: "예 - 필터 활성화 (권장)"
          description: "비밀번호, API 키, 토큰 자동 마스킹"
        - label: "아니오 - 필터 없음"
          description: "개발 환경에서만 사용"
        - label: "커스텀 규칙"
          description: "필터링할 패턴 직접 지정"
```

---

## 설정 프로파일

### Minimal (최소)

```
/setup-logging --minimal
    |
    +-- src/{project}/utils/logging.py (기본 설정)
    +-- 콘솔 출력만
```

**용도**: 빠른 시작, 스크립트, CLI 도구

### Standard (표준)

```
/setup-logging --standard
    |
    +-- src/{project}/utils/logging.py (확장 설정)
    +-- src/{project}/utils/log_context.py (컨텍스트 관리)
    +-- 콘솔 + 파일 로테이션
    +-- 환경별 설정 분리
```

**용도**: 일반 애플리케이션, API 서버

### JSON (프로덕션)

```
/setup-logging --json
    |
    +-- src/{project}/utils/logging.py (JSON 포맷터)
    +-- src/{project}/utils/log_context.py (컨텍스트 관리)
    +-- src/{project}/utils/log_filters.py (민감정보 필터)
    +-- JSON 포맷 출력
    +-- 로그 수집 시스템 연동 최적화
```

**용도**: 프로덕션 환경, 로그 분석 파이프라인

---

## 생성 파일

### 1. logging.py (핵심 모듈)

```python
"""
프로젝트 로깅 설정 모듈.

사용법:
    from {project}.utils.logging import setup_logging, get_logger

    # 애플리케이션 시작 시 한 번 호출
    setup_logging()

    # 각 모듈에서 로거 획득
    logger = get_logger(__name__)
    logger.info("Application started")
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# 환경 변수
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "text")  # text or json
LOG_DIR = os.getenv("LOG_DIR", "logs")
APP_NAME = os.getenv("APP_NAME", "{project}")


# 포맷 정의
TEXT_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
)

TEXT_FORMAT_SIMPLE = "%(asctime)s | %(levelname)-8s | %(message)s"


def setup_logging(
    level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_dir: Optional[str] = None,
    console: bool = True,
    file: bool = True,
) -> None:
    """
    로깅 시스템 초기화.

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 로그 포맷 ("text" 또는 "json")
        log_dir: 로그 파일 디렉토리
        console: 콘솔 출력 여부
        file: 파일 출력 여부
    """
    level = level or LOG_LEVEL
    log_format = log_format or LOG_FORMAT
    log_dir = log_dir or LOG_DIR

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # 기존 핸들러 제거
    root_logger.handlers.clear()

    # 포맷터 선택
    if log_format == "json":
        from {project}.utils.log_formatters import JSONFormatter
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(TEXT_FORMAT)

    # 콘솔 핸들러
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, level))
        root_logger.addHandler(console_handler)

    # 파일 핸들러 (로테이션)
    if file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{APP_NAME}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, level))
        root_logger.addHandler(file_handler)

        # 에러 전용 파일
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{APP_NAME}.error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 획득.

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        logging.Logger: 설정된 로거
    """
    return logging.getLogger(name)
```

### 2. log_formatters.py (JSON 포맷터)

```python
"""JSON 로그 포맷터."""
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """
    구조화된 JSON 로그 포맷터.

    로그 수집 시스템(ELK, CloudWatch, Datadog 등)과 호환.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 프로세스/스레드 정보
        log_data["process_id"] = record.process
        log_data["thread_name"] = record.threadName

        # 예외 정보
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # extra 필드 추가 (request_id, user_id 등)
        reserved_attrs = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "pathname", "process", "processName", "relativeCreated",
            "stack_info", "exc_info", "exc_text", "thread", "threadName",
            "message", "asctime",
        }

        for key, value in record.__dict__.items():
            if key not in reserved_attrs and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)
```

### 3. log_context.py (컨텍스트 관리)

```python
"""로그 컨텍스트 관리."""
import contextvars
import logging
import uuid
from typing import Any, Optional

# 컨텍스트 변수 정의
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "user_id", default=""
)
extra_context_var: contextvars.ContextVar[dict] = contextvars.ContextVar(
    "extra_context", default={}
)


class ContextFilter(logging.Filter):
    """로그 레코드에 컨텍스트 정보를 자동 추가하는 필터."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()

        # 추가 컨텍스트 병합
        for key, value in extra_context_var.get().items():
            setattr(record, key, value)

        return True


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **extra: Any,
) -> None:
    """
    현재 요청의 로그 컨텍스트 설정.

    Args:
        request_id: 요청 ID (없으면 자동 생성)
        user_id: 사용자 ID
        **extra: 추가 컨텍스트 필드
    """
    request_id_var.set(request_id or str(uuid.uuid4()))

    if user_id:
        user_id_var.set(user_id)

    if extra:
        current = extra_context_var.get()
        extra_context_var.set({**current, **extra})


def clear_request_context() -> None:
    """요청 컨텍스트 초기화."""
    request_id_var.set("")
    user_id_var.set("")
    extra_context_var.set({})


def get_request_id() -> str:
    """현재 요청 ID 반환."""
    return request_id_var.get()


# 컨텍스트 필터를 기본으로 적용
def install_context_filter() -> None:
    """루트 로거에 컨텍스트 필터 설치."""
    root_logger = logging.getLogger()
    context_filter = ContextFilter()

    for handler in root_logger.handlers:
        handler.addFilter(context_filter)
```

### 4. log_filters.py (민감정보 필터)

```python
"""민감 정보 마스킹 필터."""
import logging
import re
from typing import Pattern, Set


class SensitiveDataFilter(logging.Filter):
    """
    민감 정보를 자동으로 마스킹하는 필터.

    로그 메시지에서 비밀번호, API 키, 토큰 등을 마스킹.
    """

    SENSITIVE_PATTERNS: list[tuple[Pattern, str]] = [
        # 비밀번호
        (re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\'}\s,]+', re.I), 'password=***MASKED***'),
        # API 키
        (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\'}\s,]+', re.I), 'api_key=***MASKED***'),
        # 토큰
        (re.compile(r'token["\']?\s*[:=]\s*["\']?[^"\'}\s,]+', re.I), 'token=***MASKED***'),
        # Bearer 토큰
        (re.compile(r'Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+', re.I), 'Bearer ***MASKED***'),
        # 이메일 (부분 마스킹)
        (re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), r'\1[at]\2'),
        # 신용카드 번호
        (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), '****-****-****-****'),
    ]

    SENSITIVE_KEYS: Set[str] = {
        "password", "passwd", "secret", "token", "api_key", "apikey",
        "authorization", "auth", "credential", "credit_card", "ssn",
        "social_security", "private_key", "secret_key",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        # 메시지 마스킹
        record.msg = self._mask_message(str(record.msg))

        # args 마스킹
        if record.args:
            record.args = tuple(
                self._mask_message(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )

        return True

    def _mask_message(self, message: str) -> str:
        """메시지 내 민감 정보 마스킹."""
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)
        return message


def install_sensitive_filter() -> None:
    """루트 로거에 민감정보 필터 설치."""
    root_logger = logging.getLogger()
    sensitive_filter = SensitiveDataFilter()

    for handler in root_logger.handlers:
        handler.addFilter(sensitive_filter)
```

---

## 프로세스

### 단계 1: 프로젝트 분석

```
1. 프로젝트 구조 확인
   - src/ 또는 {project}/ 디렉토리
   - pyproject.toml에서 프로젝트명 추출

2. 기존 로깅 설정 확인
   - utils/logging.py 존재 여부
   - 설정 파일 내 logging 섹션
```

### 단계 2: 파일 생성

```
/setup-logging --standard

생성할 파일:
├── src/{project}/utils/logging.py
├── src/{project}/utils/log_formatters.py
├── src/{project}/utils/log_context.py
└── config/logging.yaml (선택)
```

### 단계 3: 통합 가이드 제공

```python
# main.py 또는 __init__.py에 추가
from {project}.utils.logging import setup_logging

# 애플리케이션 시작 시
setup_logging()

# FastAPI 미들웨어 예시
from {project}.utils.log_context import set_request_context, clear_request_context

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_context(request_id=request_id)

    response = await call_next(request)

    clear_request_context()
    return response
```

---

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `LOG_LEVEL` | 로그 레벨 | `INFO` |
| `LOG_FORMAT` | 포맷 (`text` 또는 `json`) | `text` |
| `LOG_DIR` | 로그 파일 디렉토리 | `logs` |
| `APP_NAME` | 애플리케이션 이름 | 프로젝트명 |

### 환경별 권장 설정

| 환경 | LOG_LEVEL | LOG_FORMAT |
|------|-----------|------------|
| 개발 | DEBUG | text |
| 테스트 | DEBUG | text |
| 스테이징 | INFO | json |
| 프로덕션 | INFO | json |

---

## pyproject.toml 설정

```toml
[tool.{project}]
# 로깅 기본 설정
log_level = "INFO"
log_format = "text"
log_dir = "logs"
```

---

## 통합

### convention-logging 연동

이 스킬은 [@skills/convention-logging/SKILL.md] 컨벤션을 준수하는 설정을 생성한다:

- 로그 레벨 기준 준수
- 표준 포맷 필드 포함
- 민감 정보 마스킹 적용
- 성능 최적화 패턴 적용

### setup-quality 연동

```
/setup-quality --standard
    |
    +-- 품질 도구 설정
    +-- /setup-logging --standard (자동 호출 가능)
```

---

## 출력 예시

### --minimal

```
/setup-logging --minimal

✅ 로깅 설정 완료 (Minimal)

생성된 파일:
- src/myapp/utils/logging.py

사용법:
from myapp.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
```

### --standard

```
/setup-logging --standard

✅ 로깅 설정 완료 (Standard)

생성된 파일:
- src/myapp/utils/logging.py
- src/myapp/utils/log_formatters.py
- src/myapp/utils/log_context.py

환경 변수:
- LOG_LEVEL=INFO
- LOG_FORMAT=text
- LOG_DIR=logs

다음 단계:
1. main.py에 setup_logging() 호출 추가
2. 필요 시 미들웨어에 컨텍스트 설정 추가
```

### --json

```
/setup-logging --json

✅ 로깅 설정 완료 (JSON)

생성된 파일:
- src/myapp/utils/logging.py
- src/myapp/utils/log_formatters.py
- src/myapp/utils/log_context.py
- src/myapp/utils/log_filters.py

프로덕션 권장 환경 변수:
- LOG_LEVEL=INFO
- LOG_FORMAT=json
- LOG_DIR=/var/log/myapp

민감정보 필터 활성화됨
```

---

## 모범 사례

### DO

1. **애플리케이션 시작 시 한 번만 `setup_logging()` 호출**
2. **각 모듈에서 `get_logger(__name__)` 사용**
3. **환경 변수로 로그 레벨 제어**
4. **프로덕션에서 JSON 포맷 사용**
5. **요청 컨텍스트 설정으로 추적성 확보**

### DON'T

1. **여러 곳에서 로깅 설정 중복**
2. **하드코딩된 로그 레벨**
3. **프로덕션에서 DEBUG 레벨 사용**
4. **민감 정보 필터 없이 배포**

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - Python 표준 logging 기반 설정 자동화 |
