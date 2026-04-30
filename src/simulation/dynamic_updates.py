import networkx as nx
from typing import List, Dict, Any
from .scenarios import ScenarioRunner
from ..graph_ingest.schema import ODPairRecord

def run_dynamic_scenario(G: nx.Graph, od_pairs: List[ODPairRecord]) -> List[Dict[str, Any]]:
    """
    Simulates a time-stepped shock scenario:
    t=0: Normal traffic
    t=1: Demand spike on the first OD pair
    t=2: Capacity drop (accident) on the most congested edge from t=1
    t=3: Pigovian taxes activated to recover
    """
    timeline = []
    
    # t=0: Normal
    runner0 = ScenarioRunner(G, od_pairs, k_paths=3, max_iter=200)
    res0 = runner0.run_equilibrium_vs_optimum()
    timeline.append({"step": 0, "description": "Normal Traffic", "res": res0})
    
    # t=1: Demand spike
    runner1 = ScenarioRunner(G, od_pairs, k_paths=3, max_iter=200)
    runner1.od_pairs[0].demand *= 3.0 # Spike the first OD
    res1 = runner1.run_equilibrium_vs_optimum()
    timeline.append({"step": 1, "description": "Demand Spike (3x) on Primary Route", "res": res1})
    
    # t=2: Capacity drop
    runner2 = ScenarioRunner(G, runner1.od_pairs, k_paths=3, max_iter=200)
    
    # Find most congested edge from t=1
    edge_flows = res1["eq_edge_flows"]
    if edge_flows:
        max_edge = max(edge_flows, key=edge_flows.get)
        u, v = max_edge[0], max_edge[1]
        key = max_edge[2] if len(max_edge) > 2 else None
        
        # Drop capacity by 80%
        if key is not None and runner2.G.is_multigraph():
            runner2.G[u][v][key]["capacity"] *= 0.2
        else:
            runner2.G[u][v]["capacity"] *= 0.2
            
    res2 = runner2.run_equilibrium_vs_optimum()
    timeline.append({"step": 2, "description": "Capacity Drop (Accident) on Busiest Edge", "res": res2})
    
    # t=3: Taxes
    tax_res = runner2.run_pigovian_tax_scenario()
    
    # Pack to match expected keys
    res3 = {
        "eq_cost": tax_res["system_cost"],
        "opt_cost": res2["opt_cost"], # Optimum stays the same
        "poa": tax_res["system_cost"] / res2["opt_cost"] if res2["opt_cost"] > 0 else 1.0,
        "eq_edge_flows": tax_res["taxed_edge_flows"]
    }
    timeline.append({"step": 3, "description": "Pigovian Tolls Activated", "res": res3})
    
    return timeline
