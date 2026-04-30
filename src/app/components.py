import streamlit as st
from pathlib import Path
import sys
import os

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.storage.graphml_io import load_from_graphml
from src.graph_model.od_pairs import generate_random_od_pairs
from src.routing_game.paths import get_candidate_paths

def load_graph_ui(sidebar=True):
    """UI component for loading graphs."""
    target = st.sidebar if sidebar else st
    
    target.header("Graph Configuration")
    
    # Auto-detect available processed graphs
    processed_dir = Path("data/processed")
    available_files = list(processed_dir.glob("*.graphml"))
    
    if not available_files:
        target.warning("No processed graphs found. Run `scripts/build_graph.py` first.")
        return
        
    if st.session_state.get("graph_name"):
        target.success(f"🟢 Active: {st.session_state['graph_name']} \n\n({len(st.session_state['od_pairs'])} OD pairs loaded)")

    options = {f.name: f for f in available_files}
    
    # Keep the selectbox and slider synced with the currently loaded state
    current_idx = 0
    if "graph_name" in st.session_state and st.session_state["graph_name"] in options:
        current_idx = list(options.keys()).index(st.session_state["graph_name"])
        
    selected_name = target.selectbox("Select Graph", list(options.keys()), index=current_idx, key=f"select_{sidebar}")
    
    current_od = st.session_state.get("num_od_target", 5)
    num_od = target.slider("Number of OD Pairs", 1, 50, current_od, key=f"slider_{sidebar}")
    
    if target.button("Load Graph & Generate OD Pairs", key=f"btn_{sidebar}"):
        with st.spinner("Loading graph and generating paths..."):
            G = load_from_graphml(options[selected_name])
            od_pairs = generate_random_od_pairs(G, num_pairs=num_od, demand_range=(100.0, 500.0), seed=42)
            
            all_paths = {}
            for od in od_pairs:
                paths = get_candidate_paths(G, od.origin, od.destination, k=3)
                if paths:
                    all_paths[od.commodity_id] = paths
                    
            od_pairs = [od for od in od_pairs if od.commodity_id in all_paths]
            
            st.session_state["G"] = G
            st.session_state["graph_name"] = selected_name
            st.session_state["num_od_target"] = num_od
            st.session_state["od_pairs"] = od_pairs
            st.session_state["all_paths"] = all_paths
            
            # Clear old scenario results from other tabs so they don't show stale data
            for key in ["res_eq_opt", "base_eq_opt", "timeline"]:
                if key in st.session_state:
                    del st.session_state[key]
            
            target.success(f"Loaded {G.number_of_nodes()} nodes, {G.number_of_edges()} edges!")
