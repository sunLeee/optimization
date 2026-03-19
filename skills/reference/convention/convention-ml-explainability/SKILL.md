---
name: convention-ml-explainability
triggers:
  - "convention ml explainability"
description: "머신러닝 모델 설명 가능성(Interpretability) 컨벤션 참조 스킬. Feature importance, SHAP, 부분 의존성 플롯 등으로 모델 결과를 해석 가능하게 만드는 방법을 제공한다."
argument-hint: "[모델타입] - tree, linear, neural, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  머신러닝 모델의 해석 가능성을 확보하는 방법을 제공한다.
  블랙박스 모델을 투명하게 만들어 비즈니스 사용자도 이해 가능하도록 한다.
agent: |
  ML 설명 가능성 전문가.
  모델별 해석 기법, 시각화 방법, 주의사항을 명확하게 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 머신러닝 모델 설명 가능성(Interpretability)

모델 예측 결과를 해석 가능하게 만드는 기법과 가이드.

## 목적

- 모델 예측 이유 설명
- 특성(Feature) 중요도 파악
- 개별 예측 해석
- 비즈니스 이해관계자와 소통

## 사용법

```
/convention-ml-explainability [모델타입]
```

| 타입 | 설명 | 사용 기법 |
|------|------|---------|
| `tree` | 의사결정나무 계열 | Feature Importance, SHAP |
| `linear` | 선형 모델 | 계수(Coefficient), 부분 의존성 |
| `neural` | 신경망 | SHAP, Attention, Grad-CAM |
| `all` | 전체 기법 (기본값) | 모두 포함 |

---

## 1. Feature Importance (특성 중요도)

### 1.1 트리 기반 모델 (의사결정나무, 랜덤포레스트, XGBoost)

**가장 간단하고 빠른 방법**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모델 설명 가능성 분석 모듈.

Author: taeyang lee
Created: 2026-01-21 15:00(KST, UTC+09:00)
Modified: 2026-01-21 15:00(KST, UTC+09:00)
Version: 1.0.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer


def analyze_tree_feature_importance(
    model: RandomForestClassifier,
    feature_names: list[str],
    top_k: int = 10,
) -> pd.DataFrame:
    """트리 기반 모델의 Feature Importance를 분석한다.

    Args:
        model (RandomForestClassifier): 학습된 모델.
        feature_names (list[str]): 특성 이름 리스트.
        top_k (int): 상위 K개 특성만 표시. 기본값 10.

    Returns:
        pd.DataFrame: 특성명, 중요도, 누적 중요도.

    Logics:
        1. 모델의 feature_importances_ 추출.
        2. 특성명과 함께 DataFrame 생성.
        3. 중요도 기준으로 내림차순 정렬.
        4. 상위 K개 추출.
        5. 누적 중요도 계산.

    Example:
        >>> from sklearn.ensemble import RandomForestClassifier
        >>> from sklearn.datasets import load_breast_cancer
        >>> X, y = load_breast_cancer(return_X_y=True)
        >>> model = RandomForestClassifier(n_estimators=100)
        >>> model.fit(X, y)
        >>> importances = analyze_tree_feature_importance(
        ...     model,
        ...     feature_names=[f'feat_{i}' for i in range(X.shape[1])],
        ...     top_k=5
        ... )
        >>> print(importances)
    """
    # 1. 특성 중요도 추출
    importances = model.feature_importances_

    # 2. DataFrame 생성
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    })

    # 3. 정렬 및 상위 K개 추출
    importance_df = importance_df.sort_values(
        'importance',
        ascending=False
    )
    importance_df = importance_df.head(top_k).reset_index(
        drop=True
    )

    # 4. 누적 중요도 계산
    importance_df['cumulative_importance'] = (
        importance_df['importance'].cumsum()
    )
    importance_df['cumulative_pct'] = (
        importance_df['cumulative_importance'] /
        importance_df['importance'].sum() * 100
    )

    return importance_df


