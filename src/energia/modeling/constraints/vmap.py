"""Map"""

from __future__ import annotations

import time as keep_time
from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING

from gana import sigma

from ..._core._generator import _Generator

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ..indices.domain import Domain


@dataclass
class Map(_Generator):
    """Maps between domains"""

    return_sum: bool = False
    reporting: bool = False

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
        time, space = self.domain.periods, self.domain.space

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

        # DONOT map across all periods, only to from the densest which is given by .of
        if space in dispositions and time in dispositions[space]:
            # the aspect is already defined at this location
            # we need to check if it is defined for any periods sparser than time
            for sparser_period in sparser_periods:
                if sparser_period in dispositions[space] and is_(
                    sparser_period.of,
                    time,
                ):
                    # check if the aspect has been defined for a sparser period
                    # this creates a map from this domain to a sparser domain
                    self.writecons_map(
                        self.domain,
                        self.domain.change({"periods": sparser_period}),
                        tsum=True,
                    )

            for denser_period in denser_periods:
                if denser_period in dispositions[space] and is_(time.of, denser_period):

                    # create a new domain to map from
                    domain_from = self.domain.copy()
                    domain_from.periods = denser_period
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
                        self.domain.change({"loc": contained_loc}),
                        self.domain,
                    )

            if parent_location in dispositions:
                # check if the aspect has been defined for a parent location
                self.writecons_map(
                    self.domain,
                    self.domain.change({"loc": parent_location}),
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
                    and is_(d.periods, time)
                    and d.binds
                ]

                for domain in domains:
                    self.writecons_map(
                        domain,
                        self.domain,
                    )

            if (
                self.domain.primary in self.grb
                and self.aspect(self.domain.primary, space, time)
                in self.grb[self.domain.primary][space][time]
            ):
                # consider the case where overall consumption for water in some location and time is defined
                # now user defines consumption due to using cement during construction
                # we should have the constraint consume(water, goa, 2025) = consume(water, goa, 2025, use, cement)

                self.writecons_map(self.domain, self.domain.change({"binds": []}))

            if self.domain.modes:
                # if the variable is defined over modes
                # we need to map it to the same domain without modes

                if self.domain.modes.parent:
                    self.writecons_map(self.domain, self.domain.change({"modes": None}))
                else:
                    self.writecons_map(
                        self.domain,
                        self.domain.change({"modes": None}),
                        msum=True,
                    )

    @property
    def name(self) -> str:
        """Name of the constraint"""
        return self.aspect.name + "_map"

    @property
    def maps(self) -> list[str]:
        """List of domains that the aspect has been mapped to"""
        if self.reporting:
            return self.aspect.maps_report
        return self.aspect.maps

    def give_sum(
        self,
        domain: Domain,
        tsum: bool = False,
        msum: bool = False,
    ):
        """Gives the sum of the variable over the domain"""
        if tsum:
            v = getattr(self.program, self.aspect.name)
            # if the domain has been mapped to but this is a time sum
            # we need to first map time
            # and then add it to an existing map at a lower domain
            return sigma(
                v(*domain.Ilist),
                domain.time.I,
            )
        if msum:
            if self.reporting:
                v = getattr(self.program, f"x_{self.aspect.name}")
            else:
                v = getattr(self.program, self.aspect.name)
            # if the domain has been mapped to but this is a mode sum
            # we need to first map modes
            # and then add it to an existing map at a lower domain
            return sigma(
                v(*domain.Ilist),
                domain.modes.I,
            )

        else:
            # the copy is important since otherwise, the printing will take
            # the update index if the variable is mutated

            return getattr(self.program, self.aspect.name)(*domain.Ilist).copy()
            # return self(*domain).V()

    def writecons_map(
        self,
        from_domain: Domain,
        to_domain: Domain = None,
        tsum: bool = False,
        msum: bool = False,
    ):
        """Scales up variable to a lower dimension"""

        if to_domain not in self.maps:
            self.maps[to_domain] = []

            self.maps[to_domain].append(from_domain)
            exists = False

        else:
            # a map to the lower order domain has already been created
            exists = True

            if from_domain in self.maps[to_domain]:
                # map already exists
                return None

            if from_domain.modes:
                # modes need some additional checks
                # constraints could be written using parent modes or child modes
                # these checks avoid writing the same constraint twice
                # AVOIDS: v_t = v_t,m1 + v_t,m2 + v_t,m; v_t,m = v_t,m1 + v_t,m2
                # CORRECT: v_t = v_t,m; v_t,m = v_t,m1 + v_t,m2 OR v_t = v_t,m1 + v_t,m2

                if from_domain.modes.parent:
                    if (
                        from_domain.change({"modes": from_domain.modes.parent})
                        in self.maps[to_domain]
                    ):
                        # map already written using parent modes
                        # no need to write again
                        return None
                else:

                    if (
                        from_domain
                        in self.maps[to_domain.change({"binds": from_domain.binds})]
                    ):
                        # TODO: This check should not be necessary
                        # TODO: but it do be necessary, figure out and rectify this
                        # map already written using no modes
                        # no need to write again
                        return None

                    domain_w_childmodes = [
                        from_domain.change({"modes": mode})
                        for mode in from_domain.modes
                    ]

                    if any(dom in self.maps[to_domain] for dom in domain_w_childmodes):
                        # map already written using child modes
                        # no need to write again
                        return None

            self.maps[to_domain].append(from_domain)

        if self.reporting:
            var = self.aspect.reporting
        else:
            var = self.aspect

        # for t sum,
        if tsum:

            print(f"--- Mapping {var} across time from {from_domain} to {to_domain}")

            rhs = self.give_sum(domain=from_domain, tsum=tsum)

            _name = f"{var}{from_domain.idxname}_to_{to_domain.idxname}_tmap"

        elif msum:
            print(f"--- Mapping {var} across modes {from_domain} to {to_domain}")

            rhs = self.give_sum(domain=from_domain, msum=msum)
            # append the from_domain to the list of maps to avoid rewriting the constraint
            self.maps[to_domain].append(from_domain)

            _name = f"{var}{from_domain.idxname}_mmap"

        else:

            rhs = self.give_sum(domain=from_domain)

            if from_domain.modes:
                # for modes, stick to the msum convention
                # the name will take the parent modes name
                # NOTE: msum is not used when writing the constraint
                # for individual modes
                if from_domain.modes.parent:
                    _name = f"{var}{from_domain.change({'modes': from_domain.modes.parent}).idxname}_mmap"
                else:
                    _name = f"{var}{from_domain.idxname}_mmap"
            else:
                # if not tsum or msum. The map to a lower order domain is unique
                _name = f"{var}{to_domain.idxname}_map"

            if exists:
                # check to see if the lower order domain has been upscaled to already

                print(f"--- Mapping {var}: from {from_domain} to {to_domain}")

                start = keep_time.time()

                cons_existing: C = getattr(self.program, _name)
                # update the existing constraint
                setattr(
                    self.program,
                    _name,
                    cons_existing - self.give_sum(domain=from_domain),
                )

                end = keep_time.time()
                print(f"    Completed in {end-start} seconds")

                return None

        print(
            f"--- Creating map to {to_domain}. Mapping {var}: from {from_domain} to {to_domain}",
        )

        start = keep_time.time()
        if self.reporting:
            v_lower = self(*to_domain).X()
        else:
            v_lower = self(*to_domain).V()

        # write the constraint
        cons: C = v_lower == rhs

        if self.return_sum:
            # if only a sum is requested, don't set to the program
            return cons

        setattr(
            self.program,
            _name,
            cons,
        )
        cons.categorize("Mapping")
        end = keep_time.time()
        print(f"    Completed in {end-start} seconds")

        self.aspect.constraints.append(_name)

        from_domain.update_cons(_name)

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
