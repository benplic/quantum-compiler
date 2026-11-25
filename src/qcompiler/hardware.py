from dataclasses import dataclass, field
import networkx as nx

@dataclass
class HardwareTarget:
    """Represents physical QPU hardware, its gate sets, error characteristics, and connectivity."""

    name: str
    coupling_graph: nx.Graph
    native_1q_gates: frozenset[str] = frozenset({"rz", "sx", "x"})
    native_2q_gates: frozenset[str] = frozenset({"cz"})
    error_1q: float = 2.5e-4       # Typical superconducting 1Q gate error rate
    error_2q: float = 6.0e-3       # Typical superconducting 2Q CZ error rate
    _shortest_paths: dict[int, dict[int, list[int]]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not nx.is_connected(self.coupling_graph):
            raise ValueError("Hardware coupling graph must be a single connected component.")
        self._shortest_paths = dict(nx.all_pairs_shortest_path(self.coupling_graph))

    @classmethod
    def linear_4q(cls) -> HardwareTarget:
        """Create a simple linear 4-qubit hardware target."""
        return cls(
            name="LINEAR_4Q_QPU",
            coupling_graph=nx.path_graph(4),
            native_1q_gates=frozenset({"rz", "sx", "x"}),
            native_2q_gates=frozenset({"cz"}),
        )

    def are_connected(self, p0: int, p1: int) -> bool:
        """Check if two physical qubits are directly connected in the hardware."""
        return self.coupling_graph.has_edge(p0, p1)

    def neighbors(self, p: int) -> list[int]:
        """Return a list of indices of physical qubits that are directly connected to the given qubit."""
        return list(self.coupling_graph.neighbors(p))