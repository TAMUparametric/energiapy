"""Conversion, Inventory, Freight
"""

from ....components.commodity.resource import Resource
from ....components.scope.temporal.mode import X

type IsSngCnv = dict[Resource, int | float]
type IsMltCnv = dict[X, IsSngCnv]
# Balance for Resource Conversion in Process
type IsCnv = IsSngCnv | IsMltCnv

# Balance for Inventory in Storage and Frieght in Transit
type IsBlc = Resource | IsSngCnv | IsMltCnv
