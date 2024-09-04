"""Aliases for Program Parameter Elements 
"""

from typing import TypeAlias

from ....elements.parameters.balances.conversion import Conversion
from ....elements.parameters.balances.freight import Freight
from ....elements.parameters.balances.inventory import Inventory

from ....elements.parameters.boundprm import BoundPrm
from ....elements.parameters.exactprm import ExactPrm

IsCnv: TypeAlias = Conversion | Freight | Inventory

# All Parameters
IsPrm: TypeAlias = BoundPrm | ExactPrm
