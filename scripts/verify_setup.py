import os
import sys

def verify_setup():
    print("Python version:", sys.version.split()[0])
    
    # Check imports
    try:
        import networkx as nx
        import pandas as pd
        import osmnx as ox
        import streamlit as st
        from dotenv import load_dotenv
        import neo4j
        print("✅ Core dependencies imported successfully.")
    except ImportError as e:
        print(f"❌ Dependency error: {e}")
        sys.exit(1)

    # Check datasets
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(cwd, "data", "raw")
    
    osm_file = os.path.join(raw_dir, "bretagne-latest.osm.pbf")
    snap_file = os.path.join(raw_dir, "as-caida20071105.txt.gz")
    
    if os.path.exists(osm_file):
        size_mb = os.path.getsize(osm_file) / (1024 * 1024)
        print(f"✅ OSM Dataset found: {osm_file} ({size_mb:.2f} MB)")
    else:
        print(f"❌ OSM Dataset NOT found: {osm_file}")
        
    if os.path.exists(snap_file):
        size_mb = os.path.getsize(snap_file) / (1024 * 1024)
        print(f"✅ SNAP Dataset found: {snap_file} ({size_mb:.2f} MB)")
    else:
        print(f"❌ SNAP Dataset NOT found: {snap_file}")

if __name__ == "__main__":
    verify_setup()
