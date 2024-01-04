import CalcGraph
import Circuit
import numpy as np

import Component


class CircuitMatrix:
    def __init__(self, circuit: Circuit.Circuit):
        self.circuit = circuit
        self.matrix = None

    def generate_matrices(self, dt=1e-6):
        node, element = self.circuit.unfold()

        sz_mat = len(node) + len(element)
        mat = np.array([[CalcGraph.Number(0) for i in range(sz_mat)] for j in range(sz_mat)])
        const_mat = np.array([[CalcGraph.Number(0)] for i in range(sz_mat)])
        self.matrix = [mat, const_mat]

        # mat column index
        # 0 ~ len(node) - 1 : voltage of node
        # len(node) ~ sz_mat - 1 : current of element

        # mat row index
        # 0 ~ len(element) - 1 : (1) voltage difference between two nodes of elements
        #                        (2) reference voltage (Ground; GND)
        # len(element) ~ sz_mat - 1 : KCL

        for e_idx, e in enumerate(element):
            volt_row_idx = e_idx
            current_col_idx = len(node) + e_idx

            n0 = e.pin[0].get_highest_level_node()
            n0_idx = node.index(n0)
            kcl_row_idx_0 = len(element) + n0_idx

            if type(e) is Component.IdealGround:
                mat[volt_row_idx][n0_idx] = CalcGraph.Number(1)
                mat[kcl_row_idx_0][current_col_idx] = CalcGraph.Number(-1)
                continue

            n1 = e.pin[1].get_highest_level_node()
            n1_idx = node.index(n1)
            kcl_row_idx_1 = len(element) + n1_idx

            mat[volt_row_idx][n0_idx] = e.get_voltage_coefficient(dt=dt)
            mat[volt_row_idx][n1_idx] = -e.get_voltage_coefficient(dt=dt)
            mat[volt_row_idx][current_col_idx] = e.get_current_coefficient(dt=dt)
            const_mat[volt_row_idx][0] = e.get_constant(dt=dt)

            # KCL
            mat[kcl_row_idx_0][current_col_idx] = CalcGraph.Number(-1)
            mat[kcl_row_idx_1][current_col_idx] = CalcGraph.Number(1)

    @staticmethod
    def get_determinant_graph(mat: np.ndarray) -> CalcGraph.Node:
        shape = mat.shape
        if shape[0] != shape[1]:
            return CalcGraph.Number(np.NaN)

        if shape[0] == 2:
            return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]

        res = CalcGraph.Number(0)
        for i in range(shape[0]):
            if mat[0][i] == 0:
                continue

            col_list = list(range(shape[0]))
            col_list.remove(i)
            sub_det = CircuitMatrix.get_determinant_graph(mat[1:, col_list])

            if i % 2 == 0:
                res += mat[0][i] * sub_det
            else:
                res -= mat[0][i] * sub_det

        return res

