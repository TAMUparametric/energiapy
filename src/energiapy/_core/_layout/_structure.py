"""Allowed disposition structures 
"""

from collections import OrderedDict
from itertools import product
from operator import is_, is_not
from typing import List, Union

from .._nirop._error import CacodcarError


def make_structures(
    emn: bool = False,
    csh: bool = False,
    cmd: str = None,
    opn: Union[List[str], str] = None,
    spt: Union[List[str], str] = None,
    opn_strict: bool = False,
    cmd_strict: bool = True,
) -> List[List[str]]:
    """Makes a list of allowed disposition structures"""

    # Order is important, follows that of disposition
    # '' is put when something is optional

    struct_dict = OrderedDict()

    # Players can be provided to any disposition, but are always optional
    struct_dict['ply'] = ['', 'ply']

    # Cash abd Emissions are optional
    if emn:
        struct_dict['emn'] = ['emn']
    else:
        struct_dict['emn'] = ['']

    if csh:
        struct_dict['csh'] = ['csh']
    else:
        struct_dict['csh'] = ['']

    # Commodities and Operations are optional, there are three types and mulitple can be provided
    if cmd:
        if not isinstance(cmd, list):
            cmd = [cmd]
        struct_dict['cmd'] = []

        for i in cmd:
            if is_(i, 'res') or is_(i, 'mat') or is_(i, 'lnd'):
                struct_dict['cmd'].append(i)

    else:
        struct_dict['cmd'] = ['']

    if opn:
        if not isinstance(opn, list):
            opn = [opn]

        struct_dict['opn'] = []

        for i in opn:
            if is_(i, 'pro') or is_(i, 'stg') or is_(i, 'trn'):
                struct_dict['opn'].append(i)
    else:
        struct_dict['opn'] = ['']

    # If both Commodity and Operation are give, disposition can have both or either one
    if cmd and opn:

        if not opn_strict:
            struct_dict['opn'].append('')

        if not cmd_strict:
            struct_dict['cmd'].append('')

    # Spatial has to be provided, multiple can be provided
    if spt:
        if not isinstance(spt, list):
            spt = [spt]

        struct_dict['spt'] = []

        for i in spt:
            if is_(i, 'loc') or is_(i, 'lnk') or is_(i, 'ntw'):
                struct_dict['spt'].append(i)
    else:
        raise CacodcarError('No spatial disposition provided')

    # Scale has to be provided
    struct_dict['scl'] = ['scl']

    structures_upd = []

    iter_list = [struct_dict[i] for i in struct_dict]

    for i in product(*iter_list):

        # pro and stg cannot be located in lnks
        if 'pro' in i or 'stg' in i:
            if 'lnk' in i:
                continue
        # trn cannot be located in locs
        if 'trn' in i and 'loc' in i:
            continue

        structures_upd.append(i)

    return [[j for j in i if is_not(j, '')] for i in structures_upd]
