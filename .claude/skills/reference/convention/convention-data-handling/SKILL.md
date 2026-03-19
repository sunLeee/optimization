---
name: convention-data-handling
triggers:
  - "convention data handling"
description: "데이터 처리 컨벤션 참조 스킬. 결측치/이상치 처리, 벡터화, 대용량 데이터 스케일링 등 데이터 엔지니어링 모범 사례를 제공한다. 데이터 처리 시 이 스킬을 참조하여 성능과 정확성을 확보한다."
argument-hint: "[섹션] - missing, outliers, vectorization, scaling"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  데이터 처리의 모범 사례를 제공한다.
  결측치, 이상치, 성능 최적화, 메모리 관리에 대한 가이드를 제시한다.
agent: |
  데이터 처리 최적화 전문가.
  데이터 품질 관리, 벡터화, 대용량 데이터 처리 전략을 명확하게 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 데이터 처리 컨벤션

데이터 엔지니어링 및 분석에서의 모범 사례를 정의한다.

## 목적

- 데이터 품질 향상 (결측치/이상치 처리)
- 성능 최적화 (벡터화)
- 메모리 효율성 (대용량 데이터 관리)
- 재현성 및 추적 가능성 확보

## 사용법

```
/convention-data-handling [섹션]
```

| 섹션 | 설명 |
|------|------|
| `missing` | 결측치 처리 전략 |
| `outliers` | 이상치 탐지 및 처리 |
| `vectorization` | 벡터화 (Pandas/Numpy) |
| `scaling` | 대용량 데이터 처리 |
| `all` | 전체 내용 (기본값) |

---

## 1. 결측치(Missing Data) 처리

### 1.1 결측치 탐지

**규칙**: 데이터 로드 직후 결측치 분석 필수.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""결측치 탐지 및 분석 모듈."""

import pandas as pd
import numpy as np


def analyze_missing_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """결측치를 분석하여 리포트를 생성한다.

    Args:
        df (pd.DataFrame): 분석 대상 DataFrame.

    Returns:
        pd.DataFrame: 결측치 통계.
            - column: 컬럼명
            - missing_count: 결측 개수
            - missing_pct: 결측 비율 (%)

    Logics:
        1. 각 컬럼별 결측치(NaN) 개수 계산.
        2. 결측치 비율(%) 계산.
        3. 결측 비율 기준으로 내림차순 정렬.
        4. 리포트 반환.

    Example:
        >>> df = pd.DataFrame({
        ...     'A': [1, 2, np.nan],
        ...     'B': [np.nan, np.nan, 3]
        ... })
        >>> report = analyze_missing_data(df)
        >>> print(report)
          column  missing_count  missing_pct
        0      B               2   66.666667
        1      A               1   33.333333
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100

    # 리포트 생성
    report = pd.DataFrame({
        'column': df.columns,
        'missing_count': missing_count.values,
        'missing_pct': missing_pct.values
    })

    # 결측 비율 기준 정렬
    report = report.sort_values(
        'missing_pct',
        ascending=False
    )

    return report.reset_index(drop=True)
