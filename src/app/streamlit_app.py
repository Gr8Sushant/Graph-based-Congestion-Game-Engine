import streamlit as st

st.set_page_config(
    page_title="Graph Congestion Lab",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Graph Congestion Lab 🚦")
st.markdown("""
Welcome to the **Graph-based Congestion Game Engine**!

This interactive dashboard demonstrates how selfish routing degrades network efficiency, how demand affects congestion, and how Pigovian taxes can recover optimal performance.

### Navigation
👈 Use the sidebar to explore the different experiments:
- **01 Overview**: Load graphs and view network topologies.
- **02 Equilibrium vs Optimum**: Compare User Equilibrium with the Social Optimum.
- **03 Tax Experiments**: See how Pigovian taxes force optimal routing.
- **04 Dynamic Scenarios**: Play back time-series shocks (demand spikes, incidents).
- **05 City Comparison**: Compare congestion patterns across different city networks.
- **06 Demand Gating**: Explore how metering and gating access impacts network flow.

---
*Built with Python, OSMnx, NetworkX, Plotly, and Streamlit.*

*by Sushant Pokharel*
""")

# Initialize session state variables if they don't exist
if "G" not in st.session_state:
    st.session_state["G"] = None
if "graph_name" not in st.session_state:
    st.session_state["graph_name"] = "None loaded"
if "od_pairs" not in st.session_state:
    st.session_state["od_pairs"] = []
if "all_paths" not in st.session_state:
    st.session_state["all_paths"] = {}
