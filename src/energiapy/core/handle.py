"""General class with functions for handling aspects
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..funcs.input.aspect import aspecter, aspectshareder

if TYPE_CHECKING:
    from ..type.alias import IsValue


class HandleAspect:
    """Updates component attributes to aspects 
    """

    def make_aspect(self, attr_name: str, attr_value: IsValue):
        """Makes Aspect

        Args:
            attr_name (str): name of the attribute
            attr_value (IsValue): value of the attribute
        """
        aspecter(component=self, attr_name=attr_name, attr_value=attr_value)

    def make_aspectshared(self, attr_name: str):
        """Makes AspectShared

        Args:
            attr_name (str): name of the attribute
        """
        aspectshareder(component=self, attr_name=attr_name)
