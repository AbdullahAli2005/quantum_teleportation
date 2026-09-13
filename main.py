from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity

def quantum_teleportation(theta=0.9):
    qc = QuantumCircuit(3, 3)

    # Step 0: Prepare the state to teleport on q0 (example: put it in some superposition)
    qc.rx(theta, 0)    # arbitrary state |ψ⟩ on q0 — replace with your actual state prep
    qc.barrier()

    # Step 1: Create Bell pair between q1 (Alice) and q2 (Bob)
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()

    # Step 2: Alice entangles q0 with q1
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()

    # Step 3: Alice measures q0 and q1
    qc.measure(0, 0)   # m1
    qc.measure(1, 1)   # m2
    qc.barrier()

    # Step 4: Bob applies corrections conditioned on classical bits
    with qc.if_test((qc.clbits[1], 1)):  # if m2 == 1, apply X
        qc.x(2)
    with qc.if_test((qc.clbits[0], 1)):  # if m1 == 1, apply Z
        qc.z(2)

    return qc


def verify_fidelity(theta=0.9, trials=20, seed=None):
    """Confirm q2 ends up in the original |ψ⟩ regardless of Alice's measurement outcomes.

    Runs the circuit `trials` times, each time collapsing the full statevector
    (including Alice's mid-circuit measurements), then reduces to q2's state and
    compares it against the target |ψ⟩ = Rx(theta)|0> via state fidelity.
    """
    target_circuit = QuantumCircuit(1)
    target_circuit.rx(theta, 0)
    target = Statevector.from_instruction(target_circuit)
    sim = AerSimulator(method="statevector")

    fidelities = []
    for _ in range(trials):
        qc = quantum_teleportation(theta)
        qc.save_statevector()
        result = sim.run(transpile(qc, sim), shots=1, seed_simulator=seed).result()
        full_state = result.get_statevector()
        bob_state = partial_trace(full_state, [0, 1])  # trace out Alice's qubits, keep q2
        fidelities.append(state_fidelity(bob_state, target))
    return fidelities


if __name__ == "__main__":
    qc = quantum_teleportation()
    qc.measure(2, 2)  # to verify q2 now holds |ψ⟩

    sim = AerSimulator()
    result = sim.run(transpile(qc, sim), shots=1000).result()
    print("Measurement counts (c2 c1 c0):", result.get_counts())

    fidelities = verify_fidelity()
    print(f"Fidelity over {len(fidelities)} trials: "
          f"min={min(fidelities):.6f}, max={max(fidelities):.6f}")