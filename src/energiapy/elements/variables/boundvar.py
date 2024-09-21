"""General Bounded Variable Class
"""

from dataclasses import dataclass

from ._variable import _Variable


@dataclass
class BoundVar(_Variable):
    """BoundVar is a general variable for how much is Bound
    This is a parent class

    Attributes:
        index (Idx): Idx of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
        p (bool): Does it add to the Balance (plus sign)
        m (bool): Does it subtract from the Balance (minus sign)
    """

    def __post_init__(self):
        _Variable.__post_init__(self)
