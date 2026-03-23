# ADR-007: 대시보드 탭 확장 방식

**날짜**: 2026-03-22
**상태**: Accepted
**작성자**: harbor-real-data-opt ralplan 합의

---

## Decision

`scripts/harbor_dashboard.py`의 기존 3탭 구조를 6탭으로 확장한다. 별도 페이지(`pages/`) 분리 없이 단일 파일 방식 유지.

### 신규 탭 3개

| 탭 번호 | 탭명 | 의존 데이터 | 주요 컴포넌트 |
|---------|------|------------|-------------|
| 탭 4 | `실증 비교` | `results/objective_comparison.csv` | 4종 KPI × 4전략 바 차트 (4 subplot) |
| 탭 5 | `KPI 분포` | `results/objective_comparison.csv` | ETA 편차 히스토그램 + 목적함수별 비용 박스플롯 |
| 탭 6 | `목적함수 가이드` | 정적 텍스트 | OBJ-A/B/C/D 특성 표 + 시나리오별 권장 전략 |

### Graceful Degradation

탭 4, 5는 `results/objective_comparison.csv`가 없으면 안내 메시지 표시:

```python
csv_path = pathlib.Path("results/objective_comparison.csv")
if not csv_path.exists():
    st.info(
        "실험 결과 파일이 없습니다. "
        "`make experiment`를 먼저 실행하세요.\n\n"
        "```bash\nmake experiment\n```"
    )
else:
    df = pd.read_csv(csv_path)
    # ... 차트 렌더링
```

### 구현 방식

```python
# 기존 (3탭)
tab1, tab2, tab3 = st.tabs(["시뮬레이션", "최적화 비교", "Phase 3"])

# 변경 후 (6탭)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "시뮬레이션", "최적화 비교", "Phase 3",
    "실증 비교", "KPI 분포", "목적함수 가이드"
])
```

---

## Drivers

1. **기존 탭 회귀 방지**: 탭 1~3 내용 완전 유지 — 기존 사용자 워크플로우 불변
2. **사이드바 설정 공유**: `pages/` 분리 시 사이드바 파라미터 공유가 복잡해짐 (Streamlit 멀티페이지 제약)
3. **개발 단순성**: 단일 파일 구조 → 탭 간 데이터 공유 용이 (`@st.cache_data` 공유)

---

## Alternatives

### Option A — `pages/` 디렉토리 분리 (거부)

```
scripts/
├── harbor_dashboard.py   # 메인 (탭 1~3)
└── pages/
    ├── 4_실증비교.py
    ├── 5_KPI분포.py
    └── 6_목적함수가이드.py
```

**거부 이유**:
- 사이드바 파라미터(예인선 수, 선석 수 등)를 `st.session_state`로 공유해야 함 → 복잡도 증가
- Streamlit 멀티페이지에서 `@st.cache_data` 공유가 제한됨
- 기존 3탭을 변경하지 않는 반면 새 3탭은 `pages/`에 있어 구조 불일치

### Option B — 기존 탭에 섹션 추가 (거부)

기존 탭 3(`Phase 3`) 내부에 섹션을 추가하는 방식.

**거부 이유**:
- 탭 3이 비대해짐
- 실증 비교는 Phase 3와 독립적인 관심사 → 별도 탭이 적절

---

## Consequences

### Positive
- 기존 탭 1~3 코드 무변경 (회귀 없음)
- 탭 6(`목적함수 가이드`)은 정적 내용으로 CSV 의존 없음 → 항상 렌더링 가능
- `make dashboard-check` (AST parse)로 문법 오류 CI 검증 가능

### Negative
- 단일 파일이 커질 수 있음 (현재 ~400 LOC → 탭 추가 후 ~600 LOC 예상)
- 탭 4~6이 `results/objective_comparison.csv` 의존 → graceful degradation 필수

### Risks
- 파일이 800 LOC 이상으로 커지면 `pages/` 분리 고려 (ADR-007 v2 대상)

---

## Follow-ups

- `make dashboard-check`: AST parse 검증 + 수동 런타임 확인 병행 권장
- 파일 800 LOC 초과 시 `pages/` 분리 고려 (ADR-007 개정)
- 탭 5 KPI 분포는 `data/raw/scheduling/data/2024-06_SchData.csv` 직접 로드 고려
