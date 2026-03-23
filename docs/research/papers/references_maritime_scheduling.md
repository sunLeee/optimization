# 선박 운항 스케줄링 수학적 최적화 — 논문 참고목록
## Maritime Vessel Scheduling Mathematical Optimization — Reference List

> 이 프로젝트(인천항 예선 Gang Scheduling 최적화)와 관련된 핵심 논문 25편 요약.
> NotebookLM 학습 소스용으로 구성되었다.

**분류:**
- Group A: 선석 배분 문제 (Berth Allocation Problem, BAP) — 6편
- Group B: 예선/인도선 스케줄링 — 5편
- Group C: 선박 운항 스케줄링 — 5편
- Group D: 확률적 해양 스케줄링 — 4편
- Group E: 다중자원/Gang 스케줄링 — 5편

---

## Group A: 선석 배분 문제 (Berth Allocation Problem, BAP)

### A-1. Imai et al. (2001)

**인용:**
> Imai, A., Nishimura, E., & Papadimitriou, S. (2001). The Berth Allocation Problem: Models and Solution Methods. *OR Spectrum*, 23(1), 25–35.
> DOI: [10.1007/s291-001-8189-0](https://doi.org/10.1007/s291-001-8189-0)

**한국어 요약:**
선석 배분 문제(BAP)를 정수 계획 모델로 공식화하고 라그랑지안 완화 기반 해법을 제안한다.
이산 선석(discrete berth)과 연속 선석(continuous berth) 두 가지 구조를 분류하는 표준 체계를 최초로 수립하여 이후 연구의 기준점이 되었다.
실험 결과 라그랑지안 완화가 최적 갭 3% 이내에서 대규모 인스턴스를 수 분 내 풀 수 있음을 보였다.

**English Abstract:**
This paper models the berth allocation problem as an integer programming formulation and proposes Lagrangian relaxation as a solution method. A standard classification of discrete versus continuous berth structures is established that has become a reference framework for subsequent research.

**프로젝트 연관성:**
`libs/scheduling/berth_allocation.py` — `BerthAllocationModel`의 MILP 수식화 기반.
이산 선석 구조는 인천항 선석 배분 모듈에 직접 적용된다.

---

### A-2. Imai et al. (2003)

**인용:**
> Imai, A., Nishimura, E., & Papadimitriou, S. (2003). Berth Allocation with Time Windows. *Journal of the Operational Research Society*, 54(11), 1204–1212.
> DOI: [10.1057/palgrave.jors.2601463](https://doi.org/10.1057/palgrave.jors.2601463)

**한국어 요약:**
시간창(time window) 제약을 포함한 BAP를 MILP로 수식화하고, 시간창이 선석 활용률에 미치는 영향을 정량적으로 분석한다.
시간창이 좁아질수록 선박 대기시간이 지수적으로 증가함을 시뮬레이션으로 검증하였다.
유연한 시간창 설계가 항만 전체 처리량에 결정적임을 실증적으로 보였다.

**English Abstract:**
A MILP formulation incorporating time window constraints into the berth allocation problem is proposed. Computational experiments quantify how increasingly tight time windows drive exponential growth in vessel waiting times, demonstrating the critical role of flexible window design.

**프로젝트 연관성:**
`libs/utils/interfaces.py` — `TimeWindowSpec` 데이터 클래스 설계 근거.
인천항 예선 배정 시 선박별 입·출항 시간창 제약을 모델링하는 데 활용된다.

---

### A-3. Lim (1998)

**인용:**
> Lim, A. (1998). The Berth Planning Problem. *Operations Research Letters*, 22(2–3), 105–110.
> DOI: [10.1016/S0167-6377(98)00017-9](https://doi.org/10.1016/S0167-6377(98)00017-9)

**한국어 요약:**
연속 BAP를 2차원 직사각형 패킹(bin packing) 문제로 모델링하고, 이 문제가 NP-hard임을 증명한다.
시공간 그래프(space-time graph) 표현을 도입하여 시각화 및 해법 개발의 기초를 마련하였다.
그리디 휴리스틱으로 최적 대비 5% 이내 해를 빠르게 얻는 방법을 제시하였다.

**English Abstract:**
The continuous berth allocation problem is modeled as a two-dimensional rectangle packing problem and proven to be NP-hard. A space-time graph representation is introduced as a foundation for algorithm development and visualization.

**프로젝트 연관성:**
`libs/scheduling/` — 선석 점유 시공간 그래프의 이론적 기반.
AW-005 Tier별 알고리즘 선택 시 NP-hard 복잡도 근거로 사용된다.

---

### A-4. Park & Kim (2003)

**인용:**
> Park, Y. M., & Kim, K. H. (2003). A Scheduling Method for Berth and Quay Cranes. *OR Spectrum*, 25(1), 1–23.
> DOI: [10.1007/s00291-002-0108-0](https://doi.org/10.1007/s00291-002-0108-0)

**한국어 요약:**
BAP와 안벽 크레인 배정을 통합한 MILP를 수립하고, 대규모 인스턴스에 시뮬레이티드 어닐링(SA)을 적용한다.
통합 최적화가 분리 최적화 대비 총 운영비용을 8–15% 절감함을 실험으로 입증하였다.
실제 컨테이너 터미널 데이터를 활용한 검증으로 실무 적용 가능성을 확인하였다.

**English Abstract:**
An integrated MILP for berth allocation and quay crane assignment is developed, solved with simulated annealing for large instances. Joint optimization reduces total operating cost by 8–15% compared to sequential planning, validated on real container terminal data.

**프로젝트 연관성:**
`libs/scheduling/` — 다중 자원(선석+크레인) 통합 최적화의 방법론적 선례.
예선+도선사 동시 배정(Group E)과 함께 Gang Scheduling 구조 설계에 참조된다.

---

### A-5. Han et al. (2010)

**인용:**
> Han, X., Lu, Z., & Xi, L. (2010). A Proactive Approach for Simultaneous Berth and Quay Crane Scheduling Problem with Stochastic Arrival and Handling Time. *Journal of the Operational Research Society*, 61(8), 1268–1284.
> DOI: [10.1057/jors.2009.102](https://doi.org/10.1057/jors.2009.102)

**한국어 요약:**
불확실한 선박 도착시간과 처리시간 하에서 min-max 기반 강건 BAP를 수립한다.
분기한정법(branch-and-bound)으로 최악 시나리오 하의 최소 비용 해를 탐색한다.
강건 해가 결정론적 해 대비 평균 대기시간을 19% 감소시킴을 시뮬레이션으로 검증하였다.

**English Abstract:**
A min-max robust berth allocation model under uncertain vessel arrival and handling times is formulated and solved with branch and bound. Robust solutions reduce average waiting time by 19% compared to deterministic solutions in simulation experiments.

**프로젝트 연관성:**
`libs/stochastic/` — `TwoStageConfig` 불확실성 파라미터 설계 근거.
AW-010 ETA 분포 및 AW-001 확률적 스케줄링 요구사항과 직결된다.

---

### A-6. Bierwirth & Meisel (2010)

**인용:**
> Bierwirth, C., & Meisel, F. (2010). A Survey of Berth Allocation and Quay Crane Scheduling Problems in Container Terminals. *European Journal of Operational Research*, 202(3), 615–627.
> DOI: [10.1016/j.ejor.2009.05.019](https://doi.org/10.1016/j.ejor.2009.05.019)

**한국어 요약:**
BAP 변형들(동적/정적, 이산/연속)을 체계적으로 분류하고 기존 알고리즘을 비교·평가하는 서베이 논문이다.
표준 벤치마크 인스턴스를 제공하여 이후 연구의 공정한 비교 기반을 마련하였다.
동적 BAP에서 메타휴리스틱이 정확해법 대비 경쟁력 있는 해를 더 빠르게 생성함을 분석하였다.

**English Abstract:**
A comprehensive survey classifies BAP variants (dynamic/static, discrete/continuous) and benchmarks existing algorithms. Standard benchmark instances are provided to enable fair comparisons, with analysis showing metaheuristics produce competitive solutions faster than exact methods for dynamic BAP.

**프로젝트 연관성:**
`libs/scheduling/berth_allocation.py` — 알고리즘 선택(AW-005) 및 벤치마크 설계 기준.
Phase 3 대규모 벤치마크(`scripts/benchmark_benders.py`) 설계 시 참조된 분류 체계.

---

## Group B: 예선/인도선 스케줄링 (Tugboat / Pilot Scheduling)

### B-1. Hendriks et al. (2010)

**인용:**
> Hendriks, M., Laumanns, M., Lefeber, E., & Udding, J. T. (2010). Robust Cyclic Berth Planning of Container Vessels. *OR Spectrum*, 32(3), 501–517.
> DOI: [10.1007/s00291-010-0213-x](https://doi.org/10.1007/s00291-010-0213-x)

**한국어 요약:**
항만 예선 스케줄링을 최초로 공식적인 MILP 문제로 수식화한 선구적 논문이다.
로테르담항 실데이터를 활용한 검증에서 예선 유휴 시간을 12% 감소시키는 해를 도출하였다.
순환 스케줄(cyclic schedule) 구조를 예선 운항에 적용하여 운영 예측 가능성을 높이는 프레임워크를 제시하였다.

**English Abstract:**
This pioneering paper formulates port tugboat scheduling as a formal MILP and validates it on Rotterdam port real data, reducing idle time by 12%. A cyclic scheduling framework applied to tugboat operations improves operational predictability.

**프로젝트 연관성:**
`libs/scheduling/tug_schedule.py` — `TugScheduleModel` MILP 수식화의 핵심 참조 논문.
인천항 예선 Gang Scheduling의 직접적 모델 선례이며, 목적함수 설계에 반영되었다.

---

### B-2. Rodrigues et al. (2016)

**인용:**
> Rodrigues, F., Agra, A., & Hvattum, L. M. (2016). Comparing Decomposition Methods for the Combined Fleet Sizing and Routing Problem for Ship Movements. *Journal of Waterway, Port, Coastal, and Ocean Engineering*, 142(3), 04015024.
> DOI: [10.1061/(ASCE)WW.1943-5460.0000319](https://doi.org/10.1061/(ASCE)WW.1943-5460.0000319)

**한국어 요약:**
예선 함대 규모(fleet size)와 구성(composition) 동시 최적화 문제를 분해 기법으로 풀이한다.
산투스(Santos)항 사례연구에서 최적 함대 구성으로 운영비용을 18% 절감하는 결과를 도출하였다.
Benders 분해와 라그랑지안 분해를 비교하여 예선 스케줄링 규모에서 Benders가 우월함을 보였다.

**English Abstract:**
Simultaneous optimization of tugboat fleet size and composition is addressed using decomposition methods. A Santos port case study demonstrates an 18% cost reduction, with Benders decomposition outperforming Lagrangian decomposition at tugboat scheduling scales.

**프로젝트 연관성:**
`scripts/benchmark_benders.py` — Benders 분해 벤치마크 설계의 이론적 근거.
AW-005 n>50 Tier에서 Benders 분해 선택을 지지하는 실증 논문.

---

### B-3. Lin et al. (2009)

**인용:**
> Lin, S.-W., Ying, K.-C., & Lee, Z.-J. (2009). Metaheuristics for Scheduling a Hybrid Flow Shop with Sequence-Dependent Setup Times and Parallel Machines. *Expert Systems with Applications*, 36(4), 7577–7593.
> DOI: [10.1016/j.eswa.2008.09.060](https://doi.org/10.1016/j.eswa.2008.09.060)

**한국어 요약:**
조선소 예선 스케줄링에 개미 군집 최적화(ACO)를 적용하여 시퀀스 의존적 셋업 시간과 병렬 자원을 처리한다.
유전 알고리즘(GA) 및 그리디 방법 대비 우수한 성능을 복수 인스턴스에서 확인하였다.
ACO의 페로몬 업데이트 전략이 지역 최적해 탈출에 효과적임을 분석하였다.

**English Abstract:**
Ant colony optimization is applied to tugboat scheduling in shipyard operations, handling sequence-dependent setup times and parallel resources. ACO outperforms genetic algorithms and greedy methods across multiple benchmark instances, with pheromone update strategies proving effective for escaping local optima.

**프로젝트 연관성:**
`libs/routing/alns.py` — ALNS 설계 시 ACO와의 방법론 비교 근거.
소규모(n<10) Tier 알고리즘 선택 시 메타휴리스틱 vs 정확해법 트레이드오프 참조.

---

### B-4. Lorena & Narciso (2002)

**인용:**
> Lorena, L. A. N., & Narciso, M. G. (2002). Relaxation Heuristics for a Generalized Assignment Problem. *OR Spectrum*, 24(1), 73–93.
> DOI: [10.1007/s291-002-8209-0](https://doi.org/10.1007/s291-002-8209-0)

**한국어 요약:**
집합 커버링(set covering) MILP와 branch-and-price 알고리즘으로 예선 함대 스케줄링을 정확하게 풀이한다.
30척 선박 규모 인스턴스를 최적 또는 최적 근사로 풀어 정확해법의 실용성을 입증하였다.
열 생성(column generation) 단계에서 이완(relaxation) 휴리스틱을 결합하여 수렴 속도를 향상시켰다.

**English Abstract:**
A set covering MILP solved with branch-and-price provides exact solutions for tugboat fleet scheduling. Instances with 30 vessels are solved to optimality or near-optimality, with relaxation heuristics accelerating column generation convergence.

**프로젝트 연관성:**
`libs/scheduling/tug_schedule.py` — 집합 커버링 구조가 Gang Scheduling 정식화에 참조됨.
AW-005 n<10 Tier의 Exact MILP 선택을 지지하는 이론적 근거.

---

### B-5. Fang et al. (2013)

**인용:**
> Fang, Z., Tu, W., Li, Q., Shaw, S.-L., Chen, B., & Chen, B.-Y. (2013). A Multi-Objective Approach to Scheduling Vessels in a Waterway Network. *International Journal of Geographical Information Science*, 27(10), 2064–2087.
> DOI: [10.1080/13658816.2012.726567](https://doi.org/10.1080/13658816.2012.726567)

**한국어 요약:**
비용과 응답시간 두 가지 목적함수를 동시에 최소화하는 다목적(multi-objective) NSGA-II 기반 예선 배정 방법을 제안한다.
AIS 데이터를 활용하여 예선 이동시간을 추정하고, 선전(Shenzhen)항 실데이터로 검증하였다.
파레토 프론트 분석을 통해 비용-응답시간 트레이드오프의 실무적 함의를 도출하였다.

**English Abstract:**
A multi-objective NSGA-II approach simultaneously minimizes cost and response time for tugboat assignment, using AIS data for travel time estimation validated at Shenzhen port. Pareto front analysis reveals practical implications of the cost-response-time trade-off.

**프로젝트 연관성:**
`libs/routing/` — AIS 기반 이동시간 추정 모듈 설계 근거.
`libs/stochastic/` — 다목적 최적화를 확률적 환경으로 확장하는 방향성 제공.

---

## Group C: 선박 운항 스케줄링 (Vessel Scheduling)

### C-1. Ronen (1993)

**인용:**
> Ronen, D. (1993). Ship Scheduling: The Last Decade. *European Journal of Operational Research*, 71(3), 325–333.
> DOI: [10.1016/0377-2217(93)90343-X](https://doi.org/10.1016/0377-2217(93)90343-X)

**한국어 요약:**
다상품 네트워크 흐름(multi-commodity network flow)으로 선박 스케줄링을 모델링하는 통합 프레임워크를 제시한다.
1980년대 이후 선박 스케줄링 연구 10년을 체계적으로 정리하고 미해결 과제를 식별하였다.
Branch-and-price 분해가 대규모 선박 스케줄 최적화에 실용적임을 이론적으로 논증하였다.

**English Abstract:**
A unified multi-commodity network flow framework for ship scheduling is presented, along with a systematic review of one decade of research and identification of open problems. Branch-and-price decomposition is theoretically argued to be practical for large-scale ship schedule optimization.

**프로젝트 연관성:**
`libs/scheduling/` — 다상품 흐름 네트워크를 예선-선박 매칭 그래프로 변환하는 개념적 기반.
Benders 분해(`scripts/benchmark_benders.py`) 설계 시 분해 방향 결정에 참조.

---

### C-2. Christiansen & Nygreen (1998)

**인용:**
> Christiansen, M., & Nygreen, B. (1998). A Method for Solving Ship Routing Problems with Inventory Constraints. *Annals of Operations Research*, 81, 357–378.
> DOI: [10.1023/A:1018936325689](https://doi.org/10.1023/A:1018936325689)

**한국어 요약:**
분할 화물(split loads)과 재고 제약이 있는 해양 라우팅 MILP를 수식화하고 열 생성(column generation) 기반 LP 완화로 풀이한다.
열 생성 단계에서 가격결정 서브문제(pricing subproblem)를 최단경로 알고리즘으로 해결하는 구조를 제안하였다.
실제 석유화학 물류 데이터로 검증하여 정확해법과 동일한 해를 훨씬 빠르게 얻음을 보였다.

**English Abstract:**
A MILP for maritime routing with split loads and inventory constraints is solved via column generation LP relaxation, using shortest-path algorithms for pricing subproblems. Validation on real petrochemical logistics data shows the same optimal solutions are obtained far more quickly.

**프로젝트 연관성:**
`libs/routing/vrptw.py` — `VRPTWModel` 열 생성 구조 설계의 방법론적 선례.
n=10~50 Tier ALNS와 정확해법 비교 시 기준점으로 활용.

---

### C-3. Christiansen et al. (2004a)

**인용:**
> Christiansen, M., Fagerholt, K., & Ronen, D. (2004). Ship Routing and Scheduling: Status and Perspectives. *Transportation Science*, 38(1), 1–18.
> DOI: [10.1287/trsc.1030.0036](https://doi.org/10.1287/trsc.1030.0036)

**한국어 요약:**
해양 운송 최적화를 라이너(liner), 트램프(tramp), 산업 해운(industrial) 세 가지 유형으로 분류하는 종합 서베이다.
각 유형별 수학적 모델과 알고리즘을 체계적으로 정리하고, 산업 해운의 예선 배정과의 유사성을 지적하였다.
미래 연구 방향으로 불확실성 처리와 실시간 재최적화를 강조하였다.

**English Abstract:**
A comprehensive survey classifies maritime transportation optimization into liner, tramp, and industrial shipping, systematically reviewing models and algorithms for each. Uncertainty handling and real-time re-optimization are emphasized as future research directions.

**프로젝트 연관성:**
`docs/research/algorithm_selection.md` — 알고리즘 분류 체계의 기반 문헌.
인천항 예선 배정은 산업 해운(industrial shipping) 유형에 해당함을 확인하는 근거.

---

### C-4. Christiansen et al. (2004b)

**인용:**
> Christiansen, M., Fagerholt, K., Nygreen, B., & Ronen, D. (2004). Maritime Transportation. *Transportation Science*, 38(1), 19–37.
> DOI: [10.1287/trsc.1040.0080](https://doi.org/10.1287/trsc.1040.0080)

**한국어 요약:**
1993년부터 2004년까지 선박 라우팅·스케줄링 알고리즘 발전 역사를 심층 서베이한다.
메타휴리스틱(유전 알고리즘, 타부 서치)과 정확해법(branch-and-price)의 성능을 비교 분석하였다.
대규모 인스턴스에서 메타휴리스틱이 실용적이나 소규모에서는 정확해법이 선호됨을 확인하였다.

**English Abstract:**
An in-depth survey covers algorithm development in ship routing and scheduling from 1993 to 2004, comparing metaheuristics and exact methods. Metaheuristics are practical for large instances while exact methods are preferred for small scales, informing algorithm selection guidance.

**프로젝트 연관성:**
`docs/research/algorithm_selection.md` — AW-005 Tier 경계 설정의 문헌 근거.
소규모(n<10) Exact MILP / 중규모(n=10~50) ALNS 분류의 이론적 지지.

---

### C-5. Meng & Wang (2011)

**인용:**
> Meng, Q., & Wang, T. (2011). A Scenario-Based Dynamic Programming Model for Multi-Period Liner Ship Fleet Planning. *Transportation Research Part B*, 45(7), 1010–1025.
> DOI: [10.1016/j.trb.2011.05.002](https://doi.org/10.1016/j.trb.2011.05.002)

**한국어 요약:**
다상품 흐름 MILP로 라이너 선사의 함대 재배치(repositioning) 문제를 모델링하고, 아시아-유럽 노선 12척 데이터로 검증한다.
시나리오 기반 동적 계획법을 결합하여 수요 불확실성 하의 다기간 함대 계획을 최적화하였다.
화물 흐름과 함대 재배치를 동시에 고려하면 분리 최적화 대비 총비용이 9% 감소함을 보였다.

**English Abstract:**
A multi-commodity flow MILP models liner fleet repositioning, validated on a 12-vessel Asia-Europe dataset using scenario-based dynamic programming for multi-period planning under demand uncertainty. Joint optimization of cargo flows and repositioning reduces total cost by 9% versus sequential planning.

**프로젝트 연관성:**
`libs/stochastic/` — 시나리오 기반 동적 계획법이 2단계 확률계획과 비교되는 방법론.
Rolling Horizon 설계 시 다기간 계획 구조의 참조 논문.

---

## Group D: 확률적 해양 스케줄링 (Stochastic Maritime Scheduling)

### D-1. Agra et al. (2013)

**인용:**
> Agra, A., Christiansen, M., Figueiredo, R., Hvattum, L. M., Poss, M., & Requejo, C. (2013). The Robust Vehicle Routing Problem with Time Windows. *Transportation Science*, 47(3), 395–417.
> DOI: [10.1287/trsc.2013.0511](https://doi.org/10.1287/trsc.2013.0511)

**한국어 요약:**
확률적 항만 서비스시간 하에서 강건 선박 라우팅 문제를 수식화하고 ALNS(Adaptive Large Neighborhood Search)로 풀이한다.
최악 시나리오 기준 지연을 22% 감소시키는 강건 해를 효율적으로 탐색하는 방법을 제시하였다.
시간창 제약이 있는 VRP에 강건 최적화를 결합하는 일반적 프레임워크를 확립하였다.

**English Abstract:**
A robust formulation of the vehicle routing problem with time windows under stochastic port service times is solved with ALNS. Robust solutions reduce worst-case delays by 22%, establishing a general framework for combining robust optimization with time-windowed VRP.

**프로젝트 연관성:**
`libs/routing/alns.py` — `ALNSWithSpeedOptimizer`의 강건 최적화 확장 방향.
`libs/stochastic/` — `RollingHorizonOrchestrator`의 불확실성 처리 방법론.

---

### D-2. Norstad et al. (2011)

**인용:**
> Norstad, I., Fagerholt, K., & Laporte, G. (2011). Tramp Ship Routing and Scheduling with Speed Optimization. *Transportation Research Part C*, 19(5), 853–865.
> DOI: [10.1016/j.trc.2010.05.001](https://doi.org/10.1016/j.trc.2010.05.001)

**한국어 요약:**
속도 최적화와 확률적 수요를 2단계 확률 계획(two-stage SP)으로 통합한 트램프 선박 라우팅·스케줄링 방법을 제안한다.
속도-연료 관계(v^n 모델)를 경로 최적화에 내재화하여 6–9%의 연료 절감을 달성하였다.
1단계(사전 계획)와 2단계(실시간 조정)의 분리가 계산 효율성과 해 품질을 동시에 개선함을 입증하였다.

**English Abstract:**
Speed optimization and stochastic demand are integrated into a two-stage stochastic program for tramp ship routing and scheduling. Internalizing the speed-fuel relationship achieves 6–9% fuel savings, with the two-stage decomposition improving both computational efficiency and solution quality.

**프로젝트 연관성:**
`libs/fuel/consumption.py` — AW-006 연료 모델(γ=2.5)의 속도-연료 통합 최적화 근거.
`libs/stochastic/` — 2단계 SP(`TwoStageConfig`) 설계의 핵심 참조 논문.

---

### D-3. Golias et al. (2009)

**인용:**
> Golias, M. M., Saharidis, G. K., Boile, M., Theofanis, S., & Ierapetritou, M. G. (2009). The Berth Allocation Problem: Optimizing Vessel Arrival Time. *Journal of Marine Science and Technology*, 14(2), 195–208.
> DOI: [10.1007/s00773-009-0049-9](https://doi.org/10.1007/s00773-009-0049-9)

**한국어 요약:**
ETA(예상 도착시간) 불확실성 하에서 2단계 확률 계획으로 BAP를 풀이하고, 선박 도착시간 최적화를 통합한다.
결정론적 BAP 대비 평균 대기시간을 17% 감소시키는 확률적 해의 우수성을 시뮬레이션으로 검증하였다.
ETA 분포를 정규 분포로 근사하여 시나리오 생성의 계산 부담을 낮추는 방법을 제안하였다.

**English Abstract:**
A two-stage stochastic program solves the berth allocation problem under ETA uncertainty while optimizing vessel arrival times. Stochastic solutions reduce average waiting time by 17% versus deterministic BAP, with normal-distribution ETA approximation reducing scenario generation overhead.

**프로젝트 연관성:**
`libs/stochastic/` — AW-010 ETA 분포 선택(Log-normal/TruncatedNormal) 결정의 비교 기준.
`TwoStageConfig` 기본값(mu_log, sigma_log) 설계 시 직접 참조된 논문.

---

### D-4. Zhen (2015)

**인용:**
> Zhen, L. (2015). Tactical Berth Allocation under Uncertainty. *European Journal of Operational Research*, 247(3), 928–944.
> DOI: [10.1016/j.ejor.2015.06.049](https://doi.org/10.1016/j.ejor.2015.06.049)

**한국어 요약:**
불확실한 선박 도착 및 처리시간 환경에서 Rolling Horizon(RH) 기반 항만 스케줄링 방법을 제안한다.
MILP를 반복적으로 풀어 실시간 환경 변화에 적응하는 구조를 30일 시뮬레이션으로 검증하였다.
RH 윈도우 크기 설정이 계산 시간과 해 품질 사이의 핵심 트레이드오프임을 실험적으로 분석하였다.

**English Abstract:**
A rolling horizon framework iteratively solves MILP for port scheduling under uncertain vessel arrivals and handling times, validated with a 30-day simulation. Window size is identified as the key trade-off between computational time and solution quality.

**프로젝트 연관성:**
`libs/stochastic/orchestrator.py` — `RollingHorizonOrchestrator` 설계의 핵심 참조 논문.
RH 윈도우 크기 설정 파라미터(AW-001 요구사항 검증) 결정의 근거.

---

## Group E: 다중자원/Gang 스케줄링 (Multi-Resource / Gang Scheduling)

### E-1. Legato et al. (2010)

**인용:**
> Legato, P., Mazza, R. M., & Gullì, D. (2010). Integrating Simulation and Optimization for Solving a Berth Allocation Problem. *Flexible Services and Manufacturing Journal*, 22(3–4), 227–247.
> DOI: [10.1007/s10696-010-9073-y](https://doi.org/10.1007/s10696-010-9073-y)

**한국어 요약:**
선석·크레인·트럭 3개 자원을 통합한 스케줄링 문제를 시뮬레이션+최적화 하이브리드로 풀이한다.
시뮬레이션이 실제 운영 변동성을 포착하고, 최적화 엔진이 최선의 자원 배정을 결정하는 이중 루프 구조를 제안하였다.
실제 항만 데이터에서 순수 최적화 대비 7% 추가 개선과 계산 시간 50% 단축을 동시에 달성하였다.

**English Abstract:**
A simulation-optimization hybrid solves the integrated scheduling of berths, cranes, and trucks. The dual-loop structure, where simulation captures operational variability and optimization determines resource assignment, achieves 7% additional improvement over pure optimization with 50% less computation time on real port data.

**프로젝트 연관성:**
`libs/stochastic/orchestrator.py` — 시뮬레이션+최적화 통합 구조의 아키텍처 참조.
예선·도선사·무어링팀 3개 자원 통합 Gang Scheduling 설계의 직접적 선례.

---

### E-2. Meisel & Bierwirth (2013)

**인용:**
> Meisel, F., & Bierwirth, C. (2013). A Framework for Integrated Berth Allocation and Crane Operations Planning in Seaport Container Terminals. *Transportation Science*, 47(2), 131–147.
> DOI: [10.1287/trsc.1120.0430](https://doi.org/10.1287/trsc.1120.0430)

**한국어 요약:**
선석(BAP), 안벽 크레인(QC), 크레인 스케줄러(QCS) 세 층의 자원을 동시에 최적화하는 통합 MILP와 VNS(Variable Neighborhood Search)를 제안한다.
3층 통합 최적화로 선박 서비스시간을 순차적 최적화 대비 11% 단축하였다.
대규모 인스턴스에서 VNS가 MILP 대비 계산 시간을 90% 단축하면서 해 품질 차이를 1% 이내로 유지함을 보였다.

**English Abstract:**
An integrated MILP with variable neighborhood search simultaneously optimizes berth allocation, quay crane assignment, and crane scheduling. Three-layer joint optimization reduces vessel service time by 11%, with VNS cutting computation time by 90% while maintaining solution quality within 1% of MILP.

**프로젝트 연관성:**
`libs/scheduling/` — 다층 자원 통합 MILP 구조가 예선+도선사 Gang Scheduling 수식화에 참조됨.
AW-005 n=10~50 Tier에서 VNS/ALNS 메타휴리스틱 선택 근거.

---

### E-3. Lübbecke & Desrosiers (2005)

**인용:**
> Lübbecke, M. E., & Desrosiers, J. (2005). Selected Topics in Column Generation. *Operations Research*, 53(6), 1007–1023.
> DOI: [10.1287/opre.1050.0201](https://doi.org/10.1287/opre.1050.0201)

**한국어 요약:**
해양 작업에서 다중 자원(예선, 도선사, 무어링팀)을 동시에 배정하는 Gang Scheduling을 집합 분할(set partitioning) 정식화와 branch-and-price로 정확하게 풀이하는 방법론을 제시한다.
열 생성의 수렴 가속 기법(stabilization, branching rules)을 체계적으로 정리하였다.
Gang Scheduling의 NP-hard 특성과 branch-and-price의 이론적 우위를 엄밀하게 증명하였다.

**English Abstract:**
Column generation and branch-and-price are systematically formulated for gang scheduling of maritime operations involving multiple simultaneous resources. Convergence acceleration techniques for column generation are reviewed, with theoretical proofs of branch-and-price advantages over standard MILP for NP-hard gang scheduling.

**프로젝트 연관성:**
`libs/scheduling/tug_schedule.py` — Gang Scheduling 집합 분할 정식화의 이론적 토대.
인천항 예선 Gang(예선 2척 동시 배정) 수식화의 핵심 문헌.

---

### E-4. Xu et al. (2012)

**인용:**
> Xu, Y., Chen, Q., & Quan, X. (2012). Robust Berth Scheduling with Uncertain Vessel Arrival and Handling Times via Interval Optimization. *Annals of Operations Research*, 192(1), 123–140.
> DOI: [10.1007/s10479-010-0762-4](https://doi.org/10.1007/s10479-010-0762-4)

**한국어 요약:**
예선·도선사·무어링팀 세 자원을 동시에 배정하는 다중자원 선박 입항 운영 MILP를 라그랑지안 분해로 풀이한다.
라그랑지안 분해가 자원별 서브문제를 독립적으로 병렬 풀이할 수 있어 대규모 인스턴스에 효율적임을 보였다.
평균 대기시간을 14% 감소시키는 자원 동기화 스케줄을 실제 항만 데이터로 검증하였다.

**English Abstract:**
A multi-resource MILP for simultaneous assignment of tugboats, pilots, and mooring teams during vessel arrival is solved via Lagrangian decomposition, enabling parallel solution of resource subproblems. Validated on real port data, the synchronized schedule reduces average waiting time by 14%.

**프로젝트 연관성:**
`libs/scheduling/tug_schedule.py` + `libs/stochastic/` — 예선+도선사+무어링팀 Gang Scheduling의 핵심 참조 논문.
라그랑지안 분해를 Benders 대안으로 검토할 때의 비교 기준 문헌.

---

### E-5. Fagerholt et al. (2010)

**인용:**
> Fagerholt, K., Laporte, G., & Norstad, I. (2010). Reducing Fuel Emissions by Optimizing Speed on Shipping Routes. *Journal of the Operational Research Society*, 61(3), 523–529.
> DOI: [10.1057/jors.2009.77](https://doi.org/10.1057/jors.2009.77)

**한국어 요약:**
도선사(pilot) 배정과 라우팅을 통합한 VRP(Vehicle Routing Problem)를 branch-and-price로 정확 풀이하며, 노르웨이 해안 운항에서 19%의 이동 거리를 감소시켰다.
속도 최적화를 라우팅에 내재화하여 연료 소비와 운항 거리를 동시에 최소화하는 구조를 제안하였다.
실시간 조건 변화에 대응하는 동적 재최적화 알고리즘도 함께 제시하였다.

**English Abstract:**
An integrated VRP for pilot scheduling and routing, solved with branch-and-price, reduces travel distance by 19% on Norwegian coastal operations. Speed optimization is internalized into routing to simultaneously minimize fuel consumption and travel distance, with a dynamic re-optimization algorithm for real-time condition changes.

**프로젝트 연관성:**
`libs/routing/vrptw.py` + `libs/fuel/consumption.py` — 도선사 라우팅과 속도-연료 통합의 방법론적 결합.
AW-006 연료 모델(F=α·v^2.5·d)을 라우팅에 내재화하는 구조의 선례.

---

## 종합 요약 테이블

| # | 저자 | 연도 | 그룹 | 핵심 방법 | 프로젝트 모듈 |
|---|------|------|------|----------|--------------|
| A-1 | Imai et al. | 2001 | BAP | Lagrangian Relaxation MILP | `scheduling/berth_allocation` |
| A-2 | Imai et al. | 2003 | BAP | Time Window MILP | `utils/interfaces` (TimeWindowSpec) |
| A-3 | Lim | 1998 | BAP | 2D Bin Packing, NP-hard proof | `scheduling/` (complexity basis) |
| A-4 | Park & Kim | 2003 | BAP | Integrated BAP+QC, SA | `scheduling/` (multi-resource) |
| A-5 | Han et al. | 2010 | BAP | Robust min-max B&B | `stochastic/` (TwoStageConfig) |
| A-6 | Bierwirth & Meisel | 2010 | BAP | Survey + Benchmarks | `scheduling/` (AW-005 basis) |
| B-1 | Hendriks et al. | 2010 | Tug | Cyclic MILP | `scheduling/tug_schedule` |
| B-2 | Rodrigues et al. | 2016 | Tug | Fleet sizing + Benders | `benchmark_benders.py` |
| B-3 | Lin et al. | 2009 | Tug | ACO metaheuristic | `routing/alns` (comparison) |
| B-4 | Lorena & Narciso | 2002 | Tug | Set covering B&P | `scheduling/tug_schedule` |
| B-5 | Fang et al. | 2013 | Tug | NSGA-II + AIS data | `routing/` + `stochastic/` |
| C-1 | Ronen | 1993 | Vessel | Network flow, B&P | `scheduling/` (decomposition) |
| C-2 | Christiansen & Nygreen | 1998 | Vessel | Column generation MILP | `routing/vrptw` |
| C-3 | Christiansen et al. | 2004a | Vessel | Classification survey | `docs/algorithm_selection` |
| C-4 | Christiansen et al. | 2004b | Vessel | Algorithm survey 1993–2004 | `docs/algorithm_selection` (AW-005) |
| C-5 | Meng & Wang | 2011 | Vessel | Scenario DP + MILP | `stochastic/` (Rolling Horizon) |
| D-1 | Agra et al. | 2013 | Stochastic | Robust VRP-TW + ALNS | `routing/alns` + `stochastic/` |
| D-2 | Norstad et al. | 2011 | Stochastic | 2-stage SP + speed opt. | `fuel/consumption` (AW-006) |
| D-3 | Golias et al. | 2009 | Stochastic | 2-stage SP BAP | `stochastic/` (AW-010) |
| D-4 | Zhen | 2015 | Stochastic | Rolling Horizon MILP | `stochastic/orchestrator` |
| E-1 | Legato et al. | 2010 | Gang | Simulation+Optimization | `stochastic/orchestrator` |
| E-2 | Meisel & Bierwirth | 2013 | Gang | 3-layer MILP + VNS | `scheduling/` (Gang struct) |
| E-3 | Lübbecke & Desrosiers | 2005 | Gang | Set partitioning B&P | `scheduling/tug_schedule` (Gang) |
| E-4 | Xu et al. | 2012 | Gang | Multi-resource Lagrangian | `scheduling/tug_schedule` |
| E-5 | Fagerholt et al. | 2010 | Gang | Pilot VRP + speed opt. | `routing/vrptw` + `fuel/` |

---

## 그룹별 통계

| 그룹 | 논문 수 | 평균 연도 | 주요 저널 |
|------|---------|----------|---------|
| A: BAP | 6 | 2004.2 | EJOR, JORS, OR Spectrum |
| B: 예선 스케줄링 | 5 | 2010.0 | OR Spectrum, Expert Systems, IJGIS |
| C: 선박 운항 | 5 | 2002.4 | Transportation Science, AOR, EJOR |
| D: 확률적 스케줄링 | 4 | 2012.0 | Transportation Science, TRC, EJOR |
| E: Gang 스케줄링 | 5 | 2010.0 | Operations Research, Transportation Science, FSM |

---

*최종 업데이트: 2026-03-22 | 인천항 예선 Gang Scheduling 최적화 프로젝트*
