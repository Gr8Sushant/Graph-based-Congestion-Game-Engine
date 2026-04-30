import sys
import os
import argparse
import logging

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.graphml_io import load_from_graphml
from src.graph_model.od_pairs import generate_random_od_pairs
from src.routing_game.paths import get_candidate_paths
from src.routing_game.wardrop import solve_wardrop
from src.routing_game.optimum import solve_optimum
from src.routing_game.poa import compute_poa

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run routing scenario on a city graph")
    parser.add_argument("--filepath", type=str, required=True, help="Path to processed GraphML file")
    parser.add_argument("--od_pairs", type=int, default=5, help="Number of OD pairs to generate")
    args = parser.parse_args()
    
    logger.info(f"Loading graph from {args.filepath}...")
    G = load_from_graphml(args.filepath)
    logger.info(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    
    logger.info(f"Generating {args.od_pairs} random OD pairs...")
    od_pairs = generate_random_od_pairs(G, num_pairs=args.od_pairs, demand_range=(100.0, 500.0))
    
    logger.info("Generating candidate paths (k=3)...")
    all_paths = {}
    for od in od_pairs:
        # Use top 3 shortest paths to keep simulation fast
        paths = get_candidate_paths(G, od.origin, od.destination, k=3)
        if len(paths) > 0:
            all_paths[od.commodity_id] = paths
        else:
            logger.warning(f"No paths found for {od.commodity_id}: {od.origin} -> {od.destination}")
    
    # Filter out OD pairs with no paths
    od_pairs = [od for od in od_pairs if od.commodity_id in all_paths]
    
    if not od_pairs:
        logger.error("No valid OD pairs with paths. Exiting.")
        return
        
    logger.info("Solving Wardrop Equilibrium...")
    eq_path_flows, eq_edge_flows = solve_wardrop(G, od_pairs, all_paths, max_iter=200, step_size=0.1)
    
    logger.info("Solving Social Optimum...")
    opt_path_flows, opt_edge_flows = solve_optimum(G, od_pairs, all_paths, max_iter=200, step_size=0.1)
    
    logger.info("Computing Price of Anarchy...")
    poa, eq_cost, opt_cost = compute_poa(G, eq_edge_flows, opt_edge_flows)
    
    print("\n" + "="*40)
    print("      SCENARIO RESULTS      ")
    print("="*40)
    print(f"Equilibrium Total Cost: {eq_cost:.2f}")
    print(f"Optimum Total Cost:     {opt_cost:.2f}")
    print(f"Price of Anarchy (PoA): {poa:.4f}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
