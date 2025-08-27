"""Transport"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...modeling.parameters.conversion import Conv
from ._operation import _Operation

if TYPE_CHECKING:
    from ..commodity.resource import Resource
    from ..measure.unit import Unit
    from ..spatial.linkage import Link
    from ..spatial.location import Loc
    from ..temporal.lag import Lag
    from ..temporal.period import Period


@dataclass
class Transport(_Operation):
    """Exports Resource through Link
    basically, moves Resources between Locations
    """

    def __post_init__(self):
        _Operation.__post_init__(self)
        self.links: list[Link] = []

    def locate(self, *links: Link):
        """Locate the transport"""
        link_times = []

        links = sum(
            [[link, link.sib] if link.sib else [link] for link in list(links)], []
        )
        for link in links:

            # check if the transport has been capacitated at that link and time
            if not self in self.tree.capacitated_at or not link in [
                l_t[0] for l_t in self.tree.capacitated_at[self]
            ]:
                # if the process is not capacitated at the link and time
                print(
                    f'--- Assuming  {self} capacity is unbounded in ({link}, {self.horizon})'
                )
                # this is not a check, this generates a constraint
                _ = self.model.capacity(self, link, self.horizon) == True

            # now that the transport has been capacitated at the link
            # check if the transport has been operated at that link and time
            if not self in self.tree.operated_at or not link in [
                l_t[0] for l_t in self.tree.operated_at[self]
            ]:
                # if the transport is not operated at the link and time
                print(f'--- Assuming {self} is operated at ({link}, {self.horizon})')
                # this is not a check, this generates a constraint
                _ = self.model.operate(self, link, self.horizon) <= 1

            for d in self.model.operate.domains:
                if d.operation == self and d.space == link:
                    link_time = (link, d.time)
                    if link_time not in link_times:
                        link_times.append(link_time)

        self.writecons_conversion(link_times)

    def writecons_conversion(self, link_times: list[tuple[Link, Period]]):
        """Write the conversion constraints for the transport"""

        self.conv.balancer()

        def time_checker(res: Resource, link: Link, time: Period):
            """This checks if it is actually necessary
            to write conversion at denser temporal scales
            """

            # This checks whether some other aspect is defined at
            # a lower temporal scale
            if (
                self.model.grb[res][link.source][time]
                or self.model.grb[res][link.sink][time]
            ):
                return time
            else:
                return time.horizon

        for link_time in link_times:
            link, time = link_time
            # time = link_time[1]

            if link in self.links:
                continue

            for res, par in self.conversion.items():
                # set, the conversion on the resource
                setattr(res, self.name, self)
                # now there are two cases possible
                # the parameter (par) is positive or negative
                # if positive, the resource is expendd
                # if negative, the resource is produced
                # also, the par can be an number or a list of numbers

                # insitu resource (expended and ship_outed within the system)
                # do not initiate a grb so we need to run a check for that first
                if res in self.model.grb:
                    time = time_checker(res, link, time)
                    _insitu = False
                else:
                    # this implies that the grb needs to be initiated
                    # by declaring relevant variable
                    # the relevant variable will be unbounded
                    _insitu = True

                upd_expend, upd_ship, upd_operate = False, False, False

                if isinstance(par, (int | float)) and par < 0:
                    # condition: negative number
                    eff = -par

                    if self.lag:
                        rhs = self.model.expend(res, self, link.source, self.lag.of)
                        lhs = self.model.operate(self, link, self.lag.of)
                    else:
                        rhs = self.model.expend(res, link.source, self, time)
                        lhs = self.model.operate(self, link, time)

                    upd_expend, upd_operate = True, True

                elif isinstance(par, list) and par[0] < 0:
                    # condition: list with negative numbers
                    eff = [-i for i in par]

                    if self.lag:
                        rhs = self.model.expend(res, self, link.source, self.lag.of)
                        lhs = self.model.operate(self, link, self.lag.of)
                    else:
                        rhs = self.model.expend(res, self, link.source, time)
                        lhs = self.model.operate(self, link, time)
                    upd_expend, upd_operate = True, True

                else:
                    # condition: positive number or list of positive numbers
                    eff = par

                    if self.lag:
                        rhs_export = self.model.ship_out(
                            res, self, link.source, self.lag.of
                        )
                        rhs_import = self.model.ship_in(
                            res, self, link.sink, self.lag.of
                        )
                        lhs = self.model.operate(self, link, self.lag)
                    else:
                        rhs_export = self.model.ship_out(res, self, link, time)
                        rhs_import = self.model.ship_in(res, self, link, time)
                        lhs = self.model.operate(self, link, time)
                    upd_operate, upd_ship = True, True

                if len(time) > 1:
                    par = [par] * len(time)

                if _insitu:
                    # this initiates a grb
                    res.insitu = True
                    if upd_ship:
                        _ = rhs_export == True
                        _ = rhs_import == True
                    v_rhs_export = rhs_export.V(par, write_grb=True)
                    v_rhs_import = rhs_import.V(par, write_grb=True)

                if upd_ship:
                    if not _insitu:
                        v_rhs_export = rhs_export.V(par, write_grb=True)
                        v_rhs_import = rhs_import.V(par, write_grb=True)
                    v_lhs = lhs.V(par)
                    dom_export = rhs_export.domain
                    dom_import = rhs_import.domain

                    cons_name_export = (
                        f'operate_export_{res}_{self}_{link}_{time}_bal'.replace(
                            '-', '_'
                        )
                    )
                    cons_name_import = (
                        f'operate_import_{res}_{self}_{link}_{time}_bal'.replace(
                            '-', '_'
                        )
                    )

                    cons_export = v_lhs - eff * v_rhs_export == 0
                    cons_import = v_lhs - eff * v_rhs_import == 0

                    cons_export.categorize('Flow')
                    cons_import.categorize('Flow')

                    setattr(self.program, cons_name_export, cons_export)
                    setattr(self.program, cons_name_import, cons_import)
                    dom_export.update_cons(cons_name_export)
                    dom_import.update_cons(cons_name_import)

                    self.model.ship_out.constraints.append(cons_name_export)
                    self.model.ship_in.constraints.append(cons_name_import)
                    if upd_expend:
                        self.model.expend.constraints.append(cons_name_export)
                        self.model.expend.constraints.append(cons_name_import)
                    if upd_operate:
                        self.model.operate.constraints.append(cons_name_export)
                        self.model.operate.constraints.append(cons_name_import)

                else:

                    v_rhs = rhs.V(par)
                    v_lhs = lhs.V(par)

                    dom = rhs.domain

                    cons_name = f'operate_{res}_{self}_{link}_{time}_bal'.replace(
                        '-', '_'
                    )

                    setattr(self.program, cons_name, v_lhs - eff * v_rhs == 0)

                    dom.update_cons(cons_name)
                    if upd_expend:
                        self.model.expend.constraints.append(cons_name)
                    if upd_ship:
                        self.model.ship_out.constraints.append(cons_name)
                    if upd_operate:
                        self.model.operate.constraints.append(cons_name)
            self.links.append(link)

    def __call__(self, resource: Resource | Conv):
        """Conversion is called with a Resource to be converted"""
        if not self._conv:

            self.conv = Conv(process=self)
            self._conv = True
        return self.conv(resource)
