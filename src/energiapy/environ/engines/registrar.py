"""Keeps a track of what elements are defined at what dispostions  
"""

from dataclasses import dataclass, field

from ...core._handy._dunders import _Dunders
from ...core.isalias.elms.iselm import IsElm
from ...core.nirop.errors import CacodcarError
from ...elements.disposition.index import Index
from .rulebook import Bhaskara


@dataclass
class ChitraGupta(_Dunders):
    """Keeps a track of what elements are defined at what indices

    Attributes:
        name (str): name, takes from the name of the Scenario
        rulebook: Bhaskara = field(default_factory=rulebook)

    """

    name: str = field(default=None)
    rulebook: Bhaskara = field(default=None)

    def __post_init__(self):

        self.name = f'Registrar|{self.name}|'

        for var in self.rulebook.vars():
            setattr(self, var.cname(), [])

        for prm in self.rulebook.prms():
            setattr(self, prm.cname(), [])

    def register(self, elm: IsElm, index: Index):
        """Register that a Variable or Parameter has been declared at a particular Index

        Args:
            elm (IsElm): Element to update
            index (Index): with this Index
        """

        # Only unique instances of indices are allowed
        if index in getattr(self, elm.cname()):
            raise CacodcarError(f'{elm} already has {index} in {self.name}')

        getattr(self, elm.cname()).append(index)
