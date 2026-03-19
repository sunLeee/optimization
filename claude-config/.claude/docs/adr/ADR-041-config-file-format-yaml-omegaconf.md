# ADR-041: 설정 파일 형식 — YAML + OmegaConf vs 대안

- **상태**: Accepted
- **날짜**: 2026-03-19
- **범용 여부**: ✅ Python 프로젝트에 적용 가능

## 맥락

하드코딩 제거를 위한 설정 파일 형식 선택 필요. 선택지: YAML, TOML, JSON, Python dict, OmegaConf.

## 결정

**YAML + OmegaConf** 조합 채택.
- 기본 설정: YAML 파일 (읽기 쉬움)
- 런타임 처리: OmegaConf (타입 안전, 계층형 병합, 변수 보간)

## 이유

- YAML: 사람이 읽기 쉬운 포맷, 주석 가능, Python 생태계 표준
- OmegaConf: 환경별 설정 오버라이드, `${path.to.key}` 보간, Pydantic 통합
- 두 조합으로 "코드에 숫자/경로 하드코딩 0" 달성 가능

## 대안 검토

| 대안 | 거부 이유 |
|------|---------|
| Python dict 하드코딩 | 환경별 설정 불가, 코드 수정 필요 |
| .env 파일만 | 계층 구조 없음, 복잡한 설정 표현 어려움 |
| TOML | OmegaConf 미지원, 생태계 제한적 |
| JSON | 주석 불가, 사람이 읽기 어려움 |

## 결과

- 모든 설정은 `config/` YAML 파일에 정의
- 하드코딩 상수 금지 → `cfg.zone.default_id` 형태로 접근
- Pydantic으로 타입 검증

## Gotchas

- OmegaConf 키에 하이픈 금지 (`grid-population` → `grid_population`)
- `.env`의 민감 정보는 OmegaConf와 별도 관리

## 참조

- `.claude/skills/reference/convention/convention-config/SKILL.md`
- `ADR-034` — 명명 규칙 (yaml 키도 snake_case)
