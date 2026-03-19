---
paths:
  - "src/**/*.py"
  - "api/**/*.py"
  - "app/**/*.py"
  - "backend/**/*.py"
---

# Python 백엔드 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **타입 힌트** | 모든 함수에 타입 힌트 작성 |

**상세**: 매개변수, 반환값 모두 명시. `Optional` 대신 `| None` 사용. 복잡한 타입은 `TypeAlias` 정의.

| **Docstring** | Google 스타일, Logics/Example 포함 |

**상세**: Args, Returns, Raises 섹션 필수. 복잡한 로직은 Logics 섹션으로 알고리즘 설명. 사용 예시 포함.

| **structlog** | 구조화된 로깅, 민감정보 금지 |

**상세**: `structlog.get_logger()` 사용. 로그에 context 바인딩. 비밀번호, 토큰, 개인정보 로깅 절대 금지.

| **예외 처리** | 구체적 예외 타입 사용 |

**상세**: `except Exception` 금지. `ValueError`, `TypeError` 등 구체적 예외 캐치. 커스텀 예외 클래스 정의 권장.

| **테스트** | 최소 80% 커버리지 |

**상세**: 핵심 비즈니스 로직 90% 이상. 단위 테스트 우선. pytest + pytest-cov로 측정.

**상세 가이드**: [@skills/convention-python/SKILL.md] 참조
