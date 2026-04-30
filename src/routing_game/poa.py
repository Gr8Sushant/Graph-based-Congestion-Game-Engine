import networkx as nx
from typing import Dict, Tuple
from .costs import total_system_cost

def compute_poa(G: nx.Graph, eq_edge_flows: Dict[Tuple, float], opt_edge_flows: Dict[Tuple, float]) -> Tuple[float, float, float]:
    """
    Computes the Price of Anarchy given User Equilibrium flows and Social Optimum flows.
    Returns:
        (PoA, Total Equilibrium Cost, Total Optimum Cost)
    """
    eq_cost = total_system_cost(G, eq_edge_flows)
    opt_cost = total_system_cost(G, opt_edge_flows)
    
    if opt_cost <= 0:
        poa = 1.0 # Avoid division by zero, though unlikely in a real network
    else:
        poa = eq_cost / opt_cost
        
    return poa, eq_cost, opt_cost
