from typing import List, Iterable
from .schema import NodeRecord, EdgeRecord, ODPairRecord

class ValidationError(Exception):
    pass

def validate_graph_records(
    nodes: Iterable[NodeRecord],
    edges: Iterable[EdgeRecord],
    od_pairs: Iterable[ODPairRecord] = None,
    allow_self_loops: bool = False
) -> None:
    """
    Validates the integrity of graph records before network construction.
    Raises ValidationError if sanity checks fail.
    """
    
    node_ids = {str(n.node_id) for n in nodes}
    edge_ids = set()
    
    for e in edges:
        s = str(e.source)
        t = str(e.target)
        
        # Null source/target check
        if not s or not t:
            raise ValidationError(f"Edge {e.edge_id} has null source or target.")
            
        # Graph integrity
        if s not in node_ids:
            raise ValidationError(f"Edge {e.edge_id} source {s} not in node list.")
        if t not in node_ids:
            raise ValidationError(f"Edge {e.edge_id} target {t} not in node list.")
            
        # Duplicate check
        if e.edge_id in edge_ids:
            raise ValidationError(f"Duplicate edge ID found: {e.edge_id}")
        edge_ids.add(e.edge_id)
        
        # Negative length check
        if e.length is not None and e.length < 0:
            raise ValidationError(f"Edge {e.edge_id} has negative length: {e.length}")
            
        # Self-loops check
        if not allow_self_loops and s == t:
            raise ValidationError(f"Self-loop detected on edge {e.edge_id} for node {s}")
            
    if od_pairs:
        for od in od_pairs:
            o = str(od.origin)
            d = str(od.destination)
            if o not in node_ids:
                raise ValidationError(f"OD Pair {od.commodity_id} origin {o} not in node list.")
            if d not in node_ids:
                raise ValidationError(f"OD Pair {od.commodity_id} destination {d} not in node list.")
