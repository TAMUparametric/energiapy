"""Error Tests
"""

import pytest
from pandas import DataFrame

from src.energiapy.components.commodity.cash import Cash
from src.energiapy.components.temporal.horizon import Horizon
from src.energiapy.core.nirop.errors import (
    NoBasisError,
    NoLabelError,
    NoScaleMatchError,
    OverWriteError,
)

from .test_fixtures import scenario_bare, scenario_def, scenario_notok, scenario_ok


def test_notok_errors(scenario_notok):
    """Overwrite Warning
    if another Horizon is defined, it should raise a warning
    """
    with pytest.raises(OverWriteError):
        scenario_notok.h = Horizon(discretizations=[4])
    with pytest.raises(NoLabelError):
        scenario_notok.r0 = Cash(basis='basis')
    with pytest.raises(NoBasisError):
        scenario_notok.r1 = Cash(label='label')


wrong_length = DataFrame({'b': list(range(9))})


def test_mismatch(scenario_ok, scenario_notok):
    """For all scenarios, data whose scales dont match should raise an error"""

    with pytest.raises(NoScaleMatchError):
        scenario_ok.c0 = Cash(spend=wrong_length)
    with pytest.raises(NoScaleMatchError):
        scenario_notok.c1 = Cash(spend=wrong_length, basis='basis', label='label')
