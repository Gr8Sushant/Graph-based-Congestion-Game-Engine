import sys
import os
import argparse
import logging
from pathlib import Path

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_ingest.loaders import load_graph
from src.graph_ingest.validators import validate_graph_records
from src.graph_model.network_builder import build_networkx_graph, get_largest_component
from src.graph_model.od_pairs import generate_random_od_pairs
from src.storage.graphml_io import save_to_graphml
from src.config import PROCESSED_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Build and process a graph")
    parser.add_argument("--source", type=str, required=True, choices=["osm", "snap"], help="Source of graph data")
    parser.add_argument("--place", type=str, help="Place name for OSM (e.g. 'Brest, France')")
    parser.add_argument("--filepath", type=str, help="File path for SNAP data")
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 2 Pipeline for source: {args.source}")
    
    # 1. Load Data
    nodes, edges, metadata = load_graph(
        source_type=args.source,
        place_name=args.place,
        filepath=args.filepath
    )
    
    # 2. Validate Records
    logger.info("Validating graph records...")
    validate_graph_records(nodes, edges, allow_self_loops=True)
    
    # 3. Build NetworkX Graph
    logger.info("Building NetworkX graph...")
    G = build_networkx_graph(nodes, edges, directed=metadata.directed, multi=True)
    
    # 4. Get Largest Component
    logger.info("Extracting largest connected component...")
    G_core = get_largest_component(G, directed=metadata.directed)
    
    # 5. Generate OD Pairs
    logger.info("Generating sample OD pairs...")
    od_pairs = generate_random_od_pairs(G_core, num_pairs=5)
    
    # 6. Save GraphML
    output_filename = f"{args.source}_{metadata.attributes.get('place_name', 'graph').replace(', ', '_').lower()}.graphml"
    if args.source == 'snap':
        output_filename = f"{args.source}_graph.graphml"
        
    output_path = PROCESSED_DIR / output_filename
    logger.info(f"Saving graph to {output_path}...")
    save_to_graphml(G_core, output_path)
    
    # 7. Print Stats
    print("\n" + "="*40)
    print("      PIPELINE COMPLETE      ")
    print("="*40)
    print(f"Source: {metadata.source_type}")
    print(f"Original Nodes: {metadata.node_count}")
    print(f"Original Edges: {metadata.edge_count}")
    print(f"Final Component Nodes: {G_core.number_of_nodes()}")
    print(f"Final Component Edges: {G_core.number_of_edges()}")
    print("\nSample OD Pairs:")
    for od in od_pairs[:3]:
        print(f"  {od.commodity_id}: {od.origin} -> {od.destination} (Demand: {od.demand:.2f})")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
