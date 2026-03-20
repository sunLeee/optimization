# 선박 ETA 도착 지연 확률분포 선택 가이드

**작성일**: 2026-03-19
**목적**: 날씨 불확실성(±2시간) 하 선박 도착 시간 편차 모델링
**채택 결정**: Log-normal 기본, 역사적 데이터 N≥200 시 KDE 대체

---

## 1. 문제 정의

```
ETA_deviation = ATA - ETA  (단위: hours)
```

- `ATA`: Actual Time of Arrival (실제 도착)
- `ETA`: Estimated Time of Arrival (예정 도착)
- 범위: ±2시간 (날씨 조건에 따라)
- 양수: 지연 (late), 음수: 조기 도착 (early)

---

## 2. 후보 분포 비교

### 2.1 균등분포 U(-2, +2)

```python
from scipy.stats import uniform
dist = uniform(loc=-2, scale=4)  # U(-2, +2)
```

**특성**:
- 지연/조기 도착 동일 확률 가정
- 경계 외부 확률 = 0 (hard bound)
- 평균 = 0, 분산 = 4/3

**장점**: 단순, 해석적 tractability
**단점**: 비현실적 — 실제 도착은 균등하지 않음. 모든 연구에서 기각됨
**사용 사례**: 보수적 worst-case bound 초기 추정

---

### 2.2 정규분포 N(0, σ)

```python
from scipy.stats import norm
dist = norm(loc=0, scale=0.85)  # σ=0.85 → P(|X|≤2) ≈ 0.98
```

**특성**:
- 대칭 분포 (지연 = 조기 도착 동일 가능성)
- σ 선택: 날씨 조건별로 달라짐

**장점**: 해석적 처리 용이, Stochastic Programming에서 다루기 쉬움
**단점**: 비대칭성 포착 불가 — 실제 지연은 우측 꼬리가 두꺼움

---

### 2.3 절단 정규분포 TruncatedNormal[-2, +2]

```python
from scipy.stats import truncnorm
a, b = -2/sigma, 2/sigma
dist = truncnorm(a, b, loc=0, scale=sigma)
```

**특성**:
- 경계 ±2시간을 hard bound로 강제
- Bierwirth & Meisel (2015) 계열 BAP 논문에서 주로 사용

**장점**: 물리적 경계 준수, 2-stage SP 시나리오 생성에 적합
**단점**: 여전히 대칭 가정. 실제 지연 비대칭성 미반영

---

### 2.4 로그정규분포 Log-Normal (채택 기본)

```python
from scipy.stats import lognorm
import numpy as np

# 지연 = max(0, ATA - ETA): 비음수 지연 모델
# zero-mean화: X = delay - E[delay]
mu_log = 0.1   # 로그 스케일 평균
sigma_log = 0.6  # 로그 스케일 표준편차
dist = lognorm(s=sigma_log, scale=np.exp(mu_log))
```

**특성**:
- 비대칭 우측 꼬리 (지연이 조기 도착보다 길게 나타남)
- 비음수 지원 → 지연 시간의 물리적 특성 반영
- Psaraftis & Kontovas (2013): 해양 지연의 실증 분포로 Log-normal 권장

**근거 논문**:
- Zhen, Lee & Wang (2011, EJOR): BAP 불확실성에서 log-normal 도착 지연 가정
- Venturini et al. (2017, TRD): 멀티포트 BAP에서 비대칭 지연 log-normal 모델

**장점**: 실제 항구 데이터에서 가장 널리 검증됨, 비대칭성 포착
**단점**: ±2시간 hard bound와 충돌 가능 → 절단 log-normal 필요시 scipy.stats.truncate

**채택 이유**: 대부분의 서양/일본 항구 실증 연구에서 지지됨

---

### 2.5 Erlang 분포

```python
from scipy.stats import erlang
k = 3  # 형태 모수 (단계 수)
dist = erlang(a=k, scale=0.5)
```

**특성**:
- k개 독립 Exponential 단계의 합
- 도선(pilot), 예인선 연결, 접안의 3단계 → Erlang-3 직관적

**적용 위치**: **서비스 시간** 모델에 적합 (처리 시간, 접안 시간)
**도착 지연**에는 부적합 — 비음수 지원만, 조기 도착 표현 불가
**참고**: Dragovic, Park & Radmilovic (2006, Promet): 항구 M/E_k/c 큐잉 모델에서 서비스 시간 Erlang-k 가정

---

### 2.6 Weibull 분포

```python
from scipy.stats import weibull_min
c = 1.5  # 형태 모수
dist = weibull_min(c=c, scale=1.2)
```

**특성**:
- 기상 조건 모델링에 자주 사용 (파고, 풍속)
- 형태 모수 c>1: 우측 꼬리 지연 패턴

