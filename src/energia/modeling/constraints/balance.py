"""Bal"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from operator import is_
from typing import TYPE_CHECKING, Self

from gana.operations.operators import sigma

from ._generator import _Generator

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.function import F

    from ...components.commodity.resource import Resource
    from ...components.operation.process import Process
    from ...components.operation.storage import Storage
    from ...components.operation.transport import Transport
    from ...components.spatial.linkage import Link
    from ...components.spatial.location import Loc
    from ...components.temporal.period import Period
    from ...core.x import X
    from ...represent.model import Model
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect


@dataclass
class Balance(_Generator):
    """Performs a general resource balance

    Args:
        aspect (Aspect. optional): Aspect to which the constraint is applied
        domain (Domain. optional): Domain over which the aspect is defined

    Attributes:
        name (str. optional): Name of the constraint.
    """

    def __post_init__(self):

        # write stream balance constraint
        if self.domain.resource:

            self.writecons_grb()

    @property
    def mapped_to(self) -> list[Domain]:
        """List of domains that the aspect has been mapped to"""
        return self.aspect.maps

    @property
    def sign(self) -> float:
        """Returns the aspect"""
        return self.aspect.sign

    def give_sum(self, mapped: F = None, tsum: bool = False):
        """Gives the sum of the variable over the domain"""
        if tsum:
            if mapped:
                v = mapped
            else:
                v = getattr(self.program, self.aspect.name)
            # if the domain has been mapped to but this is a time sum
            # we need to first map time
            # and then add it to an existing map at a lower domain
            v_sum = sigma(
                v(*self.domain.Ilist),
                self.domain.time.I,
            )
            return v_sum
        else:
            return self(*self.domain).V()

    def writecons_grb(self):
        """Writes the stream balance constraint"""

        if self.domain.lag:
            return

        resource = self.domain.resource

        space = self.domain.space

        if self.domain.link:
            if self.aspect.sign == -1:
                _loc = self.domain.link.source

            else:
                _loc = self.domain.link.sink
        else:
            _loc = self.domain.loc

        time = self.domain.time

        if time is None:
            time = self.model.default_period()

        if not resource in self.grb:
            self.model.update_grb(resource, space=_loc, time=time)

        if not self.aspect.create_grb:
            # if a general resource balance is not to be created
            # The stream will be mapped to existing balances
            spaces = [
                space
                for space, t_resource in self.grb[resource].items()
                if any(
                    [self.grb[resource][space][t] for t in self.grb[resource][space]]
                )
                and self.domain.space in space
            ]

            times = sum(
                [
                    [
                        time
                        for time, truth in self.grb[resource][space].items()
                        if truth and time < self.domain.time
                    ]
                    for space in spaces
                ],
                [],
            )

            space_map, time_map = True, True

        else:
            spaces = [_loc]
            times = [time]

            space_map, time_map = False, False

        for _loc, time in product(spaces, times):

            _name = f'{resource}_{_loc}_{time}_grb'

            # ---- initialize GRB for resource if necessary -----

            # self.model.update_grb(resource=resource, space=_loc, time=time)
            if not time in self.grb[resource][_loc]:
                # this is only used if times are being declared dynamically (based on parameter set sizes)
                self.model.update_grb(resource=resource, time=time, space=_loc)

            if not self.grb[resource][_loc][time]:
                # this checks whether a general resource balance has been defined
                # for the resource in that space and time

                # first check if a bind has been defined

                # update the GRB aspects

                self.grb[resource][_loc][time].append(self)

                # if not defined, start a new constraint
                if self.domain.operation:
                    print(
                        f'--- General Resource Balance for {resource} in ({space}, {time}): initializing constraint , adding {self.aspect} from {self.domain.operation}'
                    )

                else:
                    print(
                        f'--- General Resource Balance for {resource} in ({space}, {time}): initializing constraint , adding {self.aspect}'
                    )

                if self.aspect.ispos:  # or _signs[n]:
                    cons = self(*self.domain).V() == 0
                else:
                    cons = -self(*self.domain).V() == 0

                cons.categorize('General Resource Balance')

                setattr(
                    self.program,
                    _name,
                    cons,
                )

                # updates the constraints in all indices of self.domain
                self.domain.update_cons(_name)
                # add constraint name for aspect
                self.aspect.constraints.append(_name)

            # ---- add aspect to GRB if not added already ----

            elif not self in self.grb[resource][_loc][time]:

                if self.domain.operation:
                    print(
                        f'--- General Resource Balance for {resource} in ({space}, {time}): adding {self.aspect} from {self.domain.operation}'
                    )
                else:
                    print(
                        f'--- General Resource Balance for {resource} in ({space}, {time}): adding {self.aspect}'
                    )

                # update the GRB aspects
                self.grb[resource][_loc][time].append(self)

                # grab the constraint from the program
                cons_grb = getattr(self.program, _name)

                if space_map:
                    v_bal = self.give_sum()
                else:
                    v_bal = self(*self.domain).V()

                if time_map:
                    v_bal = self.give_sum(mapped=v_bal, tsum=True)

                # update the constraint
                if self.aspect.ispos:
                    setattr(
                        self.program,
                        _name,
                        cons_grb + v_bal,
                    )
                else:
                    setattr(
                        self.program,
                        _name,
                        cons_grb - v_bal,
                    )

                # updates the constraints in all the indices of self.domain
                self.domain.update_cons(_name)
                # add constraint name to aspect
                if _name not in self.aspect.constraints:
                    self.aspect.constraints.append(_name)

            else:
                # ---- add aspect to GRB if not added already ----

                if resource.base and self.grb[resource.base][space][time]:
                    # if the resource has a base, it is also bound at the same scale
                    # this is used for stored resources, which are bound at the same scale as their base

                    self.writecons_grb()

                # check if the resource is bound at a spatial index of a lower order
                if not self.domain.link and space.isin:
                    if self.grb[resource][space.isin][time]:

                        if self.domain.operation:
                            print(
                                f'--- General Resource Balance for {resource} in ({space.isin}, {time}): adding {self.aspect} from {self.domain.operation}'
                            )
                        else:
                            print(
                                f'--- General Resource Balance for {resource} in ({space.isin}, {time}): adding {self.aspect}'
                            )

                        _name = f'{resource}_{space.isin}_{time}_grb'

                        cons_grb = getattr(self.program, _name)
                        if self.aspect.ispos:  # or _signs[n]:
                            setattr(
                                self.program,
                                _name,
                                cons_grb + self(*self.domain).V(),
                            )
                        else:
                            setattr(
                                self.program,
                                _name,
                                cons_grb - self(*self.domain).V(),
                            )
                        self.domain.update_cons(_name)
                        if _name not in self.aspect.constraints:
                            self.aspect.constraints.append(_name)

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
