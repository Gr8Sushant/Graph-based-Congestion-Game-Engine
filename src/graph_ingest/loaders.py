from typing import Tuple, List, Any
from .schema import NodeRecord, EdgeRecord, GraphMetadata
from .osm_loader import load_osm_graph
from .snap_loader import load_snap_graph

def load_graph(source_type: str, **kwargs) -> Tuple[List[NodeRecord], List[EdgeRecord], GraphMetadata]:
    """
    Dispatcher to load graph data from various sources.
    
    Args:
        source_type: 'osm' or 'snap'
        **kwargs: Source-specific arguments (e.g., place_name for 'osm', filepath for 'snap')
    """
    if source_type == "osm":
        place_name = kwargs.get("place_name")
        if not place_name:
            raise ValueError("place_name is required for OSM loader")
        network_type = kwargs.get("network_type", "drive")
        return load_osm_graph(place_name, network_type)
        
    elif source_type == "snap":
        filepath = kwargs.get("filepath")
        if not filepath:
            raise ValueError("filepath is required for SNAP loader")
        directed = kwargs.get("directed", False)
        return load_snap_graph(filepath, directed)
        
    else:
        raise ValueError(f"Unknown source_type: {source_type}")
