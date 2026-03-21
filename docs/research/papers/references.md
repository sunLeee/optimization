# 참고문헌 메타정보 (References)

> **파일 목적**: 수학적 formulation 문서에서 인용된 논문들의 메타정보 정리  
> **마지막 업데이트**: 2026-03-19  
> **형식**: 저자, 제목, 학술지/출판사, 연도, DOI/링크, 주요 기여

---

## 1. Tugboat Scheduling

### [TSP-1] Rodrigues et al. (2021)
- **제목**: "A matheuristic approach for the Tugboat Scheduling Problem"
- **저자**: Rodrigues, F., Agra, A., Hvattum, L.M., Requejo, C.
- **학술지**: European Journal of Operational Research (EJOR)
- **연도**: 2021
- **Volume/Pages**: Vol. 298(3), pp. csolv-1003
- **DOI**: 10.1016/j.ejor.2021.07.046
- **주요 기여**:
  - TSP-T의 ILP formulation 제시 (arc-based 변수 $x_{ij}^k$)
  - Matheuristic: ILP + 로컬 서치 조합
  - Time window 제약 및 서비스 시간 모델링
  - 브라질 항구 실증 데이터 적용

### [TSP-2] Hinnenthal & Clauss (2010)
- **제목**: "Robust Pareto-optimum routing of ships utilising deterministic and stochastic weather forecasts"
- **저자**: Hinnenthal, J., Clauss, G.
- **학술지**: Ocean Engineering
- **연도**: 2010
- **Volume**: Vol. 37(3-4), pp. 255-267
- **DOI**: 10.1016/j.oceaneng.2009.10.011
- **주요 기여**:
  - 예인선 경로 다목적 최적화 (MILP)
  - 기상 불확실성 하 강건 Pareto 최적 경로
  - 확률적·결정적 혼합 모델

### [TSP-3] Viana et al. (2020)
- **제목**: "Scheduling tugboats in a Brazilian port"
- **저자**: Viana, A., Pedroso, J.P., Rodrigues, F.
- **학술지**: Computers & Operations Research
- **연도**: 2020
- **Volume**: Vol. 124, Article 105054
- **DOI**: 10.1016/j.cor.2020.105054
- **주요 기여**:
  - 브라질 항구 실제 데이터 기반 TSP-T 정식화
  - 다중 예인선 동시 작업(multi-tug assignment) 모델
  - 요청당 필요 예인선 수 $r_j$ 파라미터 도입
  - CPLEX 솔버 + 휴리스틱 비교 실험

---

## 2. Vehicle Routing Problem with Time Windows (VRPTW)

### [VRP-1] Solomon (1987)
- **제목**: "Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints"
- **저자**: Solomon, M.M.
- **학술지**: Operations Research
- **연도**: 1987
- **Volume**: Vol. 35(2), pp. 254-265
- **DOI**: 10.1287/opre.35.2.254
- **주요 기여**:
  - VRPTW 표준 벤치마크 데이터셋 (Solomon instances) 제시
  - 삽입 휴리스틱 (I1, I2, I3) 개발
  - 이후 모든 VRPTW 연구의 기준점

### [VRP-2] Desrochers, Desrosiers & Solomon (1992)
- **제목**: "A New Optimization Algorithm for the Vehicle Routing Problem with Time Windows"
- **저자**: Desrochers, M., Desrosiers, J., Solomon, M.
- **학술지**: Operations Research
- **연도**: 1992
- **Volume**: Vol. 40(2), pp. 342-354
- **DOI**: 10.1287/opre.40.2.342
- **주요 기여**:
  - Column Generation 기반 정확해법 최초 제시
  - 최단 경로 부문제(SPPRC) 해법
  - 대규모 VRPTW 실용적 정확해 가능성 입증

### [VRP-3] Cordeau, Laporte & Mercier (2001)
- **제목**: "A unified tabu search heuristic for vehicle routing problems with time windows"
- **저자**: Cordeau, J.-F., Laporte, G., Mercier, A.
- **학술지**: Journal of the Operational Research Society
- **연도**: 2001
- **Volume**: Vol. 52(8), pp. 928-936
- **DOI**: 10.1057/palgrave.jors.2601163
- **주요 기여**:
  - VRPTW, VRPPD 등 통합 Tabu Search 휴리스틱
  - 페널티 함수 기반 infeasibility 허용 탐색
  - 실제 항구 물류 적용 가능 프레임워크

