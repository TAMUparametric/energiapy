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

    Attributes:
        model (Model): Model to which the graph belongs.
        name (str): Name of the graph. Defaults to None.
        nodes (list[Node]): List of nodes in the graph.
        edges (list[Edge]): List of edges in the graph.

    Note:
        - name is generated based on Model name
        - nodes and edges are populated as model is defined
    """

    model: Model

    def __post_init__(self):
        self.name = f"Graph({self.model})"
        self.nodes = []
        self.edges = []

    def __setattr__(self, name, value):
        # give a name to the Node or Edge
        # set self as the graph of the Node or Edge
        # add the Node or Edge to the graph

        if isinstance(value, Node):
            value.name = name
            value.graph = self
            self.nodes.append(value)
        elif isinstance(value, Edge):
            value.name = name
            value.graph = self
            self.edges.append(value)

        super().__setattr__(name, value)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
