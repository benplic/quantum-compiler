from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

@dataclass
class GateOp:
    """A gate operation in a quantum circuit.

    Attributes:
        name: The name of the gate.
        qubits: The qubits that the gate acts on.
        params: The parameters of the gate.
    """
    name: str
    qubits: tuple[int, ...]
    params: tuple[float, ...] = ()
    matrix: Any | None = field(default=None, repr=False)

    @property
    def num_qubits(self) -> int:
        return len(self.qubits)

    @property
    def is_two_qubit_gate(self) -> bool:
        return self.num_qubits == 2

    def __str__(self) -> str:
        param_str = f"({', '.join(map(str, self.params))})" if self.params else ""
        qubit_str = ", ".join(map(str, self.qubits))
        return f"{self.name}{param_str} on qubits {qubit_str}"

@dataclass
class LayoutMap:
    """A mapping from virtual (logical) qubits to physical qubits."""

    v2p: dict[int, int]
    p2v: dict[int, int] = field(init=False)

    def __post_init__(self) -> None:
        if len(set(self.v2p.values())) != len(self.v2p):
            raise ValueError("Duplicate physical qubits in virtual-to-physical mapping.")
        self.p2v = {v: k for k, v in self.v2p.items()}

    @classmethod
    def trivial(cls, num_qubits: int) -> LayoutMap:
        """Create a trivial layout map where virtual qubits map to the same physical qubits."""
        return cls({i: i for i in range(num_qubits)})

    def to_physical(self, virtual_qubit: int) -> int:
        return self.v2p[virtual_qubit]

    def to_virtual(self, physical_qubit: int) -> int:
        return self.p2v[physical_qubit]

    def swap_physical(self, p0:int, p1:int) -> None:
        """Swap the physical qubits p0 and p1 in the layout map."""
        v0 = self.p2v[p0]
        v1 = self.p2v[p1]
        self.v2p[v0], self.v2p[v1] = p1, p0
        self.p2v[p0], self.p2v[p1] = v1, v0

    def copy(self) -> LayoutMap:
        """Return a copy of the layout map."""
        return LayoutMap(dict(self.v2p))

@dataclass
class CircuitIR:
    """A hardware-agnostic intermediate representation of a entire quantum circuit."""

    num_qubits: int
    ops: list[GateOp] = field(default_factory=list)
    initial_layout: LayoutMap | None = None
    final_layout: LayoutMap | None = None

    def append(self, op: GateOp) -> None:
        if any(q < 0 or q >= self.num_qubits for q in op.qubits):
            raise ValueError(f"Gate {op} references qubit outside [0, {self.num_qubits - 1}].")
        self.ops.append(op)

    def two_qubit_ops(self) -> list[GateOp]:
        """Return a list of all two-qubit gate operations in the circuit."""
        return [op for op in self.ops if op.is_two_qubit_gate]

    def gate_counts(self) -> dict[str, int]:
        """Return a dictionary mapping gate names to their counts."""
        counts: dict[str, int] = {}
        for op in self.ops:
            counts[op.name] = counts.get(op.name, 0) + 1
        return counts

    def __len__(self) -> int:
        return len(self.ops)

    def __str__(self) -> str:
        header = f"CircuitIR(num_qubits={self.num_qubits}, total_ops={len(self.ops)})"
        body = "\n".join(f"  {idx:03d}: {op}" for idx, op in enumerate(self.ops))
        return f"{header}\n{body}"
