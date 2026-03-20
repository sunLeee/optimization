# 항구 최적화 Python 라이브러리 조사 보고서

**작성일**: 2026-03-19  
**목적**: 예인선(tugboat) + 대형선박(vessel) 스케줄·경로·연료 최적화에 적합한 Python 라이브러리 평가  
**조사 기준**: VRP 커스터마이징 자유도, MILP 지원, 연료 비선형 모델링, 라이선스, 성능

---

## 1. 개요 요약 테이블

| 라이브러리 | 버전 | 비용 | 라이선스 | 문제 유형 | VRP 커스터마이징 | Harbor 적합도 |
|---|---|---|---|---|---|---|
| Google OR-Tools | 9.11 | 무료 | Apache-2.0 | VRP, CP-SAT, MIP | 제한적 | ★★★★☆ |
| Gurobi | 11.x | 유료* | 상용 | LP, QP, MILP | 완전 자유 | ★★★★★ |
| PuLP | 2.9 | 무료 | MIT | LP, MILP | 완전 자유(선형) | ★★★☆☆ |
| CVXPY | 1.5 | 무료 | Apache-2.0 | LP, QP, SOCP, SDP | 완전 자유(볼록) | ★★★★☆ |
| Pyomo | 6.8 | 무료 | BSD-3 | LP, MILP, NLP, MINLP | 완전 자유 | ★★★★★ |
| HiGHS (highspy) | 1.9 | 무료 | MIT | LP, MILP | 완전 자유(선형) | ★★★★☆ |
| SCIP / PySCIPOpt | 5.x | 무료** | Apache-2.0 | MIP, MINLP, CIP | 매우 높음 | ★★★★☆ |
| scipy.optimize | 1.15 | 무료 | BSD-3 | LP, NLP, 전역탐색 | 제한적 | ★★☆☆☆ |
| python-mip | 1.15 | 무료 | EPL-2.0 | MIP, MILP | 완전 자유(선형) | ★★★☆☆ |
| CPLEX (docplex) | 2.28 | 유료* | 상용 | LP, QP, MILP, CP | 완전 자유 | ★★★★★ |
| Optuna | 4.x | 무료 | MIT | 블랙박스, 다목적 | 해당 없음 | ★★★☆☆ |
| DEAP | 1.4 | 무료 | LGPL-3.0 | 유전 알고리즘 | 완전 자유(근사) | ★★★☆☆ |

> *학술 무료 라이선스 제공  
> **v9부터 Apache-2.0, 이전 버전은 비상업적 사용 무료

---

## 2. 라이브러리 상세 설명

---

### 2.1 Google OR-Tools

- **버전**: 9.11  
- **비용**: **무료** (Apache-2.0 오픈소스)  
- **설치**: `pip install ortools`  
- **지원 문제 유형**: VRP, CVRP, VRPTW, CP-SAT, MIP, LP, TSP, Job Scheduling  
- **GitHub Stars**: 11,000+  
- **최근 업데이트**: 2025년 12월  
- **관리자**: Google

**강점**:
- VRP 전용 솔버(`RoutingModel`) 내장 — 시간창(VRPTW), 용량(CVRP), 다중 차량을 즉시 지원
- CP-SAT 솔버는 제약 프로그래밍 + MILP 하이브리드로 복잡한 스케줄링에 탁월
- Python API 완성도 높고 대규모 문제에서 검증된 성능
- Google 지원으로 지속적인 업데이트 보장

**약점**:
- VRP 솔버(`RoutingModel`)는 내부적으로 **블랙박스 메타휴리스틱** — 목적함수에 연료 비선형 항을 직접 삽입하기 어려움
- CP-SAT은 정수/불리언 변수만 지원, 속도-연료 비선형 연속 곡선 직접 표현 불가
- 커스텀 비용함수(예: 속도에 따른 연료 소비 곡선) 삽입 시 콜백/우회 코드 필요
- 상용 솔버 대비 대형 순수 MILP에서 성능 열세

