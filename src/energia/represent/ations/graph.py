"""Graph"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...components.graph.edge import Edge
from ...components.graph.node import Node

if TYPE_CHECKING:
    from ..model import Model


@dataclass
class Graph:
    """Graph representation

    :param model: Model to which the graph belongs.
    :type model: Model

    :ivar name: Name of the graph. Defaults to None.
    :vartype name: str
    :ivar nodes: List of nodes in the graph.
    :vartype nodes: list[Node]
    :ivar edges: List of edges in the graph.
    :vartype edges: list[Edge]

    .. note::
        - name is generated based on Model name
        - nodes and edges are populated as model is defined
    """

    model: Model

    def __post_init__(self):
        self.name = f"Graph({self.model})"
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
