---
id: ADR-001
title: ETA 지연 분포 파라미터 — 실측값으로 교체
status: Accepted
date: 2026-03-21
deciders: 데이터 분석팀
---

# ADR-001: ETA 지연 분포 파라미터 — 실측값으로 교체

## 맥락 (Context)

`libs/stochastic/two_stage.py`의 `TwoStageConfig`와 `generate_eta_scenarios()`는
출항 전 ETA 지연 분포를 Log-normal로 모델링한다.
초기 파라미터는 가정값(assumed priors)을 사용했다.

```
기존: mu_log=0.1, sigma_log=0.5, clip=[-2h, +2h]
```

2024년 6월 부산항 예선 운항 실데이터(SchData)가 확보되어 MLE 피팅이 가능해졌다.

## 데이터 출처

| 파일 | 내용 |
|------|------|
| `data/raw/scheduling/data/2024-06_SchData.csv` | 실제 예선 배정 스케줄 |
| `data/raw/scheduling/data/AISLog/*.csv` | 예선·선박 AIS 궤적 |

- 기간: 2024-06-08 ~ 2024-07-01 (약 23일)
- N = **336건** (≥ 200 → AW-010 기준: KDE/GMM 또는 MLE 적용)

## 실측 분석 결과

### ETA Deviation 분포 (최초 계획 시각 대비 실제 시작 시각)

| 항목 | 값 |
|------|-----|
| N | 336 |
| mean | +86.8분 |
| median | +29.5분 |
| std | 227.3분 |
| 지연(>0) 비율 | **71.4%** |
| 조기(<0) 비율 | 28.6% |
| 실제 범위 | [-840분, +1224분] = [-14h, +20.4h] |
| ±2h 이내 비율 | 81.5% |
| ±6h 이내 비율 | 89.6% |

### Log-normal MLE 피팅 (지연 건 N=240)

| 파라미터 | 기존(가정) | **실측값** | 비고 |
|----------|-----------|-----------|------|
| `mu_log` | 0.1 | **4.015** | 지연 중앙값: 66분 → 55.4분 |
| `sigma_log` | 0.5 | **1.363** | 분산 2.6배 과소평가 |
| `clip_min_h` | -2.0h | **-6.0h** | ±2h 커버 81.5% → ±6h 89.6% |
| `clip_max_h` | +2.0h | **+6.0h** | 실제 최대 +20h이나 극단값 제외 |

## 결정 (Decision)

AW-010 기준(N≥200 → MLE 피팅 적용)에 따라 실측값으로 교체한다.

**교체 항목:**

1. `TwoStageConfig` 기본값
   ```python
   # Before
   eta_mu_log: float = 0.1
   eta_sigma_log: float = 0.5
   eta_clip_min_h: float = -2.0
   eta_clip_max_h: float = 2.0

   # After
   eta_mu_log: float = 4.015      # MLE on 2024-06 data, N=240 delay events
   eta_sigma_log: float = 1.363   # MLE on 2024-06 data
   eta_clip_min_h: float = -6.0   # covers 89.6% of observed deviations
   eta_clip_max_h: float = 6.0    # covers 89.6% of observed deviations
   ```

2. `generate_eta_scenarios()` docstring 및 default 파라미터 동기화

3. `libs/stochastic/CLAUDE.md` ETA 분포 표 업데이트

4. 루트 `CLAUDE.md` AW-010 실측값 기록

## 결과 (Consequences)

### 긍정
- 시나리오 현실성 대폭 향상 (기존 clip ±2h → 실측 ±6h)
- CVaR95 계산 기반 신뢰도 향상
- mu_log 4.015 반영 시 지연 중앙값 55.4분(실측) ≈ 실제 운항 패턴

### 주의
- 기존 테스트에서 하드코딩된 `mu_log=0.1`은 별도 업데이트 필요
- `sigma_log=1.363`은 분산이 크므로 시나리오 수 K=50 유지 적정
  (Shapiro 2003: K≥30 for 95% confidence, N=336 support)
- 데이터 갱신 시 MLE 재피팅 권장 (연 1회 이상)

## 참조

- AW-010: ETA 분포 선택 기준 (`CLAUDE.md`)
- `docs/research/eta_distributions.md`
- Ahmed & Shapiro (2002): SAA convergence
- 실측 분석 코드: `scripts/analyze_eta_distribution.py` (예정)
