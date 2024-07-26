"""General class with functions for handling aspects
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..funcs.aspect import aspectdicter, aspecter

if TYPE_CHECKING:
    from .. import IsValue


class HandleAspects:
    """Updates component attributes to aspects 
    """

    def make_aspect(self, attr_name: str, attr_value: IsValue):
        """Makes Aspect

        Args:
            attr_name (str): name of the attribute
            attr_value (IsValue): value of the attribute
        """
        aspecter(component=self, attr_name=attr_name, attr_value=attr_value)

    def make_aspectdict(self, attr_name: str):
        """Makes AspectDict

        Args:
            attr_name (str): name of the attribute
        """
        aspectdicter(component=self, attr_name=attr_name)
