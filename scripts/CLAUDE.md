# scripts/ — 실행 스크립트

## 실행 방법

**반드시 `uv run`으로 실행**:

```bash
uv run python scripts/benchmark_benders.py --n 80 --tugs 20 --berths 6
```

직접 `python scripts/...` 실행 시 `libs` import 오류 발생 가능.

## 파일 목록

| 파일 | 용도 | 주요 옵션 |
|------|------|---------|
| `benchmark_benders.py` | Phase 3a/3b 성능 비교 | `--n`, `--tugs`, `--berths`, `--compare-gamma` |
| `run_simulation.py` | 전체 시뮬레이션 실행 | — |
| `download_papers.py` | 논문 PDF 다운로드 | — |
| `harbor_dashboard.py` | Streamlit 대시보드 | — |

## benchmark_benders.py 사용법

```bash
# Phase 3a vs 3b 연료비 비교 (Phase 3b 필요성 판단)
uv run python scripts/benchmark_benders.py --n 12 --tugs 4 --berths 4 --compare-gamma

# large_n80 성능 검증 (gap ≤ 5%, time ≤ 30min)
uv run python scripts/benchmark_benders.py --n 80 --tugs 20 --berths 6

# Phase 3b (v^2.5 속도최적화) 포함
uv run python scripts/benchmark_benders.py --n 12 --mode both
```

## 새 스크립트 작성 시

```python
# 파일 상단에 반드시 추가 (uv run 없이 직접 실행 지원)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## 품질 게이트 (AW-008)

```bash
bash .claude/check-criteria.sh --score   # ≥ 90 목표
```