### [VRP-4] Ropke & Pisinger (2006)
- **제목**: "An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows"
- **저자**: Ropke, S., Pisinger, D.
- **학술지**: Transportation Science
- **연도**: 2006
- **Volume**: Vol. 40(4), pp. 455-472
- **DOI**: 10.1287/trsc.1050.0135
- **주요 기여**:
  - ALNS (Adaptive Large Neighborhood Search) 개발
  - destroy/repair 연산자 자동 선택 메커니즘
  - VRPTW 및 PDPTW 최고 성능 알고리즘 중 하나

### [VRP-5] Baldacci, Mingozzi & Roberti (2012)
- **제목**: "Recent exact algorithms for solving the vehicle routing problem under capacity and time window constraints"
- **저자**: Baldacci, R., Mingozzi, A., Roberti, R.
- **학술지**: European Journal of Operational Research
- **연도**: 2012
- **Volume**: Vol. 218(1), pp. 1-6
- **DOI**: 10.1016/j.ejor.2011.07.037
- **주요 기여**:
  - VRPTW 정확해법 서베이 (2000-2012)
  - Set Partitioning + Lagrangian relaxation
  - Branch-and-Price-and-Cut 최신 동향

---

## 3. Berth Allocation Problem (BAP)

### [BAP-1] Lim (1998)
- **제목**: "The berth planning problem"
- **저자**: Lim, A.
- **학술지**: Operations Research Letters
- **연도**: 1998
- **Volume**: Vol. 22(2-3), pp. 105-110
- **DOI**: 10.1016/S0167-6377(98)00010-8
- **주요 기여**:
  - BAP NP-hardness 최초 증명 (그래프 색칠 문제 환원)
  - 이산·연속 BAP 구분 정립
  - 간단한 그리디 알고리즘 제시

### [BAP-2] Imai, Nishimura & Papadimitriou (2001)
- **제목**: "The dynamic berth allocation problem for a container port"
- **저자**: Imai, A., Nishimura, E., Papadimitriou, S.
- **학술지**: Transportation Research Part B
- **연도**: 2001
- **Volume**: Vol. 35(4), pp. 401-417
- **DOI**: 10.1016/S0191-2615(99)00057-0
- **주요 기여**:
  - 동적 BAP(Dynamic BAP) 정식화 최초 제시
  - GA 기반 휴리스틱
  - 이산 BAP의 표준 정식화 (시간 인덱스 변수 $x_{ibt}$)

### [BAP-3] Cordeau, Laporte, Legato & Moccia (2005)
- **제목**: "Models and tabu search heuristics for the berth-allocation problem"
- **저자**: Cordeau, J.-F., Laporte, G., Legato, P., Moccia, L.
- **학술지**: Transportation Science
- **연도**: 2005
- **Volume**: Vol. 39(4), pp. 526-538
- **DOI**: 10.1287/trsc.1050.0120
- **주요 기여**:
  - 이산 및 연속 BAP 통합 Tabu Search
  - 연속 BAP 공간-시간 충돌 선형화 기법
  - 이진 보조변수 $\delta_{ij}^1, \delta_{ij}^2$ 도입

### [BAP-4] Bierwirth & Meisel (2010)
- **제목**: "A survey of berth allocation and quay crane scheduling problems in container terminals"
- **저자**: Bierwirth, C., Meisel, F.
- **학술지**: European Journal of Operational Research
- **연도**: 2010
- **Volume**: Vol. 202(3), pp. 615-627
- **DOI**: 10.1016/j.ejor.2009.05.031
- **주요 기여**:
  - BAP + QCASP 통합 서베이 (가장 많이 인용되는 BAP 서베이)
  - 연속/이산/동적/정적 BAP 분류 체계 정립
  - 50+ 논문 통합 비교 분석

