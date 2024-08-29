"""Test to check if I have  made stuff that is needed to run energiapy

e.g. are constraint rules defined for all variables? 

"""

import pytest

from .test_fixtures import scenario_bare


def test_made_rules(scenario_bare):
    """Are rules defined for all variables?"""
    assert scenario_bare.taskmaster.vars() == scenario_bare.rulebook.vars()


def test_name_overlap(scenario_bare):
    """There is no overlap between Variable and Parameter names"""
    assert (
        set([p.cname() for p in scenario_bare.rulebook.params()])
        & set([v.cname() for v in scenario_bare.rulebook.vars()])
        == set()
    )
