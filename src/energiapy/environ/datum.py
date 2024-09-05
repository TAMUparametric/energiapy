"""SpatioTemporalInput, this is an intermediate class
"""

from dataclasses import dataclass, field

from pandas import DataFrame

from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transit import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.spatial.network import Network
from ..components.temporal.incidental import I
from ..components.temporal.mode import X
from ..components.temporal.scale import Scale
from ..core._handy._dunders import _Dunders
from ..core.isalias.cmps.iscmp import IsDsp
from ..core.isalias.cmps.isdfn import IsDfn
from ..core.isalias.elms.isval import IsVal
from ..core.isalias.inps.isinp import IsBndInp, IsExtInp, IsIncInp, IsSptTmp
from ..core.nirop.errors import InputTypeError
from ..elements.disposition.index import Index
from ..utils.dictionary import flatten


@dataclass
class Datum(_Dunders):
    """This containts the dictionary of input in a particular format

    This is made in Data Model Class, and is used in Scenario class

    The format is like this:
    * - optional


    {Spatial/Network: {Scale: {*Mode: {*Operational: {*Commodity: value}}}}}

    This ensures consistence in the input once provided to the Scenario class

    The Index is also determined here and set as the key in the dictionary

    Attributes:
        attr (str): The attribute of the input
        data (IsSptTmp): Consistent spatiotemporal input dictionary
        component (IsDfn): The component to which the input belongs

    """

    attr: str = field(default=None)
    data: IsSptTmp = field(default=None)
    component: IsDfn = field(default=None)

    def __post_init__(self):
        # The original dictionary input
        # keep it because some operations birth processes
        # processes need the og input
        self.og_input = self.data
        self.update_data()

    @property
    def indices(self):
        """Returns the Index of the input"""
        return list(self.data.keys())

    @property
    def name(self):
        """Returns the Index of the input"""
        return f'{self.attr}{self.data}'

    @property
    def by_position(self):
        """Returns the Index of the input"""
        return {i: val for i, val in enumerate(list(self.data.values()))}

    def update_data(self):
        """Updates the data
        Returns:
            dict: {Index: value}
        """
        # Flatten the dictionary. Now the keys are tuples
        # {(Network/Spatial, Scale, ...): value}
        dict_iter = flatten(self.data)
        dict_upd = {}

        for key, val in dict_iter.items():

            ply, emn, csh, res, mat, lnd, pro, stg, trn, loc, lnk, ntw, scl, mde = (
                None for _ in range(14)
            )

            if not isinstance(key, tuple):
                raise ValueError(
                    f'Something is wrong with the input at {self}. If providing dict, check structure'
                )
            # Check if a particular Component has been declared
            for cmp in key:
                if isinstance(cmp, Player):
                    ply = cmp
                if isinstance(cmp, Emission):
                    emn = cmp
                if isinstance(cmp, Cash):
                    csh = cmp
                if isinstance(cmp, Resource):
                    res = cmp
                if isinstance(cmp, Material):
                    mat = cmp
                if isinstance(cmp, Land):
                    lnd = cmp
                if isinstance(cmp, Process):
                    pro = cmp
                if isinstance(cmp, Storage):
                    stg = cmp
                if isinstance(cmp, Transit):
                    trn = cmp
                if isinstance(cmp, Location):
                    loc = cmp
                if isinstance(cmp, Linkage):
                    lnk = cmp
                if isinstance(cmp, Network):
                    ntw = cmp
                if isinstance(cmp, Scale):
                    scl = cmp
                if isinstance(cmp, X):
                    mde = cmp

            disp = Index(
                ply=ply,
                emn=emn,
                csh=csh,
                res=res,
                mat=mat,
                lnd=lnd,
                pro=pro,
                stg=stg,
                trn=trn,
                loc=loc,
                lnk=lnk,
                ntw=ntw,
                scl=scl,
                mde=mde,
            )

            # Check whether the input value type is appropriate
            # if not raises an InputTypeError
            self.check_type(val)
            dict_upd[disp] = val

        # update the input with a dictionary {Index: value}
        self.data = dict_upd

    def get(self, n: IsDsp | int | None = None) -> IsVal:
        """Gets the value of the input at the index
        You can give the index or the position
        or nothing, to get some guidelines

        Args:
            n (Tuple[IsDsp], int, None]): disposition (tuple) or position (int) to get the value. Default is None

        Returns:
            IsVal: The value at the index

        Examples:
            Declare some Scenario, Horizon, and Network
            >>> s = Scenario()
            >>> s.hrz = Horizon(birth=[2, 12])
            >>> s.ntw = Network(['madgaon', 'ponje'])
            Here we are setting the cash spend at madgaon for t2
            i.e. Do not spend more than 50 money in any time period in Scale t2 at Location madgaon
            >>> s.csh = Cash(spend = {s.madgaon: {s.t2: [50]}})
            You can get the value by index
            >>> s.csh.spend.get((s.csh, s.madgaon, s.t2))
            or by position
            >>> s.csh.spend.get(0)
            Irrespective you will get:
            >>> [0[csh, madgaon, t2], 50[csh, madgaon, t2]]
            For guidelines, just use this
            >>> s.csh.spend.get()
        """

        def siren_position():
            print()
            print('For position, use this as a guideline:')
            print(f'{self.by_position}')
            print('Or just use the by_position property')

        def siren_index():
            print()
            print('For index, use this as a guideline')
            print(f'{self.data}')

        def siren_help():
            print()
            print('Use help() for examples')

        if n is None:
            print('No index or position provided')
            siren_position()
            siren_index()
            siren_help()

        if isinstance(n, tuple):

            disp = n
            if not disp in [idx.disposition for idx in self.indices]:
                print(f'Index with disposition {disp} not found')
                siren_index()
                siren_help()

            for idx, value in self.data.items():
                if idx.disposition == disp:
                    return value

        if isinstance(n, int):

            position = n
            if position > len(self.indices):
                print(f'Position {position} out of range')
                siren_position()
                siren_help()

            else:
                disp = self.indices[position]
                return self.data[disp]

    def values(self):
        """Returns the values of the input"""
        return list(self.data.values())

    def check_type(self, value: IsBndInp | IsExtInp | IsIncInp):
        """Verifies if the input type is correct

        Args:
            value (IsBndInp | IsExtInp | IsIncInp): The user input value

        Raises:
            InputTypeError: If the value is not of the correct type
        """

        # values cannot be False, if something is not needed
        # just dont set it
        if value is False:
            raise InputTypeError(
                'Value cannot be False',
                self.component,
                self.attr,
                value,
            )

        if (
            self.attr
            in self.component.taskmaster.bounds()
            + self.component.taskmaster.boundbounds()
        ):
            # Bound inputs cannot be:
            # sets - used only in the special case when there is an incidental parameter
            if not isinstance(value, (int, float, list, bool, DataFrame, tuple)):
                raise InputTypeError(
                    'Bound attrs can only take certain types',
                    self.component,
                    self.attr,
                    value,
                )

        if self.attr in self.component.taskmaster.exacts():
            # Exact inputs cannot be:
            # lists - used for upper and lower bounds
            # bool (True) - used for BigM

            if (
                not isinstance(value, (int, float, DataFrame, tuple, set, I))
                or value is True
            ):
                raise InputTypeError(
                    'Exact attrs can only take certain types',
                    self.component,
                    self.attr,
                    value,
                )

        # another check for whether the theta space extends to BigM is required
        # This is done in the Data Model Block
