---
paths:
  - "models/**/*.py"
  - "schemas/**/*.py"
  - "entities/**/*.py"
---

# 모델/스키마 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **Pydantic** | BaseModel 상속, 타입 힌트 필수 |

**상세**: Pydantic v2 사용. `BaseModel` 상속. `Optional` 대신 `| None` 문법 사용.

| **검증** | Field validator로 비즈니스 규칙 검증 |

**상세**: `@field_validator`, `@model_validator` 데코레이터 활용. 검증 실패 시 명확한 에러 메시지.

| **직렬화** | model_dump(), model_validate() 사용 |

**상세**: dict 변환 시 `model_dump()`, dict에서 모델 생성 시 `model_validate()`. `.dict()`, `.parse_obj()` 사용 금지.

| **불변성** | Config frozen=True 권장 |

**상세**: `model_config = ConfigDict(frozen=True)` 설정. 값 객체(VO)는 불변 필수. DTO는 선택적.

| **문서화** | 필드별 description 작성 |

**상세**: `Field(description="...")` 필수. OpenAPI 스키마 자동 생성에 활용. 예시값 `example` 포함 권장.

**상세 가이드**: [@skills/convention-data-validation/SKILL.md] 참조
