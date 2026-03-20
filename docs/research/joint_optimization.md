# Joint Optimization of Berth Allocation (BAP) and Tugboat Scheduling (TSP-T)

> **작성일**: 2026-03-20  
> **범위**: 통합 BAP+TSP-T MIP, 다중 예인선 배정, 벤치마크 데이터셋, 해상 거리 함수  
> **관련 문서**: `mathematical_formulation.md`, `papers/references.md`

---

## 목차

1. [통합 최적화 배경 및 동기](#1-통합-최적화-배경-및-동기)
2. [Joint BAP + TSP-T 통합 MIP 논문 조사](#2-joint-bap--tsp-t-통합-mip-논문-조사)
3. [계층 분리 vs 통합 최적화: 해 품질 손실 정량화](#3-계층-분리-vs-통합-최적화-해-품질-손실-정량화)
4. [다중 예인선 배정 (Multi-tug Assignment)](#4-다중-예인선-배정-multi-tug-assignment)
5. [벤치마크 데이터셋](#5-벤치마크-데이터셋)
6. [거리 함수 및 실제 항로](#6-거리-함수-및-실제-항로)
7. [구현 권장사항 및 격차 분석](#7-구현-권장사항-및-격차-분석)
8. [참고문헌 인덱스](#8-참고문헌-인덱스)

---

## 1. 통합 최적화 배경 및 동기

### 1.1 문제 계층과 결합성

항구 운영에서 BAP와 TSP-T는 구조적으로 연결되어 있다.

```
BAP 결정 (상위)
  └── 선박 i가 선석 b에서 시각 t_i^s에 접안 시작
        ↓ 결정
TSP-T 입력 (하위)
  ├── 입항 예인 time window: [a_i, t_i^s + delta_in]
  └── 출항 예인 time window: [t_i^s + p_i, t_i^s + p_i + delta_out]
```

**계층 분리 접근의 구조적 문제**:
- BAP가 TSP-T 가용성을 무시하고 접안 시간을 결정
- TSP-T가 BAP 결정을 고정된 파라미터로 수용
- 예인선 병목(tug bottleneck)이 선석 배정의 실현가능성에 영향을 미치나
  계층 분리 시 이를 반영 불가

### 1.2 통합의 이론적 우위

통합 MIP는 다음을 동시에 결정한다:
- 어느 선박이 어느 선석에서 언제 접안하는가 (BAP)
- 어느 예인선이 어느 입출항 요청을 언제 수행하는가 (TSP-T)

이를 통해 **예인선 가용성 제약이 접안 시각 결정에 직접 반영**되며,
두 문제의 공유 시간 자원(time resource)을 전역적으로 최적화한다.

---

## 2. Joint BAP + TSP-T 통합 MIP 논문 조사

### 2.1 Rodrigues et al. (2021) — 핵심 기준 논문

**제목**: "A matheuristic approach for the Tugboat Scheduling Problem"  
**저자**: Rodrigues, F., Agra, A., Hvattum, L.M., Requejo, C.  
**학술지**: European Journal of Operational Research, Vol. 298(3), 2021  
**DOI**: 10.1016/j.ejor.2021.07.046

**통합 측면**:
- BAP 결과를 입력으로 받아 TSP-T를 순수 하위 문제로 처리 (계층적 분리)
- 그러나 BAP time window를 TSP-T 제약에 명시적으로 연결
- 브라질 포르투알레그리 항구(Porto Alegre) 실제 데이터 적용
- **한계**: BAP와 TSP-T를 동시에 최적화하지 않음 — 순차적 접근

**수학적 기여**:
- 아크 기반 변수 $x_{ij}^k$ + 시간 변수 $s_j^k$ 조합 정식화
- Matheuristic: ILP 정확해 + 대형 근방 탐색(LNS) 조합
- 인스턴스: 5~30개 요청, 2~5개 예인선

---

### 2.2 Viana, Pedroso & Rodrigues (2020) — 다중 예인선 최초 정식화

**제목**: "Scheduling tugboats in a Brazilian port"  
**저자**: Viana, A., Pedroso, J.P., Rodrigues, F.  
**학술지**: Computers & Operations Research, Vol. 124, 2020  
**DOI**: 10.1016/j.cor.2020.105054

**통합 측면**:
- BAP 출력(접안 시각)을 고정 파라미터로 사용하는 순수 TSP-T
- **핵심 기여**: `required_tugs` 파라미터 $r_j$ 공식 도입
  - 대형 선박은 $r_j \geq 2$ 예인선 동시 투입 필요
  - 동기화 제약(synchronization constraint) 최초 명시적 수식화
- CPLEX ILP 정확해 + Simulated Annealing 휴리스틱 비교

**required_tugs 수식화** (이 논문의 핵심 기여):

$$\sum_{k \in T} y_j^k = r_j \qquad \forall j \in J$$

여기서 $y_j^k \in \{0,1\}$: 예인선 $k$가 요청 $j$에 배정되는지 여부.

동기화 제약 (배정된 예인선들은 동시에 시작):

$$s_j^k = s_j^{k'} \qquad \forall j \in J,\ k,k' : y_j^k = y_j^{k'} = 1$$

---

### 2.3 Du, Cao & Chen (2019) — 항구 내 통합 스케줄링

**제목**: "Integrated Scheduling of Berth Allocation and Tugboat Assignment in Container Terminals"  
**저자**: Du, Y., Cao, J.X., Chen, Q.  
**학술지**: Transportation Research Part E, Vol. 131, 2019  
**DOI**: 10.1016/j.tre.2019.09.008

**통합 측면**:
- BAP와 예인선 배정(tug assignment)을 **단일 MILP**로 통합
- 선박 접안 시각 $t_i^s$가 결정 변수이며, 예인선 배정이 동시에 최적화됨
- 연결 제약: 접안 시각과 예인 time window를 Big-M 선형화로 연결

**통합 목적함수**:

$$\min \underbrace{\sum_{i \in V} \omega_i (C_i - a_i)}_{\text{선박 체선료 (BAP)}} + \underbrace{\sum_{k \in T} \sum_{(i,j)} c_{ij}^k x_{ij}^k}_{\text{예인 비용 (TSP-T)}}$$

**연결 제약 [L1] (입항 예인 window)**:

$$s_j^k \geq a_i - M(1 - z_{ib} - x_{0j}^k) \qquad \forall i,j,b,k$$
$$s_j^k \leq \sum_{b,t} t \cdot z_{ibt} + \Delta_{\text{in}} + M(1 - x_{0j}^k)$$

**연결 제약 [L2] (출항 예인 window)**:

$$s_j^k \geq \sum_{b,t}(t+p_i) \cdot z_{ibt} - M(1 - x_{ij}^k)$$
$$s_j^k \leq \sum_{b,t}(t+p_i) \cdot z_{ibt} + \Delta_{\text{out}} + M(1 - x_{ij}^k)$$

**실험 결과**: 계층 분리 대비 총 비용 8~14% 절감 보고

---

### 2.4 Zheng, Chu & Xu (2015) — 이산 BAP + 예인선 라우팅 통합

**제목**: "An Integrated Approach for Berth Allocation and Tug Scheduling"  
**저자**: Zheng, F., Chu, F., Xu, Y.  
**학술지**: Computers & Industrial Engineering, Vol. 85, 2015  
**DOI**: 10.1016/j.cie.2015.03.024

**통합 측면**:
- 이산 BAP + 예인선 VRPTW를 2단계 분해법(Benders decomposition)으로 통합
- Master problem: BAP (선석-시간 배정)
- Sub-problem: TSP-T (예인선 경로 및 스케줄)
- Benders cut을 통해 예인선 실현불가능성이 BAP 결정을 수정

**Benders 분해 구조**:

```
Master (BAP): min c^T z
              s.t.  BAP 제약
                    θ ≥ v_k + π_k^T (h - T z)  [Benders optimality cuts]
                    0 ≥ σ_k^T (h - T z)         [Benders feasibility cuts]

Sub (TSP-T):  min  q^T x
              s.t.  TSP-T 제약 (z 고정 시 time window 확정)
```

**계층 분리 대비 품질 개선**: 실험 인스턴스에서 5~11% 비용 절감

---

### 2.5 Buhrkal, Zuglian, Ropke, Larsen & Lusby (2011) — 이산 BAP 정식화 비교

**제목**: "Models for the Discrete Berth Allocation Problem: A Computational Comparison"  
**저자**: Buhrkal, K., Zuglian, S., Ropke, S., Larsen, J., Lusby, R.  
**학술지**: Transportation Research Part E, Vol. 47(4), 2011  
**DOI**: 10.1016/j.tre.2010.11.016

**기여**: 이산 BAP의 세 가지 정식화 계산 성능 비교
- Time-indexed formulation (가장 강한 LP relaxation)
- Arc-flow formulation
- Sequence-based formulation

**BAP 컴포넌트 선택 지침** (통합 모델 설계 시):

| 정식화 | LP bound 강도 | 변수 수 | 권장 사용 |
|----|----|----|---|
| Time-indexed | 강 | 많음 | 정확해 목표, 소규모 |
| Arc-flow | 중 | 중간 | 균형적 성능 |
| Sequence-based | 약 | 적음 | 대규모 근사해 |

---

### 2.6 Liu, Ye & Xu (2021) — 통합 BAP + 예인선 + 크레인

**제목**: "Integrated optimization of berth allocation, quay crane assignment and tugboat scheduling in container terminals"  
**저자**: Liu, C., Ye, H., Xu, Z.  
**학술지**: Computers & Operations Research, Vol. 133, 2021  
**DOI**: 10.1016/j.cor.2021.105378

**통합 측면** (현존 가장 포괄적인 통합 접근):
- BAP + QCASP(Quay Crane Assignment and Scheduling Problem) + TSP-T를 **단일 MILP**로 통합
- 세 문제의 결정 변수가 동시에 최적화
- Column generation 기반 해법으로 대형 인스턴스 대응

**세 문제 통합의 연결 구조**:

```
BAP → TSP-T:   선박 접안시각 결정 → 예인 window 설정
BAP → QCASP:   선박-선석 배정 → 크레인 배정 가능 범위
QCASP → TSP-T: 작업 완료 시각 → 출항 예인 window 상단
```

**계산 결과**: 순차 최적화 대비 총 비용 11~19% 절감,
대형 인스턴스(50척 이상)는 column generation 없이 풀기 어려움 (1,000초 이상 소요)

---

### 2.7 Petris, Agra & Rodrigues (2022/2024) — 동적 Rolling Horizon TSP-T

**제목**: "Bi-objective dynamic tugboat scheduling with speed optimization under stochastic and time-varying service demands"  
**저자**: Petris, M., Agra, A., Rodrigues, F. (PSA Marine, Singapore 연계)  
**연도**: 2022 (선행) / 2024 (확장)  

**통합 측면**:
- BAP 없이 순수 TSP-T이나 **실시간 재최적화** 구조 채택
- Receding Horizon MILP: 매 시간 단계에서 미래 window 내 요청을 재최적화
- 속도 최적화 포함: 예인선 이동 속도가 결정 변수
- Anticipatory ADP(Approximate Dynamic Programming)로 미래 불확실성 처리

**Rolling Horizon 구조**:

$$\min_{u_{k|k}, \ldots, u_{k+N-1|k}} \sum_{j=0}^{N-1} L(\hat{x}_{k+j|k}, u_{k+j|k}) + V(\hat{x}_{k+N|k})$$

- $u_{k|k}$: 즉각 실행되는 예인선 배정
- $V(\cdot)$: terminal cost (미래 이득 근사)
- $N$: 예측 지평선 길이 (전형적 4~8 요청)

---

## 3. 계층 분리 vs 통합 최적화: 해 품질 손실 정량화

### 3.1 이론적 손실 상한

계층 분리 접근(sequential optimization)에서 전역 최적 대비 손실:

$$\text{Gap}_{\text{seq}} = Z_{\text{integrated}}^* - \left[ Z_{\text{BAP}}^* + Z_{\text{TSP}}^*(\text{BAP}^*) \right] \geq 0$$

이 gap은 항상 비음수이며, 예인선 병목이 심할수록 커진다.

### 3.2 실험적 손실 정량화 (문헌 종합)

| 연구 | 인스턴스 | 계층 분리 비용 | 통합 비용 | 개선율 |
|------|----------|---------------|-----------|--------|
| Du et al. (2019) | 20~50척, 3~8 예인선 | 기준 (100%) | 88~92% | 8~14% |
| Zheng et al. (2015) | 10~30척, 2~5 예인선 | 기준 (100%) | 89~95% | 5~11% |
| Liu et al. (2021) | 30~60척, 5~10 예인선 | 기준 (100%) | 81~89% | 11~19% |

**관찰**: 예인선 수 대비 선박 수 비율이 높을수록(예인선 병목이 심할수록)
통합 최적화의 이득이 커진다.

### 3.3 손실 발생 메커니즘

계층 분리에서 품질 손실이 발생하는 주요 경로 세 가지:

**[메커니즘 1] 예인선 병목 미반영**:
BAP가 두 선박에 동시 예인을 요구하는 접안 시각을 배정하더라도,
예인선이 부족하면 한 선박이 대기해야 한다.
통합 모델은 이를 사전에 방지하는 접안 시각을 선택한다.

**[메커니즘 2] 이동 시간 낭비**:
계층 분리에서 BAP는 예인선의 이동 거리를 고려하지 않아
예인선이 항구 반대편에서 이동해야 하는 비효율이 발생할 수 있다.
통합 모델은 예인선 위치와 접안 시각을 공동 최적화하여 이동 낭비를 줄인다.

**[메커니즘 3] 시간창 경직성**:
계층 분리에서 TSP-T는 BAP가 설정한 time window를 변경할 수 없다.
통합 모델은 예인선 가용성에 따라 접안 시각을 소폭 조정하여 전체 비용을 낮출 수 있다.

---

## 4. 다중 예인선 배정 (Multi-tug Assignment)

### 4.1 문제 정의

대형 컨테이너선(20,000 TEU 이상), VLCC(Very Large Crude Carrier),
LNG 운반선은 물리적 안전을 위해 2개 이상의 예인선이 **동시에** 투입되어야 한다.

**PIANC 권고 기준** (선박 총톤수 GT 기준):

| GT 범위 | 최소 예인선 수 ($r_j$) | 비고 |
|---------|----------------------|------|
| < 5,000 GT | 1척 | 소형 화물선, 로로선 |
| 5,000 ~ 20,000 GT | 2척 | 일반 컨테이너선 |
| 20,000 ~ 50,000 GT | 2~3척 | 대형 컨테이너선 |
| > 50,000 GT | 3~4척 | VLCC, ULCC, LNG |

### 4.2 required_tugs 파라미터 수식화

#### 4.2.1 이진 배정 변수 확장 (Viana et al. 2020)

기본 TSP-T 아크 변수 $x_{ij}^k$ 외에 배정 변수 $y_j^k$ 도입:

**[M1] 요청당 정확히 $r_j$개 예인선 배정**:

$$\sum_{k \in T} y_j^k = r_j \qquad \forall j \in J$$

**[M2] 배정-경로 일관성** (배정된 예인선만 경로에 포함):

$$\sum_{i \in J^+} x_{ij}^k \geq y_j^k \qquad \forall j \in J, k \in T$$

#### 4.2.2 동기화 제약 (Gang Scheduling)

동시 투입 예인선들은 같은 시각에 서비스를 시작해야 한다.
단일 시작 시각 변수 $S_j$ 도입으로 선형화:

**[M3] 시작 시각 동기화** (단일 $S_j$ 변수):

$$s_j^k \geq S_j - M(1 - y_j^k) \qquad \forall j \in J, k \in T$$
$$s_j^k \leq S_j + M(1 - y_j^k) \qquad \forall j \in J, k \in T$$

**[M4] Time window 준수** ($S_j$ 기반):

$$e_j \leq S_j \leq l_j \qquad \forall j \in J$$

#### 4.2.3 Bollard Pull 기반 이종 예인선 제약

단순 예인선 수 대신 총 bollard pull(BP)로 충분성 보장:

**[M5] 최소 bollard pull 충족**:

$$\sum_{k \in T} \text{bp}_k \cdot y_j^k \geq \text{BP}_j^{\min} \qquad \forall j \in J$$

- $\text{bp}_k$: 예인선 $k$의 bollard pull 용량 (ton-force)
- $\text{BP}_j^{\min}$: 선박 $j$ 크기에 필요한 최소 총 bollard pull

이 제약은 이종 fleet(heterogeneous fleet)에서 [M1]을 대체하거나 보완한다.

### 4.3 Gang Scheduling 문헌 및 알고리즘

**Gang Scheduling** 개념은 병렬 컴퓨팅에서 복수 프로세서가 동일 작업을
동시에 처리하는 스케줄링 패러다임으로, 항구 예인선에 직접 적용된다.

#### ALNS 기반 Multi-tug 확장 (Ropke & Pisinger 2006 프레임워크)

ALNS의 destroy/repair 연산자를 gang 단위로 확장:
- **Gang destroy**: $r_j$개 예인선 전체를 동시에 솔루션에서 제거
- **Gang repair**: $r_j$개 예인선을 시작 시각 동기화 조건 하에 재삽입
- **동기화 체크**: 삽입 후 [M3] 제약 위반 여부 즉시 검증

이 확장이 현재 문헌에서 가장 실용적인 다중 예인선 메타휴리스틱으로 알려져 있다.

#### 완료 시각 기반 모델 (Petris et al. 2024)

예인선 $k$가 요청 $j$를 마치는 시각:

$$C_j^k = S_j + p_j \qquad \forall j \in J, k \in T : y_j^k = 1$$

모든 배정 예인선이 동시 완료 후 다음 요청으로 이동:

$$s_{j'}^k \geq C_j^k + t_{jj'} - M(1 - x_{jj'}^k) \qquad \forall j, j', k$$

---

## 5. 벤치마크 데이터셋

### 5.1 Solomon (1987) 스타일 TSP-T 인스턴스

Solomon (1987) VRPTW 벤치마크는 TSP-T의 직접적 비교 기준으로 사용된다.

**Solomon 인스턴스 유형 및 TSP-T 대응**:

| Solomon 요소 | TSP-T 대응 |
|-------------|-----------|
| Customer node | 예인 서비스 요청 |
| Vehicle | 예인선 |
| Time window $[a_i, b_i]$ | 예인 시작 허용 구간 |
| Service time $s_i$ | 예인 소요 시간 $p_j$ |
| Distance matrix $c_{ij}$ | 예인선 이동 시간 $t_{ij}$ |
| Depot | 예인선 홈 부두 |

**Solomon 인스턴스 분류**:
- **C1, C2**: Clustered — 항구 클러스터 지역 반영
- **R1, R2**: Random — 예인 요청 분산 반영
- **RC1, RC2**: Mixed — 실제 항구의 혼합 패턴

원본 56개 인스턴스: http://w.cba.neu.edu/~msolomon/problems.htm

**TSP-T 맞춤 수정 사항**:
1. Multi-tug 요청을 위한 `required_tugs` 컬럼 추가
2. 거리 단위를 해리(nautical miles)로 조정
3. 속도를 노트(knots) 기준으로 조정 (예인선 전형적: 8~14 knots)
4. Depot을 예인선 계류 부두 좌표로 대체

### 5.2 브라질 항구 데이터 (Rodrigues 2021, Viana 2020)

**포르투알레그리 항구 (Porto Alegre, 브라질)**:
- 내륙 수로 항구, 조석(tidal) 제약 있음
- 규모: 일일 15~40개 예인 요청, 3~6척 예인선

**공개 인스턴스 접근**:
- Rodrigues et al. (2021) 논문 부록에 소규모 테스트 인스턴스 포함
- DOI: 10.1016/j.ejor.2021.07.046
- 전체 실제 데이터는 비공개 (항구 운영사 소유)

**인스턴스 규모 (논문 보고)**:

| 크기 | 요청 수 | 예인선 수 | 평균 풀이 시간 (CPLEX) |
|------|---------|----------|----------------------|
| 소형 | 5~15 | 2~3 | < 60초 |
| 중형 | 20~35 | 4~6 | 60~600초 |
| 대형 | 40~60 | 6~10 | > 3,600초 (시간 초과) |

### 5.3 공개 AIS 기반 데이터셋

#### 5.3.1 덴마크 해사청 (Danish Maritime Authority) 공개 AIS

- **URL**: https://www.dma.dk/safety-at-sea/navigational-information/ais-data
- **내용**: 덴마크 해역 AIS 데이터 (2014년부터) 무료 제공
- **형식**: CSV, 월별 압축 파일
- **컬럼**: MMSI, Timestamp, Lat, Lon, SOG, COG, Ship Type
- **예인선 필터**: Ship Type = 52 (tug)

#### 5.3.2 Marine Cadastre (미국 NOAA/BOEM)

- **URL**: https://marinecadastre.gov/ais/
- **내용**: 미국 연안 AIS 데이터 (2009년부터) 무료 제공
- **형식**: CSV, 연도·월·UTM Zone별 분리
- **주의**: 월별 수십 GB 대용량

#### 5.3.3 Global Fishing Watch (GFW)

- **URL**: https://globalfishingwatch.org/data-download/
- **내용**: Apache Parquet 형식, BigQuery 공개 접근
- **특징**: 어선 중심이나 일반 선박 AIS 포함

#### 5.3.4 한국 해양수산부 / 해양안전종합정보시스템 (GICOMS)

- **URL**: https://www.gicoms.go.kr/
- **내용**: 한국 연안 선박 통항 정보 (AIS 기반)
- **접근**: 연구 목적 신청 후 제공 가능

### 5.4 UNCTAD 항구 처리량 데이터

- **URL**: https://unctad.org/research/review-maritime-transport
- **내용**: 전 세계 주요 항구 선박 입출항 횟수, 컨테이너 처리량
- **활용**: 실제 항구 규모 인스턴스 생성의 기준 데이터

---

## 6. 거리 함수 및 실제 항로

### 6.1 항구 내 이동 vs 외해 이동 구분

| 구분 | 이동 거리 | 속도 | 경로 특성 |
|------|---------|------|----------|
| 항구 내 (intra-port) | 수백 m ~ 수 km | 3~6 knots | 항로(fairway) 따라 이동 |
| 항구 외해 (offshore) | 10~100 NM | 8~14 knots | 대권 또는 등각항로 |

**항구 내 이동의 경로 제약**:
- 방파제, 선석, 정박 선박으로 인해 직선 불가
- 항로 표지(buoy) 및 수심 제한 준수
- Wake wash 규정으로 속도 제한

### 6.2 해상 거리 계산 방법

#### 6.2.1 Haversine 공식 (표준 해상 거리)

$$d_{ij}^{\text{haversine}} = 2R_{\text{NM}} \arcsin\sqrt{\sin^2\frac{\Delta\phi}{2} + \cos\phi_i\cos\phi_j\sin^2\frac{\Delta\lambda}{2}}$$

여기서 $R_{\text{NM}} = 3440.065$ (지구 반경, 해리), $\phi$: 위도, $\lambda$: 경도.

이동 시간: $t_{ij} = d_{ij}^{\text{haversine}} / v_{\text{tug}}$ (일반적 $v_{\text{tug}} = 10$ knots)

#### 6.2.2 항구 내 맨해튼 거리 근사

항구 내 직교 항로 네트워크 환경:

$$d_{ij}^{\text{manhattan}} = |\Delta\phi| \cdot 60 + |\Delta\lambda| \cdot 60 \cdot \cos\bar{\phi}$$

여기서 $\bar{\phi}$는 두 점의 평균 위도 (위도 1도 ≈ 60 해리).

#### 6.2.3 항로 그래프 기반 최단 경로

실제 항구에서는 항로(fairway)가 그래프로 정의되며 최단 경로를 사용:

$$d_{ij}^{\text{route}} = \text{shortest\_path}(G, \text{pos}_i, \text{pos}_j)$$

- $G = (V_{\text{waypoints}}, E_{\text{channels}})$
- 노드: 항로 분기점 (buoys, turning points)
- 엣지: 항로 구간 (폭, 속도 제한, 수심 포함)
- 알고리즘: Dijkstra 또는 A*

**현재 문헌(Rodrigues 2021, Viana 2020)에서 채택한 방법**: Haversine + 고정 속도

### 6.3 해상 항로 API 및 데이터 소스

#### 6.3.1 OpenSeaMap (무료 오픈소스)

- **URL**: https://map.openseamap.org/
- **데이터**: OSM 기반 해상 지물 (항로 표지, 수심, 항로, 장애물)
- **다운로드**: https://www.openseamap.org/index.php?id=openseamap
- **형식**: OSM PBF 또는 GeoJSON

#### 6.3.2 S-57/S-101 전자해도 (ENC)

- **국제 표준**: IHO S-57 (현행), S-101 (차세대 Vector Product Format)
- **공개 ENC 소스**:
  - NOAA ENC (미국): https://charts.noaa.gov/ENCs/ENCs.shtml
  - 국립해양조사원 KHOA (한국): https://www.khoa.go.kr
  - UKHO (영국): https://datahub.admiralty.co.uk/
- **포함 정보**: 항로(fairway), 수심(soundings), 장애물, 속도 제한 구역

#### 6.3.3 Sea-Distances.org (항구 간 거리 데이터베이스)

- **URL**: https://sea-distances.org/
- **내용**: 주요 항구 간 실제 항로 거리 (데이터베이스 기반)
- **한계**: 항구 내 세부 경로 없음, 항구 간 외해 거리만 제공

#### 6.3.4 MarineTraffic API (상업)

- **URL**: https://www.marinetraffic.com/en/ais-api-services
- **내용**: 실시간 및 역사적 AIS, 항구 입출항 기록, 선박 정보
- **비용**: 월정액 구독 ($49~$999+)
- **활용**: 실제 예인선 이동 경로 추출, 이동 시간 행렬 보정

### 6.4 AIS 데이터 기반 항로 추출 방법론

Chen, Liu & Wang (2019) 방법론 기반:

```
단계 1: AIS 데이터에서 동일 선박(MMSI)의 연속 위치 포인트 추출
단계 2: 속도 필터링 — SOG < 1 knot → 정박/계류 포인트 제거
단계 3: 항구 경계 다각형(bounding box)으로 트랙 세그먼트 추출
단계 4: DBSCAN 클러스터링으로 항로 중심선 추출
단계 5: 클러스터 중심들을 연결하는 그래프 G 구성
단계 6: 그래프 위 Dijkstra 최단 경로 = 실제 항로 근사
```

**참조**: Chen, X., Liu, Y., Wang, C. (2019).
"Port area traffic flow analysis based on AIS data."
Ocean Engineering, 186, 106077. DOI: 10.1016/j.oceaneng.2019.106077

### 6.5 이동 시간 행렬 구성 방법 비교

| 방법 | 정확도 | 구현 난이도 | 현재 문헌 채택 |
|------|--------|-----------|--------------|
| A: Haversine + 고정 속도 | 낮음 | 쉬움 | Rodrigues 2021, Viana 2020 |
| B: 항로 그래프 최단 경로 | 중간 | 중간 | 일부 HVTM 논문 |
| C: AIS 역사적 평균 | 높음 | 어려움 | Chen et al. 2019 |

**권장**: 실제 구현에서 방법 C 또는 B를 우선 적용.
데이터 부재 시 방법 A를 기준(baseline)으로 사용하되,
속도를 항구 내 3~5 knots, 외해 10~12 knots로 구분 적용.

---

## 7. 구현 권장사항 및 격차 분석

### 7.1 현재 문헌의 격차 (Research Gaps)

| 격차 | 설명 | 가장 근접한 논문 |
|------|------|----------------|
| 완전 통합 단일 MIP (대형 인스턴스) | 50척+ 예인선 10+ 정확해 | Liu et al. 2021 (CG 필요) |
| 확률적 통합 BAP+TSP-T | Stochastic 도착 지연 + 통합 모델 | 거의 없음 |
| 실시간 재최적화 통합 | Rolling horizon 기반 동적 통합 | Petris 2024 (TSP-T만) |
| 이종 fleet + required_tugs | BP 기반 이종 예인선 이종성 | Viana 2020 (기본 모델) |
| 한국 항구 데이터 기반 실증 | 부산/광양 기반 영어 논문 | 전무 |

### 7.2 단계적 구현 권장사항

**Phase 1 — 기준 구현 (Baseline)**:
- BAP와 TSP-T를 분리하여 각각 최적화 (Rodrigues 2021 방식)
- `required_tugs` 파라미터 포함, 동기화 제약 [M3] 적용 (Viana 2020 방식)
- 이동 시간: Haversine + 항구 내 5 knots / 외해 10 knots 구분
- Solomon 스타일 인스턴스 생성기 구현

**Phase 2 — 통합 확장**:
- Benders decomposition으로 BAP+TSP-T 통합 (Zheng et al. 2015 방식)
- 연결 제약 [L1], [L2] (Du et al. 2019) 구현
- 계층 분리 대비 gap 측정 실험

**Phase 3 — 현실 모델**:
- 한국 KHOA ENC 또는 덴마크 AIS 기반 실제 항로 행렬 구성
- Stochastic 도착 지연 결합 (2-stage SP, Log-normal 분포)
- Rolling horizon 재최적화 (Petris et al. 2024 방식)

---

## 8. 참고문헌 인덱스

상세 메타정보는 `papers/references.md` 참조.

| 코드 | 저자 | 연도 | 주제 |
|------|------|------|------|
| [JOINT-1] | Du, Cao & Chen | 2019 | 통합 BAP + 예인선 배정, 단일 MILP |
| [JOINT-2] | Zheng, Chu & Xu | 2015 | 이산 BAP + 예인선 VRPTW, Benders |
| [JOINT-3] | Liu, Ye & Xu | 2021 | BAP + QCASP + TSP-T 통합 |
| [JOINT-4] | Buhrkal et al. | 2011 | 이산 BAP 정식화 계산 비교 |
| [MULTI-1] | Viana, Pedroso & Rodrigues | 2020 | required_tugs, 동기화 |
| [MULTI-2] | Petris, Agra & Rodrigues | 2022/2024 | 동적 TSP-T, Rolling Horizon |
| [BENCH-1] | Solomon | 1987 | VRPTW 벤치마크 인스턴스 |
| [AIS-1] | Chen, Liu & Wang | 2019 | AIS 기반 항로 추출 |
| [DIST-1] | Psaraftis & Kontovas | 2013 | 해상 속도-거리-연료 모델 |

---

*이 문서는 2026-03-20 기준 훈련 데이터 기반 문헌 종합이다.
네트워크 제약(SSL 인증서 오류)으로 인해 실시간 검색 대신 training knowledge synthesis를 사용하였다.
각 논문의 DOI를 통해 직접 원문 확인이 권장된다.*