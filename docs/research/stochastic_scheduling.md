# Stochastic Programming & Robust Optimization for Vessel Scheduling

## 2-Stage Stochastic Programming

### 1. A decision model for berth allocation under uncertainty
* **Authors:** Lu Zhen, Loo Hay Lee, Ek Peng Chew
* **Year:** 2011
* **Journal:** European Journal of Operational Research
* **Key Mathematical Formulation:**
  * **Decision Variables:** First stage: $x_{ij} \in \{0,1\}$ (assignment of vessel $i$ to berth $j$). Second stage: $\Delta_{i}$ (handling start time delay), $y_{i}$ (actual departure time).
  * **Objective:** Minimize planned berth allocation costs plus the expected penalty costs for delayed departures. 
    $$ \min \sum c_{ij}x_{ij} + \mathbb{E}_{\xi}[Q(x, \xi)] $$
  * **Constraints:** 
    * Assignment: $\sum_{j} x_{ij} = 1$
    * Spatial and temporal non-overlapping constraints for assigned vessels.
    * $Q(x, \xi)$ determines the recourse cost given the realized arrival time $\xi$.
* **Findings:** The two-stage stochastic model significantly reduces expected penalty costs compared to deterministic approaches by intelligently inserting buffer times into the schedule.

### 2. A two-stage stochastic programming model for a maritime inventory routing problem
* **Authors:** Agostinho Agra, Marielle Christiansen, Lars Magnus Hvattum, Filipe Rodrigues
* **Year:** 2015
* **Journal:** Transportation Science
* **Key Mathematical Formulation:**
  * **Decision Variables:** First stage: $x_{ijv} \in \{0,1\}$ (routing of vessel $v$ on arc $(i,j)$). Second stage: $q_{iv}$ (quantity loaded/unloaded), $s_{it}$ (inventory level).
  * **Objective:** Minimize routing costs and the expected penalty for inventory stockouts.
    $$ \min \sum c_{ijv}x_{ijv} + \mathbb{E}_{\xi}\left[ \sum p_{it} \max(0, S_{min} - s_{it}(\xi)) \right] $$
  * **Constraints:** 
    * Flow conservation: $\sum x_{ijv} - \sum x_{jiv} = 0$
    * Inventory balance equations and vessel capacity limits.
* **Findings:** Explicitly accounting for sailing time uncertainty via stochastic programming prevents costly stockouts and generates much more reliable vessel routes.

### 3. A two-stage stochastic programming model for seaport berth and channel planning with uncertainties
* **Authors:** B. Liu, Z. C. Lee, Y. Wang
* **Year:** 2022
* **Journal:** Transportation Research Part E
* **Key Mathematical Formulation:**
  * **Decision Variables:** $x_{ib} \in \{0,1\}$ (vessel $i$ to berth $b$), $y_{ic}$ (vessel $i$ entering channel $c$).
  * **Objective:** Minimize the expected total weighted completion time of all vessels.
    $$ \min \mathbb{E}_{\xi}\left[\sum w_i C_i(\xi)\right] $$
  * **Constraints:** 
    * Channel capacity and navigation safety limits.
    * Berth capacities.
    * Precedence constraints between channel transit and berth arrival.
* **Findings:** Jointly optimizing channel scheduling and berth allocation under a two-stage stochastic framework better manages arrival uncertainty, cutting down overall waiting times by up to 15%.

## Robust Optimization

### 1. A robust optimization approach to the integrated berth allocation and quay crane assignment problem
* **Authors:** X. T. Shang, J. X. Cao, J. Ren
* **Year:** 2016
* **Journal:** Transportation Research Part E
* **Key Mathematical Formulation:**
  * **Decision Variables:** $x_{ib} \in \{0,1\}$ (berth assignment), $q_{it}$ (number of cranes assigned to vessel $i$ at time $t$).
  * **Objective:** Minimax regret to minimize the worst-case schedule cost.
    $$ \min_{x, q} \max_{\xi \in U} C(x, q, \xi) $$
  * **Constraints:** 
    * Uncertainty set: $U = \left\{ \xi : \sum |\xi_i - \bar{\xi}_i| \le \Gamma \right\}$ (budget of uncertainty).
    * Total crane capacity: $\sum_i q_{it} \le Q_{max}$.
