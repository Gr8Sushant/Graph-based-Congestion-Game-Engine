import networkx as nx
from typing import Dict, List, Tuple
from ..graph_ingest.schema import ODPairRecord
from .wardrop import solve_wardrop
import logging

logger = logging.getLogger(__name__)

def solve_optimum(
    G: nx.Graph, 
    od_pairs: List[ODPairRecord], 
    all_paths: Dict[str, List[List[Tuple]]], 
    max_iter: int = 1000, 
    tol: float = 1e-4,
    step_size: float = 0.05
) -> Tuple[Dict[str, Dict[int, float]], Dict[Tuple, float]]:
    """
    Computes the Social Optimum by using Wardrop equilibrium with marginal costs.
    """
    logger.info("Computing Social Optimum (System Optimal Assignment)...")
    return solve_wardrop(
        G, 
        od_pairs, 
        all_paths, 
        max_iter=max_iter, 
        tol=tol, 
        use_marginal=True, # Key difference: use marginal cost instead of average latency
        include_tax=False,
        step_size=step_size
    )
