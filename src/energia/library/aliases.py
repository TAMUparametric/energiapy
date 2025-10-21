"""Aliases for aspects"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..represent.model import Model


def _create_default_aliases():
    _default_aliases = {
        'capacity': [
            'size',
            'volume',
            'throughput',
            'potential',
            'output',
        ],
        'setup': [
            'install',
            'build',
            'construct',
            'commission',
        ],
        'dismantle': [
            'remove',
            'take_apart',
            'decommission',
            'disassemble',
            'break_down',
            'minimize',
        ],
        'operate': ['run', 'control'],
        'rampup': ['ramp_up', 'boost', 'accelerate', 'expand', 'scale_up'],
        'rampdown': [
            'reduce',
            'decrease',
            'slow_down',
            'scale_down',
        ],
        'produce': ['generate', 'manufacture', 'create', 'fabricate', 'yield'],
        'expend': ['useup', 'use_up', 'utilize'],
        'ship_in': ['import', 'deliver_to', 'bring_in', 'transport_in'],
        'ship_out': ['send', 'export', 'dispatch', 'deliver', 'transport_out'],
        'inventory': ['inv', 'stock', 'storage', 'reserve', 'buffer'],
        'consume': ['take', 'absorb', 'deplete', 'procure', 'obtain'],
        'release': [
            'free',
            'deploy',
            'liberate',
            'give_off',
            'exhale',
            'radiate',
            'demand',
        ],
        'buy': ['purchase', 'acquire', 'order'],
        'sell': ['market', 'retail'],
        'earn': ['gain', 'receive', 'collect', 'accrue', 'credit'],
        'spend': ['pay', 'expense', 'debit'],
        'emit': ['emission', 'expel', 'pollute', 'pollution'],
        'abate': ['diminish', 'lessen', 'curtail', 'sequester'],
        'benefit': ['advantage', 'profit', 'reward', 'value'],
        'detriment': ['damage', 'harm', 'disadvantage'],
        'dispose': ['discard', 'eliminate', 'get_rid_of', 'dump'],
        'use': ['employ', 'apply', 'exploit'],
    }

    # makes aliases for key_aspect by transferring
    # right_aspect aliases onto left_aspect aliases
    # right_aspect_left_aspect is also an aliases
    transfer = {
        'invsetup': ('inventory', 'setup'),
        'invcapacity': ('inventory', 'capacity'),
        'invdismantle': ('inventory', 'dismantle'),
    }

    for key_aspect, (right_aspect, left_aspect) in transfer.items():

        # add key aspect
        _default_aliases[key_aspect] = [f'{right_aspect}_{left_aspect}']

        for right_alias in _default_aliases[right_aspect]:
            for left_alias in _default_aliases[left_aspect]:
                _default_aliases[key_aspect].append(f"{right_alias}_{left_alias}")

    return _default_aliases


default_aliases = _create_default_aliases()


def aspect_aliases(m: Model):
    """Define aspect aliases for the model.


    :param m:  The model instance to define aliases for.
    :type m: Model

    .. note::

        I have added what I could think off. Update this for reconfiguration.
        For just adding aliases use:
        model.aliases('alias1', ..., to='aspect') or model.aspect.aliases('alias', ...)

    """

    for aspect, aliases in default_aliases.items():
        m.aliases(*aliases, to=aspect)


# FOR TESTING PURPOSES ONLY
# synonym_to_keys = {}
# for key, synonyms in default_aliases.items():
#     for syn in synonyms:
#         synonym_to_keys.setdefault(syn, []).append(key)

# # Print duplicates
# for syn, keys in synonym_to_keys.items():
#     if len(keys) > 1:
#         print(f"'{syn}' appears in multiple keys: {keys}")
