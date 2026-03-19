# ADR-034: 파일/변수/디렉토리 명명 규칙 통합

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
- Python 파일/모듈/변수/함수: `snake_case`
- Python class: `PascalCase`
- Python 상수: `UPPER_SNAKE_CASE`
- 문서 파일(.md): `kebab-case`
- Git 브랜치: `{type}/issue-{number}-{subject}` (kebab-case)
- Skills/plugin: `kebab-case`
- Python import 가능 디렉토리: `snake_case`

## 이유
- snake_case = Python namespace (import 가능)
- kebab-case = 파일시스템/URL/CLI (사람이 읽기 좋음)
- 하이픈 디렉토리 = Python import 불가 → 패키지는 반드시 snake_case

## 관리 위치
`.claude/docs/naming-conventions.md`
