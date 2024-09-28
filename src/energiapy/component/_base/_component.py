"""Base Object for all Components
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from ......gana.src.gana.block.prg import Prg


if TYPE_CHECKING:

    from ...environ.horizon import Horizon
    from ...environ.network import Network
    from ...environ.system import System


class Component:


