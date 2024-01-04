from __future__ import annotations
from typing import overload
from typing import List, Tuple

import numpy as np

import Component
import CalcGraph


class Circuit:
    def __init__(self, parent: Component.PackageBase = None):
        self.parent = parent
        self.node: List[Node] = []
        self.component: List[Component.ComponentBase] = []

    def __getitem__(self, label: str):
        return self.find_by_label(label)

    def find_by_label(self, target_label: str) -> None | Component.ComponentBase | Node:
        if target_label == '':
            return None

        for comp in self.component:
            if comp.label == target_label:
                return comp

        for n in self.node:
            if n.label == target_label:
                return n

        return None

    def add_node(self, n: Node) -> bool:
        if self.find_by_label(n.label) is not None:
            return False

        self.node.append(n)
        return True

    def remove_node(self, n: Node) -> bool:
        if n is None:
            return False

        if type(n) != Node:
            return False

        self.node.remove(n)
        return True

    def add_component(self, comp: Component.ComponentBase) -> bool:
        if self.find_by_label(comp.label) is not None:
            return False

        self.component.append(comp)
        return True

    def remove_component(self, comp: Component.ComponentBase) -> bool:
        # Detach from circuit
        node_buf = comp.pin.copy()
        for i in range(len(comp.pin)):
            comp.pin[i] = None

        # Remove component from nodes
        for i in range(len(node_buf)):
            node_buf[i].remove_component_if_not_connected(comp)

        self.component.remove(comp)
        del comp
        return True

    def remove_component_by_label(self, label: str) -> bool:
        comp = self.find_by_label(label)
        if comp is None:
            return False

        return self.remove_component(comp)

    def unfold(self) -> Tuple[List[Node], List[Component.ElementBase]]:
        node: List[Node] = self.node.copy()
        element: List[Component.ElementBase] = []

        for comp in self.component:
            if issubclass(type(comp), Component.PackageBase):
                comp: Component.PackageBase
                _node, _element = comp.circuit.unfold()

                node += _node
                element += _element
            else:
                comp: Component.ElementBase
                element.append(comp)

        node = [n.get_highest_level_node() for n in node]
        node = list(set(node))

        return node, element


class Node:
    def __init__(self, parent: Circuit, init_comp: Component.ComponentBase):
        self.label = ''
        self.parent = parent
        self.component: List[Component.ComponentBase] = [init_comp]

        self.prev_voltage = CalcGraph.Number(np.NaN)

        parent.add_node(self)

    def set_label(self, new_label: str):
        if self.parent.find_by_label(new_label) is not None:
            return False

        self.label = new_label
        return True

    def connect(self, n: Node):
        n.component += self.component
        n.component = list(set(n.component))

        for comp in self.component:
            for pin_idx in range(len(comp.pin)):
                if comp.pin[pin_idx] is self:
                    comp.pin[pin_idx] = n

        self.parent.remove_node(self)
        del self

    def merge_with(self, n: Node):
        self.connect(n)

    def remove_component_if_not_connected(self, comp: Component.ComponentBase) -> bool:
        for p in comp.pin:
            if p is self:
                # Still connected with component
                return False

        self.component.remove(comp)
        if len(self.component) == 0:
            del self

        return True

    def update_component_list(self):
        for comp in self.component:
            self.remove_component_if_not_connected(comp)

    def get_highest_level_node(self) -> Node:
        parent_circuit = self.parent
        parent_component = parent_circuit.parent

        if parent_component is None:  # This node belongs highest level circuit
            return self

        try:
            pin_idx = parent_component.inner_pin.index(self)

            # Connected with high level circuit through pin
            return parent_component.pin[pin_idx].get_highest_level_node()
        except ValueError:  # Not connected with higher level circuit with pin
            return self

    def get_prev_voltage(self):
        return self.get_highest_level_node().prev_voltage
