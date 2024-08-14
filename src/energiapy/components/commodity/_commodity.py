"""Base for Commodity Component"""

from dataclasses import dataclass

from .._base._defined import _Defined
from .._base._simple import _Simple
from .._base._nature import nature


@dataclass
class _Monetary(_Simple):
    """Asset Commodity Component"""

    def __post_init__(self):
        _Simple.__post_init__(self)


@dataclass
class _Traded(_Defined):
    """Trade Commodity Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return nature['resource']['bounds']

    @staticmethod
    def expenses():
        """Attrs that determine expenses of the component"""
        return nature['resource']['expenses']

    @staticmethod
    def emitted():
        """Attrs that determine emissions of the component"""
        return nature['resource']['emitted']

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds() + cls.expenses() + cls.emitted()

    @classmethod
    def _cnst_csh(cls):
        """Adds Cash when making consistent"""
        return cls.expenses()

    @classmethod
    def _cnst_lnd(cls):
        """Adds Land when making consistent"""
        return []

    @classmethod
    def _cnst_nstd(cls):
        """Is a nested input to be made consistent"""
        return cls.emitted()

    @classmethod
    def _cnst_nstd_csh(cls):
        """Is a nested input to be made consistent with Cash"""
        return []




@dataclass
class _Used(_Defined):
    """Commodities that are Used by Operations"""

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return nature['cmd_used']['bounds']

    @staticmethod
    def expenses():
        """Attrs that determine expenses of the component"""
        return nature['cmd_used']['expenses']

    @staticmethod
    def emitted():
        """Attrs that determine emissions of the component"""
        return nature['cmd_used']['emitted']

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds() + cls.expenses() + cls.emitted()

    @classmethod
    def _cnst_csh(cls):
        """Adds Cash when making consistent"""
        return cls.expenses()

    @classmethod
    def _cnst_lnd(cls):
        """Adds Land when making consistent"""
        return []

    @classmethod
    def _cnst_nstd(cls):
        """Is a nested input to be made consistent"""
        return cls.emitted()

    @classmethod
    def _cnst_nstd_csh(cls):
        """Is a nested input to be made consistent with Cash"""
        return []
