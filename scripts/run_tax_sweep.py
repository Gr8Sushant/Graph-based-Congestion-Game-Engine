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
from src.simulation.sweeps import run_tax_sweep
from src.config import ROOT_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run a tax sweep on a specific edge")
    parser.add_argument("--filepath", type=str, default="data/processed/osm_brest_france.graphml")
    parser.add_argument("--od_pairs", type=int, default=5)
    parser.add_argument("--steps", type=int, default=10)
    args = parser.parse_args()
    
    filepath = ROOT_DIR / args.filepath
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        return
        
    G = load_from_graphml(filepath)
    od_pairs = generate_random_od_pairs(G, num_pairs=args.od_pairs, demand_range=(100.0, 500.0), seed=42)
    
    runner = ScenarioRunner(G, od_pairs, k_paths=3, max_iter=200)
    
    # Pick a random edge from the generated paths to tax
    target_edge = None
    for paths in runner.all_paths.values():
        for p in paths:
            if len(p) > 0:
                target_edge = p[0]
                break
        if target_edge:
            break
            
    if not target_edge:
        logger.error("Could not find a valid edge to tax.")
        return
        
    tax_values = np.linspace(0.0, 100.0, args.steps)
    
    logger.info(f"Starting Tax Sweep on edge {target_edge} ({args.steps} steps)...")
    df_results = run_tax_sweep(runner, target_edge, tax_values)
    
    out_dir = ROOT_DIR / "data" / "processed" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tax_sweep_results.csv"
    
    df_results.to_csv(out_path, index=False)
    logger.info(f"Sweep complete. Results saved to {out_path}")
    print(df_results)

if __name__ == "__main__":
    main()
