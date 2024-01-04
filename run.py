import time

import Circuit
import Component
import CircuitMatrix


circuit = Circuit.Circuit()

v_in = Component.VoltageSource(parent=circuit, v_th=10, r_th=1e-3)
r = Component.Resistor(parent=circuit, r=100)
ground = Component.Ground(parent=circuit)

v_in.pin[0].connect(r.pin[0])
v_in.pin[1].connect(r.pin[1])
ground.pin[0].connect(r.pin[1])

circuit_mat = CircuitMatrix.CircuitMatrix(circuit=circuit)
circuit_mat.generate_matrices(dt=1e-6)

mats = circuit_mat.matrix
for row in mats[0]:
    print(row)

print()
print()
for row in mats[1]:
    print(row)

print()
print()

print(len(circuit.node))
print(len(circuit.component))

det = circuit_mat.get_determinant_graph(mats[0])
print(det)
v_in['R_th'].set_value(100)
print(det)
