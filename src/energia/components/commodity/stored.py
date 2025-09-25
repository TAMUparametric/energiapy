"""Resource in Storage"""

from dataclasses import dataclass
from .resource import Resource


@dataclass
class Stored(Resource):
    """Stored Resource"""

    def __post_init__(self):
        Resource.__post_init__(self)
