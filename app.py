"""
Streamlit website for the molecular ground-state energy VQE prototype.

The app supports:
1. H2 - original prototype
2. N2 - reduced effective model
3. N2 + Fe catalyst - reduced effective catalytic-system model

The N2 and catalyst options are explicitly labelled as reduced models.
"""

import streamlit as st
import matplotlib.pyplot as plt
from vqe import run_vqe, SYSTEMS

st.set_page_config(
    page_title="Molecular Ground-State Energy Estimator",
    page_icon="⚛️",
)

st.title("⚛️ Molecular Ground-State Energy Estimator")
st.caption("Quantum Computing | Algorithm: VQE | Execution: Quantum Simulator")

# ---------------- INPUT ----------------
st.header("Input")

system = st.selectbox(
    "Molecule / System",
    list(SYSTEMS.keys()),
)

initial_theta = st.slider(
    "Initial variational parameter θ",
    -3.0, 3.0, 2.0, 0.1,
)

st.info(SYSTEMS[system]["description"])

# ---------------- PROCESSING ----------------
st.header("Processing")

if system == "H₂ (Hydrogen)":
    label = "Hamiltonian (H₂, mapped to 2 qubits)"
elif system.startswith("N₂ (Nitrogen)"):
    label = "Hamiltonian (N₂, reduced 2-qubit model)"
else:
    label = "Hamiltonian (N₂ + Fe catalyst, reduced 2-qubit model)"

st.markdown(f"**{label}:**  H = Σ cᵢPᵢ")

terms = SYSTEMS[system]["terms"]
st.table({
    "Pauli term Pᵢ": [t for t, _ in terms],
    "Coefficient cᵢ": [round(c, 4) for _, c in terms],
})

if system != "H₂ (Hydrogen)":
    st.caption(
        "Note: N₂ and N₂ + Fe are reduced effective demonstration models, "
        "not full ab-initio molecular/catalyst calculations."
    )

if st.button("▶ Run VQE", type="primary"):
    out = run_vqe(system, initial_theta)

    st.markdown("**Quantum circuit:**")
    st.code(str(out["circuit"].draw("text")))

    # ---------------- OUTPUT ----------------
    st.header("Output")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ground-state energy", f"{out['energy']:.6f} Hartree")
    c2.metric("Optimized θ", f"{out['theta']:.4f}")
    c3.metric("Iterations", out["iterations"])

    if out["converged"]:
        st.success(
            f"✓ Converged (reference minimum = {out['exact']:.6f} Hartree)"
        )
    else:
        st.warning("Not fully converged - try running again.")

    # Convergence graph
    st.subheader("Energy convergence")
    fig, ax = plt.subplots()
    ax.plot(
        range(1, len(out["history"]) + 1),
        out["history"],
        marker="o",
        label="VQE energy",
    )
    ax.axhline(
        out["exact"],
        linestyle="--",
        label="Reference minimum",
    )
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Energy (Hartree)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

    # Analysis
    st.subheader("Analysis")
    st.write(
        f"- Initial parameter gives energy: **{out['initial_energy']:.4f} Hartree**"
    )
    st.write("- The classical optimizer updates θ.")
    st.write("- The energy changes over successive iterations.")
    st.write(
        f"- The VQE result reaches a stable minimum: **{out['energy']:.6f} Hartree**"
    )

    if system == "H₂ (Hydrogen)":
        st.success(
            "H₂ is the original validated prototype used to demonstrate the VQE workflow."
        )
    elif system.startswith("N₂ (Nitrogen)"):
        st.info(
            "This demonstrates how the same VQE framework can be extended toward "
            "nitrogen-fixation molecular studies."
        )
    else:
        st.info(
            "This demonstrates the nitrogen-fixation catalyst direction using a "
            "reduced N₂–Fe effective model."
        )
