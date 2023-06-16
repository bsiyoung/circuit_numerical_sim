class Circuit:
    def __init__(self):
        self.__nodes = []
        self.__node_cnt = 0
        self.__elements = {}

    def run(self):
        pass

    def __del_node(self, node):
        pass

    def connect(self, e1, p1, e2, p2):
        pass


class Node:
    def __init__(self, parent):
        self.__elements = []
        self.__parent = parent

    def add_element(self, element):
        self.__elements.append(element)

    def del_element(self, element):
        # Search and remove element from list
        for i in range(len(self.__elements)):
            if self.__elements[i] is element:
                del self.__elements[i]
                break

        # Remove this node from circuit if there is no element connected this node
        if len(self.__elements) == 0:
            self.__parent.__del_node(self)


class Element:
    def __init__(self, circuit, port=None):
        if port is None:
            port = [None, None]
        self._resistance = 0
        self._voltage = 0
        self._current = 0

        self.__port = port

    def __getitem__(self, item):
        if item != 0 and item != 1:
            return None

        return self.__port[item]


class Resistor(Element):
    def __init__(self, resistance, circuit, port=None):
        super().__init__(circuit, port=port)
        self._resistance = resistance


class DCVSource(Element):
    def __init__(self, voltage, circuit, port=None):
        super().__init__(circuit, port=port)
        self._voltage = voltage


class DCISource(Element):
    def __init__(self, current, circuit, port=None):
        super().__init__(circuit, port=port)
        self._current = current