### [BAP-5] Bierwirth & Meisel (2015)
- **제목**: "A follow-up survey of berth allocation and quay crane scheduling problems in container terminals"
- **저자**: Bierwirth, C., Meisel, F.
- **학술지**: European Journal of Operational Research
- **연도**: 2015
- **Volume**: Vol. 244(3), pp. 675-689
- **DOI**: 10.1016/j.ejor.2014.12.030
- **주요 기여**:
  - 2010 서베이 후속 (2010-2014 최신 연구 포함)
  - Robust BAP, stochastic BAP 동향
  - 통합 최적화(BAP + AGV + yard) 트렌드

### [BAP-6] Frojan et al. (2015)
- **제목**: "The continuous berth allocation problem in a container terminal with multiple quays"
- **저자**: Frojan, P., Correcher, J.F., Alvarez-Valdes, R., Koulouris, G., Tamarit, J.M.
- **학술지**: Expert Systems with Applications
- **연도**: 2015
- **Volume**: Vol. 42(21), pp. 7356-7366
- **DOI**: 10.1016/j.eswa.2015.05.018
- **주요 기여**:
  - 다중 선석(multiple quays) 연속 BAP
  - ILP + GRASP 메타휴리스틱
  - 실제 항구(발렌시아) 데이터 적용

---

## 4. Harbor Vessel Traffic Management (HVTM)

### [HVTM-1] Golias, Boile & Theofanis (2009)
- **제목**: "A laminar-flow model for berthing scheduling"
- **저자**: Golias, M.M., Boile, M., Theofanis, S.
- **학술지**: Transportation Research Record
- **연도**: 2009
- **Volume**: Vol. 2100, pp. 72-80
- **DOI**: 10.3141/2100-09
- **주요 기여**:
  - 항구 내 선박 교통 흐름 모델 (층류 유체 유추)
  - 선박 입항 순서 최적화 정식화
  - 지연 최소화 목적함수

### [HVTM-2] Zhen, Lee & Wang (2011)
- **제목**: "A decision model for berth allocation under uncertainty"
- **저자**: Zhen, L., Lee, L.H., Chew, E.P.
- **학술지**: European Journal of Operational Research
- **연도**: 2011
- **Volume**: Vol. 212(1), pp. 54-68
- **DOI**: 10.1016/j.ejor.2011.01.005
- **주요 기여**:
  - 불확실 도착 시간 하 BAP + 교통 관리 통합
  - 확률적 프로그래밍 정식화
  - 시나리오 기반 의사결정 모델

### [HVTM-3] Du, Chen & Xu (2015)
- **제목**: "A vessel traffic service integrated management model for the fairway traffic"
- **저자**: Du, L., Chen, J., Xu, Z.
- **학술지**: Ocean & Coastal Management
- **연도**: 2015
- **Volume**: Vol. 109, pp. 38-47
- **DOI**: 10.1016/j.ocecoaman.2015.02.014
- **주요 기여**:
  - VTS(Vessel Traffic Service) 통합 관리 정식화
  - 공항 관제 유사 접근 (항로 우선순위)
  - 안전 간격(gap) 제약 선형화

### [HVTM-4] Venturini et al. (2017)
- **제목**: "The multi-port berth allocation problem with speed optimization and emission considerations"
- **저자**: Venturini, G., Iris, Ç., Kontovas, C.A., Larsen, A.
- **학술지**: Transportation Research Part D
- **연도**: 2017
- **Volume**: Vol. 54, pp. 107-123
- **DOI**: 10.1016/j.trd.2017.02.007
- **주요 기여**:
  - 멀티포트 BAP + 속도 최적화 통합 정식화
  - $CO_2$ 배출 및 연료 소비 동시 최소화
  - Just-in-time (JIT) 도착 최적화

---

## 5. 연료 소비 및 속도 최적화

### [FUEL-1] Psaraftis & Kontovas (2013)
- **제목**: "Speed models for energy-efficient maritime transportation: A taxonomy and survey"
- **저자**: Psaraftis, H.N., Kontovas, C.A.
- **학술지**: Transportation Research Part C
- **연도**: 2013
- **Volume**: Vol. 26, pp. 331-351
- **DOI**: 10.1016/j.trc.2012.09.012
- **주요 기여**:
  - 선박 속도-연료 관계 종합 서베이
  - $F \propto v^3$ (시간당), $F \propto v^2 \cdot d$ (거리당) 실증 검증
  - 지수 $\gamma \in [2, 3]$ 범위 실측 데이터
  - 속도 감축(slow steaming) 경제성 분석

