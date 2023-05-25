class Node:
    def __init__(self, parent):
        # parent graph
        self.parent = parent
        self.terminal = []


class Component:
    def __init__(self):
        self.terminal = []


class Element(Component):
    def __init__(self):
        super().__init__()
        self.attr = {  # Attributes
            'R': 0,  # Resistance
            'V': 0,  # Voltage source
            'I': 0  # Current source
        }

        self.current = {
            'curr': 0,  # Current current
            'prev': 0,  # Current of previous timestep
            'd': [0],  # Derivations of current with respect to time
            'i': [0]  # Integrations of current with respect to time

            # Examples of index of derivations and integrations
            # ['d'][0] : First derivation
            # ['d'][1] : Second derivation
        } 

        self.voltage = {  # Terminal voltage = V_terminal[1] - V_terminal[0]
            'curr': 0,  # Current voltage
            'prev': 0,  # Voltage of previous timestep
            'd': [0],  # Derivations of voltage with respect to time
            'i': [0]  # Integrations of voltage with respect to time
        }

    def update_inertial_values(self):
        pass


class Graph(Component):
    def __init__(self):
        super().__init__()

        self.label = ''
        self.terminal_join = []
        self.node = []
        self.components = []


class Resistor(Element):
    pass


class Inductor(Element):
    pass


class Capacitor(Element):
    pass
