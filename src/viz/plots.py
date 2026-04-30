import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_poa_vs_demand(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df, 
        x="demand_multiplier", 
        y="poa", 
        title="Price of Anarchy vs. Demand",
        labels={"demand_multiplier": "Demand Multiplier", "poa": "Price of Anarchy"},
        markers=True,
        template="plotly_dark"
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="Optimum (PoA = 1)")
    return fig

def plot_cost_comparison(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["demand_multiplier"], y=df["eq_cost"],
        mode="lines+markers", name="Equilibrium Cost", line=dict(color="red")
    ))
    fig.add_trace(go.Scatter(
        x=df["demand_multiplier"], y=df["opt_cost"],
        mode="lines+markers", name="Optimal Cost", line=dict(color="green")
    ))
    fig.update_layout(
        title="Total System Cost: Equilibrium vs Optimum",
        xaxis_title="Demand Multiplier",
        yaxis_title="Total System Cost",
        template="plotly_dark"
    )
    return fig

def plot_tax_sweep(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["tax_value"], y=df["poa"],
        mode="lines+markers", name="PoA under Tax", line=dict(color="orange")
    ))
    fig.update_layout(
        title="Effect of Manual Link Tax on Price of Anarchy",
        xaxis_title="Tax Value",
        yaxis_title="Price of Anarchy",
        template="plotly_dark"
    )
    return fig

def plot_edge_load_distribution(edge_flows: dict, title: str = "Edge Flow Distribution") -> go.Figure:
    flows = [f for f in edge_flows.values() if f > 0]
    fig = px.histogram(
        x=flows, 
        nbins=50, 
        title=title,
        labels={"x": "Flow Volume", "count": "Number of Edges"},
        template="plotly_dark",
        color_discrete_sequence=["#00CC96"]
    )
    return fig
