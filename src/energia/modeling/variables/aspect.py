"""Variable"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Self, Type, Optional

import matplotlib.pyplot as plt
from matplotlib import rc

from ...components.commodity._commodity import _Commodity
from ...components.game.couple import Couple
from ...components.game.player import Player
from ...components.impact.indicator import Indicator
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transport import Transport
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.lag import Lag
from ...components.temporal.modes import Modes
from ...components.temporal.periods import Periods
from ...dimensions.space import Space
from ...dimensions.time import Time
from ..constraints.bind import Bind
from ..indices.domain import Domain

if TYPE_CHECKING:
    from gana import I as Idx
    from gana import Prg
    from gana import V as Var
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ..._core._component import _Component
    from ...dimensions.problem import Problem
    from ...represent.model import Model


@dataclass
class Aspect:
    """
    Any kind of decision.

    :param nn: If True, the decision is a non-negative decision. Defaults to True.
    :type nn: bool
    :param types_opr: The type(s) of operation associated with the decision. Defaults to None.
    :type types_opr: tuple[Type[Process | Storage | Transport]] | None
    :param types_res: The type of commodity associated with the decision. Defaults to None.
    :type types_res: Type[_Commodity] | None
    :param types_dres: The type of derivative commodity associated with the decision. Defaults to None.
    :type types_dres: Type[_Commodity] | None
    :param types_idc: The type of indicator associated with the decision. Defaults to None.
    :type types_idc: Type[Indicator] | None
    :param ispos: If True, the decision is positive (non-negative). Defaults to True.
    :type ispos: bool
    :param neg: Negative form or representation of the decision, if any. Defaults to "".
    :type neg: str
    :param latex: LaTeX string. Defaults to "".
    :type latex: str
    :param bound: if the aspect is bounded by another. Defaults to "".
    :type bound: str

    :ivar model: Model to which the Aspect belongs.
    :vartype model: Model
    :ivar name: Name of the Aspect.
    :vartype name: str
    :ivar indices: List of indices (Location, Periods) associated with the Aspect.
    :vartype indices: list[Location | Linkage, Periods]
    :ivar bound_spaces: Spaces where the Aspect has been already bound.
    :vartype bound_spaces: dict[_Commodity | Process | Storage | Transport, list[Location | Linkage]]
    :ivar domains: List of domains associated with the Aspect.
    :vartype domains: list[Domain]

    raises ValueError:
        - If `primary_type` is not defined.
    """

    primary_type: Type[_Component]
    nn: bool = True
    ispos: bool = True
    neg: str = ""
    latex: str = ""
    bound: str = ""
    label: Optional[str] = None

    def __post_init__(self):
        # will be set when added to model
        self.name: str = ""

        # name of the decision
        self.model: Model = None

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
            _Commodity | Process | Storage | Transport,
            list[Location | Linkage],
        ] = {}

        # Domains of the decision
        self.domains: list[Domain] = []

        # a dictionary of domains and their maps from higher order domains

        self._maps: bool = False

        self._maps_report: bool = False

        # reporting variable
        self.reporting: Optional[Var] = None

        self.constraints: list[str] = []

    @property
    def maps(self) -> dict[Domain, dict[str, list[Domain]]]:
        """Maps of the decision"""
        if not self._maps:
            self.model.maps[self] = {}
            self._maps = True
        return self.model.maps[self]

    @property
    def maps_report(self) -> dict[Domain, dict[str, list[Domain]]]:
        """Maps of the decision"""
        if not self._maps_report:
            self.model.maps_report[self] = {}
            self._maps_report = True
        return self.model.maps_report[self]

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
        """Circumscribing Loc (Spatial Scale)"""
        return self.model.network

    @property
    def horizon(self) -> Periods:
        """Circumscribing Periods (Temporal Scale)"""
        return self.model.horizon

    @property
    def grb(
        self,
    ) -> dict[_Commodity, dict[Location | Linkage, dict[Periods, list[Aspect]]]]:
        """General _Commodity Balance dict"""
        return self.model.grb

    @property
    def dispositions(self) -> dict[
        Self,
        dict[
            _Commodity | Process | Storage | Transport,
            dict[
                Periods | Location | Linkage,
                dict[Location | Periods | Linkage, bool],
            ],
        ],
    ]:
        """Dispositions dict"""
        return self.model.dispositions[self]

    def aliases(self, *names: str):
        """Create aliases for the decision

        Args:
            *names (str): Names of the aliases
        """
        self.model.aliases(*names, to=self.name)

    def map_domain(self, domain: Domain):
        """Each inherited object has their own"""
        pass

    def show(self, descriptive=False):
        """Pretty print the component"""
        for c in self.cons:
            c.show(descriptive)

    def sol(
        self,
        n_sol: int = 0,
        aslist: bool = False,
        compare: bool = False,
    ) -> list[float] | None:
        """Solution
        Args:
            aslist (bool, optional): Returns values taken as list. Defaults to False.
        """
        var: Var = getattr(self.program, self.name)
        return var.sol(n_sol, aslist, compare=compare)

    def gettime(self, *index) -> list[Periods]:
        """Finds the sparsest time scale in the domains"""
        ds = [i for i in self.indices if all([x in i for x in index])]
        t = [t for t in ds if isinstance(t, Periods)]
        return t

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

    def __call__(self, *index: _X, domain: Domain = None):
        if not domain:

            (
                indicator,
                commodity,
                player,
                process,
                storage,
                transport,
                period,
                couple,
                loc,
                link,
                lag,
                modes,
            ) = (None for _ in range(12))

            binds: list[Bind] = []
            timed, spaced = False, False

            for comp in index:

                if isinstance(comp, Periods):
                    period = comp
                    timed = True

                elif isinstance(comp, Lag):
                    lag = comp
                    timed = True

                elif isinstance(comp, Location):
                    loc = comp
                    spaced = True

                elif isinstance(comp, Linkage):
                    link = comp
                    spaced = True

                elif isinstance(comp, Process):
                    if self.primary_type and isinstance(comp, self.primary_type):
                        process = comp

                    else:
                        raise ValueError(
                            f"For component {self} of type {type(self)}: {comp} of type {type(comp)} not recognized as an index",
                        )

                elif isinstance(comp, Storage):
                    if self.primary_type and isinstance(comp, self.primary_type):
                        storage = comp

                    else:
                        raise ValueError(
                            f"For component {self} of type {type(self)}: {comp} of type {type(comp)} not recognized as an index",
                        )

                elif isinstance(comp, Transport):
                    if self.primary_type and isinstance(comp, self.primary_type):
                        transport = comp

                    else:
                        raise ValueError(
                            f"For component {self} of type {type(self)}: {comp} of type {type(comp)} not recognized as an index",
                        )

                elif isinstance(comp, Player):
                    player = comp

                elif isinstance(comp, Couple):
                    couple = comp

                elif isinstance(comp, _Commodity):
                    # check if this is the right commodity type for the aspect
                    # domain.commodity should be the primary commodity only
                    if self.primary_type and isinstance(comp, self.primary_type):
                        commodity = comp
                    # else:
                    #     # anything else is a derivative commodity
                    #     dresource = comp

                elif isinstance(comp, Indicator):
                    indicator = comp

                elif isinstance(comp, Bind):
                    # if a direct Bind is being passed
                    # thing get a little easier as the bind has specific information
                    # this only comes in play for calculations (streams, impacts)

                    binds.append(comp)
                    for b in binds:
                        if b.domain.binds:
                            binds.extend(b.domain.binds)
                    binds = list(set(binds))

                elif isinstance(comp, Modes):
                    modes = comp

                else:
                    raise ValueError(
                        f"For component {self} of type {type(self)}: {comp} of type {type(comp)} not recognized as an index",
                    )

            domain = Domain(
                indicator=indicator,
                commodity=commodity,
                process=process,
                storage=storage,
                transport=transport,
                player=player,
                couple=couple,
                loc=loc,
                link=link,
                period=period,
                lag=lag,
                modes=modes,
                binds=binds,
            )

        else:
            timed = True
            spaced = True

        return Bind(aspect=self, domain=domain, timed=timed, spaced=spaced)

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
                self.V(*index).sol(True),
                linewidth=linewidth,
                color=color,
            )
        else:
            for z_ in z:
                index = [i.I for i in (z_,) + y + (x,)]
                ax.plot(
                    [i.name for i in x.I._],
                    self.V(*index).sol(True),
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __init_subclass__(cls):
        cls.__repr__ = Aspect.__repr__
        cls.__hash__ = Aspect.__hash__
