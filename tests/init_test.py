"""Test to check where all components can be initialized 

This will inherently check if there are any abstract methods have not been implemented
"""

import pytest

from src.energiapy.blocks.attr import Attr
from src.energiapy.blocks.data import Data, DataBlock
from src.energiapy.blocks.matrix import Matrix
from src.energiapy.blocks.model import Model
from src.energiapy.blocks.program import Program, ProgramBlock
from src.energiapy.blocks.spttmpinput import SptTmpInp
from src.energiapy.blocks.system import System
from src.energiapy.components.analytical.player import Player
from src.energiapy.components.commodity.cash import Cash
from src.energiapy.components.commodity.emission import Emission
from src.energiapy.components.commodity.land import Land
from src.energiapy.components.commodity.material import Material
from src.energiapy.components.commodity.resource import Resource
from src.energiapy.components.operational.process import Process
from src.energiapy.components.operational.storage import Storage
from src.energiapy.components.operational.transit import Transit
from src.energiapy.components.scope.horizon import Horizon
from src.energiapy.components.scope.network import Network
from src.energiapy.components.spatial.linkage import Linkage
from src.energiapy.components.spatial.location import Location
from src.energiapy.components.temporal.scale import Scale
from src.energiapy.model.scenario import Scenario


@pytest.fixture
def scenario():
    """Scenario"""
    scn = Scenario()
    scn.hrz = Horizon(discretizations=[1])
    scn.ntw = Network(locs=['loca', 'locb'])
    scn.lnk = Linkage(source=scn.loca, sink=scn.locb, bi=True)
    scn.ply = Player()
    scn.csh = Cash()
    scn.lnd = Land()
    scn.emn = Emission()
    scn.mat = Material()
    scn.res = Resource()
    scn.res_ = Resource()
    scn.pro = Process(conversion={scn.res: {scn.res_: -1}})
    scn.stg = Storage(inventory=scn.res)
    scn.trn = Transit(freight=scn.res)
    return scn


@pytest.fixture
def spttmpinp(scenario):
    """SptTmpInp"""
    return SptTmpInp()


@pytest.fixture
def datablock(scenario):
    """DataBlock"""
    return DataBlock()


@pytest.fixture
def programblock(scenario):
    """ProgramBlock"""
    return ProgramBlock()


def test_init(scenario):
    """Test to check if all components can be initialized"""
    assert isinstance(scenario.model, Model)
    assert isinstance(scenario.attr, Attr)
    assert isinstance(scenario.data, Data)
    assert isinstance(scenario.matrix, Matrix)
    assert isinstance(scenario.program, Program)
    assert isinstance(scenario.system, System)
    assert isinstance(scenario.horizon, Horizon)
    assert isinstance(scenario.hrz, Horizon)
    assert hasattr(scenario, 'horizon') is True
    assert hasattr(scenario, 't0') is True
    assert isinstance(scenario.t0, Scale)
    assert hasattr(scenario, 't1') is True
    assert isinstance(scenario.t1, Scale)
    assert isinstance(scenario.ntw, Network)
    assert hasattr(scenario, 'network') is True
    assert isinstance(scenario.network, Network)
    assert hasattr(scenario, 'loca') is True
    assert isinstance(scenario.loca, Location)
    assert hasattr(scenario, 'locb') is True
    assert isinstance(scenario.locb, Location)
    assert isinstance(scenario.lnk, Linkage)
    assert scenario.lnk.source == scenario.loca
    assert scenario.lnk.sink == scenario.locb
    assert scenario.lnk.bi is False
    assert hasattr(scenario, 'lnk_') is True
    assert isinstance(scenario.lnk_, Linkage)
    assert scenario.lnk_.source == scenario.locb
    assert scenario.lnk_.sink == scenario.loca
    assert scenario.lnk_.bi is False
    assert isinstance(scenario.ply, Player)
    assert isinstance(scenario.csh, Cash)
    assert hasattr(scenario, 'cash') is True
    assert isinstance(scenario.cash, Cash)
    assert isinstance(scenario.emn, Emission)
    assert isinstance(scenario.lnd, Land)
    assert hasattr(scenario, 'land') is True
    assert isinstance(scenario.land, Land)
    assert isinstance(scenario.mat, Material)
    assert isinstance(scenario.res, Resource)
    assert isinstance(scenario.pro, Process)
    assert isinstance(scenario.stg, Storage)
    assert isinstance(scenario.trn, Transit)


# def test_ind_init(spttmpinp, programblock, datablock):
#     assert isinstance(spttmpinp, SptTmpInp(dict_input={}))
#     assert isinstance(programblock, ProgramBlock)
#     assert isinstance(datablock, DataBlock)
