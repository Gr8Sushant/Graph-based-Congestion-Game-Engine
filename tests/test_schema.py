import pytest
from src.graph_ingest.schema import NodeRecord, EdgeRecord
from src.graph_ingest.validators import validate_graph_records, ValidationError

def test_schema_defaults():
    n = NodeRecord(node_id="n1")
    assert n.node_type == "intersection"
    assert n.x is None
    
    e = EdgeRecord(edge_id="e1", source="n1", target="n2")
    assert e.mode == "road"
    assert e.tax == 0.0

def test_validators():
    nodes = [NodeRecord(node_id="1"), NodeRecord(node_id="2")]
    
    # Valid edge
    edges = [EdgeRecord(edge_id="e1", source="1", target="2", length=10)]
    validate_graph_records(nodes, edges) # Should not raise
    
    # Invalid target
    edges_invalid = [EdgeRecord(edge_id="e2", source="1", target="3")]
    with pytest.raises(ValidationError, match="target 3 not in node list"):
        validate_graph_records(nodes, edges_invalid)
        
    # Negative length
    edges_neg = [EdgeRecord(edge_id="e3", source="1", target="2", length=-5)]
    with pytest.raises(ValidationError, match="negative length"):
        validate_graph_records(nodes, edges_neg)
