import streamlit as st
import sys
from pathlib import Path
import copy

sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.app.components import load_graph_ui
from src.simulation.scenarios import ScenarioRunner
from src.viz.network_viz import plot_network_load

st.set_page_config(page_title="Demand Gating", page_icon="🚦", layout="wide")


load_graph_ui()

st.title("Traffic Rationing: Odd-Even Policy 🚦")

if st.session_state.get("G") is None:
    st.info("👈 Please load a graph from the sidebar to begin.")
else:
    st.markdown("""
    This experiment simulates an **Odd-Even License Plate Policy** (or general Demand Gating). 
    We compare the network under 100% baseline demand against a restricted scenario where only 50% of the demand is allowed into the network at a given time.
    """)
    
    # We use a lower k_paths or max_iter if needed, but defaults are fine
    if st.button("▶️ Run Rationing Simulation", type="primary"):
        with st.spinner("Calculating 100% Baseline Demand..."):
            runner_base = ScenarioRunner(st.session_state["G"], st.session_state["od_pairs"], k_paths=3, max_iter=200)
            res_base = runner_base.run_equilibrium_vs_optimum()
            
        with st.spinner("Calculating 50% Restricted Demand (Odd/Even)..."):
            # Create a new runner with the exact same paths to ensure apples-to-apples
            runner_restricted = ScenarioRunner(st.session_state["G"], st.session_state["od_pairs"], k_paths=3, max_iter=200)
            runner_restricted.all_paths = runner_base.all_paths
            runner_restricted.scale_demand(0.5)
            res_restricted = runner_restricted.run_equilibrium_vs_optimum()
            
        st.success("Simulation complete!")
        
        # Calculate worst edge utilization
        def get_max_load(edge_flows):
            return max(edge_flows.values()) if edge_flows else 0.0
            
        base_max_load = get_max_load(res_base["eq_edge_flows"])
        rest_max_load = get_max_load(res_restricted["eq_edge_flows"])
        
        st.subheader("Scenario Comparison")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Baseline Cost", f"{res_base['eq_cost']:.2f}")
        col2.metric("Restricted Cost", f"{res_restricted['eq_cost']:.2f}", delta=f"{res_restricted['eq_cost'] - res_base['eq_cost']:.2f}", delta_color="inverse")
        
        col3.metric("Baseline PoA", f"{res_base['poa']:.4f}")
        col4.metric("Restricted PoA", f"{res_restricted['poa']:.4f}", delta=f"{res_restricted['poa'] - res_base['poa']:.4f}", delta_color="inverse")
        
        st.write("---")
        
        col_base, col_rest = st.columns(2)
        
        with col_base:
            st.write("### 100% Demand (Baseline)")
            st.metric("Worst-Edge Load", f"{base_max_load:.2f}")
            fig_base = plot_network_load(st.session_state["G"], res_base["eq_edge_flows"], title="Baseline Edge Loads")
            st.plotly_chart(fig_base, use_container_width=True, key="base_net")
            
        with col_rest:
            st.write("### 50% Demand (Odd-Even Restricted)")
            st.metric("Worst-Edge Load", f"{rest_max_load:.2f}", delta=f"{rest_max_load - base_max_load:.2f}", delta_color="inverse")
            fig_rest = plot_network_load(st.session_state["G"], res_restricted["eq_edge_flows"], title="Restricted Edge Loads")
            st.plotly_chart(fig_rest, use_container_width=True, key="rest_net")
