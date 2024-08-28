from enum import Enum, auto


class ResourceType(Enum):
    """Class of resource"""

    DISCHARGE = auto()
    """can be dispensed
    """
    CONSUME = auto()
    """can be consumed
    """
    SELL = auto()
    """has a selling price
    """
    PURCHASE = auto()
    """has for a purchase cost (price)
    """
    IMPLICIT = auto()
    """Does not enter or leave the system
    """
    PRODUCE = auto()
    """Produced, updated at the Process level
    """
    STORE = auto()
    """stored in inventory, updated at the Storage level
    """
    SILO = auto()
    """has to pass through a silo, updated at the Storage level
    """
    TRANSPORT = auto()
    """can be transported
    """
