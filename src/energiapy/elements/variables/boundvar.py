"""General Bounded Variable Class
"""

from dataclasses import dataclass, field

from ._variable import _Variable


@dataclass
class BoundVar(_Variable):
    """BoundVar is a general variable for how much is Bound
    This is a parent class

    Attributes:
        index (Index): Index of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
        p (bool): Does it add to the Balance (plus sign)
        m (bool): Does it subtract from the Balance (minus sign)
    """

    p: bool = field(default=False)
    m: bool = field(default=False)

    def __post_init__(self):
        _Variable.__post_init__(self)

        if not self.p and not self.m:
            raise ValueError(f'{self}: p or m must be True')

        if self.p and self.m:
            raise ValueError(f'{self}: p and m cannot be both True')
