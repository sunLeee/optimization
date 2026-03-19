# ADR-028: pytest + AAA 패턴 + 80% 커버리지

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
pytest 사용. Arrange-Act-Assert 패턴 의무. 커버리지: 핵심 로직 90%, 전체 80%.

## 이유
- AAA: 테스트 의도 명확, 유지보수 용이
- pytest: Python 표준 테스트 프레임워크, fixture 강력
- 80%: 너무 낮으면 회귀 위험, 너무 높으면 비용 증가

## Gotchas
- `@pytest.mark.unit/integration` 마커 필수 → `-m unit`으로 빠른 실행
- Mock 과다 사용 → 실제 동작과 괴리 → ADK ToolContext는 real 객체 권장

## 결과
- testing.md rule: 90%/80% 기준 통일
- convention-testing skill에 상세 예시
