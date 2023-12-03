from __future__ import annotations
from typing import Callable
from numbers import Real as RealNumber
from overrides import overrides


def add(left: RealNumber, right: RealNumber) -> RealNumber:
    return left + right


def sub(left: RealNumber, right: RealNumber) -> RealNumber:
    return left - right


def mul(left: RealNumber, right: RealNumber) -> RealNumber:
    return left * right


def div(left: RealNumber, right: RealNumber) -> RealNumber:
    return left / right


class Node:
    def __init__(self,
                 left: Node = None, right: Node = None,
                 op: Callable[[RealNumber, RealNumber], RealNumber] = None):
        self.left = left
        self.right = right
        self.op = op

    def __neg__(self):
        return Node(Number(0), self, sub)

    # @overload
    # def __add__(self, other: RealNumber) -> Node:
    #    return Node(self, Number(other), add)

    def __add__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(self, Number(other), add)

        return Node(self, other, add)

    def __radd__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(Number(other), self, add)

        return Node(other, self, add)

    def __sub__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(self, Number(other), sub)

        return Node(self, other, sub)

    def __rsub__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(Number(other), self, sub)

        return Node(other, self, sub)

    def __mul__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(self, Number(other), mul)

        return Node(self, other, mul)

    def __rmul__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(Number(other), self, mul)

        return Node(other, self, mul)

    def __truediv__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(self, Number(other), div)

        return Node(self, other, div)

    def __rtruediv__(self, other: RealNumber | Node) -> Node:
        if issubclass(type(other), RealNumber):
            return Node(Number(other), self, div)

        return Node(other, self, div)

    def __get__(self, instance, owner) -> RealNumber:
        return self.eval()

    def __repr__(self) -> str:
        return str(self.eval())

    def eval(self) -> RealNumber:
        return self.op(self.left.eval(), self.right.eval())


class Number(Node):
    def __init__(self, value: RealNumber | Number):
        super().__init__()
        self.value = value if issubclass(type(value), RealNumber) else value.value

    def __set__(self, instance, value) -> None:
        self.value = value

    def __get__(self, instance, owner) -> RealNumber:
        return self.value

    @overrides
    def eval(self) -> RealNumber:
        return self.value
