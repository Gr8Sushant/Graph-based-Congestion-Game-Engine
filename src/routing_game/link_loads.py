import networkx as nx
from typing import Dict, List, Tuple

def compute_linkloads(G: nx.Graph, path_flows: Dict[str, Dict[int, float]], all_paths: Dict[str, List[List[Tuple]]]) -> Dict[Tuple, float]:
    """
    Aggregate path flows into edge loads.
    
    Args:
        G: The network graph
        path_flows: A dict mapping commodity_id -> {path_index: flow_amount}
        all_paths: A dict mapping commodity_id -> list of edge paths
        
    Returns:
        A dictionary mapping edge tuples to total flow.
    """
    edge_flows = {edge: 0.0 for edge in G.edges(keys=True) if G.is_multigraph()}
    if not G.is_multigraph():
        edge_flows = {edge: 0.0 for edge in G.edges()}

    for commodity_id, flows in path_flows.items():
        if commodity_id not in all_paths:
            continue
            
        commodity_paths = all_paths[commodity_id]
        
        for path_idx, flow in flows.items():
            if flow > 0 and path_idx < len(commodity_paths):
                path = commodity_paths[path_idx]
                for edge in path:
                    # In case an edge is somehow missing from init, initialize to 0
                    if edge not in edge_flows:
                        edge_flows[edge] = 0.0
                    edge_flows[edge] += flow
                    
    return edge_flows
