"""
연료 소비 모델 모듈.
F(v, d) = alpha * v^gamma * d

gamma=2: QP 선형화 가능 (McCormick)
gamma=3: MINLP 필요 (IPOPT/Bonmin)

의존: libs/utils만
"""
