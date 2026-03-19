---
paths:
  - "config/**/*.yaml"
  - "config/**/*.yml"
  - "*.yaml"
  - "*.yml"
---

# 설정 파일 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **YAML 문법** | 들여쓰기 2칸, 따옴표 일관성 |

**상세**: 문자열은 따옴표 통일 (홑/겹 중 택일). 빈 값은 `null` 명시. 앵커(&)/별칭(*) 적절히 활용.

| **환경 분리** | base.yaml + {env}.yaml 구조 |

**상세**: `base.yaml` (공통) + `dev.yaml`, `staging.yaml`, `prod.yaml`. OmegaConf merge로 오버라이드.

| **민감정보 금지** | 비밀번호, API 키 절대 포함 금지 |

**상세**: 민감정보는 환경변수(`${oc.env:VAR}`) 또는 시크릿 관리 도구 사용. `.env.example`만 커밋.

| **스키마 검증** | Pydantic 모델로 타입 검증 |

**상세**: `pydantic.BaseSettings` 또는 `OmegaConf.to_object(cfg, ConfigModel)` 패턴 사용.

| **기본값 명시** | 모든 필수 설정에 기본값 제공 |

**상세**: 개발 환경에서 즉시 실행 가능하도록 합리적 기본값 제공. 프로덕션 필수값은 검증 로직 추가.

**상세 가이드**: [@skills/convention-config/SKILL.md] 참조
