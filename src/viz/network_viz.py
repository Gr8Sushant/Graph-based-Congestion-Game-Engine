import plotly.graph_objects as go
import networkx as nx
from typing import Dict, Tuple

def plot_network_load(G: nx.Graph, edge_flows: Dict[Tuple, float], title: str = "Network Flow Load") -> go.Figure:
    """
    Plots the network nodes and edges, coloring edges by flow volume.
    Requires nodes to have 'x' and 'y' attributes.
    """
    # Extract node positions
    pos = {node: (data.get('x', 0), data.get('y', 0)) for node, data in G.nodes(data=True)}
    
    edge_x = []
    edge_y = []
    edge_colors = []
    edge_widths = []
    edge_hover_text = []
    
    max_flow = max(edge_flows.values()) if edge_flows else 1.0
    if max_flow == 0: max_flow = 1.0
    
    # We create a separate trace for each edge to allow per-edge coloring in Plotly scatter
    # For large graphs, plotting everything as one trace with varying colors is better, but requires numeric colorscales
    
    fig = go.Figure()
    
    # Instead of adding an individual trace for each edge (slow), 
    # we group edges by flow-intensity bins for rendering efficiency.
    bins = 10
    traces = {i: {"x": [], "y": [], "flows": []} for i in range(bins + 1)}
    
    for edge in G.edges(keys=True) if G.is_multigraph() else G.edges():
        flow = edge_flows.get(edge, 0.0)
        
        # Determine bin
        intensity = min(int((flow / max_flow) * bins), bins)
        
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        traces[intensity]["x"].extend([x0, x1, None])
        traces[intensity]["y"].extend([y0, y1, None])
        traces[intensity]["flows"].append(flow)

    colorscale = px.colors.sequential.YlOrRd
        
    for intensity, data in traces.items():
        if not data["x"]:
            continue
            
        color_idx = int((intensity / bins) * (len(colorscale) - 1))
        color = colorscale[color_idx]
        
        # Hover info is tricky with multi-line segments, usually we just color them
        fig.add_trace(go.Scatter(
            x=data["x"], y=data["y"],
            line=dict(width=1.0 + (intensity/bins)*3.0, color=color),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
        
    # Add nodes (just small dots)
    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlOrRd',
            color=[0],
            size=3,
            colorbar=dict(
                thickness=15,
                title='Flow Intensity',
                xanchor='left'
            ),
        ),
        showlegend=False
    ))

    fig.update_layout(
        title=title,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        template="plotly_dark"
    )
    
    return fig

import plotly.express as px
