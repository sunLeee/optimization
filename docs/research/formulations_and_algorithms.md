# 수식 및 알고리즘 체계 — 인천항 예선 스케줄링 최적화
## Mathematical Formulations and Algorithms — Incheon Harbor Tugboat Scheduling

> **대상 독자**: 프로젝트 참여 연구자, NotebookLM 질의 베이스
> **데이터 출처**: 2024-06 인천항 실측 (FristAllSchData N=967, SchData N=336)
> **최종 업데이트**: 2026-03-22

---

## Part 1: 수학적 수식 정의 (Mathematical Formulations)

### 1.1 Multi-Resource Gang Scheduling MILP

**문제 클래스**: Multi-Resource Vehicle Routing Problem with Time Windows (MR-VRPTW)
**적용 범위**: 전체 967건 예선 배정 최적화
**적용 조건**: n_jobs ≤ 50 (AW-005); 초과 시 Greedy fallback

**결정 변수**:

| 변수 | 도메인 | 의미 |
|------|--------|------|
| y[j,k] | {0,1} | 예선 k가 서비스 j에 배정 |
| x[i,j,k] | {0,1} | 예선 k가 서비스 i를 j보다 먼저 수행 (순서 변수) |
| s[j] | ≥ 0 | 서비스 j 시작 시각 (분, day-relative) |
| w[j] | ≥ 0 | 선박 대기 = max(0, s[j] − e[j]) |

**제약 조건**:

| ID | 수식 | 의미 |
|----|------|------|
| C1 | Σ_k y[j,k] = r_j, ∀j | Gang requirement: 서비스 j에 정확히 r_j척 동시 배정 |
| C2 | e[j] ≤ s[j] ≤ l[j], ∀j | 시간창 (earliest/latest start) |
| C3 | x[i,j,k]+x[j,i,k] ≥ y[i,k]+y[j,k]−1, ∀i,j,k | 순서-배정 연결 |
| C4 | x[i,j,k]+x[j,i,k] ≤ 1, ∀i<j,k | 방향 상호 배제 |
| C5 | s[j] ≥ s[i]+d[i]+t(end_i,start_j)−M(1−x[i,j,k]) | 이동시간 포함 비겹침 |
| C6_ik | x[i,j,k] ≤ y[i,k], ∀i,j,k | Arc-bound cut (Phantom arc 방지) |
| C6_jk | x[i,j,k] ≤ y[j,k], ∀i,j,k | Arc-bound cut |
| C7 | w[j] ≥ s[j]−e[j], w[j] ≥ 0 | 대기시간 선형화 |

**목적함수**:

```
min Σ_j priority(j) × w[j]
```

**Big-M 계산**:

```
M = max(l[j] + d[j]) − min(e[j]) + max(t[i,j])
상한: M ≤ 3×1440 분 (day-relative 보장, 초과 시 epoch 오류로 예외 발생)
```

**변수 규모** (n=32, K=12 예선 기준):
- x 변수: n²×K = 12,288 binary
- y 변수: n×K = 384 binary
- 연속 변수: s, w 각 n개

**구현 위치**: `libs/scheduling/multi_tug_milp.py`, `libs/scheduling/multi_tug.py`
**관련 논문**: Rodrigues et al. (2021) [TSP-1], Viana et al. (2020) [TSP-3], Lübbecke & Desrosiers (2005), Hendriks et al. (2010)

---

### 1.2 Travel Time Matrix (이동시간 행렬)

**수식**:

```
t(A,B) = real_lookup[(A,B)]   if (A,B) ∈ real_lookup (SchData 실측 중앙값)
       = haversine_nm(A,B) / speed_kn × 60 × route_factor   otherwise
```

**haversine 거리** (`libs/utils/geo.py`):

```
d_nm = 2 × 3440.065 × arctan2(√a, √(1−a))
a    = sin²(Δlat/2) + cos(lat1)×cos(lat2)×sin²(Δlon/2)
```

(지구 반경 R = 3440.065 해리)

**파라미터**:

| 파라미터 | 값 | 출처 |
|---------|-----|------|
| speed_kn (AIS 실측) | 6.0 kn | SchData 2024-06 기반 fleet 속도 |
| route_factor | 1.8 | 항만 항로 보정 (실측값/haversine 비율 중앙값 기준 캘리브레이션, 신뢰 구간 1.6~2.0×) |
| fallback_min | 31.0분 | SchData 작업까지 이동시간 중앙값 (미지 코드 폴백) |

