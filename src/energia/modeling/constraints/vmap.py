"""Map"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gana import sigma
from operator import is_

from ._generator import _Generator

if TYPE_CHECKING:
    from gana import Prg, C

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
class Map(_Generator):
    """Maps between domains"""

    return_sum: bool = False

    def __post_init__(self):

        # if the variable is being defined for the first time, do not bother with the rest
        # Also note that if a variable already exists then a new is not created
        # thus map_domain is not called in Bind.V()
        # Essentially, the domain being added is always new!

        # 1. a new domain is being added to a new disposition
        # e.g.:
        #   (water, dam, goa, year) with disposition ['resource', 'operation', 'space', 'time'] exists
        #   (dam, goa, q) with disposition ['operation', 'space', 'time'] is added

        # # 2. a new domain is being added to an existing disposition
        # # e.g.:
        # #   (dam, goa, year) with disposition ['operation', 'space', 'time'] exists
        # #   (dam, goa, q) with disposition ['operation', 'space', 'time'] is added
        # #   The variable will need to be mapped across 'time

        if self.domain.lag:
            return

        # this is the disposition of the variable to be mapped
        # through time and space
        time, space = self.domain.period, self.domain.space

        # these are periods denser and sparser than the current domain
        denser_periods, sparser_periods = self.model.time.split(time)

        # these are spaces contained in loc and parent location to which this loc belongs

        contained_locations, parent_location = self.model.space.split(space)

        # this gives all the dispositions at which the aspect has been defined
        dispositions = self.dispositions[self.aspect][self.domain.primary]

        # mapping happens between:
        # 1. sparser time to denser time in same space
        # 2. contained location to parent location
        # 3. (sparser time, contained location) to (denser time, parent location)
        # you cant map at the same level
        # consider the State Goa, with two towns Madgaon and Ponje
        # Goa with Maharashtra, make up India (for the purpose of modeling)
        # Aspect from Goa can be mapped to India
        # Goa does not need to be mapped to Maharashtra
        # Madgaon and Ponje are both mapped to Just Goa
        # note that .alsohas() checks at lower levels
        # the operators <, > wont work since they will add any space a higher order
        # this will lead to adding twice. India = Goa + Madgaon + Ponje (WRONG)
        # We scale only one level up

        if space in dispositions and time in dispositions[space]:
            # the aspect is already defined at this location
            # we need to check if it is defined for any periods sparser than time
            for sparser_period in sparser_periods:
                if sparser_period in dispositions[space]:

                    # check if the aspect has been defined for a sparser period
                    # this creates a map from this domain to a sparser domain
                    self.writecons_map(
                        self.domain,
                        self.domain.change({'period': sparser_period}),
                        tsum=True,
                    )

            for denser_period in denser_periods:
                if denser_period in dispositions[space]:

                    # create a new domain to map from
                    domain_from = self.domain.copy()
                    domain_from.period = denser_period
                    binds_dict = dispositions[space][denser_period]
                    binds = []
                    # TODO - check this
                    # here I am re creating Bind objects
                    # from the dict of the form {aspect: {component: {aspect: {component: {...}}}}}
                    # there has to be a way to avoid this
                    # I make a list  of bounds as such [aspect(component), aspect(component), ...]
                    iter_dict = binds_dict
                    for aspect, component_dict in iter_dict.items():
                        for component in component_dict:
                            binds.append(aspect(component))
                            iter_dict = iter_dict[aspect][component]

                    domain_from.binds = binds
                    domain_to = self.domain.copy()

                    # check if the aspect has been defined for a denser period
                    self.writecons_map(
                        domain_from,
                        # self.domain.change({'period': denser_period}),
                        domain_to,
                        tsum=True,
                    )

            for contained_loc in contained_locations:
                if contained_loc in dispositions:
                    # check if the aspect has been defined for a contained location
                    self.writecons_map(
                        self.domain.change({'loc': contained_loc}),
                        self.domain,
                    )

            if parent_location in dispositions:
                # check if the aspect has been defined for a parent location
                self.writecons_map(
                    self.domain,
                    self.domain.change({'loc': parent_location}),
                )

            if not self.domain.binds and dispositions[space][time]:
                # if the current variable being declared has no binds
                # but the aspect has already been defined at this location and time with binds
                # there is a need to map from the defined binds to no binds
                # get list of domains of the aspect
                domains = [
                    d
                    for d in self.aspect.domains
                    if is_(d.primary, self.domain.primary)
                    and is_(d.space, space)
                    and is_(d.period, time)
                    and d.binds
                ]

                for domain in domains:
                    self.writecons_map(
                        domain,
                        self.domain,
                    )

    @property
    def maps(self) -> list[str]:
        """List of domains that the aspect has been mapped to"""
        return self.aspect.maps

    def give_sum(self, domain: Domain, tsum: bool = False):
        """Gives the sum of the variable over the domain"""
        if tsum:
            v = getattr(self.program, self.name)
            # if the domain has been mapped to but this is a time sum
            # we need to first map time
            # and then add it to an existing map at a lower domain
            v_sum = sigma(
                v(*domain.Ilist),
                domain.time.I,
            )
            return v_sum
        else:
            return self(*domain).V()

    def writecons_map(
        self,
        from_domain: Domain,
        to_domain: Domain = None,
        tsum: bool = False,
    ):
        """Scales up variable to a lower dimension"""
        if tsum:
            _name = f'{self.name}{to_domain.idxname}_tmap'
        else:
            _name = f'{self.name}{to_domain.idxname}_lmap'

        # check to see if the lower order domain has been upscaled to already
        if _name in self.maps:

            print(f'--- Mapping {self.aspect}: from {from_domain} to {to_domain}')

            cons_existing: C = getattr(self.program, _name)
            # update the existing constraint
            setattr(
                self.program,
                _name,
                cons_existing - self.give_sum(domain=from_domain, tsum=tsum),
            )

        else:

            print(
                f'--- Creating map to {to_domain}. Mapping {self.aspect}: from {from_domain} to {to_domain}'
            )

            v_lower = self(*to_domain).V()

            # write the constraint
            cons: C = v_lower == self.give_sum(domain=from_domain, tsum=tsum)

            cons.categorize('Map')

            if self.return_sum:
                # if only a sum is requested, don't set to the program
                return cons

            setattr(
                self.program,
                _name,
                cons,
            )

            self.aspect.constraints.append(_name)

        from_domain.update_cons(_name)

        # update the list of maps
        if not _name in self.maps:
            # keeping a list, allows updating constraints instead of making new

            self.maps.append(_name)

    def __call__(self, *index: X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
