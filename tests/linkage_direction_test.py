"""Verify the direction of a route in the spatial hierarchy."""

from energia import Linkage, Location, Model


def test_one_way_route_has_no_reverse_leaf():
    m = Model()
    m.source, m.sink = Location(), Location()
    m.route = Linkage(source=m.source, sink=m.sink)
    parent = m.route.isin

    assert m.route.rev() is None
    assert m.space.linkages == [m.route]
    assert [member for member in parent.all() if isinstance(member, Linkage)] == [
        m.route
    ]
