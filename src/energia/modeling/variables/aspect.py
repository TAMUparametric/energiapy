"""Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Self, Type

import matplotlib.pyplot as plt
from gana.sets.index import I
from matplotlib import rc

from ...components.commodity.resource import Resource
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
from ...core.name import Name
from ..constraints.bind import Bind
from ..indices.domain import Domain

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.constraint import C
    from gana.sets.variable import V

    from ...core.x import X
    from ...dimensions.decisiontree import DecisionTree
    from ...represent.model import Model
    from .control import Control
    from .state import State
    from .stream import Stream


@dataclass
class Aspect(Name):
    """Any kind of decision

    Attributes:
        nn (bool): If True, the decision is a non-negative decision. Defaults to True
        Operation (Type[Process | Storage | Transport]): The type of operation associated with the decision. Defaults to None
        Resource (Type[Resource]): The type of resource associated with the decision. Defaults to None
        DResource (Type[Resource]): The type of derivative resource associated with the decision. Defaults to None
        Indicator (Type[Indicator]): The type of indicator associated with the decision. Defaults to None
        latex (str): LaTeX representation of the decision. Defaults to None
    """

    nn: bool = True
    types_opr: tuple[Type[Process | Storage | Transport]] = None
    types_res: Type[Resource] = None
    types_dres: Type[Resource] = None
    types_idc: Type[Indicator] = None
    latex: str = None

    def __post_init__(self):
        Name.__post_init__(self)
        # name of the decision
        self.model: Model = None
        self.neg: Self = None
        if self.label:
            if self.nn:
                self.label += ' [+]'
            else:
                self.label += ' [-]'
        self.indices: list[Location | Linkage, Periods] = []

        # Does this add to the domain?
        self.ispos = True
        # if a decision is bounded by another decision
        self.bound: Self = None

        # spaces where the aspect has been already bound
        self.bound_spaces: dict[
            Resource | Process | Storage | Transport, list[Location | Linkage]
        ] = {}

        # Domains of the decision
        self.domains: list[Domain] = []

        # a dictionary of domains and their maps from higher order domains

        self._maps: bool = False

        self._maps_report: bool = False

        # reporting variable
        self.reporting: V = None

        # has this variable been set at as index
        self._indexed: bool = False

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

    @property
    def isneg(self) -> bool:
        """Does this remove from the domain?"""
        return not self.ispos

    @property
    def sign(self) -> float:
        """Gives the multiplier in balances"""
        if self.ispos:
            return 1.0
        else:
            return -1.0

    @property
    def I(self):
        """gana index set (I)"""
        return getattr(self.program, self.name)

    @property
    def V(self) -> V:
        """Variable"""
        return getattr(self.program, self.name)

    @property
    def index(self):
        """_Index set"""
        return getattr(self.program, self.name)

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        return [getattr(self.program, c) for c in self.constraints]

    @property
    def network(self):
        """Circumscribing Loc (Spatial Scale)"""
        return self.model.network

    @property
    def horizon(self):
        """Circumscribing Periods (Temporal Scale)"""
        return self.model.horizon

    @property
    def time(self):
        """Time"""
        return self.model.time

    @property
    def space(self):
        """Space"""
        return self.model.space

    @property
    def program(self) -> Prg:
        """Mathematical Program"""
        return self.model.program

    @property
    def tree(self) -> DecisionTree:
        """Tree"""
        return self.model.tree

    @property
    def grb(
        self,
    ) -> dict[Resource, dict[Location | Linkage, dict[Periods, list[Aspect]]]]:
        """General Resource Balance dict"""
        return self.model.grb

    @property
    def dispositions(self) -> dict[
        Self,
        dict[
            Resource | Process | Storage | Transport,
            dict[
                Periods | Location | Linkage, dict[Location | Periods | Linkage, bool]
            ],
        ],
    ]:
        """Dispositions dict"""
        return self.model.dispositions

    def map_domain(self, domain: Domain):
        """Each inherited object has their own"""
        pass

    def show(self, descriptive=False):
        """Pretty print the component"""
        for c in self.cons:
            c.show(descriptive)

    def sol(
        self, n_sol: int = 0, aslist: bool = False, compare: bool = False
    ) -> list[float] | None:
        """Solution
        Args:
            aslist (bool, optional): Returns values taken as list. Defaults to False.
        """
        var: V = getattr(self.program, self.name)
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
            types_opr=self.types_opr,
            types_res=self.types_res,
            types_idc=self.types_idc,
            types_dres=self.types_dres,
        )
        dscn.neg, self.neg = self, dscn
        dscn.ispos = not self.ispos
        return dscn

    def __init_subclass__(cls):
        cls.__repr__ = Aspect.__repr__
        cls.__hash__ = Aspect.__hash__

    def __len__(self):
        return len(self.domains)

    def __eq__(self, other: Self) -> bool:
        if isinstance(other, Aspect):
            return self.name == other.name

    def __call__(self, *index: X, domain: Domain = None):
        if not domain:

            (
                indicator,
                resource,
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
                    process = comp

                elif isinstance(comp, Storage):
                    storage = comp

                elif isinstance(comp, Transport):
                    transport = comp

                elif isinstance(comp, Player):
                    player = comp

                elif isinstance(comp, Couple):
                    couple = comp

                elif isinstance(comp, Resource):
                    # check if this is the right resource type for the aspect
                    # domain.resource should be the primary resource only
                    if isinstance(comp, self.types_res):
                        resource = comp
                    # else:
                    #     # anything else is a derivative resource
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
                        f'For component {self} of type {type(self)}: {comp} of type {type(comp)} not recognized as an index'
                    )

            domain = Domain(
                indicator=indicator,
                resource=resource,
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
        x: X,
        y: tuple[X] | X,
        z: tuple[X] | X = None,
        font_size: float = 16,
        fig_size: tuple[float, float] = (12, 6),
        linewidth: float = 0.7,
        color: str = 'blue',
        grid_alpha: float = 0.3,
        usetex: bool = True,
    ):
        """Plot the decision"""
        if not isinstance(y, tuple):
            y = (y,)
        if not z:
            index = [i.I for i in y + (x,)]
        else:
            if not isinstance(z, tuple):
                z = (z,)

        if usetex:
            rc(
                'font',
                **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size},
            )
            rc('text', usetex=usetex)
        else:
            rc('font', **{'size': font_size})

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
        plt.title(f'{self.label} - {label_}')
        plt.ylabel("Values")
        plt.xlabel(f'{x.label or x.name}')
        plt.grid(alpha=grid_alpha)
        if z:
            plt.legend()
        plt.rcdefaults()
