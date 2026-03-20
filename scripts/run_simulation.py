"""항구 시뮬레이터 실행 스크립트."""
import sys
sys.path.insert(0, '.')

from libs.simulation.agents import VesselAgent, Position
from libs.simulation.environment import PortSimulator, PortConfig
import numpy as np

def main():
    config = PortConfig(name="부산항")
    sim = PortSimulator(config=config, seed=42)

    # 선박 스케줄 생성
    rng = np.random.default_rng(42)
    vessels = []
    for i in range(10):
        arrival = float(rng.uniform(0, 20))
        duration = float(rng.exponential(4.0))
        v = VesselAgent(
            vessel_id=i,
            name=f"VESSEL-{i:03d}",
            arrival_time=arrival,
            service_duration=duration,
            priority=int(rng.choice([1, 2, 3])),
            draft_m=float(rng.uniform(8, 14)),
            length_m=float(rng.uniform(150, 300)),
            start_pos=Position(35.05 + rng.uniform(0, 0.1), 129.0 + rng.uniform(0, 0.1)),
        )
        vessels.append(v)

    sim.add_vessel_schedule(vessels, apply_weather_delay=True)
    sim.run(until_h=24.0)

    summary = sim.summary()
    print("=== 시뮬레이션 결과 ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
