# Graph Congestion Lab 🚦

> **This project models real-world road and internet networks as graphs, computes Wardrop equilibria and socially optimal flows, measures the Price of Anarchy, and explores Pigovian taxes and dynamic demand scenarios.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#) *(Deploy link placeholder)*
[![CI](https://github.com/USERNAME/graph-congestion-lab/actions/workflows/ci.yml/badge.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Streamlit Demo](assets/demo.gif)

## Overview

Selfish routing degrades network efficiency. When individuals choose their fastest route without considering the collective delay they cause others, the system falls into a suboptimal equilibrium. 

The **Graph Congestion Lab** is a simulation engine designed to mathematically analyze this behavior. By treating OpenStreetMap road networks as game-theoretic environments, it calculates exactly how much time is wasted due to selfish behavior, and how much financial tolling is required to force the network back into optimal efficiency.

### Key Features
- **Real-World Topologies**: Ingests, normalizes, and validates massive graph data from OpenStreetMap (via `osmnx`) and SNAP Autonomous Systems.
- **Wardrop User Equilibrium**: Iterative, path-based solvers to compute non-cooperative routing strategies under BPR (Bureau of Public Roads) congestion latencies.
- **Social Optimum & Price of Anarchy (PoA)**: Solves the system-optimal assignment using marginal cost functions to quantify routing inefficiency.
- **Pigovian Tax Sandbox**: Calculates mathematically optimal tolls ($Tax = x \cdot L'(x)$) to steer selfish drivers into the social optimum.
- **Demand Gating**: Simulates traffic rationing policies (e.g., Odd-Even license plates) to visualize nonlinear bottleneck relief.
- **Interactive Dashboards**: A multi-page Streamlit application with rich, dynamic `Plotly` network maps.

---

## Datasets

- **OpenStreetMap (OSM)**: Processed directly via `osmnx.graph_from_place`.
- **Stanford Network Analysis Project (SNAP)**: Internet topology datasets for abstract routing comparisons.

---

## Quick Start Guide

### 1. Installation

Requires Python 3.10+.

```bash
git clone https://github.com/USERNAME/graph-congestion-lab.git
cd graph-congestion-lab

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Build a Graph
Run the ingestion pipeline to pull data from OSM and generate the baseline `.graphml` files.

```bash
python scripts/build_graph.py --source osm --place "Brest, France"
python scripts/build_graph.py --source osm --place "Kathmandu, Nepal"
```

### 3. Run the Dashboard
Launch the interactive Streamlit UI.

```bash
streamlit run src/app/streamlit_app.py
```

---

## Core Experiments

You can also run experiments directly via the CLI:

```bash
# Sweep demand from 0.5x to 5.0x and track the Price of Anarchy
python scripts/run_demand_sweep.py --filepath data/processed/osm_brest_france.graphml --steps 10

# Sweep taxes on a highly congested edge
python scripts/run_tax_sweep.py --filepath data/processed/osm_brest_france.graphml --steps 10
```

---

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
