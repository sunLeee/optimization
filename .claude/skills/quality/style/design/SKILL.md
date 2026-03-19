---
name: convention-design
triggers:
  - "convention design"
description: 설계 원칙(SRP, KISS, DRY, YAGNI, SoC)이 불명확할 때. 클래스/함수 분리 기준이 필요할 때. "설계 원칙 알려줘", "클래스 어떻게 나눠?", "God Class 어떻게 해결해?" 요청 시. 개별 원칙은 /reference/philosophy/solid/srp 등 전용 skill 사용.
argument-hint: "[원칙] - srp, kiss, dry, yagni, soc, all"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
model: claude-sonnet-4-6[1m]
context: 소프트웨어 설계 원칙 빠른 참조 스킬. 핵심 5가지 원칙 요약. 상세 내용은 reference/philosophy/ 카테고리 skill 참조.
agent: 소프트웨어 설계 전문가. 원칙을 간결하게 설명하고 현재 코드에 적용 가능한 개선 방향을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references:
  - "@skills/reference/philosophy/solid/srp/SKILL.md"
  - "@skills/reference/philosophy/principles/kiss/SKILL.md"
  - "@skills/reference/philosophy/principles/dry/SKILL.md"
referenced-by:
  - "@skills/quality/check/anti-patterns/SKILL.md"
---

# convention-design

핵심 설계 원칙 빠른 참조. 개별 원칙 상세는 `reference/philosophy/` 카테고리 참조.

## 5가지 핵심 원칙

| 원칙 | 한 줄 요약 | 상세 skill |
|------|----------|-----------|
| **SRP** | 클래스는 변경 이유가 하나여야 한다 | `/reference/philosophy/solid/srp` |
| **KISS** | 단순하게 유지하라 | `/reference/philosophy/principles/kiss` |
| **DRY** | 지식은 단일 표현 — 중복 금지 | `/reference/philosophy/principles/dry` |
| **YAGNI** | 필요할 때만 구현 | `/reference/philosophy/principles/yagni` |
| **SoC** | 관심사를 분리하라 | `/reference/philosophy/principles/soc` |

## 빠른 판단 기준

```
클래스가 200줄 넘으면? → SRP 위반, 분리 필요
같은 로직이 3곳에? → DRY 위반, 추출 필요
"혹시 나중에 쓸지도?" → YAGNI 위반, 삭제
비즈니스 로직 + 파일 I/O 혼재? → SoC 위반, 분리
추상화 5단계 넘으면? → KISS 위반, 단순화
```

## ADK 도메인 적용

```python
# SoC 위반 — tool에서 비즈니스 로직 + I/O 혼재
def analyze_and_save(tool_context):
    df = pd.read_csv(...)  # I/O
    result = df.groupby(...)  # 비즈니스
    with open(...) as f: json.dump(...)  # I/O

# CORRECT — 분리
def load_data(tool_context): ...      # I/O 전담
def analyze(tool_context): ...        # 비즈니스 전담
def save_result(tool_context): ...    # I/O 전담
```

## Gotchas

- **원칙 간 충돌**: DRY와 SoC가 충돌하면 → SoC 우선 (관심사 분리가 더 중요)
- **YAGNI vs 확장성**: "확장할 것 같아서" → YAGNI 위반. 실제 요구가 생기면 그때 추가
- **SRP의 "변경 이유"**: 단순히 메서드 수가 아닌 "무엇이 변할 때 이 클래스가 바뀌는가"로 판단

## 참조

- 상세 원칙: `reference/philosophy/solid/` (SOLID 5원칙)
- 상세 원칙: `reference/philosophy/principles/` (KISS, DRY, YAGNI, SoC)
- [team-operations.md](../../../docs/design/ref/team-operations.md) § AW-012~020
