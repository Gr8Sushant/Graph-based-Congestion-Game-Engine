import networkx as nx
import copy
from typing import List, Dict, Tuple, Any
from ..graph_ingest.schema import ODPairRecord
from ..routing_game.paths import get_candidate_paths
from ..routing_game.wardrop import solve_wardrop
from ..routing_game.optimum import solve_optimum
from ..routing_game.poa import compute_poa
from ..routing_game.taxes import compute_pigovian_taxes, apply_taxes_to_graph
import logging

logger = logging.getLogger(__name__)

class ScenarioRunner:
    def __init__(self, G: nx.Graph, od_pairs: List[ODPairRecord], k_paths: int = 3, max_iter: int = 100):
        self.G = G.copy() # Operate on a copy to prevent side effects
        self.od_pairs = [copy.deepcopy(od) for od in od_pairs]
        self.k_paths = k_paths
        self.max_iter = max_iter
        
        self.all_paths = self._generate_paths()
        
    def _generate_paths(self) -> Dict[str, List[List[Tuple]]]:
        all_paths = {}
        for od in self.od_pairs:
            paths = get_candidate_paths(self.G, od.origin, od.destination, k=self.k_paths)
            if paths:
                all_paths[od.commodity_id] = paths
        return all_paths
        
    def scale_demand(self, multiplier: float):
        """Scales the demand for all OD pairs."""
        for od in self.od_pairs:
            od.demand *= multiplier

    def run_equilibrium_vs_optimum(self) -> Dict[str, Any]:
        """Runs both EQ and OPT, and calculates PoA."""
        logger.info("Running Wardrop Equilibrium...")
        eq_path_flows, eq_edge_flows = solve_wardrop(
            self.G, self.od_pairs, self.all_paths, max_iter=self.max_iter
        )
        
        logger.info("Running Social Optimum...")
        opt_path_flows, opt_edge_flows = solve_optimum(
            self.G, self.od_pairs, self.all_paths, max_iter=self.max_iter
        )
        
        poa, eq_cost, opt_cost = compute_poa(self.G, eq_edge_flows, opt_edge_flows)
        
        return {
            "eq_path_flows": eq_path_flows,
            "eq_edge_flows": eq_edge_flows,
            "opt_path_flows": opt_path_flows,
            "opt_edge_flows": opt_edge_flows,
            "eq_cost": eq_cost,
            "opt_cost": opt_cost,
            "poa": poa
        }
        
    def run_tax_scenario(self, taxes: Dict[Tuple, float]) -> Dict[str, Any]:
        """Runs Wardrop with specific edge taxes applied."""
        G_taxed = self.G.copy()
        apply_taxes_to_graph(G_taxed, taxes)
        
        taxed_path_flows, taxed_edge_flows = solve_wardrop(
            G_taxed, self.od_pairs, self.all_paths, max_iter=self.max_iter, include_tax=True
        )
        
        # Calculate cost WITHOUT taxes for welfare comparisons
        # The taxed flows are used, but the true system cost is just latency
        from ..routing_game.costs import total_system_cost
        cost = total_system_cost(self.G, taxed_edge_flows)
        
        return {
            "taxed_path_flows": taxed_path_flows,
            "taxed_edge_flows": taxed_edge_flows,
            "system_cost": cost
        }

    def run_pigovian_tax_scenario(self) -> Dict[str, Any]:
        """Computes Pigovian taxes from optimum and runs the taxed equilibrium."""
        logger.info("Computing Pigovian taxes via Social Optimum...")
        _, opt_edge_flows = solve_optimum(
            self.G, self.od_pairs, self.all_paths, max_iter=self.max_iter
        )
        
        taxes = compute_pigovian_taxes(self.G, opt_edge_flows)
        return self.run_tax_scenario(taxes)