```

### 1.2 결측치 처리 전략

| 전략 | 사용 사례 | 코드 예시 |
|------|---------|----------|
| **제거** | 결측치 비율 < 5% | `df.dropna()` |
| **평균값 충전** | 수치형, 정규분포 | `df.fillna(df.mean())` |
| **중앙값 충전** | 수치형, 이상치 있을 때 | `df.fillna(df.median())` |
| **최빈값 충전** | 범주형 데이터 | `df.fillna(df.mode()[0])` |
| **Forward Fill** | 시계열 데이터 | `df.fillna(method='ffill')` |
| **Interpolation** | 시계열 보간 | `df.interpolate()` |
| **모델링** | 복잡한 패턴 | KNN Imputer, MICE |

### 1.3 결측치 처리 예시

```python
def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = 'mean',
) -> pd.DataFrame:
    """결측치를 처리한다.

    Args:
        df (pd.DataFrame): 입력 DataFrame.
        strategy (str): 처리 전략.
            - 'drop': 결측치 행 제거
            - 'mean': 평균값으로 충전
            - 'median': 중앙값으로 충전
            - 'forward_fill': 앞값으로 충전

    Returns:
        pd.DataFrame: 처리된 DataFrame.

    Logics:
        1. strategy 별로 처리 방식 선택.
        2. 수치형/범주형 구분 처리.
        3. 처리 후 결측치 재확인.
    """
    df_copy = df.copy()

    if strategy == 'drop':
        # 결측치 행 제거 (비율 < 5%일 때만)
        if df_copy.isnull().sum().sum() / (
            len(df_copy) * len(df_copy.columns)
        ) < 0.05:
            df_copy = df_copy.dropna()
        else:
            raise ValueError("결측치 비율이 높아 제거 불가")

    elif strategy == 'mean':
        # 수치형: 평균값, 범주형: 최빈값
        numeric_cols = df_copy.select_dtypes(
            include=['number']
        ).columns
        categorical_cols = df_copy.select_dtypes(
            include=['object']
        ).columns

        df_copy[numeric_cols] = df_copy[
            numeric_cols
        ].fillna(df_copy[numeric_cols].mean())
        df_copy[categorical_cols] = df_copy[
            categorical_cols
        ].fillna(df_copy[categorical_cols].mode()[0])

    elif strategy == 'median':
        numeric_cols = df_copy.select_dtypes(
            include=['number']
        ).columns
        df_copy[numeric_cols] = df_copy[
            numeric_cols
        ].fillna(df_copy[numeric_cols].median())

    elif strategy == 'forward_fill':
        # 시계열 데이터: 앞값으로 충전
        df_copy = df_copy.fillna(method='ffill')

    return df_copy