# 사용 예시
if __name__ == '__main__':
    # 데이터 로드
    X, y = load_breast_cancer(return_X_y=True)
    data = load_breast_cancer()
    feature_names = list(data.feature_names)

    # 모델 학습
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )
    model.fit(X, y)

    # Feature Importance 분석
    importances = analyze_tree_feature_importance(
        model,
        feature_names,
        top_k=10
    )

    print("상위 10개 특성:")
    print(importances[['feature', 'importance', 'cumulative_pct']])
```

**결과 해석**:
- `importance`: 0~1 사이 값 (합계 = 1)
- `cumulative_pct`: 누적 중요도 %
- 상위 3개 특성이 80% 이상이면 모델이 **소수 특성에 의존**

---

### 1.2 시각화

```python
def plot_feature_importance(
    importance_df: pd.DataFrame,
    figsize: tuple = (10, 6),
) -> None:
    """Feature Importance를 막대 그래프로 시각화한다.

    Args:
        importance_df (pd.DataFrame): analyze_tree_feature_importance 결과.
        figsize (tuple): 그래프 크기. 기본값 (10, 6).

    Logics:
        1. 상위 K개 특성을 막대 그래프로 표시.
        2. 색상: 중요도 높을수록 짙은 색.
        3. 누적 퍼센트 라인 추가.
    """
    fig, ax1 = plt.subplots(figsize=figsize)

    # 막대 그래프
    ax1.barh(
        importance_df['feature'],
        importance_df['importance'],
        color='steelblue',
        alpha=0.8
    )
    ax1.set_xlabel('특성 중요도')
    ax1.set_title('상위 특성의 중요도')
    ax1.invert_yaxis()

    # 누적 중요도 라인 (오른쪽 축)
    ax2 = ax1.twiny()
    ax2.plot(
        importance_df['cumulative_pct'],
        importance_df['feature'],
        'ro-',
        linewidth=2,
        label='누적 중요도 %'
    )
    ax2.set_xlabel('누적 중요도 (%)', color='red')
    ax2.set_xlim(0, 105)
    ax2.legend(loc='lower right')

    plt.tight_layout()
    plt.show()
```

---

## 2. SHAP (SHapley Additive exPlanations)

### 2.1 전체 모델 해석 (Summary Plot)

**SHAP은 게임 이론 기반의 설명 방법** (모든 모델에 적용 가능)

```python
import shap


def analyze_with_shap(
    model,
    X_train: np.ndarray,
    X_test: np.ndarray,
    feature_names: list[str],
) -> shap.TreeExplainer:
    """SHAP을 이용하여 모델을 분석한다.

    Args:
        model: 학습된 모델 (Tree, Linear, Neural Network 등).
        X_train (np.ndarray): 학습 데이터 (배경 데이터).
        X_test (np.ndarray): 테스트 데이터.
        feature_names (list[str]): 특성 이름.

    Returns:
        shap.TreeExplainer: SHAP 설명자.

    Logics:
        1. SHAP Explainer 생성.
        2. SHAP 값 계산 (모든 예측에 대해).
        3. Summary plot으로 시각화.

    Example:
        >>> explainer = analyze_with_shap(
        ...     model, X_train, X_test, feature_names
        ... )
        >>> # Summary plot 자동 출력
    """
    # 1. Explainer 생성 (Tree 모델 대상)
    explainer = shap.TreeExplainer(model)

    # 2. SHAP 값 계산
    shap_values = explainer.shap_values(X_test)

    # 3. Summary plot (전체 모델 해석)
    plt.figure()
    shap.summary_plot(
        shap_values,
        X_test,
        feature_names=feature_names,
        plot_type='bar'  # 평균 영향도
    )
    plt.title('SHAP Summary Plot (평균 영향도)')
    plt.show()

    # 4. Summary plot (상세)
    plt.figure()
    shap.summary_plot(
        shap_values,
        X_test,
        feature_names=feature_names,
        plot_type='violin'  # 분포 표시
    )
    plt.title('SHAP Summary Plot (분포)')
    plt.show()

    return explainer
