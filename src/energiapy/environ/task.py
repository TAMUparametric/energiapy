"""Task, for Component attributes
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core._handy._printers import _EasyPrint
from ..core.isalias.elms.isvar import IsVar


@dataclass
class Task(_Dunders, _EasyPrint):
    """Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        attr (str): attr associated with Task
        var (IsVar): Task Variable
        var_i (IsVar): Incidental Task Variable
        ply (bool): Does this apply to Player?
        emn (bool): Does this apply to Emission?
        csh (bool): Does this apply to Cash?
        res (bool): Does this apply to Resource?
        mat (bool): Does this apply to Material?
        lnd (bool): Does this apply to Land?
        pro (bool): Does this apply to Process?
        stg (bool): Does this apply to Storage?
        trn (bool): Does this apply to Transit?
        loc (bool): Does this apply to Location?
        lnk (bool): Does this apply to Linkage?
        ntw (bool): Does this apply to Network?
        scl (bool): Does this apply to Scale?
        mde (bool): Does this apply to Mode?
        p (bool): Does it add to the Balance (plus sign)
        m (bool): Does it subtract from the Balance (minus sign)
    """

    attr: str = field(default=None)
    var: IsVar = field(default=None)
    var_i: IsVar = field(default=None)
    root: str = field(default=None)
    # Do not reorder these fields
    # I like to look at them in this order
    # Not sure why, but I do
    ply: bool = field(default=False)
    emn: bool = field(default=False)
    csh: bool = field(default=False)
    res: bool = field(default=False)
    mat: bool = field(default=False)
    lnd: bool = field(default=False)
    pro: bool = field(default=False)
    stg: bool = field(default=False)
    trn: bool = field(default=False)
    loc: bool = field(default=False)
    lnk: bool = field(default=False)
    ntw: bool = field(default=False)
    scl: bool = field(default=False)
    mde: bool = field(default=False)
    p: bool = field(default=False)
    m: bool = field(default=False)

    def __post_init__(self):
        self.name = f'Task|{self.attr}|'

        if self.p and self.m:
            raise ValueError('Task cannot be both plus and minus')

        if not (self.p or self.m):
            raise ValueError('Task must be either plus or minus')

        # Elements associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.indices = []

        