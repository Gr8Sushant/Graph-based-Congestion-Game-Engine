import networkx as nx
from typing import List, Tuple
from itertools import islice

def get_candidate_paths(G: nx.Graph, origin, destination, k: int = 5) -> List[List[Tuple]]:
    """
    Generates up to k simple paths between origin and destination.
    Returns paths as a list of edge tuples to handle MultiDiGraphs properly.
    """
    if origin not in G or destination not in G:
        return []
        
    try:
        # Use Yen's k-shortest paths or bounded simple paths based on weight (length or free_flow_time)
        weight = "free_flow_time" if "free_flow_time" in list(G.edges(data=True))[0][2] else "length"
        
        # nx.shortest_simple_paths is not implemented for MultiDiGraph. 
        # We can cast to DiGraph for path finding, then map back to the multi-edges.
        G_simple = nx.DiGraph(G) if G.is_multigraph() else G
        
        # nx.shortest_simple_paths returns node lists
        node_paths = list(islice(nx.shortest_simple_paths(G_simple, origin, destination, weight=weight), k))
        
        edge_paths = []
        for path in node_paths:
            edges = []
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i+1]
                if G.is_multigraph():
                    # For multigraph, pick the edge with the lowest weight
                    keys = G[u][v].keys()
                    best_key = min(keys, key=lambda k: G[u][v][k].get(weight, 1.0))
                    edges.append((u, v, best_key))
                else:
                    edges.append((u, v))
            edge_paths.append(edges)
            
        return edge_paths
    except nx.NetworkXNoPath:
        return []
