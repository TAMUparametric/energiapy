"""Map"""

from __future__ import annotations

import time as keep_time
from dataclasses import dataclass
from functools import cached_property
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
    reporting: bool = False

    def __post_init__(self):

        _Generator.__post_init__(self)

        if self.domain.lag:
            return

        time, space = self.domain.periods, self.domain.space
        denser_periods, sparser_periods = self.model.time.split(time)
        dispositions = self.dispositions[self.aspect][self.domain.primary]

        if space not in dispositions or time not in dispositions[space]:
            return

        # --- Time mapping ---
        self._map_across_time(
            dispositions, space, time, sparser_periods, denser_periods
        )

        # --- Space mapping ---
        contained_locs, parent_loc = self.model.space.split(space)
        self._map_across_space(dispositions, contained_locs, parent_loc, time)

        # --- Bind mapping ---
        self._map_across_binds(dispositions, space, time)

        # --- Mode mapping ---
        self._map_across_modes()

    # ---------------------------------------------------------------------- #
    # Subfunctions for readability
    # ---------------------------------------------------------------------- #
    def _map_across_time(
        self, dispositions, space, time, sparser_periods, denser_periods
    ):
        for sp in sparser_periods:
            if sp in dispositions[space] and is_(sp.of, time):
                self.writecons_map(
                    self.domain, self.domain.change({"periods": sp}), tsum=True
                )

        for dp in denser_periods:
            if dp in dispositions[space] and is_(time.of, dp):
                binds_dict = dispositions[space][dp]
                binds = [
                    aspect(component)
                    for aspect, comp_dict in binds_dict.items()
                    for component in comp_dict
                ]
                from_domain = self.domain.copy()
                from_domain.periods, from_domain.binds = dp, binds
                self.writecons_map(from_domain, self.domain, tsum=True)

    def _map_across_space(self, dispositions, contained_locs, parent_loc, time):
        for location in contained_locs:
            if location not in dispositions or time not in dispositions[location]:
                continue
            binds = dispositions[location][time]
            if not binds:
                self.writecons_map(
                    self.domain.change({"location": location}), self.domain
                )
            else:
                new_binds = [k(list(v)[0]) for k, v in binds.items()]
                self.writecons_map(
                    self.domain.change({"location": location, "binds": new_binds}),
                    self.domain,
                )

        if parent_loc in dispositions:
            self.writecons_map(
                self.domain, self.domain.change({"location": parent_loc})
            )

    def _map_across_binds(self, dispositions, space, time):
        if self.domain.binds or not dispositions[space][time]:
            return
        domains = [
            d
            for d in self.aspect.domains
            if is_(d.primary, self.domain.primary)
            and is_(d.space, space)
            and is_(d.periods, time)
            and d.binds
        ]
        for domain in domains:
            self.writecons_map(domain, self.domain)

    def _map_across_modes(self):
        if not self.domain.modes:
            return
        if self.domain.modes.parent:
            self.writecons_map(self.domain, self.domain.change({"modes": None}))
        else:
            self.writecons_map(
                self.domain, self.domain.change({"modes": None}), msum=True
            )

    # ---------------------------------------------------------------------- #
    # Helper functions
    # ---------------------------------------------------------------------- #
    @cached_property
    def name(self) -> str:
        return f"{self.aspect.name}_map"

    @cached_property
    def maps(self) -> dict[str, list[Domain]]:
        return self.aspect.maps_report if self.reporting else self.aspect.maps

    def give_sum(self, domain: Domain, tsum=False, msum=False):
        varname = (
            f"x_{self.aspect.name}" if (msum and self.reporting) else self.aspect.name
        )
        v = getattr(self.program, varname)

        if tsum:
            return sigma(v(*domain.Ilist), domain.time.I)
        if msum:
            return sigma(v(*domain.Ilist), domain.modes.I)
        return v(*domain.Ilist).copy()

    # ---------------------------------------------------------------------- #
    # Constraint writing
    # ---------------------------------------------------------------------- #
    def writecons_map(
        self, from_domain: Domain, to_domain: Domain, tsum=False, msum=False
    ):
        if to_domain not in self.maps:
            self.maps[to_domain] = [from_domain]
            exists = False
        elif from_domain in self.maps[to_domain]:
            return
        else:
            self.maps[to_domain].append(from_domain)
            exists = True

        var = self.aspect.reporting if self.reporting else self.aspect

        rhs = self.give_sum(from_domain, tsum, msum)

        if tsum:
            cname = f"{var}{from_domain.idxname}_to_{to_domain.idxname}_tmap"
        elif msum:
            # follow original behavior which used from_domain idxname for per-mode naming
            cname = f"{var}{from_domain.idxname}_mmap"
        elif from_domain.modes:
            if from_domain.modes.parent:
                cname = f"{var}{from_domain.change({'modes': from_domain.modes.parent}).idxname}_mmap"
            else:
                cname = f"{var}{from_domain.idxname}_mmap"

        else:
            cname = f"{var}{to_domain.idxname}_map"

        print(f"--- Mapping {var}: {from_domain} → {to_domain}")
        start = keep_time.time()

        v_lower = self(*to_domain).X() if self.reporting else self(*to_domain).V()

        if not tsum and not msum and exists:
            cons_existing: C = getattr(self.program, cname)
            setattr(self.program, cname, cons_existing - rhs)

        else:
            cons = v_lower == rhs
            setattr(self.program, cname, cons)
            cons.categorize("Mapping")

        end = keep_time.time()
        print(f"    Completed in {end-start:.3f}s")
        self.aspect.constraints.append(cname)
        from_domain.update_cons(cname)

    def __call__(self, *index: _X):
        return self.aspect(*index)


