# 항구 예인선·대형선박 스케줄·경로·연료 최적화: 수학적 Formulation 정리

> **작성 기준**: 2026-03-19  
> **범위**: Tugboat Scheduling Problem, VRPTW, Berth Allocation Problem, Harbor Traffic Management, Multi-objective Maritime Optimization  
> **표기**: GitHub Markdown 호환 LaTeX (달러 기호 블록)

---

## 목차

1. [문제 분류 및 계층 구조](#1-문제-분류-및-계층-구조)
2. [Tugboat Scheduling Problem (TSP-T)](#2-tugboat-scheduling-problem-tsp-t)
3. [Vehicle Routing Problem with Time Windows (VRPTW)](#3-vehicle-routing-problem-with-time-windows-vrptw)
4. [Berth Allocation Problem (BAP)](#4-berth-allocation-problem-bap)
5. [Harbor Vessel Traffic Management (HVTM)](#5-harbor-vessel-traffic-management-hvtm)
6. [연료 소비 모델 (Fuel Consumption Model)](#6-연료-소비-모델-fuel-consumption-model)
7. [Multi-objective Maritime Optimization](#7-multi-objective-maritime-optimization)
8. [통합 모델: Tugboat + Vessel 공동 최적화](#8-통합-모델-tugboat--vessel-공동-최적화)
9. [알고리즘 복잡도 및 NP-hardness 분류](#9-알고리즘-복잡도-및-np-hardness-분류)
10. [주요 참고 문헌](#10-주요-참고-문헌)

---

## 1. 문제 분류 및 계층 구조

항구 운영 최적화는 계층적 의사결정 구조를 가진다.

```
전략 계층 (Strategic)
  └── 항구 인프라 계획, 예인선 fleet 규모 결정

전술 계층 (Tactical)
  ├── Berth Allocation Problem (BAP)       — 어느 선박이 어느 선석에, 언제
  ├── Quay Crane Assignment Problem (QCAP) — 크레인 배정
  └── Tugboat Fleet Management            — 예인선 할당·경로

운영 계층 (Operational)
  ├── Tugboat Scheduling Problem (TSP-T)  — 실시간 예인 스케줄
  ├── VRPTW (Tugboat routing)             — 다중 예인선 경로
  └── Harbor Vessel Traffic Management   — 입출항 교통 흐름
```

**문제 간 의존성**:
- BAP → TSP-T: 선박 접안 시간창(time window)이 예인 수요를 결정
- TSP-T → VRPTW: 단일 예인선 스케줄 → 다중 예인선 라우팅으로 확장
- HVTM → BAP: 항로 혼잡도가 선박 도착 시간 불확실성에 영향

---

## 2. Tugboat Scheduling Problem (TSP-T)

### 2.1 문제 정의

**TSP-T**는 항구 내 복수의 예인선(tugboat)을 복수의 선박 서비스 요청에 할당하고, 각 예인선의 이동 순서·시간을 결정하는 조합 최적화 문제이다.

**참조 연구**: Rodrigues et al. (2021), Hinnenthal & Clauss (2010), Viana et al. (2020)

### 2.2 인덱스 및 집합

| 기호 | 정의 |
|------|------|
| $T = \{1, \ldots, m\}$ | 예인선(tugboat) 집합, $m$: 예인선 수 |
| $J = \{1, \ldots, n\}$ | 서비스 요청(job) 집합, $n$: 요청 수 |
| $J^+ = J \cup \{0, n+1\}$ | 출발·도착 depot(0, $n+1$)을 포함한 확장 집합 |
| $V = J^+$ | 노드 집합 (각 요청 = 노드) |
| $A$ | 호(arc) 집합: $(i, j) \in J^+ \times J^+$, $i \neq j$ |

### 2.3 파라미터

| 기호 | 정의 |
|------|------|
| $e_j, l_j$ | 요청 $j$의 earliest/latest start time (time window) |
| $p_j$ | 요청 $j$의 서비스 소요 시간(processing time) |
| $t_{ij}$ | 노드 $i$에서 $j$로의 예인선 이동 시간 |
| $d_{ij}$ | 노드 $i$에서 $j$로의 이동 거리 |
| $r_j$ | 요청 $j$에 필요한 예인선 수(tugboat demand) |
| $c_{ij}^k$ | 예인선 $k$가 $i \to j$ 이동 시 발생 비용 |
| $w_j$ | 요청 $j$의 대기 비용(penalty per unit time) |
| $M$ | 충분히 큰 상수 (Big-M) |

### 2.4 Decision Variables

$$x_{ij}^k = \begin{cases} 1 & \text{예인선 } k \text{가 요청 } i \text{ 직후 요청 } j \text{를 수행} \\ 0 & \text{otherwise} \end{cases}$$

$$s_j^k = \text{예인선 } k \text{가 요청 } j \text{를 시작하는 시각}$$

$$w_j^k = \max(0,\; e_j - (s_{i}^k + p_i + t_{ij})) \quad \text{(대기 시간)}$$

### 2.5 목적함수

**총 비용 최소화** (이동 비용 + 대기 페널티):

$$\min \quad Z = \sum_{k \in T} \sum_{(i,j) \in A} c_{ij}^k x_{ij}^k + \sum_{k \in T} \sum_{j \in J} w_j \cdot \max(0,\; s_j^k - l_j^{\text{req}})$$

또는 **완료 시간 최소화** (makespan):

$$\min \quad C_{\max} = \max_{k \in T} \left( s_{n+1}^k \right)$$

### 2.6 제약조건

**[C1] 각 요청은 정확히 한 예인선이 수행**:

$$\sum_{k \in T} \sum_{j \in J^+,\, j \neq i} x_{ij}^k = 1 \qquad \forall i \in J$$

**[C2] 흐름 보존(flow conservation)**:

$$\sum_{j \in J^+} x_{ij}^k = \sum_{j \in J^+} x_{ji}^k \qquad \forall i \in J,\; k \in T$$

**[C3] 예인선은 depot에서 출발하고 depot으로 귀환**:

$$\sum_{j \in J} x_{0j}^k = 1, \quad \sum_{i \in J} x_{i,n+1}^k = 1 \qquad \forall k \in T$$

**[C4] Time window 준수**:

$$e_j \leq s_j^k \leq l_j \qquad \forall j \in J,\; k \in T$$

**[C5] 시간 연속성(subtour elimination + time propagation)**:

$$s_j^k \geq s_i^k + p_i + t_{ij} - M(1 - x_{ij}^k) \qquad \forall (i,j) \in A,\; k \in T$$

**[C6] 이진 및 비음수 조건**:

$$x_{ij}^k \in \{0, 1\} \qquad \forall (i,j) \in A,\; k \in T$$
$$s_j^k \geq 0 \qquad \forall j \in J^+,\; k \in T$$

**[C7] 요청별 최소 예인선 수 보장** (일부 모델):

$$\sum_{k \in T} \sum_{j \in J^+} x_{ij}^k \geq r_i \qquad \forall i \in J$$

### 2.7 특수 변형: Time-Indexed Formulation

대안적 정식화로 시간 인덱스 변수를 사용한다:

$$y_{jt}^k = \begin{cases} 1 & \text{예인선 } k \text{가 시각 } t \text{에 요청 } j \text{를 시작} \\ 0 & \text{otherwise} \end{cases}$$

$$\min \sum_{k \in T} \sum_{j \in J} \sum_{t=e_j}^{l_j} c_{jt}^k \cdot y_{jt}^k$$

**[C8] 각 예인선은 한 번에 하나의 작업만 수행**:

$$\sum_{j \in J} \sum_{\tau = \max(0, t-p_j+1)}^{t} y_{j\tau}^k \leq 1 \qquad \forall t,\; k \in T$$

---

## 3. Vehicle Routing Problem with Time Windows (VRPTW)

### 3.1 항구 VRPTW 컨텍스트

VRPTW는 TSP-T의 일반화 프레임워크이다. 예인선을 차량(vehicle)으로, 서비스 요청을 고객(customer)으로 매핑한다. 항구 맥락에서는 용량 제약이 연료 탱크 또는 예인력(bollard pull)으로 해석된다.

**참조 연구**: Solomon (1987), Desrochers et al. (1992), Cordeau et al. (2001), Baldacci et al. (2012)

### 3.2 집합 및 파라미터

| 기호 | 정의 |
|------|------|
| $K$ | 예인선(차량) 집합 |
| $N = \{0, 1, \ldots, n, n+1\}$ | 노드: 0=출발 depot, $n+1$=도착 depot, $1..n$=요청 |
| $[a_i, b_i]$ | 노드 $i$의 time window |
| $s_i$ | 노드 $i$에서 서비스 시간 |
| $q_i$ | 노드 $i$의 수요(연료 소비량 또는 bollard pull 요구량) |
| $Q$ | 예인선 용량(fuel capacity 또는 max bollard pull) |
| $c_{ij}$ | 호 $(i,j)$ 이동 비용 |
| $t_{ij}$ | 호 $(i,j)$ 이동 시간 |

### 3.3 Decision Variables

$$x_{ijk} = \begin{cases} 1 & \text{차량 } k \text{가 } i \text{에서 } j \text{로 직행} \\ 0 & \text{otherwise} \end{cases}$$

$$T_i^k = \text{차량 } k \text{가 노드 } i \text{에 도착하는 시각}$$

### 3.4 목적함수

$$\min \quad \sum_{k \in K} \sum_{i \in N} \sum_{j \in N} c_{ij} x_{ijk}$$

### 3.5 제약조건

**[V1] 각 고객은 정확히 한 번 방문**:

$$\sum_{k \in K} \sum_{j \in N \setminus \{i\}} x_{ijk} = 1 \qquad \forall i \in \{1,\ldots,n\}$$

**[V2] 차량 출발/도착**:

$$\sum_{j \in N \setminus \{0\}} x_{0jk} = 1, \quad \sum_{i \in N \setminus \{n+1\}} x_{i,n+1,k} = 1 \qquad \forall k \in K$$

**[V3] 흐름 보존**:

$$\sum_{i \in N} x_{ijk} = \sum_{i \in N} x_{jik} \qquad \forall j \in \{1,\ldots,n\},\; k \in K$$

**[V4] 용량 제약**:

$$\sum_{i \in N} \sum_{j \in N} q_i x_{ijk} \leq Q \qquad \forall k \in K$$

**[V5] Time window**:

$$a_i \leq T_i^k \leq b_i \qquad \forall i \in N,\; k \in K$$

**[V6] 시간 연속성**:

$$T_i^k + s_i + t_{ij} - M(1 - x_{ijk}) \leq T_j^k \qquad \forall i,j \in N,\; k \in K$$

**[V7] 이진 및 비음수**:

$$x_{ijk} \in \{0,1\}, \quad T_i^k \geq 0$$

### 3.6 VRPTW 확장: 항구 특화 변형

#### 3.6.1 Heterogeneous Fleet (HFVRPTW)

예인선마다 bollard pull, 속도, 연료 소비율이 다른 경우:

$$c_{ijk} = \alpha_k \cdot d_{ij} \cdot f(v_k) \qquad \text{(예인선 } k \text{의 비용)}$$

여기서 $\alpha_k$는 예인선 $k$의 단위 거리당 비용 계수, $f(v_k)$는 속도 함수.

#### 3.6.2 Multiple Time Windows (VRPMTW)

선박 입출항에는 조석(tidal window)이 복수로 존재:

$$T_i^k \in \bigcup_{r=1}^{R_i} [a_i^r, b_i^r]$$

---

## 4. Berth Allocation Problem (BAP)

### 4.1 문제 정의

BAP는 $n$척의 선박을 항구의 연속 또는 이산 선석(berth)에 할당하여 총 대기시간·체선료를 최소화하는 문제이다. 예인선 스케줄의 상위 의사결정으로, 선석 배정 결과가 예인 수요의 시간창을 결정한다.

**참조 연구**: Lim (1998), Imai et al. (2001), Cordeau et al. (2005), Bierwirth & Meisel (2010, 2015)

### 4.2 집합 및 파라미터

| 기호 | 정의 |
|------|------|
| $V = \{1,\ldots,n\}$ | 선박 집합 |
| $B = \{1,\ldots,m\}$ | 선석 집합 |
| $H$ | 계획 기간(horizon) |
| $a_i$ | 선박 $i$의 도착 시각 |
| $p_i$ | 선박 $i$의 처리(접안) 시간 |
| $l_i$ | 선박 $i$의 선체 길이 |
| $L_b$ | 선석 $b$의 길이 |
| $\omega_i$ | 선박 $i$의 중요도 가중치(tonnage, priority) |

### 4.3 Decision Variables (이산 BAP)

$$x_{ibt} = \begin{cases} 1 & \text{선박 } i \text{가 선석 } b \text{에서 시각 } t \text{에 접안 시작} \\ 0 & \text{otherwise} \end{cases}$$

### 4.4 목적함수

**총 가중 완료 시간 최소화**:

$$\min \quad \sum_{i \in V} \omega_i \left( \sum_{b \in B} \sum_{t} (t + p_i) x_{ibt} - a_i \right)$$

이를 분해하면:

$$\min \quad \sum_{i \in V} \omega_i \left( C_i - a_i \right)$$

여기서 $C_i = \sum_{b,t} (t + p_i) x_{ibt}$는 선박 $i$의 출항 시각.

### 4.5 제약조건

**[B1] 각 선박은 정확히 한 번 배정**:

$$\sum_{b \in B} \sum_{t=a_i}^{H} x_{ibt} = 1 \qquad \forall i \in V$$

**[B2] 선석 길이 제약**:

$$\sum_{i \in V} l_i \cdot x_{ibt} \leq L_b \qquad \forall b \in B,\; t \in [0,H]$$

**[B3] 동일 선석 내 중복 방지** (이진 충돌 제약):

$$x_{ibt} + x_{jbt'} \leq 1 \qquad \forall i \neq j,\; b,\; [t, t+p_i) \cap [t', t'+p_j) \neq \emptyset$$

**[B4] 접안 시작은 도착 이후**:

$$\sum_{b,t} t \cdot x_{ibt} \geq a_i \qquad \forall i \in V$$

**[B5] 이진 조건**:

$$x_{ibt} \in \{0,1\}$$

### 4.6 연속 BAP (Continuous BAP)

선박의 위치를 연속 변수로 모델링:

$$b_i \in [0, L - l_i] \quad \text{(선석 상 연속 위치)}$$
$$t_i^s \geq a_i \quad \text{(접안 시작 시각)}$$

**비중복 제약** (no-overlap in space-time):

두 선박 $i, j$에 대해 다음 중 하나 이상이 성립:

$$b_i + l_i \leq b_j \quad \text{(공간)} \quad \text{OR} \quad t_i^s + p_i \leq t_j^s \quad \text{(시간)}$$

선형화를 위해 이진 변수 $\delta_{ij}^1, \delta_{ij}^2 \in \{0,1\}$ 도입:

$$b_i + l_i \leq b_j + M(1 - \delta_{ij}^1)$$
$$t_i^s + p_i \leq t_j^s + M(1 - \delta_{ij}^2)$$
$$\delta_{ij}^1 + \delta_{ij}^2 \geq 1 \qquad \forall i < j$$

---

## 5. Harbor Vessel Traffic Management (HVTM)

### 5.1 문제 정의

HVTM은 항구 내 항로(channel), 교차로(junction), 대기 구역(anchorage)에서 선박들의 이동 순서와 속도를 결정하여 충돌 방지와 처리량 최대화를 동시에 달성하는 문제이다.

**참조 연구**: Golias et al. (2009), Zhen et al. (2011), Du et al. (2015), Venturini et al. (2017)

### 5.2 집합 및 파라미터

| 기호 | 정의 |
|------|------|
| $S = \{1,\ldots,n\}$ | 선박 집합 |
| $R = \{1,\ldots,r\}$ | 항로 구간(segment) 집합 |
| $P_s$ | 선박 $s$의 이동 경로(구간 순서열) |
| $v_s^{\min}, v_s^{\max}$ | 선박 $s$의 최소/최대 속도 |
| $\ell_r$ | 구간 $r$의 길이 |
| $\text{cap}_r$ | 구간 $r$의 최대 동시 통과 선박 수 |
| $\text{gap}$ | 선박 간 최소 안전 간격(시간) |

### 5.3 Decision Variables

$$v_s^r = \text{선박 } s \text{의 구간 } r \text{에서의 속도}$$
$$\tau_s^r = \text{선박 } s \text{가 구간 } r \text{에 진입하는 시각}$$
$$\sigma_{ij}^r = \begin{cases} 1 & \text{구간 } r \text{에서 선박 } i \text{가 선박 } j \text{보다 먼저 진입} \\ 0 & \text{otherwise} \end{cases}$$

### 5.4 목적함수

**총 지연 최소화**:

$$\min \quad \sum_{s \in S} \left( \tau_s^{\text{arrive}} - \hat{\tau}_s^{\text{arrive}} \right)$$

**또는 혼합 목적**: 지연 + 연료 (속도 제어를 통한 연료 절감):

$$\min \quad \alpha \sum_{s \in S} D_s + \beta \sum_{s \in S} \sum_{r \in P_s} F(v_s^r, \ell_r)$$

여기서 $D_s$는 선박 $s$의 지연, $F(\cdot)$는 연료 소비 함수, $\alpha, \beta$는 가중치.

### 5.5 제약조건

**[H1] 속도 한계**:

$$v_s^{\min} \leq v_s^r \leq v_s^{\max} \qquad \forall s \in S,\; r \in P_s$$

**[H2] 구간 통과 시간**:

$$\tau_s^{r+1} = \tau_s^r + \frac{\ell_r}{v_s^r} \qquad \forall s,\; r \in P_s$$

**[H3] 안전 간격 (선행 선박 기준)**:

$$\tau_j^r \geq \tau_i^r + \text{gap} - M(1 - \sigma_{ij}^r) \qquad \forall i \neq j,\; r$$

**[H4] 구간 용량**:

$$\sum_{s \in S} \mathbf{1}\left[\tau_s^r \leq t \leq \tau_s^r + \frac{\ell_r}{v_s^r}\right] \leq \text{cap}_r \qquad \forall r,\; t$$

**[H5] 도착 시간 준수**:

$$\tau_s^{\text{arrive}} \leq \hat{\tau}_s^{\text{arrive}} + D_s^{\max} \qquad \forall s$$

---

## 6. 연료 소비 모델 (Fuel Consumption Model)

### 6.1 기본 물리 관계: 속도 세제곱 법칙

선박/예인선의 연료 소비는 속도의 세제곱에 비례한다. 이는 유체역학적 저항(resistance)이 $v^2$에 비례하고, 거리당 소요 동력이 $v^3$에 비례하는 데서 유도된다.

$$\boxed{F(v) = \alpha \cdot v^3 \cdot \frac{d}{v} = \alpha \cdot v^2 \cdot d}$$

단, 시간 단위 소비로 표현하면:

$$\dot{F}(v) = \alpha \cdot v^3 \qquad \text{[fuel/time]}$$

거리 $d$를 이동할 때 총 소비량:

$$F(v, d) = \dot{F}(v) \cdot \frac{d}{v} = \alpha \cdot v^2 \cdot d \qquad \text{[fuel]}$$

**참조**: Psaraftis & Kontovas (2013) — "Speed models for energy-efficient maritime transportation", Transportation Research Part C.

### 6.2 일반화 연료 소비 모델

실제 선박에서는 지수가 2~3 사이의 범위를 가진다:

$$F(v, d) = \alpha \cdot v^{\gamma} \cdot \frac{d}{v} = \alpha \cdot v^{\gamma - 1} \cdot d, \quad \gamma \in [2, 3]$$

선박 엔진 부하율(MCR: Maximum Continuous Rating) 기반 모델:

$$F = c_0 + c_1 \cdot P + c_2 \cdot P^2 + c_3 \cdot P^3$$

여기서 $P \propto R(v) \cdot v$이고, 선체 저항 $R(v) \approx k \cdot v^2$이므로 $P \propto v^3$.

### 6.3 Eco-speed 최적화

단일 예인선의 구간별 속도 최적화:

$$\min_{v_1, \ldots, v_K} \sum_{k=1}^{K} \alpha \cdot v_k^2 \cdot d_k$$

$$\text{s.t.} \quad \sum_{k=1}^{K} \frac{d_k}{v_k} \leq T^{\max}, \quad v^{\min} \leq v_k \leq v^{\max}$$

**해석적 해**: KKT 조건으로부터, 시간 제약이 binding일 때 최적 속도는 구간별 일정(constant speed):

$$v_k^* = \frac{\sum_k d_k}{T^{\max}} \qquad \text{(equal speed across segments)}$$

### 6.4 연료 소비 최소화와 시간 최소화의 트레이드오프

두 목표 간 Pareto 프론티어:

$$\min \quad \{F(v), T(v)\} = \left\{ \alpha v^2 d, \; \frac{d}{v} \right\}$$

$\varepsilon$-제약법으로 단일화:

$$\min \quad \alpha v^2 d \quad \text{s.t.} \quad \frac{d}{v} \leq T_{\max}$$

최적해: $v^* = d / T_{\max}$ (가능한 한 느리게 운항).

### 6.5 항구 내 예인선 연료 모델 특수성

예인선은 일반 선박과 달리 다음 특성을 가진다:

1. **Bollard pull 모드**: 선박을 견인할 때 속도는 매우 낮으나 출력(power)은 최대
2. **Transit 모드**: 공선(空船) 이동 시 연료는 $v^3$에 비례
3. **대기 모드(idle)**: 엔진 공회전, 기저 연료 소비 $F_{\text{idle}}$

통합 연료 모델:

$$F_{\text{total}}^k = \sum_{(i,j): x_{ij}^k=1} \left[ \alpha_{\text{transit}} \cdot (v_{ij}^k)^2 \cdot d_{ij} \right] + \sum_{j \in J} \left[ \alpha_{\text{tow}} \cdot P_j \cdot p_j \right] + F_{\text{idle}} \cdot T_{\text{idle}}^k$$

---

## 7. Multi-objective Maritime Optimization

### 7.1 일반 다목적 정식화

항구 최적화는 본질적으로 다목적이다. 공식적 벡터 최소화:

$$\min_{\mathbf{x}} \quad \mathbf{f}(\mathbf{x}) = \left( f_1(\mathbf{x}),\; f_2(\mathbf{x}),\; f_3(\mathbf{x}),\; f_4(\mathbf{x}) \right)$$

$$\text{s.t.} \quad \mathbf{x} \in \mathcal{X}$$

| 목적함수 | 의미 |
|----------|------|
| $f_1(\mathbf{x}) = \sum_{k,i,j} c_{ij}^k x_{ij}^k$ | 총 운항 비용 최소화 |
| $f_2(\mathbf{x}) = \sum_k \sum_{(i,j)} F(v_{ij}^k, d_{ij}) x_{ij}^k$ | 총 연료 소비 최소화 |
| $f_3(\mathbf{x}) = \sum_i (s_i - a_i)$ | 총 선박 대기 시간 최소화 |
| $f_4(\mathbf{x}) = 1 - \frac{\text{실제 서비스 수}}{\|J\|}$ | 예인선 비활용율 최소화 (활용률 최대화) |

### 7.2 가중합법 (Weighted Sum)

$$\min \quad \sum_{q=1}^{4} \lambda_q f_q(\mathbf{x}), \quad \lambda_q \geq 0,\; \sum_q \lambda_q = 1$$

**단점**: 비볼록 Pareto 프론티어 구간을 탐색 불가.

### 7.3 $\varepsilon$-제약법

$$\min \quad f_1(\mathbf{x})$$
$$\text{s.t.} \quad f_q(\mathbf{x}) \leq \varepsilon_q \quad \forall q \in \{2,3,4\}$$
$$\quad \mathbf{x} \in \mathcal{X}$$

$\varepsilon_q$를 체계적으로 변화시켜 Pareto 프론티어 구성.

### 7.4 Pareto 최적성

해 $\mathbf{x}^* \in \mathcal{X}$가 Pareto 최적이면:

$$\nexists\; \mathbf{x} \in \mathcal{X} \text{ s.t. } f_q(\mathbf{x}) \leq f_q(\mathbf{x}^*)\; \forall q \text{ and } f_q(\mathbf{x}) < f_q(\mathbf{x}^*) \text{ for some } q$$

### 7.5 주요 MCDM 접근법

| 방법 | 특징 | 항구 최적화 적용 |
|------|------|----------------|
| NSGA-II | 비지배 정렬 GA | 연료-시간 Pareto 탐색 |
| MOPSO | 다목적 입자군 최적화 | 연속 속도 최적화 |
| Lexicographic | 목적함수 우선순위 부여 | 안전 > 비용 > 연료 |
| Goal Programming | 목표값 이탈 최소화 | 실무 KPI 기반 |

---

## 8. 통합 모델: Tugboat + Vessel 공동 최적화

### 8.1 계층적 통합 정식화

BAP와 TSP-T를 동시에 결정하는 통합 문제. 상위(BAP) 결정이 하위(TSP-T)의 time window를 결정한다.

**참조 연구**: Frojan et al. (2015), Rodriguez et al. (2021)

### 8.2 통합 Decision Variables

| 변수 | 정의 |
|------|------|
| $x_{ij}^k \in \{0,1\}$ | 예인선 $k$가 $i$ 직후 $j$ 수행 |
| $z_{ib}^t \in \{0,1\}$ | 선박 $i$가 선석 $b$에서 시각 $t$에 접안 시작 |
| $v_{ij}^k \geq 0$ | 예인선 $k$의 $i \to j$ 구간 속도 |
| $s_j^k \geq 0$ | 예인선 $k$의 요청 $j$ 시작 시각 |

### 8.3 통합 목적함수

$$\min \quad \underbrace{\sum_{i \in V} \omega_i (C_i - a_i)}_{\text{선박 체선료 (BAP)}} + \underbrace{\sum_{k \in T} \sum_{(i,j)} c_{ij}^k x_{ij}^k}_{\text{예인 비용 (TSP-T)}} + \underbrace{\sum_{k \in T} \sum_{(i,j)} \alpha (v_{ij}^k)^2 d_{ij} x_{ij}^k}_{\text{연료비 (Fuel)}}$$

### 8.4 연결 제약: BAP-TSP-T 인터페이스

선박 $i$의 예인 수요는 접안 시작 전후 각각 발생한다:

- **입항 예인(inbound tug)**: 시각 $e_i^{\text{in}} = a_i$, $l_i^{\text{in}} = \sum_{b,t} t \cdot z_{ibt} + \Delta^{\text{in}}$
- **출항 예인(outbound tug)**: 시각 $e_i^{\text{out}} = \sum_{b,t}(t+p_i) \cdot z_{ibt}$, $l_i^{\text{out}} = e_i^{\text{out}} + \Delta^{\text{out}}$

**[I1] BAP 결정이 TSP-T time window를 결정**:

$$s_j^k \in [e_j(\mathbf{z}),\; l_j(\mathbf{z})] \qquad \forall j \in J$$

여기서 $e_j(\mathbf{z}), l_j(\mathbf{z})$는 $z_{ibt}$의 함수.

---

## 9. 알고리즘 복잡도 및 NP-hardness 분류

| 문제 | 복잡도 | 근거 |
|------|--------|------|
| TSP-T (단일 예인선) | NP-hard | TSP 환원 (Garey & Johnson 1979) |
| TSP-T (다중 예인선) | NP-hard | mTSP 환원 |
| VRPTW | NP-hard | VRP 환원 (Lenstra & Rinnooy Kan 1981) |
| BAP (이산) | NP-hard | 2D Bin Packing 환원 (Lim 1998) |
| BAP (연속) | NP-hard | |
| HVTM (속도 제어) | NP-hard (일반); P (단일 채널) | |
| 통합 BAP+TSP-T | NP-hard | 부분 문제가 NP-hard |

### 9.1 근사 알고리즘 및 메타휴리스틱

| 알고리즘 | 문제 적용 | 주요 논문 |
|----------|-----------|-----------|
| Column Generation | VRPTW, TSP-T | Desrosiers et al. (1995) |
| Branch-and-Price | VRPTW 정확해 | Barnhart et al. (1998) |
| Tabu Search | TSP-T, BAP | Cordeau et al. (2001) |
| ALNS (Adaptive LNS) | VRPTW | Ropke & Pisinger (2006) |
| Genetic Algorithm | BAP, TSP-T | Kim & Moon (2003) |
| Simulated Annealing | BAP | Hansen & Ravn (2002) |
| NSGA-II | Multi-objective | Deb et al. (2002) |

---

## 10. 주요 참고 문헌

상세 메타정보는 `/docs/research/papers/references.md` 참조.

| # | 저자 | 연도 | 주제 |
|---|------|------|------|
| 1 | Solomon | 1987 | VRPTW 벤치마크 및 삽입 휴리스틱 |
| 2 | Lim | 1998 | BAP NP-hardness, 그래프 이론 접근 |
| 3 | Imai et al. | 2001 | 이산 BAP, GA 적용 |
| 4 | Cordeau et al. | 2001 | VRP 통합 Tabu Search |
| 5 | Bierwirth & Meisel | 2010 | BAP 서베이 |
| 6 | Psaraftis & Kontovas | 2013 | 선박 속도 및 연료 모델 |
| 7 | Ropke & Pisinger | 2006 | ALNS for VRPTW |
| 8 | Rodrigues et al. | 2021 | Tugboat Scheduling, ILP |
| 9 | Venturini et al. | 2017 | Port vessel traffic speed optimization |
| 10 | Deb et al. | 2002 | NSGA-II |
| 11 | Frojan et al. | 2015 | BAP + crane integrated optimization |
| 12 | Du et al. | 2015 | Harbor traffic management model |
| 13 | Hinnenthal & Clauss | 2010 | Tugboat routing, MILP |
| 14 | Baldacci et al. | 2012 | VRPTW exact methods survey |
| 15 | Zhen et al. | 2011 | Vessel scheduling in liner shipping |

---

*이 문서는 항구 예인선 + 대형선박 통합 최적화의 수학적 기반을 정리한 것이다. 각 formulation은 실제 구현 시 문제 규모와 실시간 요구사항에 따라 relaxation 또는 decomposition이 필요하다.*

---

## 부록: 시각화 자료 (Figures)

시각화 파일은 `/docs/research/figures/` 디렉터리에 저장되어 있다.

| 파일명 | 내용 |
|--------|------|
| `fig1_problem_hierarchy.png` | 항구 최적화 문제 계층 구조 및 의존성 그래프 |
| `fig2_fuel_model.png` | 연료 소비 모델: (a) 연료율 vs 속도, (b) 구간 연료 vs 속도, (c) 연료-시간 Pareto 프론티어 |
| `fig3_schedule_complexity.png` | (a) TSP-T Gantt 스케줄 + time window 시각화, (b) 문제별 복잡도·알고리즘 비교표 |

### 그림 설명

**Fig 1** — 3개 계층(전략·전술·운영)과 교차 관심사(연료 모델, 다목적 최적화) 간의 의존성을 방향 그래프로 표현. 실선은 직접 결정 흐름, 점선은 크로스커팅 영향.

**Fig 2** — Psaraftis & Kontovas (2013) 기반. 지수 $\gamma \in \{2.0, 2.5, 3.0\}$에 따른 연료율 곡선과 Pareto 프론티어. 느린 속도(slow steaming)가 연료 절감에 미치는 효과를 확인할 수 있다.

**Fig 3** — 6개 요청·2개 예인선 가상 시나리오의 Gantt 차트. 청색/적색 바는 서비스 구간, 흐린 음영은 time window $[e_j, l_j]$, 역삼각형은 마감시한 $l_j$. 우측 표는 각 문제의 NP-hardness 증명 근거와 최적 알고리즘.
