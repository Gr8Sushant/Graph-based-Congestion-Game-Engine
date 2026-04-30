import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.storage.graphml_io import load_from_graphml
from src.graph_model.od_pairs import generate_random_od_pairs
from src.simulation.scenarios import ScenarioRunner
from src.viz.network_viz import plot_network_load

st.set_page_config(page_title="City Comparison", page_icon="🏙️", layout="wide")

st.title("City Comparison: Brest vs. Kathmandu 🏙️")
st.markdown("Compare the baseline Price of Anarchy and network vulnerabilities between two distinctly structured cities.")

@st.cache_resource
def load_and_solve(city_name: str, filepath: str):
    G = load_from_graphml(filepath)
    od_pairs = generate_random_od_pairs(G, num_pairs=5, demand_range=(100.0, 500.0), seed=42)
    runner = ScenarioRunner(G, od_pairs, k_paths=3, max_iter=200)
    res = runner.run_equilibrium_vs_optimum()
    return G, res

# Paths to the pre-processed graphs
path_brest = "data/processed/osm_brest_france.graphml"
path_ktm = "data/processed/osm_kathmandu_nepal.graphml"

if st.button("▶️ Run Comparative Simulation", type="primary"):
    if not os.path.exists(path_brest) or not os.path.exists(path_ktm):
        st.error("Missing GraphML files. Ensure both Brest and Kathmandu have been built via `scripts/build_graph.py`.")
    else:
        with st.spinner("Simulating Brest..."):
            G_brest, res_brest = load_and_solve("Brest", path_brest)
            
        with st.spinner("Simulating Kathmandu..."):
            G_ktm, res_ktm = load_and_solve("Kathmandu", path_ktm)
            
        st.success("Simulations complete!")
        
        # Display side-by-side metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🇫🇷 Brest, France")
            st.metric("Nodes", G_brest.number_of_nodes())
            st.metric("Edges", G_brest.number_of_edges())
            st.metric("Price of Anarchy (PoA)", f"{res_brest['poa']:.4f}")
            st.metric("Eq Cost", f"{res_brest['eq_cost']:.2f}")
            
            st.write("**Equilibrium Edge Loads**")
            fig_brest = plot_network_load(G_brest, res_brest["eq_edge_flows"], title="Brest Loads")
            st.plotly_chart(fig_brest, use_container_width=True, key="brest_net")

        with col2:
            st.subheader("🇳🇵 Kathmandu, Nepal")
            st.metric("Nodes", G_ktm.number_of_nodes())
            st.metric("Edges", G_ktm.number_of_edges())
            st.metric("Price of Anarchy (PoA)", f"{res_ktm['poa']:.4f}")
            st.metric("Eq Cost", f"{res_ktm['eq_cost']:.2f}")
            
            st.write("**Equilibrium Edge Loads**")
            fig_ktm = plot_network_load(G_ktm, res_ktm["eq_edge_flows"], title="Kathmandu Loads")
            st.plotly_chart(fig_ktm, use_container_width=True, key="ktm_net")
