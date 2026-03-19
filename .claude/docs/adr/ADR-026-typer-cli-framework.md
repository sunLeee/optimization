# ADR-026: CLI 프레임워크로 typer 채택

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
CLI 작성 시 **typer** 사용. click은 레거시 또는 복잡한 커스터마이징 시에만. argparse는 레거시.

## 이유
- 타입 힌트 기반 자동 CLI 생성 → 코드가 문서
- `--help` 자동 생성, tab 완성 지원
- ADR-006(타입 힌트 필수)과 자연스럽게 연계

## Gotchas
- cli.md rule과 scripts.md rule 모두 typer 권장으로 통일 (ADR 수정 반영)
- click과의 혼용 금지 (하나의 프로젝트에서)
