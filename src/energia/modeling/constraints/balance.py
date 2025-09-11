"""Bal"""

from __future__ import annotations

from dataclasses import dataclass
import time as keep_time
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
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
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

        # this is the disposition of the variable to be mapped
        # through time and space
        resource = self.domain.resource
        binds = self.domain.binds
        time = self.domain.time

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

        if not binds and resource:
            # if no binds, then create GRB or append to exisiting GRB
            # writecons_grb will figure it out
            self.writecons_grb(resource, loc, time)

        else:
            # if there are binds

            if resource.insitu:
                # # we need to still check if this is this is an insitu (e.g. a storage resource)
                # if the resource is insitu that means that
                # no external bounds have been defined
                # a GRB is still needed
                self.writecons_grb(resource, loc, time)

            if (
                self.grb[resource][loc][time]
                and self.aspect(resource, loc, time)
                not in self.grb[resource][loc][time]
            ):
                # for the second check, consider the case where

                # # these do not get their own GRB, as they are only utilized within a process

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
                    f'--- General Resource Balance for {resource} in ({loc}, {time}): initializing constraint, adding {self.aspect} from {self.domain.operation}'
                )

            else:
                print(
                    f'--- General Resource Balance for {resource} in ({loc}, {time}): initializing constraint, adding {self.aspect}'
                )
            start = keep_time.time()

            if resource.inv_of and self.aspect.name == 'inventory':
                if len(time) == 1:
                    return
                # if inventory is being add to GRB
                lagged_domain = self.domain.change({'lag': -1 * time, 'period': None})

                cons_grb = -self(*self.domain).V() + self(*lagged_domain).V() == 0
            else:
                if self.aspect.ispos:  # or _signs[n]:
                    cons_grb = self(*self.domain).V() == 0
                else:
                    cons_grb = -self(*self.domain).V() == 0

            cons_grb.categorize('General Resource Balance')

            setattr(
                self.program,
                _name,
                cons_grb,
            )
            end = keep_time.time()
            print(f'    Completed in {end-start} seconds')

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

            start = keep_time.time()

            # update the GRB aspects
            self.grb[resource][loc][time].append(self)

            # grab the constraint from the program
            cons_grb = getattr(self.program, _name)

            if resource.in_inv and self.aspect.name == 'inventory':
                # if inventory is being add to GRB
                lagged_domain = self.domain.change({'lag': -1 * time, 'period': None})

                setattr(
                    self.program,
                    _name,
                    cons_grb + self(*lagged_domain).V() - self(*self.domain).V(),
                )

            else:

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
            end = keep_time.time()
            print(f'    Completed in {end-start} seconds')

            # updates the constraints in all the indices of self.domain
            self.domain.update_cons(_name)
            # add constraint name to aspect
            if _name not in self.aspect.constraints:
                self.aspect.constraints.append(_name)

        else:
            # ---- add aspect to GRB if not added already ----

            # if resource.base and self.grb[resource.base][loc][time]:
            #     # if the resource has a base, it is also bound at the same scale
            #     # this is used for stored resources, which are bound at the same scale as their base

            #     self.writecons_grb(resource.base, loc, time)
            #     self.writecons_grb(resource, loc, -1 * time)

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

                    start = keep_time.time()

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

                    end = keep_time.time()
                    print(f'    Completed in {end-start} seconds')

                    self.domain.update_cons(_name)
                    if _name not in self.aspect.constraints:
                        self.aspect.constraints.append(_name)

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
