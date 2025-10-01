from energia.modeling.variables.control import Control
from operator import is_
import pytest

from energia import Model, Resource


@pytest.fixture
def m():
    m = Model()
    m.r = Resource()
    m.attr_map['d'] = {'gg': {'type': Control}}
    m.attr_map['b'] = {'gg': {'type': Control}}
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

    