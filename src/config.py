import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

# Neo4j Settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# OSM defaults
DEFAULT_CITY = "Brest, France"
DEFAULT_CRS = "epsg:4326"
PROJECTED_CRS = "epsg:3857" # Web Mercator for meter measurements
SIMPLIFY_GRAPH = True
KEEP_LARGEST_COMPONENT = True

# Routing Game Defaults
DEFAULT_LATENCY_ALPHA = 0.15 # BPR function parameter
DEFAULT_LATENCY_BETA = 4.0 # BPR function parameter
DEFAULT_MODE = "road"
