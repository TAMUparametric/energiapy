"""Variable"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Self, Type

import matplotlib.pyplot as plt
from matplotlib import rc

from ...components.commodities.commodity import Commodity
from ...components.game.couple import Interact
from ...components.game.player import Player
from ...components.impact.indicator import Indicator
from ...components.operations.process import Process
from ...components.operations.storage import Storage
from ...components.operations.transport import Transport
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.lag import Lag
from ...components.temporal.modes import Modes
from ...components.temporal.periods import Periods
from ...dimensions.space import Space
from ...dimensions.time import Time
from ..indices.domain import Domain
from .sample import Sample

if TYPE_CHECKING:
    from gana import I as Idx
    from gana import Prg
    from gana import V as Var
    from gana.sets.constraint import C

    from ..._core._component import _Component
    from ..._core._x import _X
    from ...dimensions.problem import Problem
    from ...represent.model import Model


@dataclass
class Aspect:
    r"""
    A particular facet of the system under consideration. A sample of an aspect at a
    specific disposition is represented by a variable (:math:`\overset{\*}{v} \in \overset{\*}{\mathcal{V}}`).
    The range of values which the :math:`\overset{\*}{v}` is bounded such that:

    .. math::

        \overset{\*}{v} \in [\underline{\theta}, \overline{\theta}]

    Aspects can be decision-variables (:math:`\dot{v}`) that prescribe a control action
    or a set point for the state, or derived (calculated) variables (:math:`\hat{v}`) that
    represent the state of the system. States can be operation capacity, production levels,
    purchase levels, emissions, consumption levels, etc.


    :param primary_types: associated components type(s). Defaults to None.
    :type primary_types: Type[_Component] | tuple[Type[_Component], ...]
    :param nn: If True, the decision is a non-negative decision. Defaults to True.
    :type nn: bool
    :param ispos: If True, the decision is positive (non-negative). Defaults to True.
    :type ispos: bool
    :param neg: Negative form or representation of the decision, if any. Defaults to "".
    :type neg: str
    :param latex: LaTeX string. Defaults to "".
    :type latex: str
    :param bound: if the aspect is bounded by another. Defaults to "".
    :type bound: str
    :param label: Label for the decision. Defaults to "".
    :type label: str

    :ivar model: Model to which the Aspect belongs.
    :vartype model: Model
    :ivar name: Name of the Aspect.
    :vartype name: str
    :ivar indices: List of indices (Location, Periods) associated with the Aspect.
    :vartype indices: list[Location | Linkage, Periods]
    :ivar bound_spaces: Spaces where the Aspect has been already bound.
    :vartype bound_spaces: dict[Commodity | Process | Storage | Transport, list[Location | Linkage]]
    :ivar domains: List of domains associated with the Aspect.
    :vartype domains: list[Domain]

    :raises ValueError: If `primary_type` is not defined.
    """

    primary_type: Type[_Component] | tuple[Type[_Component], ...]
    nn: bool = True
    ispos: bool = True
    neg: str = ""
    latex: str = ""
    bound: str = ""
    label: str = ""

    def __post_init__(self):
        # will be set when added to model
        self.name: str = ""

        # name of the decision
        self.model: Model | None = None

        if self.label:
            if self.nn:
                self.label += " [+]"
            else:
                self.label += " [-]"
        self.indices: list[Location | Linkage | Periods] = []

        # # if a decision is bounded by another decision
        # self.bound: Self = None

        # spaces where the aspect has been already bound
        self.bound_spaces: dict[
            Commodity | Process | Storage | Transport,
            list[Location | Linkage],
        ] = {}

        # upper/lower/exact bounds are set on these locations/periods

        self.ubs: dict[Location | Linkage, Periods] = {}
        self.lbs: dict[Location | Linkage, Periods] = {}
        self.eqs: dict[Location | Linkage, Periods] = {}

        # Domains of the decision
        self.domains: list[Domain] = []

        # a dictionary of domains and their maps from higher order domains
        # reporting variable
        self.reporting: Var | None = None

        self.constraints: list[str] = []

        # this keeps track of whether GRB has already been added
        self.balances: dict[tuple[Idx, ...], bool] = {}

    @cached_property
    def maps(self) -> dict[Aspect, dict[str, list[Domain]]]:
        """Maps of the decision"""
        self.model.maps[self] = {"time": {}, "space": {}, "modes": {}, "samples": {}}
        return self.model.maps[self]

    @cached_property
    def maps_report(self) -> dict[Aspect, dict[str, list[Domain]]]:
        """Maps of the decision"""
        self.model.maps_report[self] = {
            "time": {},
            "space": {},
            "modes": {},
            "samples": {},
        }
        return self.model.maps_report[self]

    # @cached_property
    # def maps(self) -> dict[Aspect, dict[str, list[Domain]]]:
    #     """Maps of the decision"""
    #     self.model.maps[self] = {}
    #     return self.model.maps[self]

    # @cached_property
    # def maps_report(self) -> dict[Aspect, dict[str, list[Domain]]]:
    #     """Maps of the decision"""
    #     self.model.maps_report[self] = {s}
    #     return self.model.maps_report[self]

    @cached_property
    def isneg(self) -> bool:
        """Does this remove from the domain?"""
        return not self.ispos

    @cached_property
    def sign(self) -> float:
        """Gives the multiplier in balances"""
        if self.ispos:
            return 1.0
        else:
            return -1.0

    @cached_property
    def space(self) -> Space:
        """Space"""
        return self.model.space

    @cached_property
    def program(self) -> Prg:
        """Mathematical Program"""
        return self.model.program

    @cached_property
    def problem(self) -> Problem:
        """Tree"""
        return self.model.problem

    @cached_property
    def time(self) -> Time:
        """Time"""
        return self.model.time

    @property
    def I(self) -> Idx:
        """gana index set (I)"""
        return getattr(self.program, self.name)

    @property
    def V(self) -> Var:
        """Variable"""
        return getattr(self.program, self.name)

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        return [getattr(self.program, c) for c in self.constraints]

    @property
    def network(self) -> Location:
        """Circumscribing Location (Spatial Scale)"""
        return self.model.network

    @property
    def horizon(self) -> Periods:
        """Circumscribing Periods (Temporal Scale)"""
        return self.model.horizon

    @property
    def dispositions(self) -> dict[
        Self,
        dict[
            Commodity | Process | Storage | Transport,
            dict[
                Periods | Location | Linkage,
                dict[Location | Periods | Linkage, bool],
            ],
        ],
    ]:
        """Dispositions dict"""
        return self.model.dispositions[self]

    def alias(self, *names: str):
        """
        Create aliases for the decision

        :param names: Names of the aliases
        :type names: str
        """
        self.model.alias(*names, of=self.name)

    def update(self, domain: Domain, reporting: bool = False):
        """Each inherited object has their own"""

    def show(self, descriptive=False):
        """Pretty print the component"""
        for c in self.cons:
            c.show(descriptive)

    def output(
        self,
        n_sol: int = 0,
        aslist: bool = False,
        asdict: bool = False,
        compare: bool = False,
    ) -> list[float] | dict[tuple[Idx, ...], float] | None:
        """
        Solution

        :param n_sol: Solution number. Defaults to 0.
        :type n_sol: int, optional
        :param compare: Compares the solution with the previous one. Defaults to False.
        :type compare: bool, optional
        :param asdict (bool, optional): Returns values taken as dict. Defaults to False.
        :type asdict: bool, optional
        :param aslist (bool, optional): Returns values taken as list. Defaults to False.
        :type aslist: bool, optional

        :return: List of values taken by the decision.
        :rtype: list[float] | None
        """
        var: Var = getattr(self.program, self.name)
        return var.output(n_sol, aslist=aslist, asdict=asdict, compare=compare)

    def gettime(self, *index) -> list[Periods]:
        """Finds the sparsest time scale in the domains"""
        ds = [i for i in self.indices if all([x in i for x in index])]
        t = [t for t in ds if isinstance(t, Periods)]
        return t

    def draw(
        self,
        x: _X,
        y: tuple[_X] | _X,
        z: tuple[_X] | _X = None,
        font_size: float = 16,
        fig_size: tuple[float, float] = (12, 6),
        linewidth: float = 0.7,
        color: str = "blue",
        grid_alpha: float = 0.3,
        usetex: bool = True,
    ):
        """Plot the decision"""
        if not isinstance(y, tuple):
            y = (y,)
        if not z:
            index = [i.I for i in y + (x,)]
        elif not isinstance(z, tuple):
            z = (z,)

        if usetex:
            rc(
                "font",
                **{"family": "serif", "serif": ["Computer Modern"], "size": font_size},
            )
            rc("text", usetex=usetex)
        else:
            rc("font", **{"size": font_size})

        fig, ax = plt.subplots(figsize=fig_size)

        if not z:
            ax.plot(
                [i.name for i in x.I._],
                self.V(*index).output(True),
                linewidth=linewidth,
                color=color,
            )
        else:
            for z_ in z:
                index = [i.I for i in (z_,) + y + (x,)]
                ax.plot(
                    [i.name for i in x.I._],
                    self.V(*index).output(True),
                    linewidth=linewidth,
                    label=z_.label if z_.label else z_.name,
                )

        label_ = [i.label if i.label else i.name for i in y]
        label_ = str(label_).replace("[", "").replace("]", "").replace("'", "")
        plt.title(f"{self.label} - {label_}")
        plt.ylabel("Values")
        plt.xlabel(f"{x.label or x.name}")
        plt.grid(alpha=grid_alpha)
        if z:
            plt.legend()
        plt.rcdefaults()

    def __neg__(self):
        """Negative Consequence"""

        dscn = type(self)(
            nn=False,
            primary_type=self.primary_type,
        )
        dscn.neg, self.neg = self, dscn
        dscn.ispos = not self.ispos
        return dscn

    def __len__(self):
        return len(self.domains)

    def __eq__(self, other: Self) -> bool:
        if isinstance(other, Aspect):
            return self.name == other.name

    def __call__(self, *index: _X, domain: Domain | None = None):

        if not domain:

            args = {
                "indicator": None,
                "commodity": None,
                "player": None,
                "process": None,
                "storage": None,
                "transport": None,
                "periods": None,
                "couple": None,
                "location": None,
                "linkage": None,
                "lag": None,
                "modes": None,
            }

            type_map = {
                Periods: ("periods", "timed", False),
                Lag: ("lag", "timed", False),
                Location: ("location", "spaced", False),
                Linkage: ("linkage", "spaced", False),
                Process: ("process", None, True),
                Storage: ("storage", None, True),
                Transport: ("transport", None, True),
                Player: ("player", None, False),
                Interact: ("couple", None, False),
                Indicator: ("indicator", None, False),
                Modes: ("modes", None, False),
                Commodity: ("commodity", None, True),
            }

            samples: list[Sample] = []
            timed, spaced = False, False

            for comp in index:
                if isinstance(comp, Sample):
                    samples.append(comp)
                    for b in samples:
                        if b.domain.samples:
                            samples.extend(b.domain.samples)
                    samples = list(set(samples))
                    continue

                for typ, (attr, flag, require_primary) in type_map.items():
                    if isinstance(comp, typ):
                        if require_primary and (
                            not self.primary_type
                            or not isinstance(comp, self.primary_type)
                        ):
                            raise ValueError(
                                f"For component {self} of type {type(self)}: "
                                f"{comp} of type {type(comp)} not recognized as an index",
                            )
                        args[attr] = comp
                        if flag == "timed":
                            timed = True
                        elif flag == "spaced":
                            spaced = True
                        break
                else:
                    raise ValueError(
                        f"For component {self} of type {type(self)}: "
                        f"{comp} of type {type(comp)} not recognized as an index",
                    )

            args = {k: v for k, v in args.items() if v is not None}

            if samples:
                args["samples"] = samples

            domain = Domain(**args)

        else:
            timed = spaced = True

        return Sample(aspect=self, domain=domain, timed=timed, spaced=spaced)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __init_subclass__(cls):
        cls.__repr__ = Aspect.__repr__
        cls.__hash__ = Aspect.__hash__

    def __iter__(self):
        """Iterate over domains"""
        for d in self.domains:
            yield self(domain=d)
