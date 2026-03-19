---
name: adversarial-review
triggers:
  - "adversarial review"
description: 코드, 문서, 설계 결과물을 작성 완료 후 레드팀/블루팀 관점으로 검토하고 싶을 때. "셀프 리뷰", "경쟁모드", "레드팀 블루팀", "허점 찾아줘" 요청 시.
argument-hint: "[코드/문서/결과물 경로 또는 설명]"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: 레드팀(공격)이 허점을 찾고 블루팀(방어)이 수정하는 반복 리뷰. 우선순위 15가지 이슈를 찾아 최상의 버전을 생성한다.
agent: 소프트웨어 리뷰 전문가. 공격적 시각으로 취약점을 발굴하고, 방어적 시각으로 최소 변경 개선안을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 코드 품질
skill-type: Atomic
references:
  - "@skills/quality/check/anti-patterns/SKILL.md"
  - "@skills/reference/python/SKILL.md"
referenced-by: []
---

# adversarial-review

구현한 코드를 레드팀(공격자 관점)과 블루팀(방어자 관점)으로 이중 검토한다.

## 레드팀 (공격 관점) — 취약점 탐색

다음 질문으로 허점을 찾는다:

1. **예외 케이스**: 입력값이 None, 빈 리스트, 음수일 때 어떻게 되는가?
2. **경계 조건**: 최대/최소값, 빈 파일, 대용량 데이터에서 동작하는가?
3. **상태 오염**: 전역 변수, 클래스 변수가 다른 호출에 영향을 주는가?
4. **type safety**: mypy --strict 통과 여부
5. **ADK 패턴 위반**: tool이 파일 경로를 인자로 받는가? (금지)
6. **DRY 위반**: 같은 로직이 3곳 이상 반복되는가?
7. **SRP 위반**: 함수/클래스가 2개 이상의 책임을 지는가?

**상황 1**: `load_data(file_path=None)` → `AttributeError` 발생 → type hint + None 처리 추가
**상황 2**: 대용량 CSV (1GB) → 메모리 초과 → chunked reading 또는 lazy loading 도입

## 블루팀 (방어 관점) — 개선 적용

레드팀이 발견한 허점에 대해 최소 변경으로 방어한다:

1. **취약점별 우선순위**: Critical > High > Medium > Low
2. **최소 수정**: 다른 기능에 영향을 주지 않는 수정만
3. **테스트 추가**: 발견된 케이스에 대한 단위 테스트 작성

## 출력 형식

```
## 레드팀 발견 사항 (우선순위 15개)
1. [Critical] {허점 설명}
2. [High] {허점 설명}
...

## 블루팀 수정 계획
1. {수정 방법} → {예상 라인 수}

## 최상의 버전
{수정된 코드}
```

## Gotchas (실패 포인트)

- **너무 많은 지적**: 15개 우선순위에 집중, 완벽주의 금지
- **범위 이탈**: 요청받은 코드만 검토, 인접 코드 개선 금지 (Boy Scout는 별도)
- **ADK 검토 시**: ToolContext state 접근 패턴, tool function 시그니처를 반드시 확인
- **false negative**: mypy strict 통과해도 런타임 오류 가능 — 경계값 테스트 필수

## 관련 CLAUDE.md 규칙

| 규칙 | 위치 | 내용 |
|------|------|------|
| 구현 시 필수 스킬 | CLAUDE.md | 마지막 단계로 반드시 실행 |
| @AW-007 | team-operations.md | 모든 구현 ralph + verifier 검증 |
| Goal-Driven Execution | CLAUDE.md § LLM 행동지침 | success criteria → 검증 → 반복 |

## 참조

- `/quality/check/anti-patterns` — 안티패턴 먼저 탐지
- `/reference/python` — Python 컨벤션 기준
- [team-operations.md](../../../docs/design/ref/team-operations.md) § AW-007
