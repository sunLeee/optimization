# libs/ — 최적화 라이브러리

## 역할

항구 최적화 시스템의 핵심 알고리즘 모듈 모음.
외부 의존: `pyomo`, `highspy`, `cvxpy`, `scipy`, `numpy`.

## 모듈 구조

```
libs/
├── utils/         공통 유틸리티 (geo, constants, 인터페이스 계약)
├── fuel/          연료 소비 모델
├── scheduling/    BAP, TSP-T MILP, Benders Decomposition
├── routing/       ALNS + eco-speed alternating
├── stochastic/    Rolling Horizon Orchestrator, 2-stage SAA
├── simulation/    에이전트 시뮬레이션 환경
├── optimization/  목적함수 Strategy Pattern (ObjectiveStrategy Protocol, 4종 구현체)
├── evaluation/    실데이터 백테스터 (RealDataBacktester)
├── solver/        알고리즘 Strategy Pattern (SolverStrategy Protocol, 4종 래퍼) [신규]
└── visualization/ 시각화 (수렴 곡선, OSM 지도, MP4 애니메이션) [신규]
```

## 의존 방향 (AW-007) — 절대 준수

```
libs/stochastic   → libs/scheduling   → libs/utils
libs/stochastic   → libs/routing      → libs/utils
libs/stochastic   → libs/fuel         → libs/utils
libs/stochastic   → libs/optimization → libs/utils
libs/optimization → libs/fuel         → libs/utils
libs/evaluation   → libs/optimization → libs/utils
libs/evaluation   → libs/fuel         → libs/utils
libs/evaluation   → libs/solver       → libs/scheduling → libs/utils
                                      → libs/routing    → libs/utils
                                      → libs/stochastic → libs/utils
libs/visualization → libs/utils       (solver에 의존 금지 — SolveResult는 solver에서 임시 받음)
```

**역방향 금지**: `routing → scheduling`, `scheduling → stochastic`,
`optimization → stochastic`, `evaluation → stochastic` 등.
위반 발생 시 → `check-anti-patterns` 실행 후 `libs/utils/`로 이동.

## 새 모듈 추가 시 체크리스트

1. 의존 방향 AW-007 준수 확인
2. `libs/utils/__init__.py`에 공개 API export 추가 (utils 모듈인 경우)
3. 파라미터 단위 suffix 규칙 준수 (`_min`, `_kn`, `_nm`, `_mt`, `_sec`)
4. 공개 API: `solve() → OptResult` 패턴 통일
5. `check-anti-patterns` + `check-python-style` 실행