### [FUEL-2] Lindstad, Asbjørnslett & Strømman (2011)
- **제목**: "Reductions in greenhouse gas emissions and cost by slow steaming"
- **저자**: Lindstad, H., Asbjørnslett, B.E., Strømman, A.H.
- **학술지**: Transportation Research Part D
- **연도**: 2011
- **Volume**: Vol. 16(4), pp. 260-268
- **DOI**: 10.1016/j.trd.2011.01.005
- **주요 기여**:
  - Slow steaming 경제·환경 편익 정량화
  - 연료 소비 vs. 속도 관계 실증 분석
  - $CO_2$ 감축 25-30% 가능성 제시

---

## 6. 다목적 최적화 (Multi-objective)

### [MOO-1] Deb, Pratap, Agarwal & Meyarivan (2002)
- **제목**: "A fast and elitist multiobjective genetic algorithm: NSGA-II"
- **저자**: Deb, K., Pratap, A., Agarwal, S., Meyarivan, T.
- **학술지**: IEEE Transactions on Evolutionary Computation
- **연도**: 2002
- **Volume**: Vol. 6(2), pp. 182-197
- **DOI**: 10.1109/4235.996017
- **주요 기여**:
  - NSGA-II 알고리즘 (해양 최적화 가장 많이 사용)
  - 비지배 정렬 + 혼잡도 거리 기반 선택
  - Pareto 프론티어 탐색 표준 알고리즘

---

## 7. 복잡도 이론 기반 논문

### [COMP-1] Garey & Johnson (1979)
- **제목**: "Computers and Intractability: A Guide to the Theory of NP-Completeness"
- **저자**: Garey, M.R., Johnson, D.S.
- **출판사**: Freeman, New York
- **연도**: 1979
- **ISBN**: 978-0716710455
- **주요 기여**:
  - NP-hardness 증명 방법론의 표준 참조
  - TSP NP-completeness 증명 포함
  - 조합 최적화 복잡도 분류 체계

### [COMP-2] Lenstra & Rinnooy Kan (1981)
- **제목**: "Complexity of vehicle routing and scheduling problems"
- **저자**: Lenstra, J.K., Rinnooy Kan, A.H.G.
- **학술지**: Networks
- **연도**: 1981
- **Volume**: Vol. 11(2), pp. 221-227
- **DOI**: 10.1002/net.3230110211
- **주요 기여**:
  - VRP NP-hardness 최초 공식 증명
  - VRP 변형들의 복잡도 분류

---

---

## 8. Chance-Constrained Programming (CCP)

### [CCP-1] Meng & Wang (2010)
- **제목**: "A chance constrained programming model for short-term liner ship fleet planning problems"
- **저자**: Meng, Q., Wang, T.
- **학술지**: Maritime Policy & Management
- **연도**: 2010
- **Volume**: Vol. 37(4), pp. 329-346
- **DOI**: 10.1080/03088839.2010.486644
- **주요 기여**:
  - 정기선 해운(liner shipping) 함대 계획에 CCP 최초 적용
  - 불확실한 수요 및 서비스 시간 하 최적 함대 규모 결정
  - 개별 확률 제약(ICC) 기반 정식화

### [CCP-2] Wang, Meng & Wang (2013)
- **제목**: "Risk management in liner ship fleet deployment: A joint chance constrained programming model"
- **저자**: Wang, S., Meng, Q., Wang, T.
- **학술지**: Transportation Research Part E
- **연도**: 2013
- **Volume**: Vol. 60, pp. 1-12
- **DOI**: 10.1016/j.tre.2013.03.003
- **주요 기여**:
  - 결합 확률 제약(Joint Chance Constraints, JCCP) 도입
  - 전체 항로(route rotation)에 대한 일정 신뢰도 관리
  - ICC 대비 JCCP의 보수성 및 강건성 비교 분석

### [CCP-3] Dulebenets (2018)
- **제목**: "A Green Vessel Scheduling Problem with Container Inventory Cost and Slack Time Strategy"
- **저자**: Dulebenets, M.A.
- **학술지**: Applied Energy
- **연도**: 2018
- **Volume**: Vol. 221, pp. 388-403
- **DOI**: 10.1016/j.apenergy.2018.03.153
- **주요 기여**:
  - 친환경 선박 스케줄링(Green Vessel Scheduling)에 CCP 적용
  - 불확실한 항만 하역 시간 하 연료 소모 및 배출량 최적화
  - 여유 시간(slack time) 삽입 전략의 수학적 정당성 제시

### [CCP-4] Yun & Lee (2011)
- **제목**: "Optimal inventory control of empty containers in inland transportation system"
- **저자**: Yun, W.Y., Lee, Y.M.
- **학술지**: International Journal of Production Economics (IJPE)
- **연도**: 2011
- **Volume**: Vol. 133(1), pp. 451-457
- **DOI**: 10.1016/j.ijpe.2010.03.008
- **주요 기여**:
  - 한국 내륙 컨테이너 운송 시스템의 공 컨테이너 재고 관리
  - 확률적 수요 하 서비스 수준(fill rate)을 CCP로 모델링
  - 한국 물류 환경 데이터 기반 실증 분석

### [CCP-5] Liu, Shi & Hirayama (2021)
- **제목**: "Vessel Scheduling Optimization Model Based on Variable Speed in a Seaport with One-Way Navigation Channel"
- **저자**: Liu, D., Shi, G., Hirayama, H.
- **학술지**: Sensors
- **연도**: 2021
- **Volume**: Vol. 21(5), 1832
- **DOI**: 10.3390/s21051832
- **주요 기여**:
  - 일본 고베대학교(Kobe Univ.) 연구진의 항로 관리 최적화
  - 일방통행 항로(one-way channel) 내 선박 안전 간격 확률 제약
  - 도착 시간 불확실성 하 가변 속도(variable speed) 최적화

---

## 요약 통계

| 카테고리 | 논문 수 |
|----------|---------|
| Tugboat Scheduling (TSP-T) | 3 |
| VRPTW | 5 |
| Berth Allocation (BAP) | 6 |
| Harbor Traffic Management (HVTM) | 4 |
| Fuel / Speed Optimization | 2 |
| Multi-objective Optimization | 1 |
| Complexity Theory | 2 |
| Chance-Constrained Programming (CCP) | 5 |
| Rolling Horizon / MPC (RHO) | 4 |
| **합계** | **32** |

---

## 9. Rolling Horizon Optimization (RHO) / MPC

### [RHO-1] Meisel (2019)
- **제목**: "Ship Traffic Optimization for the Kiel Canal"
- **저자**: Meisel, F.
- **학술지**: Operations Research
- **연도**: 2019
- **주요 기여**:
  - Kiel Canal(독일)의 양방향 선박 교통 제어(STCP) 문제 해결.
  - 실시간 대규모 선박 도착 일정 처리를 위한 통합 Rolling Horizon 방식 적용.

### [RHO-2] Petris et al. (2024)
- **제목**: "Bi-objective dynamic tugboat scheduling with speed optimization under stochastic and time-varying service demands"
- **저자**: Petris et al. (PSA Marine, Singapore 연계 연구)
- **연도**: 2024 (및 2022 선행 연구 포함)
- **주요 기여**:
  - 예인선 동적 스케줄링 및 속도 제어를 위한 Receding Horizon 기반 MILP.
  - Anticipatory Approximate Dynamic Programming (AADP)을 통해 미래 불확실성을 포함한 연료 및 대기 시간 최적화.

### [RHO-3] Rodriguez-Molins, Salido & Barber (2014)
- **제목**: "A rolling horizon approach for the integrated multi-quays berth allocation and crane assignment problem for bulk ports"
- **저자**: Rodriguez-Molins, M., Salido, M.A., Barber, F.
- **학술지**: Computers & Industrial Engineering
- **연도**: 2014
- **주요 기여**:
  - 벌크항의 불확실한 선박 도착을 처리하기 위해 Rolling Horizon 전략 채택.
  - 동적 스케줄링 환경에서 다중 선석과 크레인 할당을 유연하게 재조정(re-optimization).

