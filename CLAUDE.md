# 항구 최적화 프로젝트 (Harbor Optimization)

## 프로젝트 개요

항구 운영 최적화 시스템. 예인선(Tugboat), 대형선박(Vessel), 항구(Port/Berth) 간의
스케줄·경로·연료 최적화를 수학적 최적화 기법으로 해결한다.

### 핵심 최적화 문제

| 문제 유형 | 설명 | 관련 문제 클래스 |
|-----------|------|----------------|
| 스케줄 최적화 | 예인선 배치 타임라인 최적화 | Tugboat Scheduling Problem (TSP-T) |
| 경로 최적화 | 예인선 이동 경로 최적화 | VRP with Time Windows (VRPTW) |
| 연료 최적화 | 속도-연료 관계 기반 소비 최소화 | Multi-objective Maritime Opt. |
| 선석 배분 | 선박-선석 매칭 및 시간 배분 | Berth Allocation Problem (BAP) |

### 불확실성 모델

- 선박 도착 스케줄은 **사전 확정**이 기본 가정
- 날씨 조건에 따라 도착 시간 ±2시간 변동 가능
- 확률분포: 정규분포 N(0, σ) 또는 균등분포 U(-2, +2) 가정
- Stochastic Programming 또는 Robust Optimization 접근

## 기술 스택

- **언어**: Python 3.11+
- **최적화**: (라이브러리 선정 중 → `docs/research/optimization_libraries.md` 참조)
- **수학적 formulation**: `docs/research/mathematical_formulation.md` 참조
- **알고리즘 선택**: `docs/research/algorithm_selection.md` 참조

## 리서치 문서 구조

```
docs/research/
├── optimization_libraries.md    # Python 최적화 라이브러리 비교 (유/무료)
├── mathematical_formulation.md  # 논문 기반 수학적 formulation
├── algorithm_selection.md       # Big-O 복잡도별 알고리즘 가이드
├── stochastic_scheduling.md     # 확률적 스케줄링 불확실성 처리
└── papers/                      # 인용 논문 원문/요약
```

## 개발 원칙

- 커스터마이징 자유도 우선: OR-Tools VRP의 블랙박스 한계를 인지하고, 직접 구현 가능한 솔버 우선 검토
- Exact solution은 소규모(n<15)에만 적용; 중·대규모는 metaheuristic 또는 decomposition
- 확률적 스케줄링: 날씨 불확실성은 2-stage stochastic programming으로 처리
- 연료 모델: fuel ∝ v³ (속도 세제곱 관계) 기반 비선형 목적함수

## 현재 상태

- [x] 프로젝트 구조 정의
- [x] 리서치 디렉토리 생성
- [ ] 최적화 라이브러리 선정
- [ ] 수학적 formulation 확정
- [ ] 알고리즘 프로토타입 구현
