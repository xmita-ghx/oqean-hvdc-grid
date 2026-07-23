"""
oqean-hvdc-grid: Results Evaluator Module

Decodes quantum measurement bitstrings, evaluates QUBO energy costs,
ranks cable routing candidates, and formats printable reports.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from src.qubo import evaluate_bitstring_energy


def parse_measurement_results(
    counts: Dict[str, int],
    qubo_matrix: np.ndarray,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Evaluates quantum measurement bitstrings against the QUBO matrix and ranks them.

    Args:
        counts: Measurement frequency dictionary from Quantum Rings execution.
        qubo_matrix: N x N QUBO matrix used to calculate energy costs.
        top_k: Number of top candidate topologies to return.

    Returns:
        List[Dict[str, Any]]: Sorted list of dictionary results containing bitstring,
                              energy cost, shot count, and selected cable IDs.
    """
    total_shots = sum(counts.values())
    evaluated_list: List[Tuple[str, float, int]] = []

    for bitstring, count in counts.items():
        energy = evaluate_bitstring_energy(bitstring, qubo_matrix)
        evaluated_list.append((bitstring, energy, count))

    # Sort primarily by lowest energy cost, secondarily by highest measurement frequency
    evaluated_list.sort(key=lambda x: (x[1], -x[2]))

    results: List[Dict[str, Any]] = []
    for bitstring, energy, count in evaluated_list[:top_k]:
        selected_cables = [f"Cable {i}" for i, b in enumerate(bitstring) if b == '1']
        probability = (count / total_shots) * 100

        results.append({
            "bitstring": bitstring,
            "energy_cost": round(energy, 4),
            "shot_count": count,
            "probability_pct": round(probability, 2),
            "selected_cables": selected_cables
        })

    return results


def print_optimization_report(results: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """
    Prints a clean, formatted report of the top subsea cable routing topologies.

    Args:
        results: Evaluated results list from parse_measurement_results.
        config: Full project configuration dictionary.
    """
    num_cables = config["subsea_constraints"]["num_cables"]
    shots = config["quantum_parameters"]["shots"]

    print("\n" + "=" * 78)
    print(" OQEAN-HVDC-GRID: SUBSEA TRENCH OPTIMIZATION REPORT")
    print("=" * 78)
    print(f" Candidate Cables Evaluated : {num_cables} (Qubits)")
    print(f" Quantum Rings Shots        : {shots}")
    print("-" * 78)
    print(f"{'Rank':<5} | {'Bitstring':<12} | {'QUBO Energy':<12} | {'Shots (%)':<12} | {'Active Cable Route'}")
    print("-" * 78)

    for idx, item in enumerate(results, 1):
        cables_str = ", ".join(item["selected_cables"]) if item["selected_cables"] else "No Cables Active"
        print(
            f"{idx:<5} | "
            f"{item['bitstring']:<12} | "
            f"{item['energy_cost']:<12.4f} | "
            f"{item['shot_count']} ({item['probability_pct']}%) | "
            f"{cables_str}"
        )

    print("-" * 78)
    best = results[0]
    print(f" OPTIMAL SUBSEA TOPOLOGY : Bitstring '{best['bitstring']}'")
    print(f" Minimum Cost Energy     : {best['energy_cost']}")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    # Test runner with mock counts and QUBO matrix
    mock_qubo = np.array([
        [0.3, 5.0, 0.2, 0.2],
        [5.0, 0.5, 0.2, 0.2],
        [0.2, 0.2, 0.8, 5.0],
        [0.2, 0.2, 5.0, 0.4]
    ])

    mock_counts = {
        "1001": 420,
        "0110": 310,
        "1100": 150,
        "0011": 120
    }

    mock_config = {
        "subsea_constraints": {"num_cables": 4},
        "quantum_parameters": {"shots": 1000}
    }

    parsed = parse_measurement_results(mock_counts, mock_qubo)
    print_optimization_report(parsed, mock_config)