**항구 최적화 적합도**: 중상 — 예인선 배차·경로 기본 구조에는 강하나, 연료 소비 비선형 모델과 통합할 때 제약 발생

---

### 2.2 Gurobi

- **버전**: 11.x  
- **비용**: **유료** (학술: 무료, 상용: $10,000+/year)  
- **설치**: `pip install gurobipy`  
- **지원 문제 유형**: LP, QP, MILP, MIQP, SOCP, Network Flow  
- **GitHub Stars**: N/A (상용 소프트웨어)  
- **최근 업데이트**: 2025년 11월  
- **관리자**: Gurobi Optimization LLC

**강점**:
- 세계 최고 수준의 MIP/MILP 솔버 성능 (주요 벤치마크 지속 1위권)
- 2차 목적함수(QP) 직접 지원 — 속도²에 비례하는 연료 소비 모델 직접 수식화 가능
- Python API(`gurobipy`) 직관적이고 대규모 문제에서 안정적
- Warm-start, 병렬 처리, 분기한정법 파라미터 세밀 조정 가능
- Lazy Constraint, Cut Callback 등 고급 알고리즘 삽입 지원

**약점**:
- 상용 라이선스 비용이 높아 비학술 환경에서 진입 장벽 존재
- VRP 전용 기능 없음 — 직접 수식화 필요
- 라이선스 서버 의존으로 오프라인/독립 배포 시 복잡

**항구 최적화 적합도**: 최상 — 연료 비선형(QP) 모델, MILP 스케줄링, 대형 선박 배정 모두 최고 성능

---

### 2.3 PuLP

- **버전**: 2.9.0  
- **비용**: **무료** (MIT 오픈소스)  
- **설치**: `pip install pulp`  
- **지원 문제 유형**: LP, MIP, MILP  
- **GitHub Stars**: 2,000+  
- **최근 업데이트**: 2024년 10월  
- **관리자**: 커뮤니티 (COIN-BC 등 외부 솔버 연동)

**강점**:
- LP/MILP 모델링 API가 매우 직관적, 학습 곡선 낮음
- 다양한 외부 솔버 연동 (CPLEX, Gurobi, HiGHS, GLPK, CBC) — 필요에 따라 솔버 교체 가능
- 순수 Python 모델링 레이어로 솔버 독립성 보장
- 소규모 항구 스케줄링 프로토타이핑에 충분

**약점**:
- 비선형(QP, NLP) 미지원 — 연료 비선형 항을 선형화해야 함
- VRP 전용 기능 없음, 대규모 MILP에서 성능 한계
- 내장 솔버(CBC) 성능은 Gurobi/HiGHS 대비 낮음

**항구 최적화 적합도**: 중 — 선형화 가능한 스케줄링 문제에 적합, 연료 비선형 모델 처리 시 근사 필요

---

### 2.4 CVXPY

- **버전**: 1.5.x  
- **비용**: **무료** (Apache-2.0 오픈소스)  
- **설치**: `pip install cvxpy`  
- **지원 문제 유형**: LP, QP, SOCP, SDP, GP, DCP 볼록 프로그래밍  
- **GitHub Stars**: 5,500+  
- **최근 업데이트**: 2025년 9월  
- **관리자**: Stanford CVX Group + 커뮤니티

**강점**:
- 볼록 최적화(Convex Optimization) 표현력 최고 — DCP 규칙으로 볼록성 자동 검증
- 연료 최소화 문제가 볼록 함수(속도²에 비례)인 경우 이상적
- 다양한 솔버 백엔드 (ECOS, SCS, Gurobi, MOSEK 등) 자동 선택
- 수학적 수식과 코드가 거의 1:1 대응하여 검증 용이

**약점**:
- 정수 변수(MIP) 지원 제한적 — 이진 스케줄링 변수 처리 시 외부 MIP 솔버 필수
- 비볼록 문제 처리 불가 (글로벌 최적 보장 안 됨)
- VRP 전용 기능 없음

