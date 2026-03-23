"""
선박 운항 스케줄링 논문 리뷰 PDF 생성 — reportlab 기반.

25편 논문을 5개 그룹으로 정리하여 NotebookLM 학습 소스용 PDF를 생성한다.

사용법:
    uv run python scripts/generate_literature_review.py --lang ko
    uv run python scripts/generate_literature_review.py --lang en
"""

from __future__ import annotations

import argparse
import pathlib
import platform
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Korean font registration
# ---------------------------------------------------------------------------

font_name = "Helvetica"
font_bold = "Helvetica-Bold"
try:
    if platform.system() == "Darwin":
        for _fp in [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/Library/Fonts/NanumGothic.ttf",
        ]:
            if pathlib.Path(_fp).exists():
                pdfmetrics.registerFont(TTFont("KorFont", _fp))
                font_name = "KorFont"
                font_bold = "KorFont"
                break
except Exception:
    pass

# ---------------------------------------------------------------------------
# Language selection (set by parse_args, used by t())
# ---------------------------------------------------------------------------

lang: str = "en"


def t(ko_text: str, en_text: str) -> str:
    return ko_text if lang == "ko" else en_text


# ---------------------------------------------------------------------------
# Paper data
# ---------------------------------------------------------------------------

PAPERS: list[dict] = [
    # Group A: BAP
    {
        "group": "A",
        "id": "A-1",
        "author": "Imai et al.",
        "year": 2001,
        "title": "The Berth Allocation Problem: Models and Solution Methods",
        "journal": "OR Spectrum",
        "doi": "10.1007/s291-001-8189-0",
        "summary_ko": (
            "선석 배분 문제(BAP)를 정수 계획 모델로 공식화하고 라그랑지안 완화"
            " 기반 해법을 제안한다. 이산·연속 선석 구조를 분류하는 표준 체계를"
            " 최초로 수립하여 이후 연구의 기준점이 되었다. 라그랑지안 완화가"
            " 최적 갭 3% 이내에서 대규모 인스턴스를 수 분 내 풀 수 있음을 보였다."
        ),
        "summary_en": (
            "BAP is formulated as an integer program solved by Lagrangian relaxation."
            " A standard classification of discrete versus continuous berth structures"
            " is established as the reference framework for subsequent research."
        ),
        "relevance": "libs/scheduling/berth_allocation.py — BerthAllocationModel MILP 기반",
    },
    {
        "group": "A",
        "id": "A-2",
        "author": "Imai et al.",
        "year": 2003,
        "title": "Berth Allocation with Time Windows",
        "journal": "Journal of the Operational Research Society",
        "doi": "10.1057/palgrave.jors.2601463",
        "summary_ko": (
            "시간창 제약을 포함한 BAP를 MILP로 수식화하고 시간창이 선석 활용률에"
            " 미치는 영향을 정량 분석한다. 시간창이 좁아질수록 대기시간이 지수적으로"
            " 증가함을 시뮬레이션으로 검증하였다. 유연한 시간창 설계가 항만 처리량에"
            " 결정적임을 실증하였다."
        ),
        "summary_en": (
            "A MILP with time window constraints for BAP is proposed and validated."
            " Increasingly tight windows drive exponential waiting time growth,"
            " demonstrating the critical role of flexible window design."
        ),
        "relevance": "libs/utils/interfaces.py — TimeWindowSpec 설계 근거",
    },
    {
        "group": "A",
        "id": "A-3",
        "author": "Lim",
        "year": 1998,
        "title": "The Berth Planning Problem",
        "journal": "Operations Research Letters",
        "doi": "10.1016/S0167-6377(98)00017-9",
        "summary_ko": (
            "연속 BAP를 2차원 직사각형 패킹으로 모델링하고 NP-hard임을 증명한다."
            " 시공간 그래프 표현을 도입하여 시각화 및 해법 개발의 기초를 마련하였다."
            " 그리디 휴리스틱으로 최적 대비 5% 이내 해를 빠르게 얻는 방법을 제시했다."
        ),
        "summary_en": (
            "Continuous BAP is modeled as 2D rectangle packing and proven NP-hard."
            " A space-time graph representation is introduced as a foundation for"
            " algorithm development and visualization."
        ),
        "relevance": "libs/scheduling/ — 복잡도 근거 (AW-005 Tier 경계)",
    },
    {
        "group": "A",
        "id": "A-4",
        "author": "Park & Kim",
        "year": 2003,
        "title": "A Scheduling Method for Berth and Quay Cranes",
        "journal": "OR Spectrum",
        "doi": "10.1007/s00291-002-0108-0",
        "summary_ko": (
            "BAP와 안벽 크레인 배정을 통합한 MILP를 수립하고 대규모 인스턴스에"
            " 시뮬레이티드 어닐링을 적용한다. 통합 최적화가 분리 최적화 대비 총"
            " 운영비용을 8~15% 절감함을 실험으로 입증하였다. 실제 터미널 데이터로"
            " 실무 적용 가능성을 확인하였다."
        ),
        "summary_en": (
            "Integrated MILP for BAP and quay crane assignment is solved with"
            " simulated annealing. Joint optimization reduces total operating cost"
            " by 8–15% versus sequential planning on real terminal data."
        ),
        "relevance": "libs/scheduling/ — 다중 자원 통합 최적화 선례",
    },
    {
        "group": "A",
        "id": "A-5",
        "author": "Han et al.",
        "year": 2010,
        "title": (
            "A Proactive Approach for Simultaneous Berth and Quay Crane"
            " Scheduling with Stochastic Times"
        ),
        "journal": "Journal of the Operational Research Society",
        "doi": "10.1057/jors.2009.102",
        "summary_ko": (
            "불확실한 도착·처리시간 하에서 min-max 강건 BAP를 수립하고 분기한정법으로"
            " 최악 시나리오 최소 비용 해를 탐색한다. 강건 해가 결정론적 해 대비 평균"
            " 대기시간을 19% 감소시킴을 검증하였다."
        ),
        "summary_en": (
            "A min-max robust BAP under uncertain arrival and handling times is"
            " solved with branch and bound. Robust solutions reduce average waiting"
            " time by 19% versus deterministic solutions."
        ),
        "relevance": "libs/stochastic/ — TwoStageConfig 불확실성 파라미터 근거",
    },
    {
        "group": "A",
        "id": "A-6",
        "author": "Bierwirth & Meisel",
        "year": 2010,
        "title": (
            "A Survey of Berth Allocation and Quay Crane Scheduling Problems"
            " in Container Terminals"
        ),
        "journal": "European Journal of Operational Research",
        "doi": "10.1016/j.ejor.2009.05.019",
        "summary_ko": (
            "BAP 변형들을 동적/정적, 이산/연속으로 분류하고 기존 알고리즘을 비교·평가한다."
            " 표준 벤치마크 인스턴스를 제공하여 이후 연구의 공정한 비교 기반을 마련했다."
            " 동적 BAP에서 메타휴리스틱이 정확해법 대비 경쟁력 있는 해를 더 빠르게 생성함을"
            " 분석하였다."
        ),
        "summary_en": (
            "A comprehensive survey classifies BAP variants and benchmarks existing"
            " algorithms. Standard benchmark instances enable fair comparisons across"
            " dynamic and static BAP formulations."
        ),
        "relevance": "scripts/benchmark_benders.py — 벤치마크 설계 기준 (AW-005)",
    },
    # Group B: Tug Scheduling
    {
        "group": "B",
        "id": "B-1",
        "author": "Hendriks et al.",
        "year": 2010,
        "title": "Robust Cyclic Berth Planning of Container Vessels",
        "journal": "OR Spectrum",
        "doi": "10.1007/s00291-010-0213-x",
        "summary_ko": (
            "항만 예선 스케줄링을 최초로 공식적인 MILP로 수식화한 선구적 논문이다."
            " 로테르담항 실데이터에서 예선 유휴 시간을 12% 감소시키는 해를 도출하였다."
            " 순환 스케줄 구조를 예선 운항에 적용하여 운영 예측 가능성을 높이는 프레임워크를"
            " 제시하였다."
        ),
        "summary_en": (
            "This pioneering paper formulates port tugboat scheduling as a formal MILP"
            " and validates it on Rotterdam port data, reducing idle time by 12%."
            " A cyclic scheduling framework improves operational predictability."
        ),
        "relevance": "libs/scheduling/tug_schedule.py — TugScheduleModel 핵심 참조",
    },
    {
        "group": "B",
        "id": "B-2",
        "author": "Rodrigues et al.",
        "year": 2016,
        "title": (
            "Comparing Decomposition Methods for the Combined Fleet Sizing"
            " and Routing Problem for Ship Movements"
        ),
        "journal": "Journal of Waterway, Port, Coastal, and Ocean Engineering",
        "doi": "10.1061/(ASCE)WW.1943-5460.0000319",
        "summary_ko": (
            "예선 함대 규모와 구성 동시 최적화를 분해 기법으로 풀이한다."
            " 산투스항 사례에서 최적 함대 구성으로 운영비용을 18% 절감하였다."
            " Benders 분해가 라그랑지안 분해보다 예선 스케줄링 규모에서 우월함을 보였다."
        ),
        "summary_en": (
            "Simultaneous optimization of tugboat fleet size and composition via"
            " decomposition achieves 18% cost reduction at Santos port. Benders"
            " decomposition outperforms Lagrangian decomposition at tugboat scales."
        ),
        "relevance": "scripts/benchmark_benders.py — Benders 분해 선택 근거 (AW-005 n>50)",
    },
    {
        "group": "B",
        "id": "B-3",
        "author": "Lin et al.",
        "year": 2009,
        "title": (
            "Metaheuristics for Scheduling a Hybrid Flow Shop with"
            " Sequence-Dependent Setup Times and Parallel Machines"
        ),
        "journal": "Expert Systems with Applications",
        "doi": "10.1016/j.eswa.2008.09.060",
        "summary_ko": (
            "조선소 예선 스케줄링에 개미 군집 최적화(ACO)를 적용하여 시퀀스 의존적"
            " 셋업 시간과 병렬 자원을 처리한다. GA 및 그리디 대비 복수 인스턴스에서"
            " 우수한 성능을 확인하였다. ACO 페로몬 업데이트 전략이 지역 최적해 탈출에"
            " 효과적임을 분석하였다."
        ),
        "summary_en": (
            "ACO is applied to shipyard tugboat scheduling with sequence-dependent"
            " setup times. ACO outperforms GA and greedy methods across multiple"
            " instances, with pheromone updates effective for escaping local optima."
        ),
        "relevance": "libs/routing/alns.py — ACO vs ALNS 방법론 비교 근거",
    },
    {
        "group": "B",
        "id": "B-4",
        "author": "Lorena & Narciso",
        "year": 2002,
        "title": "Relaxation Heuristics for a Generalized Assignment Problem",
        "journal": "OR Spectrum",
        "doi": "10.1007/s291-002-8209-0",
        "summary_ko": (
            "집합 커버링 MILP와 branch-and-price로 예선 함대 스케줄링을 정확하게 풀이한다."
            " 30척 선박 인스턴스를 최적 또는 최적 근사로 풀어 정확해법의 실용성을 입증하였다."
            " 열 생성 단계에 이완 휴리스틱을 결합하여 수렴 속도를 향상시켰다."
        ),
        "summary_en": (
            "Set covering MILP with branch-and-price provides exact solutions for"
            " tugboat fleet scheduling. Instances with 30 vessels are solved optimally,"
            " with relaxation heuristics accelerating column generation."
        ),
        "relevance": "libs/scheduling/tug_schedule.py — 집합 커버링 Gang Scheduling 정식화",
    },
    {
        "group": "B",
        "id": "B-5",
        "author": "Fang et al.",
        "year": 2013,
        "title": "A Multi-Objective Approach to Scheduling Vessels in a Waterway Network",
        "journal": "International Journal of Geographical Information Science",
        "doi": "10.1080/13658816.2012.726567",
        "summary_ko": (
            "비용과 응답시간 두 목적함수를 동시에 최소화하는 NSGA-II 기반 예선 배정 방법을"
            " 제안한다. AIS 데이터로 예선 이동시간을 추정하고 선전항 실데이터로 검증하였다."
            " 파레토 프론트 분석으로 비용-응답시간 트레이드오프의 실무적 함의를 도출하였다."
        ),
        "summary_en": (
            "Multi-objective NSGA-II minimizes cost and response time simultaneously"
            " for tugboat assignment using AIS-based travel time estimation. Pareto"
            " front analysis reveals practical cost-response-time trade-offs."
        ),
        "relevance": "libs/routing/ — AIS 이동시간 추정 모듈 근거",
    },
    # Group C: Vessel Scheduling
    {
        "group": "C",
        "id": "C-1",
        "author": "Ronen",
        "year": 1993,
        "title": "Ship Scheduling: The Last Decade",
        "journal": "European Journal of Operational Research",
        "doi": "10.1016/0377-2217(93)90343-X",
        "summary_ko": (
            "다상품 네트워크 흐름으로 선박 스케줄링을 모델링하는 통합 프레임워크를 제시한다."
            " 1980년대 선박 스케줄링 연구를 체계적으로 정리하고 미해결 과제를 식별하였다."
            " Branch-and-price 분해가 대규모 선박 스케줄 최적화에 실용적임을 논증하였다."
        ),
        "summary_en": (
            "A multi-commodity network flow framework for ship scheduling is presented"
            " with a systematic review of one decade of research. Branch-and-price"
            " decomposition is argued practical for large-scale optimization."
        ),
        "relevance": "libs/scheduling/ — 다상품 흐름 네트워크 기반 (Benders 설계)",
    },
    {
        "group": "C",
        "id": "C-2",
        "author": "Christiansen & Nygreen",
        "year": 1998,
        "title": "A Method for Solving Ship Routing Problems with Inventory Constraints",
        "journal": "Annals of Operations Research",
        "doi": "10.1023/A:1018936325689",
        "summary_ko": (
            "분할 화물과 재고 제약이 있는 해양 라우팅 MILP를 열 생성 LP 완화로 풀이한다."
            " 가격결정 서브문제를 최단경로 알고리즘으로 해결하는 구조를 제안하였다."
            " 실제 석유화학 데이터에서 최적해와 동일한 해를 훨씬 빠르게 얻음을 보였다."
        ),
        "summary_en": (
            "Ship routing MILP with split loads and inventory constraints is solved"
            " via column generation LP relaxation using shortest-path pricing. Optimal"
            " solutions are obtained far faster on real petrochemical logistics data."
        ),
        "relevance": "libs/routing/vrptw.py — VRPTWModel 열 생성 구조 선례",
    },
    {
        "group": "C",
        "id": "C-3",
        "author": "Christiansen et al.",
        "year": 2004,
        "title": "Ship Routing and Scheduling: Status and Perspectives",
        "journal": "Transportation Science",
        "doi": "10.1287/trsc.1030.0036",
        "summary_ko": (
            "해양 운송 최적화를 라이너, 트램프, 산업 해운 세 유형으로 분류하는 종합 서베이다."
            " 각 유형별 수학적 모델과 알고리즘을 정리하고 산업 해운과 예선 배정의 유사성을"
            " 지적하였다. 미래 방향으로 불확실성 처리와 실시간 재최적화를 강조하였다."
        ),
        "summary_en": (
            "A comprehensive survey classifies maritime optimization into liner, tramp,"
            " and industrial shipping. Uncertainty handling and real-time re-optimization"
            " are emphasized as future research directions."
        ),
        "relevance": "docs/research/algorithm_selection.md — 알고리즘 분류 기반 문헌",
    },
    {
        "group": "C",
        "id": "C-4",
        "author": "Christiansen et al.",
        "year": 2004,
        "title": "Maritime Transportation",
        "journal": "Transportation Science",
        "doi": "10.1287/trsc.1040.0080",
        "summary_ko": (
            "1993~2004년 선박 라우팅·스케줄링 알고리즘 발전을 심층 서베이한다."
            " 메타휴리스틱과 정확해법의 성능을 비교 분석하였다. 대규모에서 메타휴리스틱이,"
            " 소규모에서 정확해법이 선호됨을 확인하였다."
        ),
        "summary_en": (
            "An in-depth survey covers ship routing algorithm development from 1993 to"
            " 2004. Metaheuristics are practical for large instances while exact methods"
            " are preferred for small scales."
        ),
        "relevance": "docs/research/algorithm_selection.md — AW-005 Tier 경계 근거",
    },
    {
        "group": "C",
        "id": "C-5",
        "author": "Meng & Wang",
        "year": 2011,
        "title": (
            "A Scenario-Based Dynamic Programming Model for Multi-Period"
            " Liner Ship Fleet Planning"
        ),
        "journal": "Transportation Research Part B",
        "doi": "10.1016/j.trb.2011.05.002",
        "summary_ko": (
            "다상품 흐름 MILP로 라이너 함대 재배치를 모델링하고 아시아-유럽 노선 12척으로"
            " 검증한다. 시나리오 기반 동적 계획법으로 수요 불확실성 하의 다기간 함대 계획을"
            " 최적화하였다. 화물 흐름과 재배치 동시 고려 시 총비용 9% 감소를 보였다."
        ),
        "summary_en": (
            "Multi-commodity flow MILP models liner fleet repositioning, validated on"
            " 12 Asia-Europe vessels with scenario-based dynamic programming."
            " Joint optimization reduces total cost by 9% versus sequential planning."
        ),
        "relevance": "libs/stochastic/ — 시나리오 DP와 Rolling Horizon 비교 방법론",
    },
    # Group D: Stochastic
    {
        "group": "D",
        "id": "D-1",
        "author": "Agra et al.",
        "year": 2013,
        "title": "The Robust Vehicle Routing Problem with Time Windows",
        "journal": "Transportation Science",
        "doi": "10.1287/trsc.2013.0511",
        "summary_ko": (
            "확률적 항만 서비스시간 하에서 강건 선박 라우팅을 ALNS로 풀이한다."
            " 최악 시나리오 지연을 22% 감소시키는 강건 해를 효율적으로 탐색한다."
            " 시간창 VRP에 강건 최적화를 결합하는 일반적 프레임워크를 확립하였다."
        ),
        "summary_en": (
            "Robust ship routing under stochastic port service times is solved with"
            " ALNS. Robust solutions reduce worst-case delays by 22%, establishing"
            " a general framework for robust time-windowed VRP."
        ),
        "relevance": "libs/routing/alns.py + libs/stochastic/ — 강건 최적화 ALNS",
    },
    {
        "group": "D",
        "id": "D-2",
        "author": "Norstad et al.",
        "year": 2011,
        "title": "Tramp Ship Routing and Scheduling with Speed Optimization",
        "journal": "Transportation Research Part C",
        "doi": "10.1016/j.trc.2010.05.001",
        "summary_ko": (
            "속도 최적화와 확률적 수요를 2단계 확률 계획으로 통합한 트램프 라우팅 방법이다."
            " 속도-연료 관계를 경로 최적화에 내재화하여 6~9%의 연료 절감을 달성하였다."
            " 1단계(사전 계획)와 2단계(실시간 조정) 분리가 효율성과 해 품질을 동시에 개선했다."
        ),
        "summary_en": (
            "Speed optimization and stochastic demand are integrated into a two-stage"
            " stochastic program. Internalizing speed-fuel achieves 6–9% fuel savings,"
            " with two-stage decomposition improving efficiency and solution quality."
        ),
        "relevance": "libs/fuel/consumption.py — AW-006 γ=2.5 속도-연료 통합 근거",
    },
    {
        "group": "D",
        "id": "D-3",
        "author": "Golias et al.",
        "year": 2009,
        "title": "The Berth Allocation Problem: Optimizing Vessel Arrival Time",
        "journal": "Journal of Marine Science and Technology",
        "doi": "10.1007/s00773-009-0049-9",
        "summary_ko": (
            "ETA 불확실성 하에서 2단계 확률 계획으로 BAP를 풀이하고 선박 도착시간을 최적화한다."
            " 결정론적 BAP 대비 평균 대기시간을 17% 감소시키는 확률적 해의 우수성을 검증하였다."
            " ETA를 정규 분포로 근사하여 시나리오 생성 부담을 낮추는 방법을 제안하였다."
        ),
        "summary_en": (
            "Two-stage stochastic programming solves BAP under ETA uncertainty while"
            " optimizing vessel arrival times. Stochastic solutions reduce average"
            " waiting time by 17% versus deterministic BAP."
        ),
        "relevance": "libs/stochastic/ — AW-010 ETA 분포 선택 비교 기준",
    },
    {
        "group": "D",
        "id": "D-4",
        "author": "Zhen",
        "year": 2015,
        "title": "Tactical Berth Allocation under Uncertainty",
        "journal": "European Journal of Operational Research",
        "doi": "10.1016/j.ejor.2015.06.049",
        "summary_ko": (
            "불확실한 도착·처리시간 환경에서 Rolling Horizon 기반 항만 스케줄링을 제안한다."
            " MILP를 반복적으로 풀어 실시간 변화에 적응하는 구조를 30일 시뮬레이션으로 검증했다."
            " RH 윈도우 크기가 계산 시간과 해 품질 사이의 핵심 트레이드오프임을 분석하였다."
        ),
        "summary_en": (
            "A rolling horizon framework iteratively solves MILP under uncertain vessel"
            " arrivals, validated with a 30-day simulation. Window size is identified"
            " as the key trade-off between computation time and solution quality."
        ),
        "relevance": "libs/stochastic/orchestrator.py — RollingHorizonOrchestrator 핵심 참조",
    },
    # Group E: Gang Scheduling
    {
        "group": "E",
        "id": "E-1",
        "author": "Legato et al.",
        "year": 2010,
        "title": "Integrating Simulation and Optimization for Solving a Berth Allocation Problem",
        "journal": "Flexible Services and Manufacturing Journal",
        "doi": "10.1007/s10696-010-9073-y",
        "summary_ko": (
            "선석·크레인·트럭 3개 자원 통합 스케줄링을 시뮬레이션+최적화 하이브리드로 풀이한다."
            " 시뮬레이션이 변동성을 포착하고 최적화 엔진이 자원 배정을 결정하는 이중 루프를 제안했다."
            " 순수 최적화 대비 7% 추가 개선과 계산 시간 50% 단축을 동시에 달성하였다."
        ),
        "summary_en": (
            "A simulation-optimization hybrid solves integrated scheduling of berths,"
            " cranes, and trucks. The dual-loop achieves 7% additional improvement over"
            " pure optimization with 50% less computation on real port data."
        ),
        "relevance": "libs/stochastic/orchestrator.py — 시뮬레이션+최적화 아키텍처 참조",
    },
    {
        "group": "E",
        "id": "E-2",
        "author": "Meisel & Bierwirth",
        "year": 2013,
        "title": (
            "A Framework for Integrated Berth Allocation and Crane Operations"
            " Planning in Seaport Container Terminals"
        ),
        "journal": "Transportation Science",
        "doi": "10.1287/trsc.1120.0430",
        "summary_ko": (
            "선석·안벽 크레인·크레인 스케줄러 3층 자원을 동시 최적화하는 통합 MILP와 VNS를 제안한다."
            " 3층 통합으로 선박 서비스시간을 순차 최적화 대비 11% 단축하였다."
            " VNS가 MILP 대비 계산 시간을 90% 단축하면서 해 품질 차이를 1% 이내로 유지했다."
        ),
        "summary_en": (
            "Integrated MILP with VNS simultaneously optimizes three resource layers."
            " Three-layer joint optimization reduces vessel service time by 11%, with"
            " VNS cutting computation by 90% at under 1% quality loss."
        ),
        "relevance": "libs/scheduling/ — 다층 자원 MILP + VNS/ALNS 선택 근거 (AW-005)",
    },
    {
        "group": "E",
        "id": "E-3",
        "author": "Lübbecke & Desrosiers",
        "year": 2005,
        "title": "Selected Topics in Column Generation",
        "journal": "Operations Research",
        "doi": "10.1287/opre.1050.0201",
        "summary_ko": (
            "해양 작업 다중 자원 동시 배정(Gang Scheduling)을 집합 분할 정식화와"
            " branch-and-price로 정확 풀이하는 방법론을 제시한다."
            " 열 생성의 수렴 가속 기법(stabilization, branching)을 체계적으로 정리하였다."
            " Gang Scheduling의 NP-hard 특성과 branch-and-price의 이론적 우위를 증명하였다."
        ),
        "summary_en": (
            "Column generation and branch-and-price are formulated for gang scheduling"
            " of maritime multi-resource assignment. Convergence acceleration techniques"
            " and theoretical proofs of branch-and-price advantages are presented."
        ),
        "relevance": "libs/scheduling/tug_schedule.py — Gang Scheduling 집합 분할 토대",
    },
    {
        "group": "E",
        "id": "E-4",
        "author": "Xu et al.",
        "year": 2012,
        "title": "Robust Berth Scheduling with Uncertain Vessel Arrival and Handling Times",
        "journal": "Annals of Operations Research",
        "doi": "10.1007/s10479-010-0762-4",
        "summary_ko": (
            "예선·도선사·무어링팀 동시 배정 다중자원 MILP를 라그랑지안 분해로 풀이한다."
            " 자원별 서브문제 병렬 풀이가 가능하여 대규모 인스턴스에 효율적임을 보였다."
            " 자원 동기화 스케줄로 평균 대기시간을 14% 감소시킴을 실데이터로 검증하였다."
        ),
        "summary_en": (
            "Multi-resource MILP for simultaneous tugboat, pilot, and mooring team"
            " assignment is solved via Lagrangian decomposition enabling parallel"
            " subproblems. Validated on real data showing 14% waiting time reduction."
        ),
        "relevance": "libs/scheduling/tug_schedule.py — 예선+도선사 Gang Scheduling 핵심 참조",
    },
    {
        "group": "E",
        "id": "E-5",
        "author": "Fagerholt et al.",
        "year": 2010,
        "title": "Reducing Fuel Emissions by Optimizing Speed on Shipping Routes",
        "journal": "Journal of the Operational Research Society",
        "doi": "10.1057/jors.2009.77",
        "summary_ko": (
            "도선사 배정과 라우팅을 통합한 VRP를 branch-and-price로 정확 풀이하며"
            " 노르웨이 해안에서 이동 거리를 19% 감소시켰다."
            " 속도 최적화를 라우팅에 내재화하여 연료 소비와 거리를 동시에 최소화한다."
            " 동적 재최적화 알고리즘으로 실시간 조건 변화에 대응하는 구조도 제시하였다."
        ),
        "summary_en": (
            "Integrated VRP for pilot scheduling and routing solved with branch-and-price"
            " reduces travel distance by 19% on Norwegian operations. Speed optimization"
            " is internalized to simultaneously minimize fuel and distance."
        ),
        "relevance": "libs/routing/vrptw.py + libs/fuel/ — 도선사 라우팅+속도-연료 통합 선례",
    },
]

