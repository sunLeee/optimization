---
id: ADR-002
title: Shaw Destroy Lambda — 부산항 실측 피팅 결과 및 이중 전략
status: Accepted
date: 2026-03-21
deciders: 데이터 분석팀
---

# ADR-002: Shaw Destroy Lambda — 부산항 실측 피팅 결과 및 이중 전략

## 맥락 (Context)

`libs/routing/alns.py`의 Shaw Destroy(D3)는 작업 간 relatedness를 다음으로 계산한다.

```
r(i, j) = λ_d·(d_ij/d_max) + λ_t·(|e_i - e_j|/T) + λ_p·(|p_i - p_j|/P_max)
```

초기 파라미터는 원논문 기본값(Ropke & Pisinger 2006)을 사용했다.

```
원논문 기본값: λ_d=0.500, λ_t=0.300, λ_p=0.200
```

2024-06 부산항 실데이터(N=336건)를 활용하여 데이터 기반 피팅을 실시했다.

## 데이터 및 방법

| 항목 | 내용 |
|------|------|
| 데이터 | `data/raw/scheduling/data/2024-06_SchData.csv` + AIS 궤적 336건 |
| similar 쌍 | 같은 예선에 순차 배정된 인접 작업 쌍 (N=326) |
| dissimilar 쌍 | 다른 예선의 무작위 작업 쌍 (N=326) |
| 최적화 | `differential_evolution` — 분리도(dissimilar_mean - similar_mean) 최대화 |
| 거리 | Proxy(작업이동거리 차이) 및 AIS 실궤적 haversine 합산 두 버전 시도 |

## 피팅 결과

| λ | 원논문 | **Proxy 피팅** | **AIS 실거리 피팅** |
|---|--------|----------------|---------------------|
| λ_d (거리) | 0.500 | 0.000 | 0.000 |
| λ_t (시간창) | 0.300 | **1.000** | **1.000** |
| λ_p (우선순위) | 0.200 | 0.000 | 0.000 |
| 분리도 | — | 0.3089 | 0.3089 |
| 분류 정확도 | — | 90.8% | 90.8% |

**두 방법 모두 동일 결과**: λ_t=1.0이 압도적으로 지배.

## 해석

부산항 예선 배정에서 **시간창(time window) 근접도만이 유사성을 결정**한다.
- 예선은 항구 내에서 이동거리 차이가 크지 않아 거리 변별력이 낮다.
- 동일 예선이 연속 수행하는 작업은 시간적으로 연속되는 특성이 있다.
- 우선순위(톤수 기반)는 예선 배정 클러스터링과 상관관계가 낮다.

## 결정 (Decision)

**이중 전략 유지**:

1. `ALNSConfig` 기본값 = **원논문 값 유지** (0.5, 0.3, 0.2)
   - 도메인 이전성: 다른 항구 데이터에 일반화 가능
   - 원논문 벤치마크와의 비교 가능성 보장

2. `fit_shaw_lambdas(windows, assignments, distances)` **구현 완료**
   - 역사적 데이터가 있으면 데이터 기반 override
   - 데이터 부족(N<5) 시 자동 fallback to 원논문 기본값

```python
# 사용 예:
from libs.routing.alns import fit_shaw_lambdas, ALNSConfig

ld, lt, lp = fit_shaw_lambdas(windows, historical_assignments, distances)
cfg = ALNSConfig(shaw_lambda_d=ld, shaw_lambda_t=lt, shaw_lambda_p=lp)
# 부산항 실측: ld=0.0, lt=1.0, lp=0.0
```

## 결과 (Consequences)

### 긍정
- 데이터 기반 파라미터 결정 프로세스 확립
- `fit_shaw_lambdas()` fallback 구조로 데이터 없는 환경에서도 안전
- 90.8% 분류 정확도 — Shaw Destroy가 실제 유사 작업을 잘 식별함

### 주의
- λ_t=1.0 적용 시 Shaw Destroy가 TW Destroy(D4)와 유사하게 동작
  → 연산자 다양성 감소 가능 → Adaptive Weight가 D4를 선호하면 자동 대응
- 부산항 특화 결과: 다른 항구에서는 다른 λ 분포 예상
- 데이터 갱신(연 1회) 시 `fit_shaw_lambdas()` 재실행 권장

## 참조

- Ropke & Pisinger (2006): ALNS for PDPTW, Transportation Science
- Shaw (1998): Using constraint programming and local search methods
- `docs/research/algorithm_selection.md` §3 ALNS
- ADR-001: ETA 분포 파라미터 교체
