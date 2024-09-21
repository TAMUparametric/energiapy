"""SpatioTemporalInput, this is an intermediate class
"""

from dataclasses import dataclass, field


from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transit import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from .network import Network
from ..components.abstract.mode import X
from ..components.temporal.scale import Scale
from ..core._handy._dunders import _Dunders
from ..core.isalias.cmps.iscmp import IsDsp
from ..core.isalias.cmps.isdfn import IsDfn
from ..core.isalias.elms.isval import IsVal
from ..core.isalias.inps.isinp import IsBndInp, IsExtInp, IsIncInp, IsSptTmp
from ..core.nirop.errors import InputTypeError
from ..utils.dictionary import flatten


@dataclass
class Datum(_Dunders):
    """This containts the dictionary of input in a particular format

    This is made in Data Model Class, and is used in Scenario class

    The format is like this:
    * - optional


    {Spatial/Network: {Scale: {*Mode: {*Operational: {*Commodity: value}}}}}

    This ensures consistence in the input once provided to the Scenario class

    The Idx is also determined here and set as the key in the dictionary

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
        """Returns the Idx of the input"""
        return list(self.data.keys())

    @property
    def name(self):
        """Returns the Idx of the input"""
        return f'{self.attr}{self.data}'

    @property
    def by_position(self):
        """Returns the Idx of the input"""
        return dict(enumerate(list(self.data.values())))

    @property
    def registrar(self):
        """Registrar"""
        return self.component.registrar

    def update_data(self):
        """Updates the data
        Returns:
            dict: {Idx: value}
        """
        # Flatten the dictionary. Now the keys are tuples
        # {(Network/Spatial, Scale, ...): value}
        dict_iter = flatten(self.data)
        dict_upd = {}

        for key, val in dict_iter.items():
            disposition = {
                d: None
                for d in [
                    'ply',
                    'emn',
                    'csh',
                    'res',
                    'lnd',
                    'pro',
                    'stg',
                    'trn',
                    'loc',
                    'lnk',
                    'ntw',
                    'scl',
                    'mde',
                ]
            }
            if not isinstance(key, tuple):
                raise ValueError(
                    f'Something is wrong with the input at {self}. If providing dict, check structure'
                )

            # Check if a particular Component has been declared
            for cmp in key:
                if isinstance(cmp, Player):
                    disposition['ply'] = cmp
                if isinstance(cmp, Emission):
                    disposition['emn'] = cmp
                if isinstance(cmp, Cash):
                    disposition['csh'] = cmp
                if isinstance(cmp, Resource):
                    disposition['res'] = cmp
                if isinstance(cmp, Land):
                    disposition['lnd'] = cmp
                if isinstance(cmp, Process):
                    disposition['pro'] = cmp
                if isinstance(cmp, Storage):
                    disposition['stg'] = cmp
                if isinstance(cmp, Transit):
                    disposition['trn'] = cmp
                if isinstance(cmp, Location):
                    disposition['loc'] = cmp
                if isinstance(cmp, Linkage):
                    disposition['lnk'] = cmp
                if isinstance(cmp, Network):
                    disposition['ntw'] = cmp
                if isinstance(cmp, Scale):
                    disposition['scl'] = cmp
                if isinstance(cmp, X):
                    disposition['mde'] = cmp

            # fish will either return an existing index or create a new one
            index = self.registrar.fish(self.attr, disposition)

            # Check whether the input value type is appropriate
            # if not raises an InputTypeError
            self.check_type(val)
            dict_upd[index] = val

        # update the input with a dictionary {Idx: value}
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
                print(f'Idx with disposition {disp} not found')
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
            if not isinstance(value, (int, float, list, bool, tuple)):
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

            if not isinstance(value, (int, float, list, tuple, set)) or value is True:
                raise InputTypeError(
                    'Exact attrs can only take certain types',
                    self.component,
                    self.attr,
                    value,
                )

        # another check for whether the theta space extends to BigM is required
        # This is done in the Data Model Block