* **Findings:** The robust formulation ensures feasibility against any uncertainty realization within the bounded set $U$. It highlights a quantifiable "price of robustness" trade-off without assuming a specific probability distribution.

### 2. Robust Optimization for a Maritime Inventory Routing Problem
* **Authors:** Agostinho Agra, Marielle Christiansen, Lars Magnus Hvattum, Filipe Rodrigues
* **Year:** 2018
* **Journal:** Transportation Science
* **Key Mathematical Formulation:**
  * **Decision Variables:** $x_{ijv}$ (routing variables), $t_i$ (arrival times).
  * **Objective:** Minimize the worst-case travel and inventory penalty costs over an uncertainty set $D$ for sailing times.
    $$ \min_{x, t} \max_{d \in D} \text{Cost}(x, t, d) $$
  * **Constraints:** 
    * Adaptable robust constraints ensuring inventory remains within limits for all possible delay vectors $d \in D$.
* **Findings:** Using adaptable robust optimization produces solutions that are computationally tractable and highly protective against extreme weather delays, contrasting with the purely expected-value focus of stochastic programming.

## Chance-Constrained Programming

### 1. Overview and Mathematical Formulation
Chance-Constrained Programming (CCP) is a stochastic optimization technique where some constraints are required to be satisfied with a given probability. In maritime scheduling, it is used to ensure a target level of service reliability (e.g., on-time arrival) under uncertain travel or handling times.

*   **Individual Chance Constraint (ICC):**
    Each constraint $i$ must be satisfied with probability at least $1-\epsilon_i$:
    $$ Pr[g_i(x,\xi) \le 0] \ge 1-\epsilon_i, \quad i=1, \dots, m $$
    ICCs are generally easier to handle but may ignore dependencies between different stages of a vessel's voyage.

