from dataclasses import dataclass


@dataclass(kw_only=True)
class Linkage:
    name: str
