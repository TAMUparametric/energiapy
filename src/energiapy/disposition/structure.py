"""Allowed disposition structures for a Variable 
A check is run while declaring (see _Variable)
"""

from collections import OrderedDict
from itertools import product
from typing import List, Union

from .._core._nirop._error import CacodcarError


def make_structures(
    emn_strict: bool = False,
    csh_strict: bool = False,
    opn_strict: bool = False,
    cmd_strict: bool = True,
    ply_strict: bool = False,
    mde: bool = False,
    cmd: Union[List[str], str] = None,
    opn: Union[List[str], str] = None,
    spt: Union[List[str], str] = None,
) -> List[List[str]]:
    """Makes a list of allowed disposition structures

    E.g. ['res', 'pro', 'loc', 'scl'] is a valid structure for
    a Variable that can be declared for a Resource being used by a Process at some Location

    Infact some spatial (ntw, loc, lnk) and a scale is compulsory
    The function returns a list of all structures that are allowed



    Args:
        emn_strict (bool): If variable has to be declared strictly for Emission
        csh_strict (bool): If variable has to be declared strictly for Cash
        opn_strict (bool): If variable has to be declared strictly for Operation
        cmd_strict (bool): If variable has to be declared strictly for Commodity
        ply_strict (bool): If variable has to be declared strictly for Player
        mde (bool): If True, the Variable can have Modes
        cmd (Union[List[str], str]): What commodities can this variable be declare for
        opn (Union[List[str], str]): What operations can this variable be declared for
        spt (Union[List[str], str]): What spatial disposition can this variable be declared for

    Returns:
        List[List[str]]: List of allowed disposition structures.
    """

    # Order is important, follows that of disposition
    # '' is put when something is optional
    # The '' is cleared at the end
    # This is a dumb way of doing it, but it works
    # If you have something better, let me know

    struct_dict = OrderedDict()

    # Players can be provided to any disposition, but are always optional
    if ply_strict:
        struct_dict['ply'] = ['ply']
    else:
        struct_dict['ply'] = ['', 'ply']

    # Cash and Emissions are optional
    if emn_strict:
        struct_dict['emn'] = ['emn']
    else:
        struct_dict['emn'] = ['']

    if csh_strict:
        struct_dict['csh'] = ['csh']
    else:
        struct_dict['csh'] = ['']

    # Commodities and Operations are optional, there are three types and mulitple can be provided
    if cmd:
        if not isinstance(cmd, list):
            cmd = [cmd]
        struct_dict['cmd'] = []

        for i in cmd:
            if i == 'res' or i == 'mat' or i == 'lnd' or i == 'csh':
                struct_dict['cmd'].append(i)

    else:
        struct_dict['cmd'] = ['']

    if opn:
        if not isinstance(opn, list):
            opn = [opn]

        struct_dict['opn'] = []

        for i in opn:
            if i == 'pro' or i == 'stg' or i == 'trn':
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
            if i == 'loc' or i == 'lnk' or i == 'ntw':
                struct_dict['spt'].append(i)
    else:
        raise CacodcarError('No spatial disposition provided')

    # Scale has to be provided
    struct_dict['scl'] = ['scl']

    if mde:
        struct_dict['mde'] = ['', 'mde']
    else:
        struct_dict['mde'] = ['']

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

    return [[j for j in i if j != ''] for i in structures_upd]
