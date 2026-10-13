"""
VQE molecular ground-state energy prototype.

The H2 model is the original validated prototype.
N2 and N2 + catalyst are included as REDUCED EFFECTIVE 2-qubit
demonstration models so the same VQE workflow can be shown for the
nitrogen-fixation direction without claiming a full ab-initio catalyst
calculation.

Pipeline:
Molecule/system -> Hamiltonian -> Qubit mapping -> Quantum circuit
-> Energy measurement -> Classical optimization -> Ground-state estimate
"""

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp, Statevector


# -------------------------------------------------------------------
# Molecular/system Hamiltonians
# -------------------------------------------------------------------
# H2: original project Hamiltonian, mapped to 2 qubits.
H2_TERMS = [
    ("II", -1.052373245772859),
    ("IZ",  0.397937424843180),
    ("ZI", -0.397937424843180),
    ("ZZ", -0.011280104256235),
    ("XX",  0.180931199784231),
]

# IMPORTANT:
# These are reduced effective 2-qubit demonstration Hamiltonians.
# They are NOT full ab-initio N2 or catalyst Hamiltonians.
# They let the prototype demonstrate the same VQE workflow for the
# nitrogen-fixation direction while keeping the current 2-qubit UI.
N2_TERMS = [
    ("II", -0.90),
    ("IZ",  0.32),
    ("ZI", -0.32),
    ("ZZ", -0.08),
    ("XX",  0.22),
]

N2_CATALYST_TERMS = [
    ("II", -1.00),
    ("IZ",  0.30),
    ("ZI", -0.30),
    ("ZZ", -0.12),
    ("XX",  0.25),
]

SYSTEMS = {
    "H₂ (Hydrogen)": {
        "terms": H2_TERMS,
        "description": "Original 2-qubit H₂ prototype.",
        "type": "Prototype molecule",
    },
    "N₂ (Nitrogen) — reduced model": {
        "terms": N2_TERMS,
        "description": "Reduced 2-qubit effective model used to demonstrate the N₂ direction.",
        "type": "Nitrogen-fixation molecule",
    },
    "N₂ + Fe catalyst — reduced model": {
        "terms": N2_CATALYST_TERMS,
        "description": "Reduced 2-qubit effective model representing an N₂–Fe catalytic interaction.",
        "type": "Catalytic-system demonstration",
    },
}


def get_hamiltonian(system_name="H₂ (Hydrogen)"):
    """Return the selected system's Pauli Hamiltonian."""
    if system_name not in SYSTEMS:
        raise ValueError(f"Unknown system: {system_name}")
    return SparsePauliOp.from_list(SYSTEMS[system_name]["terms"])


def get_terms(system_name="H₂ (Hydrogen)"):
    return SYSTEMS[system_name]["terms"]


# -------------------------------------------------------------------
# VQE ansatz
# -------------------------------------------------------------------
def build_circuit():
    """Build the same simple 2-qubit parameterized circuit."""
    theta = Parameter("θ")
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.ry(theta, 1)
    qc.cx(1, 0)
    return qc, theta


def calculate_energy(qc, theta, hamiltonian, value):
    """Calculate E(theta) = <psi(theta)|H|psi(theta)>."""
    state = Statevector(qc.assign_parameters({theta: value}))
    return float(state.expectation_value(hamiltonian).real)


def run_vqe(system_name="H₂ (Hydrogen)", initial_theta=2.0):
    """Run the classical optimization around the quantum energy evaluation."""
    hamiltonian = get_hamiltonian(system_name)
    qc, theta = build_circuit()

    history = []

    def cost(x):
        energy = calculate_energy(qc, theta, hamiltonian, x[0])
        history.append(energy)
        return energy

    result = minimize(
        cost,
        x0=[initial_theta],
        method="COBYLA",
        options={"maxiter": 100},
    )

    # Exact eigenvalue is used only as a simulator-side reference for this
    # reduced Hamiltonian; VQE still performs the variational optimization.
    exact = float(np.linalg.eigvalsh(hamiltonian.to_matrix()).min())

    return {
        "system": system_name,
        "circuit": qc,
        "history": history,
        "initial_energy": history[0],
        "energy": float(result.fun),
        "theta": float(result.x[0]),
        "iterations": len(history),
        "exact": exact,
        "converged": abs(result.fun - exact) < 1e-3,
        "terms": get_terms(system_name),
        "description": SYSTEMS[system_name]["description"],
        "type": SYSTEMS[system_name]["type"],
    }
