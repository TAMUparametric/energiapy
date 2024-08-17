""" energiapy.Location
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING

from ._spatial import _Spatial

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation


@dataclass
class Location(_Spatial):
    """Location where Process and Storage can reside"""

    label: str = field(default=None)

    def __post_init__(self):
        _Spatial.__post_init__(self)

    @property
    def processes(self):
        """Process Operations at the Location"""
        return self._system.processes

    @property
    def storages(self):
        """Storage Operations at the Location"""
        return self._system.storages

    def is_sink(self):
        """Tells whether the location is a sink"""
        if self in self._system.sinks:
            return True
        return False

    def is_source(self):
        """Tells whether the location is a source"""
        if self in self._system.sources:
            return True
        return False

    def find_links(self, location: IsLocation, print_link: bool = True) -> list:
        """Finds the links between two Locations

        Args:
            location (IsLocation): Location to find links with
            print_link (bool, optional): Whether the links are to be printed. Defaults to True.

        Returns:
            list: Provides the links between the locations
        """
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
        """Finds whether the Locations are connected
        Args:
            location (IsLocation): Location to verify Links with
            print_link (bool, optional): Whether to print the Links. Defaults to False.

        Returns:
            bool: True if Locations are connection
        """
        if self.find_links(location, print_link=print_link):
            return True
        print(self.find_links(location, print_link=print_link))
        return False
