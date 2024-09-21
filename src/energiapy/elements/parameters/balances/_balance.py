"""Balance for Storage Inventory and Transit Freight 
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ....components.abstract.mode import X
from ....core._handy._dunders import _Reprs


@dataclass
class _Balance(_Reprs, ABC):
    """Inventory Balance for Storage

    Attributes:
        balance (IsInvInput): The inventory balance.
        operation (IsStorage): The operation component.
    """

    @property
    @abstractmethod
    def balance(self):
        """The balance attribute"""

    @property
    @abstractmethod
    def operation(self):
        """The operation attribute"""

    def __post_init__(self):
        # If dictionary is given, there are dependent Resources
        # this is mostly used for material Resources
        # Hydrogen for example, may need power to be stored
        # Trains for goods need for power too
        if isinstance(self.balance, dict):

            # The purpose of the Operation is to do something with operated Resource
            # The basis if set to one unit of this Resource
            # Cost inputs, for example, are scaled as per this operated
            self.operated = list(self.balance)[0]

            # if Modes are given, then personalize the Modes to the Inventory Conversion
            if isinstance(self.balance[self.operated], dict):
                if not all(isinstance(i, X) for i in self.balance[self.operated]):
                    # add a dummy mode if no modes present
                    self.balance[self.operated] = {'x': self.balance[self.operated]}

                # Balances have the charging an discharging conversion balances
                # Take a gander at Conversion if whats happening here is not clear
                # 'r' is a dummy resource which will be replaced with ResourceTrn or ResourceStg
                self.conversion_in = {'r': {}}

                # iterate over modes
                for x in self.balance[self.operated]:
                    self.conversion_in['r'][x] = {
                        **{
                            res: -1 / val
                            for res, val in self.balance[self.operated][x].items()
                        },
                        **{self.operated: -1},
                    }
                # 'x' is a dummy mode, which can be removed here
                if self.conversion_in['r'] == 'x':

                    self.conversion_in['r'] = self.conversion_in['r']['x']

                    del self.conversion_in['r']['x']

                self.conversion_out = {self.operated: {'r': 1}}

            else:
                # This is used when a single efficiency value is given
                efficiency = self.balance[self.operated]
                self.conversion_in = {'r': {self.operated: -1 / efficiency}}
                self.conversion_out = {self.operated: {'r': -1}}

        else:
            # If only a Resource is given, consider 100% efficiency
            self.operated = self.balance
            self.conversion_in = {'r': {self.operated: -1}}
            self.conversion_out = {self.operated: {'r': -1}}

        self.name = f'Bal({self.operated}, {self.operation})'
