"""Planning Horizon of the problem
"""


class Time:
    """Time"""

    def __init__(self):
        self.name = 't'

    def __post_init__(self):
        self.name = f'Horizon|{self.name}|'
        self.scales: list[Scale] = []

    def __setattr__(self, name, scale):

        if isinstance(scale, Scale):
            self.scales.append(scale)

        super().__setattr__(name, scale)
