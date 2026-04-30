import sys
import os
import argparse
import logging
from pathlib import Path
import numpy as np

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.graphml_io import load_from_graphml
from src.graph_model.od_pairs import generate_random_od_pairs
from src.simulation.scenarios import ScenarioRunner
from src.simulation.sweeps import run_demand_sweep
from src.config import ROOT_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run a demand sweep on a graph")
    parser.add_argument("--filepath", type=str, default="data/processed/osm_brest_france.graphml")
    parser.add_argument("--od_pairs", type=int, default=5)
    parser.add_argument("--steps", type=int, default=10, help="Number of sweep steps")
    args = parser.parse_args()
    
    filepath = ROOT_DIR / args.filepath
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        return
        
    G = load_from_graphml(filepath)
    od_pairs = generate_random_od_pairs(G, num_pairs=args.od_pairs, demand_range=(100.0, 500.0), seed=42)
    
    runner = ScenarioRunner(G, od_pairs, k_paths=3, max_iter=200)
    
    # Sweep from 0.5x to 5.0x demand
    multipliers = np.linspace(0.5, 5.0, args.steps)
    
    logger.info(f"Starting Demand Sweep ({args.steps} steps)...")
    df_results = run_demand_sweep(runner, multipliers)
    
    out_dir = ROOT_DIR / "data" / "processed" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "demand_sweep_results.csv"
    
    df_results.to_csv(out_path, index=False)
    logger.info(f"Sweep complete. Results saved to {out_path}")
    print(df_results)

if __name__ == "__main__":
    main()
