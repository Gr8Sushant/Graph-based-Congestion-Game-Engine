import streamlit as st
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.app.components import load_graph_ui
from src.viz.network_viz import plot_network_load
from src.viz.plots import plot_edge_load_distribution

st.set_page_config(page_title="Overview", page_icon="🗺️", layout="wide")

load_graph_ui()

st.title("Network Overview 🗺️")

if st.session_state.get("G") is None:
    st.info("👈 Please load a graph from the sidebar to begin.")
else:
    G = st.session_state["G"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodes", G.number_of_nodes())
    col2.metric("Edges", G.number_of_edges())
    col3.metric("Generated OD Pairs", len(st.session_state["od_pairs"]))
    
    st.subheader("Base Network Topology")
    # Base network with zero flow
    fig = plot_network_load(G, {}, title="Network Topology (Unloaded)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Origin-Destination Demand Matrix")
    for od in st.session_state["od_pairs"]:
        st.write(f"- **{od.commodity_id}**: Node `{od.origin}` ➡️ Node `{od.destination}` | Demand: `{od.demand:.2f}`")
        