# from __future__ import annotations

# import time as keep_time
# from dataclasses import dataclass
# from functools import cached_property
# from operator import is_
# from typing import TYPE_CHECKING

# from gana import sigma

# from ..._core._generator import _Generator

# if TYPE_CHECKING:
#     from gana.sets.constraint import C

#     from ..._core._x import _X
#     from ..indices.domain import Domain


# @dataclass
# class Map(_Generator):
#     """Maps between domains

#     :param aspect: Aspect to which the constraint is applied.
#     :type aspect: Aspect
#     :param domain: Domain over which the aspect is defined.
#     :type domain: Domain
#     :param reporting: If True, the map is for a reporting variable.
#     :type reporting: bool
#     """

#     reporting: bool = False

#     def __post_init__(self):

#         _Generator.__post_init__(self)

#         # if the variable is being defined for the first time, do not bother with the rest
#         # Also note that if a variable already exists then a new is not created
#         # thus map_domain is not called in Bind.V()
#         # Essentially, the domain being added is always new!

#         # 1. a new domain is being added to a new disposition
#         # e.g.:
#         #   (water, dam, goa, year) with disposition ['resource', 'operation', 'space', 'time'] exists
#         #   (dam, goa, q) with disposition ['operation', 'space', 'time'] is added

#         # # 2. a new domain is being added to an existing disposition
#         # # e.g.:
#         # #   (dam, goa, year) with disposition ['operation', 'space', 'time'] exists
#         # #   (dam, goa, q) with disposition ['operation', 'space', 'time'] is added
#         # #   The variable will need to be mapped across 'time

#         # mapping happens between:
#         # 1. sparser time to denser time in same space
#         # 2. contained location to parent location
#         # 3. (sparser time, contained location) to (denser time, parent location)
#         # you cant map at the same level
#         # consider the State Goa, with two towns Madgaon and Ponje
#         # Goa with Maharashtra, make up India (for the purpose of modeling)
#         # Aspect from Goa can be mapped to India
#         # Goa does not need to be mapped to Maharashtra
#         # Madgaon and Ponje are both mapped to Just Goa
#         # note that .alsohas() checks at lower levels
#         # the operators <, > wont work since they will add any space a higher order
#         # this will lead to adding twice. India = Goa + Madgaon + Ponje (WRONG)
#         # We scale only one level up

#         if self.domain.lag:
#             return

#         # this is the disposition of the variable to be mapped
#         # through time and space
#         time, space = self.domain.periods, self.domain.space

#         # these are periods denser and sparser than the current domain
#         denser_periods, sparser_periods = self.model.time.split(time)

#         # these are spaces contained in location and parent location to which this location belongs

#         # this gives all the dispositions at which the aspect has been defined
#         dispositions = self.dispositions[self.aspect][self.domain.primary]

#         # DONOT map across all periods, only to from the densest which is given by .of
#         if space in dispositions and time in dispositions[space]:
#             # the aspect is already defined at this location
#             # we need to check if it is defined for any periods sparser than time
#             for sparser_period in sparser_periods:
#                 if sparser_period in dispositions[space] and is_(
#                     sparser_period.of,
#                     time,
#                 ):
#                     # check if the aspect has been defined for a sparser period
#                     # this creates a map from this domain to a sparser domain
#                     self.writecons_map(
#                         self.domain,
#                         self.domain.change({"periods": sparser_period}),
#                         tsum=True,
#                     )

#             for denser_period in denser_periods:
#                 if denser_period in dispositions[space] and is_(time.of, denser_period):

