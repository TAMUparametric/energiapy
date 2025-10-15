"""Edge"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._name import _Name

if TYPE_CHECKING:
    from ...represent._ations.graph import Graph


@dataclass
class Edge(_Name):
    """Edge of a Graph

    Attributes:
        label (str): Label of the component, used for plotting. Defaults to None.
        graph (Graph): Graph to which the edge belongs. Defaults to None.
        name (str): name. Defaults to ''.

    Note:
        - name and Graph are set when made a Graph attribute.
    """

    def __post_init__(self):
        self.graph: Graph = None
        _Name.__post_init__(self)