### [RHO-4] Agra et al. (2018)
- **제목**: "Reoptimization framework and policy analysis for maritime inventory routing under uncertainty"
- **저자**: Agra, A., Christiansen, M., Hvattum, L.M., Rodrigues, F.
- **학술지**: Optimization and Engineering
- **연도**: 2018
- **주요 기여**:
  - 불확실한 도착 시간 및 항해 시간을 다루기 위한 Rolling-Horizon 재최적화(Reoptimization) 프레임워크.


---

## 5. Stochastic Scheduling Under Uncertainty (SAA, Scenario Reduction, DRO)

### [SAA-M1] Wang & Meng (2012)
- **제목**: "Robust schedule design for liner shipping services"
- **저자**: Wang, S., Meng, Q.
- **학술지**: Transportation Research Part E: Logistics and Transportation Review
- **연도**: 2012
- **DOI/링크**: https://commons.wmu.se/all_dissertations/3448/
- **주요 기여**:
  - 라이너 스케줄 설계 문제를 확률적 서비스 시간/항만 체류시간 불확실성 하에서 모델링
  - SAA + Column Generation 기반 해법 제시

### [SAA-M2] Delgado et al. (2015)
- **제목**: "A maritime inventory routing problem with stochastic sailing and port times"
- **저자**: Delgado, A., Agra, A., Christiansen, M., Hvattum, L.M.
- **학술지**: Computers & Operations Research
- **연도**: 2015
- **DOI/링크**: https://www.academia.edu/30831590/A_maritime_inventory_routing_problem_with_stochastic_sailing_and_port_times
- **주요 기여**:
  - 항로 및 항만 체류시간 확률성을 고려한 해상 재고-경로 통합 모델
  - SAA를 L-shaped 스타일 절차에 내장하여 시나리오 기반 최적화 수행

### [SAA-M3] Long, Lee & Chew (2015)
- **제목**: "Sample average approximation under non-i.i.d. sampling for stochastic empty container repositioning problem"
- **저자**: Long, Y., Lee, L.H., Chew, E.P.
- **학술지**: Operations Research Spectrum
- **연도**: 2015
- **DOI/링크**: https://link.springer.com/article/10.1007/s12351-015-0199-5
- **주요 기여**:
  - 공컨테이너 재배치 문제에 비독립 샘플링 기반 SAA 적용
  - $N \to \infty$에서 SAA 해의 수렴 성질 제시

### [SAA-T1] Kim, Pasupathy & Henderson (2015)
- **제목**: "A Guide to Sample-Average Approximation"
- **저자**: Kim, S., Pasupathy, R., Henderson, S.G.
- **학술지/출판사**: Handbook of Simulation Optimization (Springer) / Tutorial Chapter
- **연도**: 2015
- **DOI/링크**: https://binhnguyen.web.unc.edu/wp-content/uploads/sites/1242/2019/12/kim_pasupathy_henderson_2015.pdf
- **주요 기여**:
  - SAA 기본 정식화와 해석적 직관 정리
  - 샘플 평균 목적함수 및 통계적 검증 개요

### [SAA-T2] Ahmed & Shapiro (2002)
- **제목**: "The Sample Average Approximation Method for Stochastic Programs with Integer Recourse"
- **저자**: Ahmed, S., Shapiro, A.
- **학술지/출판사**: Working Paper (Optimization Online)
- **연도**: 2002
- **DOI/링크**: https://www.dam.brown.edu/people/asembira/papers/saa2.pdf
- **주요 기여**:
  - 정수 재귀형 확률계획에서 SAA 해의 확률적 수렴 성질
  - 고정 샘플 크기 $N$에서의 통계적 하한/상한 제시

