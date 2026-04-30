from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class NodeRecord(BaseModel):
    node_id: Union[str, int]
    x: Optional[float] = None
    y: Optional[float] = None
    node_type: str = "intersection"

class EdgeRecord(BaseModel):
    edge_id: str
    source: Union[str, int]
    target: Union[str, int]
    length: Optional[float] = None
    free_flow_time: Optional[float] = None
    capacity: Optional[float] = None
    latency_alpha: float = 0.15
    latency_beta: float = 4.0
    tax: float = 0.0
    mode: str = "road"
    
class ODPairRecord(BaseModel):
    origin: Union[str, int]
    destination: Union[str, int]
    demand: float
    commodity_id: str

class GraphMetadata(BaseModel):
    source_type: str
    crs: str
    node_count: int
    edge_count: int
    directed: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)
