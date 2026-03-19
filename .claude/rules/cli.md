---
paths:
  - "cli/**/*.py"
  - "commands/**/*.py"
  - "src/**/cli.py"
  - "src/**/commands/*.py"
---

# CLI 애플리케이션 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **프레임워크** | typer 또는 click 사용 |

**상세**: typer 권장 (타입 힌트 기반). click은 레거시 또는 복잡한 커스터마이징 필요 시.

| **도움말** | 모든 명령어/옵션에 help 문자열 |

**상세**: `typer.Option(help="...")`, `typer.Argument(help="...")`. 예시 포함 권장.

| **종료 코드** | 성공 0, 사용자 에러 1, 시스템 에러 2 |

**상세**: `raise typer.Exit(code=1)` 사용. 사용자 입력 오류와 시스템 오류 구분 필수.

| **출력 형식** | --json, --quiet 옵션 지원 |

**상세**: `--json` 옵션 시 JSON 출력, `--quiet` 옵션 시 결과만 출력. 스크립트 연동 고려.

| **설정** | 환경변수 + 설정파일 우선순위 |

**상세**: CLI 인자 > 환경변수 > 설정파일 > 기본값 순서. `typer.Option(envvar="...")` 활용.

**상세 가이드**: [@skills/convention-python/SKILL.md] 참조