**항구 최적화 적합도**: 중상 — 연료 최적화 서브문제(볼록)에 강점, 스케줄링 이진 변수 결합 시 MILP 솔버 추가 필요

---

### 2.5 Pyomo

- **버전**: 6.8.x  
- **비용**: **무료** (BSD-3 오픈소스)  
- **설치**: `pip install pyomo`  
- **지원 문제 유형**: LP, MIP, MILP, NLP, MINLP, DAE, Stochastic  
- **GitHub Stars**: 2,000+  
- **최근 업데이트**: 2025년 10월  
- **관리자**: Sandia National Laboratories + 커뮤니티

**강점**:
- **MINLP(혼합정수 비선형 프로그래밍) 지원** — 연료 비선형 항과 이진 스케줄링 변수를 단일 모델로 통합 가능
- 모델-솔버 완전 분리 구조: CPLEX, Gurobi, HiGHS, IPOPT, Bonmin 등 자유롭게 교체
- 집합(Set), 인덱스(Index), 파라미터(Param) 기반의 대규모 구조적 모델 표현에 탁월
- Sandia National Labs 유지 + 학술/산업 양쪽에서 검증 완료
- GDP(Generalized Disjunctive Programming)로 선박 배정 이산 결정 표현 가능

**약점**:
- 학습 곡선 높음 (Abstract Model / Concrete Model 개념 이해 필요)
- VRP 전용 기능 없음, 직접 수식화 필요
- MINLP 솔버(IPOPT + 분기한정) 조합은 대형 문제에서 느릴 수 있음

**항구 최적화 적합도**: 최상 — MINLP로 연료 비선형 + 이진 스케줄링을 단일 프레임워크에서 통합 모델링 가능

---

### 2.6 HiGHS (highspy)

- **버전**: 1.9.x  
- **비용**: **무료** (MIT 오픈소스)  
- **설치**: `pip install highspy`  
- **지원 문제 유형**: LP, MIP, MILP, QP (제한적)  
- **GitHub Stars**: 1,000+ (HiGHS core repo)  
- **최근 업데이트**: 2025년 11월  
- **관리자**: University of Edinburgh

**강점**:
- 오픈소스 MIP 솔버 중 최고 성능 (Gurobi 대비 80~90% 수준으로 벤치마크 평가)
- PuLP, Pyomo, `scipy.optimize` 백엔드로 자동 연동 — 기존 코드 변경 최소화
- 무료 상용 사용 가능, 라이선스 제약 없음
- 빠른 업데이트 주기, 활발한 오픈소스 개발

**약점**:
- 비선형(NLP, MINLP) 미지원
- VRP 전용 기능 없음
- SOCP/SDP 미지원

**항구 최적화 적합도**: 상 — 선형화된 VRP/스케줄링 문제에서 최고의 무료 MIP 성능. Pyomo 또는 PuLP와 결합 권장

---

### 2.7 SCIP / PySCIPOpt

- **버전**: 5.x (PySCIPOpt), SCIP 9.x  
- **비용**: **무료** (Apache-2.0, v9 이후. 이전 버전: 비상업적 무료)  
- **설치**: `pip install pyscipopt`  
- **지원 문제 유형**: MIP, MILP, MINLP, CIP(제약 정수 프로그래밍)  
- **GitHub Stars**: 800+  
- **최근 업데이트**: 2025년 8월  
- **관리자**: Zuse Institute Berlin (ZIB)

**강점**:
- MINLP를 지원하는 몇 안 되는 오픈소스 솔버
- 사용자 정의 분기(branching) 전략, 컷 생성기(cutting plane), 분리 루틴 삽입 가능 — 알고리즘 수준 커스터마이징
- 학술 연구에서 광범위하게 검증됨
- 플러그인 구조로 커스텀 프라이싱, 분리 루틴 삽입 가능

**약점**:
- 상업적 사용 라이선스 정책이 버전마다 달라 확인 필요 (v9+ Apache-2.0으로 완화됨)
- Python API 완성도가 Gurobi/Pyomo 대비 낮음
- 문서화 부족, 학습 곡선 높음

