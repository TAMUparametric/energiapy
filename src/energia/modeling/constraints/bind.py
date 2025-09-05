"""Bind"""

from __future__ import annotations

from dataclasses import dataclass
from re import S
from typing import TYPE_CHECKING, Self, Literal

from gana.operations.composition import inf, sup
from gana.operations.operators import sigma
from gana.sets.function import F
from gana.sets.index import I
from gana.sets.variable import V

from ...utils.math import normalize
from ._generator import _Generator
from .calculate import Calculate

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.constraint import C
    from ...core.component import Component
    from ...core.x import X


# ------------------------------------------------------------------------------
# Bind is the primary constraint generator
# These are essentially a variable waiting to be bound
# ------------------------------------------------------------------------------


@dataclass
class Bind(_Generator):
    """Sets a bound on a variable (V) within a particular domain

    Args:
        aspect (Aspect. optional): Aspect to which the constraint is applied
        domain (Domain. optional): Domain over which the aspect is defined
        timed (bool): If the temporal index is predetermined. Defaults to None.
        spaced (bool): If the spatial index is predetermined. Defaults to None.



    Attributes:
        name (str, optional): Name.
        model (Model, optional): Model to which the generator belongs.
        program (Prg, optional): Gana Program to which the generated constraint belongs.
        opr (F): Operation to bind (in lieu of a single variable). Defaults to None.
        domains (Domain): set of domains over which the Bind is applied. Defaults to [].
        hasinc (bool): If the Bind has some incidental calculation. Defaults to False.
    Note:
        - timed and spaced help skip the calculation of finding the appropriate index
          for time this is done based on length of input parameter
        - opr is useful if providing a combined bound to different variables
        - name is generated based on the variable
        - domains are updated as the program is built
    """

    # if the temporal index is predetermined
    timed: bool = None
    # if the spatial index is predetermined
    spaced: bool = None

    def __post_init__(self):

        # if the aspect is bound (operate for example)
        self.bound = self.aspect.bound

        # this is set if the aspect needs a reporting binary variable
        self.report: bool = False

        # if incidental calculation is generated
        self.hasinc: bool = False

        # if nominal is provided
        # and multiplied by the nominal value
        self._nominal: float = None
        # the input argument is normalized if True
        self._normalize: bool = False

        # the bound is set for all indices
        self._forall: list[X] = []

        # an index will be carried here
        self._index: I = None

    @property
    def index(self) -> list[Component]:
        """_Index"""
        return self.domain.index

    @property
    def I(self) -> I:
        """gana index set (I)"""
        return self.aspect.I

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
        return self.V(1)

    @property
    def constraints(self):
        """Constraints"""
        return self.aspect.constraints

    def show(self, descriptive=False):
        """Pretty print the component"""
        constraints = list(set(sum([i.constraints for i in self.index], [])))

        for c in constraints:
            if c in self.aspect.constraints:
                cons: C = getattr(self.program, c)
                cons.show(descriptive)

    def V(
        self,
        parameters: float | list = None,
        length: int = None,
        report: bool = False,
        incidental: bool = False,
    ) -> V:
        """Returns a gana variable (V) using .domain as the index.
        If time and space are (or) not given, i.e. .spaced or .timed are False,
        They can be determined.

        For identifying the appropriate temporal scale (index):
            The length of the parameter set is used
            Alternatively, the length of the parameter set can passed directly
            If neither are passed, it defaults to horizon

        If the spatial index is not given, it defaults to the network.


        Args:
            parameters (int | list): the parameter/parameter set. Defaults to None.
            length (int): length of the parameter set. Defaults to None.
            report (bool): to make a binary reporting variable. Defaults to False.
            incidental (bool): if this is an incidental calculation. Defaults to False.
        Note:
            - parameters and length are mutually exclusive
        """

        # with lag it is assumed that the variable of which this is a lagged subset is already defined
        # for example, if opr_t = opr_t-1 + x_t, then opr_t is already defined
        if self.domain.lag:
            # t - 1 is made after t, so no need to set a new one
            return getattr(self.program, self.name)(*self.domain.Ilist)

        # ------ Check time and space -------
        # this is only called if the bind variable has no temporal index defined
        def time():
            """Matches an appropriate temporal scale"""
            if isinstance(parameters, list):
                # if list is given, find using length of the list
                self.domain.period = self.aspect.time.find(len(parameters))
            elif isinstance(length, int):
                # if length is given, use it directly
                self.domain.period = self.aspect.time.find(length)
            else:
                # else the size of parameter set is exactly one
                # or nothing is given, meaning the variable is not time dependent
                # thus, index by horizon
                self.domain.period = self.aspect.horizon

        # this is only called if the bind variable has no spatial index defined
        def space():
            """Assigns to network is spatial index is not given"""
            # if spatial index is not explicity given
            # default to the network
            self.domain.loc = self.aspect.network

        if not self.spaced:
            # if the spatial index is not passed
            space()

        if not self.domain.primary in self.aspect.bound_spaces:
            self.aspect.bound_spaces[self.domain.primary] = []

        if not self.timed:
            # if the temporal index is not passed
            time()

        # get the list of Indices in the domain
        index = tuple(self.domain.Ilist)

        # --------- if reporting binary ---------------
        # if a reporting binary variable is needed
        if report:
            # these are basically named using a breve over the variable name or latex name
            if self.aspect.latex:
                ltx = r'{\breve{' + self.aspect.latex + r'}}'
            else:
                ltx = r'{\breve{' + self.name + r'}}'
            # create a binary variable
            setattr(
                self.program,
                f'x_{self.name}',
                V(
                    *index,
                    mutable=True,
                    ltx=ltx,
                    bnr=True,
                ),
            )
            v_rpt = getattr(self.program, f'x_{self.name}')
            self.aspect.reporting = v_rpt
            return v_rpt(*index)

        # if incidental calculation is needed
        # incidental calculations do not scale with variable value
        # rather, they are incurred if the reporting binary = 1
        # see the equations below:
        #   calc_total = calc + calc_incidental
        #   calc = v * param
        #   calc_incidental = v_reporting * param_incidental

        # --------- if incidental ---------------

        if incidental:
            # named with a superscript inc
            if self.aspect.latex:
                ltx = self.aspect.latex + r'^{inc}'
            else:
                ltx = self.name + r'^{inc}'

            # create an incidental variable (continuous)
            setattr(
                self.program,
                f'{self.name}_incidental',
                V(*index, mutable=True, ltx=ltx),
            )
            return getattr(self.program, f'{self.name}_incidental')(*index)

        # --------- if continuous ---------------

        # the reason we check by name:
        # some variables can serve as indices, a normal check ends by
        # creating a constraint variable == variable
        # if not [i.name for i in index] in [
        #     [i.name for i in idx] for idx in self.aspect.indices
        # ]:

        if not [i.name for i in index] in [
            [i.name for i in idx] for idx in self.aspect.indices
        ]:
            # if not index in self.aspect.indices:

            # if a variable has not been created for the index
            # create a variable
            # all energia variables are mutable by default
            setattr(
                self.program,
                self.name,
                V(*index, mutable=True, ltx=self.aspect.latex),
            )

            # updated the indices
            # we can be confident that the index is unique
            # because of the check above
            self.aspect.indices.append(index)

            # if write_grb and not self.domain.resource in self.grb:

            # this updates the balanced dictionary, by adding the resource as a key

            if self.domain.resource:
                self.model.update_grb(
                    self.domain.resource, time=self.domain.period, space=self.domain.loc
                )

            # if write_grb and self.domain.resource:
            #     # if this aspects needs to feature in the general resource balance
            #     # at some space and time
            #     # this is where it is declared
            #     # if self.domain.resource:
            #     self.write_grb()

            # this lets all index elements in the domain know
            # that the aspect was sampled
            self.domain.update_domains(self.aspect)

            # --------- Update the disposition ---------------

            # get the primary component
            # update the disposition dictionary
            self.model.update_dispositions(self.aspect, self.domain)

            # for the same aspect, map variables with higher order indices
            # to variables with lower order indices
            self.aspect.map_domain(self.domain)

            self.aspect.domains.append(self.domain)

        return getattr(self.program, self.name)(*index)

    def Vinc(self, parameters: float | list = None, length: int = None) -> V:
        """Returns the incidental variable

        Args:
            parameters (float | list): the parameter/parameter set. Defaults to None.
            length (int): length of the parameter set. Defaults to None.

        Returns:
            V: the incidental variable
        """
        self.hasinc = True
        return self.V(parameters, length, incidental=True)

    def Vb(self) -> V:
        r"""Bound Variable

        Returns:
            V: the bound variable

        These apply when there are multiple levels of variable-making
        Endogenous bounds apply, i.e.

        ..math::
           \mathbf{v}_{\dots, t^{+}} <= {\theta}_{\dots, t^{+}} \cdot \mathbf{v}_{\dots, t^{-}}

        where :
        - :math:`\mathbf{v}` is the variable
        - :math:`\theta` is the parameter set
        - :math:`t^{i}` are bespoke discretizations of the horizon
        - :math:`i \in \{-, +\}` are variable-making levels
        """

        if not self.aspect.bound in self.model.dispositions:
            print(
                f'--- Aspect ({self.aspect.bound}) not defined, a variable will be created at {self.domain.space} assuming {self.model.horizon} as the temporal index'
            )

            _ = self.aspect.bound(self.domain.primary, self.domain.space).V()

        if (
            not self.domain.space
            in self.model.dispositions[self.aspect.bound][self.domain.primary]
        ):

            # if the bound variable has not been defined at the given space
            print(
                f'--- Aspect ({self.aspect.bound}) not defined at {self.domain.space}, a variable will be created assuming {self.model.horizon} as the temporal index'
            )

            domain = self.domain.change({'period': self.model.horizon})

        else:
            # if the bound variable has been defined for the given space
            times = self.model.dispositions[self.aspect.bound][self.domain.primary][
                self.domain.space
            ]
            time = max(list(times))
            if time >= self.domain.period:
                domain = self.domain.change({'period': time})
            else:
                # this is if the binding variable has a sparser temporal index compared to time
                raise ValueError(
                    f'Incompatible temporal indices: {self.aspect.bound} defined in time {time} and {self.aspect} defined in time {self.domain.period}\n'
                    f'Binding variable ({self.aspect.bound}) cannot have a denser discretization than variable being bound ({self.aspect})'
                )
        return self.aspect.bound(domain=domain).V()

    def X(self, parameters: float | list = None, length: int = None) -> V:
        r"""Binary Reporting Variable

        These report whether a variable has been made or not
        Also useful to make the variable space semi-continuous

        ..math::
              \mathbf{v}_{\dots, t} <= {\theta}_{\dots, t} \cdot \mathbf{x}_{\dots, t}

          where :
            - :math:`\mathbf{v}` is the variable
            - :math:`\mathbf{x}` is the binary reporting variable
            - :math:`\theta` is the parameter set
            - :math:`t` some bespoke discretization of the horizon
        """
        return self.V(parameters, length, report=True)

    def opt(self, max: bool = False):
        """Optimize

        max (bool): if maximization, defaults to False
        """
        if not self.timed:
            # if the temporal index is not passed
            self.domain.period = self.model.horizon
        if not self.spaced:
            # if the spatial index is not passed
            self.domain.loc = self.model.network

        # consider all of self.domain
        v = self.V()

        if len(v) == 1:
            obj = v
        else:
            obj = sigma(v)

        if self.hasinc:
            # if there is an incidental variable
            # the incidental variable is added to the objective
            v_inc = self.Vinc()
            if len(v_inc) == 1:
                obj += v_inc
            else:
                obj += sigma(v_inc)

        if max:
            setattr(self.program, f'max{self.name})', sup(obj))
        else:
            setattr(self.program, f'min({self.name})', inf(obj))

        # optimize!
        self.program.opt()

    def bounds(self):
        """Finds the bounds of the variable"""
        # TODO
        self.opt()
        bmin = self.program.obj()
        self.opt(max=True)
        bmax = -self.program.obj()
        return (bmin, bmax)

    def preprocess(self, nominal: float = 1, norm: bool = True) -> Self:
        """Nominal value
        Args:
            value (float): Nominal value to multiply with bounds
            norm (bool): If the input argument (bounds) are normalized, defaults to True
        """
        self._nominal = nominal
        self._normalize = norm
        return self

    def sol(self, aslist: bool = False):
        """Solution

        Args:
            aslist (bool, optional): Returns the solution as a list, otherwise as a variable
        """
        return self.V().sol(aslist=aslist)

    def forall(self, index) -> Self:
        """Returns the function at the given index"""
        self._forall = index
        return self

    # -----------------------------------------------------
    #                    Write Constraints
    # -----------------------------------------------------

    def writecons_bind(
        self,
        rel: Literal['leq', 'eq', 'geq'],
        other: float | list[float] | tuple[float | list[float]],
    ):
        """Binds a variable (aspect at some index) to a parameter"""

        if self._forall:
            # --------- repeats the constraint for all elements in _forall

            if isinstance(other, list):
                for n, idx in enumerate(self._forall):

                    if rel == 'leq':
                        _ = self(idx) <= other[n]
                    elif rel == 'eq':
                        _ = self(idx) == other[n]
                    elif rel == 'geq':
                        _ = self(idx) >= other[n]
            else:
                for idx in self._forall:
                    if rel == 'leq':
                        _ = self(idx) <= other
                    elif rel == 'eq':
                        _ = self(idx) == other
                    elif rel == 'geq':
                        _ = self(idx) >= other

        else:

            # --------- handle the scaling of the data
            if self._nominal:
                if self._normalize:
                    other = [
                        (
                            (self._nominal * i[0], self._nominal * i[1])
                            if isinstance(i, tuple)
                            else self._nominal * i
                        )
                        for i in normalize(other)
                    ]
                else:
                    other = [
                        (
                            (self._nominal * i[0], self._nominal * i[1])
                            if isinstance(i, tuple)
                            else self._nominal * i
                        )
                        for i in other
                    ]

            # --------- Get LHS
            # lhs needs to be determined here
            # because V will be spaced and timed if not passed by user
            # .X(), .Vb() need time and space

            lhs = self.V(other)

            # --------- Get RHS

            if self.aspect.bound is not None and (
                self.model.capacitate
                or (
                    self.aspect.bound in self.dispositions
                    and self.domain.primary in self.dispositions[self.aspect.bound]
                )
            ):
                # --------- if variable bound
                if self.report:
                    # --------- if variable bound and reported
                    # we do not want a bi-linear term
                    rhs = other * self.X(other)

                else:
                    # --------- if just variable bound
                    rhs = other * self.Vb()

                # return if aspect already bound in space
                if self.domain.space in self.aspect.bound_spaces[self.domain.primary]:
                    return
                # else append new space
                self.aspect.bound_spaces[self.domain.primary].append(self.domain.space)

            else:
                # --------- if  parameter bound
                if self.report:
                    # --------- if  parameter bound and reported
                    rhs = other * self.X(other)
                else:
                    # --------- if just parameter bound
                    rhs = other

            if rel == 'leq':
                # Less than equal to
                cons: C = lhs <= rhs
                rel = '_ub'
            elif rel == 'eq':
                # Exactly equal to
                cons: C = lhs == rhs
                rel = '_eq'
            elif rel == 'geq':
                # Greater than equal to
                cons: C = lhs >= rhs
                rel = '_lb'
            else:
                return

            # name of the constraint
            cons_name = rf'{self.name}{self.domain.idxname}{rel}'

            # categorize the constraint
            cons.categorize('Bound')

            # let all objects in the domain know that
            # a constraint with this name contains it
            self.domain.update_cons(cons_name)

            # let the aspect know about the new constraint
            self.aspect.constraints.append(cons_name)

            # set the constraint
            setattr(
                self.program,
                cons_name,
                cons,
            )

    def __le__(self, other):

        self.writecons_bind('leq', other)

    def __ge__(self, other):

        self.writecons_bind('geq', other)

    def __eq__(self, other):

        if other is True:
            # if a truth value is give
            # just declare the variable
            # it will be non-negative by default
            # and will begin a resource balance
            self.V()

        elif isinstance(other, Bind):
            if self.name == other.name:
                if self.domain == other.domain:
                    return True
            return False

        else:
            self.writecons_bind('eq', other)

    def __gt__(self, other):
        _ = self >= other

    def __lt__(self, other):
        _ = self <= other

    def __add__(self, other: Self | FBind):
        if isinstance(other, (int, float)):
            return FBind(F=self.F + other, program=self.program)
        return FBind(F=self.F + other.F, program=self.program)

    def __radd__(self, other):
        if not other:
            return self

    def __sub__(self, other: Self | FBind):
        if isinstance(other, (int, float)):
            return FBind(F=self.F - other, program=self.program)
        return FBind(F=self.F - other.F, program=self.program)

    def __rsub__(self, other: int | float):
        return FBind(F=other - self.F, program=self.program)

    def __mul__(self, other: Self | FBind):
        return FBind(F=self.F * other.F, program=self.program)

    def __rmul__(self, other: int | float):
        return FBind(F=other * self.F, program=self.program)

    def __call__(self, *index):
        index = list(set(self.index + list(index)))
        v = self.aspect(*index)
        v.report = self.report
        return v

    def __getitem__(self, dependent: Bind):
        if isinstance(dependent, int):
            f = self.F(self.F.index[dependent])
            f.report = self.report
            return f

        calculation = dependent(self)

        decision = self(*self.index)
        decision.report = self.report

        return Calculate(calculation=calculation, decision=decision)

        # variable.report = self.report
        # return Calculate(calc=dependent(*self.index), decision=variable)

    def draw(self, **kwargs):
        """Draws the variable"""
        v = self.V()
        v.draw(**kwargs)


class FBind:
    """Function Bind

    This is used to bind a function of variables to a given parameter (set)

    """

    def __init__(self, F: F, program: Prg):
        self.program = program
        self.F = F

    def __add__(self, other: Self | Bind):
        if isinstance(other, (int, float)):
            return FBind(F=self.F + other, program=self.program)
        return FBind(F=self.F + other.F, program=self.program)

    def __radd__(self, other):
        if not other:
            return self

    def __sub__(self, other: Self | Bind):
        if isinstance(other, (int, float)):
            return FBind(F=self.F - other, program=self.program)
        return FBind(F=self.F - other.F, program=self.program)

    def __rsub__(self, other: int | float):
        return FBind(F=other - self.F, program=self.program)

    def __mul__(self, other: Self | Bind):
        return FBind(F=self.F * other.F, program=self.program)

    def __rmul__(self, other: int | float):
        return FBind(F=other * self.F, program=self.program)

    def __eq__(self, other):
        setattr(self.program, f'eq_{self.F.name}', self.F == other)

    def __le__(self, other):
        setattr(self.program, f'le_{self.F.name}', self.F <= other)

    def __ge__(self, other):
        setattr(self.program, f'ge_{self.F.name}', self.F >= other)
