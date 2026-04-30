from src.graph_ingest.schema import NodeRecord, EdgeRecord
from src.graph_model.network_builder import build_networkx_graph

def test_build_networkx_graph():
    nodes = [
        NodeRecord(node_id="1", x=0.0, y=0.0),
        NodeRecord(node_id="2", x=1.0, y=1.0)
    ]
    edges = [
        EdgeRecord(edge_id="e1", source="1", target="2", length=100.0, capacity=2000.0)
    ]
    
    G = build_networkx_graph(nodes, edges, directed=True, multi=False)
    
    assert G.number_of_nodes() == 2
    assert G.number_of_edges() == 1
    assert G.is_directed() == True
    
    edge_data = G.edges["1", "2"]
    assert edge_data["length"] == 100.0
    assert edge_data["capacity"] == 2000.0
    assert "free_flow_time" in edge_data # Fallback calculated
    assert edge_data["edge_id"] == "e1"