```

**결과 해석**:
- `bar plot`: 평균적으로 각 특성이 모델에 미치는 영향
- `violin plot`: 특성 값이 높을 때 vs 낮을 때의 영향 분포

---

### 2.2 개별 예측 해석 (Waterfall Plot)

```python
def explain_single_prediction(
    explainer: shap.TreeExplainer,
    X_test: np.ndarray,
    instance_idx: int,
    feature_names: list[str],
) -> None:
    """개별 예측을 SHAP Waterfall Plot으로 설명한다.

    Args:
        explainer (shap.TreeExplainer): SHAP 설명자.
        X_test (np.ndarray): 테스트 데이터.
        instance_idx (int): 설명할 인스턴스 인덱스.
        feature_names (list[str]): 특성 이름.

    Logics:
        1. 해당 인스턴스의 SHAP 값 추출.
        2. Waterfall plot으로 시각화.
        3. 각 특성의 영향을 누적으로 표시.

    Example:
        >>> explain_single_prediction(
        ...     explainer, X_test, 0, feature_names
        ... )
        # 첫 번째 예측이 어떻게 나왔는지 상세 설명
    """
    # SHAP 값 계산
    shap_values = explainer.shap_values(X_test)

    # Waterfall plot
    plt.figure()
    shap.plots.waterfall(
        shap.Explanation(
            values=shap_values[instance_idx],
            base_values=explainer.expected_value,
            data=X_test[instance_idx],
            feature_names=feature_names
        )
    )
    plt.title(
        f'SHAP Waterfall: 인스턴스 #{instance_idx} 예측 설명'
    )
    plt.show()
```

**결과 해석**:
- Base value: 모델의 기본 예측값
- 빨강(↑): 예측값을 증가시킨 특성
- 파랑(↓): 예측값을 감소시킨 특성

---

## 3. 선형 모델 (회귀, 로지스틱 회귀)

### 3.1 계수(Coefficients) 분석

```python
from sklearn.linear_model import LogisticRegression


def analyze_linear_model(
    model: LogisticRegression,
    feature_names: list[str],
) -> pd.DataFrame:
    """선형 모델의 계수를 분석한다.

    Args:
        model (LogisticRegression): 학습된 선형 모델.
        feature_names (list[str]): 특성 이름.

    Returns:
        pd.DataFrame: 특성, 계수, 절댓값 기준 정렬.

    Logics:
        1. 모델의 계수 추출.
        2. 특성명과 함께 DataFrame 생성.
        3. 절댓값으로 정렬 (영향도 크기).
        4. 계수 부호로 방향 판단 (양수=증가, 음수=감소).

    Example:
        >>> from sklearn.linear_model import LogisticRegression
        >>> model = LogisticRegression()
        >>> model.fit(X_train, y_train)
        >>> coef_df = analyze_linear_model(model, feature_names)
        >>> print(coef_df)
    """
    coefficients = model.coef_[0]

    coef_df = pd.DataFrame({
        'feature': feature_names,
        'coefficient': coefficients,
        'abs_coefficient': np.abs(coefficients)
    })

    coef_df = coef_df.sort_values(
        'abs_coefficient',
        ascending=False
    )

    return coef_df


# 시각화
def plot_linear_coefficients(
    coef_df: pd.DataFrame,
    figsize: tuple = (10, 6),
) -> None:
    """선형 모델 계수를 시각화한다."""
    fig, ax = plt.subplots(figsize=figsize)

    # 양수는 빨강, 음수는 파랑
    colors = ['red' if x > 0 else 'blue'
              for x in coef_df['coefficient']]

    ax.barh(coef_df['feature'], coef_df['coefficient'],
            color=colors, alpha=0.7)
    ax.set_xlabel('계수값')
    ax.set_title('선형 모델 계수 (양수=증가, 음수=감소)')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.show()
```

---

## 4. 부분 의존성(Partial Dependence)

### 4.1 단일 특성 부분 의존성

```python
from sklearn.inspection import plot_partial_dependence


