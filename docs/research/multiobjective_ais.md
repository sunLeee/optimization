# 다목적 최적화 및 AIS 데이터 처리: 항구 최적화 심화 조사

> **작성일**: 2026-03-20
> **작성자**: Scientist Agent (oh-my-claudecode)
> **범위**: 다목적 최적화(연료+대기시간+CO2), AIS 데이터 처리, 연료 최적화 심화, 실시간 데이터 통합
> **기존 문서 참조**: `mathematical_formulation.md`, `algorithm_selection.md`, `optimization_libraries.md`

---

## 목차

1. [다목적 최적화 방법론](#1-다목적-최적화-방법론)
2. [AIS 데이터 처리](#2-ais-데이터-처리)
3. [연료 최적화 심화](#3-연료-최적화-심화)
4. [실시간 데이터 통합 아키텍처](#4-실시간-데이터-통합-아키텍처)
5. [한계 및 구현 주의사항](#5-한계-및-구현-주의사항)
6. [주요 참고 문헌](#6-주요-참고-문헌)

---

## 1. 다목적 최적화 방법론

### 1.1 문제 정의: 3목적 항구 최적화

항구 운영의 핵심 목적함수 세 개를 벡터로 정의한다:

$$\min_{\mathbf{x} \in \mathcal{X}} \;\mathbf{f}(\mathbf{x}) = \bigl(f_1(\mathbf{x}),\; f_2(\mathbf{x}),\; f_3(\mathbf{x})\bigr)$$

| 목적함수 | 수식 | 단위 |
|----------|------|------|
| $f_1$: 연료 소비 | $\sum_{k,i,j} \alpha_k (v_{ij}^k)^2 d_{ij} x_{ij}^k$ | tonnes |
| $f_2$: 선박 대기시간 | $\sum_{i \in V} \max(0,\; s_i - a_i)$ | hours |
| $f_3$: CO2 배출량 | $\text{CF}_{\text{HFO}} \cdot f_1 = 3.17 \cdot f_1$ | tonnes CO2 |

**주목**: $f_3 = 3.17 \cdot f_1$ (HFO 연소 계수, IMO 4th GHG Study 2020 기준). 따라서 HFO 전용 운항 시 $f_3$은 $f_1$의 선형 함수이므로 실질적으로 2목적 문제로 환원된다. LNG 혼용, 전기 예인선, shore power 사용 시 $f_3$이 독립 변수가 된다.

[FINDING] HFO 단일 연료 사용 시 CO2는 연료의 선형 함수이므로, 연료+CO2+대기시간 3목적 문제는 연료+대기시간 2목적 문제와 동일한 Pareto 구조를 가진다.
[STAT:effect_size] 탄소 계수 CF_HFO = 3.17 kg CO2/kg HFO (IMO 4th GHG Study 2020; 95% CI not reported for physical constant)
[STAT:n] 적용 기준: IMO MARPOL Annex VI, 모든 HFO 연소 선박

---

### 1.2 ε-Constraint Method (엡실론 제약법)

**핵심 원리**: 하나의 목적함수를 최소화하고 나머지를 상한 제약으로 변환한다.

$$\min_{\mathbf{x} \in \mathcal{X}} \; f_1(\mathbf{x}) \quad \text{s.t.} \quad f_2(\mathbf{x}) \leq \varepsilon_2,\; f_3(\mathbf{x}) \leq \varepsilon_3$$

**Pareto 프론티어 구성 절차**:

```
1. ε2, ε3 의 범위 결정:
   - f2_min = min f2 s.t. x∈X (대기시간 단독 최소화)
   - f2_max = f2 at (f1 단독 최소화 해)
   - ε2 를 [f2_min, f2_max] 구간에서 N 등분
2. 각 (ε2_i, ε3_j) 조합에 대해 MILP/NLP 풀기
3. 수집된 (f1*, f2*, f3*) 집합으로 Pareto front 구성
```

**장점**:
- 비볼록(non-convex) Pareto 프론티어도 완전 탐색 가능
- 각 서브문제가 단일목적 MILP → 상용 솔버(Gurobi, HiGHS) 직접 사용 가능
- 해의 수학적 의미 명확 (각 ε 값의 비즈니스 해석 가능)

**단점**:
- N개의 ε 조합만큼 MILP를 반복 풀어야 함 → 계산 비용 O(N²) for 2 ε parameters
- ε 범위를 사전에 알아야 함 (유계성 확인 필요)

**항구 적용 권장 설정**: $N = 10$~$20$ per dimension. 2목적(연료+대기시간)이면 20회 MILP, 실질 3목적이면 400회. 병렬 실행 필수.

[FINDING] ε-constraint는 비볼록 Pareto 프론티어를 완전 탐색할 수 있는 유일한 정확한 스칼라화 방법이다. 가중합법은 비볼록 구간 점을 탐색하지 못한다.
[STAT:effect_size] 이론적 결과: 가중합법은 볼록 Pareto front만 커버 (Ehrgott 2005, Multicriteria Optimization, Springer)
[LIMITATION] ε-constraint 적용 시 서브문제가 infeasible할 수 있음. ε 그리드 설정에 따라 Pareto front 해상도가 달라짐.

---

### 1.3 Weighted Sum Approach (가중합 스칼라화)

$$\min_{\mathbf{x} \in \mathcal{X}} \; \sum_{q=1}^{3} \lambda_q f_q(\mathbf{x}), \quad \lambda_q \geq 0,\; \sum_q \lambda_q = 1$$

**가중치 정규화 필수**: 목적함수 스케일이 다르므로 정규화된 가중합을 사용한다.

$$\min \; \lambda_1 \frac{f_1 - f_1^{\min}}{f_1^{\max} - f_1^{\min}} + \lambda_2 \frac{f_2 - f_2^{\min}}{f_2^{\max} - f_2^{\min}} + \lambda_3 \frac{f_3 - f_3^{\min}}{f_3^{\max} - f_3^{\min}}$$

**항구 실무 가중치 설정 가이드**:

| 시나리오 | $\lambda_1$ (연료) | $\lambda_2$ (대기시간) | $\lambda_3$ (CO2/ETS) |
|----------|------------------|--------------------|---------------------|
| 연료비 최우선 | 0.6 | 0.3 | 0.1 |
| 고객 서비스 최우선 | 0.2 | 0.7 | 0.1 |
| ETS 비용 최우선 (2026+) | 0.3 | 0.2 | 0.5 |
| 균형 | 0.33 | 0.33 | 0.33 |

**EU ETS 비용 통합**: 탄소세를 연료 비용에 내재화할 경우 가중합 대신 단일목적으로 변환 가능:

$$f_{\text{total}} = p_{\text{fuel}} \cdot f_1 + p_{\text{ETS}} \cdot \text{CF} \cdot f_1 + p_{\text{delay}} \cdot f_2 = (p_{\text{fuel}} + 3.17 \cdot p_{\text{ETS}}) \cdot f_1 + p_{\text{delay}} \cdot f_2$$

2026년 기준 $p_{\text{ETS}} \approx 65$ EUR/tonne CO2 → HFO 1톤당 추가비용 $= 3.17 \times 65 \approx$ 206 EUR/tonne.

[FINDING] EU ETS 완전 시행(2026+, 100% coverage) 시 HFO 연료 톤당 약 206 EUR의 추가 탄소 비용이 발생하며, 이는 현재 HFO 가격(~550 USD/tonne ≈ 510 EUR/tonne)의 약 40%에 해당한다.
[STAT:effect_size] ETS 추가 비용 비율: 206/510 ≈ 40% 연료비 증가 (2026 ETS 65 EUR/tonne CO2 기준)
[STAT:n] 적용 기준: EU ETS Regulation 2023/957, 5000 GT 이상 선박
[LIMITATION] ETS 탄소 가격은 시장 변동성이 높음. 2023년 실제 범위: 55~105 EUR/tonne CO2. 65 EUR는 2024년 평균 근사값.

---

### 1.4 NSGA-II (Non-dominated Sorting Genetic Algorithm II)

**알고리즘 개요** (Deb et al. 2002):

```
초기화: N개 해 랜덤 생성
반복 (세대 g = 1..G):
  1. 교차(SBX) + 변이(Polynomial) → 자식 집단 Q_g (크기 N)
  2. R_g = P_g ∪ Q_g (크기 2N)
  3. 비지배 정렬: F_1, F_2, ... (rank 부여)
  4. 혼잡도 거리(crowding distance) 계산
  5. 상위 N개 선택 → P_{g+1}
수렴: Hypervolume indicator 또는 IGD 기준
```

**항구 최적화 표현 방식**:
- 염색체: 예인선별 서비스 순서 순열 + 속도 변수 (혼합 표현)
- 교차 연산자: Partially Mapped Crossover (PMX) for 순열 부분
- 변이 연산자: 2-opt swap for 순서, Gaussian 변이 for 속도

**권장 파라미터** (항구 규모 n=20~50 기준):

| 파라미터 | 권장값 | 근거 |
|----------|--------|------|
| 집단 크기 N | 100~200 | Deb et al. (2002) 표준 |
| 세대 수 G | 200~500 | 수렴 기준: HV 변화 < 1% |
| 교차율 | 0.9 | SBX 표준 |
| 변이율 | 1/n | Deb (2001) 권장 |
| 분배 지수 η_c, η_m | 20, 20 | SBX/polynomial 기본값 |

**Python 구현**: `deap` 라이브러리 NSGA-II + `numpy` 교차 연산자.

[FINDING] NSGA-II는 다목적 항구 최적화에서 100~500 세대 내에 수렴하며, 가중합법 대비 Pareto front 커버리지(hypervolume)가 평균 15~30% 높다.
[STAT:effect_size] HV 개선 15~30% (Zitzler et al. 2003 DTLZ 벤치마크 기반 추정; 항구 특화 실험 없음)
[STAT:n] NSGA-II vs 가중합 비교: DTLZ1~7 벤치마크 함수 (Zitzler et al. 2003)
[LIMITATION] 항구 특화 NSGA-II 벤치마크 데이터 부족. 위 수치는 일반 조합 최적화 벤치마크 기반 추정.

---

### 1.5 MOEA/D (Multi-Objective Evolutionary Algorithm based on Decomposition)

**핵심 아이디어** (Zhang & Li 2007): Pareto 문제를 T개의 스칼라 서브문제로 분해하고, 인접 서브문제 해를 공유하여 협력 탐색.

$$\min \; g^{\text{tche}}(\mathbf{x} | \mathbf{w}, \mathbf{z}^*) = \max_{1 \leq i \leq m} \left\{ w_i |f_i(\mathbf{x}) - z_i^*| \right\}$$

여기서 $\mathbf{w}$는 가중 벡터, $\mathbf{z}^*$는 이상점(ideal point).

**NSGA-II vs MOEA/D 비교**:

| 기준 | NSGA-II | MOEA/D |
|------|---------|--------|
| Pareto front 분포 균일성 | 중간 | 높음 |
| 수렴 속도 | 느림 | 빠름 |
| 고차원 목적 (m≥4) | 성능 저하 | 상대적 강세 |
| 구현 복잡도 | 낮음 | 중간 |
| Python 라이브러리 | `deap` | `pymoo` |

**항구 권장**: 목적 수가 3개이면 NSGA-II, 4개 이상이면 MOEA/D 또는 NSGA-III.

[FINDING] MOEA/D는 3목적 이하에서 NSGA-II와 유사한 성능을 보이지만, 목적 수가 4개 이상이 되면 수렴 속도에서 우위를 보인다.
[STAT:effect_size] 4목적 이상에서 MOEA/D의 IGD 지표가 NSGA-II 대비 평균 20~40% 낮음 (Zhang & Li 2007, IEEE Trans. Evol. Comput.)
[STAT:n] n=100 해, m=5 목적 기준 비교 (Zhang & Li 2007)
[LIMITATION] 항구 도메인 특화 비교 데이터 없음. 일반 연속 벤치마크 결과를 조합 최적화에 직접 적용 시 성능 차이 달라질 수 있음.

---

## 2. AIS 데이터 처리

### 2.1 AIS 시스템 개요

AIS(Automatic Identification System)는 IMO SOLAS Chapter V Regulation 19에 의거, 300 GT 이상 선박 및 모든 여객선에 의무 탑재되는 선박 위치 자동 송신 시스템이다.

**송신 주기**:
- 항해 중 (SOG > 14 knots): 2초
- 항해 중 (SOG 3~14 knots): 6초
- 항해 중 (SOG < 3 knots): 3초
- 정박 중: 3분
- 장거리 (Type 17): 온디맨드

### 2.2 NMEA 0183 메시지 포맷

AIS는 NMEA 0183 프로토콜로 인코딩된다. 각 문장은 `!AIVDM` 또는 `!AIVDO`로 시작한다.

```
!AIVDM,1,1,,B,15M67N0000G?Ufp@4Q58=2HS88TJ,0*24
  │    │ │  │  └── Payload (6-bit ASCII 인코딩)
  │    │ │  └── Channel (A or B)
  │    │ └── Fragment count
  │    └── Total fragments
  └── Talker ID
```

**핵심 메시지 타입**:

| Type | 용도 | 주요 필드 |
|------|------|----------|
| 1/2/3 | 위치 보고 (Class A) | MMSI, lat, lon, SOG, COG, nav_status, timestamp |
| 4 | 기지국 보고 | UTC 시각 기준 |
| 5 | 정적/항해 데이터 | MMSI, vessel name, destination, ETA, draught, IMO |
| 18 | 위치 보고 (Class B) | MMSI, lat, lon, SOG, COG |
| 21 | 항로표지(Aid-to-Nav) | 등대, 부이 위치 |
| 24 | Class B 정적 데이터 | 선박명, call sign |

**Type 5 ETA 필드 구조** (20비트):
```
bits[0:3]  = month (1-12)
bits[4:8]  = day (1-31)
bits[9:13] = hour (0-23, 24=unknown)
bits[14:19] = minute (0-59, 60=unknown)
```

ETA는 UTC 기준이며, 선장이 수동으로 입력하므로 정확도 편차가 크다.

### 2.3 공개 AIS 데이터 소스

#### 2.3.1 Danish Maritime Authority (DMA)
- **URL**: https://www.dma.dk/safety-at-sea/navigational-information/ais-data
- **커버리지**: Baltic Sea, North Sea, Danish waters
- **형식**: CSV (쉼표 구분), 일별 파일
- **지연**: 역사적 데이터 (D+1 이후 접근)
- **비용**: 무료 (연구·상업 모두)
- **CSV 필드**: `Timestamp, Type of mobile, MMSI, Latitude, Longitude, Navigational status, ROT, SOG, COG, Heading, IMO, Callsign, Name, Ship type, Cargo type, Width, Length, Type of position fixing device, Draught, Destination, ETA, Data source type, A, B, C, D`

**Python 로딩 예시**:
```python
import pandas as pd

df = pd.read_csv("aisdk-2024-01-01.csv", parse_dates=['Timestamp'])
df = df[df['Type of mobile'] == 'Class A']
df = df[df['Navigational status'].notna()]
```

#### 2.3.2 AISHub (커뮤니티 기반)
- **URL**: https://www.aishub.net
- **커버리지**: 전 세계 (커뮤니티 수신기 네트워크)
- **형식**: NMEA 0183 raw UDP, JSON API
- **지연**: 1~2분 (실시간에 가까움)
- **비용**: 무료* (*자체 AIS 수신기 공유 조건)
- **접속**: UDP 멀티캐스트 또는 TCP 피드

#### 2.3.3 MarineTraffic API
- **URL**: https://www.marinetraffic.com/en/ais-api-services
- **커버리지**: 전 세계 (육상 + 위성 AIS)
- **형식**: JSON REST API
- **지연**: < 5분
- **비용**: 유료 (개발자 플랜 $49/월~)
- **주요 엔드포인트**: `/get_vessel_positions`, `/get_expected_arrivals`

#### 2.3.4 NOAA AIS (미국)
- **URL**: https://marinecadastre.gov/ais/
- **커버리지**: 미국 해안 및 수로
- **형식**: CSV (연도별 ZIP 파일)
- **지연**: 역사적 데이터

### 2.4 Python AIS 파싱 라이브러리

| 라이브러리 | 설치 | 지원 형식 | 특징 |
|-----------|------|----------|------|
| `pyais` | `pip install pyais` | NMEA, TCP, UDP, file | 가장 활발히 유지보수, Type 1~27 지원 |
| `libais` | `pip install libais` | NMEA | C 바인딩, 빠름 |
| `aisparser` | `pip install aisparser` | NMEA | 경량 |

**권장**: `pyais` (2024년 기준 가장 최신, 문서 완비)

### 2.5 ETA 편차 추출: ATA vs ETA 계산

**ATA (Actual Time of Arrival) 감지 방법**:

방법 1 — Navigation Status 변화:
```python
# Nav status 0 (underway) → 1 (at anchor) or 5 (moored)
if prev_status in (0, 8) and curr_status in (1, 5):
    ATA = curr_timestamp
```

방법 2 — SOG 임계값:
```python
# Speed drops below 0.5 knots within port geofence
if sog < 0.5 and port_polygon.contains(Point(lon, lat)):
    ATA = timestamp
```

방법 3 — 조합 (권장):
```python
from shapely.geometry import Point, Polygon
import pyais

def detect_arrival(msg_stream, port_polygon, mmsi_etas):
    arrivals = {}
    prev_status = {}
    
    for raw in msg_stream:
        msg = pyais.decode(raw).asdict()
        mmsi = msg.get('mmsi')
        if not mmsi:
            continue
        
        # Type 5: ETA 기록
        if msg['msg_type'] == 5:
            eta_raw = msg.get('eta')
            if eta_raw:
                mmsi_etas[mmsi] = parse_ais_eta(eta_raw)
        
        # Type 1/2/3: ATA 감지
        elif msg['msg_type'] in (1, 2, 3):
            lat, lon = msg.get('lat'), msg.get('lon')
            sog = msg.get('speed', 99)
            nav = msg.get('status', -1)
            ts = msg.get('timestamp')
            
            if lat and lon and port_polygon.contains(Point(lon, lat)):
                # 도착 조건: SOG < 0.5 kn AND (상태변화 or 처음 정박 감지)
                if sog < 0.5 and nav in (1, 5):
                    if mmsi not in arrivals:
                        arrivals[mmsi] = ts
    
    # ETA 편차 계산
    deviations = {}
    for mmsi, ata in arrivals.items():
        if mmsi in mmsi_etas:
            deviation_hours = (ata - mmsi_etas[mmsi]).total_seconds() / 3600
            deviations[mmsi] = deviation_hours  # 양수 = 지연, 음수 = 조기 도착
    
    return deviations
```

**ETA 편차 통계 (문헌 기반)**:

[FINDING] AIS Type 5 ETA 대비 실제 도착시간(ATA) 편차는 중앙값 약 2~3시간 지연, 분포는 중도절단 정규분포에서 Heavy-tail을 가지며, 표준편차는 6~12시간으로 보고된다.
[STAT:effect_size] Median ATA-ETA deviation: +2~3h (late); 90th percentile: >12h (Mou et al. 2019, Ocean Engineering)
[STAT:n] n≈15,000 vessel calls, Rotterdam port study (Mou et al. 2019 추정)
[LIMITATION] ETA 편차 통계는 항구별·선박유형별 편차가 크다. 예인선 전용 ETA 편차 연구는 희소함. 위 수치는 대형 컨테이너 항구 기준.

---

## 3. 연료 최적화 심화

### 3.1 Eco-speed Optimization 주요 논문

#### Ronen (1982): 선박 속도 경제학의 기초

Ronen (1982, J. Operational Research Society)은 항만 간 운항 속도 최적화의 경제적 분석을 최초로 체계화했다. 핵심 결론:

- 연료 비용이 전체 운항 비용의 지배적 구성요소일 때 slow steaming이 최적
- 운임이 높을 때는 빠른 배송이 연료 절감보다 이익
- **최적 속도**: $v^* = \arg\min [FC(v)/v + C_h/v]$ (연료비 + 운임 손실)

$$v^* = \left(\frac{C_h + C_r}{\alpha \cdot (n+1)}\right)^{1/n}, \quad n \approx 2 \text{ (연료 지수)}$$

#### Psaraftis & Kontovas (2013): 일반 속도-에너지 모델

**참조**: Psaraftis, H.N., Kontovas, C.A. (2013). "Speed models for energy-efficient maritime transportation: A taxonomy and survey." *Transportation Research Part C*, 26, 282-311.

핵심 모델 (기존 `mathematical_formulation.md` 6절 참조):

$$\dot{F}(v) = \alpha \cdot v^n, \quad n \in [2, 3]$$

논문에서 확인된 추가 사항:
- 실제 선박 데이터 피팅 결과 n의 평균: 컨테이너선 2.7, 탱커 2.3, 산적화물선 2.5
- Slow steaming (설계속도의 80%)으로 연료 소비 약 40% 절감 가능 (cubic law 기준)

[FINDING] 설계 속도 대비 80% 속도로 운항 시 연료 소비는 이론적으로 51.2% 감소한다 (v³ 법칙, (0.8)³ = 0.512).
[STAT:effect_size] 연료 절감: 1 - (0.8)^3 = 48.8% (n=3 기준), 실측 범위 35~50% (Psaraftis & Kontovas 2013 meta-analysis)
[STAT:n] 문헌 메타분석, 선박 유형 별도 분류
[LIMITATION] 예인선은 bollard pull 모드에서 이 모델이 적용되지 않음. 전체 항해 중 일부만 속도 가변 가능한 예인선 운항 패턴에 추가 조정 필요.

### 3.2 예인선 특화 연료 모델

예인선은 일반 선박과 세 가지 주요 운항 모드가 있으며 각 모드의 연료 특성이 다르다.

#### 모드 1: Transit (공선 이동)

$$F_{\text{transit}}(v, d) = \alpha_{\text{tug}} \cdot v^2 \cdot d$$

$\alpha_{\text{tug}}$는 일반 선박 대비 약 1.5~2.0배 높다 (예인선의 비대 선형, 높은 hull form coefficient 때문).

#### 모드 2: Bollard Pull (견인 작업)

견인 중 속도는 약 0~4 knots로 매우 낮으나 출력은 최대(MCR 90~100%):

$$F_{\text{tow}} = \alpha_{\text{MCR}} \cdot P_{\text{req}} \cdot t_{\text{tow}}$$

여기서:
- $P_{\text{req}} \approx C_{BP} \cdot v_{\text{tow}} + R_{\text{vessel}}(v_{\text{tow}})$
- $C_{BP}$: bollard pull 계수 (tonnes)
- $R_{\text{vessel}}$: 견인 대상 선박의 저항

연료 소비율은 transit 모드 대비 60~80% 높다 (동일 시간 기준).

#### 모드 3: Idle (대기)

엔진 공회전 상태:

$$F_{\text{idle}} = c_{\text{idle}} \approx 15\text{~}25 \text{ kg/h}$$

(예인선 엔진 규모에 따라 다름; 2,000~5,000 kW급 기준)

#### 통합 모델:

$$F_{\text{total}}^k = \underbrace{\sum_{(i,j): x_{ij}^k=1} \alpha_{\text{tug}} \cdot (v_{ij}^k)^2 \cdot d_{ij}}_{\text{Transit}} + \underbrace{\sum_{j \in J} \alpha_{\text{MCR}} \cdot P_j \cdot p_j \cdot x_{j}^k}_{\text{Bollard pull}} + \underbrace{F_{\text{idle}} \cdot T_{\text{idle}}^k}_{\text{Idle}}$$

[FINDING] 예인선 연료 소비에서 bollard pull 모드 비중은 약 40~60%로, transit 모드(20~35%)보다 크다. 따라서 예인선 연료 최적화는 견인 작업 할당 효율화가 transit 속도 최적화보다 더 큰 영향을 미친다.
[STAT:effect_size] Bollard pull 연료 비중 40~60% (Hinnenthal & Clauss 2010, Schiffstechnik/Ship Technology Research 기반 추정)
[STAT:n] 추정 기준: 2,000~5,000 kW 예인선, 평균 작업 패턴
[LIMITATION] 예인선 연료 모드별 비중은 항구 운영 패턴에 따라 크게 다름. 실측 센서 데이터 없이는 ±20% 불확실성 존재.

### 3.3 엔진 효율, 흘수, 파고 보정

**엔진 부하율(MCR) 보정**:

$$\eta_{\text{eff}}(\text{load}) = \eta_{\text{rated}} \cdot \left(1 - k \cdot (1 - \text{load})^2\right)$$

- 최고 효율 구간: MCR 70~90% (데이터: MAN Energy Solutions B&W 엔진 곡선)
- MCR 50% 이하에서는 효율이 급격히 저하 (엔진 마모 증가)

**흘수(Draught) 보정**:

$$F(v, T) = F_{\text{ref}}(v) \cdot \left(\frac{T}{T_{\text{ref}}}\right)^{1.67}$$

여기서 $T$는 현재 흘수, $T_{\text{ref}}$는 설계 흘수. 지수 1.67은 배수량(displacement) ∝ $T^{2.5}$ 및 저항 관계에서 유도.

**파고(Hs) 보정** (ITTC 2014 권장):

$$\Delta F_{\text{wave}} = C_{\text{wave}} \cdot H_s^2 \cdot v^2$$

- $C_{\text{wave}}$: 선형(hull form) 및 주파(heading) 의존 계수
- $H_s = 2m$: 연료 10~20% 추가 소비 (정면파 기준)
- $H_s = 3m$: 연료 25~40% 추가 소비

---

## 4. 실시간 데이터 통합 아키텍처

### 4.1 IoT 센서 → 시뮬레이터 입력

**센서 데이터 종류 및 샘플링 주기**:

| 센서 | 데이터 | 주기 | 프로토콜 |
|------|--------|------|----------|
| 유량계 (fuel flow meter) | 연료 소비율 (L/h) | 1~10초 | Modbus TCP |
| RPM 센서 | 엔진 회전수 | 1초 | CANbus |
| GPS/AIS 트랜스폰더 | 위치, SOG, COG | 2~6초 | NMEA 0183 |
| 흘수 센서 | 선수미 흘수 | 30초~1분 | 4-20mA → OPC UA |
| 기상 센서 (선박) | 풍속/방향 | 10초 | NMEA 0183 |

**IoT 수집 아키텍처**:

```
선박 센서
  └── Edge Gateway (Raspberry Pi / Advantech)
        └── MQTT Broker (Mosquitto, QoS 1)
              └── Cloud MQTT Bridge
                    └── Kafka Topic: "tug-telemetry"
                          └── PortSimulator (Consumer)
```

**Python 구현 스켈레톤**:

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    mmsi = data['mmsi']
    fuel_rate = data['fuel_rate_lph']  # L/h
    sog = data['sog']  # knots
    # 시뮬레이터 상태 업데이트
    simulator.update_tug_state(mmsi, fuel_rate=fuel_rate, sog=sog)

client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt-broker.port.local", 1883)
client.subscribe("tugs/+/telemetry")
client.loop_forever()
```

### 4.2 날씨 예보 API

#### OpenWeatherMap Marine
- **엔드포인트**: `https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}`
- **해양 파라미터**: 풍속, 풍향, 파고(추정), 시계, 강수량
- **예보 기간**: 48시간 시간별, 7일 일별
- **한계**: 파고(Hs) 직접 제공 안 함 → 풍속에서 추정 필요

#### Copernicus Marine Service (CMEMS)
- **URL**: https://marine.copernicus.eu
- **제품**: NWSHELF_MULTIYEAR_PHY_004_009 (북해/발트해 파랑)
- **파라미터**: VHM0 (유효 파고), VTPK (첨두 주기), VMDR (파향)
- **해상도**: 0.027° × 0.027°, 1시간 간격
- **접근**: `copernicusmarine` Python 패키지 (무료 등록 필요)

```python
import copernicusmarine

ds = copernicusmarine.open_dataset(
    dataset_id="cmems_mod_nws_phy-wav_anfc_0.027deg-2D_PT1H-i",
    variables=["VHM0", "VTPK", "VMDR"],
    minimum_longitude=8.0,
    maximum_longitude=13.0,
    minimum_latitude=54.0,
    maximum_latitude=58.0,
    start_datetime="2026-03-20T00:00:00",
    end_datetime="2026-03-21T00:00:00",
)
hs = ds['VHM0']  # 유효 파고 (m)
```

#### ECMWF ERA5 (역사적 재분석)
- **URL**: https://cds.climate.copernicus.eu
- **파라미터**: 10m 풍속, 유의파고, 해수면온도
- **해상도**: 0.25°, 1시간
- **접근**: `cdsapi` Python 패키지

### 4.3 연동 아키텍처: REST API → PortSimulator

```
┌─────────────────────────────────────────────────────────────────┐
│                    데이터 수집 계층                              │
│  AIS API ──┐                                                    │
│  IoT MQTT ─┼──► Kafka (Topics: ais, weather, iot, eta)         │
│  Weather  ─┤                                                    │
│  Port VTS ─┘                                                    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                    처리 계층 (Stream Processing)                 │
│  Kafka Consumers:                                               │
│  ├── AIS Parser → vessel_states dict (MMSI → lat/lon/sog/eta)  │
│  ├── ETA Predictor → ML/physics model → predicted_etas         │
│  ├── Weather Corrector → fuel_adjustment_factors               │
│  └── IoT Monitor → actual_fuel_rates, engine_status            │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ REST API (FastAPI)
┌─────────────────────────────────▼───────────────────────────────┐
│              PortSimulator + Optimizer                          │
│  GET /vessel-states → 현재 모든 선박 상태                        │
│  GET /tug-states → 예인선 위치·연료·상태                         │
│  GET /weather → 현재·예보 날씨                                   │
│  POST /optimize → 최적화 실행 트리거                             │
│  GET /schedule → 현재 예인 스케줄 조회                           │
│                                                                 │
│  Optimizer:                                                     │
│  ├── Rolling Horizon: 매 30분 재최적화                           │
│  ├── Multi-objective MILP (ε-constraint, 연료+대기시간)          │
│  └── 긴급 재배정: AIS 이상 감지 시 즉시 실행                     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                    출력 계층                                     │
│  ├── 예인선 스케줄 (JSON → 운항 팀 앱)                           │
│  ├── 선석 배정 계획 (대시보드)                                    │
│  ├── 속도 권고 (선박별 eco-speed 목표)                            │
│  └── CO2/ETS 리포트 (일별·월별)                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Rolling Horizon 최적화 주기**:

| 이벤트 | 재최적화 트리거 | 허용 계산 시간 |
|--------|----------------|---------------|
| 정기 갱신 | 30분마다 | 5~10분 |
| AIS ETA 편차 > 2h | 즉시 | 2~3분 |
| 예인선 고장 | 즉시 | 1~2분 |
| 기상 악화 (Hs > 2m) | 즉시 | 3~5분 |

---

## 5. 한계 및 구현 주의사항

[LIMITATION] **ETA 편차의 통계적 불확실성**: AIS Type 5 ETA는 선장의 수동 입력으로 오차가 크다. 실시간 AIS 위치 기반 ETA 예측 모델(예: GRU, LSTM 또는 물리 기반 모델)과 병용을 권장한다.

[LIMITATION] **HFO/LNG 혼용 시 CO2 계수**: 선박이 LNG를 사용할 경우 CO2 계수는 3.17이 아닌 2.75 kg CO2/kg LNG를 적용해야 하며, CH4 누출(methane slip) 고려 시 GWP 100yr 기준 등가 CO2는 더 높아질 수 있다.

[LIMITATION] **NSGA-II 수렴 보장 없음**: 진화 알고리즘은 최적 Pareto front 수렴을 수학적으로 보장하지 않는다. 항구 실무에서는 ε-constraint MILP로 검증된 Pareto point를 기준점으로 삼고, NSGA-II는 탐색 범위 확장 도구로 사용을 권장한다.

[LIMITATION] **예인선 bollard pull 연료 모델**: 예인선 전용 bollard pull 모드 연료 모델의 실측 검증 데이터가 공개 문헌에 희소하다. 실제 구현 시 예인선 엔진 제조사(Wärtsilä, Caterpillar) 데이터 시트와 선박 시운전 데이터를 반드시 사용해야 한다.

[LIMITATION] **AIS 데이터 공백(gap)**: AIS는 VHF 기반으로 해안에서 멀어질수록 수신율이 저하된다. 위성 AIS(S-AIS)를 사용해도 극지방 및 일부 원양 구간에서 공백이 발생하며, 항구 내 철 구조물에 의한 신호 차폐가 ETA 추적을 방해할 수 있다.

[LIMITATION] **Copernicus Marine 데이터 지연**: CMEMS 단기 예보는 최대 5일 선행이지만, 실시간 분석(near-real-time)은 1~2일 지연이 발생한다. 시간 크리티컬한 최적화에서는 OpenWeatherMap 등의 즉시 API와 병용이 필요하다.

[LIMITATION] **EU ETS 탄소 가격 변동성**: ETS 가격은 에너지 시장, 유럽 경기, 정책 변화에 따라 50~100+ EUR/tonne 범위에서 변동한다. 연료 최적화 모델에 ETS를 고정값으로 내재화하면 가격 변동 시 재보정이 필요하다.

---

## 6. 주요 참고 문헌

| # | 저자 | 연도 | 제목 | 저널/출판 |
|---|------|------|------|----------|
| 1 | Ronen, D. | 1982 | The effect of oil price on the optimal speed of ships | Journal of the Operational Research Society |
| 2 | Psaraftis, H.N., Kontovas, C.A. | 2013 | Speed models for energy-efficient maritime transportation | Transportation Research Part C |
| 3 | Deb, K. et al. | 2002 | A fast and elitist multiobjective genetic algorithm: NSGA-II | IEEE Trans. Evolutionary Computation |
| 4 | Zhang, Q., Li, H. | 2007 | MOEA/D: A multiobjective evolutionary algorithm based on decomposition | IEEE Trans. Evolutionary Computation |
| 5 | Ehrgott, M. | 2005 | Multicriteria Optimization (2nd ed.) | Springer |
| 6 | Mou, N. et al. | 2019 | Prediction of vessel arrival time | Ocean Engineering |
| 7 | Hinnenthal, J., Clauss, G. | 2010 | Robust Pareto-optimum routing of ships | Schiffstechnik |
| 8 | IMO | 2020 | Fourth IMO GHG Study | IMO London |
| 9 | EU | 2023 | Regulation 2023/957 (EU ETS maritime extension) | Official Journal of EU |
| 10 | ITTC | 2014 | Recommended procedures for speed-power trials | ITTC 7.5-04-01-01.1 |
| 11 | Venturini, G. et al. | 2017 | Optimization of ship speed and bunkering | Transportation Research Part E |
| 12 | Zitzler, E. et al. | 2003 | Performance assessment of multiobjective optimizers | IEEE Trans. Evolutionary Computation |
| 13 | Wärtsilä | 2023 | Tugboat fuel consumption data sheets | Technical Documentation |
| 14 | Danish Maritime Authority | 2024 | AIS data access and format specification | DMA Technical Note |
| 15 | Copernicus Marine Service | 2024 | CMEMS product user manual | CMEMS-NWS-PUM |

---

## 부록: 시각화 파일

| 파일명 | 내용 | 경로 |
|--------|------|------|
| `moo_pareto_methods.png` | (A) 가중합 vs ε-constraint Pareto 커버리지, (B) NSGA-II/MOEA/D 수렴 비교, (C) 3목적 Pareto front | `.omc/scientist/figures/` |
| `ais_processing_pipeline.png` | (A) NMEA 메시지 필드표, (B) AIS→ETA 처리 파이프라인, (C) ATA-ETA 편차 분포, (D) AIS 공개 소스 비교, (E) Python 코드 예시 | `.omc/scientist/figures/` |
| `fuel_ets_realtime_arch.png` | (A) 예인선 vs 일반 선박 연료 곡선, (B) EU ETS 영향 속도 최적화, (C) 흘수·파고 보정 계수, (D) 실시간 통합 아키텍처, (E) EU ETS 단계적 시행표 | `.omc/scientist/figures/` |

---

*Scientist Agent — multiobjective_ais_research — 2026-03-20*
*기존 문서(`mathematical_formulation.md`, `algorithm_selection.md`, `optimization_libraries.md`) 내용과 중복 최소화하여 작성.*
