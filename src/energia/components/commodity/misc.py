from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, Self

# from ..operation.task import Task
from ...modeling.variables.default import Transact, Utilize

# from ..impact.categories import Eco
from .resource import Resource

if TYPE_CHECKING:
    from ..spatial.location import Location


@dataclass
class Emission(Resource):
    """Emission"""


@dataclass
class Material(Resource):
    """Materials are Resources, that are used to set up Operations"""


@dataclass
class Land(Resource):
    """Land used by Operations"""


@dataclass
class Package(Resource):
    """Package, discrete"""


@dataclass
class Human(Resource):
    """Human"""


@dataclass
class Mana(Resource):
    """Mana"""


@dataclass
class Etc(Resource):
    """Etc, used for resources that do not fit into the other categories"""
