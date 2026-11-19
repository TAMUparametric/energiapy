"""Traverse the spatial hierarchy with local and cross-region linkages."""

import pytest

from energia import Linkage, Location, Model


@pytest.fixture
def network():
    m = Model()
    m.a, m.b, m.c = Location(), Location(), Location()
    m.west = Location(m.a, m.b)
    m.east = Location(m.c)
    m.country = Location(m.west, m.east)
    m.local = Linkage(source=m.a, sink=m.b)
    m.cross = Linkage(source=m.a, sink=m.c)
    assert m.local.isin is m.west
    assert m.cross.isin is m.country
    return m


def test_tree_keeps_local_and_cross_region_routes_as_leaves(network):
    m = network
    west = {m.a: {}, m.b: {}, m.local: {}}
    country = {m.west: west, m.east: {m.c: {}}, m.cross: {}}
    assert m.west.tree == west
    assert m.country.tree == country
    assert m.space.tree == {m.country: country}


def test_all_visits_each_location_and_registered_route_once(network):
    m = network
    assert m.local.isin is m.west
    assert m.cross.isin is m.country
    assert list(m.west.all()) == [m.a, m.b, m.local]
    assert list(m.country.all()) == [m.west, m.a, m.b, m.local, m.east, m.c, m.cross]


def test_route_is_a_leaf_in_an_implicit_network():
    m = Model()
    m.a, m.b = Location(), Location()
    m.route = Linkage(source=m.a, sink=m.b)
    parent = m.route.isin
    assert parent is m.network
    assert m.space.tree == {parent: {m.a: {}, m.b: {}, m.route: {}}}
    assert list(m.route.all()) == []
