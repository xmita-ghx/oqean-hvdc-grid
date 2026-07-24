# OQEAN: Quantum-Accelerated Subsea HVDC Cable Routing Optimization

OQEAN is an end-to-end quantum optimization framework designed to compute optimal subsea High-Voltage Direct Current (HVDC) power line routes. By mapping spatial, thermal, transmission, and structural fault-resilience constraints into Quadratic Unconstrained Binary Optimization (QUBO) formulations, OQEAN executes Quantum Approximate Optimization Algorithm (QAOA) circuits using the Quantum Rings SDK simulator and provides an interactive visualization.

---

# Technical Overview

Subsea HVDC grid deployment requires balancing direct power transmission efficiency against environmental and structural penalties, such as cable line crossings, trench depth limits, and **N-1** grid fault resilience.

OQEAN models candidate cable routing variables as binary vectors

$$
x \in \{0,1\}^n
$$

and constructs an upper-triangular cost matrix \(Q\). The optimization objective is

$$
\min_x f(x)=x^TQx
=\sum_{i=1}^{n}Q_{ii}x_i
+\sum_{i<j}Q_{ij}x_ix_j
$$

where:

- **Diagonal terms** (\(Q_{ii}\)) represent cable transmission losses, thermal dissipation, and bathymetric trench cost coefficients.
- **Off-diagonal terms** (\(Q_{ij}\)) encode structural interference penalties, cable crossings, and redundancy constraints required for **N-1** fault tolerance.

The constructed QUBO is compiled into a multi-qubit QAOA circuit parameterized by problem angles \(\gamma\) and mixer angles \(\beta\). The circuit is executed on the **Quantum Rings** backend (`scarlet_quantum_rings`), and measurement outcomes are ranked according to their energy expectation values.

---

# System Architecture & Repository Structure

```text
oqean-hvdc-grid/
│
├── config/
│   └── grid_config.json
│
├── docs/
│   └── data/
│       └── results.json
│
├── notebooks/
│   └── oqean_interactive.ipynb
│
├── src/
│   ├── __init__.py
│   ├── evaluator.py
│   ├── inputs.py
│   ├── quantum_circuit.py
│   └── qubo.py
│
├── .env.example
├── .gitignore
├── index.html
├── README.md
└── requirements.txt
```

## Directory Overview

| File | Description |
|------|-------------|
| `config/grid_config.json` | Stores topology parameters, penalty weights, and QAOA settings |
| `docs/data/results.json` | Auto-generated optimization results consumed by the web dashboard |
| `notebooks/oqean_interactive.ipynb` | Interactive Jupyter notebook |
| `src/inputs.py` | Configuration loader and CLI input parser |
| `src/qubo.py` | QUBO matrix formulation engine |
| `src/quantum_circuit.py` | Quantum Rings SDK interface and QAOA circuit builder |
| `src/evaluator.py` | Energy evaluator and JSON exporter |
| `index.html` | Interactive GitHub Pages dashboard |
| `requirements.txt` | Python dependencies |

---

# Core System Components

## 1. Configuration Engine (`src/inputs.py`)

Loads project configuration, bathymetric trench metadata, cable segment definitions, and QAOA execution parameters from `config/grid_config.json`. Supports fallback interactive CLI inputs.

---

## 2. QUBO Matrix Generator (`src/qubo.py`)

Converts transmission losses and engineering constraints into an \(N \times N\) NumPy matrix \(Q\). Large off-diagonal penalty values discourage invalid routing combinations during quantum optimization.

---

## 3. Quantum Circuit Builder (`src/quantum_circuit.py`)

Authenticates with **QuantumRingsLib** using API credentials and constructs a single-layer QAOA circuit using:

- Hadamard initialization
- \(R_z\) problem rotations
- \(R_x\) mixer rotations
- Controlled-NOT (CX) entangling gates

The compiled circuit is submitted to the `scarlet_quantum_rings` simulator backend.

---

## 4. Evaluation Engine (`src/evaluator.py`)

Computes energy values

$$
x^TQx
$$

for sampled bitstrings, ranks solutions according to probability, prints formatted terminal reports, and exports structured JSON data to

```text
docs/data/results.json
```

---

## 5. Interactive Dashboard (`index.html`)

The GitHub Pages dashboard visualizes optimization results using modern JavaScript libraries.

### Features

- Candidate solution leaderboard
- Energy landscape visualization (Plotly)
- Grid topology diagram (Mermaid)
- Geographic route visualization (Leaflet)

---

# Installation

## Prerequisites

- Python 3.10+
- Git
- Quantum Rings API credentials

---

## Clone the Repository

```bash
git clone https://github.com/<your-username>/oqean-hvdc-grid.git

cd oqean-hvdc-grid
```

---

## Create a Virtual Environment

### Windows (PowerShell)

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

```env
QUANTUMRINGS_TOKEN=your_quantum_rings_token_here
QUANTUMRINGS_NAME=your_account_name_here
```

---

# Execution Workflows

## Command-Line Execution

Run the complete optimization pipeline:

```bash
python -m src.evaluator
```

### Example Output

```text
============================================================
 OQEAN HVDC GRID - QAOA ROUTING OPTIMIZATION REPORT
============================================================

Total Quantum Shots Evaluated: 1000

Rank | Bitstring | Cost (Energy) | Probability
------------------------------------------------------------
1    | 1010      | 1.1000        | 34.20%
2    | 0101      | 1.3000        | 28.50%
3    | 1001      | 5.8000        | 12.10%

============================================================

Web results successfully exported to
docs/data/results.json
```

---

## Interactive Notebook

Open

```text
notebooks/oqean_interactive.ipynb
```

Then:

1. Select the project's virtual environment.
2. Run all notebook cells.
3. Explore the generated QUBO matrices and QAOA circuits interactively.

---

## GitHub Pages Deployment

Generate fresh optimization results:

```bash
python -m src.evaluator
```

Commit the updated dashboard assets:

```bash
git add index.html docs/data/results.json

git commit -m "docs: publish updated QAOA subsea routing results"

git push origin main
```

Enable **GitHub Pages** from:

```
Settings → Pages
```

using:

- **Branch:** `main`
- **Folder:** `/ (root)`

---

# Mathematical Example

For four candidate cable routes

$$
(x_0,x_1,x_2,x_3)
$$

the QUBO matrix is

$$
Q=
\begin{pmatrix}
0.3 & 5.0 & 0.2 & 0.2\\
0.0 & 0.5 & 0.2 & 0.2\\
0.0 & 0.0 & 0.8 & 5.0\\
0.0 & 0.0 & 0.0 & 0.4
\end{pmatrix}
$$

where

- **Diagonal entries** represent linear cable costs.
- **Penalty terms** such as

$$
Q_{01}=5.0,\qquad
Q_{23}=5.0
$$

discourage selecting mutually incompatible cable routes due to trench overlap.

---

# Technology Stack

## Programming

- Python 3.10+

## Quantum Computing

- QuantumRingsLib

## Scientific Computing

- NumPy
- python-dotenv

## Visualization

### Python

- Matplotlib

### Web

- HTML5
- CSS3
- JavaScript (ES6+)
- Plotly.js
- Leaflet.js
- Mermaid.js

## Deployment

- GitHub Pages
