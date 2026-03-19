# ADR-037: 코드/폴더 스캐폴딩 기준

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
프로젝트 폴더 구조는 Gall's Law(ADR-003 AW-023) 적용 — 단순한 것부터 시작하여 진화.
`scaffold-structure` skill로 팀 합의 후 생성.

## 기본 Python 프로젝트 구조
```
project/
├── src/                # 소스 코드
├── tests/              # 테스트 (src 미러)
├── scripts/            # 유틸리티 스크립트
├── docs/               # 프로젝트 문서
├── pyproject.toml
├── CLAUDE.md
└── .claude/
```

## 이유
- 처음부터 복잡한 구조 금지 (YAGNI, Gall's Law)
- 팀원과 합의 후 생성 (scaffold-structure skill)
- snake_case 디렉토리 (Python import 가능)
