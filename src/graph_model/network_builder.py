import networkx as nx
from typing import List, Iterable
from ..graph_ingest.schema import NodeRecord, EdgeRecord

def build_networkx_graph(
    nodes: Iterable[NodeRecord],
    edges: Iterable[EdgeRecord],
    directed: bool = True,
    multi: bool = True
) -> nx.Graph:
    """
    Builds a NetworkX graph from validated Node and Edge records.
    """
    if directed and multi:
        G = nx.MultiDiGraph()
    elif directed:
        G = nx.DiGraph()
    elif multi:
        G = nx.MultiGraph()
    else:
        G = nx.Graph()

    # Add nodes
    for node in nodes:
        node_attr = node.model_dump(exclude={"node_id"})
        # Filter out None values to save memory/storage
        node_attr = {k: v for k, v in node_attr.items() if v is not None}
        G.add_node(node.node_id, **node_attr)

    # Add edges
    for edge in edges:
        edge_attr = edge.model_dump(exclude={"source", "target", "edge_id"})
        # Filter out None values
        edge_attr = {k: v for k, v in edge_attr.items() if v is not None}
        
        # Derive free_flow_time if missing but we have length and speed limit (capacity/speed proxy)
        # Note: OSMNx loader usually handles this, but as a fallback:
        if "free_flow_time" not in edge_attr or edge_attr["free_flow_time"] is None:
            if "length" in edge_attr and edge_attr["length"] is not None:
                # Fallback: assume 50 km/h (approx 13.89 m/s) if no speed limit or free flow time
                edge_attr["free_flow_time"] = edge_attr["length"] / 13.89

        if multi:
            G.add_edge(edge.source, edge.target, key=edge.edge_id, **edge_attr)
        else:
            G.add_edge(edge.source, edge.target, edge_id=edge.edge_id, **edge_attr)

    return G

def get_largest_component(G: nx.Graph, directed: bool = True) -> nx.Graph:
    """
    Returns the largest connected component of the graph.
    Uses strongly connected components for directed graphs if we want strict routing,
    but weakly connected components are standard for road networks.
    """
    if directed:
        # For road routing, weakly connected is often preferred to keep graph intact, 
        # but strongly connected ensures any A->B path works.
        # We'll use strongly connected for rigorous routing game compatibility.
        largest_cc = max(nx.strongly_connected_components(G), key=len)
    else:
        largest_cc = max(nx.connected_components(G), key=len)
        
    return G.subgraph(largest_cc).copy()
