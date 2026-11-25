# quantum-compiler
A lightweight, modular hardware-aware quantum circuit compiler written in Python. `qcompiler` lowers high-level Qiskit circuits into a hardware-agnostic Intermediate Representation (IR), maps and routes them onto a constrained 1D linear quantum processor, synthesizes native gate sequences, and formally verifies unitary equivalence.


## Target Hardware Model

By default, `qcompiler` targets a 4-qubit superconducting processor with nearest-neighbor linear connectivity and a native microwave/entangling basis set:

* **Coupling Topology:** `q0 --- q1 --- q2 --- q3` (1D chain; non-adjacent two-qubit gates require SWAP routing)
* **Native Single-Qubit Gates:** `{Rz(θ), SX, X}`
* **Native Two-Qubit Gate:** `{CZ}` (configurable to `{CX}`)

## Compilation Pipeline

```text
Qiskit QuantumCircuit (All-to-All, Arbitrary Gates)
       │
       ▼
 [1. Parser]       Unrolls >2Q gates (CCX, MCX) into 1Q/2Q CircuitIR
       │
       ▼
 [2. Layout]       Maps high-interaction virtual qubits to adjacent physical nodes
       │
       ▼
 [3. Routing]      Inserts shortest-path SWAPs via NetworkX; tracks LayoutMap
       │
       ▼
 [4. Synthesis]    Decomposes SWAP -> 3 CX -> CZ; fuses 1Q gates into Rz-SX-Rz-SX-Rz
       │
       ▼
 [5. Emitter]      Outputs physical Qiskit QuantumCircuit
       │
       ├──► [Verify]     Checks U_compiled == P_final · U_original (up to global phase)
       └──► [Benchmark]  Compares depth, 2Q count, and fidelity vs. Qiskit O1 / O3
```

---

## Repository Structure

```text
qcompiler/
├── pyproject.toml             # Package metadata, dependencies, and build config
├── README.md                  # Project documentation and usage guide
├── src/
│   └── qcompiler/
│       ├── __init__.py        # Public package exports
│       ├── ir.py              # GateOp, CircuitIR, and bidirectional LayoutMap
│       ├── hardware.py        # NetworkX CouplingGraph & HardwareTarget specs
│       ├── parser.py          # Qiskit ingestion & multi-qubit gate unrolling
│       ├── layout.py          # Initial virtual-to-physical qubit placement
│       ├── routing.py         # Topology-aware SWAP insertion & permutation tracker
│       ├── synthesis.py       # ZSX Euler synthesis, CX->CZ translation, 1Q fusion
│       ├── emitter.py         # CircuitIR -> physical Qiskit QuantumCircuit converter
│       ├── verify.py          # Permutation-aware unitary equivalence checker
│       └── benchmark.py       # Depth, 2Q gate count, fidelity estimator & plots
├── tests/
│   ├── test_step1_ir.py       # Unit tests for IR, hardware graph, and parser
│   ├── test_routing.py        # Routing adjacency & permutation tracking tests
│   └── test_end_to_end.py     # Full-pipeline unitary verification tests
└── examples/
    └── benchmark_suite.py     # 4-qubit QPE & Grover benchmarks vs. Qiskit transpile()
```

---

## Installation

Create a virtual environment and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Core Dependencies
* `qiskit >= 1.0` (circuit frontend, operator extraction, and baseline transpiler)
* `networkx >= 3.0` (coupling graph modeling and shortest-path routing)
* `numpy >= 1.24` (unitary matrix math and Euler angle decomposition)
* `matplotlib >= 3.7` (benchmark comparison plots)
* `pytest >= 7.0` (automated verification suite)

---

## Quickstart

```python
from qiskit import QuantumCircuit
from qcompiler.hardware import HardwareTarget
from qcompiler.parser import parse_qiskit_circuit
from qcompiler.layout import compute_initial_layout
from qcompiler.routing import route_circuit
from qcompiler.synthesis import synthesize_circuit
from qcompiler.emitter import emit_qiskit_circuit
from qcompiler.verify import verify_equivalence

# 1. Define an uncompiled logical circuit with non-adjacent interactions
qc = QuantumCircuit(4)
qc.h(0)
qc.cx(0, 3)
qc.ccx(0, 1, 2)

# 2. Configure the 4-qubit linear hardware target
target = HardwareTarget.linear_4q(native_2q="cz")

# 3. Run the compilation passes
ir = parse_qiskit_circuit(qc, max_qubits=target.num_qubits)
ir.initial_layout = compute_initial_layout(ir, target)
routed_ir = route_circuit(ir, target)
native_ir = synthesize_circuit(routed_ir, target)

# 4. Emit physical circuit and verify unitary equivalence
compiled_qc = emit_qiskit_circuit(native_ir)
assert verify_equivalence(qc, compiled_qc, native_ir.final_layout)
print(compiled_qc.draw())
```

---

## Running Tests & Benchmarks

```bash
# Run unit and unitary-verification tests
pytest

# Run QPE and Grover benchmark suite against Qiskit optimization_level 1 & 3
python examples/benchmark_suite.py
```
