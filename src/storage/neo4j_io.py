from neo4j import GraphDatabase
import networkx as nx
from typing import List, Dict, Any
from ..config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import logging

logger = logging.getLogger(__name__)

class Neo4jConnector:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def write_graph(self, G: nx.Graph, batch_size: int = 1000):
        """
        Scaffolding for writing a NetworkX graph to Neo4j.
        This is a basic implementation for the MVP.
        """
        logger.info(f"Writing {G.number_of_nodes()} nodes and {G.number_of_edges()} edges to Neo4j...")
        with self.driver.session() as session:
            # Write Nodes
            nodes_data = [
                {"id": str(n), "properties": {k: str(v) for k, v in data.items()}} 
                for n, data in G.nodes(data=True)
            ]
            session.run("""
                UNWIND $nodes AS node
                MERGE (n:Node {id: node.id})
                SET n += node.properties
            """, nodes=nodes_data)
            
            # Write Edges
            edges_data = [
                {"source": str(u), "target": str(v), "properties": {k: str(val) for k, val in data.items()}}
                for u, v, data in G.edges(data=True)
            ]
            session.run("""
                UNWIND $edges AS edge
                MATCH (s:Node {id: edge.source})
                MATCH (t:Node {id: edge.target})
                MERGE (s)-[r:CONNECTED_TO]->(t)
                SET r += edge.properties
            """, edges=edges_data)
        logger.info("Graph successfully written to Neo4j.")
