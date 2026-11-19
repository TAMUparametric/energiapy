"""Paths and levels in nested model trees."""

from energia.utils.dictionary import merge_tree_levels, tupler


def test_merge_tree_levels_groups_sites_with_matching_time_scales():
    tree = {
        "north": {"steam": {"hour": {}}},
        "south": {"steam": {"hour": {}}},
        "east": {"steam": {"day": {}}},
    }
    assert merge_tree_levels(tree) == [
        [["north", "south"], "east"],
        ["steam"],
        ["hour", "day"],
    ]


def test_tupler_keeps_the_prefix_in_branches_and_set_leaves():
    tree = {"north": {"power": {"hour"}}, "south": {}}
    assert tupler(tree, path=("grid",)) == [
        ("grid", "north"),
        ("grid", "north", "power"),
        ("grid", "north", "power", "hour"),
        ("grid", "south"),
    ]
