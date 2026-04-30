import osmnx as ox
import networkx as nx
from typing import Tuple, List, Dict, Any
import logging

from .schema import NodeRecord, EdgeRecord, GraphMetadata
from ..config import DEFAULT_LATENCY_ALPHA, DEFAULT_LATENCY_BETA, SIMPLIFY_GRAPH

logger = logging.getLogger(__name__)

def load_osm_graph(place_name: str, network_type: str = "drive") -> Tuple[List[NodeRecord], List[EdgeRecord], GraphMetadata]:
    """
    Downloads OSM data for a place, processes it, and normalizes into our schema.
    """
    logger.info(f"Downloading OSM graph for {place_name} with type {network_type}...")
    
    # Download graph
    G = ox.graph_from_place(place_name, network_type=network_type, simplify=SIMPLIFY_GRAPH)
    
    # Add edge speeds and travel times
    logger.info("Adding edge speeds and travel times...")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    
    nodes_records = []
    edges_records = []
    
    logger.info("Normalizing nodes to schema...")
    for node_id, data in G.nodes(data=True):
        nodes_records.append(
            NodeRecord(
                node_id=str(node_id),
                x=data.get("x"),
                y=data.get("y"),
                node_type="highway_node" if "highway" in data else "intersection"
            )
        )
        
    logger.info("Normalizing edges to schema...")
    for u, v, key, data in G.edges(keys=True, data=True):
        # Handle capacity proxy (num lanes)
        lanes = data.get("lanes", 1)
        if isinstance(lanes, list):
            lanes = lanes[0]
        try:
            lanes = float(lanes)
        except (ValueError, TypeError):
            lanes = 1.0
            
        # Basic capacity proxy: 1800 vehicles per hour per lane
        capacity = lanes * 1800.0
        
        edges_records.append(
            EdgeRecord(
                edge_id=f"{u}_{v}_{key}",
                source=str(u),
                target=str(v),
                length=data.get("length"),
                free_flow_time=data.get("travel_time"),
                capacity=capacity,
                latency_alpha=DEFAULT_LATENCY_ALPHA,
                latency_beta=DEFAULT_LATENCY_BETA,
                tax=0.0,
                mode="road"
            )
        )
        
    metadata = GraphMetadata(
        source_type="osm",
        crs=str(G.graph.get("crs", "epsg:4326")),
        node_count=len(nodes_records),
        edge_count=len(edges_records),
        directed=nx.is_directed(G),
        attributes={"place_name": place_name, "network_type": network_type}
    )
    
    return nodes_records, edges_records, metadata
