from dataclasses import dataclass, field


@dataclass
class Matrix:
    """Matrix representation of the Model
    """
    name: str = field(default=None)
