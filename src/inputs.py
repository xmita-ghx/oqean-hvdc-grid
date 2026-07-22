"""
oqean-hvdc-grid: User Input & Config Module

Handles loading subsea trench grid parameters from JSON config files
or collecting custom user inputs via CLI.
"""

import json
import os
from typing import Dict, Any, List, Tuple


def load_config_from_json(filepath: str = "config/grid_config.json") -> Dict[str, Any]:
    """
    Loads subsea grid and quantum parameters from a JSON configuration file.
    
    Args:
        filepath: Path to the JSON configuration file.
        
    Returns:
        Dict containing subsea_constraints and quantum_parameters.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Configuration file not found at: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    # Convert crossing_pairs list of lists to list of tuples
    crossing_pairs = [tuple(pair) for pair in config["subsea_constraints"]["crossing_pairs"]]
    config["subsea_constraints"]["crossing_pairs"] = crossing_pairs
    
    return config


def get_interactive_cli_inputs() -> Dict[str, Any]:
    """
    Prompts the user via CLI to enter custom subsea trench constraints.
    
    Returns:
        Dict formatted identically to load_config_from_json output.
    """
    print("\n" + "=" * 60)
    print(" OQEAN-HVDC-GRID: INTERACTIVE SUBSEA CONFIGURATOR")
    print("=" * 60)
    
    # 1. Number of candidate cables
    num_cables_in = input("Enter number of candidate subsea cable routes [default: 4]: ").strip()
    num_cables = int(num_cables_in) if num_cables_in else 4
    
    # 2. Thermal loss per cable
    print(f"\nEnter thermal/transmission loss for each of the {num_cables} candidate cables:")
    thermal_losses: List[float] = []
    for i in range(num_cables):
        default_loss = round(0.3 * (i + 1), 2)
        loss_in = input(f"  - Cable {i} loss (I^2 * R * Sediment Penalty) [default: {default_loss}]: ").strip()
        thermal_losses.append(float(loss_in) if loss_in else default_loss)
        
    # 3. Crossing conflicts
    print("\nDefine cable crossing conflicts (cables intersecting on seabed):")
    crossing_pairs: List[Tuple[int, int]] = []
    add_crossings = input("Are there intersecting cable paths? (y/n) [default: y]: ").strip().lower() != 'n'
    
    if add_crossings:
        pairs_in = input("  - Enter pairs as i-j separated by commas (e.g. 0-1, 2-3) [default: 0-1, 2-3]: ").strip()
        if pairs_in:
            for pair in pairs_in.split(','):
                u, v = map(int, pair.strip().split('-'))
                crossing_pairs.append((u, v))
        else:
            crossing_pairs = [(0, 1), (2, 3)] if num_cables >= 4 else ([(0, 1)] if num_cables >= 2 else [])

    crossing_penalty_in = input("\nEnter weight penalty for cable crossings [default: 5.0]: ").strip()
    crossing_penalty = float(crossing_penalty_in) if crossing_penalty_in else 5.0
    
    # 4. Fault resilience
    resilience_in = input("Enter N-1 fault resilience constraint weight [default: 2.0]: ").strip()
    resilience_weight = float(resilience_in) if resilience_in else 2.0
    
    # 5. Quantum Execution Shots
    shots_in = input("\nEnter Quantum Rings execution shots [default: 1000]: ").strip()
    shots = int(shots_in) if shots_in else 1000

    return {
        "grid_metadata": {
            "project_name": "oqean-hvdc-grid",
            "description": "User-defined CLI configuration",
            "version": "1.0.0"
        },
        "subsea_constraints": {
            "num_cables": num_cables,
            "thermal_losses": thermal_losses,
            "cable_capacities_gw": [1.5] * num_cables,
            "crossing_pairs": crossing_pairs,
            "crossing_penalty_weight": crossing_penalty,
            "fault_resilience_weight": resilience_weight
        },
        "quantum_parameters": {
            "backend_name": "scarlet_quantum_rings",
            "qaoa_gamma": 0.75,
            "qaoa_beta": 0.35,
            "shots": shots
        }
    }


if __name__ == "__main__":
    # Quick test runner
    user_data = get_interactive_cli_inputs()
    print("\nParsed Configuration:")
    print(json.dumps(user_data, indent=2, default=str))