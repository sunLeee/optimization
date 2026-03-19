---
name: convention-async-python
triggers:
  - "convention async python"
description: "Python 비동기 프로그래밍(Async/Await) 컨벤션 참조 스킬. asyncio, aiohttp, 동시성 패턴, 에러 처리로 효율적인 비동기 코드를 작성한다."
argument-hint: "[섹션] - basics, patterns, aiohttp, semaphore, testing, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  Python asyncio 기반 비동기 프로그래밍 패턴을 제공한다.
  고성능 I/O 바운드 애플리케이션을 위한 필수 지식.
agent: |
  비동기 프로그래밍 전문가.
  asyncio, aiohttp, 동시성 제어, 에러 처리 패턴을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# Python 비동기 프로그래밍(Async/Await) 컨벤션

asyncio 기반 비동기 프로그래밍으로 고성능 I/O 바운드 애플리케이션을 구축하기 위한 규칙.

## 목적

- **asyncio 기초**: async/await 문법, 이벤트 루프, 코루틴
- **동시성 패턴**: gather, TaskGroup, Semaphore
- **HTTP 클라이언트**: aiohttp를 사용한 비동기 HTTP 요청
- **에러 처리**: 비동기 컨텍스트에서의 예외 처리
- **테스트**: pytest-asyncio를 사용한 비동기 테스트

---

## 1. Async/Await 기초

### 1.1 코루틴 정의

**규칙**: `async def`로 코루틴을 정의하고, I/O 작업에서 `await`를 사용한다.

**예제**: [@templates/skill-examples/convention-async-python/basic-coroutine.py]

### 1.2 동기 vs 비동기 선택 기준

| 상황 | 권장 방식 |
|------|----------|
| I/O 바운드 (네트워크, 파일) | 비동기 (`async/await`) |
| CPU 바운드 (계산 집약적) | 멀티프로세싱 (`multiprocessing`) |
| 혼합 워크로드 | 비동기 + `run_in_executor` |

**예제**: [@templates/skill-examples/convention-async-python/mixed-workload.py]

---

## 2. 동시성 패턴

### 2.1 asyncio.gather - 여러 코루틴 동시 실행

**규칙**: 독립적인 여러 I/O 작업은 `gather`로 동시 실행한다.

**예제**: [@templates/skill-examples/convention-async-python/gather-pattern.py]

### 2.2 asyncio.TaskGroup (Python 3.11+)

**규칙**: Python 3.11+에서는 `TaskGroup`을 사용하여 구조화된 동시성을 구현한다.

**예제**: [@templates/skill-examples/convention-async-python/taskgroup-pattern.py]

### 2.3 asyncio.Semaphore - 동시 실행 제한

**규칙**: 동시 연결 수를 제한해야 할 때 `Semaphore`를 사용한다.

**예제**: [@templates/skill-examples/convention-async-python/semaphore-pattern.py]

### 2.4 asyncio.Queue - 생산자-소비자 패턴

**예제**: [@templates/skill-examples/convention-async-python/queue-pattern.py]

---

## 3. aiohttp - 비동기 HTTP 클라이언트

### 3.1 기본 사용법

**규칙**: HTTP 요청에는 `aiohttp.ClientSession`을 사용하고, 세션을 재사용한다.

### 3.2 세션 재사용 (권장)

**예제**: [@templates/skill-examples/convention-async-python/aiohttp-client.py]

### 3.3 동시 요청 with 속도 제한

**예제**: [@templates/skill-examples/convention-async-python/rate-limiting.py]

---

## 4. 에러 처리

### 4.1 비동기 예외 처리

**규칙**: `gather`에서 `return_exceptions=True`를 사용하거나 개별 try-except를 사용한다.

### 4.2 타임아웃 처리

### 4.3 재시도 with Exponential Backoff

**예제**: [@templates/skill-examples/convention-async-python/error-handling.py]

---

## 5. 컨텍스트 관리

### 5.1 비동기 컨텍스트 매니저

**규칙**: 리소스 정리가 필요한 객체는 `__aenter__`와 `__aexit__`를 구현한다.

**예제**: [@templates/skill-examples/convention-async-python/context-manager.py]

---

## 6. 테스트

### 6.1 pytest-asyncio 사용

**규칙**: 비동기 함수 테스트에는 `pytest-asyncio`를 사용한다.

### 6.2 Mock 비동기 함수

**예제**: [@templates/skill-examples/convention-async-python/testing-examples.py]

### 6.3 pytest 설정

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

---

## 7. 안티패턴

### 7.1 피해야 할 패턴

**예제**: [@templates/skill-examples/convention-async-python/anti-patterns.py]

---

## 8. 체크리스트

구현 완료 후 다음을 확인하세요:

- [ ] `async def`로 코루틴 정의
- [ ] I/O 작업에 `await` 사용
- [ ] `asyncio.gather` 또는 `TaskGroup`으로 동시 실행
- [ ] `Semaphore`로 동시 실행 수 제한
- [ ] `aiohttp.ClientSession` 재사용
- [ ] 타임아웃 설정 (`asyncio.timeout`)
- [ ] 재시도 로직 구현 (exponential backoff)
- [ ] 예외 처리 (`return_exceptions=True` 또는 개별 try-except)
- [ ] pytest-asyncio로 테스트
- [ ] blocking I/O 사용하지 않음

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |
| [@skills/convention-error-handling/SKILL.md] | 에러 처리 패턴 |
| [@skills/convention-testing/SKILL.md] | 테스트 작성 규칙 |
| [@skills/check-python-style/SKILL.md] | 스타일 검증 |

---

## 참고

- Python asyncio: https://docs.python.org/3/library/asyncio.html
- aiohttp: https://docs.aiohttp.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Real Python - Async IO: https://realpython.com/async-io-python/

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.1.0 | 리팩토링 - 코드 블록을 템플릿으로 분리 (12개 예제) |
| 2026-01-22 | 1.0.0 | 초기 생성 - asyncio, aiohttp, 동시성 패턴 |

## Gotchas (실패 포인트)

- `asyncio.run()` 내부에서 `asyncio.run()` 호출 금지 (nested event loop)
- blocking 함수를 async 함수 내에서 직접 호출 시 전체 event loop 블록
- `await` 없이 coroutine 호출 시 실행 안 됨 — 경고도 없음
- `asyncio.gather` 예외 처리 누락 시 일부 태스크 결과 분실
