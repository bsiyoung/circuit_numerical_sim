import Circuit

v1 = Circuit.VSource('V1', 10, [None, None])
Circuit.add_element(v1)

r1 = Circuit.Resistor('R1', 2, [v1.port[1], None])
Circuit.add_element(r1)

r2 = Circuit.Resistor('R2', 5, [r1.port[1], v1.port[0]])
Circuit.add_element(r2)

r3 = Circuit.Resistor('R3', 3, [r1.port[1], v1.port[0]])
Circuit.add_element(r3)

Circuit.gnd.append(v1.port[0])

mat = Circuit.gen_circuit_matrix()
mat = Circuit.rref(mat)
print(mat)
