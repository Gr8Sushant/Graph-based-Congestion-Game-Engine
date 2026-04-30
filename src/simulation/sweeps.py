import pandas as pd
import numpy as np
import logging
from typing import List
from .scenarios import ScenarioRunner

logger = logging.getLogger(__name__)

def run_demand_sweep(
    runner_template: ScenarioRunner,
    multipliers: List[float]
) -> pd.DataFrame:
    """
    Runs a demand sweep and returns a DataFrame with EQ cost, OPT cost, and PoA.
    """
    results = []
    
    # Pre-generate paths once using the template
    all_paths = runner_template.all_paths
    
    for m in multipliers:
        logger.info(f"--- Running Demand Sweep: Multiplier {m:.2f} ---")
        
        # Re-initialize to avoid cumulative scaling bugs
        runner = ScenarioRunner(runner_template.G, runner_template.od_pairs, k_paths=runner_template.k_paths, max_iter=runner_template.max_iter)
        runner.all_paths = all_paths # Share paths to save time
        
        runner.scale_demand(m)
        
        res = runner.run_equilibrium_vs_optimum()
        
        results.append({
            "demand_multiplier": m,
            "eq_cost": res["eq_cost"],
            "opt_cost": res["opt_cost"],
            "poa": res["poa"]
        })
        
    return pd.DataFrame(results)

def run_tax_sweep(
    runner: ScenarioRunner,
    edge_to_tax: tuple,
    tax_values: List[float]
) -> pd.DataFrame:
    """
    Sweeps a single edge's tax and evaluates the Price of Anarchy changes.
    """
    results = []
    
    # Get base optimum for PoA calculation
    base_res = runner.run_equilibrium_vs_optimum()
    opt_cost = base_res["opt_cost"]
    
    for t in tax_values:
        logger.info(f"--- Running Tax Sweep: Tax {t:.2f} on edge {edge_to_tax} ---")
        
        taxes = {edge_to_tax: t}
        res = runner.run_tax_scenario(taxes)
        
        taxed_eq_cost = res["system_cost"]
        poa = taxed_eq_cost / opt_cost if opt_cost > 0 else 1.0
        
        results.append({
            "tax_value": t,
            "system_cost": taxed_eq_cost,
            "opt_cost": opt_cost,
            "poa": poa
        })
        
    return pd.DataFrame(results)