**실측 lookup 구축** (`libs/data/loader.py:build_real_travel_lookup()`):
- SchData 에서 (출발지, 도착지) 쌍별 실측 이동시간 중앙값 추출
- 유효성 검증: `0.3 ≤ 실측값/haversine ≤ 3.0` 범위만 포함 (대기시간 혼입 이상값 제외)
- 최소 관측 건수: 2건 이상인 경로만 포함

**노드 집합**: 111 선석 + 4 정계지 = 115 노드 (AIS 보조 좌표 포함 시 확장)

**구현 위치**: `libs/utils/travel_time.py`, `libs/data/loader.py`
**관련 논문**: Fang et al. (2013) — AIS 기반 이동시간 추정

---

### 1.3 Stochastic ETA Delay Distribution (AW-010)

**수식**:

```
delay_i ~ (1 − p_d) × Uniform(−360, 0)  +  p_d × LogNormal(μ_log, σ_log)
결과 클립: delay_i ∈ [−360, +360] 분
```

**파라미터** (2024-06 인천항 실측 N=336, ADR-001):

| 파라미터 | 값 | 의미 |
|---------|-----|------|
| μ_log | 4.015 | Log-normal 위치 파라미터 (자연로그 스케일) |
| σ_log | 1.363 | Log-normal 척도 파라미터 |
| p_d | 0.714 | 지연 발생 확률 (71.4% 지연, 28.6% 조기 도착) |
| clip | [−360, +360] 분 | ±6시간 클립 (±2h 커버 81.5% → ±6h 89.6%) |

**CVaR95 계산** (`libs/evaluation/robustness.py`):

```
VaR_95  = Q_95(cost_distribution)       (95번째 백분위수)
CVaR_95 = E[cost | cost > VaR_95]       (꼬리 기댓값, strict greater-than)
```

**구현 위치**: `libs/evaluation/robustness.py`, `scripts/stochastic_robustness_full.py`
**관련 논문**: Agra et al. (2013), Golias et al. (2009), Rockafellar & Uryasev (2000)

---

### 1.4 Newsvendor Model (도선사 최적 배차)

**문제**: 불확실 선박 도착 하에 도선사 출발 시각 최적화

**수식**:

```
Critical ratio:  cr = w_v / (w_v + w_p)
Effective quantile: q_eff = max(0, (cr − (1 − p_d)) / p_d)
Optimal buffer:  b* = F^{−1}(q_eff)   where F = LogNormal(μ_log, σ_log) CDF
```

| 파라미터 | 값 | 의미 |
|---------|-----|------|
| w_v | 2 | 선박 대기 단위비용 (상대값) |
| w_p | 1 | 도선사 대기 단위비용 (상대값) |
| b* | 계산값 (AW-010 분포 기준) | 최적 버퍼 (분) |

**도선사 출발 시각**:

```
t_depart = t_service_start − t_travel − b*
```

도선사 출발지: PAL (팔미 파일럿 스테이션, 37.463117°N, 126.596133°E)
도선사 이동속도: 20.0 km/h

**구현 위치**: `scripts/pilot_analysis.py`
**관련 논문**: Arrow et al. (1951), Fagerholt et al. (2010)

---

### 1.5 필요 예선 수 결정 규칙 (Tug Requirement Rule)

**수식** (`libs/data/loader.py:compute_required_tugs()`):

```
r_j = 1   if tonnage_mt < 5,000
r_j = 2   if 5,000  ≤ tonnage_mt < 30,000
r_j = 3   if 30,000 ≤ tonnage_mt < 60,000
r_j = 4   if tonnage_mt ≥ 60,000
```

**데이터 근거**: SchData 실측 (N=336) 톤수별 실제 배정 예선 수 분포

**Gang scheduling 동기화 제약** (`libs/scheduling/multi_tug.py`):

```
Σ_{k∈K} y_jk = r_j          (필요 예선 수 충족)
s_jk = S_j  ∀k: y_jk=1      (동시 작업 시작 — 동기화)
S_j ≥ e_j                   (시간창 하한)
S_j ≤ l_j                   (시간창 상한)
```

---

## Part 2: 알고리즘 (Algorithms)

### 2.1 HiGHS MILP Solver

