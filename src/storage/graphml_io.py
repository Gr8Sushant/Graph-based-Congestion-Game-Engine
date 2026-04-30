import networkx as nx
from pathlib import Path

def save_to_graphml(G: nx.Graph, filepath: str | Path) -> None:
    """
    Saves a NetworkX graph to a GraphML file.
    Lists and dicts in attributes are converted to strings since GraphML doesn't support them.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Clean attributes for GraphML compatibility
    G_clean = G.copy()
    for n, data in G_clean.nodes(data=True):
        for k, v in data.items():
            if isinstance(v, (list, dict)):
                data[k] = str(v)
                
    for u, v, data in G_clean.edges(data=True):
        for k, val in data.items():
            if isinstance(val, (list, dict)):
                data[k] = str(val)
                
    nx.write_graphml(G_clean, path)

def load_from_graphml(filepath: str | Path) -> nx.Graph:
    """
    Loads a NetworkX graph from a GraphML file.
    """
    return nx.read_graphml(filepath)
