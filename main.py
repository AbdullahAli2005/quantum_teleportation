from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def quantum_teleportation():
    qc = QuantumCircuit(3, 3)

    # Step 0: Prepare the state to teleport on q0 (example: put it in some superposition)
    qc.rx(0.9, 0)      # arbitrary state |ψ⟩ on q0 — replace with your actual state prep
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

qc = quantum_teleportation()
qc.measure(2, 2)  # to verify q2 now holds |ψ⟩

sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=1000).result()
print(result.get_counts())