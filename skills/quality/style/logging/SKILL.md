---
name: convention-logging
triggers:
  - "convention logging"
description: Python 로깅 코드를 작성할 때. structlog vs logging 선택이 불명확할 때. 로그 레벨 기준, 포맷, 메시지 작성 규칙이 필요할 때.
argument-hint: "[섹션] - levels, format, messages, security, structlog, all"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
model: claude-sonnet-4-6[1m]
context: Python 로깅 컨벤션 참조 스킬. 표준 logging과 structlog 기반 규칙을 제공한다. 검증은 check-logging 스킬이 담당한다.
agent: Python 로깅 전문가. 적절한 로그 레벨, 포맷, 보안을 고려한 메시지 작성 방법을 안내한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []
---

# convention-logging

Python 로깅 컨벤션.

## 선택 기준: structlog vs logging

| 상황 | 사용 |
|------|------|
| 단순 스크립트, 유틸리티 | `logging` (표준) |
| 운영 서비스, JSON 로그 필요 | `structlog` |
| ADK 에이전트 | `libs/logger` (커스텀 TRACE 레벨) |

## 로그 레벨 기준

| 레벨 | 기준 | 예시 |
|------|------|------|
| `TRACE` | 내부 상태, 디버깅 | `tool_context.state dump` |
| `DEBUG` | 개발 중 상세 정보 | `df.shape, column names` |
| `INFO` | 정상 흐름의 주요 단계 | `demand_loaded: rows=1000` |
| `WARNING` | 예상 가능한 문제 | `zone_id=0 (H3 null cell)` |
| `ERROR` | 처리 실패, 복구 가능 | `FileNotFoundError` |
| `CRITICAL` | 시스템 중단 필요 | `DB connection failed` |

## 설정 패턴

```python
# 표준 logging
import logging
logger = logging.getLogger(__name__)

# structlog
import structlog
logger = structlog.get_logger(__name__)
logger.info("demand_loaded", rows=len(df), zone_count=zones)
```

## 메시지 작성 규칙

```python
# CORRECT: 구조화된 메시지 (검색 가능)
logger.info("zone_aggregated", zone_id=zone_id, total=total_demand)

# VIOLATION: 문자열 포맷 (검색 어려움)
logger.info(f"Zone {zone_id} aggregated: {total_demand}")  # 금지

# CORRECT: 개인정보 마스킹
logger.info("user_loaded", user_id=user_id[:4] + "****")

# VIOLATION: 개인정보 노출
logger.info("user_loaded", email=user_email)  # 금지
```

## Gotchas (실패 포인트)

- **f-string in logger**: `logger.info(f"...")` → 항상 구조화된 kwargs 사용
- **개인정보 로그**: email, user_id 전체 → 마스킹 필수
- **Exception 로깅**: `except Exception as e: logger.error(str(e))` → `logger.exception("msg")` 사용
- **TRACE 레벨**: 표준 logging에 없음 → `libs/logger` 사용 필수

## libs/logger 사용 (ADK 프로젝트)

```python
from libs.logger import get_logger
logger = get_logger(__name__)
logger.trace("tool_state", state=tool_context.state)  # TRACE 레벨
```

## 관련 규칙

- CLAUDE.md § 코드 스타일
- [check-logging](../../check/check-logging/SKILL.md) — 로깅 패턴 검증
