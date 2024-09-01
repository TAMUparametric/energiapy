"""Conversion, Inventory, Freight
"""

from typing import TypeAlias

from ....components.commodity.resource import Resource
from ....components.temporal.mode import X

IsSngCnv: TypeAlias = dict[Resource, int | float]
IsMltCnv: TypeAlias = dict[X, IsSngCnv]
# Balance for Resource Conversion in Process
IsCnv: TypeAlias = IsSngCnv | IsMltCnv

# Balance for Inventory in Storage and Frieght in Transit
IsBlc: TypeAlias = Resource | IsSngCnv | IsMltCnv
