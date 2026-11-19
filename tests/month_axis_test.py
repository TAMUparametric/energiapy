"""Month labels for hourly, daily, and monthly axes."""

import pytest
from matplotlib.figure import Figure

from energia.utils.plot import axis_formatter


@pytest.mark.parametrize(
    ("periods", "february", "december"),
    [(12, 1, 11), (365, 31, 334), (8760, 744, 8016)],
)
def test_month_ticks_match_the_time_resolution(periods, february, december):
    axes = Figure().subplots()
    assert axis_formatter(axes, range(periods)) is axes
    ticks = axes.get_xticks().tolist()
    assert len(ticks) == 12
    assert (ticks[0], ticks[1], ticks[-1]) == (0, february, december)
    assert [label.get_text() for label in axes.get_xticklabels()] == (
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    )


@pytest.mark.parametrize(("periods", "labels"), [(24, "M"), (12, "custom")])
def test_custom_or_unsupported_axes_keep_their_ticks(periods, labels):
    axes = Figure().subplots()
    axes.set_xticks([1, 4], labels=["start", "end"])
    axis_formatter(axes, range(periods), axis_labels=labels)
    assert axes.get_xticks().tolist() == [1, 4]
    assert [label.get_text() for label in axes.get_xticklabels()] == ["start", "end"]
