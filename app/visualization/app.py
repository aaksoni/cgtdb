import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import httpx
from datetime import datetime
import json
import asyncio
from typing import List, Dict, Any

st.set_page_config(page_title="Graph DB Visualizer", layout="wide")

# Initialize session state
if 'graph' not in st.session_state:
    st.session_state.graph = nx.Graph()

async def fetch_all_nodes() -> List[Dict[str, Any]]:
    """Fetch all nodes from the database"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/nodes/all")
        if response.status_code == 200:
            return response.json()
    return []

async def fetch_all_relationships() -> List[Dict[str, Any]]:
    """Fetch all relationships from the database"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/relationships/all")
        if response.status_code == 200:
            return response.json()
    return []

async def fetch_data():
    """Fetch both nodes and relationships"""
    nodes = await fetch_all_nodes()
    relationships = await fetch_all_relationships()
    return nodes, relationships

def create_network_graph(nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> nx.Graph:
    """Create a NetworkX graph from nodes and relationships"""
    G = nx.Graph()
    
    # Add nodes
    for node in nodes:
        G.add_node(
            node['id'],
            label=node['label'],
            properties=node['properties'],
            context=node['context']
        )
    
    # Add edges
    for rel in relationships:
        G.add_edge(
            rel['source_id'],
            rel['target_id'],
            type=rel['type'],
            properties=rel['properties'],
            context=rel['context']
        )
    
    return G

def visualize_graph(G: nx.Graph) -> go.Figure:
    """Create an interactive Plotly visualization of the graph"""
    if not G.nodes:
        return go.Figure()

    pos = nx.spring_layout(G)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    edge_text = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_data = G.edges[edge]
        edge_text.append(
            f"Type: {edge_data.get('type', 'Unknown')}<br>"
            f"Properties: {json.dumps(edge_data.get('properties', {}), indent=2)}<br>"
            f"Context: {json.dumps(edge_data.get('context', {}), indent=2)}"
        )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        hovertext=edge_text,
        mode='lines')

    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_info = G.nodes[node]
        node_text.append(
            f"ID: {node}<br>"
            f"Label: {node_info['label']}<br>"
            f"Properties: {json.dumps(node_info['properties'], indent=2)}<br>"
            f"Context: {json.dumps(node_info['context'], indent=2)}"
        )
        # Color nodes by label
        if node_info['label'] == 'Department':
            node_colors.append('#1f77b4')  # blue
        elif node_info['label'] == 'Project':
            node_colors.append('#2ca02c')  # green
        elif node_info['label'] == 'Employee':
            node_colors.append('#ff7f0e')  # orange
        else:
            node_colors.append('#7f7f7f')  # gray

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            color=node_colors,
            size=20,
            line=dict(width=2)
        ),
        text=[G.nodes[node]['properties'].get('name', '') for node in G.nodes()],
        textposition="bottom center"
    )

    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title="Graph Database Visualization",
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       plot_bgcolor='white')
                   )
    
    return fig

def main():
    st.title("Graph Database Visualizer")
    
    # Sidebar controls
    st.sidebar.title("Controls")
    if st.sidebar.button("Refresh Data"):
        with st.spinner("Fetching data..."):
            # Run async code using asyncio
            nodes, relationships = asyncio.run(fetch_data())
            st.session_state.graph = create_network_graph(nodes, relationships)
    
    # Main visualization
    if st.session_state.graph and len(st.session_state.graph.nodes) > 0:
        st.plotly_chart(visualize_graph(st.session_state.graph), use_container_width=True)
        
        # Graph statistics
        st.subheader("Graph Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Number of Nodes", len(st.session_state.graph.nodes))
        with col2:
            st.metric("Number of Relationships", len(st.session_state.graph.edges))
        with col3:
            st.metric("Average Degree", 
                     round(sum(dict(st.session_state.graph.degree()).values()) / 
                           len(st.session_state.graph.nodes), 2))
        
        # Node List
        st.subheader("Nodes by Type")
        node_types = {}
        for node, data in st.session_state.graph.nodes(data=True):
            label = data['label']
            if label not in node_types:
                node_types[label] = []
            node_types[label].append(data['properties'].get('name', node))
        
        for label, nodes in node_types.items():
            with st.expander(f"{label}s ({len(nodes)})"):
                st.write(", ".join(nodes))
    else:
        st.info("Click 'Refresh Data' to load the graph visualization")

if __name__ == "__main__":
    main() 