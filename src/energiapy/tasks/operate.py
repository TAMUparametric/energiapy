@dataclass
class Produce(Trade):
    """Produce Resource via Process"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Store(Trade):
    """Charge Resource via Storage"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Transport(Trade):
    """Transport Resource via Transit"""

    def __post_init__(self):
        Trade.__post_init__(self)