def plot_pdp_single_feature(
    model,
    X_train: pd.DataFrame,
    feature_name: str,
    feature_idx: int,
) -> None:
    """한 특성의 부분 의존성 플롯을 그린다.

    특성 값이 변할 때 모델 예측이 어떻게 변하는지 시각화.

    Args:
        model: 학습된 모델.
        X_train (pd.DataFrame): 학습 데이터.
        feature_name (str): 특성 이름.
        feature_idx (int): 특성 인덱스.

    Logics:
        1. 특성 값을 범위내에서 변경.
        2. 다른 특성은 고정.
        3. 각 특성 값에 대한 평균 예측값 계산.
        4. 곡선으로 시각화.

    Example:
        >>> plot_pdp_single_feature(
        ...     model, X_train, 'age', 0
        ... )
        # 나이가 증가하면서 예측값이 어떻게 변하는지 표시
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    plot_partial_dependence(
        model,
        X_train,
        features=[feature_idx],
        feature_names=X_train.columns.tolist(),
        ax=ax,
        grid_resolution=50
    )

    plt.suptitle(
        f'부분 의존성 플롯: {feature_name}'
    )
    plt.show()
```

**결과 해석**:
- Y축: 모델 예측값 (평균)
- X축: 특성 값
- 곡선이 가파르면: 그 특성이 예측에 큰 영향
- 곡선이 완만하면: 그 특성의 영향 작음

---

## 5. 신경망 모델 해석

### 5.1 Attention Visualization (변환기 모델)

```python
def extract_attention_weights(
    model,
    input_data,
    layer_idx: int = -1,
) -> np.ndarray:
    """신경망 모델의 Attention 가중치를 추출한다.

    Args:
        model: Transformer 기반 모델.
        input_data: 입력 데이터.
        layer_idx (int): 추출할 레이어 인덱스. 기본값 -1 (마지막).

    Returns:
        np.ndarray: Attention 가중치 행렬.

    Logics:
        1. 모델의 특정 레이어의 attention 가중치 추출.
        2. 입력과 출력의 관계를 시각화.
        3. Attention이 어느 입력에 집중하는지 분석.
    """
    # Attention 가중치 추출 (모델 구조에 따라 다름)
    with torch.no_grad():
        outputs = model(
            input_data,
            output_attentions=True
        )
        attention_weights = (
            outputs[-1][layer_idx].cpu().numpy()
        )

    return attention_weights
```

---

## 6. 요약: 모델별 추천 기법

| 모델 타입 | 1차 선택 | 2차 선택 | 3차 선택 |
|----------|---------|---------|---------|
| **랜덤포레스트** | Feature Importance | SHAP | Partial Dependence |
| **XGBoost** | Feature Importance | SHAP | Partial Dependence |
| **로지스틱 회귀** | 계수(Coefficient) | SHAP | Partial Dependence |
| **신경망** | SHAP | Attention (변환기) | Grad-CAM |
| **SVM** | SHAP | Permutation Importance | - |

---

## 7. 체크리스트

구현 후 다음을 확인하세요:

- [ ] 모든 모델에 최소 1가지 해석 기법 적용
- [ ] 프로덕션 배포 전 Feature Importance 검증
- [ ] 비즈니스 팀이 결과를 이해 가능한가?
- [ ] 예측 불일치 시 설명 가능한가?
- [ ] 모델 개선 방향을 도출 가능한가?

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |
| [@skills/convention-data-handling/SKILL.md] | 데이터 처리 |
| [@skills/check-anti-patterns/SKILL.md] | 안티패턴 검출 |

---

## 참고

- SHAP 공식 문서: https://shap.readthedocs.io
- scikit-learn Inspection: https://scikit-learn.org/stable/modules/inspection.html
- Interpretable ML Book: https://christophm.github.io/interpretable-ml-book/

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - Feature Importance, SHAP, Partial Dependence |

## Gotchas (실패 포인트)

- SHAP 값은 feature interaction 고려 안 함 — 복잡한 모델에서 오해 가능
- Feature importance는 데이터셋 의존적 — 다른 데이터에서 달라질 수 있음
- 설명 가능성과 성능은 트레이드오프 — 과도한 설명 요구 시 성능 하락
- 비기술자에게 SHAP plot 설명 시 오해 발생 가능 — 직관적 시각화 필요
