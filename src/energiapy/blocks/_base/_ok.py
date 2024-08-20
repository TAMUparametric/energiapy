"""This allows certain behaviors when modeling the Scenario
"""

from abc import ABC, abstractmethod
from warnings import warn
from dataclasses import dataclass, field


@dataclass
class _Ok(ABC):
    """Allows certain behaviors when modeling the Scenario

    Attributes:
        ok_overwrite (bool): Allow overwriting of Components. Default is True
        ok_nobasis (bool): Allow Components without basis. Default is True
        ok_nolabel (bool): Allow Components without label. Default is True
        be_strict (bool): Be strict with the above. Default is False
    """

    ok_overwrite: bool = field(default=True)
    ok_nobasis: bool = field(default=True)
    ok_nolabel: bool = field(default=True)
    be_strict: bool = field(default=False)

    def __post_init__(self):
        if self.be_strict:
            self.ok_overwrite = False
            self.ok_nobasis = False
            self.ok_nolabel = False

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
                raise AttributeError(
                    f'{cmp} already exists\nset Scenario.ok_overwrite=True if intentional'
                )
            else:
                warn(
                    f'{cmp} already exists, overwriting\nset Scenario.ok_overwrite=False, to enforce strictly'
                )

    def isok_nobasis(self, component: str):
        """Check if component without basis is allowed

        component (str): Component to be checked

        """
        if not self.ok_nobasis and not component.basis:
            raise AttributeError(
                f'{component} cannot be created without basis\nSet ok_nobasis=True if intentional'
            )

    def isok_nolabel(self, component: str):
        """Check if component without label is allowed

        Args:
            component (str): Component to be checked
        """

        if not self.ok_nolabel and not component.label:
            raise AttributeError(
                f'{component} cannot be created without label\nSet ok_nolabel=True if intentional'
            )
