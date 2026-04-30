import networkx as nx
import pytest
from src.graph_ingest.schema import ODPairRecord
from src.routing_game.wardrop import solve_wardrop
from src.routing_game.optimum import solve_optimum
from src.routing_game.poa import compute_poa
from src.routing_game.taxes import compute_pigovian_taxes

def build_pigou_network():
    """Builds the classic Pigou network (2 nodes, 2 parallel edges)."""
    G = nx.MultiDiGraph()
    G.add_node("A")
    G.add_node("B")
    
    # Edge 0 (Bottom): L(x) = 1.0 (Affine with alpha=0, free_flow_time=1)
    G.add_edge("A", "B", key=0, edge_id="e_bottom", free_flow_time=1.0, alpha=0.0)
    
    # Edge 1 (Top): L(x) = x (Affine with alpha=1.0, free_flow_time=0)
    G.add_edge("A", "B", key=1, edge_id="e_top", free_flow_time=0.0, alpha=1.0)
    
    od_pairs = [ODPairRecord(origin="A", destination="B", demand=1.0, commodity_id="c_1")]
    
    all_paths = {
        "c_1": [
            [("A", "B", 1)], # Top path
            [("A", "B", 0)]  # Bottom path
        ]
    }
    return G, od_pairs, all_paths

def test_pigou_wardrop():
    G, od_pairs, all_paths = build_pigou_network()
    
    path_flows, eq_edge_flows = solve_wardrop(G, od_pairs, all_paths, step_size=0.1)
    
    # Equilibrium: Everyone takes the top edge until cost equals bottom edge (1.0)
    # Since L_top(x) = x, flow will be 1.0 on top, 0.0 on bottom
    assert abs(path_flows["c_1"][0] - 1.0) < 0.05
    assert abs(path_flows["c_1"][1] - 0.0) < 0.05
    
def test_pigou_optimum():
    G, od_pairs, all_paths = build_pigou_network()
    
    path_flows, opt_edge_flows = solve_optimum(G, od_pairs, all_paths, step_size=0.1)
    
    # Optimum: L_top_marginal(x) = 2x, L_bottom_marginal(x) = 1.0
    # 2x = 1.0 => x = 0.5. Top path flow = 0.5, Bottom path flow = 0.5
    assert abs(path_flows["c_1"][0] - 0.5) < 0.05
    assert abs(path_flows["c_1"][1] - 0.5) < 0.05

def test_pigou_poa():
    G, od_pairs, all_paths = build_pigou_network()
    
    _, eq_edge_flows = solve_wardrop(G, od_pairs, all_paths, step_size=0.1)
    _, opt_edge_flows = solve_optimum(G, od_pairs, all_paths, step_size=0.1)
    
    poa, eq_cost, opt_cost = compute_poa(G, eq_edge_flows, opt_edge_flows)
    
    # EQ cost = 1.0 * 1.0 = 1.0
    # OPT cost = 0.5 * 0.5 + 0.5 * 1.0 = 0.75
    # PoA = 1.0 / 0.75 = 4/3 = 1.333...
    assert abs(eq_cost - 1.0) < 0.05
    assert abs(opt_cost - 0.75) < 0.05
    assert abs(poa - 1.333) < 0.05
