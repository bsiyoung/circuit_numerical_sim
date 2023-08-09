from __future__ import annotations

from typing import Union


class Circuit:
    def __init__(self, parent: Circuit):
        self.__parent = parent
        self.__gnd = []
        self.__node = []
        self.__element = []

    def add_element(self,
                    element: Element,
                    node: Union[tuple[Node, Node], list[Node, Node]] = (None, None)):
        # Check is adding available
        if element.parent is not None:
            raise Exception("")

        if element in self.__element:
            raise Exception("")

        # Check are nodes available

        # Add element to circuit
        self.__element.append(element)

    def run(self, sim_time):
        pass

    def rm_node(self, node):
        self.__node.remove(node)


class Element:
    def __init__(self, node: Union[tuple[Node, Node], list[Node, Node]] = (None, None)):
        self.parent = None
        self.__conf = {
            'volt_supply': 0,  # Power source
            'curr_supply': 0,
            'resistance': 0,  # Passive circuit element
            'inductance': 0,
            'capacitance': 0
        }
        self.__node = [node[0], node[1]]

    def __getitem__(self, item):
        if type(item) is int:
            return self.__node[item]

        if type(item) is str:
            return self.__conf[item]

    def __setitem__(self, key, value):
        if type(key) is int:
            if self.__node[key] is not None:
                self.__node[key].remove(self)
            self.__node[key] = value

        if type(key) is str:
            self.__conf[key] = value


class Node:
    def __init__(self, parent: Circuit):
        self.__parent = parent
        self.__component = []

    def append(self, comp: Element, node_idx: int):
        self.__component.append(comp)
        comp[node_idx] = self

    def remove(self, comp):
        self.__component.remove(comp)

        if len(self.__component) == 0:
            self.__parent.rm_node(self)