# ---------------------------------------------------------------------------
# Group metadata
# ---------------------------------------------------------------------------

GROUPS_KO: dict[str, str] = {
    "A": "Group A: 선석 배분 문제 (Berth Allocation Problem)",
    "B": "Group B: 예선/인도선 스케줄링",
    "C": "Group C: 선박 운항 스케줄링",
    "D": "Group D: 확률적 해양 스케줄링",
    "E": "Group E: 다중자원/Gang 스케줄링",
}

GROUPS_EN: dict[str, str] = {
    "A": "Group A: Berth Allocation Problem (BAP)",
    "B": "Group B: Tugboat / Pilot Scheduling",
    "C": "Group C: Vessel / Ship Scheduling",
    "D": "Group D: Stochastic Maritime Scheduling",
    "E": "Group E: Multi-Resource / Gang Scheduling",
}

GROUPS: dict[str, dict] = {
    "A": {
        "color": colors.HexColor("#1A4E8C"),
        "bg": colors.HexColor("#E8F0FB"),
    },
    "B": {
        "color": colors.HexColor("#166A35"),
        "bg": colors.HexColor("#E8F5EC"),
    },
    "C": {
        "color": colors.HexColor("#7B3800"),
        "bg": colors.HexColor("#FBF0E8"),
    },
    "D": {
        "color": colors.HexColor("#5C007A"),
        "bg": colors.HexColor("#F5E8FB"),
    },
    "E": {
        "color": colors.HexColor("#7A3B00"),
        "bg": colors.HexColor("#FBF3E8"),
    },
}


