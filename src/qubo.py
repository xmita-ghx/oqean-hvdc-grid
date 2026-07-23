"""
oqean-hvdc-grid: QUBO Matrix Construction Module

Translates subsea HVDC trench grid parameters, thermal losses,
oceanbed crossing rules, and N-1 fault resilience constraints into a 
Quadratic Unconstrained Binary Optimization (QUBO) cost matrix.
"""

from typing import Dict, Any
import numpy as np


def build_qubo_matrix(config: Dict[str, Any]) -> np.ndarray:
    """
    Constructs an N x N QUBO matrix from input subsea constraints.

    The cost function minimized is:
        E(x) = x^T * Q * x

    Where:
        - Diagonal Q[i, i]: Transmission and trench thermal dissipation loss for cable i.
        - Off-diagonal Q[i, j] (i != j): Heavy penalty if candidate cables i and j cross on the seabed.
        - Coupling Q[i, j]: Penalty terms to enforce N-1 fault resilience redundancy.

    Args:
        config: Dictionary containing 'subsea_constraints' sub-dictionary.

    Returns:
        np.ndarray: N x N QUBO cost matrix Q.
    """
    constraints = config["subsea_constraints"]
    num_cables = constraints["num_cables"]
    thermal_losses = constraints["thermal_losses"]
    crossing_pairs = constraints["crossing_pairs"]
    crossing_penalty = constraints["crossing_penalty_weight"]
    resilience_weight = constraints["fault_resilience_weight"]

    # Initialize empty N x N QUBO matrix
    Q = np.zeros((num_cables, num_cables), dtype=float)

    # 1. Diagonal Terms: Individual cable I^2 * R line loss + depth sediment thermal penalty
    for i in range(num_cables):
        Q[i, i] += thermal_losses[i]

    # 2. Off-Diagonal Terms: Heavy penalty for intersecting cable paths
    for u, v in crossing_pairs:
        if u < num_cables and v < num_cables:
            Q[u, v] += crossing_penalty
            Q[v, u] += crossing_penalty

    # 3. Coupling Terms: N-1 Fault Resilience (Encourage selecting redundant active paths)
    for i in range(num_cables):
        for j in range(i + 1, num_cables):
            coupling_penalty = resilience_weight * 0.1
            Q[i, j] += coupling_penalty
            Q[j, i] += coupling_penalty

    return Q


def evaluate_bitstring_energy(bitstring: str, qubo_matrix: np.ndarray) -> float:
    """
    Calculates the total QUBO cost energy for a specific binary cable selection configuration.

    Args:
        bitstring: Binary string (e.g. '1010' where '1' = cable active, '0' = inactive).
        qubo_matrix: N x N QUBO cost matrix Q.

    Returns:
        float: Scalar energy/cost value x^T * Q * x.
    """
    x = np.array([int(b) for b in bitstring], dtype=float)
    return float(x.T @ qubo_matrix @ x)


if __name__ == "__main__":
    # Quick test runner with mock config
    sample_config = {
        "subsea_constraints": {
            "num_cables": 4,
            "thermal_losses": [0.3, 0.5, 0.8, 0.4],
            "crossing_pairs": [(0, 1), (2, 3)],
            "crossing_penalty_weight": 5.0,
            "fault_resilience_weight": 2.0
        }
    }

    Q_mat = build_qubo_matrix(sample_config)
    print("QUBO Matrix Q:")
    print(Q_mat)

    # Test bitstring energy: 1001 (selecting Cable 0 and Cable 3)
    test_bitstring = "1001"
    energy = evaluate_bitstring_energy(test_bitstring, Q_mat)
    print(f"\nEnergy for bitstring '{test_bitstring}': {energy:.4f}")