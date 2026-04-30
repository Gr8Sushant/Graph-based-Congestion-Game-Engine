import networkx as nx
from typing import Dict, Tuple
from .costs import get_edge_data

def compute_pigovian_taxes(G: nx.Graph, opt_edge_flows: Dict[Tuple, float]) -> Dict[Tuple, float]:
    """
    Computes the optimal Pigovian tax for each edge.
    Tax = x * L'(x) evaluated at the social optimum flow x.
    """
    taxes = {}
    for edge, flow in opt_edge_flows.items():
        if flow <= 0:
            taxes[edge] = 0.0
            continue
            
        u, v = edge[0], edge[1]
        key = edge[2] if len(edge) > 2 else None
        data = get_edge_data(G, u, v, key)
        
        # Affine case
        if "alpha" in data and "beta" not in data:
            alpha = data["alpha"]
            tax = flow * alpha
        else:
            # BPR case
            ff_time = data.get("free_flow_time", 1.0)
            capacity = data.get("capacity", 1000.0)
            alpha = data.get("latency_alpha", 0.15)
            beta = data.get("latency_beta", 4.0)
            
            if capacity <= 0:
                tax = 0.0
            else:
                derivative = ff_time * alpha * beta * (flow ** (beta - 1)) / (capacity ** beta)
                tax = flow * derivative
                
        taxes[edge] = tax
        
    return taxes

def apply_taxes_to_graph(G: nx.Graph, taxes: Dict[Tuple, float]) -> None:
    """Applies the computed taxes directly to the graph edge attributes."""
    for edge, tax in taxes.items():
        u, v = edge[0], edge[1]
        key = edge[2] if len(edge) > 2 else None
        if key is not None and G.is_multigraph():
            G[u][v][key]["tax"] = tax
        else:
            G[u][v]["tax"] = tax