```

---

## 2. 이상치(Outliers) 처리

### 2.1 이상치 탐지

**규칙**: IQR(Interquartile Range) 방식 사용.

```python
def detect_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    multiplier: float = 1.5,
) -> pd.DataFrame:
    """IQR 방식으로 이상치를 탐지한다.

    Args:
        df (pd.DataFrame): 입력 DataFrame.
        column (str): 대상 컬럼명.
        multiplier (float): IQR 배수 (기본값 1.5).

    Returns:
        pd.DataFrame: 이상치 여부 컬럼 추가된 DataFrame.

    Logics:
        1. Q1(25%ile) 계산.
        2. Q3(75%ile) 계산.
        3. IQR = Q3 - Q1.
        4. 하한 = Q1 - multiplier * IQR.
        5. 상한 = Q3 + multiplier * IQR.
        6. 범위 밖 데이터를 이상치로 표시.

    Example:
        >>> df = pd.DataFrame({
        ...     'value': [1, 2, 3, 4, 100]
        ... })
        >>> result = detect_outliers_iqr(df, 'value')
        >>> print(result[result['is_outlier']])
        index  value  is_outlier
        4      100     True
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    df_copy = df.copy()
    df_copy['is_outlier'] = (
        (df_copy[column] < lower_bound) |
        (df_copy[column] > upper_bound)
    )

    return df_copy
```

### 2.2 이상치 처리 전략

| 전략 | 사용 시점 | 방법 |
|------|---------|------|
| **제거** | 에러성 이상치 | `df[~df['is_outlier']]` |
| **Capping** | 극단값 제한 | `df.clip(lower, upper)` |
| **Log 변환** | 정규화 | `np.log1p(df)` |
| **Robust 스케일** | 이상치 고려 | (x - median) / IQR |

---

## 3. 벡터화(Vectorization)

### 3.1 핵심 원칙

**규칙**: `for` 루프 금지. Pandas/Numpy 벡터 연산 사용.

| ❌ 금지 (느림) | ✅ 권장 (빠름) | 성능 향상 |
|-------------|-----------|---------|
| `for i in range(len(df)):` | `df.apply()` | 10배 |
| `df.apply(lambda x: ...)` | 벡터 연산 | 100배 |
| Pandas loop | Numpy 배열 | 1000배 |

### 3.2 벡터화 예시

```python
# ❌ 느린 코드 (for 루프)
def slow_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """정규화를 for 루프로 수행 (NO!)"""
    df_copy = df.copy()
    for col in df.columns:
        max_val = df[col].max()
        min_val = df[col].min()
        for i in range(len(df)):
            df_copy[col].iloc[i] = (
                df_copy[col].iloc[i] - min_val
            ) / (max_val - min_val)
    return df_copy


# ✅ 빠른 코드 (벡터화)
def fast_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """정규화를 벡터 연산으로 수행 (YES!)"""
    # 방법 1: Pandas 벡터 연산
    return (df - df.min()) / (df.max() - df.min())


# 성능 비교
import time

df_large = pd.DataFrame(
    np.random.randn(100000, 100)
)

# 느린 방식 (약 60초)
# start = time.time()
# slow_normalize(df_large)
# print(f"느린 코드: {time.time() - start:.2f}초")

# 빠른 방식 (약 0.1초)
start = time.time()
fast_normalize(df_large)
print(f"빠른 코드: {time.time() - start:.2f}초")
```

### 3.3 일반적인 벡터화 패턴

```python
# 조건부 처리
# ❌ 느림
result = []
for val in series:
    if val > threshold:
        result.append(val * 2)
    else:
        result.append(val)

# ✅ 빠름
result = series.where(
    series > threshold,
    series
) * series.where(series > threshold, 1)
# 또는
result = np.where(
    series > threshold,
    series * 2,
    series
)

# 그룹별 연산
# ❌ 느림
for group in df['category'].unique():
    subset = df[df['category'] == group]
    mean_val = subset['value'].mean()

# ✅ 빠름
df.groupby('category')['value'].transform('mean')
```

---

## 4. 대용량 데이터 처리 (Scaling)

### 4.1 메모리 효율화

**규칙**: 불필요한 복사 방지, dtype 최적화.

```python
def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame의 메모리 사용을 최적화한다.

    Args:
        df (pd.DataFrame): 최적화 대상 DataFrame.

    Returns:
        pd.DataFrame: 최적화된 DataFrame.

    Logics:
        1. 각 컬럼의 데이터 타입 분석.
        2. 수치형: 더 작은 타입으로 변환.
           - int64 → int32 또는 int8
           - float64 → float32
        3. 문자형: category로 변환 (반복되는 값).
        4. 메모리 사용량 출력.

    Example:
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 35],
        ...     'category': ['A', 'B', 'A']
        ... })
        >>> optimized = optimize_dtypes(df)
        >>> print(df.memory_usage(deep=True))
        >>> print(optimized.memory_usage(deep=True))
    """
    df_opt = df.copy()
    orig_memory = df.memory_usage(deep=True).sum()

    # 수치형 최적화
    for col in df_opt.columns:
        col_type = df_opt[col].dtype

        if col_type == 'int64':
            # int 범위 확인 후 축소
            if df_opt[col].min() >= 0:
                if df_opt[col].max() < 256:
                    df_opt[col] = df_opt[col].astype('uint8')
                elif df_opt[col].max() < 65536:
                    df_opt[col] = df_opt[col].astype('uint16')
            else:
                if (
                    df_opt[col].min() > -128 and
                    df_opt[col].max() < 128
                ):
                    df_opt[col] = df_opt[col].astype('int8')

        elif col_type == 'float64':
            df_opt[col] = df_opt[col].astype('float32')

        elif col_type == 'object':
            # 중복값이 많으면 category로 변환
            num_unique = len(df_opt[col].unique())
            num_total = len(df_opt[col])
            if num_unique / num_total < 0.5:
                df_opt[col] = df_opt[col].astype(
                    'category'
                )

    opt_memory = df_opt.memory_usage(deep=True).sum()
    reduction = (
        (orig_memory - opt_memory) / orig_memory * 100
    )

    print(
        f"메모리 절감: {reduction:.2f}% "
        f"({orig_memory / 1024**2:.2f}MB → "
        f"{opt_memory / 1024**2:.2f}MB)"
    )

    return df_opt
