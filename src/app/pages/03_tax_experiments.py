import streamlit as st
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.app.components import load_graph_ui
from src.simulation.scenarios import ScenarioRunner
from src.viz.network_viz import plot_network_load

st.set_page_config(page_title="Tax Experiments", page_icon="💰", layout="wide")

load_graph_ui()


st.title("Tax Experiments 💰")

if st.session_state.get("G") is None:
    st.info("👈 Please load a graph from the sidebar to begin.")
else:
    st.markdown("""
    Explore how tolling affects user route choices.
    - **Pigovian Taxes**: Computes the mathematically optimal marginal tax per edge, forcing selfish users into the social optimum.
    """)
    
    runner = ScenarioRunner(st.session_state["G"], st.session_state["od_pairs"], k_paths=3, max_iter=200)
    
    # Calculate baseline first to compare
    if "base_eq_opt" not in st.session_state:
        with st.spinner("Calculating baseline..."):
            st.session_state["base_eq_opt"] = runner.run_equilibrium_vs_optimum()
            
    base_res = st.session_state["base_eq_opt"]
    
    st.subheader("Pigovian Tax Intervention")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Original PoA", f"{base_res['poa']:.4f}")
    col2.metric("Original System Cost", f"{base_res['eq_cost']:.2f}")
    col3.metric("Optimum Target Cost", f"{base_res['opt_cost']:.2f}")
    
    if st.button("▶️ Apply Pigovian Taxes", type="primary"):
        with st.spinner("Computing Pigovian taxes and re-running equilibrium..."):
            tax_res = runner.run_pigovian_tax_scenario()
            
            taxed_cost = tax_res["system_cost"]
            new_poa = taxed_cost / base_res["opt_cost"] if base_res["opt_cost"] > 0 else 1.0
            
            st.success("Taxes Applied!")
            
            col1_res, col2_res = st.columns(2)
            col1_res.metric("New Taxed System Cost", f"{taxed_cost:.2f}", delta=f"{taxed_cost - base_res['eq_cost']:.2f}", delta_color="inverse")
            col2_res.metric("New Taxed PoA", f"{new_poa:.4f}", delta=f"{new_poa - base_res['poa']:.4f}", delta_color="inverse")
            
            col_eq, col_tax = st.columns(2)
            with col_eq:
                st.write("**Untaxed Equilibrium Loads**")
                fig_eq = plot_network_load(st.session_state["G"], base_res["eq_edge_flows"], title="")
                st.plotly_chart(fig_eq, use_container_width=True, key="untaxed_eq_chart")
                
            with col_tax:
                st.write("**Taxed Equilibrium Loads**")
                fig_tax = plot_network_load(st.session_state["G"], tax_res["taxed_edge_flows"], title="")
                st.plotly_chart(fig_tax, use_container_width=True, key="taxed_eq_chart")
