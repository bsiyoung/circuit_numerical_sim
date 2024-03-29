from __future__ import annotations
from typing import List
from numbers import Real as RealNumber

import numpy as np
from overrides import overrides

import Circuit
import CalcGraph


"""
ComponentBase
 ├─ IdealGround
 ├─ ElementBase
 │   ├─ IdealVoltageSource
 │   ├─ IdealCurrentSource
 │   ├─ IdealResistor
 │   ├─ IdealCapacitor
 │   └─ IdealInductor
 └─ PackageBase
     ├─ Ground
     ├─ VoltageSource
     ├─ CurrentSource
     ├─ Resistor
     ├─ Capacitor
     └─ Inductor
"""


class ComponentBase:
    def __init__(self,
                 parent: Circuit.Circuit,
                 n_pin: int,
                 label: str = ''):
        self.label = label
        self.parent = parent

        if parent.add_component(self) is False:
            raise Exception

        self.pin = [Circuit.Node(parent, self) for i in range(n_pin)]

    def reset_pin(self, pin_idx):
        # Replace to new pin
        orig_node = self.pin[pin_idx]
        self.pin[pin_idx] = Circuit.Node(self.parent, self)

        # Update component list of node
        orig_node.remove_component_if_not_connected(self)

    def reset_all_pin(self):
        for pin_idx in range(len(self.pin)):
            self.reset_pin(pin_idx)


class IdealGround(ComponentBase):
    def __init__(self, parent: Circuit.Circuit, label: str = ''):
        super().__init__(parent=parent, n_pin=1, label=label)


class ElementBase(ComponentBase):
    def __init__(self, parent: Circuit.Circuit, value: CalcGraph.Number, n_pin=2, label: str = ''):
        super().__init__(parent=parent, n_pin=n_pin, label=label)

        self.value: CalcGraph.Number = value
        self.prev_current = CalcGraph.Number(np.NaN)

    def set_value(self, value: RealNumber):
        self.value.value = value

    # noinspection PyMethodMayBeStatic
    def get_voltage_coefficient(self, dt):
        return CalcGraph.Number(0)

    # noinspection PyMethodMayBeStatic
    def get_current_coefficient(self, dt):
        return CalcGraph.Number(0)

    # noinspection PyMethodMayBeStatic
    def get_constant(self, dt):
        return CalcGraph.Number(0)


class IdealVoltageSource(ElementBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 value: RealNumber = 10.0,
                 label: str = ''):
        super().__init__(value=CalcGraph.Number(value), parent=parent, label=label)

    @overrides
    def get_voltage_coefficient(self, dt):
        return CalcGraph.Number(1)

    @overrides
    def get_constant(self, dt):
        return self.value


class IdealCurrentSource(ElementBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 value: RealNumber = 1.0,
                 label: str = ''):
        super().__init__(value=CalcGraph.Number(value), parent=parent, label=label)

    @overrides
    def get_current_coefficient(self, dt):
        return CalcGraph.Number(1)

    @overrides
    def get_constant(self, dt):
        return self.value


class IdealResistor(ElementBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 value: RealNumber = 100,
                 label: str = ''):
        super().__init__(value=CalcGraph.Number(value), parent=parent, label=label)

    @overrides
    def get_voltage_coefficient(self, dt):
        return CalcGraph.Number(1)

    @overrides
    def get_current_coefficient(self, dt):
        return -self.value


class IdealCapacitor(ElementBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 value: RealNumber = 1e-6,
                 init_voltage: RealNumber = 0.0,
                 label: str = ''):
        super().__init__(value=CalcGraph.Number(value), parent=parent, label=label)
        self.init_voltage = CalcGraph.Number(init_voltage)

    def set_init_voltage(self, value: RealNumber):
        self.init_voltage.value = value

    @overrides
    def get_voltage_coefficient(self, dt):
        return CalcGraph.Number(1)

    @overrides
    def get_current_coefficient(self, dt):
        return -dt / self.value

    @overrides
    def get_constant(self, dt):
        volt_diff = self.pin[0].prev_voltage - self.pin[1].prev_voltage
        if np.isnan(volt_diff.value):
            return self.init_voltage

        return volt_diff


class IdealInductor(ElementBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 value: RealNumber = 1e-6,
                 init_current: RealNumber = 0.0,
                 label: str = ''):
        super().__init__(value=CalcGraph.Number(value), parent=parent, label=label)
        self.init_current = CalcGraph.Number(init_current)

    def set_init_current(self, value: RealNumber):
        self.init_current.value = value

    @overrides
    def get_voltage_coefficient(self, dt):
        return dt / self.value

    @overrides
    def get_current_coefficient(self, dt):
        return CalcGraph.Number(-1)

    @overrides
    def get_constant(self, dt):
        return -self.prev_current


class PackageBase(ComponentBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 n_pin: int,
                 label: str = ''):
        super().__init__(parent=parent, n_pin=n_pin, label=label)
        self.parent = parent
        self.inner_pin: List[None | Circuit.Node] = [None for i in range(n_pin)]
        self.circuit = Circuit.Circuit(parent=self)

    def __getitem__(self, label: str) -> None | Circuit.Node | ElementBase | PackageBase:
        return self.circuit[label]

    def update(self) -> None:
        return


class Ground(PackageBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 r: RealNumber = 1e+9,
                 label: str = ''):
        super().__init__(parent=parent, n_pin=1, label=label)

        r = IdealResistor(self.circuit, r, 'R')
        gnd = IdealGround(self.circuit, 'GND')

        r.pin[1].connect(gnd.pin[0])

        self.inner_pin[0] = r.pin[0]


class VoltageSource(PackageBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 v_th: RealNumber = 10.0,
                 r_th: RealNumber = 1.0,
                 label: str = ''):
        super().__init__(parent=parent, n_pin=2, label=label)

        v = IdealVoltageSource(self.circuit, v_th, 'V_th')
        r = IdealResistor(self.circuit, r_th, 'R_th')

        v.pin[1].connect(r.pin[0])

        self.inner_pin[0] = v.pin[0]
        self.inner_pin[1] = r.pin[1]


class Resistor(PackageBase):
    def __init__(self,
                 parent: Circuit.Circuit,
                 r: RealNumber = 100.0,
                 label: str = ''):
        super().__init__(parent=parent, n_pin=2, label=label)

        r = IdealResistor(self.circuit, r, 'R')

        self.inner_pin[0] = r.pin[0]
        self.inner_pin[1] = r.pin[1]
