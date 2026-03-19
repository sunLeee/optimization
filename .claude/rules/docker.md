---
paths:
  - "Dockerfile"
  - "Dockerfile.*"
  - "docker-compose*.yml"
  - "docker-compose*.yaml"
  - ".dockerignore"
---

# Docker/컨테이너 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **베이스 이미지** | 공식 이미지, 버전 태그 명시 |

**상세**: `python:3.11-slim` 형태로 명시. `latest` 태그 사용 금지. Alpine은 호환성 이슈 주의.

| **멀티스테이지** | 빌드/런타임 분리로 이미지 최소화 |

**상세**: builder 스테이지에서 의존성 설치, runtime 스테이지에 필요한 파일만 복사. 최종 이미지 크기 최소화.

| **비root 사용자** | USER 지시어로 권한 최소화 |

**상세**: `RUN useradd -m appuser && USER appuser`. 1000:1000 UID/GID 권장. 루트 실행 절대 금지.

| **헬스체크** | HEALTHCHECK 지시어 포함 |

**상세**: `HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1`

| **.dockerignore** | 불필요 파일 제외 (venv, __pycache__) |

**상세**: `.git`, `.venv`, `__pycache__`, `*.pyc`, `.env`, `tests/`, `docs/` 포함. 빌드 컨텍스트 최소화.

**참고 skill**: 보안 강화 [@skills/reference/convention/convention-security-hardening/SKILL.md], 환경 설정 [@skills/reference/convention/convention-environment-config/SKILL.md]