**유형**: Branch-and-Bound (B&B) Mixed Integer Linear Programming
**인터페이스**: Pyomo `appsi_highs` (HiGHS 1.x)

**적용 조건**: n_jobs ≤ 50 (AW-005)

**솔버 파라미터** (`libs/scheduling/multi_tug_milp.py`):

```python
solver.options["time_limit"] = 60.0    # 초
solver.options["mip_rel_gap"] = 0.05   # 5% MIP gap 허용
```

**종료 조건**: `optimal` 또는 `feasible` — 그 외 조건 시 Greedy fallback

**구현 흐름**:
1. Pyomo `ConcreteModel`로 변수/제약/목적함수 구성
2. `appsi_highs`로 풀이
3. 결과 추출: `y[j,k] > 0.5`이면 배정, `s[j]`에서 시작 시각 추출

**관련 논문**: Huangfu & Hall (2018)

---

### 2.2 Travel-time-aware Greedy (이동시간 인식 그리디)

**유형**: Priority-based greedy heuristic
**적용 조건**: n_jobs > 50 fallback 또는 MILP 실패 시, 실시간 배정

**알고리즘 의사코드** (`libs/scheduling/multi_tug.py:assign_multi_tug_greedy()`):

```
Input:  서비스 목록 (earliest_start 순 정렬), tug_fleet
Init:   tug_free_at[k] = 0.0  ∀k

For each service j (earliest_start 순):
    sorted_tugs = sort(tug_fleet, key=tug_free_at)
    selected   = sorted_tugs[:r_j]          # 가장 빨리 가용한 r_j척
    max_free   = max(tug_free_at[k] for k in selected)
    start      = max(earliest_start[j], max_free)  # 동기화
    For each tug in selected:
        tug_free_at[tug] = start + service_duration[j]
    record MultiTugAssignment(vessel_id, tug_ids=selected, start_time=start)
```

**시간 복잡도**: O(n × K × log K)
**특성**: 100% 물리적 실행가능성 보장, optimality_gap = NaN (경험적 해)

---

### 2.3 ALNS (Adaptive Large Neighborhood Search)

**유형**: Metaheuristic — random restart greedy
**구현 방식**: Random-restart greedy (n_restarts=20)

**알고리즘** (`scripts/run_nm_benchmark_full.py` 등):

```
best = greedy(windows, tug_fleet)
For i in range(20):
    shuffled   = random.shuffle(windows)
    candidate  = greedy(shuffled, tug_fleet)
    if objective(candidate) < objective(best):
        best = candidate
Return best
```

**적용**: N×M 벤치마크 비교 실험
**관련 논문**: Agra et al. (2013) — ALNS for maritime routing

---

### 2.4 Monte Carlo Simulation (확률적 강건성)

**유형**: Stochastic simulation
**파라미터**: n_mc=200 시나리오, seed=42 (`scripts/stochastic_robustness_full.py`)

**알고리즘** (`libs/evaluation/robustness.py:RobustnessAnalyzer`):

```
rng = default_rng(seed=42)

# 지연 행렬 샘플링 (shape: n_mc × n_vessels)
is_delayed  = rng.random((n_mc, n)) < p_d            # 71.4% 지연 마스크
delay_pos   = rng.lognormal(μ_log, σ_log, (n_mc, n)) # 지연 (양수)
delay_neg   = −rng.uniform(0, 360, (n_mc, n))         # 조기 도착 (음수)
delays      = where(is_delayed, delay_pos, delay_neg)
delays      = clip(delays, −360, +360)

For each scenario mc:
    actual_arrival = earliest_start + delays[mc, :]
    extra_wait     = max(0, actual_arrival − scheduled_start)
    cost[mc]       = Σ_j priority_j × extra_wait_j / 60

CVaR95 = mean(cost[cost > percentile(cost, 95)])
```

**구현 위치**: `libs/evaluation/robustness.py`, `scripts/stochastic_robustness_full.py`

---

### 2.5 Distribution Fitting (분포 피팅)

**알고리즘**: Maximum Likelihood Estimation (MLE) via `scipy.stats`
**구현**: `scripts/fit_eta_parameters.py`

**적용 분포**:

