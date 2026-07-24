"""
oqean-hvdc-grid: Quantum Result Evaluator & Reporting Module

Parses raw measurement counts from the Quantum Rings QAOA execution, calculates
energy cost metrics, and exports reports for CLI and GitHub Pages web UI.
"""

import json
import os
from typing import Dict, Any, List


def evaluate_bitstring_cost(bitstring: str, qubo_matrix) -> float:
    """
    Calculates $x^T Q x$ cost for a given candidate binary string.

    Args:
        bitstring: Binary candidate string (e.g., '1010').
        qubo_matrix: N x N QUBO cost matrix.

    Returns:
        float: Calculated energy cost.
    """
    x = [int(b) for b in bitstring]
    x_vec = list(x)
    
    # Calculate x^T * Q * x
    cost = 0.0
    n = len(x_vec)
    for i in range(n):
        for j in range(n):
            cost += x_vec[i] * qubo_matrix[i, j] * x_vec[j]
            
    return cost


def parse_measurement_results(
    counts: Dict[str, int], 
    qubo_matrix, 
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Processes measurement counts from the quantum backend, computes bitstring costs,
    and returns top-ranking route candidates.

    Args:
        counts: Dictionary of bitstring counts from execution.
        qubo_matrix: QUBO cost matrix used in optimization.
        top_k: Number of top candidate routes to return.

    Returns:
        Dict[str, Any]: Parsed evaluation payload including top candidates and total shots.
    """
    total_shots = sum(counts.values())
    candidates = []

    for bitstring, count in counts.items():
        cost = evaluate_bitstring_cost(bitstring, qubo_matrix)
        probability = count / total_shots if total_shots > 0 else 0.0
        
        candidates.append({
            "bitstring": bitstring,
            "count": count,
            "probability": probability,
            "cost": cost,
            "is_valid": True  # Extended constraint validation logic can be checked here
        })

    # Sort candidate routes by lowest energy cost ascending
    candidates.sort(key=lambda item: item["cost"])

    return {
        "total_shots": total_shots,
        "top_candidates": candidates[:top_k],
        "all_candidates": candidates
    }


def export_results_for_web(
    results: Dict[str, Any], 
    config: Dict[str, Any], 
    output_path: str = "docs/data/results.json"
):
    """
    Exports the top quantum candidate routes and metadata to JSON for the GitHub Pages web UI.

    Args:
        results: Evaluated results dictionary containing top candidates.
        config: Configuration dictionary with grid metadata.
        output_path: Path where JSON output should be stored.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    web_payload = {
        "project_name": config.get("grid_metadata", {}).get("project_name", "OQEAN HVDC Grid"),
        "timestamp": config.get("grid_metadata", {}).get("timestamp", "Latest Run"),
        "top_routes": []
    }

    for route in results.get("top_candidates", []):
        web_payload["top_routes"].append({
            "bitstring": route["bitstring"],
            "cost": float(route["cost"]),
            "probability": float(route["probability"]),
            "status": "Feasible" if route.get("is_valid", True) else "Violates Constraint"
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(web_payload, f, indent=2)

    print(f"Web results successfully exported to '{output_path}'!")


def print_optimization_report(results: Dict[str, Any], config: Dict[str, Any]):
    """
    Prints a formatted summary table of candidate routes to the console and
    exports web results.
    """
    project_name = config.get("grid_metadata", {}).get("project_name", "OQEAN HVDC Grid")
    
    print("\n" + "=" * 60)
    print(f" {project_name.upper()} - QAOA ROUTING OPTIMIZATION REPORT")
    print("=" * 60)
    print(f"Total Quantum Shots Evaluated: {results['total_shots']}\n")
    print(f"{'Rank':<6} | {'Bitstring':<12} | {'Cost (Energy)':<15} | {'Probability':<12}")
    print("-" * 60)

    for rank, candidate in enumerate(results["top_candidates"], start=1):
        print(
            f"{rank:<6} | "
            f"{candidate['bitstring']:<12} | "
            f"{candidate['cost']:<15.4f} | "
            f"{candidate['probability'] * 100:<11.2f}%"
        )
    print("=" * 60 + "\n")

    # Automatically trigger web export when printing report
    export_results_for_web(results, config)


if __name__ == "__main__":
    import numpy as np
    from src.inputs import load_config_from_json
    from src.quantum_circuit import get_quantum_rings_provider, build_qaoa_circuit, execute_qaoa_job
    from src.qubo import build_qubo_matrix

    # Load configuration
    config_data = load_config_from_json("config/grid_config.json")
    
    # 1. Build QUBO matrix
    qubo = build_qubo_matrix(config_data)

    # 2. Authenticate and build circuit
    provider_inst = get_quantum_rings_provider()
    circuit, backend = build_qaoa_circuit(qubo, provider=provider_inst)

    # 3. Execute job and evaluate
    counts = execute_qaoa_job(circuit, backend, config_data)
    eval_results = parse_measurement_results(counts, qubo, top_k=5)

    # 4. Print CLI report & export web results
    print_optimization_report(eval_results, config_data)