def group_label(key: str) -> str:
    return t(GROUPS_KO[key], GROUPS_EN[key])


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------


def build_styles() -> dict:
    base = getSampleStyleSheet()

    def ps(name: str, **kwargs: object) -> ParagraphStyle:
        return ParagraphStyle(name, parent=base["Normal"], **kwargs)

    return {
        "title_ko": ps(
            "TitleKo",
            fontName=font_bold,
            fontSize=18,
            leading=26,
            spaceAfter=4,
            alignment=1,
        ),
        "title_en": ps(
            "TitleEn",
            fontName=font_name,
            fontSize=13,
            leading=18,
            spaceAfter=6,
            alignment=1,
            textColor=colors.HexColor("#444444"),
        ),
        "subtitle": ps(
            "Subtitle",
            fontName=font_name,
            fontSize=10,
            leading=14,
            spaceAfter=4,
            alignment=1,
            textColor=colors.HexColor("#666666"),
        ),
        "group_header": ps(
            "GroupHeader",
            fontName=font_bold,
            fontSize=13,
            leading=18,
            spaceBefore=18,
            spaceAfter=6,
        ),
        "paper_id": ps(
            "PaperId",
            fontName=font_bold,
            fontSize=10,
            leading=14,
            spaceBefore=10,
            spaceAfter=2,
        ),
        "citation": ps(
            "Citation",
            fontName=font_name,
            fontSize=8,
            leading=12,
            spaceAfter=4,
            textColor=colors.HexColor("#444444"),
        ),
        "label": ps(
            "Label",
            fontName=font_bold,
            fontSize=8,
            leading=12,
            spaceAfter=1,
            textColor=colors.HexColor("#333333"),
        ),
        "body": ps(
            "Body",
            fontName=font_name,
            fontSize=8,
            leading=12,
            spaceAfter=4,
        ),
        "relevance": ps(
            "Relevance",
            fontName=font_name,
            fontSize=8,
            leading=12,
            spaceAfter=6,
            textColor=colors.HexColor("#0055AA"),
        ),
        "table_header": ps(
            "TableHeader",
            fontName=font_bold,
            fontSize=7,
            leading=10,
            alignment=1,
            textColor=colors.white,
        ),
        "table_cell": ps(
            "TableCell",
            fontName=font_name,
            fontSize=7,
            leading=10,
        ),
        "stat_label": ps(
            "StatLabel",
            fontName=font_bold,
            fontSize=9,
            leading=13,
            spaceBefore=4,
        ),
        "stat_body": ps(
            "StatBody",
            fontName=font_name,
            fontSize=8,
            leading=12,
            spaceAfter=4,
        ),
    }


