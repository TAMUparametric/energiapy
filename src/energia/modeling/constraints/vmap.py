"""Map"""

from __future__ import annotations

import time as keep_time
from functools import cached_property
from operator import is_
from typing import TYPE_CHECKING

from gana import sigma

from ...utils.decorators import timer

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect

import logging

logger = logging.getLogger("energia")


class Map:
    """
    Maps between domains

    :param aspect: Aspect to which the constraint is applied.
    :type aspect: Aspect
    :param domain: Domain over which the aspect is defined.
    :type domain: Domain
    :param reporting: If True, the map is for a reporting variable.
    :type reporting: bool
    :param label: Label for the constraint. Defaults to "".
    :type label: str
    """

    def __init__(
        self, aspect: Aspect, domain: Domain, reporting=False, label: str = ""
    ):

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

        self.aspect = aspect
        self.domain = domain
        self.reporting = reporting
        self.label = label

        if self.domain.lag:
            return

        self.model = self.aspect.model
        self.dispositions = self.model.dispositions
        self.program = self.model.program

        # this is the disposition of the variable to be mapped
        # through time and space
        self.time, self.space = self.domain.periods, self.domain.space

        # these are spaces contained in location and parent location to which this location belongs
        # this gives all the dispositions at which the aspect has been defined
        self.dispositions = self.dispositions[self.aspect][self.domain.primary]

        if (
            self.space not in self.dispositions
            or self.time not in self.dispositions[self.space]
        ):
            return

        # Time mapping ---

        # these are periods denser and sparser than the current domain
        self._map_across_time()

        # Space mapping ---
        self._map_across_space()
        # Bind mapping ---
        self._map_across_binds()

        # Mode mapping ---
        self._map_across_modes()

    @cached_property
    def name(self) -> str:
        return f"{self.aspect.name}_map"

    @cached_property
    def maps(self) -> dict[Domain, list[Domain]]:
        return self.aspect.maps_report if self.reporting else self.aspect.maps

    # -------------------------------------------------------------------#
    # Helper functions
    # -------------------------------------------------------------------#

    def _map_across_time(self):
        """
        Maps across time


        :param sparser_periods: Periods sparser than the domain period
        :type sparser_periods: list[Periods]
        :param denser_periods: Periods denser than the domain period
        :type denser_periods: list[Periods]
        """
        denser_periods, sparser_periods = self.model.time.split(self.time)

        for sp in sparser_periods:
            # check if the aspect has been defined for a sparser period
            # this creates a map from this domain to a sparser domain
            if sp in self.dispositions[self.space] and is_(sp.of, self.time):
                self.writecons_map(
                    self.domain, self.domain.change({"periods": sp}), tsum=True
                )

        for dp in denser_periods:
            if dp in self.dispositions[self.space] and is_(self.time.of, dp):
                binds_dict = self.dispositions[self.space][dp]
                # TODO - check this
                # here I am re creating Bind objects
                # from the dict of the form {aspect: {component: {aspect: {component: {...}}}}}
                # there has to be a way to avoid this
                # I make a list  of bounds as such [aspect(component), aspect(component), ...]
                samples = [
                    aspect(component)
                    for aspect, comp_dict in binds_dict.items()
                    for component in comp_dict
                ]
                from_domain = self.domain.copy()
                from_domain.periods, from_domain.samples = dp, samples
                self.writecons_map(from_domain, self.domain, tsum=True)

    def _map_across_space(self):
        """
        Maps across space

        :param contained_locs: Locations contained in the domain location
        :type contained_locs: list[Space]
        :param parent_loc: Parent location of the domain location
        :type parent_loc: Space | None
        :param time: Time at which the domain is defined
        :type time: Periods
        """
        parent_loc = self.domain.location.isin

        if parent_loc:
            if (
                parent_loc not in self.dispositions
                or self.time not in self.dispositions[parent_loc]
            ):
                return
            self.writecons_map(
                self.domain,
                self.domain.change({"location": parent_loc}),
            )

        # contained_locs, parent_loc = self.model.space.split(self.space)
        # for location in contained_locs:
        #     if location not in dispositions or time not in dispositions[location]:
        #         # the aspect is already defined at this location
        #         # we need to check if it is defined for any periods sparser than time
        #         continue
        #     # samples = dispositions[location][time]
        #     # if not samples:

        #     logger.info('asdadada', location, self.domain)
        #     self.writecons_map(self.domain.change({"location": location}), self.domain)
        # else:
        #     new_binds = [k(list(v)[0]) for k, v in samples.items()]
        #     logger.info('aaaa', self.aspect, new_binds, self.domain)
        #     # consider the case where overall consumption for water in some location and time is defined
        #     # now user defines consumption due to using cement during construction
        #     # we should have the constraint consume(water, goa, 2025) = consume(water, goa, 2025, use, cement)
        #     # in that case, samples is just []
        #     self.writecons_map(
        #         self.domain.change({"location": location, "samples": new_binds}),
        #         self.domain,
        #     )

        # if parent_loc in dispositions:

        #     self.writecons_map(
        #         self.domain, self.domain.change({"location": parent_loc})
        #     )

    def _map_across_binds(self):
        if self.domain.samples or not self.dispositions[self.space][self.time]:
            return
        # if the current variable being declared has no samples
        # but the aspect has already been defined at this location and time with samples
        # there is a need to map from the defined samples to no samples
        # get list of domains of the aspect

        domains = [
            d
            for d in self.aspect.domains
            if is_(d.primary, self.domain.primary)
            and is_(d.space, self.space)
            and is_(d.periods, self.time)
            and d.samples
        ]
        for domain in domains:
            self.writecons_map(domain, self.domain)

    def _map_across_modes(self):
        # modes need some additional checks
        # constraints could be written using parent modes or child modes
        # these checks avoid writing the same constraint twice
        # AVOIDS: v_t = v_t,m1 + v_t,m2 + v_t,m; v_t,m = v_t,m1 + v_t,m2
        # CORRECT: v_t = v_t,m; v_t,m = v_t,m1 + v_t,m2 OR v_t = v_t,m1 + v_t,m2
        if not self.domain.modes:
            return
        if self.domain.modes.parent:
            self.writecons_map(self.domain, self.domain.change({"modes": None}))
        else:
            self.writecons_map(
                self.domain, self.domain.change({"modes": None}), msum=True
            )

    def _give_cname(
        self,
        var,
        from_domain,
        to_domain,
        tsum: bool = False,
        msum: bool = False,
    ) -> str:
        """Return canonical map constraint name based on domain relationship and aggregation type."""

        if tsum:
            return f"{var}{from_domain.idxname}_to_{to_domain.idxname}_tmap"

        if msum:
            # Original behavior: use from_domain idxname for per-mode naming
            return f"{var}{from_domain.idxname}_mmap"

        if from_domain.modes:
            if from_domain.modes.parent:
                parent_domain = from_domain.change({"modes": from_domain.modes.parent})
                return f"{var}{parent_domain.idxname}_mmap"
            return f"{var}{from_domain.idxname}_mmap"

        return f"{var}{to_domain.idxname}_map"

    def _give_sum(self, domain: Domain, tsum=False, msum=False):
        """Gives the sum of the variable over the domain"""
        varname = (
            f"x_{self.aspect.name}" if (msum and self.reporting) else self.aspect.name
        )
        v = getattr(self.program, varname)

        if tsum:
            # if the domain has been mapped to but this is a time sum
            # we need to first map time
            # and then add it to an existing map at a lower domain
            return sigma(v(*domain.Ilist), domain.time.I)
        if msum:
            # if the domain has been mapped to but this is a mode sum
            # we need to first map modes
            # and then add it to an existing map at a lower domain
            return sigma(v(*domain.Ilist), domain.modes.I)
        # the copy is important since otherwise, the printing will take
        # the update index if the variable is mutated

        return v(*domain.Ilist).copy()

    # -------------------------------------------------------------------#
    # Constraint writing
    # -------------------------------------------------------------------#

    @timer(logger, kind='map')
    def writecons_map(
        self, from_domain: Domain, to_domain: Domain, tsum=False, msum=False
    ):
        """Scales up variable to a lower dimension"""

        if to_domain not in self.maps:
            self.maps[to_domain] = [from_domain]
            exists = False
        elif from_domain in self.maps[to_domain]:
            return
        else:
            self.maps[to_domain].append(from_domain)
            exists = True

        var = self.aspect.reporting if self.reporting else self.aspect

        rhs = self._give_sum(from_domain, tsum, msum)

        cname = self._give_cname(var, from_domain, to_domain, tsum, msum)

        v_lower = self(*to_domain).X() if self.reporting else self(*to_domain).V()

        if not tsum and not msum and exists:
            cons_existing: C = getattr(self.program, cname)
            setattr(self.program, cname, cons_existing - rhs)

        else:
            cons = v_lower == rhs
            setattr(self.program, cname, cons)
            cons.categorize("Mapping")

        if cname not in self.aspect.constraints:
            self.aspect.constraints.append(cname)

        from_domain.update_cons(cname)

        return (self.aspect, from_domain, to_domain)

    def __call__(self, *index: _X):
        return self.aspect(*index)
