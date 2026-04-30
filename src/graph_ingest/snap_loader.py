import gzip
import logging
from typing import Tuple, List

from .schema import NodeRecord, EdgeRecord, GraphMetadata
from ..config import DEFAULT_LATENCY_ALPHA, DEFAULT_LATENCY_BETA

logger = logging.getLogger(__name__)

def load_snap_graph(filepath: str, directed: bool = False) -> Tuple[List[NodeRecord], List[EdgeRecord], GraphMetadata]:
    """
    Loads a SNAP edge list (e.g. CAIDA AS graph) and normalizes into our schema.
    """
    logger.info(f"Loading SNAP graph from {filepath}...")
    
    nodes_set = set()
    edges_records = []
    
    opener = gzip.open if str(filepath).endswith('.gz') else open
    
    with opener(filepath, 'rt') as f:
        for line in f:
            if line.startswith('#'):
                continue
                
            parts = line.strip().split()
            if len(parts) < 2:
                continue
                
            u, v = parts[0], parts[1]
            nodes_set.add(u)
            nodes_set.add(v)
            
            # For AS topology, latency and capacity are synthetic
            edges_records.append(
                EdgeRecord(
                    edge_id=f"e_{u}_{v}_{len(edges_records)}",
                    source=u,
                    target=v,
                    length=1.0, # Unit hop
                    free_flow_time=1.0, # Unit hop time
                    capacity=1000.0, # Arbitrary synthetic capacity
                    latency_alpha=DEFAULT_LATENCY_ALPHA,
                    latency_beta=DEFAULT_LATENCY_BETA,
                    tax=0.0,
                    mode="internet"
                )
            )
            
    nodes_records = [NodeRecord(node_id=n, node_type="router") for n in nodes_set]
    
    metadata = GraphMetadata(
        source_type="snap",
        crs="none",
        node_count=len(nodes_records),
        edge_count=len(edges_records),
        directed=directed,
        attributes={"filepath": str(filepath)}
    )
    
    return nodes_records, edges_records, metadata
