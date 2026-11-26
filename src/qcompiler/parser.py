from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from .ir import CircuitIR, GateOp

def parse_qiskit_circuit(qc: QuantumCircuit, max_qubits: int = 4) -> CircuitIR:

    if qc.num_qubits > max_qubits:
        raise ValueError(f"Quantum circuit has {qc.num_qubits} qubits, which exceeds the maximum allowed {max_qubits} qubits.")

    # Unroll multi-qubit gates into 1- and 2-qubit gates
    unrolled = qc.copy()
    while any(inst.operation.num_qubits > 2 for inst in unrolled.data):
        unrolled = unrolled.decompose()

    # Create a CircuitIR object
    ir = CircuitIR(num_qubits=unrolled.num_qubits)
    for inst in unrolled.data:
        name = inst.operation.name.lower()
        if name == "barrier":
            continue  # Skip barriers
        if name in {"measure","reset"}:
            raise ValueError(f"Unsupported operation '{name}' in the circuit.")

        qubits = tuple(unrolled.find_bit_index(q) for q in inst.qubits)
        params = tuple(float(p) for p in inst.operation.params)
        matrix = Operator(inst.operation).data
        ir.append_gate(GateOp(name=name, qubits=qubits, params=params, matrix=matrix))

    return ir