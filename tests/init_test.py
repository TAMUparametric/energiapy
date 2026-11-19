import pytest

from energia import *
from energia.components.commodities.misc import Package, Human, Mana, Etc
from energia.modeling.variables.control import Control
from energia.modeling.variables.states import State


def test_init():
    m0 = Model(init=[misc_units])
    m1 = Model(init=[time_units, si_units, misc_units, env_indicators, currencies])
    m2 = Model()
    m2(time_units, si_units, misc_units, env_indicators, currencies)
    m = Model('mm')
    m.r = Resource()
    m.soc = Social()
    m.econ = Economic()
    m.env = Environ()
    m.lnd = Land()
    m.emm = Emission()
    m.pac = Package()
    m.hum = Human()
    m.mana = Mana()
    m.etc = Etc()
    m.pp = Player()
    m.pro = Process()
    m.sto = Storage()
    m.trn = Transport()
    m.r.release >= 20
    m.r.consume <= 40
    m.pro.capacity == 30
    m.l1 = Location()
    m.l2 = Location()
    m.Link(m.l0, m.l1)
    m.ll = Linkage(m.l1, m.l2)

    assert m.indicators == [m.env, m.soc, m.econ]
    assert m.operations == [m.pro, m.sto.charge, m.sto.discharge, m.sto, m.trn]
    assert m.aspects == [m.capacity, m.release, m.consume]

    with pytest.raises(AttributeError):
        m.r = Resource()

    with pytest.raises(AttributeError):
        m.r = Process()

    with pytest.raises(ValueError):
        m.Link(m.l1, m.l2)

    assert m.A == [[-1.0, 0, 0], [0, 1, 0], [-1.0, 1, 0], [0, 0, 1]]

    assert m.__repr__() == "mm"

    assert m.__hash__() == hash("mm")


def test_redefine_recipe_preserves_child_kinds_and_signs():
    model = Model()
    model.Recipe("custom", State, Resource, add="up", sub="down", sub_kind=State)
    assert model.cookbook["up"].kind is State
    model.Recipe(
        "custom", State, Resource, add="up", sub="down",
        add_kind=Control, sub_kind=State,
    )
    assert model.cookbook["up"].kind is Control
    assert model.cookbook["up"].ispos
    assert model.cookbook["down"].kind is State
    assert not model.cookbook["down"].ispos
