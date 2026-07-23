"""
oqean-hvdc-grid: Quantum Circuit & Execution Module

Constructs QAOA ansatz circuits for subsea cable routing and dispatches execution
jobs to the Quantum Rings SDK simulator.
"""

import os
from typing import Dict, Any, Tuple
import numpy as np
from dotenv import load_dotenv

from QuantumRingsLib import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    QuantumRingsProvider
)


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

    return QuantumRingsProvider(token=token, name=account_name)


def build_qaoa_circuit(qubo_matrix: np.ndarray, gamma: float = 0.75, beta: float = 0.35) -> QuantumCircuit:
    """
    Constructs a 1-step QAOA circuit based on the given QUBO cost matrix.

    Circuit Architecture:
        1. Equal Superposition: Apply Hadamard gates across all qubits.
        2. Problem Hamiltonian: Apply RZ (diagonal loss) and ZZ coupling (crossings/faults).
        3. Mixer Hamiltonian: Apply RX rotations across all qubits.
        4. Measurement: Measure all qubits into classical bits.

    Args:
        qubo_matrix: N x N QUBO cost matrix.
        gamma: Problem Hamiltonian phase rotation angle.
        beta: Mixer Hamiltonian phase rotation angle.

    Returns:
        QuantumCircuit: Constructed Quantum Rings circuit object.
    """
    num_qubits = qubo_matrix.shape[0]
    qr = QuantumRegister(num_qubits, "cable")
    cr = ClassicalRegister(num_qubits, "select")
    qc = QuantumCircuit(qr, cr)

    # 1. Prepare Initial Superposition
    for i in range(num_qubits):
        qc.h(qr[i])

    # 2. Problem Cost Phase Shift
    for i in range(num_qubits):
        # Single-qubit bias (diagonal loss term)
        if qubo_matrix[i, i] != 0:
            qc.rz(2 * gamma * qubo_matrix[i, i], qr[i])
            
        for j in range(i + 1, num_qubits):
            weight = qubo_matrix[i, j]
            if weight != 0:
                # Two-qubit coupling for line crossings and fault resilience
                qc.cx(qr[i], qr[j])
                qc.rz(2 * gamma * weight, qr[j])
                qc.cx(qr[i], qr[j])

    # 3. Mixer Phase Shift
    for i in range(num_qubits):
        qc.rx(2 * beta, qr[i])

    # 4. Measurement
    qc.measure(qr, cr)

    return qc


def execute_qaoa_job(
    circuit: QuantumCircuit,
    config: Dict[str, Any]
) -> Dict[str, int]:
    """
    Dispatches a QAOA circuit job to the Quantum Rings backend and collects measurement counts.

    Args:
        circuit: Constructed QuantumCircuit object.
        config: Configuration dictionary containing backend_name and shots.

    Returns:
        Dict[str, int]: Measurement counts dictionary (e.g. {'1010': 342, '0101': 210}).
    """
    provider = get_quantum_rings_provider()
    backend_name = config["quantum_parameters"].get("backend_name", "scarlet_quantum_rings")
    shots = config["quantum_parameters"].get("shots", 1000)

    backend = provider.get_backend(backend_name)
    
    print(f"Submitting QAOA job to Quantum Rings backend '{backend_name}' ({shots} shots)...")
    job = backend.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    return counts


if __name__ == "__main__":
    # Test circuit construction with mock QUBO matrix
    mock_qubo = np.array([
        [0.3, 5.0, 0.2, 0.2],
        [5.0, 0.5, 0.2, 0.2],
        [0.2, 0.2, 0.8, 5.0],
        [0.2, 0.2, 5.0, 0.4]
    ])
    
    test_qc = build_qaoa_circuit(mock_qubo, gamma=0.75, beta=0.35)
    print("QAOA Circuit built successfully.")
    print(f"Number of qubits: {test_qc.num_qubits}")