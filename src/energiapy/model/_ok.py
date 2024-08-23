"""This allows certain behaviors when modeling the Scenario
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from warnings import warn

from ..core.nirop.errors import NoBasisError, NoLabelError, OverWriteError
from ..core.nirop.warnings import OverWriteWarning


@dataclass
class _Ok(ABC):
    """Allows certain behaviors when modeling the Scenario

    Attributes:
        ok_overwrite (bool): Allow overwriting of Components. Default is True
        ok_nobasis (bool): Allow Components without basis. Default is True
        ok_nolabel (bool): Allow Components without label. Default is True
        ok_inconsistent (bool): Fix incosistent Dispositions, with warnings. Default is True
        chill (bool): If False, disallow all the above. Default is True
    """

    ok_overwrite: bool = field(default=True)
    ok_nobasis: bool = field(default=True)
    ok_nolabel: bool = field(default=True)
    ok_inconsistent: bool = field(default=True)
    chill: bool = field(default=True)

    def __post_init__(self):
        if not self.chill:
            # if not chill, then enforce stricitly
            self.ok_overwrite = False
            self.ok_nobasis = False
            self.ok_nolabel = False
            self.ok_inconsistent = False

    @property
    @abstractmethod
    def system(self):
        """System of the Scenario"""

    def isok_ovewrite(self, cmp: str):
        """Check if overwriting is allowed

        Args:
            cmp (str): Component to be overwritten

        """
        if hasattr(self.system, cmp):
            if not self.ok_overwrite:
                raise OverWriteError(cmp)
            else:
                warn(OverWriteWarning(cmp))

    def isok_nobasis(self, component: str):
        """Check if component without basis is allowed

        component (str): Component to be checked

        """
        if not self.ok_nobasis and not component.basis:
            raise NoBasisError(component)

    def isok_nolabel(self, component: str):
        """Check if component without label is allowed

        Args:
            component (str): Component to be checked
        """

        if not self.ok_nolabel and not component.label:
            raise NoLabelError(component)