**사용 사례**: 기상 조건 자체를 Weibull으로 모델링 후, 조건부 지연 분포 구성
**한계**: 조기 도착(음수 지연) 표현 불가

---

### 2.7 Gaussian Mixture Model (GMM)

```python
from sklearn.mixture import GaussianMixtureMixin
# 날씨 좋음 (calm): N(0, 0.3) - 정시 근처
# 날씨 나쁨 (rough): N(1.5, 0.8) - 지연 편향
# π = [0.7, 0.3]  # 날씨 좋은 날 70% 가정
```

**특성**:
- 다중 날씨 체제를 혼합으로 포착
- Beaufort scale 또는 해상 상태별 조건부 분포 구성 가능

**장점**: 가장 현실적, 실제 AIS 데이터에서 좋은 적합도
**단점**: 파라미터 추정에 데이터 필요 (N≥200 권장), EM 알고리즘 필요

---

## 3. 분포 선택 결정 트리

```
역사적 ETA 편차 데이터 보유?
├── YES: N개 샘플
│   ├── N ≥ 200: KDE (비모수적) 또는 GMM (EM 적합)
│   │   → KS-test / Anderson-Darling으로 Log-normal vs Weibull 검증
│   └── N < 200: Log-normal 파라미터 추정 (MLE)
│       → scipy.stats.lognorm.fit(data)
└── NO: 선험적 분포 가정
    ├── 대칭 가정 수용: TruncatedNormal(-2, +2, σ=0.85)
    └── 비대칭 필요: Log-normal (mu=0.1, sigma=0.6) + zero-mean shift
```

---

## 4. 채택 분포 및 구현

### 4.1 기본 채택: Log-normal (비대칭 지연)

```python
# libs/stochastic/distributions.py 예시

import numpy as np
from scipy.stats import lognorm, norm
from scipy.stats import truncnorm


def eta_delay_distribution(
    weather_condition: str = "calm",
    n_historical: int = 0,
    historical_data: np.ndarray | None = None,
) -> object:
    """ETA 지연 분포 팩토리.

    Args:
        weather_condition: 'calm' | 'moderate' | 'rough'
        n_historical: 역사적 샘플 수
        historical_data: ATA - ETA 편차 배열 (hours)

    Returns:
        scipy.stats frozen distribution
    """
    if historical_data is not None and n_historical >= 200:
        # KDE 또는 GMM 사용
        from scipy.stats import gaussian_kde
        return gaussian_kde(historical_data)

    # 날씨 조건별 Log-normal 파라미터
    params = {
        "calm":     {"mu": 0.05, "sigma": 0.4},  # 소지연
        "moderate": {"mu": 0.15, "sigma": 0.7},  # 중지연
        "rough":    {"mu": 0.40, "sigma": 1.0},  # 대지연
    }
    p = params.get(weather_condition, params["calm"])
    return lognorm(s=p["sigma"], scale=np.exp(p["mu"]))


def sample_scenarios(dist, n_scenarios: int = 100, seed: int = 42) -> np.ndarray:
    """Monte Carlo 시나리오 생성."""
    rng = np.random.default_rng(seed)
    return dist.rvs(size=n_scenarios, random_state=rng)
```

### 4.2 KDE 대체 조건

```python
# 조건: len(historical_eta_errors) >= 200
if len(historical_data) >= 200:
    from scipy.stats import gaussian_kde
    dist = gaussian_kde(historical_data)
```

---

## 5. 2-Stage Stochastic Programming 연동

```python
# 시나리오 생성 → SAA
scenarios = sample_scenarios(dist, n_scenarios=50, seed=42)

# 2-stage SP: 1st stage (스케줄 결정) + 2nd stage (지연 재배정)
# E[Q(x, ξ)] ≈ (1/N) Σ Q(x, ξ^s)  for s=1,...,N
```

**권장 시나리오 수**: N=50~200 (SAA convergence: Ahmed & Shapiro 2002)

---

## 6. 참고 문헌

| 논문 | 분포 사용 | 적용 문제 |
|------|----------|-----------|
| Zhen et al. (2011, EJOR) | Log-normal 도착 지연 | BAP 불확실성 |
| Bierwirth & Meisel (2015, EJOR) | TruncatedNormal | Stochastic BAP 서베이 |
| Dragovic et al. (2006, Promet) | Erlang-k | 항구 서비스 시간 |
| Psaraftis & Kontovas (2013, TRC) | — | 속도-연료 관계 |
| Ahmed & Shapiro (2002) | — | SAA 수렴 분석 |

---

**결론**: 역사적 데이터 미보유 시 **Log-normal** 기본 채택.
데이터 N≥200 시 **KDE** 또는 날씨 조건별 **GMM** 전환.
Erlang은 도착 지연이 아닌 **서비스 시간** 전용으로 사용한다.
