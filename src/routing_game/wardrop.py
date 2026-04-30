import networkx as nx
import logging
from typing import Dict, List, Tuple
from ..graph_ingest.schema import ODPairRecord
from .costs import path_cost
from .link_loads import compute_linkloads

logger = logging.getLogger(__name__)

def solve_wardrop(
    G: nx.Graph, 
    od_pairs: List[ODPairRecord], 
    all_paths: Dict[str, List[List[Tuple]]], 
    max_iter: int = 1000, 
    tol: float = 1e-4,
    use_marginal: bool = False,
    include_tax: bool = False,
    step_size: float = 0.05
) -> Tuple[Dict[str, Dict[int, float]], Dict[Tuple, float]]:
    """
    Computes User Equilibrium (Wardrop) using path-based iterative flow shifting.
    Can also compute Social Optimum if use_marginal=True.
    """
    
    # Initialize path flows: put all demand on the shortest free-flow path (index 0)
    path_flows = {}
    for od in od_pairs:
        commodity = od.commodity_id
        path_flows[commodity] = {0: od.demand}
        for i in range(1, len(all_paths.get(commodity, []))):
            path_flows[commodity][i] = 0.0
            
    edge_flows = compute_linkloads(G, path_flows, all_paths)
    
    for iteration in range(max_iter):
        max_gap = 0.0
        
        for od in od_pairs:
            commodity = od.commodity_id
            paths = all_paths.get(commodity, [])
            if len(paths) < 2:
                continue
                
            # Calculate cost of all paths under current edge flows
            costs = [
                path_cost(G, p, edge_flows, use_marginal=use_marginal, include_tax=include_tax) 
                for p in paths
            ]
            
            # Find cheapest path and its cost
            min_cost = min(costs)
            min_idx = costs.index(min_cost)
            
            # Shift flow from more expensive paths to the cheapest path
            # Flow shifts proportionally to the cost difference and current flow
            flow_shifted_total = 0.0
            
            for i, p in enumerate(paths):
                if i == min_idx:
                    continue
                    
                current_flow = path_flows[commodity][i]
                if current_flow > 0:
                    cost_diff = costs[i] - min_cost
                    # Only shift if there is a meaningful cost difference
                    if cost_diff > tol:
                        max_gap = max(max_gap, cost_diff)
                        # The shift amount is a fraction of the current flow on the expensive path
                        shift = current_flow * step_size * (cost_diff / min_cost)
                        # Cap the shift to the available flow
                        shift = min(shift, current_flow)
                        
                        path_flows[commodity][i] -= shift
                        flow_shifted_total += shift
                        
            # Add all shifted flow to the minimum cost path
            path_flows[commodity][min_idx] += flow_shifted_total
            
        # Update edge flows
        edge_flows = compute_linkloads(G, path_flows, all_paths)
        
        # Check convergence
        if max_gap < tol:
            logger.info(f"Equilibrium reached at iteration {iteration} with max gap {max_gap:.6f}")
            break
            
    else:
        logger.warning(f"Solver did not perfectly converge after {max_iter} iterations. Max gap: {max_gap:.6f}")
        
    return path_flows, edge_flows