#                     # create a new domain to map from
#                     domain_from = self.domain.copy()
#                     domain_from.periods = denser_period
#                     binds_dict = dispositions[space][denser_period]
#                     binds = []
#                     # TODO - check this
#                     # here I am re creating Bind objects
#                     # from the dict of the form {aspect: {component: {aspect: {component: {...}}}}}
#                     # there has to be a way to avoid this
#                     # I make a list  of bounds as such [aspect(component), aspect(component), ...]
#                     iter_dict = binds_dict
#                     for aspect, component_dict in iter_dict.items():
#                         for component in component_dict:
#                             binds.append(aspect(component))
#                             iter_dict = iter_dict[aspect][component]

#                     domain_from.binds = binds
#                     domain_to = self.domain.copy()

#                     # check if the aspect has been defined for a denser period
#                     self.writecons_map(
#                         domain_from,
#                         # self.domain.change({'period': denser_period}),
#                         domain_to,
#                         tsum=True,
#                     )

#             contained_locations, parent_location = self.model.space.split(space)

#             # TODO: spatial mapping is too convoluted
#             for contained_loc in contained_locations:
#                 if contained_loc in dispositions:
#                     if time in dispositions[contained_loc]:
#                         # check if the aspect has been defined for a contained location
#                         if not dispositions[contained_loc][time]:
#                             self.writecons_map(
#                                 self.domain.change({"location": contained_loc}),
#                                 self.domain,
#                             )
#                         else:

#                             if not self.domain.binds:

#                                 self.writecons_map(
#                                     self.domain.change(
#                                         {
#                                             "location": contained_loc,
#                                             "binds": [
#                                                 k(list(v)[0])
#                                                 for k, v in dispositions[contained_loc][
#                                                     time
#                                                 ].items()
#                                             ],
#                                         }
#                                     ),
#                                     self.domain,
#                                 )

#             if parent_location in dispositions:
#                 # check if the aspect has been defined for a parent location
#                 self.writecons_map(
#                     self.domain,
#                     self.domain.change({"location": parent_location}),
#                 )

#             if not self.domain.binds and dispositions[space][time]:
#                 # if the current variable being declared has no binds
#                 # but the aspect has already been defined at this location and time with binds
#                 # there is a need to map from the defined binds to no binds
#                 # get list of domains of the aspect
#                 domains = [
#                     d
#                     for d in self.aspect.domains
#                     if is_(d.primary, self.domain.primary)
#                     and is_(d.space, space)
#                     and is_(d.periods, time)
#                     and d.binds
#                 ]

#                 for domain in domains:
#                     self.writecons_map(
#                         domain,
#                         self.domain,
#                     )

#             if (
#                 self.domain.primary in self.grb
#                 and self.aspect(self.domain.primary, space, time)
#                 in self.grb[self.domain.primary][space][time]
#             ):
#                 # consider the case where overall consumption for water in some location and time is defined
#                 # now user defines consumption due to using cement during construction
#                 # we should have the constraint consume(water, goa, 2025) = consume(water, goa, 2025, use, cement)

#                 self.writecons_map(self.domain, self.domain.change({"binds": []}))

#             if self.domain.modes:
#                 # if the variable is defined over modes
#                 # we need to map it to the same domain without modes

#                 if self.domain.modes.parent:
#                     self.writecons_map(self.domain, self.domain.change({"modes": None}))
#                 else:
#                     self.writecons_map(
#                         self.domain,
#                         self.domain.change({"modes": None}),
#                         msum=True,
#                     )

#     @cached_property
#     def name(self) -> str:
#         """Name of the constraint"""
#         return self.aspect.name + "_map"

#     @cached_property
#     def maps(self) -> dict[str, list[Domain]]:
#         """List of domains that the aspect has been mapped to"""
#         if self.reporting:
#             return self.aspect.maps_report
#         return self.aspect.maps

#     def give_sum(
#         self,
#         domain: Domain,
#         tsum: bool = False,
#         msum: bool = False,
#     ):
#         """Gives the sum of the variable over the domain"""
#         if tsum:
#             v = getattr(self.program, self.aspect.name)
#             # if the domain has been mapped to but this is a time sum
#             # we need to first map time
#             # and then add it to an existing map at a lower domain
#             return sigma(
#                 v(*domain.Ilist),
#                 domain.time.I,
#             )
#         if msum:
#             if self.reporting:
#                 v = getattr(self.program, f"x_{self.aspect.name}")
#             else:
#                 v = getattr(self.program, self.aspect.name)
#             # if the domain has been mapped to but this is a mode sum
#             # we need to first map modes
#             # and then add it to an existing map at a lower domain
#             return sigma(
#                 v(*domain.Ilist),
#                 domain.modes.I,
#             )

#         else:
#             # the copy is important since otherwise, the printing will take
#             # the update index if the variable is mutated

