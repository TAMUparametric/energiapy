"""Dummy components, used as place holders
These are replaced or dumped based on certain rules 
and situations
"""

from enum import Enum, auto


class _Dummy(Enum):
    """Dummy Enum for dummy values
    These are corrected later as per some rules

    t - usually defaults to the root scale (t0, ph)
    n - defaults to Network if bound, applied across all locations if exact
    x - is removed in the end
    r - is replaced with the actual resource (ResourceStg or ResourceTrn)
    """

    T = auto()
    """Dummy Temporal"""
    N = auto()
    """Dummy Spatial"""
    X = auto()
    """Dummy Mode"""
    R = auto()
    """Dummy Resource"""
