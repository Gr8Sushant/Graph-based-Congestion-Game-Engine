import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.app.components import load_graph_ui
from src.simulation.dynamic_updates import run_dynamic_scenario
from src.viz.network_viz import plot_network_load

st.set_page_config(page_title="Dynamic Scenarios", page_icon="🌊", layout="wide")


load_graph_ui()

st.title("Dynamic Scenario Playback ⏱️")

if st.session_state.get("G") is None:
    st.info("👈 Please load a graph from the sidebar to begin.")
else:
    st.markdown("""
    Watch the network react to a sequence of events over time.
    """)
    
    if st.button("▶️ Run Playback", type="primary"):
        with st.spinner("Simulating timeline (this may take a moment)..."):
            timeline = run_dynamic_scenario(st.session_state["G"], st.session_state["od_pairs"])
            st.session_state["timeline"] = timeline
            
    if "timeline" in st.session_state:
        timeline = st.session_state["timeline"]
        
        # Plot timeline summary
        steps = [t["step"] for t in timeline]
        costs = [t["res"]["eq_cost"] for t in timeline]
        descriptions = [t["description"] for t in timeline]
        
        df = pd.DataFrame({"Step": steps, "Cost": costs, "Event": descriptions})
        fig = px.line(df, x="Step", y="Cost", text="Event", markers=True, title="System Cost over Time", template="plotly_dark")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True, key="timeline_line_chart")
        
        st.divider()
        
        # Step slider
        step_idx = st.slider("Select Time Step", 0, len(timeline) - 1, 0, key="step_slider")
        current_step = timeline[step_idx]
        
        st.subheader(f"t={current_step['step']}: {current_step['description']}")
        
        col1, col2 = st.columns(2)
        col1.metric("System Cost", f"{current_step['res']['eq_cost']:.2f}")
        col2.metric("PoA", f"{current_step['res']['poa']:.4f}")
        
        fig_net = plot_network_load(st.session_state["G"], current_step["res"]["eq_edge_flows"], title="Edge Loads")
        st.plotly_chart(fig_net, use_container_width=True, key="timeline_net_chart")
