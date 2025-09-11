"""Inherited _Component class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .x import X

if TYPE_CHECKING:
    from ..components.measure.unit import Unit
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.period import Period
    from ..dimensions.decisiontree import DecisionTree
    from ..dimensions.space import Space
    from ..dimensions.time import Time
    from ..modeling.variables.aspect import Aspect


@dataclass
class Component(X):
    """A component with a mathematical program (hence index in it) and
    input parameters (modeling aspects).

    Attributes:
        basis (Unit): Unit basis of the component. Defaults to None.
        label (str): Label of the component, used for plotting. Defaults to None.
    """

    # every component has a basis unit
    basis: Unit = None

    def __post_init__(self):
        """
        Args:
            model (Model): The model to which the component belongs. Defaults to None.
            name (str): Set when the component is made a Model attribute. Defaults to ''.
            _indexed (I): The index set, set the first time it is made. For easy call. Defaults to None.
            constraints (list[str]): List of constraints associated with the object. Defaults to [].
            domains (list[Domain]): List of domains associated with the object. Defaults to [].

        Note:
            name and model are set when the component is made a Model attribute.
            _indexed is made the first time the model is indexed.
            constraints and domains are populated as the program is built.

        """
        # what differentiates a component from an index is that it has aspects
        # that we can control to adjust their states of existence
        X.__post_init__(self)

    @property
    def tree(self) -> DecisionTree:
        """Feasible Region"""
        # the decision tree gives the component access to
        # the aspects of all other components
        return self.model.tree

    @property
    def network(self) -> Location:
        """Circumscribing Loc (Spatial Scale)"""
        return self.model.network

    @property
    def horizon(self) -> Period:
        """Circumscribing Period (Temporal Scale)"""
        return self.model.horizon

    @property
    def time(self) -> Time:
        """Time"""
        return self.model.time

    @property
    def space(self) -> Space:
        """Space"""
        return self.model.space

    def get(self, aspect: str) -> Aspect:
        """Gets the the aspect from the model

        Args:
            aspect (str): Variable name

        Returns:
            Aspect: Can be a State, Control response, Stream, Impact
        """
        # There is only one instance of any aspect in the model
        # so that aspect is called and index at the bare minimum
        # of the component that is calling it
        return getattr(self.model, aspect)(self)
