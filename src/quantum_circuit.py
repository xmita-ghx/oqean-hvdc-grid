"""
oqean-hvdc-grid: Quantum Circuit & Execution Module

Constructs QAOA ansatz circuits for subsea cable routing and dispatches execution
jobs to the Quantum Rings SDK simulator.
"""

import os
from typing import Dict, Any, Tuple
import numpy as np
from dotenv import load_dotenv

from QuantumRingsLib import QuantumCircuit, QuantumRingsProvider


def get_quantum_rings_provider() -> QuantumRingsProvider:
    """
    Loads API credentials from environment variables and initializes the Quantum Rings Provider.

    Returns:
        QuantumRingsProvider: Authenticated provider instance.
    """
    load_dotenv()
    
    token = os.getenv("QUANTUMRINGS_TOKEN")
    account_name = os.getenv("QUANTUMRINGS_NAME")

    if not token or not account_name:
        raise ValueError(
            "Missing Quantum Rings credentials! "
            "Ensure your .env file exists and contains QUANTUMRINGS_TOKEN and QUANTUMRINGS_NAME."
        )

    # Clean up outer quotes or whitespace if present
    token = token.strip("\"' ")
    account_name = account_name.strip("\"' ")

    return QuantumRingsProvider(token=token, name=account_name)


def build_qaoa_circuit(
    qubo_matrix: np.ndarray, 
    provider: QuantumRingsProvider, 
    gamma: float = 0.75, 
    beta: float = 0.35,
    backend_name: str = "scarlet_quantum_rings"
) -> Tuple[QuantumCircuit, Any]:
    """
    Constructs a 1-step QAOA circuit based on the given QUBO cost matrix.

    Args:
        qubo_matrix: N x N QUBO cost matrix.
        provider: Authenticated QuantumRingsProvider instance.
        gamma: Problem Hamiltonian phase rotation angle.
        beta: Mixer Hamiltonian phase rotation angle.
        backend_name: Name of the target Quantum Rings backend simulator.

    Returns:
        Tuple[QuantumCircuit, Any]: (Constructed QuantumCircuit, Target Backend)
    """
    backend = provider.get_backend(backend_name)
    num_qubits = qubo_matrix.shape[0]

    # Initialize circuit with integer qubit and classical bit counts
    qc = QuantumCircuit(num_qubits, num_qubits)

    # 1. Prepare Initial Superposition
    for i in range(num_qubits):
        qc.h(i)

    # 2. Problem Cost Phase Shift
    for i in range(num_qubits):
        # Single-qubit bias (diagonal loss term)
        if qubo_matrix[i, i] != 0:
            qc.rz(2 * gamma * qubo_matrix[i, i], i)
            
        for j in range(i + 1, num_qubits):
            weight = qubo_matrix[i, j]
            if weight != 0:
                # Two-qubit coupling for line crossings and fault resilience
                qc.cx(i, j)
                qc.rz(2 * gamma * weight, j)
                qc.cx(i, j)

    # 3. Mixer Phase Shift
    for i in range(num_qubits):
        qc.rx(2 * beta, i)

    # 4. Measurement
    qc.measure(list(range(num_qubits)), list(range(num_qubits)))

    return qc, backend


def execute_qaoa_job(
    circuit: QuantumCircuit,
    backend: Any,
    config: Dict[str, Any]
) -> Dict[str, int]:
    """
    Dispatches a QAOA circuit job to the Quantum Rings backend and collects measurement counts.
    """
    shots = config["quantum_parameters"].get("shots", 1000)

    print(f"Submitting QAOA job to Quantum Rings backend '{backend.name}' ({shots} shots)...")
    job = backend.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    return counts


if __name__ == "__main__":
    # 1. Initialize credentials and provider
    provider_inst = get_quantum_rings_provider()

    # 2. Mock QUBO matrix
    mock_qubo = np.array([
        [0.3, 5.0, 0.2, 0.2],
        [5.0, 0.5, 0.2, 0.2],
        [0.2, 0.2, 0.8, 5.0],
        [0.2, 0.2, 5.0, 0.4]
    ])

    # 3. Build QAOA circuit
    test_qc, test_backend = build_qaoa_circuit(mock_qubo, provider=provider_inst, gamma=0.75, beta=0.35)
    
    print("QAOA Circuit built successfully.")
    print(f"Number of qubits: {test_qc.num_qubits}")
    print(f"Bound to backend: {test_backend.name}")