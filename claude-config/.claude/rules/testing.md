---
paths:
  - "tests/**/*.py"
  - "test_*.py"
  - "*_test.py"
---

# 테스트 코드 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **AAA 패턴** | Arrange-Act-Assert 구조 준수 |

**상세**: Arrange(준비) -> Act(실행) -> Assert(검증) 분리. 각 섹션 빈 줄로 구분. 한 테스트당 하나의 개념만.

| **명명 규칙** | `test_<함수>_<시나리오>_<예상결과>` |

**상세**: `test_calculate_total_with_discount_returns_reduced_price` 형태. 테스트 목적이 이름에서 드러나야 함.

| **Fixtures** | 하드코딩 금지, conftest.py 활용 |

**상세**: 공통 fixture는 `conftest.py`에 정의. 테스트 데이터는 factory 패턴 또는 fixture로 생성.

| **독립성** | 테스트 간 의존성 금지 |

**상세**: 테스트 실행 순서 무관하게 동작. 각 테스트 후 상태 정리. DB 테스트는 트랜잭션 롤백 활용.

| **커버리지** | 핵심 로직 90%, 전체 80% 이상 |

**상세**: `pytest-cov` 사용. 비즈니스 로직은 엣지 케이스 포함 철저히. 유틸리티 함수는 기본 케이스만.

**상세 가이드**: [@skills/convention-testing/SKILL.md] 참조
