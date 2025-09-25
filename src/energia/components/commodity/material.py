"""Material"""

from dataclasses import dataclass
from .resource import Resource


@dataclass
class Material(Resource):
    """Materials are Resources, that are used to set up Operations"""

    def __post_init__(self):
        Resource.__post_init__(self)
