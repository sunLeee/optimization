# 항구 최적화 — 수학적 참조 문서

**작성일**: 2026-03-22 | **버전**: Phase 4 기준

---

## 1. 결정변수 (Decision Variables)

### 1.1 TSP-T MILP (Tier 1, n < 10)

| 변수 | 도메인 | 설명 |
|------|--------|------|
| `x_ij_k ∈ {0,1}` | Binary | 예인선 k가 job i 직후 job j를 수행하면 1 |
| `s_j_k ≥ 0` | Continuous | 예인선 k의 job j 시작 시간 (minutes) |
| `y_j_k ∈ {0,1}` | Binary | 예인선 k가 job j를 수행하면 1 |
| `d_j ≥ 0` | Continuous | job j의 대기시간 보조변수 (linearization) |

### 1.2 Benders Decomposition (Tier 3, n > 50)

**Master Problem:**

| 변수 | 도메인 | 설명 |
|------|--------|------|
| `y_jk ∈ {0,1}` | Binary | 예인선 k가 vessel j를 서비스하면 1 |
| `θ ≥ 0` | Continuous | Benders surrogate 비용 변수 |

**Subproblem (y 고정 후 연속 최적화):**

| 변수 | 도메인 | 설명 |
|------|--------|------|
| `v_ij ≥ 0` | Continuous | arc (i→j) 이동 속도 (knots) |
| `t_j ≥ 0` | Continuous | vessel j 서비스 시작 시간 (minutes) |

### 1.3 ALNS (Tier 2, n = 10~50)

ALNS는 메타휴리스틱으로 명시적 결정변수 없음.
내부 상태: `routes: dict[str, list[str]]` — 예인선별 서비스 순서.

### 1.4 Rolling Horizon (MPC)

각 타임스텝에서 Tier별 솔버를 재호출. 결정변수는 해당 Tier와 동일.
"첫 번째 결정만 실행" (MPC 원칙): 지평선 내 첫 배정만 확정.

---

## 2. 목적함수 (Objective Functions)

### 2.1 MILP 내부 목적함수

```
min  w1 · Σ_j (priority_j × d_j / 60)    [대기시간 비용, hours]
   + w2 · Σ_{i,j,k} (α × dist_ij × x_ij_k)  [연료 비용, 선형 F=α·d]

기본값: w1=1.0, w2=0.01, α=0.5
```

### 2.2 ObjectiveStrategy 4종 (libs/optimization/objective.py)

| ID | 이름 | 수식 | 설명 |
|----|------|------|------|
| OBJ-A | `MinWaitObjective` | `min Σ(priority × wait_h)` | 우선순위 가중 대기시간 최소화 |
| OBJ-B | `MinIdleObjective` | `min Σ idle_h` | 예인선 유휴시간 최소화 |
| OBJ-C | `MinCompositeObjective` | `min w2·idle_h + w3·priority×wait_h` | 가중합 (기본: w2=w3=0.5) |
| OBJ-D | `MinAllObjective` | `min w_idle·idle_h + w_wait·wait_h + λ·dist_nm` | 4대 KPI 사후집계 |

**KPI 정의 (KPIResult)**:

| KPI | 단위 | 계산식 |
|-----|------|--------|
| `dist_nm` | 해리 | 총 이동거리 (RouteResult 주입 필요; 미주입 시 0.0) |
| `idle_h` | 시간 | `Σ_tug Σ_gap max(0, s_{i+1} - (s_i + duration_i)) / 60` |
| `wait_h` | 시간 | `Σ_j priority_j × max(0, scheduled_start_j - earliest_start_j) / 60` |
| `fuel_mt` | 메트릭톤 | 현재 미구현 (0.0 fallback) |

---

## 3. 제약 조건 (Constraints)

### 3.1 공통 제약

| 번호 | 이름 | 수식 | 설명 |
|------|------|------|------|
| C1 | 배정 | `Σ_k y_j_k = 1` | 각 vessel 정확히 하나의 예인선 |
| C2a | 흐름 보존 (in) | `Σ_{i≠j} x_ij_k = y_j_k` | 진입 흐름 = 배정 |
| C2b | 흐름 보존 (out) | `Σ_{j≠i} x_ij_k = y_i_k` | 진출 흐름 = 배정 |
| C3a | 시간창 하한 | `s_j_k ≥ e_j · y_j_k` | earliest_start 준수 |
| C3b | 시간창 상한 | `s_j_k ≤ l_j · y_j_k + M·(1-y_j_k)` | latest_start 준수 |
| C4 | 순서 (Big-M) | `s_j_k ≥ s_i_k + dur_i + travel(i→j) - M·(1-x_ij_k)` | 선행 후행 순서 |

**Big-M 계산**: `M = max(l_j + dur_j) - min(e_j)` (데이터 기반, tight)

### 3.2 Benders Cut

```
θ ≥ α_k + Σ_{j,k'} β_{j,k'} · y_{j,k'}
```

- `α_k`: Subproblem 비용 (서브그레디언트 기준점)
- `β_{j,k'}`: 한계비용 (대안 배정 비용 증분)

---

## 4. 알고리즘 요약 (Algorithms)

### 4.1 TSP-T MILP (Tier 1)