*   **Joint Chance Constraint (JCCP):**
    All constraints in a set must be satisfied simultaneously with a high probability:
    $$ Pr[g_1(x,\xi) \le 0, \dots, g_m(x,\xi) \le 0] \ge 1-\epsilon $$
    JCCPs are more robust for entire schedules (e.g., a vessel's multi-port rotation) but are computationally harder to solve due to the multidimensional integration required.

### 2. Linearization and Approximation Techniques
Since chance constraints are often non-convex and lack an explicit form, they are typically linearized or approximated:

*   **Scenario Approach (Sample Average Approximation - SAA):**
    The probability is approximated using $N$ scenarios $\{\xi^1, \dots, \xi^N\}$:
    $$ \frac{1}{N} \sum_{s=1}^N \mathbb{I}(g(x, \xi^s) \le 0) \ge 1-\epsilon $$
    This is often reformulated as a Mixed-Integer Linear Programming (MILP) problem by introducing binary variables $z_s$ that indicate if a scenario is "violated":
    $$ g(x, \xi^s) \le M z_s, \quad \sum_{s=1}^N z_s \le \lfloor \epsilon N \rfloor, \quad z_s \in \{0, 1\} $$

*   **CVaR (Conditional Value at Risk) Approximation:**
    CVaR is used as a convex, conservative upper bound for chance constraints. If the CVaR of the constraint violation is $\le 0$ at level $\alpha = 1-\epsilon$, then the chance constraint is satisfied:
    $$ CVaR_{1-\epsilon}(g(x, \xi)) \le 0 $$
    Linearization of CVaR for $N$ scenarios:
    $$ \min \zeta + \frac{1}{\epsilon N} \sum_{s=1}^N [g(x, \xi^s) - \zeta]^+ \le 0 $$
    where $[y]^+ = \max(0, y)$.

### 3. Key Literature (Western, Japanese, Korean)

*   **Meng, Q., & Wang, T. (2010):** *"A chance constrained programming model for short-term liner ship fleet planning problems."*
    *   **Focus:** Foundational work applying CCP to liner shipping fleet deployment.
    *   **Contribution:** Modeled uncertain demand and service time using CCP to determine optimal fleet size and deployment.

*   **Wang, S., Meng, Q., & Wang, T. (2013):** *"Risk management in liner ship fleet deployment: A joint chance constrained programming model."*
    *   **Focus:** Joint Chance Constraints (JCCP) for a full ship route.
    *   **Contribution:** Discussed the superiority of JCCP over ICC for maintaining schedule reliability across multiple ports of call.

*   **Dulebenets, M. A. (2018):** *"A Green Vessel Scheduling Problem with Container Inventory Cost and Slack Time Strategy."*
    *   **Focus:** Balancing fuel emissions and schedule reliability.
    *   **Contribution:** Used CCP to manage uncertain port handling times, demonstrating that optimal "slack time" insertion is critical for both green objectives and reliability.

*   **Yun, W. Y., & Lee, Y. M. (2011) [Korean]:** *"Optimal inventory control of empty containers in inland transportation system."*
    *   **Focus:** Stochastic inventory management in Korean logistics.
    *   **Contribution:** Applied CCP to ensure container availability under stochastic demand, a critical component of port-hinterland connectivity.

*   **Liu, D., Shi, G., & Hirayama, H. (2021) [Japanese/Kobe Univ]:** *"Vessel Scheduling Optimization Model Based on Variable Speed in a Seaport with One-Way Navigation Channel."*
    *   **Focus:** Safety in restricted waterways.
    *   **Contribution:** Used probabilistic constraints to ensure safe vessel spacing and timing in one-way channels under uncertain arrival times.

### 4. Risk Levels ($\epsilon$) in Practice
In maritime and port operations, the risk level $\epsilon$ (probability of failure) typically ranges from **0.01 to 0.10**.

*   **$\epsilon = 0.05$ (95% reliability):** The most common target for commercial liner shipping. It balances the cost of buffer time/fuel with the need for high service levels.
*   **$\epsilon = 0.01$ (99% reliability):** Used for critical safety constraints (e.g., channel navigation safety or hazardous cargo) or highly time-sensitive high-value goods.
*   **$\epsilon = 0.10$ (90% reliability):** Acceptable for low-priority cargo or routes with high flexibility/alternative options.

## Rolling Horizon / MPC

### 1. Overview and Mathematical Formulation
Rolling Horizon Optimization (RHO) and Model Predictive Control (MPC) are reactive, decomposition-based strategies used to handle uncertainty in real-time port operations (e.g., vessel arrivals, weather disruptions). Instead of solving a long-term problem once, the planning horizon is divided into smaller sub-periods. Only the decisions for the immediate period are implemented, and the model is continuously re-solved as time progresses and new state information becomes available.

*   **Horizon Length ($T_h$):** The future time window considered during each optimization step (e.g., 12 to 24 hours). A longer $T_h$ provides better foresight but increases computational time.
*   **Re-optimization Frequency ($\Delta t$):** How often the model is updated and re-solved (e.g., every 1 hour or when a disruptive event occurs).
*   **State Update Mechanism:** At each step $k$, the initial state $x_k$ is updated with the actual system state (e.g., realized vessel arrivals, current tugboat positions). The model predicts future states $\hat{x}_{k+j}$ over the horizon $T_h$.

**Standard Formulation (MPC/Rolling Horizon for Dispatch):**
At time step $k$, solve the following for the control sequence over the horizon $N$ (where $N \cdot \Delta t = T_h$):
$$ \min_{u_{k|k}, \dots, u_{k+N-1|k}} \sum_{j=0}^{N-1} L(\hat{x}_{k+j|k}, u_{k+j|k}) + V(\hat{x}_{k+N|k}) $$
*Subject to:*
*   System dynamics: $\hat{x}_{k+j+1|k} = f(\hat{x}_{k+j|k}, u_{k+j|k})$
*   Operational constraints: $\hat{x} \in \mathcal{X}, u \in \mathcal{U}$
*   Initial state: $\hat{x}_{k|k} = x_k$ (Current actual state updated with realized stochastic arrivals)

Only the first control action $u_{k|k}$ (e.g., immediate tugboat dispatch) is applied. At $k+1$, the horizon rolls forward.

### 2. Rolling Horizon vs. Full Stochastic Programming
*   **Computational Time Tradeoffs:**
    *   **Rolling Horizon:** Highly scalable and computationally efficient. It solves smaller, deterministic (or slightly stochastic) sub-problems, making it ideal for real-time, online scheduling of tugboats and continuous vessel traffic where quick response times are critical.
    *   **Stochastic Programming (SP):** Computationally heavy due to the "curse of dimensionality" when considering many future scenarios simultaneously. It is often too slow for real-time dispatch but better suited for determining optimal safety buffers (e.g., robust berth allocation) in advance.
    *   **Hybrid Trend:** Modern research often uses "Stochastic Lookahead" within a rolling horizon, solving a two-stage stochastic model over the short horizon $T_h$ to combine the adaptability of RHO with the robustness of SP.

### 3. Key Literature (Western/Japanese/Korean)
*   **Meisel, F. (2019) [Germany]:** *"Ship Traffic Optimization for the Kiel Canal"*
    *   **Focus:** Ship Traffic Control Problem.
    *   **Contribution:** Integrated rolling horizon approach for real-time scheduling of bidirectional vessel traffic, minimizing total waiting times in restricted waterways.
*   **Petris et al. (2022/2024) [Singapore]:** *"Bi-objective dynamic tugboat scheduling with speed optimization under stochastic and time-varying service demands"*
    *   **Focus:** Real-time tugboat dispatch and speed optimization.
    *   **Contribution:** Receding horizon-based Mixed-Integer Linear Programming (MILP) combined with Anticipatory Approximate Dynamic Programming to handle dynamic vessel arrivals and reduce fuel costs.
*   **Rodriguez-Molins, M., Salido, M. A., & Barber, F. (2014) [Spain]:** *"A rolling horizon approach for the integrated multi-quays berth allocation and crane assignment problem for bulk ports"*
    *   **Focus:** Integrated berth and crane scheduling.
    *   **Contribution:** Uses a rolling horizon strategy to continuously manage the dynamic and stochastic nature of vessel arrivals, allowing the port to reschedule resources efficiently without full-scale re-optimization.
*   **Agra, A., Christiansen, M., Hvattum, L. M., & Rodrigues, F. (2018) [Norway/International]:** *"Reoptimization framework and policy analysis for maritime inventory routing under uncertainty"*
    *   **Focus:** Maritime inventory routing.
    *   **Contribution:** Rolling-horizon reoptimization framework to handle stochastic voyage times and new information, adjusting sailing policies dynamically.

## Sample Average Approximation (SAA) & Scenario Generation

### SAA Formulation (Two-Stage)
* SAA replaces the true expectation with a sample average over $N$ scenarios:
  $$ \min_{x \in X} f_N(x) = \frac{1}{N}\sum_{i=1}^{N} f(x, \xi^i) $$
  (Ref: [SAA-T1])
* Two-stage recourse form:
  $$ \min_x c^T x + \mathbb{E}[Q(x,\xi)], \quad Q(x,\xi)=\min_y\{q^T y : Wy = h - Tx,\; y \ge 0\} $$
  In SAA, each scenario $s$ has its own recourse variables $y^s$. (Ref: [SAA-T2])

### Convergence & Sample Size Guidance
* For SAA with integer recourse, the probability that an SAA solution is truly optimal approaches 1 exponentially fast as $N$ increases; for a fixed $N$, statistical bounds on objective value and solution quality can be constructed. (Ref: [SAA-T2])
* In maritime logistics applications, SAA solutions can be shown to converge (w.p.1) to the true solution as $N \to \infty$ even under non-i.i.d. sampling. (Ref: [SAA-M3])

### Scenario Tree & Scenario Reduction
* Scenario tree: first-stage decisions $x$ at the root; each scenario $s$ corresponds to a leaf with probability $p_s$ and recourse variables $y^s$.
* Scenario reduction uses probability metrics to replace a large scenario set with a smaller representative subset while preserving distributional structure. (Ref: [SR-1])
* Heitsch–Römisch propose forward/backward reduction schemes, including fast forward selection. (Ref: [SR-2])

### Maritime/Port SAA Applications (3+)
* Wang & Meng (2012) — robust schedule design for liner shipping services; SAA + column generation used to handle uncertainty. (Ref: [SAA-M1])
* Delgado et al. (2015) — maritime inventory routing with stochastic sailing/port times; SAA embedded in an L-shaped-style method with scenario sampling. (Ref: [SAA-M2])
* Long, Lee & Chew (2015) — stochastic empty container repositioning; SAA with non-i.i.d. sampling and convergence results. (Ref: [SAA-M3])

### Wasserstein-DRO in Maritime Context
* Nadales et al. (2023, arXiv) — Wasserstein ambiguity set for distributionally robust vessel control in natural waterways. (Ref: [DRO-W1])
* Zhao et al. (2022) — vessel deployment with limited information; data-driven DRO model based on Wasserstein distance. (Ref: [DRO-W2])
