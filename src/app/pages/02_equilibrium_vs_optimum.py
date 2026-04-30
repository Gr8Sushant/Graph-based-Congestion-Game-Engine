import streamlit as st
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.app.components import load_graph_ui
from src.simulation.scenarios import ScenarioRunner
from src.viz.network_viz import plot_network_load
from src.viz.plots import plot_edge_load_distribution

st.set_page_config(page_title="Equilibrium vs Optimum", page_icon="📈", layout="wide")


load_graph_ui()

st.title("Equilibrium vs Social Optimum ⚖️")

if st.session_state.get("G") is None:
    st.info("👈 Please load a graph from the sidebar to begin.")
else:
    st.markdown("""
    This experiment compares the **Wardrop User Equilibrium** (selfish routing) against the **Social Optimum** (system optimal routing based on marginal costs).
    """)
    
    if st.button("▶️ Run Scenario", type="primary"):
        with st.spinner("Computing flows..."):
            runner = ScenarioRunner(st.session_state["G"], st.session_state["od_pairs"], k_paths=3, max_iter=200)
            res = runner.run_equilibrium_vs_optimum()
            
            st.session_state["res_eq_opt"] = res
            
    if "res_eq_opt" in st.session_state:
        res = st.session_state["res_eq_opt"]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Equilibrium Cost", f"{res['eq_cost']:.2f}")
        col2.metric("Optimum Cost", f"{res['opt_cost']:.2f}")
        col3.metric("Price of Anarchy (PoA)", f"{res['poa']:.4f}", help="EQ Cost / OPT Cost. Values > 1 indicate inefficiency.")
        
        st.divider()
        
        col_eq, col_opt = st.columns(2)
        
        with col_eq:
            st.subheader("Selfish Routing (Equilibrium)")
            fig_eq = plot_network_load(st.session_state["G"], res["eq_edge_flows"], title="Equilibrium Edge Loads")
            st.plotly_chart(fig_eq, use_container_width=True, key="eq_net_chart")
            
            fig_dist_eq = plot_edge_load_distribution(res["eq_edge_flows"], title="EQ Load Distribution")
            st.plotly_chart(fig_dist_eq, use_container_width=True, key="eq_dist_chart")
            
        with col_opt:
            st.subheader("Social Optimum")
            fig_opt = plot_network_load(st.session_state["G"], res["opt_edge_flows"], title="Optimum Edge Loads")
            st.plotly_chart(fig_opt, use_container_width=True, key="opt_net_chart")
            
            fig_dist_opt = plot_edge_load_distribution(res["opt_edge_flows"], title="OPT Load Distribution")
            st.plotly_chart(fig_dist_opt, use_container_width=True, key="opt_dist_chart")
