# 항구 최적화 수학적 용어집

> **범위**: 항구 예인선·선박 스케줄·경로·연료 최적화 프로젝트에서 사용되는 전문용어
> **갱신**: 2026-03-20

---

## 목차

1. [문제 유형 (Problem Types)](#1-문제-유형-problem-types)
2. [알고리즘 (Algorithms)](#2-알고리즘-algorithms)
3. [확률적 최적화 (Stochastic Optimization)](#3-확률적-최적화-stochastic-optimization)
4. [복잡도 이론 (Complexity Theory)](#4-복잡도-이론-complexity-theory)
5. [해양·항구 전문용어 (Maritime)](#5-해양항구-전문용어-maritime)
6. [솔버 (Solvers)](#6-솔버-solvers)

---

## 1. 문제 유형 (Problem Types)

### 요약 테이블

| 약어 | 한국어 명칭 | 복잡도 | 프로젝트 적용 |
|------|------------|--------|--------------|
| VRP | 차량 경로 문제 | NP-hard | 예인선 다중 경로 기반 프레임워크 |
| VRPTW | 시간창 차량 경로 문제 | NP-hard | Tier 2 예인선 경로 (n=10~50) |
| TSP | 순회 판매원 문제 | NP-hard | 단일 예인선 스케줄 하한 |
| TSP-T | 예인선 스케줄링 문제 | NP-hard | 핵심 문제 — `libs/scheduling/tsp_t_milp.py` |
| BAP | 선석 배정 문제 | NP-hard | 상위 결정: 선박→선석 배정 |
| TRP | 수리 순회 문제 | NP-hard | 우선순위 대기 비용 모델링 참조 |
| CVRP | 용량 제약 차량 경로 문제 | NP-hard | bollard pull 제약 적용 시 |
| PDPTW | 픽업·배달 시간창 문제 | NP-hard | 예인선 입출항 양방향 서비스 |
| MIP | 혼합 정수 계획 | — | MILP/MINLP의 상위 범주 |
| MILP | 혼합 정수 선형 계획 | — | Tier 1·3 주 모델 형식 |
| MINLP | 혼합 정수 비선형 계획 | — | 연료 모델 $\alpha v^\gamma d$ 포함 시 |
| LP | 선형 계획 | P | MILP 완화(relaxation) |
| QP | 이차 계획 | P (볼록) | 속도 최적화 완화 |
| GP | 기하 계획 | 볼록 | 연료·속도 트레이드오프 연구 참조 |
| HVTM | 항만 선박 교통 관리 | NP-hard (일반) | 항로 혼잡·안전 간격 제약 |

---

### 세부 설명

#### VRP — Vehicle Routing Problem

- **한국어**: 차량 경로 문제
- **정의**: 단일 또는 복수의 depot에서 출발하는 차량들이 고객 집합을 모두 방문하고 귀환하는 최소 비용 경로를 구하는 문제.
- **수식**:

$$\min \sum_{k \in K} \sum_{i \in N} \sum_{j \in N} c_{ij} x_{ijk}$$

- **프로젝트 적용**: 예인선(tug)을 차량, 서비스 요청을 고객으로 매핑하는 기반 프레임워크. VRPTW로 특화됨.

---

#### VRPTW — Vehicle Routing Problem with Time Windows

- **한국어**: 시간창 차량 경로 문제
- **정의**: VRP에 각 고객 방문 시간 제약 $[a_i, b_i]$를 추가한 문제. Solomon (1987) 벤치마크로 알고리즘 성능을 측정함.
- **수식**: 시간창 제약

$$a_i \leq T_i^k \leq b_i \qquad \forall i \in N,\; k \in K$$

- **프로젝트 적용**: Tier 2 (n=10~50). `libs/routing/alns.py`의 `ALNSWithSpeedOptimizer`가 VRPTW 형식으로 예인선 경로를 계산함. Solomon R101(25 node) BKS 대비 5% 이내를 성공 기준으로 사용.

---

#### TSP — Travelling Salesman Problem

- **한국어**: 순회 판매원 문제
- **정의**: 단일 차량이 모든 도시를 정확히 한 번 방문하고 출발지로 돌아오는 최소 거리 경로를 구하는 문제. 조합 최적화의 표준 기준 문제.
- **수식**:

$$\min \sum_{i} \sum_{j \neq i} c_{ij} x_{ij}, \quad x_{ij} \in \{0,1\}$$

- **프로젝트 적용**: 단일 예인선 스케줄(TSP-T)의 기반 구조. NP-hardness 환원 기준점.

---

#### TSP-T — Tugboat Scheduling Problem

- **한국어**: 예인선 스케줄링 문제
- **정의**: 복수의 예인선을 복수의 선박 서비스 요청에 할당하고 각 예인선의 방문 순서·시간창을 결정하는 조합 최적화 문제. Rodrigues et al. (2021) 정식화 기준.
- **수식**: 목적함수 (이동비용 + 우선순위 대기 페널티)

$$\min \; w_1 \sum_{k,j} \text{priority}_j \cdot d_j / 60 + w_2 \sum_{k,i,j} \alpha \cdot d_{ij} \cdot x_{ij}^k$$

여기서 $d_j$는 job $j$의 대기 시간(분), $x_{ij}^k \in \{0,1\}$은 예인선 $k$가 $i$ 직후 $j$를 수행하는지 나타냄.

- **프로젝트 적용**: 핵심 문제. Tier 1 (n<10): `libs/scheduling/tsp_t_milp.py`의 `TugScheduleModel`이 Pyomo+HiGHS MILP로 정확해를 계산함.

---

#### BAP — Berth Allocation Problem

- **한국어**: 선석 배정 문제
- **정의**: $n$척의 선박을 항구 선석에 할당하여 총 대기시간·체선료를 최소화하는 문제. 공간(선석 위치)과 시간(접안 시각) 양 차원에서 비중복 제약을 가짐.
- **수식**: 이산 BAP 목적함수

$$\min \sum_{i \in V} \omega_i \left( C_i - a_i \right)$$

여기서 $C_i$는 선박 $i$의 출항 시각, $a_i$는 도착 시각, $\omega_i$는 중요도 가중치.

- **프로젝트 적용**: TSP-T의 상위 결정. BAP 결과가 예인 수요의 시간창 $[e_j, l_j]$를 결정함. `libs/scheduling/benders.py`의 Master Problem이 BAP+TSP-T 통합 배정을 담당.

---

#### TRP — Travelling Repairman Problem

- **한국어**: 수리 순회 문제 (최소 대기시간 TSP)
- **정의**: 순회 판매원 문제의 변형으로, 총 이동 거리가 아닌 각 고객의 누적 대기 시간 합(sum of completion times)을 최소화하는 문제.
- **수식**:

$$\min \sum_{i=1}^{n} C_i \quad \text{(각 고객의 서비스 완료 시각 합)}$$

- **프로젝트 적용**: 우선순위 가중 대기 비용 모델 $\sum \text{priority}_j \times \text{wait}_j$의 이론적 참조점.

---

#### CVRP — Capacitated VRP

- **한국어**: 용량 제약 차량 경로 문제
- **정의**: VRP에 각 차량의 최대 용량 $Q$를 추가. 경로 내 총 수요가 $Q$를 초과할 수 없음.
- **수식**: 용량 제약

$$\sum_{i \in N} q_i x_{ijk} \leq Q \qquad \forall k \in K$$

- **프로젝트 적용**: 예인선의 최대 bollard pull 또는 연료 탱크 용량을 $Q$로 모델링할 때 적용.

---

#### PDPTW — Pickup and Delivery Problem with Time Windows

- **한국어**: 픽업·배달 시간창 문제
- **정의**: 각 요청이 픽업 위치와 배달 위치를 가지며, 픽업이 배달보다 먼저 이루어져야 하는 쌍(pairing) 제약과 시간창 제약을 동시에 만족해야 하는 VRP 변형.
- **프로젝트 적용**: 예인선의 입항(pickup)·출항(delivery) 양방향 서비스를 단일 경로 문제로 모델링하는 구조적 참조.

---

#### MIP — Mixed Integer Programming

- **한국어**: 혼합 정수 계획
- **정의**: 일부 결정변수가 정수(또는 이진)이고 나머지는 연속인 최적화 문제의 총칭. MILP와 MINLP를 포함하는 상위 범주.
- **프로젝트 적용**: 배정 변수 $x_{ij}^k, y_{jk} \in \{0,1\}$와 연속 시간 변수 $s_j^k \geq 0$을 동시에 포함하는 모든 모델의 범주.

---

#### MILP — Mixed Integer Linear Programming

- **한국어**: 혼합 정수 선형 계획
- **정의**: MIP 중 목적함수와 모든 제약이 선형인 문제. 연료 비용을 $F = \alpha \cdot d$ (선형)로 근사하면 MILP로 다룰 수 있음.
- **프로젝트 적용**: Tier 1 `tsp_t_milp.py` (Phase 2 Step 1: 속도 고정, 연료 선형 근사), Tier 3 `benders.py`의 Master Problem. HiGHS로 풀이.

---

#### MINLP — Mixed Integer Nonlinear Programming

- **한국어**: 혼합 정수 비선형 계획
- **정의**: MIP 중 목적함수 또는 제약에 비선형 항이 포함된 문제. 일반적으로 풀기 더 어려우며 전역 최적해 보장이 어려움.
- **수식**: 연료 비선형 항 ($\gamma=2.5$)

$$F(v, d) = \alpha \cdot v^{\gamma} \cdot \frac{d}{v} = \alpha \cdot v^{\gamma-1} \cdot d, \quad \gamma \in [2, 3]$$

- **프로젝트 적용**: 속도 변수 $v$를 포함한 연료 모델. Phase 2 Step 2에서 ALNS+EcoSpeedOptimizer의 alternating loop로 비선형성을 처리함.

---

#### LP — Linear Programming

- **한국어**: 선형 계획
- **정의**: 목적함수와 제약이 모두 선형인 최적화 문제. 다항 시간에 최적해 도출 가능(Simplex, Interior Point).
- **프로젝트 적용**: MILP의 LP 완화(relaxation)로 Lower Bound 계산. Benders Decomposition의 각 반복에서 Master의 LB 갱신에 사용.

---

#### QP — Quadratic Programming

- **한국어**: 이차 계획
- **정의**: 목적함수가 이차식이고 제약이 선형인 최적화 문제. 볼록 QP는 다항 시간에 풀 수 있음.
- **프로젝트 적용**: 속도 최적화를 $\min \sum \alpha v_k^2 d_k$ (거리 가중 이차식)으로 정식화할 때의 구조. `libs/fuel/eco_speed.py`의 `EcoSpeedOptimizer` 참조.

---

#### GP — Geometric Programming

- **한국어**: 기하 계획
- **정의**: 목적함수와 제약이 포시노미얼(posynomial) 형태인 비선형 최적화. 로그 변환으로 볼록 문제로 변환 가능.
- **프로젝트 적용**: 연료-속도 관계 $\alpha v^\gamma d$의 볼록 구조 분석에 사용되는 이론적 참조 프레임워크.

---

#### HVTM — Harbor Vessel Traffic Management

- **한국어**: 항만 선박 교통 관리
- **정의**: 항만 내 항로·교차로에서 복수 선박의 통과 순서와 속도를 결정하여 충돌 방지와 처리량 최대화를 동시에 달성하는 문제.
- **수식**: 안전 간격 제약 (Big-M 선형화)

$$\tau_j^r \geq \tau_i^r + \text{gap} - M(1 - \sigma_{ij}^r) \qquad \forall i \neq j,\; r$$

- **프로젝트 적용**: ETA 불확실성이 항로 혼잡을 통해 선석 배정에 영향을 미치는 상위 계층 모델. `docs/research/mathematical_formulation.md` Section 5 참조.

---

## 2. 알고리즘 (Algorithms)

### 요약 테이블

| 약어 | 한국어 명칭 | 유형 | 프로젝트 Tier |
|------|------------|------|--------------|
| B&B | 분기 한정법 | 정확해 | 내부 (HiGHS 내장) |
| B&P | 분기 가격법 | 정확해 | 참조 |
| ALNS | 적응형 대규모 이웃 탐색 | 메타휴리스틱 | Tier 2 |
| LNS | 대규모 이웃 탐색 | 메타휴리스틱 | ALNS 기반 |
| SA | 모의 담금질 | 메타휴리스틱 | ALNS 수용 기준 |
| GA | 유전 알고리즘 | 진화 알고리즘 | 참조 |
| ACO | 개미 군집 최적화 | 군집 지능 | 참조 |
| PSO | 입자 군집 최적화 | 군집 지능 | 참조 |
| Column Generation | 열 생성법 | 정확해 분해 | 참조 |
| Benders | 벤더스 분해 | 정확해 분해 | Tier 3 |
| Dantzig-Wolfe | 단치그-울프 분해 | 정확해 분해 | 참조 |
| RHO | 롤링 호라이즌 최적화 | 온라인/재최적화 | 확률 실험 최우수 |
| MPC | 모델 예측 제어 | 온라인/피드백 | RHO 동의어 |

---

### 세부 설명

#### B&B — Branch and Bound

- **한국어**: 분기 한정법
- **정의**: 정수 계획의 정확해 알고리즘. LP 완화로 하한을 계산하고, 이진 변수를 0/1로 분기하며 탐색 트리를 구성. 상한 이하인 노드만 탐색하여 최적해를 보장.
- **프로젝트 적용**: HiGHS 솔버가 내부적으로 B&B를 실행. `tsp_t_milp.py`에서 `mip_rel_gap=0.05` 설정으로 gap 5% 이내에서 조기 종료.

---

#### B&P — Branch and Price

- **한국어**: 분기 가격법
- **정의**: B&B와 Column Generation을 결합. 각 분기 노드에서 LP 완화를 Column Generation으로 풀어 변수(열)를 동적 생성. VRPTW 정확해에 표준적으로 사용.
- **프로젝트 적용**: 대규모 VRPTW 정확해의 이론적 참조. Barnhart et al. (1998) 기반.

---

#### ALNS — Adaptive Large Neighborhood Search

- **한국어**: 적응형 대규모 이웃 탐색
- **정의**: Ropke & Pisinger (2006)이 제안한 메타휴리스틱. 복수의 Destroy 연산자(해의 일부 제거)와 Repair 연산자(재삽입)를 확률적으로 선택하며 반복 개선. 성능에 따라 연산자 가중치를 동적으로 조정.
- **수식**: SA 수용 기준

$$P(\text{accept}) = \exp\!\left(-\frac{\Delta \text{cost}}{T}\right), \quad T \leftarrow T \times \text{cooling}$$

- **프로젝트 적용**: Tier 2 (n=10~50). `libs/routing/alns.py`의 `ALNSWithSpeedOptimizer`. Destroy: `destroy_random` + `destroy_worst` (50:50 혼합), Repair: `repair_greedy_insert`. EcoSpeedOptimizer와 교대(alternating) 반복으로 속도 최적화.

---

#### LNS — Large Neighborhood Search

- **한국어**: 대규모 이웃 탐색
- **정의**: 현재 해의 일부(large neighborhood)를 파괴(destroy)하고 재구성(repair)하는 방식의 지역 탐색. ALNS의 기반 알고리즘.
- **프로젝트 적용**: ALNS의 단일 연산자 버전으로 이해할 수 있음. `destroy_fraction=0.3`으로 각 반복마다 경로의 30%를 제거.

---

#### SA — Simulated Annealing

- **한국어**: 모의 담금질
- **정의**: 물리의 담금질(annealing) 과정을 모방한 확률적 최적화. 나쁜 해도 확률 $e^{-\Delta/T}$로 수용하며 지역 최적해를 탈출. 온도 $T$를 점차 낮추며 수렴.
- **프로젝트 적용**: `ALNSConfig.temperature=0.1`, `cooling=0.995`. ALNS 내부 루프의 해 수용 기준으로 사용.

---

#### GA — Genetic Algorithm

- **한국어**: 유전 알고리즘
- **정의**: 진화론에서 영감을 받은 메타휴리스틱. 해 집단(population)에 선택(selection), 교차(crossover), 돌연변이(mutation)를 적용하여 세대를 거쳐 개선.
- **프로젝트 적용**: 이론적 참조 (Kim & Moon 2003, BAP). 현재 구현에서는 ALNS를 사용.

---

#### ACO — Ant Colony Optimization

- **한국어**: 개미 군집 최적화
- **정의**: 개미의 페로몬 통신을 모방한 확률적 최적화. 좋은 경로에 페로몬을 축적하여 후속 개미의 경로 선택 확률을 높임. TSP·VRP에 효과적.
- **프로젝트 적용**: 이론적 참조. 현재 구현에서는 ALNS를 사용.

---

#### PSO — Particle Swarm Optimization

- **한국어**: 입자 군집 최적화
- **정의**: 새 떼의 이동을 모방한 군집 지능 알고리즘. 각 입자가 개인 최적(pbest)과 전체 최적(gbest) 방향으로 속도를 갱신하며 탐색.
- **프로젝트 적용**: 연속 속도 최적화(eco-speed)의 이론적 참조 알고리즘.

---

#### Column Generation

- **한국어**: 열 생성법
- **정의**: LP/MILP에서 변수(열) 수가 매우 많을 때 모든 열을 사전에 열거하지 않고, 비용을 낮출 수 있는 열을 반복적으로 생성하는 분해 기법. Master Problem + Pricing Subproblem 구조.
- **수식**: Reduced cost 조건

$$\bar{c}_j = c_j - \mathbf{\pi}^T A_j < 0$$

이 조건을 만족하는 열 $j$를 Pricing Problem으로 탐색.

- **프로젝트 적용**: VRPTW 정확해(B&P)의 핵심 구성요소. 참조 연구 기반 (Desrosiers et al. 1995).

---

#### Benders Decomposition

- **한국어**: 벤더스 분해
- **정의**: 이진 변수(복잡한 제약 연결)를 포함하는 큰 MIP를 Master Problem과 Subproblem으로 분리. Master가 이진 변수를 고정하면 Subproblem이 연속 변수를 최적화하여 Benders Cut을 생성, Master에 추가. 수렴할 때까지 반복.
- **수식**: Optimality cut

$$\theta \geq \alpha_k + \beta_k^T y \qquad \text{(누적 Benders Cut)}$$

- **프로젝트 적용**: Tier 3 (n>50). `libs/scheduling/benders.py`의 `BendersDecomposition`. Master: HiGHS (배정 이진변수 $y_{jk}$), Subproblem: eco-speed 고정 + 그리디 스케줄. 성능 목표: n=75, 10분 이내, gap ≤ 5%.

---

#### Dantzig-Wolfe Decomposition

- **한국어**: 단치그-울프 분해
- **정의**: 블록 구조(block-diagonal)를 가진 LP를 분해하는 기법. 각 블록의 LP를 독립적으로 풀고 Master Problem이 볼록 결합(convex combination)으로 전체 해를 구성. Column Generation의 이론적 기반.
- **프로젝트 적용**: Column Generation과 B&P의 이론적 기반. VRPTW 정확해 분석 참조.

---

#### Rolling Horizon (RHO) — Rolling Horizon Optimization

- **한국어**: 롤링 호라이즌 최적화
- **정의**: 전체 계획 기간을 짧은 구간으로 분할하여 매 주기마다 재최적화하는 온라인 전략. 가장 가까운 구간의 결정만 실행하고 새 정보가 들어오면 수평선을 한 주기 앞으로 이동.
- **수식**: 각 시점 $k$에서의 최적화

$$\min_{u_{k|k},\ldots,u_{k+N-1|k}} \sum_{j=0}^{N-1} L(\hat{x}_{k+j|k}, u_{k+j|k}) + V(\hat{x}_{k+N|k})$$

- **프로젝트 적용**: `libs/stochastic/simulation.py`의 `rolling_horizon_schedule`. 2,000회 OOS Monte Carlo 실험에서 CVaR95=95.25로 5개 방법론 중 최우수 성능. 재최적화 주기 `horizon_h=2.0` (2시간).

---

#### MPC — Model Predictive Control

- **한국어**: 모델 예측 제어
- **정의**: 제어 공학에서 Rolling Horizon과 동일한 구조. 현재 상태를 측정하여 미래 시스템 거동을 예측하고, 예측 구간 내 비용을 최소화하는 제어 입력을 결정. 첫 번째 입력만 실제로 적용.
- **프로젝트 적용**: RHO와 동의어로 사용. 예인선 실시간 배차 시스템의 참조 아키텍처.

---

## 3. 확률적 최적화 (Stochastic Optimization)

### 요약 테이블

| 약어 | 한국어 명칭 | 프로젝트 적용 |
|------|------------|--------------|
| SAA | 표본 평균 근사 | K=200 시나리오, 수렴 최적점 |
| SP | 확률 계획법 | 2-stage SP 구조 |
| CCP | 기회 제약 계획법 | ε=0.05, 95% 신뢰수준 |
| DRO | 분포적 강건 최적화 | Wasserstein 거리 기반 참조 |
| ETA | 예상 도착 시각 | 입력 불확실성 원천 |
| ATA | 실제 도착 시각 | OOS 평가의 실현 값 |
| KDE | 커널 밀도 추정 | 역사 데이터 ≥200개 시 분포 추정 |
| GMM | 가우시안 혼합 모델 | 날씨 혼합 분포 모델 |
| CVaR | 조건부 위험 가치 | 95% CVaR로 방법론 비교 |

---

### 세부 설명

#### SAA — Sample Average Approximation

- **한국어**: 표본 평균 근사
- **정의**: 기댓값 목적함수를 유한 개의 시나리오 표본으로 근사하는 방법. $N$개 시나리오에 대한 평균 비용을 최소화하며, $N \to \infty$이면 참 해에 수렴(w.p.1).
- **수식**:

$$\min_{x \in X} f_N(x) = \frac{1}{N} \sum_{s=1}^{N} f(x, \xi^s)$$

2-stage 형식:

$$\min_x \; c^T x + \mathbb{E}[Q(x, \xi)], \quad Q(x,\xi) = \min_y\{q^T y : Wy = h - Tx,\; y \geq 0\}$$

- **프로젝트 적용**: `libs/stochastic/simulation.py`의 `two_stage_saa_schedule`. 실험 결과 K=200이 수렴·계산비용의 최적 균형점. `n_scenarios` 파라미터로 제어.

---

#### SP — Stochastic Programming

- **한국어**: 확률 계획법
- **정의**: 불확실한 파라미터 $\xi$를 확률 변수로 명시적으로 모델링하고, 기댓값이나 분위수 같은 통계적 목적함수를 최적화하는 방법론의 총칭.
- **수식**: 일반 형식

$$\min_{x} \; c^T x + \mathbb{E}_\xi[Q(x, \xi)]$$

- **프로젝트 적용**: ETA 불확실성(날씨 지연 $\pm 2$h)을 확률 변수로 모델링. `libs/stochastic/simulation.py`에서 5개 방법론(Deterministic, SAA, CCP, Robust, Rolling Horizon)을 2,000회 OOS 비교.

---

#### CCP — Chance-Constrained Programming

- **한국어**: 기회 제약 계획법
- **정의**: 제약 위반 확률이 허용 수준 $\varepsilon$ 이하가 되도록 요구하는 확률 최적화. 개별 기회 제약(ICC)과 결합 기회 제약(JCCP)으로 구분.
- **수식**: 개별 기회 제약

$$\Pr[g(x, \xi) \leq 0] \geq 1 - \varepsilon$$

SAA 선형화:

$$g(x, \xi^s) \leq M z_s, \quad \sum_{s=1}^N z_s \leq \lfloor \varepsilon N \rfloor, \quad z_s \in \{0,1\}$$

- **프로젝트 적용**: `chance_constrained_schedule`에서 $\varepsilon=0.05$ (95% 신뢰수준). $(1-\varepsilon)$ 분위수를 버퍼 시간으로 사용. 해양 운영에서 $\varepsilon \in [0.01, 0.10]$이 일반적.

---

#### DRO — Distributionally Robust Optimization

- **한국어**: 분포적 강건 최적화
- **정의**: 진짜 확률 분포를 모르는 상황에서, 분포들의 집합(ambiguity set) 중 최악의 분포에 대해 최적화하는 방법. Wasserstein 거리 기반 ambiguity set이 최근 표준.
- **수식**: Wasserstein DRO

$$\min_x \; \sup_{\mathbb{P} \in \mathcal{B}_\rho(\hat{\mathbb{P}}_N)} \mathbb{E}^\mathbb{P}[f(x, \xi)]$$

여기서 $\mathcal{B}_\rho(\hat{\mathbb{P}}_N)$은 경험 분포 $\hat{\mathbb{P}}_N$ 주변 반경 $\rho$의 Wasserstein ball.

- **프로젝트 적용**: Nadales et al. (2023), Zhao et al. (2022) 기반 이론 참조. `docs/research/stochastic_scheduling.md` Wasserstein-DRO 섹션.

---

#### ETA — Estimated Time of Arrival

- **한국어**: 예상 도착 시각
- **정의**: 선박이 특정 지점(선석, 항구 입구)에 도착할 것으로 예상되는 시각. AIS 신호와 항로 정보를 바탕으로 계산. 실제 도착(ATA)과의 편차가 스케줄 불확실성의 주요 원천.
- **프로젝트 적용**: `libs/scheduling/tsp_t_milp.py`에서 `eta_j = earliest_start_j`로 사용. 대기 시간 $d_j \geq s_j - \text{eta}_j$ 제약의 기준값.

---

#### ATA — Actual Time of Arrival

- **한국어**: 실제 도착 시각
- **정의**: 선박이 실제로 도착한 시각. ETA 대비 편차(delay)가 날씨, 항로 혼잡, 항구 운영 등 불확실성 요인으로 발생.
- **프로젝트 적용**: OOS 시뮬레이션에서 `actual_arrival = job.arrival_time + delays[idx]`로 실현. ETA-ATA 편차 분포가 `make_delay_distribution`의 입력.

---

#### KDE — Kernel Density Estimation

- **한국어**: 커널 밀도 추정
- **정의**: 비모수적 확률 밀도 추정 방법. 각 데이터 포인트 주위에 커널 함수(보통 Gaussian)를 배치하고 합산하여 연속 밀도 함수를 추정.
- **수식**:

$$\hat{f}(x) = \frac{1}{Nh} \sum_{i=1}^{N} K\!\left(\frac{x - x_i}{h}\right)$$

- **프로젝트 적용**: `make_delay_distribution`에서 역사 ATA-ETA 편차 데이터 $\geq 200$개일 때 `stats.gaussian_kde`로 지연 분포를 추정. 파라메트릭 분포가 불충분할 때 대안.

---

#### GMM — Gaussian Mixture Model

- **한국어**: 가우시안 혼합 모델
- **정의**: 복수의 Gaussian 분포를 가중 결합하여 복잡한 다봉(multimodal) 분포를 표현하는 모델.
- **수식**:

$$p(x) = \sum_{k=1}^{K} \pi_k \cdot \mathcal{N}(x \mid \mu_k, \sigma_k^2), \quad \sum_k \pi_k = 1$$

- **프로젝트 적용**: `_empirical_mixture`에서 날씨 좋음(calm, 70%) + 나쁨(rough, 30%) 혼합 분포로 구현. $K=2$인 GMM 구조.

---

#### CVaR — Conditional Value at Risk

- **한국어**: 조건부 위험 가치
- **정의**: 손실 분포의 상위 $(1-\alpha)$ 분위수를 초과하는 손실의 기댓값. VaR(Value at Risk)보다 극단 손실에 민감하며 볼록 위험 척도.
- **수식**:

$$\text{CVaR}_\alpha(X) = \mathbb{E}[X \mid X \geq \text{VaR}_\alpha(X)]$$

SAA 추정:

$$\widehat{\text{CVaR}}_{0.95} = \frac{1}{|\{s : c^s \geq q_{0.95}\}|} \sum_{s:\, c^s \geq q_{0.95}} c^s$$

- **프로젝트 적용**: `evaluate_method`에서 95번째 백분위수 초과 비용의 평균으로 계산. Rolling Horizon이 CVaR95=95.25로 5개 방법론 중 최우수. 극단적 날씨 지연에 대한 방법론 강건성 비교 지표.

---

## 4. 복잡도 이론 (Complexity Theory)

### 요약 테이블

| 개념 | 의미 | 항구 최적화 관련성 |
|------|------|-------------------|
| NP-hard | 다항 시간 알고리즘 미발견 | TSP-T, VRPTW, BAP 모두 해당 |
| NP-complete | NP-hard + NP 소속 | 결정 버전 문제들 |
| P vs NP | 미해결 핵심 문제 | 정확해 알고리즘의 이론적 한계 |
| Big-O | 점근 복잡도 표기 | 알고리즘 확장성 분석 |
| Polynomial time | 다항 시간 알고리즘 존재 | LP, QP (볼록) |

---

### 세부 설명

#### NP-hard

- **한국어**: NP-난해
- **정의**: NP에 속하는 모든 문제를 다항 시간 내에 환원할 수 있는 문제 클래스. NP-hard 문제는 다항 시간 정확해 알고리즘이 알려져 있지 않음.
- **수식**: 환원 관계

$$\text{TSP} \leq_p \text{TSP-T} \leq_p \text{VRPTW}$$

- **프로젝트 적용**: TSP-T (단일 예인선: TSP 환원), VRPTW (VRP 환원), BAP (2D Bin Packing 환원). 대규모 인스턴스에서 정확해 대신 ALNS·Benders를 사용하는 근거.

| 문제 | 복잡도 | 환원 근거 |
|------|--------|----------|
| TSP-T (단일 예인선) | NP-hard | TSP 환원 |
| TSP-T (다중 예인선) | NP-hard | mTSP 환원 |
| VRPTW | NP-hard | VRP 환원 |
| BAP (이산·연속) | NP-hard | 2D Bin Packing 환원 |
| 통합 BAP+TSP-T | NP-hard | 부분 문제가 NP-hard |

---

#### NP-complete

- **한국어**: NP-완전
- **정의**: NP-hard이면서 동시에 NP에 속하는 결정 문제. "해가 존재하는가"를 묻는 결정 버전이 NP-complete이면, 최적화 버전은 NP-hard.
- **프로젝트 적용**: TSP-T의 결정 버전("비용 $C$ 이하인 예인 스케줄이 존재하는가")이 NP-complete.

---

#### P vs NP

- **한국어**: P 대 NP 문제
- **정의**: P(다항 시간에 풀 수 있는 결정 문제)와 NP(다항 시간에 검증 가능한 결정 문제)가 동일한지에 대한 미해결 문제. P=NP이면 NP-hard 문제에도 다항 시간 알고리즘이 존재.
- **프로젝트 적용**: 현재 P≠NP로 간주하여 ALNS, Benders 등 근사·분해 알고리즘을 채택한 이론적 근거.

---

#### Big-O notation

- **한국어**: 빅-O 표기법
- **정의**: 알고리즘의 점근적 최악 시간·공간 복잡도를 표현하는 표기. 입력 크기 $n$에 대한 실행 시간의 상한을 나타냄.
- **수식**: 정의

$$f(n) = O(g(n)) \iff \exists c > 0,\; n_0 : f(n) \leq c \cdot g(n) \; \forall n \geq n_0$$

- **프로젝트 적용**: Greedy 초기해 $O(n^2)$, ALNS 내부 루프 $O(\text{max\_iter} \times n^2)$, 거리 행렬 구축 $O(n^2)$. Tier별 알고리즘 선택 기준.

---

#### Polynomial time

- **한국어**: 다항 시간
- **정의**: 입력 크기 $n$의 다항식에 비례하는 시간 내에 풀 수 있는 알고리즘의 특성. $O(n^k)$ 형태($k$: 상수).
- **프로젝트 적용**: LP 완화는 다항 시간 (Interior Point $O(n^{3.5})$). MILP는 최악의 경우 지수 시간이지만 B&B로 실용적 풀이 가능. Gap 허용 시 조기 종료로 시간 제한 내 결과 획득.

---

## 5. 해양·항구 전문용어 (Maritime)

### 요약 테이블

| 용어 | 한국어 | 단위/범주 |
|------|--------|----------|
| Berth | 선석 | 물리적 위치 |
| Tugboat / Tug | 예인선 | 차량(vehicle) 역할 |
| Bollard pull | 계류력 | tf (ton-force) |
| Draft | 흘수 | m |
| ETA / ATA / ETD / ATD | 예상/실제 도착/출항 시각 | datetime |
| AIS | 자동 선박 식별 시스템 | 데이터 소스 |
| Slow steaming | 감속 운항 | 연료 절감 전략 |
| JIT arrival | 적시 도착 | 운항 전략 |
| Port congestion | 항만 혼잡 | 운영 상태 |

---

### 세부 설명

#### Berth (선석)

- **한국어**: 선석
- **정의**: 선박이 접안하여 화물 하역·적재 작업을 수행하는 부두 내 지정 구역. 이산 BAP에서 이산 위치로, 연속 BAP에서 $[0, L]$ 구간 내 연속 위치로 모델링.
- **프로젝트 적용**: `libs/stochastic/simulation.py`에서 `n_berths=3`. `TimeWindowSpec.berth_id`로 각 서비스 요청의 목적 선석을 지정. `berth_locations: dict[str, tuple[float, float]]`로 GPS 좌표 저장.

---

#### Tugboat / Tug (예인선)

- **한국어**: 예인선
- **정의**: 대형 선박의 접·이안을 보조하는 소형 고출력 선박. 자체 추진력은 낮지만 강한 견인력(bollard pull)을 제공. 항구 최적화에서 "차량(vehicle)"에 해당.
- **프로젝트 적용**: `tug_fleet: list[str]`으로 관리. TSP-T에서 $k \in K$로 인덱싱. Tier별 예인선 수: Tier 1 (소수), Tier 2 (m=5~20), Tier 3 (n>50 선박 대응).

---

#### Bollard pull (계류력)

- **한국어**: 볼라드 풀, 계류력
- **정의**: 예인선이 정지 상태에서 발휘하는 최대 견인력. 단위는 tf(ton-force). 예인선 선택 시 선박 배수량(displacement)에 비례하는 bollard pull이 필요.
- **프로젝트 적용**: CVRP 맥락에서 용량 제약 $Q$의 물리적 해석. 특정 선박은 최소 bollard pull 이상의 예인선만 서비스 가능한 이종(heterogeneous) fleet 제약으로 모델링 가능.

---

#### Draft (흘수)

- **한국어**: 흘수
- **정의**: 선박 선체가 수면 아래 잠기는 깊이(단위: m). 선박 만재 흘수가 선석 수심 이하여야 접안 가능. 조석(tidal window)에 따라 허용 흘수가 변동.
- **프로젝트 적용**: BAP에서 선박-선석 적합성 제약의 물리적 근거. 복수의 시간창(multiple time windows, VRPMTW)은 조석 변화에 따른 접안 가능 구간을 모델링.

---

#### ETA / ATA / ETD / ATD

- **한국어**: 예상 도착 시각 / 실제 도착 시각 / 예상 출항 시각 / 실제 출항 시각
- **정의**:
  - **ETA** (Estimated Time of Arrival): 선박이 선석 또는 항구에 도착할 것으로 예상되는 시각.
  - **ATA** (Actual Time of Arrival): 실제로 도착한 시각.
  - **ETD** (Estimated Time of Departure): 예상 출항 시각.
  - **ATD** (Actual Time of Departure): 실제 출항 시각.
- **프로젝트 적용**: ETA-ATA 편차가 날씨 지연 $\delta \sim \mathcal{N}(0, \sigma=0.85\text{h})$으로 모델링됨. `earliest_start = eta_j`. `docs/research/eta_distributions.md` 참조.

---

#### AIS — Automatic Identification System

- **한국어**: 자동 선박 식별 시스템
- **정의**: 선박이 실시간으로 위치, 속도, 침로, 선박 정보를 브로드캐스트하는 해상 무선 통신 시스템(IMO 의무 탑재). AIS 데이터로 ETA를 실시간 갱신.
- **프로젝트 적용**: 실제 ETA 예측 및 ATA-ETA 편차 분포 추정의 데이터 소스. `docs/research/multiobjective_ais.md`의 AIS 기반 속도 최적화 연구 참조.

---

#### Slow steaming (감속 운항)

- **한국어**: 감속 운항
- **정의**: 선박이 설계 속도보다 낮은 속도로 운항하여 연료를 절감하는 전략. 연료 소비가 속도의 세제곱에 비례하므로 속도를 10% 낮추면 연료는 약 27% 감소.
- **수식**:

$$F(v) = \alpha v^3, \quad \frac{F(0.9v)}{F(v)} = 0.9^3 \approx 0.73$$

- **프로젝트 적용**: `libs/fuel/eco_speed.py`의 `EcoSpeedOptimizer`. `v_eco=10.0 kn`(설계 속도 대비 감속)으로 기본 설정. ALNS에서 `gamma=2.5`로 일반화 지수 적용.

---

#### Just-in-time arrival (JIT)

- **한국어**: 적시 도착
- **정의**: 선박이 불필요한 대기 없이 선석이 준비되는 시점에 맞춰 도착하도록 속도를 조절하는 운항 전략. 선박 대기 비용과 연료 소비를 동시에 절감.
- **프로젝트 적용**: eco-speed 최적화의 목표. 선박이 `latest_start`보다 늦지 않고, 대기 없이 바로 서비스받을 수 있도록 속도 $v^* = d / T_{\max}$로 운항.

---

#### Port congestion (항만 혼잡)

- **한국어**: 항만 혼잡
- **정의**: 선박 도착이 처리 용량을 초과하여 선박들이 안벽 또는 묘박지(anchorage)에서 대기하는 상태. 체선료(demurrage) 발생 원인.
- **프로젝트 적용**: `libs/stochastic/simulation.py`의 `berth_free_time` 배열이 선석 가용성을 추적. 혼잡 시 `start = max(actual_arrival, berth_free_time[berth_id])`로 대기 시간 계산.

---

## 6. 솔버 (Solvers)

### 요약 테이블

| 솔버 | 유형 | 라이선스 | 프로젝트 적용 |
|------|------|----------|--------------|
| HiGHS | LP/MIP | 오픈소스 (MIT) | 주 솔버 (Tier 1·3) |
| Gurobi | LP/MIP/QP | 상용 | 비교 참조 |
| CPLEX | LP/MIP/QP | 상용 | 비교 참조 |
| Pyomo | 모델링 언어 | 오픈소스 | 모델 정식화 인터페이스 |
| CVXPY | 볼록 최적화 DSL | 오픈소스 | 볼록 하위 문제 |
| OR-Tools | 조합 최적화 | 오픈소스 (Apache) | 참조 |
| ECOS | 2차 원뿔 계획 | 오픈소스 | CVXPY 백엔드 |
| SCS | 1차 원뿔 계획 | 오픈소스 | CVXPY 백엔드 |
| CLARABEL | 내점법 | 오픈소스 | CVXPY 기본 백엔드 |

---

### 세부 설명

#### HiGHS

- **한국어**: HiGHS (High-performance Simplex)
- **정의**: LP, MIP, QP를 지원하는 고성능 오픈소스 솔버. Huangfu & Hall (2018)이 개발. Revised Simplex, IPM, B&B를 구현.
- **프로젝트 적용**: 주 솔버. `libs/scheduling/tsp_t_milp.py`와 `libs/scheduling/benders.py`에서 Pyomo를 통해 사용. 설치: `uv add highspy>=1.7`. `mip_rel_gap=0.05`, `time_limit=60`으로 설정.

---

#### Gurobi

- **한국어**: 구로비
- **정의**: LP, MILP, QP, SOCP 등을 지원하는 업계 표준 상용 솔버. 학술 라이선스 무료 제공. 대규모 문제에서 HiGHS 대비 빠른 경우가 많음.
- **프로젝트 적용**: Pyomo에서 `pyo.SolverFactory("gurobi")`로 교체 가능. 성능 벤치마크 비교 참조.

---

#### CPLEX

- **한국어**: IBM CPLEX
- **정의**: IBM이 개발한 LP/MILP/QP 상용 솔버. Concert Technology API와 Python API(DOcplex)를 제공. 대규모 산업 문제에 널리 사용.
- **프로젝트 적용**: HiGHS·Gurobi의 비교 대상. 학술 라이선스로 성능 검증 가능.

---

#### Pyomo

- **한국어**: 파이오모
- **정의**: Python 기반 오픈소스 최적화 모델링 언어(Algebraic Modeling Language). 문제를 수학적 추상화로 정의하고 HiGHS, Gurobi, CPLEX 등 다양한 솔버에 전달.
- **프로젝트 적용**: `libs/scheduling/tsp_t_milp.py`와 `libs/scheduling/benders.py`에서 `pyomo.environ`으로 모델 구축. `pyo.ConcreteModel`, `pyo.Var`, `pyo.Constraint`, `pyo.Objective` 사용.

```python
import pyomo.environ as pyo
m = pyo.ConcreteModel()
m.x = pyo.Var(domain=pyo.Binary)
```

---

#### CVXPY

- **한국어**: CVXPY
- **정의**: Python 기반 볼록 최적화 모델링 DSL(Domain-Specific Language). 볼록 문제를 자동으로 표준 형식으로 변환하고 적합한 솔버(ECOS, SCS, CLARABEL, Gurobi 등)를 선택.
- **프로젝트 적용**: 볼록 하위 문제(속도 최적화 QP, CVaR 계산) 구현에 적합. `requirements-research.txt` 참조.

---

#### OR-Tools

- **한국어**: OR-Tools (Google Operations Research Tools)
- **정의**: Google이 개발한 오픈소스 조합 최적화 라이브러리. VRP, CP-SAT (constraint programming), 선형 계획 등 다양한 솔버를 포함. Python API 제공.
- **프로젝트 적용**: VRP 빠른 프로토타이핑 참조 도구. Pyomo+HiGHS 기반 주 구현과 병렬 비교 가능.

---

#### ECOS / SCS / CLARABEL

- **한국어**: ECOS / SCS / CLARABEL
- **정의**:
  - **ECOS**: 2차 원뿔 계획(SOCP) 전용 내점법 솔버. 소규모 문제에서 빠름.
  - **SCS**: 1차 원뿔 계획 솔버. 대규모 문제에서 메모리 효율적. Splitting Conic Solver.
  - **CLARABEL**: Rust 기반 내점법 범용 원뿔 계획 솔버. CVXPY 0.8+ 기본 백엔드.
- **프로젝트 적용**: CVXPY 사용 시 자동 선택되는 백엔드 솔버. 볼록 속도 최적화 하위 문제에 적용 가능.

---

## 참고 문헌

| # | 저자 | 연도 | 주제 |
|---|------|------|------|
| 1 | Solomon | 1987 | VRPTW 벤치마크 및 삽입 휴리스틱 |
| 2 | Lim | 1998 | BAP NP-hardness |
| 3 | Ropke & Pisinger | 2006 | ALNS for VRPTW/PDPTW |
| 4 | Rodrigues et al. | 2021 | Tugboat Scheduling (EJOR) |
| 5 | Viana et al. | 2020 | 브라질 항구 예인선 스케줄 (COR) |
| 6 | Psaraftis & Kontovas | 2013 | 선박 속도·연료 모델 |
| 7 | Bierwirth & Meisel | 2010 | BAP 서베이 |
| 8 | Zheng, Chu & Xu | 2015 | Benders for berth + tug (COR) |
| 9 | Zhen, Lee & Chew | 2011 | 2-stage SP for BAP (EJOR) |
| 10 | Nadales et al. | 2023 | Wasserstein DRO, vessel control |

상세 메타정보: `docs/research/papers/references.md`
수학적 formulation 상세: `docs/research/mathematical_formulation.md`
