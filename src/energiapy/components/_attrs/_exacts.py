"""Exact input attributes for Components
"""

from dataclasses import dataclass, field, fields

from ...core.isalias.inps.isinp import IsExt, IsInc


# -------------Transact Exacts-------------


@dataclass
class _ResTscExacts:
    """Exact Transaction Inputs for Resources"""

    buy_spend: IsInc = field(default=None)
    buy_earn: IsInc = field(default=None)

    sell_earn: IsInc = field(default=None)
    sell_spend: IsInc = field(default=None)

    lose_spend: IsInc = field(default=None)
    recover_earn: IsInc = field(default=None)


@dataclass
class _UsdTscExacts:
    """Exact Transact Inputs for Land and Material (Used)"""

    use_spend: IsInc = field(default=None)
    use_earn: IsInc = field(default=None)

    dispose_spend: IsInc = field(default=None)
    dispose_earn: IsInc = field(default=None)


@dataclass
class _OpnTscExacts:
    """Exact Transact Inputs for Operational Components"""

    setup_spend: IsInc = field(default=None)
    setup_earn: IsInc = field(default=None)

    dismantle_spend: IsInc = field(default=None)
    dismantle_earn: IsInc = field(default=None)

    operate_spend: IsInc = field(default=None)
    operate_earn: IsInc = field(default=None)


@dataclass
class _TscExacts(_ResTscExacts, _UsdTscExacts, _OpnTscExacts):
    """Exact Transact Inputs for Components"""


# -------------Emission Exacts-------------


@dataclass
class _ResEmnExacts:
    """Exact Emission Inputs for Resources"""

    buy_emit: IsExt = field(default=None)
    buy_sequester: IsExt = field(default=None)

    sell_emit: IsExt = field(default=None)
    sell_sequester: IsExt = field(default=None)

    lose_emit: IsExt = field(default=None)
    recover_sequester: IsExt = field(default=None)


@dataclass
class _UsdEmnExacts:
    """Exact Emissions Inputs for Land and Material (Used)"""

    use_emit: IsExt = field(default=None)
    use_sequester: IsExt = field(default=None)

    dispose_emit: IsExt = field(default=None)
    dispose_sequester: IsExt = field(default=None)


@dataclass
class _OpnEmnExacts:
    """Exact Emission Inputs for Operational Components"""

    setup_emit: IsExt = field(default=None)
    setup_sequester: IsExt = field(default=None)

    dismantle_emit: IsExt = field(default=None)
    dismantle_sequester: IsExt = field(default=None)

    operate_emit: IsExt = field(default=None)
    operate_sequester: IsExt = field(default=None)


@dataclass
class _EmnExacts(_ResEmnExacts, _UsdEmnExacts, _OpnEmnExacts):
    """Exact Emission Inputs for Components"""


# -------------Use Exacts-------------


@dataclass
class _OpnUseExacts:
    """Exact Use Inputs for Operational Components"""

    setup_use: IsExt = field(default=None)

    dismantle_dispose: IsExt = field(default=None)


@dataclass
class _UseExacts(_OpnUseExacts):
    """Exact Use Inputs for Components"""


# -------------Loss Exacts-------------


@dataclass
class _OpnLseExacts:
    """Exact Loss Inputs for Operational Components"""

    operate_lose: IsExt = field(default=None)
    operate_recover: IsExt = field(default=None)


@dataclass
class _LseExacts(_OpnLseExacts):
    """Exact Loss Inputs for Components"""


# -------------Rate Exacts-------------


@dataclass
class _OpnRteExacts:
    """Exact Rate Inputs for Operational Components"""

    setup_time: IsExt = field(default=None)
    dismantle_time: IsExt = field(default=None)
    operate_time: IsExt = field(default=None)


@dataclass
class _RteExacts(_OpnRteExacts):
    """Exact Rate Inputs for Components"""


# -------------Component-wise Exacts-------------
# These are inherited by the Components


@dataclass
class _ResExacts(_ResTscExacts, _ResEmnExacts):
    """Exact Inputs for Resources imported by Process"""


@dataclass
class _UsdExacts(_UsdTscExacts, _UsdEmnExacts):
    """Exact Inputs for Land and Material (Used)"""


@dataclass
class _OpnExacts(
    _OpnTscExacts, _OpnEmnExacts, _OpnUseExacts, _OpnLseExacts, _OpnRteExacts
):
    """Exact Inputs for Operational Components"""


class _ExactAttrs:
    """Exact input attributes for Components"""

    @staticmethod
    def transactions():
        """Transacts"""
        return [f.name for f in fields(_TscExacts)]

    @staticmethod
    def emissions():
        """Emissions"""
        return [f.name for f in fields(_EmnExacts)]

    @staticmethod
    def uses():
        """Uses"""
        return [f.name for f in fields(_UseExacts)]

    @staticmethod
    def losses():
        """Losses"""
        return [f.name for f in fields(_LseExacts)]

    @staticmethod
    def rates():
        """Rates"""
        return [f.name for f in fields(_RteExacts)]

    @staticmethod
    def exacts():
        """Returns all Exact Inputs"""
        return sum(
            [
                [f.name for f in fields(ext)]
                for ext in [
                    _TscExacts,
                    _EmnExacts,
                    _UseExacts,
                    _LseExacts,
                ]
            ],
            [],
        )
