import numpy as np

node_count = 0
nodes = []
elements = []
gnd = []


class Node:
    def __init__(self, label):
        self.label = label
        self.elements = []


class Element:
    def __init__(self, label, resistance, voltage, current, port):
        self.label = label
        self.resistance = resistance
        self.voltage = voltage
        self.current = current
        self.port = port

        if port[0] is None or port[1] is None:
            pass
        else:
            if port[0] is port[1]:
                raise Exception('Same Ports')


class Resistor(Element):
    def __init__(self, label, resistive, port):
        super().__init__(label, resistive, 0, 0, port)


class VSource(Element):
    def __init__(self, label, voltage, port):
        super().__init__(label, 0, voltage, 0, port)


class ISource(Element):
    def __init__(self, label, current, port):
        super().__init__(label, 0, 0, current, port)


def add_element(element):
    global node_count
    global nodes, elements

    elements.append(element)

    for i in [0, 1]:
        if element.port[i] is None:
            node_label = 'node_' + str(node_count)
            node_count += 1

            new_node = Node(node_label)
            nodes.append(new_node)
            element.port[i] = new_node

        element.port[i].elements.append([element, i])


def del_element(element):
    global nodes, elements
    global gnd

    for i in [0, 1]:
        n = element.port[i]
        for j in range(len(n.elements)):
            if n.elements[j][0] is element:
                del n.elements[j]

        if len(n.elements) == 0:
            for j in range(len(nodes)):
                if nodes[j] is n:
                    del nodes[j]

            for j in range(len(gnd)):
                if gnd[j] is n:
                    del gnd[j]

    del elements[element.label]


def gen_circuit_matrix():
    global nodes, elements
    global gnd

    mat_width = len(elements) + len(nodes) + 1
    res = []

    for i in range(len(elements)):
        e = elements[i]
        if e.voltage != 0:
            buf = [0 for j in range(mat_width)]
            cnt = 0
            for j in range(len(nodes)):
                if nodes[j] is e.port[0]:
                    buf[j] = -1
                    cnt += 1

                if nodes[j] is e.port[1]:
                    buf[j] = 1
                    cnt += 1

                if cnt == 2:
                    break
            buf[-1] = e.voltage
            res.append(buf)

        if e.current != 0:
            buf = [0 for j in range(mat_width)]
            buf[len(nodes) + i] = 1
            buf[-1] = e.current
            res.append(buf)

        if e.resistance != 0:
            buf = [0 for j in range(mat_width)]
            cnt = 0
            for j in range(len(nodes)):
                if nodes[j] is e.port[0]:
                    buf[j] = -1
                    cnt += 1

                if nodes[j] is e.port[1]:
                    buf[j] = 1
                    cnt += 1

                if cnt == 2:
                    break
            buf[len(nodes) + i] = e.resistance
            res.append(buf)

    for i in range(len(nodes)):
        buf = [0 for j in range(mat_width)]
        for j in range(len(nodes[i].elements)):
            e_info = nodes[i].elements[j]
            in_out = -1 if e_info[1] == 0 else 1
            for k in range(len(elements)):
                if e_info[0] is elements[k]:
                    buf[len(nodes) + k] = in_out
                    break

        res.append(buf)

    for i in range(len(gnd)):
        buf = [0 for j in range(mat_width)]
        for j in range(len(nodes)):
            if gnd[i] is nodes[j]:
                buf[i] = 1
        res.append(buf)

    return np.array(res, dtype=np.float32)


def rref(mat):
    for i in range(len(mat)):
        if mat[i][i] == 0:
            for j in range(i, len(mat)):
                if mat[j][i] != 0:
                    for k in range(len(mat[0])):
                        tmp = mat[j][k]
                        mat[j][k] = mat[i][k]
                        mat[i][k] = tmp
                    break
        if mat[i][i] == 0:
            continue

        mat[i] /= mat[i][i]

        for j in range(len(mat)):
            if j != i:
                mat[j] -= mat[j][i] * mat[i]

    return mat

