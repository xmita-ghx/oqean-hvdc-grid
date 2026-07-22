"""
oqean-hvdc-grid: Quantum-Enhanced Subsea HVDC Power Grid & Oceanbed Trench Routing Optimizer

Modules:
    inputs: Handles CLI user prompts and JSON config parsing.
    qubo: Formulates subsea trench constraints into a QUBO cost matrix.
    quantum_circuit: Constructs and submits QAOA circuits via Quantum Rings SDK.
    evaluator: Decodes quantum measurement counts and ranks optimal cable topologies.
"""

__version__ = "1.0.0"
__author__ = "oqean Developer"