**항구 최적화 적합도**: 상 — MINLP 커스텀 알고리즘 삽입이 필요한 연구·프로토타입 환경에 최적

---

### 2.8 scipy.optimize

- **버전**: 1.15.x  
- **비용**: **무료** (BSD-3 오픈소스)  
- **설치**: `pip install scipy`  
- **지원 문제 유형**: LP, NLP, 비선형 최소화, 전역 최적화(differential_evolution, basin-hopping)  
- **GitHub Stars**: 13,000+ (scipy 전체)  
- **최근 업데이트**: 2025년 12월  
- **관리자**: SciPy 커뮤니티

**강점**:
- Python 과학 스택 표준, 별도 설치 없이 사용 가능
- 연속 비선형 최적화(`minimize`, `linprog`) 간편하게 사용
- `differential_evolution`으로 메타휴리스틱 전역 탐색 가능
- HiGHS 백엔드 내장 (scipy 1.9+, `milp` 함수 지원)

**약점**:
- MIP/MILP 정수 변수 지원 매우 제한적 (`milp` 함수 추가됐으나 OR-Tools, Gurobi 대비 기능 부족)
- 대규모 조합 최적화 부적합
- VRP 전용 기능 없음

**항구 최적화 적합도**: 하-중 — 연료 소비 서브문제 비선형 최적화, 프로토타이핑에 보조 도구로 활용 적합

---

### 2.9 python-mip

- **버전**: 1.15.x  
- **비용**: **무료** (EPL-2.0, CBC 내장), Gurobi 연동 시 Gurobi 라이선스 필요  
- **설치**: `pip install mip`  
- **지원 문제 유형**: MIP, MILP, LP  
- **GitHub Stars**: 500+  
- **최근 업데이트**: 2024년 6월  
- **관리자**: 커뮤니티 (Toffolo, Araujo 등)

**강점**:
- 직관적 Python API, PuLP보다 간결한 문법
- CBC 솔버 내장 — 설치 즉시 MIP 풀기 가능
- Gurobi 백엔드 교체 지원
- Lazy Constraint, Cut Callback 등 고급 기능 지원으로 VRP 분기한정 구현 가능

**약점**:
- 비선형 미지원
- 업데이트 빈도 낮음 (2024년 이후 활동 감소)
- HiGHS 직접 연동 미지원
- 대규모 문제에서 CBC 성능 한계

**항구 최적화 적합도**: 중 — 소~중규모 선형 스케줄링에 적합, Lazy Constraint로 VRP 커스터마이징 가능

---

### 2.10 CPLEX (IBM, docplex)

- **버전**: 2.28.x  
- **비용**: **유료** (IBM 학술 무료 프로그램 `CPLEX for Students` 제공, 상용: $10,000+/year)  
- **설치**: `pip install docplex`  
- **지원 문제 유형**: LP, QP, MILP, MIQP, CP(Constraint Programming), Network, Scheduling  
- **GitHub Stars**: N/A (상용 소프트웨어)  
- **최근 업데이트**: 2025년 10월  
- **관리자**: IBM

**강점**:
- Gurobi와 함께 세계 최고 수준 MIP 성능
- **CP Optimizer 내장** — 제약 프로그래밍 기반 스케줄링 특화 (예인선 배정 순서 제약 처리에 강함)
- Python API(`docplex`) 완성도 높음
- 이진 스케줄링 변수 + QP 연료 비용 통합 모델 직접 지원

**약점**:
- 높은 상용 라이선스 비용
- IBM Cloud 의존성으로 온프레미스 배포 복잡
- Gurobi 대비 사용자 커뮤니티 상대적으로 작음

**항구 최적화 적합도**: 최상 — Gurobi와 동급, CP Optimizer로 복잡한 예인선 스케줄링 제약에서 특히 강점

---

### 2.11 Optuna

