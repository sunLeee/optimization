# 항구 최적화 알고리즘 선택 가이드

**생성일**: 2026-03-19  
**분야**: 수학적 최적화 — 예인선·선박·항구 복합 스케줄링  
**파라미터**: n (선박 수), m (예인선 수), T (계획 기간), k (선석 수)

---

## 1. 문제 정의 및 복잡도 근거

항구 최적화 문제는 세 가지 하위 문제의 결합이다.

| 하위 문제 | 단독 복잡도 | 결합 시 추가 복잡도 |
|-----------|------------|-------------------|
| 선박 입·출항 스케줄링 (BAP) | NP-Hard | O(n · k) coupling |
| 예인선 배정 (TAP) | NP-Hard | O(n · m) matching |
| 선석 할당 (BAP+TAP) | NP-Hard | O(n · m · k · T) |

결합 문제의 탐색 공간 크기:

- 상태 공간: O(n! · m^n · k^n · T^n)
- 완전 열거는 n ≥ 15 이상에서 실용 불가 (> 10^15 상태)

---

## 2. 문제 규모별 복잡도 분류

### 소규모 (n < 10, m < 5) — Exact Methods 적용 가능

| 알고리즘 | 시간 복잡도 | 공간 복잡도 | n=5 ops | n=10 ops |
|----------|------------|------------|---------|---------|
| Branch & Bound | O(2^n) worst | O(n) | 3.2×10¹ | 1.0×10³ |
| Dynamic Programming | O(n² · 2^n) | O(n · 2^n) | 8.0×10² | 1.0×10⁵ |
| MIP (CPLEX/Gurobi) | O(2^n · log n) | O(n²) | 8.3×10¹ | 3.3×10³ |

**선택 기준**: n < 10이고 최적해가 필수이면 MIP(CPLEX/Gurobi)를 우선한다. B&B는 bounds 품질에 민감하므로 tight relaxation이 없으면 DP보다 느릴 수 있다.

**[FINDING] Exact methods의 실용 한계**: n = 20에서 B&B 탐색 노드 수는 약 10^6, n = 30에서는 10^9을 초과하여 단일 코어 기준 1시간 이상 소요된다.  
[STAT:n] n = 2 ~ 30 (분석 범위)  
[STAT:effect_size] n=20 vs n=10: ops 비율 = 2^10 = 1024배 증가 (지수적)

---

### 중규모 (n = 10~50, m = 5~20) — Heuristics 권장

| 알고리즘 | 시간 복잡도 | 매개변수 | 실용 런타임 (n=30) |
|----------|------------|---------|-----------------|
| Greedy | O(n²) | — | < 1 ms |
| 2-opt | O(n²) per pass | passes: 10~100 | < 100 ms |
| 3-opt | O(n³) per pass | passes: 10~50 | < 5 sec |
| Tabu Search | O(n² · iter) | iter: 500~2000 | 1~30 sec |
| Simulated Annealing | O(n · iter) | iter: 10^4~10^6 | 5~60 sec |

**선택 기준**: 시간 제약이 엄격하면 Greedy → 2-opt 체인. 해 품질이 우선이면 Tabu Search (tenure 길이 = n/3 권장).

**[FINDING] 2-opt vs 3-opt 품질-시간 트레이드오프**: n=30 기준 3-opt는 2-opt 대비 평균 2~4% 추가 품질 향상을 제공하지만 런타임은 O(n) 배 증가한다.  
[STAT:effect_size] 품질 향상 2~4% (문헌 평균, VRP 벤치마크 기준)  
[STAT:n] n = 10~50 적용 범위

---

### 대규모 (n = 50~100, m = 20~50) — Metaheuristics 권장

| 알고리즘 | 시간 복잡도 | 권장 파라미터 | 실용 런타임 (n=75) |
|----------|------------|------------|-----------------|
| Genetic Algorithm (GA) | O(n · gen · pop) | gen=500, pop=200 | 2~10 min |
| Ant Colony Opt (ACO) | O(n² · ants · iter) | ants=50, iter=500 | 5~20 min |
| Large Neighborhood Search (LNS) | O(n · log n · iter) | iter=2000 | 1~5 min |

**선택 기준**:  
- **LNS 우선**: 항구 도메인에서 destroy/repair 연산자를 자연스럽게 정의 가능 (예: 특정 시간대 예인선 배정 재계획). 런타임 대비 해 품질이 GA/ACO보다 우수한 경향.  
- **GA**: 다목적 최적화(비용 + 시간 + 연료)가 필요할 때 Pareto front 탐색에 적합.  
- **ACO**: 경로 최적화 성분이 강할 때 (예인선 이동 경로) 적합.

