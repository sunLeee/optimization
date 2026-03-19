---
paths:
  - "api/**/*.py"
  - "routes/**/*.py"
  - "endpoints/**/*.py"
---

# API 엔드포인트 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **RESTful** | 명사 기반 URL, HTTP 메서드 준수 |

**상세**: GET(조회), POST(생성), PUT(전체수정), PATCH(부분수정), DELETE(삭제). 복수형 명사 사용 (`/users`, `/items`).

| **응답 형식** | Pydantic 모델로 응답 스키마 정의 |

**상세**: 모든 응답에 `response_model` 지정. 리스트 응답은 `List[Model]` 또는 페이지네이션 스키마 사용.

| **에러 처리** | HTTPException + 구체적 상태 코드 |

**상세**: 400(잘못된 요청), 401(인증 필요), 403(권한 없음), 404(찾을 수 없음), 422(검증 실패), 500(서버 오류).

| **인증** | 민감 엔드포인트에 인증 데코레이터 |

**상세**: `Depends(get_current_user)` 패턴 사용. 권한 레벨별 데코레이터 분리 (user, admin).

| **문서화** | Docstring으로 OpenAPI 자동 생성 |

**상세**: 함수 docstring이 OpenAPI description으로 변환. `summary`, `tags` 파라미터 활용.

**상세 가이드**: [@skills/convention-python/SKILL.md] 참조
