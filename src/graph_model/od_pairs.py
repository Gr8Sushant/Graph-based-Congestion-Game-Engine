import random
import networkx as nx
from typing import List
from ..graph_ingest.schema import ODPairRecord

def generate_random_od_pairs(
    G: nx.Graph,
    num_pairs: int,
    demand_range: tuple = (10.0, 100.0),
    seed: int = 42
) -> List[ODPairRecord]:
    """
    Generates random OD pairs from the nodes of the graph.
    """
    random.seed(seed)
    nodes = list(G.nodes())
    od_pairs = []
    
    if len(nodes) < 2:
        return od_pairs
        
    for i in range(num_pairs):
        o, d = random.sample(nodes, 2)
        demand = random.uniform(*demand_range)
        od_pairs.append(
            ODPairRecord(
                origin=str(o),
                destination=str(d),
                demand=demand,
                commodity_id=f"c_{i}"
            )
        )
    return od_pairs
