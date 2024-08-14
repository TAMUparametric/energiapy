"""If the component is simple, it should inherit from this class"""

from dataclasses import dataclass

from ._defined import _Defined


@dataclass
class _Simple(_Defined):

    def __post_init__(self):
        _Defined.__post_init__(self)

    @classmethod
    def _cnst_csh(cls):
        """Adds Cash when making consistent"""
        return []

    @classmethod
    def _cnst_lnd(cls):
        """Adds Land when making consistent"""
        return []

    @classmethod
    def _cnst_nstd(cls):
        """Is a nested input to be made consistent"""
        return []

    @classmethod
    def _cnst_nstd_csh(cls):
        """Is a nested input to be made consistent with Cash"""
        return []
