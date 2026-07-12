"""Sample of an Aspect"""

from __future__ import annotations

import logging
from functools import cached_property
from itertools import chain
from typing import TYPE_CHECKING, Self

from gana import I as Idx
from gana import V, inf, sigma, sup

from ..._core._hash import _Hash
from ...utils.dictionary import merge_trees
from ..constraints.bind import Bind

logger = logging.getLogger("energia")


if TYPE_CHECKING:
    from gana import P, Prg
    from gana.sets.constraint import C
    from gana.sets.function import F

    from ..._core._component import _Component
    from ..._core._x import _X
    from ..variables.aspect import Aspect
    from .domain import Domain


# ------------------------------------------------------------------------------
# Sample is the primary constraint generator
# These are essentially a variable waiting to be bound
# ------------------------------------------------------------------------------


class Sample(_Hash):
    """
    Sets a bound on a variable (V) within a particular domain.

    :param aspect: Aspect to which the constraint is applied.
    :type aspect: Aspect | None
    :param domain: Domain over which the aspect is defined.
    :type domain: Domain | None
    :param timed: If the temporal index is predetermined. Defaults to None.
    :type timed: bool | None
    :param spaced: If the spatial index is predetermined. Defaults to None.
    :type spaced: bool | None
    :param report: If a reporting binary variable is needed. Defaults to False.
    :type report: bool, optional

    :ivar hasinc: If incidental calculation is generated.
    :vartype hasinc: bool
    :ivar nominal: If nominal is provided and multiplied by the nominal value.
    :vartype nominal: float | None
    :ivar norm: The input argument is normalized if True.
    :vartype norm: bool
    :ivar parameter: Parameter
    :vartype parameter: P
    :ivar length: Length of the parameter set.
    :vartype length: int

    .. note::
        - ``timed`` and ``spaced`` help skip the calculation of finding the appropriate index.
            For time, this is done based on the length of the input parameter.
        - ``opr`` is useful if providing a combined bound to different variables.
        - ``name`` is generated based on the variable.
        - ``domains`` are updated as the program is built.
    """

    def __init__(
        self,
        aspect: Aspect,
        domain: Domain,
        timed: bool = False,
        spaced: bool = False,
        report: bool = False,
    ):

        self.aspect = aspect
        self.domain = domain
        self.timed = timed
        self.spaced = spaced
        self.report = report

        self._handshake()

        # if incidental calculation is generated
        self.hasinc: bool = False
        # if nominal is provided
        # and multiplied by the nominal value
        self.nominal: float | None = None
        # the input argument is normalized if True
        self.norm: bool = False
        # parameter and length
        self.parameter: P | None = None
        self.length: int = 0

        # the bound is set for all indices
        self._forall: list[_X] = []

    @property
    def of(self) -> Self | None:
        """Sample being calculated"""
        return self.domain.samples[0] if self.domain.samples else None

    @cached_property
    def name(self) -> str:
        """Name of the constraint"""
        # can have a sample without aspect or primary
        # safe to cache
        return f"{self.domain.primary}.{self.aspect.name}"

    @property
    def index(self) -> list[_Component]:
        """_Index"""
        return self.domain.index

    @property
    def index_short(self) -> list[_X | Sample]:
        """Short Index"""
        return self.domain.index_short

    @cached_property
    def I(self) -> Idx:
        """gana index set (I)"""
        return self.domain.I

    @property
    def x(self) -> Self:
        """Binary Reporting Variable"""
        self.report = True
        return self

    @property
    def add(self) -> Self:
        """Positive Control Response"""
        return self.aspect.add(*self.index)

    @property
    def sub(self) -> Self:
        """Negative Control Response"""
        return self.aspect.sub(*self.index)

    @property
    def F(self):
        """Function"""
        return self.X(1) if self.report else self.V(1)

    @property
    def constraints(self):
        """Constraints"""
        return self.aspect.constraints

    @cached_property
    def space(self):
        """Assigns to network is spatial index is not given"""
        if not self.spaced:
            # if spatial index is not explicity given
            # default to the network
            self.domain.location = self.aspect.network

        return self.domain.location

    @cached_property
    def time(self):
        """Matches an appropriate temporal scale
        Sets domain.periods if needed and
        returns domain.periods
        """
        if not self.timed:
            self.domain.periods = self._match_time()
        return self.domain.periods

    def _match_time(self):
        """Matches an appropriate temporal scale"""
        if isinstance(self.parameter, list):
            # if list is given, find using length of the list
            if self.domain.modes is not None:
                return self.aspect.time.find(
                    len(self.parameter) / len(self.domain.modes),
                )
            return self.aspect.time.find(len(self.parameter))

        if isinstance(self.length, int):
            # if length is given, use it directly
            return self.aspect.time.find(self.length)
        # else the size of parameter set is exactly one
        # or nothing is given, meaning the variable is not time dependent
        # thus, index by horizon
        return self.aspect.horizon

    def _handshake(self):
        """Take what is needed"""
        self.model = self.aspect.model
        self.program = self.model.program
        self.balances = self.model.balances
        # if the aspect is bound (operate for example)
        self.bound = self.aspect.bound

    def _inform(self):
        """Informs the aspect and domain about the sample"""
        # updated the indices
        # we can be confident that the self.I is unique
        # because of the check above
        self.aspect.indices.append(self.I)

        # this updates the balanced dictionary, by adding the commodity as a key

        if self.domain.commodity and not self.domain.lag:
            _ = self.balances[self.domain.commodity][self.domain.space][
                self.domain.time
            ]

        # this lets all self.I elements in the domain know
        # that the aspect was sampled
        self.domain.inform_components_of_domain(self.aspect)

        # ------Update the disposition ---------------

        # get the primary component
        # update the disposition dictionary
        self.model.dispositions = merge_trees(
            self.model.dispositions,
            {self.aspect: self.domain.tree},
        )
        # for the same aspect, map variables with higher order indices
        # to variables with lower order indices
        self.aspect.update(self.domain)

        self.aspect.domains.append(self.domain)

    # ---------------------------------------------------------------------------
    #               Preparation and Additional Args
    # ---------------------------------------------------------------------------

    def prep(self, nominal: float = 1, norm: bool = True) -> Self:
        """
        Nominal value

        :param nominal: If the input argument (bounds) are to be scaled, defaults to 1
        :type nominal: float, optional
        :param norm: If the input argument (bounds) are normalized, defaults to True
        :type norm: bool, optional
        """
        self.nominal = nominal
        self.norm = norm
        return self

    def forall(self, index) -> Self:
        """Returns the function at the given index"""
        self._forall = index
        return self

    # ---------------------------------------------------------------------------
    #               Variable Birthing
    # ---------------------------------------------------------------------------

    def _init_V(
        self, parameter: float | list[float] | None = None, length: int | None = None
    ):
        """Initialize making a variable"""

        self.parameter = parameter
        self.length = length

        if self.domain.primary not in self.aspect.bound_spaces:
            self.aspect.bound_spaces[self.domain.primary] = {
                rel: [] for rel in ["ub", "lb", "eq"]
            }

        # Sample will figure these out if needed
        _ = self.time
        _ = self.space

    def V(
        self,
        parameter: float | list[float] | None = None,
        length: int | None = None,
    ) -> V:
        """
        Returns a gana variable (V) using .domain as the index.
        If time and space are (or) not given, i.e. .spaced or .timed are False,
        They can be determined.

        For identifying the appropriate temporal scale (index):
            The length of the parameter set is used
            Alternatively, the length of the parameter set can passed directly
            If neither are passed, it defaults to horizon

        If the spatial index is not given, it defaults to the network.

        :param parameters: the parameter/parameter set. Defaults to None.
        :type parameters: int | list, optional
        :param length: length of the parameter set. Defaults to None.
        :type length: int, optional
        :param report: to make a binary reporting variable. Defaults to False.
        :type report: bool, optional
        :param incidental: if this is an incidental calculation. Defaults to False.
        :type incidental: bool, optional

        .. note::
            - parameters and length are mutually exclusive
        """

        self._init_V(parameter, length)

        # with lag it is assumed that the variable of which this is a lagged subset is
        # already defined
        # for example, if opr_t = opr_t-1 + x_t, then opr_t is already defined
        if self.domain.lag:
            return self.Vlag()

        # the reason we check by string is that:
        # some variables can serve as indices, a normal check ends by
        # creating a constraint variable == variable

        # TODO: run this check for all V types.
        # TODO: Will require separate aspect.indices lists

        if str(self.I) not in [str(i) for i in self.aspect.indices]:

            # if a variable has not been created for the self.I
            # create a variable
            # all energia variables are mutable by default
            setattr(
                self.program,
                self.aspect.name,
                V(*self.I, mutable=True, ltx=self.aspect.latex),
            )
            self._inform()

        return getattr(self.program, self.aspect.name)(*self.I)

    def Vinc(self, parameters: float | list = None, length: int = None) -> V:
        """
        Returns the incidental variable

        :param parameters: the parameter/parameter set. Defaults to None.
        :type parameters: float | list, optional
        :param length: length of the parameter set. Defaults to None.
        :type length: int, optional

        :returns: the incidental variable
        :rtype: V
        """
        self._init_V(parameters, length)

        if self.domain.lag:
            return self.Vlag()

        self.hasinc = True

        # if incidental calculation is needed
        # incidental calculations do not scale with variable value
        # rather, they are incurred if the reporting binary = 1
        # see the equations below:
        #   calc_total = calc + calc_incidental
        #   calc = v * param
        #   calc_incidental = v_reporting * param_incidental
        # named with a superscript inc
        ltx = (
            self.aspect.latex + r"^{inc}"
            if self.aspect.latex
            else self.aspect.name + r"^{inc}"
        )

        # create an incidental variable (continuous)
        setattr(
            self.program,
            f"{self.aspect.name}_incidental",
            V(*self.I, mutable=True, ltx=ltx),
        )
        return getattr(self.program, f"{self.aspect.name}_incidental")(*self.I)

    def Vb(self) -> V:
        r"""
        Bound Variable
        These apply when there are multiple levels of variable-making
        Endogenous bounds apply, i.e.

        :returns: the bound variable
        :rtype: V

        .. math::
           \mathbf{v}_{\dots, t^{+}} <= {\theta}_{\dots, t^{+}} \cdot \mathbf{v}_{\dots, t^{-}}

        where :
        - :math:`\mathbf{v}` is the variable
        - :math:`\theta` is the parameter set
        - :math:`t^{i}` are bespoke discretizations of the horizon
        - :math:`i \in \{-, +\}` are variable-making levels
        """

        bound_aspect = getattr(self.model, self.aspect.bound)

        if bound_aspect not in self.model.dispositions:
            return 1

        if (
            self.domain.space
            not in self.model.dispositions[bound_aspect][self.domain.primary]
        ):

            # if the bound variable has not been defined at the given space
            logger.info(
                "Aspect (%s) not defined at %s, a variable will be created assuming %s as the temporal index",
                bound_aspect,
                self.domain.space,
                self.model.horizon,
            )

            domain = self.domain.edit({"periods": self.model.horizon})

        else:
            # if the bound variable has been defined for the given space
            times = self.model.dispositions[bound_aspect][self.domain.primary][
                self.domain.space
            ]
            time = max(list(times))
            if time >= self.domain.periods:
                domain = self.domain.edit({"periods": time})
            else:
                # this is if the binding variable has a sparser temporal index compared to time
                raise ValueError(
                    f"Incompatible temporal indices: {bound_aspect} defined in time {time} and {self.aspect} defined in time {self.domain.periods}\n"
                    f"Binding variable ({bound_aspect}) cannot have a denser discretization than variable being bound ({self.aspect})",
                )
        return bound_aspect(domain=domain).V()

    def X(
        self, parameters: float | list[float] | None = None, length: int | None = None
    ) -> V:
        r"""
        Binary Reporting Variable
        These report whether a variable has been made or not
        Also useful to make the variable space semi-continuous

        .. math::
              \mathbf{v}_{\dots, t} <= {\theta}_{\dots, t} \cdot \mathbf{x}_{\dots, t}

        where :
            - :math:`\mathbf{v}` is the variable
            - :math:`\mathbf{x}` is the binary reporting variable
            - :math:`\theta` is the parameter set
            - :math:`t` some bespoke discretization of the horizon
        """

        self._init_V(parameters, length)

        if self.domain.lag:
            return self.Vlag()

        # these are basically named using a breve over the variable name or latex name

        if self.aspect.latex:
            ltx = r"{\breve{" + self.aspect.latex + r"}}"
        else:
            ltx = r"{\breve{" + self.aspect.name + r"}}"
        # create a binary variable
        setattr(
            self.program,
            f"x_{self.aspect.name}",
            V(
                *self.I,
                mutable=True,
                ltx=ltx,
                bnr=True,
            ),
        )
        v_rpt = getattr(self.program, f"x_{self.aspect.name}")
        self.aspect.reporting = v_rpt
        return v_rpt(*self.I)

    def Vlag(self):
        """Handles lagged domains"""
        # with lag it is assumed that the variable of which this is a lagged subset is
        # already defined
        # for example, if opr_t = opr_t-1 + x_t, then opr_t is already defined
        try:
            return getattr(self.program, self.aspect.name)(*self.domain.I)

        except AttributeError:
            _ = self >= 0
            return getattr(self.program, self.aspect.name)(*self.domain.I)

        except KeyError:
            # the variable has not been defined yet
            lag = self.domain.lag
            self.domain = self.domain.edit(
                {"lag": None, "periods": self.domain.lag.of},
            )
            args = (self.parameter, self.length)

            if self.hasinc:
                _ = self.Vinc(*args)

            if self.report:
                _ = self.X(*args)

            else:
                _ = self.V(*args)

            self.domain = self.domain.edit({"lag": lag, "periods": None})
            return getattr(self.program, self.aspect.name)(*self.domain.I)

    # ---------------------------------------------------------------------------
    #               Optimization and Evaluation
    # ---------------------------------------------------------------------------

    def obj(self, maximize: bool = False):
        """
        Set the sample itself as the objective

        :param max: if maximization, defaults to False
        :type max: bool, optional
        """
        if not self.timed:
            # if the temporal index is not passed
            self.domain.periods = self.model.horizon
        if not self.spaced:
            # if the spatial index is not passed
            self.domain.location = self.model.network

        # consider all of self.domain
        v = self.V()

        if len(v) == 1:
            _obj = v
        else:
            _obj = sigma(v)

        if self.hasinc:
            # if there is an incidental variable
            # the incidental variable is added to the objective
            v_inc = self.Vinc()
            if len(v_inc) == 1:
                _obj += v_inc
            else:
                _obj += sigma(v_inc)

        if maximize:
            setattr(self.program, f"max{self.aspect.name})", sup(_obj))
        else:
            setattr(self.program, f"min({self.aspect.name})", inf(_obj))

        self.program.renumber()

    def opt(self, maximize: bool = False):
        """
        Optimize

        :param maximize: if maximization, defaults to False
        :type maximize: bool, optional
        """
        self.obj(maximize)
        # optimize!
        self.program.opt()

    def bounds(self):
        """Finds the bounds of the variable"""
        # TODO
        self.opt()
        bmin = self.program.obj()
        self.opt(maximize=True)
        bmax = -self.program.obj()
        return (bmin, bmax)

    def eval(self, *values: float):
        """
        Evaluate the variable using parametric variable values

        :param values: values for the parametric variables
        :type values: float
        """
        return self.V().eval(*values)

    # ---------------------------------------------------------------------------
    #               Illustration and Output
    # ---------------------------------------------------------------------------

    def output(self, aslist: bool = False, asdict: bool = False, compare: bool = False):
        """
        Solution

        :param aslist: Returns the solution as list, otherwise as a variable
        :type aslist: bool, optional
        :param asdict: Returns the solution as dict, otherwise as a variable
        :type asdict: bool, optional
        :param compare: If True, compares the solutions across multiple solves
        :type compare: bool, optional
        """
        return self.V().output(aslist=aslist, asdict=asdict, compare=compare)

    def show(self, descriptive=False):
        """Pretty print constraints"""

        for c in (
            set(chain.from_iterable(i.constraints for i in self.index))
            & self.aspect.constraints
        ):
            cons: C = getattr(self.program, c)
            cons.show(descriptive)

    def bar(
        self,
        font_size: float = 16,
        fig_size: tuple[float, float] = (12, 6),
        linewidth: float = 0.7,
        color: str = "blue",
        grid_alpha: float = 0.3,
        usetex: bool = True,
        str_idx_lim: int = 10,
    ):
        """Draws the variable as a bar chart"""
        v = self.V()
        v.bar(
            font_size=font_size,
            fig_size=fig_size,
            linewidth=linewidth,
            color=color,
            grid_alpha=grid_alpha,
            usetex=usetex,
            str_idx_lim=str_idx_lim,
        )

    def line(
        self,
        font_size: float = 16,
        fig_size: tuple[float, float] = (12, 6),
        linewidth: float = 0.7,
        color: str = "blue",
        grid_alpha: float = 0.3,
        usetex: bool = True,
        str_idx_lim: int = 10,
    ):
        """Draws the variable as a line chart"""
        v = self.V()
        v.line(
            font_size=font_size,
            fig_size=fig_size,
            linewidth=linewidth,
            color=color,
            grid_alpha=grid_alpha,
            usetex=usetex,
            str_idx_lim=str_idx_lim,
        )

    # ---------------------------------------------------------------------------
    #               Dunders
    # ---------------------------------------------------------------------------

    def __getattr__(self, other):
        aspect = getattr(self.model, other)
        return aspect(self)

    def __le__(self, other):

        Bind(sample=self, parameter=other, leq=True, forall=self._forall)

    def __ge__(self, other):

        if self.aspect.nn and isinstance(other, (int, float)) and other == 0:
            # if a zero lower bound is given
            # just declare the variable
            # it will be non-negative by default
            # and will begin a commodity balance
            self.V()
        else:
            Bind(sample=self, parameter=other, geq=True, forall=self._forall)

    def __eq__(self, other):

        if other is True:
            # if a truth value is give
            # just declare the variable
            # it will be non-negative by default
            # and will begin a commodity balance
            self.V()

        elif isinstance(other, Sample):
            if self.aspect.name == other.aspect.name:
                # if self.domain == other.domain:
                return True
            return False

        else:
            if callable(self.of):
                _ = self.of(*self.domain.index_primary[1:]) >= 0
            Bind(sample=self, parameter=other, eq=True, forall=self._forall)

    def __gt__(self, other):
        logger.info(
            "Bind %s > %s is being written as %s >= %s", self, other, self, other
        )
        _ = self >= other

    def __lt__(self, other):
        logger.info(
            "Bind %s < %s is being written as %s <= %s", self, other, self, other
        )
        _ = self <= other

    def __call__(self, *index) -> Sample:
        return self.aspect(*{*self.domain.index_short, *index}, report=self.report)

    def __getitem__(self, calculate: Sample):
        if isinstance(calculate, int):
            f = self.F(self.F.index[calculate])
            f.report = self.report
            return f
        return calculate(self(), *self.domain.index_spatiotemporal)

    def __add__(self, other: Self | FuncOfSamples):
        if isinstance(other, (int, float)):
            return FuncOfSamples(F=self.F + other, program=self.program)
        return FuncOfSamples(F=self.F + other.F, program=self.program)

    def __radd__(self, other):
        if not other:
            return self

    def __sub__(self, other: Self | FuncOfSamples):
        if isinstance(other, (int, float)):
            return FuncOfSamples(F=self.F - other, program=self.program)
        return FuncOfSamples(F=self.F - other.F, program=self.program)

    def __rsub__(self, other: int | float):
        return FuncOfSamples(F=other - self.F, program=self.program)

    def __mul__(self, other: Self | FuncOfSamples):
        return FuncOfSamples(F=self.F * other.F, program=self.program)

    def __rmul__(self, other: int | float):
        return FuncOfSamples(F=other * self.F, program=self.program)


