import Circuit
import Component

circuit = Circuit.Circuit()

v_in = Component.VoltageSource(parent=circuit, v_th=10, r_th=1e-3)
r = Component.Resistor(parent=circuit, r=100)
ground = Component.GroundElement(parent=circuit)

v_in.pin[0].connect(r.pin[0])
v_in.pin[1].connect(r.pin[1])
ground.pin[0].connect(r.pin[1])

print(len(circuit.node))
print(len(circuit.component))
