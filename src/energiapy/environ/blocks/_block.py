"""Base Class for all Modeling Blocks in energiapy"""

from dataclasses import asdict, dataclass, field

from ...core._handy._dunders import _Dunders


@dataclass
class _Block(_Dunders):
    """Base Class for all Modeling Blocks in energiapy

    Attributes:
        name (str): name of the Block
    """

    name: str = field(default=None)

    def __post_init__(self):
        # This is the initial state of the Block
        # Usually included just the name and post init arguments
        self._initial_state = asdict(self)
        self.name = f'{self.cname()}|{self.name}|'

    def components(self) -> dict:
        """Returns the names (n) and Components (cmp) that have been added to the block

        Returns:
            dict: {name: Component}
        """
        # This is the current state of the Block
        # Basically a dictionary of all the added attributes (Components)

        current_state = {
            n: cmp
            for n, cmp in self.__dict__.items()
            if not n.startswith('_') and not isinstance(cmp, str)
        }

        # Returns the difference between the current state and the initial state
        return {
            n: cmp
            for n, cmp in current_state.items()
            if n not in self._initial_state or self._initial_state[n] != cmp
        }
