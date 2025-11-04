"""Inherited _Component class"""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from gana import I

from ._x import _X

if TYPE_CHECKING:
    from ..components.spatial.location import Location
    from ..components.temporal.periods import Periods
    from ..dimensions.problem import Problem
    from ..dimensions.space import Space
    from ..dimensions.time import Time
    from ..modeling.indices.sample import Sample
    from ..represent.model import Model


class _Component(_X):
    """
    A component with a mathematical program (hence index in it) and
    input parameters (modeling aspects).

    :param label: Label for the component. Defaults to None.
    :type label: str, optional
    :param citations: Citation for the component. Defaults to None.
    :type citations: str | list[str] | dict[str, str | list[str]], optional

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str
    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]

    :raises AttributeError: If an invalid parameter is provided for the component type.

    .. note:
        - `name`, `model` set when component assigned to Model attribute.
        - `constraints` and `domains` are populated as the program is built.
    """

    def __init__(
        self,
        label: str = "",
        citations: str = "",
        **kwargs,
    ):
        self.parameters = kwargs

        # what differentiates a component from an index is that it has aspects
        # that we can control to adjust their states of existence
        _X.__init__(self, label=label, citations=citations)

    @property
    def network(self) -> Location:
        """Circumscribing Loc (Spatial Scale)"""
        return self.model.network

    @property
    def horizon(self) -> Periods:
        """Circumscribing Periods (Temporal Scale)"""
        return self.model.horizon

    @cached_property
    def time(self) -> Time:
        """Time"""
        return self.model.time

    @cached_property
    def space(self) -> Space:
        """Space"""
        return self.model.space

    @cached_property
    def problem(self) -> Problem:
        """Feasible Region"""
        # the decision tree gives the component access to
        # the aspects of all other components
        return self.model.problem

    def _handle_norm(self, aspect: str, sample: Sample) -> Sample:
        """Check if a nominal parameter is set for the aspect"""
        # check if a request to normalize has been made
        nominal = aspect + "_nominal"
        nom = aspect + "_nom"
        normalize = aspect + "_normalize"
        norm = aspect + "_norm"

        if normalize in self.parameters or norm in self.parameters:
            _normalize = self.parameters.get(normalize, self.parameters.get(norm))
        else:
            # default behavior is to normalize
            _normalize = False

        # irrespective of normalize request, check if nominal value set
        if nominal in self.parameters or nom in self.parameters:
            # if nominal is given, normalize to it
            return sample.prep(self.parameters[nominal], True)

        if _normalize:
            # if _normalize is True but no nominal provided
            return sample.prep(norm=True)

        return sample

    def _handle_x(self, aspect: str, sample: Sample) -> Sample:
        """Check if aspect is optional"""

        if (
            aspect + '_optional' in self.parameters
            and self.parameters[aspect + '_optional']
        ):
            return sample.x
        if (
            aspect + '_report' in self.parameters
            and self.parameters[aspect + '_report']
        ):
            return sample.x

        return sample

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        # this handles the parameters being set on init
        if name == "model" and value is not None:

            model: Model = value

            for attr, param in self.parameters.items():

                if attr in model.manual:
                    _ = getattr(self, attr) == param
                    continue

                # attributes name expected here are of the format <aspect>_<bound>
                # for exact equality, just <aspect>

                split_attr = attr.split('_')
                # irrespective of exact or bound, first part is always the aspect
                aspect = split_attr[0]

                if isinstance(self, getattr(self.model, aspect).primary_type):
                    # check type match

                    # get the sample
                    sample = getattr(self, aspect)

                    if isinstance(param, list):
                        sample = self._handle_x(
                            aspect, self._handle_norm(aspect, sample)
                        )

                    else:
                        sample = self._handle_x(aspect, sample)

                    if len(split_attr) == 1:
                        # if split returned just the aspect name
                        # then it's an equality
                        _ = sample == param

                    # else, check if lower or upper bound

                    elif split_attr[1] in ["max", "ub", "UB", "leq"]:

                        _ = sample <= param

                    elif split_attr[1] in ["min", "lb", "LB", "geq"]:
                        _ = sample >= param

                else:
                    # error if type mismatch
                    raise AttributeError(
                        f"Parameter {attr} valid for {self.model.cookbook[aspect].primary_type} not {type(self).__name__}"
                    )

    def __getattr__(self, name):

        if self.model:
            # no need to run a hasattr check
            # let it raise an attribute error if not found
            aspect = getattr(self.model, name)
            if callable(aspect):
                return aspect(self)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'",
        )

    @cached_property
    def I(self):
        """gana index set (I)"""
        _index = I(self.name, tag=self.label or "")
        setattr(self.program, self.name, _index)
        return _index

    def __len__(self):
        """Length of the component's index set"""
        # always one
        return 1
