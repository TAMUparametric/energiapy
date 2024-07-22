from dataclasses import dataclass
from typing import List
from .resource import Resource  # Import the Resource class


@dataclass
class Storage:
    store: Resource
    requires: List[Resource]