**[FINDING] LNS의 scalability 우위**: LNS는 O(n · log n · iter)로 ACO O(n² · ants · iter) 대비 n=75에서 약 37배 연산량이 적다.  
[STAT:effect_size] 연산 비율 = (75² × 50 × 500) / (75 × log(75) × 2000) ≈ 37×  
[STAT:n] n = 50~100

---

### 초대규모 (n > 100, m > 50) — Decomposition 필수

| 알고리즘 | 적용 방식 | 수렴 보장 | 구현 난이도 |
|----------|---------|---------|-----------|
| Dantzig-Wolfe Decomp | Master + pricing subproblems | Yes (LP bound) | 높음 |
| Benders Decomp | Master (선석) + sub (예인선) | Yes (cuts) | 중간 |
| Column Generation (CG) | 경로/패턴 열 생성 | Yes (LP relaxation) | 높음 |
| CG + LNS (Hybrid) | CG로 하한, LNS로 feasible sol | Heuristic | 중간 |

**선택 기준**:  
- 선석 할당(BAP)을 master, 예인선 배정(TAP)을 subproblem으로 분리하는 **Benders decomposition**이 항구 도메인 구조에 가장 자연스럽게 맞음.  
- Column Generation은 예인선 경로(route)를 열(column)로 모델링할 때 적합.  
- 초기 feasible solution은 반드시 Greedy/LNS로 warm-start할 것.

**[FINDING] Benders vs DW 선택**: 선석 수 k ≤ 20이면 Benders가 구현 복잡도 대비 효율적. k > 20이면 DW + Lagrangian relaxation 조합이 수렴 속도에서 우위.  
[STAT:n] n > 100, k > 20 기준  
[STAT:effect_size] Benders cut 수 ∝ O(k × iter); DW column 수 ∝ O(n × patterns)

---

## 3. 거리 함수별 복잡도 및 선택 기준

| 거리 함수 | 연산 복잡도 | 정확도 | 적용 상황 |
|----------|------------|------|---------|
| 유클리드 거리 | O(1)/쌍, 상수 ≈ 5 flops | 낮음 | 초기 파일럿, 알고리즘 검증 |
| Haversine (구면 거리) | O(1)/쌍, 상수 ≈ 20 flops | 중간 | GPS 좌표 기반 open-sea 구간 |
| 실제 항로 (API) | O(1)/cached 쌍 | 높음 | 프로덕션; 캐싱 필수 |

**캐싱 전략 (API 기반)**:
```
pairwise 거리 행렬 크기: n² pairs
n=50  → 2,500 API 호출 (1회 사전 계산 후 캐시)
n=100 → 10,000 API 호출
n=200 → 40,000 API 호출
권장: Redis 또는 SQLite 로컬 캐시, TTL = 24hr (조류/날씨 반영 갱신 주기)
```

**[FINDING] Haversine vs 실제 항로 오차**: 항구 내 좁은 수로에서 Haversine 오차는 10~40%까지 발생 가능. 예인선 비용 계산에 실제 항로 필수.  
[STAT:effect_size] 오차 범위 10~40% (항구 지형 복잡도에 따라 다름)  
[LIMITATION] 실제 항로 API 오차 수치는 특정 항구의 실측 데이터 없이 문헌 기반 추정값임.

---

## 4. 시간 기간 T 및 선석 k 의 영향

- **T (계획 기간)**: Rolling-horizon 적용 시 전체 복잡도는 O(알고리즘 복잡도 × T/window). Window 크기를 n에 비례해 설정 권장 (window ≈ 2n 시간 단위).
- **k (선석 수)**: k개 선석은 k개의 병렬 스케줄을 생성. Lagrangian relaxation으로 선석 coupling 제거 가능. k > 20이면 반드시 분리 접근법 적용.

---

## 5. 알고리즘 결정 트리 (요약)

```
START: (n, m, k, T) 파라미터 확인
│
├── n < 10 AND m < 5?
│   └── YES → MIP (gurobipy / python-mip) → 최적해 보장
│
├── n ≤ 50 AND m ≤ 20?
│   └── YES → Tabu Search / 2-opt (simanneal / 자체 구현)
│              └── 시간 < 1min 필요 → Greedy + 2-opt
│
├── n ≤ 100 AND m ≤ 50?
│   └── YES → LNS 우선 (OR-Tools LNS / 자체 구현)
│              └── 다목적 → DEAP (GA) / Pareto front
│
└── n > 100 OR m > 50?
    └── YES → Benders Decomp (Pyomo + GLPK/Gurobi)
               └── k > 20 → Dantzig-Wolfe / Column Generation
               └── Warm-start → Greedy or LNS initial solution
```

---

## 6. Python 구현 라이브러리 매핑

