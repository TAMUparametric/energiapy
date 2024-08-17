"""Base Class for all Modeling Blocks in energiapy"""

from dataclasses import dataclass, asdict

from ..._core._handy._dunders import _Dunders


@dataclass
class _Block(_Dunders):
    """Base Class for all Modeling Blocks in energiapy"""

    def __post_init__(self):
        self._initial_state = asdict(self)

    def components(self):
        """Returns the names Components that have been added to the block"""

        current_state = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith('_') and not isinstance(v, str)
        }

        return {
            k: v
            for k, v in current_state.items()
            if k not in self._initial_state or self._initial_state[k] != v
        }