# ---------------------------------------------------------------------------
# Build flowables
# ---------------------------------------------------------------------------


def title_page(styles: dict) -> list:
    flowables = []
    flowables.append(Spacer(1, 3 * cm))

    if lang == "ko":
        flowables.append(
            Paragraph("선박 운항 스케줄링 최적화 논문 리뷰", styles["title_ko"])
        )
        flowables.append(
            Paragraph(
                "Maritime Vessel Scheduling Optimization — Literature Review",
                styles["title_en"],
            )
        )
    else:
        flowables.append(
            Paragraph(
                "Maritime Vessel Scheduling Optimization — Literature Review",
                styles["title_ko"],
            )
        )
        flowables.append(
            Paragraph("선박 운항 스케줄링 최적화 논문 리뷰", styles["title_en"])
        )

    flowables.append(Spacer(1, 0.5 * cm))
    flowables.append(
        HRFlowable(width="80%", thickness=1, color=colors.HexColor("#AAAAAA"))
    )
    flowables.append(Spacer(1, 0.5 * cm))
    flowables.append(
        Paragraph(
            t(
                "인천항 예선 Gang Scheduling 최적화 프로젝트",
                "Incheon Harbor Tugboat Gang Scheduling Optimization Project",
            ),
            styles["subtitle"],
        )
    )
    flowables.append(Spacer(1, 0.4 * cm))
    flowables.append(
        Paragraph(
            t("NotebookLM 학습 소스용 · 25편 논문 요약", "NotebookLM training source · 25 paper summaries"),
            styles["subtitle"],
        )
    )
    flowables.append(
        Paragraph(
            t("2026-03-22 | 최적화 연구팀", "2026-03-22 | Optimization Research Team"),
            styles["subtitle"],
        )
    )
    flowables.append(Spacer(1, 1.5 * cm))

    if lang == "ko":
        toc_data = [
            ["그룹", "주제", "논문 수"],
            ["A", "선석 배분 문제 (BAP)", "6"],
            ["B", "예선/인도선 스케줄링", "5"],
            ["C", "선박 운항 스케줄링", "5"],
            ["D", "확률적 해양 스케줄링", "4"],
            ["E", "다중자원/Gang 스케줄링", "5"],
            ["합계", "", "25"],
        ]
    else:
        toc_data = [
            ["Group", "Topic", "Papers"],
            ["A", "Berth Allocation Problem (BAP)", "6"],
            ["B", "Tugboat / Pilot Scheduling", "5"],
            ["C", "Vessel / Ship Scheduling", "5"],
            ["D", "Stochastic Maritime Scheduling", "4"],
            ["E", "Multi-Resource / Gang Scheduling", "5"],
            ["Total", "", "25"],
        ]

    col_widths = [2 * cm, 10 * cm, 2.5 * cm]
    toc_table = Table(toc_data, colWidths=col_widths)
    toc_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A4E8C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F5F5F5")]),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E0E0E0")),
                ("FONTNAME", (0, -1), (-1, -1), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flowables.append(toc_table)
    return flowables


def paper_block(paper: dict, styles: dict, group_color: colors.Color) -> list:
    flowables: list = []
    flowables.append(
        Paragraph(
            f"<b>{paper['id']}.</b> {paper['author']} ({paper['year']})",
            styles["paper_id"],
        )
    )
    flowables.append(
        Paragraph(
            f"<i>{paper['title']}</i> — {paper['journal']}",
            styles["citation"],
        )
    )
    flowables.append(
        Paragraph(
            f"DOI: {paper['doi']}",
            styles["citation"],
        )
    )
    summary_text = paper["summary_ko"] if lang == "ko" else paper["summary_en"]
    summary_label = t("요약", "Summary")
    flowables.append(Paragraph(summary_label, styles["label"]))
    flowables.append(Paragraph(summary_text, styles["body"]))
    relevance_label = t("프로젝트 연관성", "Project Relevance")
    flowables.append(Paragraph(relevance_label, styles["label"]))
    flowables.append(Paragraph(paper["relevance"], styles["relevance"]))
    flowables.append(
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD"))
    )
    return flowables


def group_section(group_key: str, papers: list[dict], styles: dict) -> list:
    meta = GROUPS[group_key]
    flowables: list = []

    label = group_label(group_key)
    header_para = Paragraph(
        f"<font color='#{meta['color'].hexval()[2:]}'>■</font>  {label}",
        styles["group_header"],
    )
    flowables.append(header_para)
    flowables.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=meta["color"],
            spaceAfter=6,
        )
    )

    for paper in papers:
        flowables.extend(paper_block(paper, styles, meta["color"]))

    return flowables


