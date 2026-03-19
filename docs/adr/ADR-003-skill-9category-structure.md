# ADR-003: Anthropic 9카테고리 Skill 구조 채택

- **상태**: Accepted
- **날짜**: 2026-03-19
- **결정자**: sunLeee

## 맥락

127개 이상의 skill이 flat 구조로 나열되면:
1. 어떤 skill이 있는지 파악하기 어려움
2. 중복 skill 생성 방지 어려움
3. 관련 skill 간 관계 불명확
4. 새 skill 추가 위치 결정 기준 없음

## 결정

**Anthropic 공식 블로그("Claude Code를 만들면서 배운 것: 우리가 Skills를 사용하는 법") 9카테고리 채택:**

```
.claude/skills/
├── reference/       # 라이브러리/API 레퍼런스 (convention-python, philosophy/...)
├── quality/         # 코드 품질 & 리뷰 (check-*, adversarial-review)
├── process/         # 비즈니스 프로세스 자동화 (commit, adr, pr, testing)
├── scaffolding/     # 코드/프로젝트 스캐폴딩 (project-init, doc-*)
├── data-fetch/      # 데이터 패칭 & 분석 (ref-*, markdown-converter)
├── utility/         # 유틸리티 (lint-fix, setup-*, manage-*)
├── monitoring/      # (미래 확장)
├── incident/        # (미래 확장)
└── infra/           # (미래 확장)
```

**Skill 이름**: `name:` 필드로 호출 이름 결정. 폴더 구조는 탐색/조직용.

## 이유

- Anthropic이 수백 개 skill 운영 경험에서 도출한 카테고리
- "최고의 skill은 하나의 카테고리에 명확히 속한다"
- description 필드 = 언제 호출하는지 (요약 X)
- Gotchas 섹션 = 가장 가치 높은 콘텐츠

## 대안 검토

| 대안 | 이유 채택 안 함 |
|------|----------------|
| Flat 구조 | 127개 → 탐색 불가 |
| 5카테고리 사용자 정의 | Anthropic 검증된 구조 대신 미검증 구조 사용 |
| 이름에 카테고리 prefix | `quality-check-anti-patterns` 너무 길음 |

## 폴더 vs 호출 이름 분리 원칙

```
폴더: .claude/skills/reference/python/SKILL.md  → 조직/탐색용
이름: name: convention-python                    → 호출용 (/convention-python)
```

## 결과

- **긍정**: skill 발견 가능성 향상, 중복 방지, Anthropic 표준 준수
- **부정**: 마이그레이션 비용 (flat → 계층화)
- **완화**: install.sh가 name: 필드로 ~/.claude/skills/ 설치 → 호출명 유지

## 참조

- [skill.md](../skill.md) § Anthropic 9카테고리
- [skill-catalog.md](../../skill-catalog.md) — 전체 skill 인벤토리
- 원문: https://www.anthropic.com/engineering/claude-code-skills