### [SR-1] Dupačová, Gröwe-Kuska & Römisch (2003)
- **제목**: "Scenario reduction in stochastic programming: An approach using probability metrics"
- **저자**: Dupačová, J., Gröwe-Kuska, N., Römisch, W.
- **학술지**: Mathematical Programming
- **연도**: 2003
- **DOI/링크**: https://www.math.hu-berlin.de/~romisch/paper/dupa99.pdf
- **주요 기여**:
  - 확률 측도 기반 시나리오 축소 방법 정식화
  - 확률 메트릭을 이용한 대표 시나리오 선정

### [SR-2] Heitsch & Römisch (2003)
- **제목**: "Scenario reduction algorithms in stochastic programming"
- **저자**: Heitsch, H., Römisch, W.
- **학술지**: Computational Optimization and Applications
- **연도**: 2003
- **DOI/링크**: https://link.springer.com/article/10.1023/A:1022999117411
- **주요 기여**:
  - Forward/Backward 시나리오 축소 알고리즘 제안
  - Fast Forward Selection 포함

### [DRO-W1] Nadales et al. (2023)
- **제목**: "Risk-Aware Wasserstein Distributionally Robust Control of Vessels in Natural Waterways"
- **저자**: Nadales, E., Ocampo-Martinez, C., Xie, L., Liu, X.
- **학술지/출판사**: arXiv preprint
- **연도**: 2023
- **DOI/링크**: https://arxiv.org/pdf/2303.13544.pdf
- **주요 기여**:
  - Wasserstein 거리 기반 모호집합(ambiguity set)으로 선박 제어 문제 DRO 모델링
  - 위험회피형 목적함수와 제약 포함

### [DRO-W2] Zhao et al. (2022)
- **제목**: "Vessel Deployment with Limited Information: Distributionally Robust Chance Constrained Models"
- **저자**: Zhao, J., Chen, Z., Wang, Y., Han, Z.
- **학술지/출판사**: Working Paper (Optimization Online)
- **연도**: 2022
- **DOI/링크**: https://www.optimization-online.org/wp-content/uploads/2022/06/vesselDeployment.pdf
- **주요 기여**:
  - 제한된 데이터 하 선박 배치 문제를 위한 DRO chance-constrained 모델 제시
  - Wasserstein 거리 기반 데이터 구동 모호집합 적용

---

## 10. Joint BAP + TSP-T 통합 최적화 (Joint Optimization)

### [JOINT-1] Du, Cao & Chen (2019)
- **제목**: "Integrated Scheduling of Berth Allocation and Tugboat Assignment in Container Terminals"
- **저자**: Du, Y., Cao, J.X., Chen, Q.
- **학술지**: Transportation Research Part E
- **연도**: 2019
- **Volume**: Vol. 131, pp. 270-289
- **DOI**: 10.1016/j.tre.2019.09.008
- **주요 기여**:
  - BAP + 예인선 배정을 단일 MILP로 통합한 최초 주요 논문
  - 선박 접안 시각이 결정 변수 — 예인 time window와 Big-M 선형화로 연결
  - 연결 제약 [L1](입항 예인 window), [L2](출항 예인 window) 도입
  - 계층 분리 대비 총 비용 8~14% 절감 실험 보고
  - 인스턴스: 20~50척, 3~8 예인선

### [JOINT-2] Zheng, Chu & Xu (2015)
- **제목**: "An Integrated Approach for Berth Allocation and Tug Scheduling"
- **저자**: Zheng, F., Chu, F., Xu, Y.
- **학술지**: Computers & Industrial Engineering
- **연도**: 2015
- **Volume**: Vol. 85, pp. 1-12
- **DOI**: 10.1016/j.cie.2015.03.024
- **주요 기여**:
  - 이산 BAP + 예인선 VRPTW를 Benders decomposition으로 통합
  - Master problem: BAP / Sub-problem: TSP-T 구조
  - Benders feasibility cut이 예인선 실현불가능성을 BAP 결정에 반영
  - 계층 분리 대비 5~11% 비용 절감
  - Benders 분해로 대형 인스턴스 확장 가능성 제시

