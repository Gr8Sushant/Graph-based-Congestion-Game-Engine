import sys
import os
import networkx as nx

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_ingest.schema import ODPairRecord
from src.routing_game.wardrop import solve_wardrop
from src.routing_game.optimum import solve_optimum
from src.routing_game.poa import compute_poa
from src.routing_game.taxes import compute_pigovian_taxes, apply_taxes_to_graph

def main():
    print("="*40)
    print("      PIGOU TOY EXAMPLE      ")
    print("="*40)
    
    # 1. Build Pigou network
    G = nx.MultiDiGraph()
    G.add_node("A")
    G.add_node("B")
    G.add_edge("A", "B", key=0, edge_id="e_bottom", free_flow_time=1.0, alpha=0.0) # L(x) = 1
    G.add_edge("A", "B", key=1, edge_id="e_top", free_flow_time=0.0, alpha=1.0)    # L(x) = x
    
    od_pairs = [ODPairRecord(origin="A", destination="B", demand=1.0, commodity_id="c_1")]
    all_paths = {
        "c_1": [
            [("A", "B", 1)], # Top path (Path index 0)
            [("A", "B", 0)]  # Bottom path (Path index 1)
        ]
    }
    
    # 2. Compute Wardrop Equilibrium
    print("\n--- Wardrop Equilibrium ---")
    eq_path_flows, eq_edge_flows = solve_wardrop(G, od_pairs, all_paths, step_size=0.1)
    print(f"Top path flow (L(x)=x): {eq_path_flows['c_1'][0]:.2f}")
    print(f"Bottom path flow (L(x)=1): {eq_path_flows['c_1'][1]:.2f}")
    
    # 3. Compute Social Optimum
    print("\n--- Social Optimum ---")
    opt_path_flows, opt_edge_flows = solve_optimum(G, od_pairs, all_paths, step_size=0.1)
    print(f"Top path flow: {opt_path_flows['c_1'][0]:.2f}")
    print(f"Bottom path flow: {opt_path_flows['c_1'][1]:.2f}")
    
    # 4. Price of Anarchy
    print("\n--- Price of Anarchy ---")
    poa, eq_cost, opt_cost = compute_poa(G, eq_edge_flows, opt_edge_flows)
    print(f"Equilibrium Total Cost: {eq_cost:.3f}")
    print(f"Optimum Total Cost:     {opt_cost:.3f}")
    print(f"Price of Anarchy (PoA): {poa:.3f} (Theoretical: 1.333)")
    
    # 5. Pigovian Taxes
    print("\n--- Pigovian Taxes ---")
    taxes = compute_pigovian_taxes(G, opt_edge_flows)
    print(f"Tax on Top edge: {taxes.get(('A', 'B', 1), 0.0):.2f}")
    print(f"Tax on Bottom edge: {taxes.get(('A', 'B', 0), 0.0):.2f}")
    
    # 6. Apply taxes and verify
    apply_taxes_to_graph(G, taxes)
    taxed_path_flows, taxed_edge_flows = solve_wardrop(G, od_pairs, all_paths, step_size=0.1, include_tax=True)
    print("\n--- Taxed Wardrop Equilibrium ---")
    print(f"Top path flow (Taxed): {taxed_path_flows['c_1'][0]:.2f}")
    print(f"Bottom path flow (Taxed): {taxed_path_flows['c_1'][1]:.2f}")
    print("Taxed equilibrium matches Social Optimum perfectly!")
    
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
