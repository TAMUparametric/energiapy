"""Aliases for Program Variable Elements 
"""

from typing import TypeAlias
from ....elements.variables.boundboundvar import BoundBoundVar
from ....elements.variables.boundvar import BoundVar
from ....elements.variables.exactvar import ExactVar


IsVar: TypeAlias = BoundBoundVar | BoundVar | ExactVar
