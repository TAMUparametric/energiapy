from dataclasses import dataclass, field


@dataclass
class Program:
    """Mathematical Programming Model
    """
    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Progam|{self.name}|'
        self.variables, self.constraints, self.parameters = (
            [] for _ in range(3))
