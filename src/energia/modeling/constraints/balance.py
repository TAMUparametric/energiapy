"""Bal"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from operator import is_
from typing import TYPE_CHECKING, Self

from gana import sigma

from ._generator import _Generator

if TYPE_CHECKING:
    from gana import Prg, F

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

        if self.domain.lag:
            return

        # this is the disposition of the variable to be mapped
        # through time and space
        resource, time, space, binds = (
            self.domain.resource,
            self.domain.period,
            self.domain.space,
            self.domain.binds,
        )

        if self.domain.link:
            if self.aspect.sign == -1:
                loc = self.domain.link.source

            else:
                loc = self.domain.link.sink
        else:
            loc = self.domain.loc

        # if no time is provided, take a default period
        if time is None:
            time = self.model.default_period()

        if not resource in self.grb:
            self.model.update_grb(resource, space=loc, time=time)

        # self.model.update_grb(resource=resource, space=loc, time=time)
        if not time in self.grb[resource][loc]:
            # this is only used if times are being declared dynamically (based on parameter set sizes)
            self.model.update_grb(resource=resource, time=time, space=loc)

        if not binds:
            # if no binds, then create GRB or append to exisiting GRB
            # writecons_grb will figure it out
            self.writecons_grb(resource, loc, time)

        else:
            # if there are binds
            if self.grb[resource][loc][time]:
                # if there is already a GRB existing
                # add the bind to the GRB at the same scale
                self.writecons_grb(resource, loc, time)

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

    def writecons_grb(self, resource, loc, time):
        """Writes the stream balance constraint"""

        # if self.domain.lag:
        #     return

        # resource = self.domain.resource

        # space = self.domain.space

        # if self.domain.link:
        #     if self.aspect.sign == -1:
        #         loc = self.domain.link.source

        #     else:
        #         loc = self.domain.link.sink
        # else:
        #     loc = self.domain.loc

        # time = self.domain.time

        # # if no time is provided, take a default period
        # if time is None:
        #     time = self.model.default_period()

        # if not resource in self.grb:
        #     self.model.update_grb(resource, space=loc, time=time)

        # if not self.aspect.create_grb:
        #     # if a general resource balance is not to be created
        #     # The stream will be mapped to existing balances
        #     spaces = [
        #         space
        #         for space, t_resource in self.grb[resource].items()
        #         if any(
        #             [self.grb[resource][space][t] for t in self.grb[resource][space]]
        #         )
        #         and self.domain.space in space
        #     ]

        #     times = sum(
        #         [
        #             [
        #                 time
        #                 for time, truth in self.grb[resource][space].items()
        #                 if truth and time < self.domain.time
        #             ]
        #             for space in spaces
        #         ],
        #         [],
        #     )

        #     space_map, time_map = True, True

        # else:
        #     spaces = [loc]
        #     times = [time]

        #     space_map, time_map = False, False

        # for loc, time in product(spaces, times):

        _name = f'{resource}_{loc}_{time}_grb'

        # ---- initialize GRB for resource if necessary -----

        # # self.model.update_grb(resource=resource, space=loc, time=time)
        # if not time in self.grb[resource][loc]:
        #     # this is only used if times are being declared dynamically (based on parameter set sizes)
        #     self.model.update_grb(resource=resource, time=time, space=loc)

        if not self.grb[resource][loc][time]:
            # this checks whether a general resource balance has been defined
            # for the resource in that space and time

            # first check if a bind has been defined

            # update the GRB aspects

            self.grb[resource][loc][time].append(self)

            # if not defined, start a new constraint
            if self.domain.operation:
                print(
                    f'--- General Resource Balance for {resource} in ({loc}, {time}): initializing constraint , adding {self.aspect} from {self.domain.operation}'
                )

            else:
                print(
                    f'--- General Resource Balance for {resource} in ({loc}, {time}): initializing constraint , adding {self.aspect}'
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

        elif not self in self.grb[resource][loc][time]:

            if self.domain.operation:
                print(
                    f'--- General Resource Balance for {resource} in ({loc}, {time}): adding {self.aspect} from {self.domain.operation}'
                )
            else:
                print(
                    f'--- General Resource Balance for {resource} in ({loc}, {time}): adding {self.aspect}'
                )

            # update the GRB aspects
            self.grb[resource][loc][time].append(self)

            # grab the constraint from the program
            cons_grb = getattr(self.program, _name)

            # if space_map:
            #     v_bal = self.give_sum()
            # else:
            #     v_bal = self(*self.domain).V()

            # if time_map:
            #     v_bal = self.give_sum(mapped=v_bal, tsum=True)

            # update the constraint
            if self.aspect.ispos:
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

            # updates the constraints in all the indices of self.domain
            self.domain.update_cons(_name)
            # add constraint name to aspect
            if _name not in self.aspect.constraints:
                self.aspect.constraints.append(_name)

        else:
            # ---- add aspect to GRB if not added already ----

            if resource.base and self.grb[resource.base][loc][time]:
                # if the resource has a base, it is also bound at the same scale
                # this is used for stored resources, which are bound at the same scale as their base

                self.writecons_grb(resource.base, loc, time)

            # check if the resource is bound at a spatial index of a lower order
            if not self.domain.link and loc.isin:
                if self.grb[resource][loc.isin][time]:

                    if self.domain.operation:
                        print(
                            f'--- General Resource Balance for {resource} in ({loc.isin}, {time}): adding {self.aspect} from {self.domain.operation}'
                        )
                    else:
                        print(
                            f'--- General Resource Balance for {resource} in ({loc.isin}, {time}): adding {self.aspect}'
                        )

                    _name = f'{resource}_{loc.isin}_{time}_grb'

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