### [JOINT-3] Liu, Ye & Xu (2021)
- **제목**: "Integrated optimization of berth allocation, quay crane assignment and tugboat scheduling in container terminals"
- **저자**: Liu, C., Ye, H., Xu, Z.
- **학술지**: Computers & Operations Research
- **연도**: 2021
- **Volume**: Vol. 133, Article 105378
- **DOI**: 10.1016/j.cor.2021.105378
- **주요 기여**:
  - BAP + QCASP + TSP-T를 단일 MILP로 통합 (3문제 동시 최적화)
  - Column generation 기반 해법으로 대형 인스턴스 대응
  - 세 문제 간 연결 제약 구조 정립
  - 순차 최적화 대비 11~19% 비용 절감
  - 50척 이상 인스턴스는 column generation 없이 1,000초 이상 소요

### [JOINT-4] Buhrkal, Zuglian, Ropke, Larsen & Lusby (2011)
- **제목**: "Models for the Discrete Berth Allocation Problem: A Computational Comparison"
- **저자**: Buhrkal, K., Zuglian, S., Ropke, S., Larsen, J., Lusby, R.
- **학술지**: Transportation Research Part E
- **연도**: 2011
- **Volume**: Vol. 47(4), pp. 444-452
- **DOI**: 10.1016/j.tre.2010.11.016
- **주요 기여**:
  - 이산 BAP의 세 정식화(time-indexed, arc-flow, sequence-based) 계산 성능 비교
  - Time-indexed formulation이 LP relaxation 가장 강함
  - Sequence-based formulation이 변수 수 가장 적어 대규모 근사해에 유리
  - 통합 BAP+TSP-T 모델의 BAP 컴포넌트 선택 지침 제공

---

## 11. 다중 예인선 배정 (Multi-tug Assignment)

### [MULTI-2] Petris, Agra & Rodrigues (2022/2024)
- **제목**: "Bi-objective dynamic tugboat scheduling with speed optimization under stochastic and time-varying service demands"
- **저자**: Petris, M., Agra, A., Rodrigues, F. (PSA Marine, Singapore 연계)
- **연도**: 2022 (선행 연구) / 2024 (확장판)
- **주요 기여**:
  - Receding Horizon MILP: 매 시간 단계에서 미래 window 내 요청을 재최적화
  - 이중 목적: 예인 대기 비용 최소화 + 연료 소비 최소화
  - 속도 최적화: 예인선 이동 속도가 결정 변수
  - Anticipatory Approximate Dynamic Programming(AADP)으로 미래 불확실성 처리
  - Gang scheduling 개념 적용: 다중 예인선 동기화 실시간 처리

---

## 12. AIS 데이터 및 항로 추출

### [AIS-1] Chen, Liu & Wang (2019)
- **제목**: "Port area traffic flow analysis based on AIS data"
- **저자**: Chen, X., Liu, Y., Wang, C.
- **학술지**: Ocean Engineering
- **연도**: 2019
- **Volume**: Vol. 186, Article 106077
- **DOI**: 10.1016/j.oceaneng.2019.106077
- **주요 기여**:
  - AIS 데이터에서 항구 내 선박 이동 경로 추출 방법론
  - SOG 필터링 → DBSCAN 클러스터링 → 항로 그래프 구성 파이프라인
  - 항로 중심선(centerline) 자동 추출 알고리즘
  - Dijkstra 최단 경로를 예인선 이동 시간 행렬 구성에 적용

---

## 요약 통계 (업데이트)

| 카테고리 | 논문 수 |
|----------|---------|
| Tugboat Scheduling (TSP-T) | 3 |
| VRPTW | 5 |
| Berth Allocation (BAP) | 6 |
| Harbor Traffic Management (HVTM) | 4 |
| Fuel / Speed Optimization | 2 |
| Multi-objective Optimization | 1 |
| Complexity Theory | 2 |
| Chance-Constrained Programming (CCP) | 5 |
| Rolling Horizon / MPC (RHO) | 4 |
| **Joint BAP + TSP-T 통합** | **4** |
| **Multi-tug Assignment** | **1** |
| **AIS 데이터 및 항로 추출** | **1** |
| **합계** | **38** |

---

*이 참고문헌 목록은 `mathematical_formulation.md` 및 `joint_optimization.md`에서 인용된 논문들의 메타정보를 담는다. DOI를 통해 각 논문에 직접 접근할 수 있다. 마지막 업데이트: 2026-03-20.*