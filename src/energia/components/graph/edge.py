"""Edge"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ..._core._name import _Name

if TYPE_CHECKING:
    from ...represent.ations.graph import Graph


@dataclass
class Edge(_Name):
    """
    Edge of a Graph

    :param label: Label of the component, used for plotting. Defaults to None.
    :type label: str, optional
    :param graph: Graph to which the edge belongs. Defaults to None.
    :type graph: Graph, optional
    :ivar name: name. Defaults to ''.
    :vartype name: str

    .. note::
        - name and Graph are set when made a Graph attribute.
    """

    def __post_init__(self):
        self.graph: Optional[Graph] = None
        _Name.__post_init__(self)
