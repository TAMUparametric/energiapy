"""General Bounded Bound Variable Class
"""

from dataclasses import dataclass, field

from .boundvar import BoundVar


@dataclass
class BoundBoundVar(BoundVar):
    """BoundBoundVar is a general variable which is essentially a Bound Variable
    Bounded by another Bound Variable

    These are a mainstay in multiscale modeling and optimization

    Attributes:
        index (Index): Index of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
        p (bool): Does it add to the Balance (plus sign)
        m (bool): Does it subtract from the Balance (minus sign)
        parent (BoundVar): The Parent Variable of the Variable
    """

    parent: BoundVar = field(default=None)

    def __post_init__(self):
        BoundVar.__post_init__(self)
