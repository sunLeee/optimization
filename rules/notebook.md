---
paths:
  - "notebooks/**/*.ipynb"
  - "*.ipynb"
---

# Jupyter 노트북 핵심 원칙

| 원칙 | 필수 |
|------|------|
| **셀 순서** | 위에서 아래로 순차 실행 가능 |

**상세**: "Restart Kernel & Run All"로 순차 실행 검증 필수. 셀 간 숨은 의존성 제거.

| **출력 정리** | 커밋 전 출력 셀 정리 (nbstripout) |

**상세**: pre-commit에 nbstripout 설정. 출력/메타데이터 제거로 diff 충돌 방지. 이미지 출력은 별도 저장.

| **재현성** | 랜덤 시드 고정, 버전 명시 |

**상세**: `np.random.seed(42)`, `torch.manual_seed(42)` 설정. 첫 셀에 라이브러리 버전 출력.

| **파일명** | `{순번}-{설명}.ipynb` 형식 (kebab-case) |

**상세**: `01-data-exploration.ipynb`, `02-feature-engineering.ipynb` 형태. 실행 순서 명확화.

| **모듈화** | 재사용 코드는 .py로 분리 |

**상세**:
- 노트북 내 함수 정의 **3개 이하** 유지
- 3회 이상 사용되는 함수는 `src/` 모듈로 분리
- `%autoreload` 매직으로 실시간 반영

**자동화**: [@skills/extract-module-from-notebook/SKILL.md]로 자동 추출 가능

**상세 가이드**: [@skills/convention-jupyter-setup/SKILL.md] 참조