```

### 4.2 청킹(Chunking) - 대용량 파일 읽기

```python
def read_large_csv_chunked(
    filepath: str,
    chunksize: int = 10000,
) -> pd.DataFrame:
    """대용량 CSV를 청크 단위로 읽어 처리한다.

    Args:
        filepath (str): CSV 파일 경로.
        chunksize (int): 청크 크기 (행 수).

    Returns:
        pd.DataFrame: 처리된 전체 DataFrame.

    Logics:
        1. CSV를 chunksize 단위로 읽음.
        2. 각 청크를 처리 (정규화, 필터링 등).
        3. 처리된 청크를 누적.
        4. 최종 결과 반환.

    Example:
        >>> df = read_large_csv_chunked(
        ...     'data/sales.csv',
        ...     chunksize=50000
        ... )
    """
    chunks = []

    # CSV를 청크 단위로 읽음
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        # 각 청크 처리
        chunk_processed = (
            chunk
            .dropna()  # 결측치 제거
            .loc[chunk['amount'] > 0]  # 필터링
        )
        chunks.append(chunk_processed)

    # 모든 청크 병합
    result = pd.concat(chunks, ignore_index=True)

    return result
```

### 4.3 Dask를 이용한 병렬 처리

```python
import dask.dataframe as dd


def process_with_dask(filepath: str) -> dd.DataFrame:
    """Dask를 이용하여 병렬 처리한다.

    Args:
        filepath (str): 입력 파일 경로.

    Returns:
        dd.DataFrame: Dask DataFrame.

    Logics:
        1. Dask DataFrame 생성 (청크 단위 자동 분할).
        2. 연산 정의 (실행 미룸).
        3. compute()로 실행.

    Example:
        >>> ddf = process_with_dask('data/large.csv')
        >>> result = ddf.groupby('category')[
        ...     'amount'
        ... ].mean().compute()
    """
    # Dask로 DataFrame 읽기 (자동 분할)
    ddf = dd.read_csv(filepath)

    # 연산 정의
    result = (
        ddf
        .dropna()
        .groupby('category')['amount']
        .mean()
    )

    # 실행
    return result.compute()
```

---

## 5. 데이터 품질 체크리스트

코드 작성 후 다음을 확인하세요:

- [ ] 결측치 분석: `df.isnull().sum()` 확인
- [ ] 결측치 처리: 전략 문서화 및 적용
- [ ] 이상치 탐지: IQR 또는 Z-score 적용
- [ ] 벡터화: for 루프 제거 확인
- [ ] 메모리 최적화: dtype 변환 확인
- [ ] 성능 측정: 대용량 데이터 테스트
- [ ] 재현성: random seed 고정 (필요시)

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-python/SKILL.md] | Python 코딩 컨벤션 |
| [@skills/convention-reproducibility/SKILL.md] | 재현성 (random seed 관리) |
| [@skills/check-python-style/SKILL.md] | Python 스타일 검증 |
| [@skills/code-review/SKILL.md] | 코드 리뷰 |

---

## 참고

- Pandas 공식 문서: https://pandas.pydata.org
- Numpy 벡터화: https://numpy.org/doc/stable/reference/ufuncs.html
- Dask 병렬 처리: https://dask.pydata.org

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - 결측치, 이상치, 벡터화, 스케일링 |

## Gotchas (실패 포인트)

- iterrows() 사용 시 대용량 데이터에서 수백 배 느림 → vectorized 연산 사용
- inplace=True 사용 시 예상치 못한 원본 변경 — .copy() 또는 새 변수 할당
- chained indexing `df['a']['b']` → SettingWithCopyWarning — .loc 사용
- NaN 처리 전 비교 연산 금지 — NaN == NaN은 False
