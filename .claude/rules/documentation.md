---
paths:
  - "docs/**/*.md"
  - "*.md"
  - "README.md"
---

# 문서 작성 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **제목 계층** | H1 1개, H2-H4 순차적 사용 |

**상세**: H1(#)은 문서당 1개만. H2(##) -> H3(###) -> H4(####) 순차적으로 사용. 레벨 건너뛰기 금지.

| **코드 블록** | 언어 명시 필수 (` ```python `) |

**상세**: 모든 코드 블록에 언어 지정 (python, bash, yaml, json 등). 인라인 코드는 백틱(`) 사용.

| **경로** | 상대 경로 사용, 절대 경로 금지 |

**상세**: `./docs/api.md`, `../config/` 형태 사용. 루트 기준 절대 경로(`/Users/...`) 절대 금지.

| **버전** | 하드코딩 금지, 변수/참조 사용 |

**상세**: 버전은 `pyproject.toml`, `CHANGELOG.md` 참조. 문서 내 `v1.2.3` 직접 기입 금지.

| **README** | 개요, 설치, 빠른 시작, 기능, 라이선스 필수 |

**상세**: 최소 구성: Overview, Installation, Quick Start, Features, License. 배지(shields.io) 권장.

**상세 가이드**: [@skills/convention-documentation/SKILL.md] 참조
