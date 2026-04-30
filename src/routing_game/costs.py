import networkx as nx
from typing import List, Dict, Tuple

def get_edge_data(G: nx.Graph, u, v, key=None):
    if key is not None and G.is_multigraph():
        return G.edges[u, v, key]
    else:
        return G.edges[u, v]

def bpr_latency(free_flow_time: float, capacity: float, flow: float, alpha: float = 0.15, beta: float = 4.0) -> float:
    """Bureau of Public Roads (BPR) latency function."""
    if capacity <= 0:
        return free_flow_time
    return free_flow_time * (1.0 + alpha * (flow / capacity) ** beta)

def bpr_marginal_cost(free_flow_time: float, capacity: float, flow: float, alpha: float = 0.15, beta: float = 4.0) -> float:
    """Marginal cost: L(x) + x * L'(x)"""
    if capacity <= 0:
        return free_flow_time
    latency = bpr_latency(free_flow_time, capacity, flow, alpha, beta)
    derivative = free_flow_time * alpha * beta * (flow ** (beta - 1)) / (capacity ** beta)
    return latency + flow * derivative

def affine_latency(free_flow_time: float, alpha: float, flow: float) -> float:
    """Simple affine latency: alpha * x + free_flow_time"""
    return alpha * flow + free_flow_time

def affine_marginal_cost(free_flow_time: float, alpha: float, flow: float) -> float:
    """Marginal cost for affine: L(x) + x * L'(x) = 2 * alpha * x + free_flow_time"""
    return 2 * alpha * flow + free_flow_time

def edge_latency(G: nx.Graph, u, v, key=None, flow: float = 0.0) -> float:
    """Calculate the latency of an edge given a flow."""
    data = get_edge_data(G, u, v, key)
    
    # Simple affine check for toy networks (e.g. Pigou)
    if "alpha" in data and "beta" not in data:
        return affine_latency(data.get("free_flow_time", 0.0), data["alpha"], flow)
        
    # Standard BPR check
    ff_time = data.get("free_flow_time", 1.0)
    capacity = data.get("capacity", 1000.0)
    alpha = data.get("latency_alpha", 0.15)
    beta = data.get("latency_beta", 4.0)
    
    return bpr_latency(ff_time, capacity, flow, alpha, beta)

def edge_marginal_cost(G: nx.Graph, u, v, key=None, flow: float = 0.0) -> float:
    """Calculate the marginal cost of an edge given a flow."""
    data = get_edge_data(G, u, v, key)
    
    if "alpha" in data and "beta" not in data:
        return affine_marginal_cost(data.get("free_flow_time", 0.0), data["alpha"], flow)
        
    ff_time = data.get("free_flow_time", 1.0)
    capacity = data.get("capacity", 1000.0)
    alpha = data.get("latency_alpha", 0.15)
    beta = data.get("latency_beta", 4.0)
    
    return bpr_marginal_cost(ff_time, capacity, flow, alpha, beta)

def path_cost(G: nx.Graph, path_edges: List[Tuple], edge_flows: Dict[Tuple, float], use_marginal: bool = False, include_tax: bool = False) -> float:
    """Calculate the total cost of a path given the network flows."""
    total_cost = 0.0
    for edge in path_edges:
        flow = edge_flows.get(edge, 0.0)
        
        # Handle multigraph tuple expansion gracefully
        u, v = edge[0], edge[1]
        key = edge[2] if len(edge) > 2 else None
        
        if use_marginal:
            cost = edge_marginal_cost(G, u, v, key, flow)
        else:
            cost = edge_latency(G, u, v, key, flow)
            
        if include_tax:
            data = get_edge_data(G, u, v, key)
            cost += data.get("tax", 0.0)
            
        total_cost += cost
    return total_cost

def total_system_cost(G: nx.Graph, edge_flows: Dict[Tuple, float]) -> float:
    """Calculate the total latency experienced by all users."""
    system_cost = 0.0
    for edge, flow in edge_flows.items():
        if flow > 0:
            u, v = edge[0], edge[1]
            key = edge[2] if len(edge) > 2 else None
            latency = edge_latency(G, u, v, key, flow)
            system_cost += latency * flow
    return system_cost
