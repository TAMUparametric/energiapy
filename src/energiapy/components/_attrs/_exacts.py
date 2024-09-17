"""Exact input attributes for Components
"""

from dataclasses import dataclass, field, fields

from ...core.isalias.inps.isinp import IsExt, IsInc

# -------------Exacts with Transact as parent-------------


@dataclass
class _TradeTransact:
    """Transactions due to Trade of Resource"""

    buy_spend: IsInc = field(default=None)
    buy_earn: IsInc = field(default=None)

    sell_earn: IsInc = field(default=None)
    sell_spend: IsInc = field(default=None)


@dataclass
class _TradeEmit:
    """Emissions due to Trade of Resource"""

    buy_emit: IsExt = field(default=None)
    buy_sequester: IsExt = field(default=None)

    sell_emit: IsExt = field(default=None)
    sell_sequester: IsExt = field(default=None)

    lose_emit: IsExt = field(default=None)
    recover_sequester: IsExt = field(default=None)


# -------------Exacts with Use as parent-------------


@dataclass
class _UseTransact:
    """Transactions due to Use of Resource"""

    use_spend: IsInc = field(default=None)
    use_earn: IsInc = field(default=None)

    dispose_spend: IsInc = field(default=None)
    dispose_earn: IsInc = field(default=None)


@dataclass
class _UseEmit:
    """Emissions due to Use of Resource"""

    use_emit: IsExt = field(default=None)
    use_sequester: IsExt = field(default=None)

    dispose_emit: IsExt = field(default=None)
    dispose_sequester: IsExt = field(default=None)


# -------------Exacts with Setup as parent-------------


@dataclass
class _SetupTransact:
    """Transactions due to Construction of Operation"""

    setup_spend: IsInc = field(default=None)
    setup_earn: IsInc = field(default=None)
    dismantle_spend: IsInc = field(default=None)
    dismantle_earn: IsInc = field(default=None)


@dataclass
class _SetupEmit:
    """Emissions due to Construction of Operation"""

    setup_emit: IsExt = field(default=None)
    dismantle_emit: IsExt = field(default=None)

    setup_sequester: IsExt = field(default=None)
    dismantle_sequester: IsExt = field(default=None)


@dataclass
class _SetupUse:
    """Use due to Construction of Operation"""

    setup_use: IsExt = field(default=None)
    dismantle_dispose: IsExt = field(default=None)


# -------------Exacts with Operate as parent-------------


@dataclass
class _OperateTrade:
    """Trades due to Operation of Operation"""

    consume: IsInc = field(default=None)
    discharge: IsInc = field(default=None)


@dataclass
class _OperateTransact:
    """Transactions due to Operation of Operation"""

    operate_spend: IsInc = field(default=None)
    operate_earn: IsInc = field(default=None)


@dataclass
class _OperateLose:
    """Loss due to Operation of Operation"""

    operate_lose: IsExt = field(default=None)
    operate_recover: IsExt = field(default=None)


class _ExactAttrs:
    """Exact input attributes for Components"""

    @staticmethod
    def trades():
        """Trades"""
        return [f.name for f in fields(_OperateTrade)]

    @staticmethod
    def transacts():
        """Transacts"""
        return [
            f.name
            for f in fields(_TradeTransact)
            + fields(_UseTransact)
            + fields(_SetupTransact)
            + fields(_OperateTransact)
        ]

    @staticmethod
    def emits():
        """Emissions"""
        return [
            f.name for f in fields(_TradeEmit) + fields(_UseEmit) + fields(_SetupEmit)
        ]

    @staticmethod
    def uses():
        """Uses"""
        return [f.name for f in fields(_SetupUse)]

    @staticmethod
    def losses():
        """Losses"""
        return [f.name for f in fields(_OperateLose)]

    @staticmethod
    def exacts():
        """Returns all Exact Inputs"""
        return [
            f.name
            for f in fields(_OperateTrade)
            + fields(_OperateTransact)
            + fields(_OperateLose)
            + fields(_SetupUse)
            + fields(_SetupTransact)
            + fields(_SetupEmit)
            + fields(_TradeTransact)
            + fields(_TradeEmit)
            + fields(_UseTransact)
            + fields(_UseEmit)
        ]