- **분류**: Exact, Branch-and-Bound
- **솔버**: Pyomo + HiGHS (appsi_highs)
- **복잡도**: NP-hard in general; n<10에서 실용적
- **수렴 기준**: MIP optimality gap ≤ 5% 또는 time_limit_sec
- **연료 모델**: 선형 근사 `F = α·dist_nm` (γ=1, 선형화)
- **수렴 로그**: 단일 call, per-iteration 없음

### 4.2 ALNS + EcoSpeed (Tier 2)

- **분류**: 메타휴리스틱 (이론적 수렴 보장 없음)
- **Outer loop**: EcoSpeedOptimizer alternating (max_outer_iter=20)
- **Inner loop**: ALNS Destroy-Repair-Accept (max_iter=200)
- **수렴 기준**: `|Δcost_avg| / cost < tol=0.001` (window 평균, oscillation 완화)
- **SA acceptance**: `P(accept) = exp(-Δ/T)`, T₀=0.1, cooling=0.995
- **Adaptive weight**: σ1=33 (new best), σ2=9 (improve), σ3=3 (accept), ρ=0.1
- **연료 모델**: `F(v,d) = α·v^2.5·d` (EcoSpeedOptimizer, AW-006)
- **수렴 로그**: `RouteResult.iterations` (outer loop 횟수), `converged` flag

| Destroy Op | 설명 | 복잡도 |
|------------|------|--------|
| D1 Random | 무작위 제거 | O(n) |
| D2 Worst | 최고 비용 제거 | O(n log n) |
| D3 Shaw | Relatedness (거리+시간+우선순위) | O(n²) |
| D4 TimeWindow | 혼잡 시간대 제거 | O(n) |

| Repair Op | 설명 | 복잡도 |
|-----------|------|--------|
| R1 Greedy Insert | 최소 비용 삽입 | O(n²·m) |
| R2 Regret-2 | 최선-차선 차이 최대화 | O(n²·m·log n) |

### 4.3 Benders Decomposition (Tier 3)

- **분류**: Exact (LP relaxation 기반 lower bound)
- **솔버**: Master→HiGHS(MILP), Subproblem→Greedy+EcoSpeed
- **수렴 기준**: `(UB-LB)/UB ≤ gap_tol=0.05` 또는 max_iter=50
- **초기 UB**: ALNS warm-start
- **수렴 로그**: 최종 LB/UB 저장, per-iteration 이력 Phase 7 예정

### 4.4 Rolling Horizon (MPC)

- **분류**: 온라인 알고리즘 (Receding Horizon Control)
- **수평선**: horizon_h=2.0h, 재최적화 주기 dt_h=0.5h
- **Tier 자동**: n<10→MILP, n<50→ALNS, n≥50→Benders
- **원칙**: 첫 번째 결정만 확정 후 재최적화

---

## 5. ETA 불확실성 분포 (AW-010)

**실측값 (2024-06 부산항, N=336):**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| `mu_log` | 4.015 | Log-normal μ (지연 중앙값 55.4분) |
| `sigma_log` | 1.363 | Log-normal σ |
| `clip` | [-6h, +6h] | 클리핑 범위 (±6h → 89.6% 커버) |
| 지연 비율 | 71.4% | |
| 조기 도착 | 28.6% | |

**분포 선택 기준:**
- N ≥ 200: KDE (Gaussian kernel)
- N < 200: Log-normal (MLE 피팅)
- 데이터 없음: TruncatedNormal(-2h, +2h)

---

## 6. 연료 모델 (AW-006)

```
F(v, d) = α · v^γ · d

γ = 2.5  (실제 항구 데이터 피팅, AW-006 고정값)
α = 0.5  (연료 계수, MT/nm/kn^2.5)
```

**단순화**: `F ≈ α · d` (γ=1 선형화, MILP Tier 1에서 적용)

---

## 7. CVaR (Conditional Value at Risk)

**Phase 4 Robustness 분석에 사용:**

```
CVaR_α = VaR_α + E[(cost - VaR_α)^+ | cost > VaR_α]
       = (1/(1-α)) · E[cost · 1{cost ≥ VaR_α}]

α = 0.95 (상위 5% 최악 시나리오 평균)
```

구현: `libs/stochastic/two_stage.py compute_cvar(scenario_costs, alpha=0.95)`

---

## 8. 모듈-수식 매핑

| 모듈 | 수식 구현 | 관련 섹션 |
|------|----------|---------|
| `libs/scheduling/tsp_t_milp.py` | TSP-T MILP (C1~C4, Big-M) | §3.1 |
| `libs/scheduling/benders.py` | Benders Master+Sub | §3.2, §4.3 |
| `libs/routing/alns.py` | ALNS + EcoSpeed | §4.2 |
| `libs/stochastic/rolling_horizon.py` | MPC Tier 선택 | §4.4 |
| `libs/stochastic/two_stage.py` | CVaR95 계산 | §7 |
| `libs/optimization/objective.py` | OBJ-A/B/C/D KPI | §2.2 |
| `libs/fuel/consumption.py` | F(v,d)=α·v^γ·d | §6 |
| `libs/evaluation/robustness.py` | Monte Carlo + CVaR | §5, §7 |
