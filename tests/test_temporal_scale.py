from src.energiapy.components.temporal_scale import Temporal_scale

scales = Temporal_scale(discretization_list=list(range(4)))


def test_temporal_scale_list(scales):
    list_ = scales.list
    assert list_ == list(range(4))


def test_temporal_scale_scale(scales):
    scale = scales.scale
    assert scale == {i: list(range(i + 1)) for i in range(4)}
