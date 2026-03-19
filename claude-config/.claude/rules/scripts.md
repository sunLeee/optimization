---
paths:
  - "scripts/**/*.py"
  - "bin/**/*.py"
  - "tools/**/*.py"
---

# 스크립트 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **진입점** | `if __name__ == "__main__":` 필수 |

**상세**: 스크립트 직접 실행과 모듈 임포트 구분. `main()` 함수 정의 후 진입점에서 호출.

| **인자 처리** | typer 권장 (argparse는 레거시) |

**상세**: typer 사용 권장 (타입 힌트 기반, `--help` 자동 생성). argparse는 외부 의존성 없이 사용해야 할 때만. cli.md와 동일 기준 적용.

| **로깅** | print 대신 logging 사용 |

**상세**: `logging.basicConfig(level=logging.INFO)` 최소 설정. 디버그 출력은 `--verbose` 옵션으로 제어.

| **종료 코드** | 성공 0, 실패 1 반환 |

**상세**: `sys.exit(0)` 또는 `sys.exit(1)` 명시적 반환. 쉘 스크립트 연동, CI/CD 파이프라인 고려.

| **문서화** | 스크립트 목적과 사용법 주석 |

**상세**: 파일 상단 docstring에 목적, 사용법, 예시 명시. `--help` 출력과 일관성 유지.

**상세 가이드**: [@skills/convention-python/SKILL.md] 참조
