from tests.test_fixtures import temporal_scale


def test_temporal_scale_levels(temporal_scale):
    assert (temporal_scale.scale_levels == 2)


def test_temporal_scale_scale(temporal_scale):
    assert (temporal_scale.scale == {0: [0], 1: [0, 1, 2, 3]})


def test_temporal_scale_list(temporal_scale):
    assert (temporal_scale.list == [0, 1])


def test_temporal_scale_scale_iter(temporal_scale):
    assert (temporal_scale.scale_iter(0) == [(0,)])
    assert (temporal_scale.scale_iter(1) == [(0, 0), (0, 1), (0, 2), (0, 3)])