class FuncOfSamples:
    """Some Function of Samples

    This is used to bind a function of variables to a given parameter (set)

    """

    def __init__(self, F: F, program: Prg):
        self.program = program
        self.F = F

    def __add__(self, other: Self | Sample):
        if isinstance(other, (int, float)):
            return FuncOfSamples(F=self.F + other, program=self.program)
        return FuncOfSamples(F=self.F + other.F, program=self.program)

    def __radd__(self, other):
        if not other:
            return self

    def __sub__(self, other: Self | Sample):
        if isinstance(other, (int, float)):
            return FuncOfSamples(F=self.F - other, program=self.program)
        return FuncOfSamples(F=self.F - other.F, program=self.program)

    def __rsub__(self, other: int | float):
        return FuncOfSamples(F=other - self.F, program=self.program)

    def __mul__(self, other: Self | Sample):
        return FuncOfSamples(F=self.F * other.F, program=self.program)

    def __rmul__(self, other: int | float):
        return FuncOfSamples(F=other * self.F, program=self.program)

    def __eq__(self, other):
        func = self.F == other
        setattr(self.program, f"eq_{self.F.name}", func)
        return func

    def __le__(self, other):
        func = self.F <= other
        setattr(self.program, f"le_{self.F.name}", func)
        return func

    def __ge__(self, other):
        func = self.F >= other
        setattr(self.program, f"ge_{self.F.name}", func)
        return func

    def opt(self, maximize=False):
        """Optimize the function

        :param max: if maximization, defaults to False
        :type max: bool, optional
        """

        setattr(self.program, f"min_{self.F.name}", inf(self.F))
        self.program.opt(maximize=maximize)