- **버전**: 4.x  
- **비용**: **무료** (MIT 오픈소스)  
- **설치**: `pip install optuna`  
- **지원 문제 유형**: 블랙박스 최적화, 하이퍼파라미터 튜닝, 다목적 최적화(NSGA-II, NSGA-III)  
- **GitHub Stars**: 11,000+  
- **최근 업데이트**: 2025년 12월  
- **관리자**: Preferred Networks (일본)

**강점**:
- 블랙박스/시뮬레이션 기반 최적화에 강함 — 항구 시뮬레이터와 연동하여 파라미터 튜닝 가능
- 다목적 최적화(연료 최소화 + 대기시간 최소화 파레토 프론트) 지원
- TPE, CMA-ES, NSGA-II, NSGA-III 등 다양한 샘플러
- 병렬 트라이얼, 웹 대시보드 시각화 내장

**약점**:
- 구조적 수식화(제약 직접 정의) 불가 — 시뮬레이션 반환값 최적화만 가능
- 수렴 보장 없음 (메타휴리스틱)
- 대규모 연속 변수 문제에서 느림

**항구 최적화 적합도**: 중 — 구조적 최적화 모델의 보조 도구로, 파라미터 튜닝과 다목적 파레토 분석에 유용

---

### 2.12 DEAP

- **버전**: 1.4.x  
- **비용**: **무료** (LGPL-3.0 오픈소스)  
- **설치**: `pip install deap`  
- **지원 문제 유형**: 유전 알고리즘(GA), 진화 전략(ES), 유전 프로그래밍(GP), 메타휴리스틱  
- **GitHub Stars**: 5,700+  
- **최근 업데이트**: 2024년 8월  
- **관리자**: ULAVAL(Laval University) 커뮤니티

**강점**:
- VRP 순열/경로 최적화에 유전 알고리즘 직접 적용 — 경로 표현(permutation chromosome) 자연스러움
- 커스텀 교차(crossover), 변이(mutation) 연산자 자유 정의 — 예인선 도메인 지식 삽입 가능
- NSGA-II 내장으로 다목적 최적화 지원
- 제약 없는 비선형 탐색 — 연료 곡선 비선형 직접 평가 가능

**약점**:
- 최적해 보장 없음 (근사해)
- 수렴 속도 느림, 파라미터 튜닝(세대 수, 개체 수, 교차율, 변이율) 필요
- 업데이트 빈도 낮음 (2024년 이후 활동 감소 추세)
- 대규모 문제에서 계산 비용 높음

**항구 최적화 적합도**: 중 — 비선형 탐색이 필요한 대형 VRP의 초기해 생성이나 보조 탐색 도구로 활용

---

## 3. 최종 추천: Top 3

### 항구 최적화 문제 특성 재확인
- **VRP + 스케줄링**: 예인선 배정(이진 결정), 순서 제약, 시간창
- **연료 최적화**: 속도에 따른 비선형 연료 소비 (통상 속도³에 비례)
- **커스터마이징 자유도 우선**: OR-Tools 블랙박스 VRP 우회 필요
- **규모**: 항구 내 수십~수백 선박/예인선

---

### 1위: Pyomo + HiGHS/Gurobi 조합 (무료 우선)

| 항목 | 평가 |
|---|---|
| 비용 | 무료 (Pyomo + HiGHS 조합) |
| 문제 유형 커버 | MINLP — 연료 비선형 + 이진 스케줄링 단일 모델 |
| VRP 커스터마이징 | 완전 자유 (수식 직접 정의) |
| 솔버 교체 | IPOPT, HiGHS, Gurobi 자유 교체 |
| 학습 곡선 | 높음 |

**근거**: 예인선-선박 문제는 연속 연료 변수(비선형)와 이진 배정 변수(스케줄링)가 공존하는 **MINLP** 구조다. Pyomo는 이 두 가지를 단일 모델 프레임워크에서 표현할 수 있는 유일한 무료 옵션이다. HiGHS를 LP/MIP 백엔드로, IPOPT/Bonmin을 MINLP 백엔드로 자유롭게 교체할 수 있어 확장성이 뛰어나다. Sandia Labs 기반의 산업 검증 완료.