| 알고리즘 범주 | 라이브러리 | 설치 | 비고 |
|-------------|----------|------|-----|
| MIP / B&B | `gurobipy` | 상용 (학술 무료) | 최고 성능 solver |
| MIP (오픈소스) | `pulp`, `python-mip` | pip | CBC/GLPK backend |
| MIP (Google) | `ortools` | pip | CP-SAT solver 포함 |
| Tabu Search | `자체 구현` + `numpy` | — | 도메인 특화 필수 |
| SA | `simanneal` | pip | 간단한 인터페이스 |
| GA | `deap` | pip | 다목적 지원 (NSGA-II) |
| ACO | `자체 구현` + `numpy` | — | 항구 그래프 특화 |
| LNS | `ortools` LNS / 자체 | pip | destroy/repair 커스텀 |
| Benders | `pyomo` + `glpk`/`gurobi` | pip | 분리 모델링 |
| Column Gen | `gurobipy` + 자체 pricing | — | B&P 프레임워크 |
| 거리 계산 | `geopy` (Haversine) | pip | API 캐시는 `diskcache` |

---

## 7. 한계 및 주의사항

[LIMITATION] 모든 복잡도 수치는 worst-case 또는 문헌 평균 기반이며, 실제 항구 인스턴스의 구조적 특성(대기 패턴, 조류 스케줄, 우선순위 선박)에 따라 크게 달라질 수 있다.

[LIMITATION] MIP solver(CPLEX/Gurobi)의 실제 성능은 LP relaxation 품질, cutting planes, presolve에 의존하며, 이론적 worst-case보다 훨씬 빠른 경우가 많다. 중규모(n=20~50)에서 MIP가 Tabu Search보다 빠를 수 있다.

[LIMITATION] 메타휴리스틱 파라미터(population size, iteration count, cooling schedule)는 인스턴스마다 튜닝이 필요하다. 본 문서의 runtime 추정은 기본 파라미터 기준이다.

[LIMITATION] Decomposition 방법의 수렴 속도는 subproblem 구조에 크게 의존한다. Benders cut 품질이 낮으면 수렴이 느리거나 실패할 수 있다.

[LIMITATION] 실제 항로 API 오차 수치(10~40%)는 항구별 실측 데이터 없이 문헌 기반 추정값이다.

---

## 8. 시각화 참조

| 그림 | 내용 | 경로 |
|-----|------|-----|
| Fig 1 | 알고리즘 클래스별 복잡도 곡선 (log scale) | `.omc/scientist/figures/fig1_complexity_curves.png` |
| Fig 2 | 문제 규모 × 알고리즘 적합도 히트맵 | `.omc/scientist/figures/fig2_suitability_heatmap.png` |
| Fig 3 | 결정 트리 플로우차트 | `.omc/scientist/figures/fig3_decision_tree.png` |
| Fig 4 | 실용 런타임 추정 (초 단위, log scale) | `.omc/scientist/figures/fig4_runtime_estimates.png` |

---

*Scientist agent — port-opt-complexity session — 2026-03-19*

---

## 9. 프로젝트 결정 사항 (deep-interview 2026-03-20 확정)

본 문서의 일반 가이드와 달리, 이 프로젝트의 실제 Tier 경계는 deep-interview 결과를 따른다.

| Tier | 규모 | 알고리즘 | 솔버/프레임워크 | 연료 모델 |
|------|------|---------|----------------|---------|
| **Tier 1** | n < 10 | Exact MILP (McCormick 선형화) | Pyomo + HiGHS | F=α·d (선형) |
| **Tier 2** | n = 10~50 | **ALNS** (Ropke & Pisinger 2006) + eco-speed alternating | 자체 구현 + CVXPY GP | F=α·v^2.5·d |
| **Tier 3** | n > 50 | Benders Decomposition (Master HiGHS + Sub IPOPT) | Pyomo | F=α·v^2.5·d |

> 주의: 문서 섹션 2의 "중규모 (n=10~50)"는 일반 문헌 기준 Tabu/2-opt를 권장하지만,
> 본 프로젝트에서는 커스터마이징 자유도를 위해 ALNS를 Tier 2로 채택한다.
> ALNS는 destroy/repair 연산자를 도메인 특화 방식으로 정의 가능하여
> 예인선 배정 재계획(time-window aware) 구현에 최적이다.

**γ=2.5 처리 전략 (Tier별)**:
- Tier 1: F=α·d 완전 선형화 (속도 고정, Step 1 구현)
- Tier 2: ALNS outer loop에서 x 고정 후 CVXPY GP로 eco-speed 최적화 (alternating)
- Tier 3: Benders subproblem에서 IPOPT로 연속 속도 최적화