#             return getattr(self.program, self.aspect.name)(*domain.Ilist).copy()
#             # return self(*domain).V()

#     def writecons_map(
#         self,
#         from_domain: Domain,
#         to_domain: Domain = None,
#         tsum: bool = False,
#         msum: bool = False,
#     ):
#         """Scales up variable to a lower dimension"""

#         if to_domain not in self.maps:
#             self.maps[to_domain] = []

#             self.maps[to_domain].append(from_domain)
#             exists = False

#         else:
#             # a map to the lower order domain has already been created
#             exists = True

#             if from_domain in self.maps[to_domain]:
#                 # map already exists
#                 return None

#             if from_domain.modes:
#                 # modes need some additional checks
#                 # constraints could be written using parent modes or child modes
#                 # these checks avoid writing the same constraint twice
#                 # AVOIDS: v_t = v_t,m1 + v_t,m2 + v_t,m; v_t,m = v_t,m1 + v_t,m2
#                 # CORRECT: v_t = v_t,m; v_t,m = v_t,m1 + v_t,m2 OR v_t = v_t,m1 + v_t,m2

#                 if from_domain.modes.parent:
#                     if (
#                         from_domain.change({"modes": from_domain.modes.parent})
#                         in self.maps[to_domain]
#                     ):
#                         # map already written using parent modes
#                         # no need to write again
#                         return None
#                 else:

#                     if (
#                         from_domain
#                         in self.maps[to_domain.change({"binds": from_domain.binds})]
#                     ):
#                         # TODO: This check should not be necessary
#                         # TODO: but it do be necessary, figure out and rectify this
#                         # map already written using no modes
#                         # no need to write again
#                         return None

#                     domain_w_childmodes = [
#                         from_domain.change({"modes": mode})
#                         for mode in from_domain.modes
#                     ]

#                     if any(dom in self.maps[to_domain] for dom in domain_w_childmodes):
#                         # map already written using child modes
#                         # no need to write again
#                         return None

#             self.maps[to_domain].append(from_domain)

#         if self.reporting:
#             var = self.aspect.reporting
#         else:
#             var = self.aspect

#         # for t sum,
#         if tsum:

#             print(f"--- Mapping {var} across time from {from_domain} to {to_domain}")

#             rhs = self.give_sum(domain=from_domain, tsum=tsum)

#             _name = f"{var}{from_domain.idxname}_to_{to_domain.idxname}_tmap"

#         elif msum:
#             print(f"--- Mapping {var} across modes {from_domain} to {to_domain}")

#             rhs = self.give_sum(domain=from_domain, msum=msum)
#             # append the from_domain to the list of maps to avoid rewriting the constraint
#             self.maps[to_domain].append(from_domain)

#             _name = f"{var}{from_domain.idxname}_mmap"

#         else:

#             rhs = self.give_sum(domain=from_domain)

#             if from_domain.modes:
#                 # for modes, stick to the msum convention
#                 # the name will take the parent modes name
#                 # NOTE: msum is not used when writing the constraint
#                 # for individual modes
#                 if from_domain.modes.parent:
#                     _name = f"{var}{from_domain.change({'modes': from_domain.modes.parent}).idxname}_mmap"
#                 else:
#                     _name = f"{var}{from_domain.idxname}_mmap"
#             else:
#                 # if not tsum or msum. The map to a lower order domain is unique
#                 _name = f"{var}{to_domain.idxname}_map"

#             if exists:
#                 # check to see if the lower order domain has been upscaled to already

#                 print(f"--- Mapping {var}: from {from_domain} to {to_domain}")

#                 start = keep_time.time()

#                 cons_existing: C = getattr(self.program, _name)
#                 # update the existing constraint
#                 setattr(
#                     self.program,
#                     _name,
#                     cons_existing - self.give_sum(domain=from_domain),
#                 )

#                 end = keep_time.time()
#                 print(f"    Completed in {end-start} seconds")

#                 return None

#         print(
#             f"--- Creating map to {to_domain}. Mapping {var}: from {from_domain} to {to_domain}",
#         )

#         start = keep_time.time()
#         if self.reporting:
#             v_lower = self(*to_domain).X()
#         else:
#             v_lower = self(*to_domain).V()

#         # write the constraint
#         cons: C = v_lower == rhs

#         setattr(
#             self.program,
#             _name,
#             cons,
#         )
#         cons.categorize("Mapping")
#         end = keep_time.time()
#         print(f"    Completed in {end-start} seconds")

#         self.aspect.constraints.append(_name)

#         from_domain.update_cons(_name)

#     def __call__(self, *index: _X):
#         """Returns the variable for the aspect at the given index"""
#         return self.aspect(*index)