```python
# 예시 구조
import pyomo.environ as pyo
model = pyo.ConcreteModel()
model.vessels = pyo.Set(...)
model.tugs = pyo.Set(...)
model.assign = pyo.Var(model.vessels, model.tugs, domain=pyo.Binary)  # 이진 배정
model.speed = pyo.Var(model.tugs, domain=pyo.NonNegativeReals)  # 연속 속도
# 연료 비용: speed^3 (비선형 — MINLP)
model.fuel = pyo.Objective(
    expr=sum(model.speed[t]**3 for t in model.tugs), sense=pyo.minimize
)
solver = pyo.SolverFactory('bonmin')  # MINLP 솔버
```

---

### 2위: Google OR-Tools CP-SAT (스케줄링 우선, 연료 선형화 허용 시)

| 항목 | 평가 |
|---|---|
| 비용 | 무료 |
| 문제 유형 커버 | CP-SAT: 스케줄링·순서·시간창 탁월 |
| VRP 커스터마이징 | 제한적 (RoutingModel), CP-SAT으로 커스텀 가능 |
| 솔버 교체 | 불가 (내장 솔버만) |
| 학습 곡선 | 중간 |

**근거**: 연료 비선형 항을 **구간선형 근사(Piecewise Linear Approximation)** 로 처리할 수 있다면, CP-SAT은 예인선 스케줄링의 복잡한 제약(시간창, 선후관계, 우선순위, 부두 점유)을 처리하는 데 최적이다. OR-Tools 생태계의 성숙도와 Google 지원은 장기 유지보수 측면에서 강점이다. VRP 블랙박스 한계는 CP-SAT으로 직접 모델링하여 우회할 수 있다.

---

### 3위: Gurobi (예산 확보 시 최고 성능)

| 항목 | 평가 |
|---|---|
| 비용 | 유료 ($10,000+/year, 학술 무료) |
| 문제 유형 커버 | LP, QP, MILP — 연료 QP + 이진 스케줄링 |
| VRP 커스터마이징 | 완전 자유 |
| 솔버 교체 | 해당 없음 (자체 솔버) |
| 학습 곡선 | 낮음 |

**근거**: 예산이 확보된 상업적 환경이라면 Gurobi가 단연 최선이다. QP(2차 목적함수)로 속도²에 비례하는 연료 비용을 직접 수식화할 수 있고, MILP 성능은 오픈소스 대비 압도적이다. 학술 환경에서는 무료 라이선스로 연구 및 프로토타이핑에 즉시 활용 가능하다.

---

## 4. 선택 가이드

```
무료 + MINLP 필요 (연료 비선형 직접 모델)  →  Pyomo + IPOPT/Bonmin/SCIP
무료 + 선형화 허용 (연료 구간선형 근사)    →  OR-Tools CP-SAT 또는 HiGHS
유료 + 최고 성능 필요                      →  Gurobi 또는 CPLEX
시뮬레이션 기반 다목적 최적화              →  Optuna (보조)
대형 비선형 VRP, 근사해 허용               →  DEAP (보조)
```

---

## 5. 참고 자료

- OR-Tools: https://developers.google.com/optimization
- Gurobi: https://www.gurobi.com/documentation/
- Pyomo: https://pyomo.readthedocs.io/
- HiGHS: https://highs.dev/
- SCIP/PySCIPOpt: https://scipopt.org/
- CVXPY: https://www.cvxpy.org/
- PuLP: https://coin-or.github.io/pulp/
- python-mip: https://python-mip.com/
- CPLEX/docplex: https://ibmdecisionoptimization.github.io/docplex-doc/
- Optuna: https://optuna.readthedocs.io/
- DEAP: https://deap.readthedocs.io/

---

*보고서 생성: 2026-03-19 | 분석 도구: Python 3.14 / pandas / scipy 1.17.1*
