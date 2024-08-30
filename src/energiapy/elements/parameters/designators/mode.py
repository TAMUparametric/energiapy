"""Operational Mode
"""

from dataclasses import dataclass, field


from sympy import Symbol

from ....core._handy._dunders import _Dunders

from ....core.aliases.iscmp import IsOperational


@dataclass
class X(_Dunders):
    """Mode of Operation, can be used for Conversion, Use, etc.

    Attributes:
        name (Union[str, float, int]): The name of the mode, usually a number.
    """

    name: str | float | int = field(default=None)

    def __post_init__(self):
        self.name = str(f'x_{self.name}')
        # Dummy initial name
        setattr(self, 'sym', Symbol(f'{self.name}'))

    def personalize(self, opn: IsOperational, attr: str):
        """Personalizes the operational mode
        adds the name of the operation
        and first three letters of the attribute
        """
        x = Symbol(f'{self.name}^{attr[0]}{attr[-1]}_{opn.name}')
        setattr(self, 'sym', x)
        self.name = str(x)
        return self

    @property
    def sym(self):
        """Symbol"""
        return self._sym

    @sym.setter
    def sym(self, new_sym):
        self._sym = new_sym
