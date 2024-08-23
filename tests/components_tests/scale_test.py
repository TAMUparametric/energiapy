from tests.test_fixtures import single_level_scale, multi_two_level_scale, multi_three_level_scale, scheduling_single_level_scale
from src.energiapy.components.temporal_scale import Scale, ProblemType


def test_scales_defaulting(single_level_scale, multi_two_level_scale, multi_three_level_scale, scheduling_single_level_scale):
    assert (single_level_scale.scale_levels == 1)
    assert (single_level_scale.design_scale == 0)
    assert (single_level_scale.scheduling_scale == 0)
    assert (single_level_scale.problem_type ==
            ProblemType.DESIGN_AND_SCHEDULING)
    assert (single_level_scale.scale_type == Scale.SINGLE)

    assert (scheduling_single_level_scale.scale_levels == 1)
    assert (scheduling_single_level_scale.design_scale is None)
    assert (scheduling_single_level_scale.scheduling_scale == 0)
    assert (scheduling_single_level_scale.problem_type == ProblemType.SCHEDULING)

    assert (multi_two_level_scale.scale_levels == 2)
    assert (multi_two_level_scale.design_scale == 0)
    assert (multi_two_level_scale.scheduling_scale == 1)
    assert (multi_two_level_scale.problem_type ==
            ProblemType.DESIGN_AND_SCHEDULING)
    assert (multi_two_level_scale.scale_type == Scale.MULTI)

    assert (multi_three_level_scale.scale_levels == 3)
    assert (multi_three_level_scale.design_scale == 0)
    assert (multi_three_level_scale.scheduling_scale == 2)