def summary_table(papers: list[dict], styles: dict) -> list:
    flowables: list = []
    flowables.append(Spacer(1, 0.5 * cm))
    flowables.append(
        Paragraph(
            t("종합 요약 테이블 / Summary Table", "Summary Table / 종합 요약 테이블"),
            styles["group_header"],
        )
    )
    flowables.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#333333"), spaceAfter=6)
    )

    if lang == "ko":
        header = ["ID", "저자", "연도", "그룹", "핵심 방법 (요약)", "프로젝트 모듈"]
    else:
        header = ["ID", "Author", "Year", "Group", "Key Method (Summary)", "Project Module"]
    rows = [header]

    method_abbrev: dict[str, str] = {
        "A-1": "Lagrangian Relaxation MILP",
        "A-2": "Time Window MILP",
        "A-3": "2D Bin Packing, NP-hard",
        "A-4": "BAP+QC Integrated SA",
        "A-5": "Robust min-max B&B",
        "A-6": "Survey + Benchmarks",
        "B-1": "Cyclic Tug MILP",
        "B-2": "Fleet sizing + Benders",
        "B-3": "ACO Metaheuristic",
        "B-4": "Set covering B&P",
        "B-5": "NSGA-II + AIS",
        "C-1": "Network flow, B&P",
        "C-2": "Column generation MILP",
        "C-3": "Classification survey",
        "C-4": "Algorithm survey",
        "C-5": "Scenario DP + MILP",
        "D-1": "Robust VRP-TW ALNS",
        "D-2": "2-stage SP + speed opt.",
        "D-3": "2-stage SP BAP",
        "D-4": "Rolling Horizon MILP",
        "E-1": "Simulation+Optimization",
        "E-2": "3-layer MILP + VNS",
        "E-3": "Set partitioning B&P",
        "E-4": "Multi-resource Lagrangian",
        "E-5": "Pilot VRP + speed opt.",
    }

    module_abbrev: dict[str, str] = {
        "A-1": "scheduling/berth_allocation",
        "A-2": "utils/interfaces",
        "A-3": "scheduling/ (complexity)",
        "A-4": "scheduling/ (multi-res.)",
        "A-5": "stochastic/ (TwoStage)",
        "A-6": "benchmark_benders.py",
        "B-1": "scheduling/tug_schedule",
        "B-2": "benchmark_benders.py",
        "B-3": "routing/alns",
        "B-4": "scheduling/tug_schedule",
        "B-5": "routing/ + stochastic/",
        "C-1": "scheduling/ (Benders)",
        "C-2": "routing/vrptw",
        "C-3": "docs/algorithm_selection",
        "C-4": "docs/algorithm_selection",
        "C-5": "stochastic/ (RH)",
        "D-1": "routing/alns + stochastic/",
        "D-2": "fuel/consumption",
        "D-3": "stochastic/ (AW-010)",
        "D-4": "stochastic/orchestrator",
        "E-1": "stochastic/orchestrator",
        "E-2": "scheduling/ (Gang)",
        "E-3": "scheduling/tug_schedule",
        "E-4": "scheduling/tug_schedule",
        "E-5": "routing/vrptw + fuel/",
    }

    group_colors: dict[str, colors.Color] = {
        g: GROUPS[g]["bg"] for g in GROUPS
    }

    for p in papers:
        rows.append(
            [
                p["id"],
                p["author"],
                str(p["year"]),
                p["group"],
                method_abbrev.get(p["id"], ""),
                module_abbrev.get(p["id"], ""),
            ]
        )

    col_widths = [1.2 * cm, 3.2 * cm, 1.2 * cm, 1.2 * cm, 5.0 * cm, 5.2 * cm]
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A4E8C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), font_bold),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
    ]

    for i, paper in enumerate(papers, start=1):
        bg = group_colors[paper["group"]]
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_cmds))
    flowables.append(table)
    return flowables