| 대상 | 분포 | 주요 파라미터 |
|------|------|------------|
| 선박 도착 지연 | Log-normal | μ=4.015, σ=1.363 |
| 서비스 시간 | 실측값 직접 사용 (SchData) | — |
| AIS 예선 속도 | 중앙값 통계 | fleet 중앙값 (SOG > 0.5 kn 필터) |
| 톤수 | 구간 규칙 (1.5) | 4구간 이산화 |

**AIS 속도 파생** (`libs/utils/travel_time.py:derive_speed_from_ais()`):
- `_tug_` 패턴 CSV 파일에서 SOG > 0.5 kn 행만 사용
- 파일별 중앙값 → 전체 중앙값 → [1.0, 20.0] kn 클립

---

## Part 3: 수식 ↔ 알고리즘 ↔ 구현 매핑

| 수식/모델 | 구현 알고리즘 | 구현 파일 | 관련 논문 |
|---------|------------|---------|---------|
| Gang Scheduling MILP (C1~C7) | HiGHS B&B | `libs/scheduling/multi_tug_milp.py` | TSP-1, TSP-3 |
| Travel Time Matrix | AIS 캘리브레이션 + haversine | `libs/utils/travel_time.py` | Fang et al. (2013) |
| Time Window Scheduling | Travel-time Greedy | `libs/scheduling/multi_tug.py` | VRP-1, TSP-1 |
| ETA Stochastic Model | Monte Carlo CVaR | `libs/evaluation/robustness.py` | Agra et al. (2013) |
| Multi-resource assignment | MILP C1 (Σy=r_j) | `libs/scheduling/multi_tug_milp.py` | TSP-3, Viana et al. |
| Newsvendor pilot dispatch | Closed-form F^{−1} | `scripts/pilot_analysis.py` | Arrow et al. (1951) |
| Rolling horizon | Greedy (real-time) | `libs/stochastic/rolling_horizon.py` | — |
| ALNS metaheuristic | Random restart Greedy | `scripts/run_nm_benchmark_full.py` | Agra et al. (2013) |
| Tug requirement rule | 톤수 구간 이산화 | `libs/data/loader.py` | TSP-3 (r_j 파라미터) |
| AIS speed derivation | 중앙값 통계 | `libs/utils/travel_time.py` | Fang et al. (2013) |

---

## Part 4: 모듈 의존 방향 (AW-007)

```
libs/stochastic  → libs/scheduling  → libs/utils
libs/stochastic  → libs/routing     → libs/utils
libs/stochastic  → libs/fuel        → libs/utils
libs/evaluation  → libs/solver      → libs/scheduling → libs/utils
                                    → libs/routing    → libs/utils
libs/data        (standalone — libs/utils만 의존)
```

역방향 참조 금지: `routing → scheduling`, `scheduling → stochastic`, `evaluation → stochastic`

---

## Part 5: NotebookLM 활용 가이드

이 문서를 NotebookLM에 업로드하면 다음 질문에 답할 수 있다:

1. "이 프로젝트에서 사용한 MILP 제약 조건은 무엇인가?"
   → Part 1.1 — C1~C7 제약 테이블 참조

2. "Gang Scheduling과 일반 VRP의 차이는?"
   → C1 제약 (Σy=r_j)이 핵심 — 단일 예선이 아닌 r_j척 동시 투입 요구

3. "CVaR95를 왜 사용하는가? 수식은?"
   → Part 1.3 — 꼬리 위험 최소화; CVaR = E[cost | cost > Q_95]

4. "도선사 최적 배차 시각은 어떻게 계산하나?"
   → Part 1.4 — Newsvendor critical ratio → LogNormal quantile → buffer b*

5. "어떤 알고리즘이 어떤 상황에서 사용되는가?"
   → Part 2 + Part 3 매핑 테이블 참조; n≤50 → MILP, n>50 → Greedy/ALNS

6. "Big-M은 어떻게 계산하나? 너무 크면 어떻게 되는가?"
   → Part 1.1 — M = max(l[j]+d[j]) − min(e[j]) + max(t[i,j]); 3×1440 초과 시 epoch 오류 감지

7. "AIS 데이터에서 예선 속도를 어떻게 추출하나?"
   → Part 2.5 — _tug_ 파일 SOG > 0.5 kn 필터 → 파일별 중앙값 → fleet 전체 중앙값

8. "ETA 지연 분포 파라미터의 데이터 근거는?"
   → Part 1.3 — 2024-06 인천항 N=336 실측, μ_log=4.015, σ_log=1.363, p_d=0.714
