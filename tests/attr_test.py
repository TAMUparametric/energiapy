from energia.modeling.variables.control import Control
from operator import is_
import pytest

from energia import Model, Resource, Transport, Process, Storage
from energia.library.aliases import default_aliases


@pytest.fixture
def m():
    m = Model()
    m.r = Resource()

    m.Recipe(
        'gg',
        Control,
        primary_type=(Process, Transport),
        label='Operational Capacity',
        latex='cap',
    )
    m.alias('d', 'b', of='gg')
    return m


def test_attr(m):
    with pytest.raises(AttributeError):
        # attribute does not exist
        m.r.xyz

    with pytest.raises(AttributeError):
        # default exists in model
        if hasattr(m, 'default'):
            # but should not be accessible through resource
            m.r.default

    # returns the same object
    # through the alias
    assert is_(m.d, m.d)

    # gg should have been created by now
    # check if the attribute is created
    assert is_(m.d, m.gg)

    # returns the same object
    # through different aliases
    assert is_(m.d, m.b)

    m.cookbook


def test_aliases():

    all_aliases = []
    for alias_list in default_aliases.values():
        all_aliases.extend(alias_list)

    all_aliases_set = set(all_aliases)

    # check all aliases are unique
    assert len(all_aliases) == len(all_aliases_set)

    assert not (set(default_aliases) & all_aliases_set)


def test_error(m):

    with pytest.raises(AttributeError):
        m.rr = Resource(fail_attr=4)

    with pytest.raises(AttributeError):
        m.rrr = Resource(capacity=10)

    r = Resource()
    with pytest.raises(AttributeError):
        r.program

    with pytest.raises(TypeError):
        m.rrrr = Resource(capex=5)


def test_storage_attrs():
    # storage pulls some attrs from constituents:

    m = Model()
    m.r = Resource()
    m.s = Storage()
    m.s(m.r) == 1

    for attr in ["capacity", "setup", "dismantle"]:
        assert getattr(m.s, attr) == getattr(m.resources[-1], "inv" + attr)

    for attr in ["inventory"]:
        assert getattr(m.s, attr) == getattr(m.resources[-1], attr)