def group_stats(papers: list[dict], styles: dict) -> list:
    flowables: list = []
    flowables.append(Spacer(1, 0.5 * cm))
    flowables.append(
        Paragraph(
            t("그룹별 통계 / Group Statistics", "Group Statistics / 그룹별 통계"),
            styles["group_header"],
        )
    )
    flowables.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#333333"), spaceAfter=6)
    )

    if lang == "ko":
        stat_rows = [["그룹", "논문 수", "평균 연도", "주요 저널"]]
        group_names: dict[str, str] = {
            "A": "A: BAP",
            "B": "B: 예선 스케줄링",
            "C": "C: 선박 운항",
            "D": "D: 확률적 스케줄링",
            "E": "E: Gang 스케줄링",
        }
    else:
        stat_rows = [["Group", "Papers", "Avg. Year", "Key Journals"]]
        group_names = {
            "A": "A: BAP",
            "B": "B: Tug Scheduling",
            "C": "C: Vessel Routing",
            "D": "D: Stochastic",
            "E": "E: Gang Scheduling",
        }

    group_journals: dict[str, str] = {
        "A": "EJOR, JORS, OR Spectrum",
        "B": "OR Spectrum, Expert Systems, IJGIS",
        "C": "Transportation Science, AOR, EJOR",
        "D": "Transportation Science, TRC, EJOR",
        "E": "Operations Research, Transportation Science, FSM",
    }

    for g in ["A", "B", "C", "D", "E"]:
        gpapers = [p for p in papers if p["group"] == g]
        avg_year = sum(p["year"] for p in gpapers) / len(gpapers)
        stat_rows.append(
            [
                group_names[g],
                str(len(gpapers)),
                f"{avg_year:.1f}",
                group_journals[g],
            ]
        )

    col_widths = [3.5 * cm, 1.8 * cm, 2.2 * cm, 10 * cm]
    stat_table = Table(stat_rows, colWidths=col_widths, repeatRows=1)
    stat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 0), (2, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flowables.append(stat_table)
    return flowables


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate literature review PDF in Korean or English."
    )
    parser.add_argument(
        "--lang",
        choices=["ko", "en"],
        default="en",
        help="Output language: ko (Korean) or en (English). Default: en",
    )
    return parser.parse_args()


def main() -> None:
    global lang
    args = parse_args()
    lang = args.lang

    out_path = (
        pathlib.Path(__file__).parent.parent
        / "results"
        / f"literature_review_{lang}.pdf"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc_title = t(
        "선박 운항 스케줄링 최적화 논문 리뷰",
        "Maritime Vessel Scheduling Optimization — Literature Review",
    )
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=doc_title,
        author="Incheon Harbor Optimization Project",
    )

    styles = build_styles()
    flowables: list = []

    flowables.extend(title_page(styles))

    for group_key in ["A", "B", "C", "D", "E"]:
        group_papers = [p for p in PAPERS if p["group"] == group_key]
        flowables.extend(group_section(group_key, group_papers, styles))

    flowables.extend(summary_table(PAPERS, styles))
    flowables.extend(group_stats(PAPERS, styles))

    doc.build(flowables)
    print(f"PDF generated: {out_path}")


if __name__ == "__main__":
    main()
