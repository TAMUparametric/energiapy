""" energiapy.Location
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING

from .._base._spttmp import _Spatial

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Location(_Spatial):
    """Location where Process and Storage can reside"""

    label: str = field(default=None)

    def __post_init__(self):
        _Spatial.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'locations'

    @property
    def processes(self):
        return self._system.processes

    @property
    def storages(self):
        return self._system.storages

    def is_sink(self):
        if self in self._system.sinks:
            return True
        return False

    def is_source(self):
        if self in self._system.sources:
            return True
        return False

    def find_links(self, location: IsLocation, print_link: bool = True) -> list:
        links = []
        for link in self._system.linkages:
            source, sink = False, False

            if is_(self, link.source) and is_(location, link.sink):
                source, sink = self, location

            if is_(self, link.sink) and is_(location, link.source):
                source, sink = location, self

            if source and sink:
                links.append(link)
                if print_link:
                    print(f'{source} is source and {sink} is sink in {link}')
                continue
        return links

    def is_connected(self, location: IsLocation, print_link: bool = False) -> bool:
        if self.find_links(location, print_link=print_link):
            return True
        print(self.find_links(location, print_link=print_link))
        return False
